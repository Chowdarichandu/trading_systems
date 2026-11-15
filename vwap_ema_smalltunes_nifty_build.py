#!/usr/bin/env python3
"""SMALL TUNES — VWAP x EMA CROSSOVER, NIFTY (spec: vwap_ema_smalltunes_nifty_SPEC.md, frozen).
Research only. Reads persisted stores; writes vwap_ema_smalltunes_nifty_results.json.
"""
import json, re, random
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

TR = Path.home() / "workspace" / "trading"
LOT, COST = 65, 220.0
random.seed(20261114)

# ------------------------------------------------------------------ spot + EMA
spot = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv", parse_dates=["timestamp"])
spot = spot.sort_values("timestamp").reset_index(drop=True)
spot["date"] = spot["timestamp"].dt.date
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
closes = spot["close"].values
n = len(spot)

def ema_series(p):
    k = 2.0 / (p + 1)
    out = np.empty(n); e = closes[0]; out[0] = e
    for i in range(1, n):
        e = closes[i] * k + e * (1 - k); out[i] = e
    return out

PERIODS = [5, 9, 13, 20, 21, 34, 50]
EMA = {p: ema_series(p) for p in PERIODS}
PAIRS = [(5, 20), (9, 21), (13, 34), (20, 50)]

def pair_arrays(pair):
    f, s = EMA[pair[0]], EMA[pair[1]]
    cross = np.zeros(n, dtype=int)
    d = f - s
    cross[1:] = np.where((d[1:] > 0) & (d[:-1] <= 0), 1, np.where((d[1:] < 0) & (d[:-1] >= 0), -1, 0))
    return f, s, cross
PAIR_DATA = {pr: pair_arrays(pr) for pr in PAIRS}

# ------------------------------------------------------------------ futures VWAP (DIAL convention)
fut_by_exp = {}
for fn in (TR / "phase3_buildup_data/futures").glob("FUT7_NIFTY_*.json"):
    m = re.match(r"FUT7_NIFTY_(\d{4}-\d{2}-\d{2})_", fn.name)
    if not m: continue
    exp = m.group(1)
    dd = fut_by_exp.setdefault(exp, {})
    for ts, o_, h_, l_, c_, v_, oi_ in json.load(open(fn))["data"]["candles"]:
        dd.setdefault(ts[:10], {})[ts[11:16]] = ((h_ + l_ + c_) / 3.0, v_, c_)
fut_exps = sorted(fut_by_exp)

_vwap_cache = {}
def vwap_series(day_iso):
    if day_iso in _vwap_cache: return _vwap_cache[day_iso]
    exp = next((e for e in fut_exps if e >= day_iso), None)
    out = {}
    if exp is not None:
        bars = fut_by_exp[exp].get(day_iso, {})
        pv = vv = 0.0; last = None
        for t in sorted(bars):
            tp, v_, fc = bars[t]
            pv += tp * v_; vv += v_
            last = pv / vv if vv > 0 else last
            out[t] = (last, fc)
    _vwap_cache[day_iso] = out
    return out

# ------------------------------------------------------------------ option store
OI = TR / "oi_buildup_data"
expiry_cal = sorted({re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name).group(1)
                     for fn in OI.glob("candles_NIFTY_*.json")
                     if re.match(r".*candles_NIFTY_\d+(?:CE|PE)_(\d{4}-\d{2}-\d{2})_", fn.name)})
_file_cache = {}
def contract_bars(day_iso, strike, typ, exp):
    key = (day_iso, strike, typ, exp)
    if key in _file_cache: return _file_cache[key]
    fn = OI / f"candles_NIFTY_{strike}{typ}_{exp}_{day_iso}.json"
    out = None
    if fn.exists():
        bars = {}
        for ts, o_, h_, l_, c_, v_, oi_ in json.load(open(fn))["data"]["candles"]:
            bars[ts[11:16]] = (o_, h_, l_, c_)
        out = bars
    _file_cache[key] = out
    return out

BAR_TIMES = [f"{9 + (15 + 5*i)//60:02d}:{(15 + 5*i) % 60:02d}" for i in range(75)]
def t_idx(t): return BAR_TIMES.index(t)
def scorable_window(bars, entry_t):
    if bars is None: return False
    return all(BAR_TIMES[j] in bars for j in range(t_idx(entry_t), t_idx("15:20") + 1))
def weekly_expiry(day_iso):
    return next((e for e in expiry_cal if e >= day_iso), None)

# ------------------------------------------------------------------ day structures
_day_cache = {}
def day_struct(d):
    """d: datetime.date -> dict with times, global idxs, aligned fut_close/vwap arrays."""
    if d in _day_cache: return _day_cache[d]
    idxs = spot.index[spot["date"] == d].tolist()
    times = [spot.at[i, "time"] for i in idxs]
    vw = vwap_series(d.isoformat())
    fc = [vw[t][1] if t in vw else None for t in times]
    vv = [vw[t][0] if t in vw else None for t in times]
    st = {"idxs": idxs, "times": times, "fc": fc, "vw": vv}
    _day_cache[d] = st
    return st

def side_at(st, pos, buf):
    fc, vv = st["fc"][pos], st["vw"][pos]
    if fc is None or vv is None: return None
    if fc > vv * (1 + buf): return 1
    if fc < vv * (1 - buf): return -1
    return 0

def vwap_crosses(st, buf):
    """list of (pos, direction) VWAP crosses within the session (spec definition)."""
    out = []
    for pos in range(1, len(st["times"])):
        s_cur, s_prev = side_at(st, pos, buf), side_at(st, pos - 1, buf)
        if s_cur is None or s_prev is None: continue
        if s_cur == 1 and s_prev != 1: out.append((pos, 1))
        elif s_cur == -1 and s_prev != -1: out.append((pos, -1))
    return out

# ------------------------------------------------------------------ exits
def sim_level(bars, entry_t, stop_pts, tgt_pts):
    ep = bars[entry_t][0]
    stop, tgt = ep - stop_pts, ep + tgt_pts
    for t in BAR_TIMES[t_idx(entry_t): t_idx("15:15") + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "stop"
        if h_ >= tgt: return ep, tgt, "target"
    return ep, bars["15:20"][0], "sq1520"

def sim_e3(bars, entry_t, day_iso, direction):
    ep = bars[entry_t][0]; stop = ep - 60.0
    vw = vwap_series(day_iso)
    for t in BAR_TIMES[t_idx(entry_t): t_idx("15:15") + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "hardstop"
        if t in vw:
            vwap_v, fut_c = vw[t]
            if (direction == 1 and fut_c < vwap_v) or (direction == -1 and fut_c > vwap_v):
                return ep, c_, "vwap_back"
    return ep, bars["15:20"][0], "sq1520"

def sim_e4(bars, entry_t, d, direction, pair):
    ep = bars[entry_t][0]; stop = ep - 60.0
    st = day_struct(d)
    _, _, cross = PAIR_DATA[pair]
    cross_at = {st["times"][k]: int(cross[st["idxs"][k]]) for k in range(len(st["times"]))}
    want = -direction  # opposite cross
    for t in BAR_TIMES[t_idx(entry_t): t_idx("15:15") + 1]:
        o_, h_, l_, c_ = bars[t]
        if l_ <= stop: return ep, stop, "hardstop"
        if cross_at.get(t, 0) == want:
            return ep, c_, "ema_opp_cross"
    return ep, bars["15:20"][0], "sq1520"

def simulate(exit_kind, bars, entry_t, d, direction, pair):
    if exit_kind == "E1": return sim_level(bars, entry_t, 40.0, 70.0)
    if exit_kind == "E2": return sim_level(bars, entry_t, 50.0, 90.0)
    if exit_kind == "E3": return sim_e3(bars, entry_t, d.isoformat(), direction)
    if exit_kind == "E4": return sim_e4(bars, entry_t, d, direction, pair if pair else (9, 21))
    raise ValueError(exit_kind)

# ------------------------------------------------------------------ signal generation
def find_candidate(rule, pair, hold, buf, d):
    """Returns (final_signal_pos_in_day, direction) or None."""
    st = day_struct(d)
    times, idxs = st["times"], st["idxs"]
    if rule == "B":
        _, _, cross = PAIR_DATA[pair]
        for pos, gi in enumerate(idxs):
            if int(cross[gi]) != 0:
                return pos, int(cross[gi])
        return None
    if rule == "A":
        for pos, dr in vwap_crosses(st, buf):
            if hold == 0: return pos, dr
            if pos + 1 < len(times) and side_at(st, pos + 1, buf) == dr:
                return pos + 1, dr
            return None  # first cross is the only candidate; failed confirmation = dead
        return None
    if rule == "C":
        f, s, cross = PAIR_DATA[pair]
        for pos, gi in enumerate(idxs):
            cd = int(cross[gi])
            if cd == 0: continue
            if side_at(st, pos, buf) != cd: continue
            if hold == 0: return pos, cd
            if pos + 1 < len(times):
                gi1 = idxs[pos + 1]
                ema_ok = (f[gi1] > s[gi1]) if cd == 1 else (f[gi1] < s[gi1])
                if ema_ok and side_at(st, pos + 1, buf) == cd:
                    return pos + 1, cd
            # confirmation failed -> keep scanning later crosses
        return None
    if rule == "C2":
        f, s, _ = PAIR_DATA[pair]
        for pos, dr in vwap_crosses(st, buf):
            gi = idxs[pos]
            aligned = (f[gi] > s[gi]) if dr == 1 else (f[gi] < s[gi])
            if not aligned: continue
            if hold == 0: return pos, dr
            if pos + 1 < len(times):
                gi1 = idxs[pos + 1]
                al1 = (f[gi1] > s[gi1]) if dr == 1 else (f[gi1] < s[gi1])
                if al1 and side_at(st, pos + 1, buf) == dr:
                    return pos + 1, dr
            # confirmation failed -> keep scanning later crosses
        return None
    raise ValueError(rule)

def score_candidate(rule, pair, d, cand):
    """Score one candidate under all 4 exits. Returns (status, {exit: trade_dict})."""
    st = day_struct(d)
    pos, direction = cand
    sig_t = st["times"][pos]
    j = t_idx(sig_t)
    if j + 1 >= len(BAR_TIMES): return "late", None
    entry_t = BAR_TIMES[j + 1]
    if entry_t > "15:15": return "late", None
    strike = int(round(spot.at[st["idxs"][pos], "close"] / 50.0) * 50)
    typ = "CE" if direction == 1 else "PE"
    exp = weekly_expiry(d.isoformat())
    bars = contract_bars(d.isoformat(), strike, typ, exp)
    if bars is None: return "nc_no_file", None
    if not scorable_window(bars, entry_t): return "nc_partial", None
    out = {}
    for ek in ("E1", "E2", "E3", "E4"):
        ep, xp, reason = simulate(ek, bars, entry_t, d, direction, pair)
        out[ek] = {"date": d.isoformat(), "signal_time": sig_t, "entry_time": entry_t,
                   "direction": typ, "strike": strike, "expiry": exp, "entry": ep,
                   "exit": xp, "exit_reason": reason, "net": round((xp - ep) * LOT - COST, 2)}
    return "scored", out

# ------------------------------------------------------------------ grid
def combos():
    for hold in (0, 1):
        for buf in (0.0, 0.0005, 0.001):
            yield ("A", None, hold, buf)
    for pair in PAIRS:
        yield ("B", pair, None, None)
    for pair in PAIRS:
        for hold in (0, 1):
            for buf in (0.0, 0.0005, 0.001):
                yield ("C", pair, hold, buf)
                yield ("C2", pair, hold, buf)

def row_key(rule, pair, hold, buf, ek):
    return {"rule": rule, "pair": list(pair) if pair else None, "hold": hold,
            "buffer": buf, "exit": ek}

def metrics(trades):
    if not trades: return {"trades": 0, "net": 0.0, "wr": 0.0}
    tot = round(sum(t["net"] for t in trades), 2)
    wins = sum(1 for t in trades if t["net"] > 0)
    return {"trades": len(trades), "net": tot, "wr": round(100 * wins / len(trades), 1)}

def run_grid(d0, d1):
    days = sorted(d for d in spot["date"].unique() if d0 <= d <= d1)
    # per combo: per exit: trades list; status counts
    acc = {}
    for combo in combos():
        rule, pair, hold, buf = combo
        per_exit = {ek: [] for ek in ("E1", "E2", "E3", "E4")}
        counts = {"signals": 0, "scored": 0, "nc_no_file": 0, "nc_partial": 0, "late": 0}
        for d in days:
            cand = find_candidate(rule, pair, hold, buf, d)
            if cand is None: continue
            counts["signals"] += 1
            status, scored = score_candidate(rule, pair, d, cand)
            if status == "scored":
                counts["scored"] += 1
                for ek in ("E1", "E2", "E3", "E4"):
                    per_exit[ek].append(scored[ek])
            else:
                counts[status] += 1
        acc[combo] = (per_exit, counts)
    return acc

print("running Jan-Oct grid...")
acc_main = run_grid(date(2026, 1, 1), date(2026, 10, 31))
print("running November grid...")
acc_nov = run_grid(date(2026, 11, 2), date(2026, 11, 13))

rows = []
best_trades = {}   # rule -> (row, trades)
for combo, (per_exit, counts) in acc_main.items():
    rule, pair, hold, buf = combo
    nov_exit, _ = acc_nov[combo]
    for ek in ("E1", "E2", "E3", "E4"):
        tr = per_exit[ek]
        jj = [t for t in tr if t["date"] < "2026-07-01"]
        jo = [t for t in tr if t["date"] >= "2026-07-01"]
        row = row_key(rule, pair, hold, buf, ek)
        row.update({"jan_jun": metrics(jj), "jul_oct": metrics(jo), "full": metrics(tr),
                    "november_cf": metrics(nov_exit[ek]),
                    "signals": counts["signals"], "nc_no_file": counts["nc_no_file"],
                    "nc_partial": counts["nc_partial"], "late": counts["late"]})
        rows.append(row)
        cur = best_trades.get(rule)
        if cur is None or row["full"]["net"] > cur[0]["full"]["net"]:
            best_trades[rule] = (row, tr, nov_exit[ek])

# ------------------------------------------------------------------ stepwise paths
def get_row(rule, pair, hold, buf, ek):
    for r in rows:
        if r["rule"] == rule and r["pair"] == (list(pair) if pair else None) and \
           r["hold"] == hold and r["buffer"] == buf and r["exit"] == ek:
            return r
    return None

def path_for(rule):
    steps = []
    if rule == "A":
        cur_hold, cur_buf, cur_ek = 0, 0.0, "E2"
        steps.append({"step": "base", "rows": [get_row("A", None, 0, 0.0, "E2")]})
        cand = [get_row("A", None, h, cur_buf, cur_ek) for h in (0, 1)]
        steps.append({"step": "dial2_hold", "rows": cand})
        cur_hold = max(cand, key=lambda r: r["full"]["net"])["hold"]
        cand = [get_row("A", None, cur_hold, b, cur_ek) for b in (0.0, 0.0005, 0.001)]
        steps.append({"step": "dial3_buffer", "rows": cand})
        cur_buf = max(cand, key=lambda r: r["full"]["net"])["buffer"]
        cand = [get_row("A", None, cur_hold, cur_buf, e) for e in ("E1", "E2", "E3", "E4")]
        steps.append({"step": "dial4_exit", "rows": cand})
        cur_ek = max(cand, key=lambda r: r["full"]["net"])["exit"]
        return steps, get_row("A", None, cur_hold, cur_buf, cur_ek)
    if rule == "B":
        cur_pair, cur_ek = (9, 21), "E2"
        steps.append({"step": "base", "rows": [get_row("B", (9, 21), None, None, "E2")]})
        cand = [get_row("B", p, None, None, cur_ek) for p in PAIRS]
        steps.append({"step": "dial1_pair", "rows": cand})
        cur_pair = tuple(max(cand, key=lambda r: r["full"]["net"])["pair"])
        cand = [get_row("B", cur_pair, None, None, e) for e in ("E1", "E2", "E3", "E4")]
        steps.append({"step": "dial4_exit", "rows": cand})
        cur_ek = max(cand, key=lambda r: r["full"]["net"])["exit"]
        return steps, get_row("B", cur_pair, None, None, cur_ek)
    # C / C2
    cur_pair, cur_hold, cur_buf, cur_ek = (9, 21), 0, 0.0, "E2"
    steps.append({"step": "base", "rows": [get_row(rule, (9, 21), 0, 0.0, "E2")]})
    cand = [get_row(rule, p, cur_hold, cur_buf, cur_ek) for p in PAIRS]
    steps.append({"step": "dial1_pair", "rows": cand})
    cur_pair = tuple(max(cand, key=lambda r: r["full"]["net"])["pair"])
    cand = [get_row(rule, cur_pair, h, cur_buf, cur_ek) for h in (0, 1)]
    steps.append({"step": "dial2_hold", "rows": cand})
    cur_hold = max(cand, key=lambda r: r["full"]["net"])["hold"]
    cand = [get_row(rule, cur_pair, cur_hold, b, cur_ek) for b in (0.0, 0.0005, 0.001)]
    steps.append({"step": "dial3_buffer", "rows": cand})
    cur_buf = max(cand, key=lambda r: r["full"]["net"])["buffer"]
    cand = [get_row(rule, cur_pair, cur_hold, cur_buf, e) for e in ("E1", "E2", "E3", "E4")]
    steps.append({"step": "dial4_exit", "rows": cand})
    cur_ek = max(cand, key=lambda r: r["full"]["net"])["exit"]
    return steps, get_row(rule, cur_pair, cur_hold, cur_buf, cur_ek)

paths = {rule: path_for(rule) for rule in ("A", "B", "C", "C2")}

# ------------------------------------------------------------------ timing audit on best rows
def audit_rule(rule):
    row, trades, _ = best_trades[rule]
    ok = True
    for t in trades:
        bars = contract_bars(t["date"], t["strike"], t["direction"], t["expiry"])
        if bars[t["entry_time"]][0] != t["entry"] or t_idx(t["entry_time"]) != t_idx(t["signal_time"]) + 1:
            ok = False
    indep = {"checked": False}
    if trades:
        t0 = trades[0]
        d0 = date.fromisoformat(t0["date"])
        st = day_struct(d0)
        pos = st["times"].index(t0["signal_time"])
        gi = st["idxs"][pos]
        # independent EMA recompute (direct loops from series start)
        res = {}
        pair = tuple(row["pair"]) if row["pair"] else (9, 21)
        for p in pair:
            k = 2.0 / (p + 1); e = closes[0]
            for i in range(1, gi + 1): e = closes[i] * k + e * (1 - k)
            res[p] = e
        # independent VWAP recompute for the day up to signal time
        exp = next((e for e in fut_exps if e >= t0["date"]), None)
        bars_f = fut_by_exp[exp].get(t0["date"], {})
        pv = vv = 0.0; vw_at = fc_at = None
        for tt in sorted(bars_f):
            if tt > t0["signal_time"]: break
            tp, v_, fc = bars_f[tt]; pv += tp * v_; vv += v_
            if tt == t0["signal_time"]: vw_at, fc_at = pv / vv, fc
        main_vw = st["vw"][pos]; main_fc = st["fc"][pos]
        indep = {"checked": True, "date": t0["date"], "signal_time": t0["signal_time"],
                 "ema_fast_main": round(float(EMA[pair[0]][gi]), 3), "ema_fast_indep": round(float(res[pair[0]]), 3),
                 "ema_slow_main": round(float(EMA[pair[1]][gi]), 3), "ema_slow_indep": round(float(res[pair[1]]), 3),
                 "ema_match": abs(float(EMA[pair[0]][gi]) - res[pair[0]]) < 0.01 and abs(float(EMA[pair[1]][gi]) - res[pair[1]]) < 0.01,
                 "vwap_main": round(float(main_vw), 3) if main_vw is not None else None,
                 "vwap_indep": round(float(vw_at), 3) if vw_at is not None else None,
                 "vwap_match": (main_vw is None and vw_at is None) or (main_vw is not None and vw_at is not None and abs(main_vw - vw_at) < 0.01)}
    return {"entry_timing_ok": ok, "independent_recompute": indep}

audits = {rule: audit_rule(rule) for rule in ("A", "B", "C", "C2")}

# ------------------------------------------------------------------ placebo on best rows
universe = {"CE": [], "PE": []}
for fn in OI.glob("candles_NIFTY_*.json"):
    m = re.match(r"candles_NIFTY_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", fn.name)
    if not m: continue
    strike, typ, exp, day_iso = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if not ("2026-01-01" <= day_iso <= "2026-10-31"): continue
    bars = contract_bars(day_iso, strike, typ, exp)
    feas = [BAR_TIMES[j] for j in range(0, t_idx("15:15") + 1) if scorable_window(bars, BAR_TIMES[j])]
    if feas: universe[typ].append((day_iso, bars, feas))

def placebo_for(rule):
    row, trades, _ = best_trades[rule]
    pair = tuple(row["pair"]) if row["pair"] else None
    ek = row["exit"]
    totals = []
    for _ in range(1000):
        tot = 0.0
        for t in trades:
            typ = t["direction"]
            day_iso, bars, feas = universe[typ][random.randrange(len(universe[typ]))]
            et = feas[random.randrange(len(feas))]
            d = date.fromisoformat(day_iso)
            direction = 1 if typ == "CE" else -1
            ep, xp, _r = simulate(ek, bars, et, d, direction, pair)
            tot += (xp - ep) * LOT - COST
        totals.append(round(tot, 2))
    pct = sum(1 for v in totals if v <= row["full"]["net"]) / len(totals)
    return {"iterations": 1000, "percentile": round(pct, 4),
            "mean_total": round(float(np.mean(totals)), 2),
            "p95_total": round(float(np.percentile(totals, 95)), 2),
            "real_total": row["full"]["net"], "trades": len(trades)}

print("running placebos on best rows...")
placebos = {rule: placebo_for(rule) for rule in ("A", "B", "C", "C2")}

results = {
    "book": "SMALL TUNES — VWAP x EMA CROSSOVER, NIFTY",
    "spec": "vwap_ema_smalltunes_nifty_SPEC.md",
    "rows": rows,
    "paths": {rule: {"steps": [{"step": s["step"], "rows": s["rows"]} for s in paths[rule][0]],
                     "path_end_row": paths[rule][1]} for rule in paths},
    "best_rows": {rule: best_trades[rule][0] for rule in best_trades},
    "best_trades": {rule: best_trades[rule][1] for rule in best_trades},
    "timing_audits": audits,
    "placebos": placebos,
}
json.dump(results, open(TR / "vwap_ema_smalltunes_nifty_results.json", "w"), indent=1,
          default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))

for rule in ("A", "B", "C", "C2"):
    r = best_trades[rule][0]
    print(rule, "BEST:", r["pair"], "hold", r["hold"], "buf", r["buffer"], r["exit"],
          "| JJ", r["jan_jun"], "| JO", r["jul_oct"], "| FULL", r["full"],
          "| NOV", r["november_cf"], "| NC", r["nc_no_file"] + r["nc_partial"],
          "| placebo pct", placebos[rule]["percentile"], "| audit", audits[rule]["entry_timing_ok"])
    print("   path end:", paths[rule][1]["pair"], paths[rule][1]["hold"], paths[rule][1]["buffer"],
          paths[rule][1]["exit"], paths[rule][1]["full"])
