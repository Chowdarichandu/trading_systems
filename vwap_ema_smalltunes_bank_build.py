#!/usr/bin/env python3
"""SMALL TUNES — VWAP x EMA CROSSOVER, Bank Nifty.
Spec: vwap_ema_smalltunes_bank_SPEC.md (frozen 2026-11-14 before
scoring). Local stores only — NO API calls. Research only: writes
vwap_ema_smalltunes_bank_results.json + the .md report only."""
import bisect, csv, json, math, random, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
LOT, COST, SQ = 30, 220.0, "15:20"
STEP = 100
SEED = 20261114
PAIRS = [(5, 20), (9, 21), (13, 34), (20, 50)]
BUFFERS = [0.0, 0.0005, 0.0010]
EXITS = ["E1", "E2", "E3", "E4"]
EXIT_LVL = {"E1": (40.0, 70.0), "E2": (50.0, 90.0)}
HARD_STOP = 60.0
BASE_PAIR = (9, 21)

# ---------------- spot (continuous series) ----------------
spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot = spot[(spot["timestamp"] >= "2026-01-01") &
            (spot["timestamp"] <= "2026-11-13")].sort_values("timestamp")
spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
C = spot["close"].to_numpy(float)
DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
day_idx = {}
for i, d in enumerate(DATES):
    day_idx.setdefault(d, []).append(i)
POS = {}
for d, idxs in day_idx.items():
    for p, gi in enumerate(idxs):
        POS[gi] = p
TPOS = {d: {TIMES[gi]: p for p, gi in enumerate(idxs)}
        for d, idxs in day_idx.items()}
GATE_DAYS = sorted(d for d in day_idx if d <= "2026-10-31")
NOV_DAYS = sorted(d for d in day_idx if "2026-11-02" <= d <= "2026-11-13")

# ---------------- expiry map ----------------
EXP = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        EXP[r["date"]] = r["expiry"]
for d in NOV_DAYS:
    EXP[d] = "2026-11-23"

# ---------------- futures session VWAP ----------------
_fut = {}
def fut_day(exp, day):
    if exp not in _fut:
        fn = TR / f"round5_history/FUT7_{exp}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]),
                                                  float(r[6]))
        _fut[exp] = byd
    return _fut[exp].get(day)

def vwap_series(day):
    fd = fut_day(EXP[day], day)
    if not fd:
        return None
    out, cum_pv, cum_v = {}, 0.0, 0.0
    for t in sorted(fd):
        o, h, l, c, v = fd[t]
        tp = (h + l + c) / 3.0
        cum_pv += tp * v; cum_v += v
        out[t] = cum_pv / cum_v if cum_v > 0 else None
    return out

_vw_cache = {}
def day_vwap(day):
    if day in _vw_cache:
        return _vw_cache[day]
    raw = vwap_series(day)
    if raw is None:
        _vw_cache[day] = None
        return None
    ftimes = sorted(raw)
    out = {}
    for gi in day_idx[day]:
        t = TIMES[gi]
        j = bisect.bisect_right(ftimes, t) - 1
        out[t] = raw[ftimes[j]] if j >= 0 else None
    _vw_cache[day] = out
    return out

# ---------------- premium stores (house resolution order) ----------------
_c5 = {}
def prem_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = TR / f"round5_history/C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]))
        _c5[ck] = byd
    return _c5[ck].get(day)

PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
_prem_cache = {}
def prem_store(exp, strike, typ, day):
    ck = (exp, strike, typ, day)
    if ck in _prem_cache:
        return _prem_cache[ck]
    res = prem_c5(exp, strike, typ, day)
    if not res:
        cd = PREM_B.get(f"{exp}|{int(strike)}|{typ}", {}).get(day)
        if cd:
            res = {t: tuple(float(x) for x in v) for t, v in cd.items()}
    if not res:
        for folder in ("btst_data", "november_shadow_data",
                       "nifty_weekly_expiry_chain", "oi_buildup_data"):
            fn = TR / folder / f"candles_BANKNIFTY_{int(strike)}{typ}_{exp}_{day}.json"
            if fn.exists():
                body = json.loads(fn.read_text())
                rows = [c for c in ((body.get("data") or {}).get("candles")
                                    or []) if c[0][:10] == day]
                if rows:
                    res = {c[0][11:16]: (float(c[1]), float(c[2]),
                                         float(c[3]), float(c[4]))
                           for c in rows}
                    break
    _prem_cache[ck] = res
    return res

# ---------------- EMA (continuous, causal) ----------------
def ema_series(c, period):
    n = len(c); out = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(c[:period]) / period
    for i in range(period, n):
        out[i] = c[i] * k + out[i - 1] * (1 - k)
    return out

_ema_cache = {}
def emas(pair):
    if pair not in _ema_cache:
        _ema_cache[pair] = (ema_series(C, pair[0]), ema_series(C, pair[1]))
    return _ema_cache[pair]

_cross_cache = {}
def ema_cross(pair, gi):
    """'up'/'down'/None: EMA cross event AT bar gi (continuous)."""
    ck = (pair, gi)
    if ck in _cross_cache:
        return _cross_cache[ck]
    F, S = emas(pair)
    res = None
    if gi >= 1 and F[gi] is not None and S[gi] is not None and \
            F[gi - 1] is not None and S[gi - 1] is not None:
        if F[gi - 1] <= S[gi - 1] and F[gi] > S[gi]:
            res = "up"
        elif F[gi - 1] >= S[gi - 1] and F[gi] < S[gi]:
            res = "down"
    _cross_cache[ck] = res
    return res

def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

# ---------------- signal generation ----------------
def vwap_cross(day, pos, buf):
    """VWAP cross at day-position pos (needs pos>=1, same session)."""
    idxs = day_idx[day]
    if pos < 1:
        return None
    vw = day_vwap(day)
    if vw is None:
        return None
    gi, gp = idxs[pos], idxs[pos - 1]
    v0, v1 = vw.get(TIMES[gp]), vw.get(TIMES[gi])
    if v0 is None or v1 is None:
        return None
    if C[gp] <= v0 * (1 + buf) and C[gi] > v1 * (1 + buf):
        return "up"
    if C[gp] >= v0 * (1 - buf) and C[gi] < v1 * (1 - buf):
        return "down"
    return None

def vwap_side(day, gi, side, buf):
    vw = day_vwap(day)
    if vw is None:
        return False
    v = vw.get(TIMES[gi])
    if v is None:
        return False
    return C[gi] > v * (1 + buf) if side == "up" else C[gi] < v * (1 - buf)

def ema_aligned(pair, gi, side):
    F, S = emas(pair)
    if F[gi] is None or S[gi] is None:
        return False
    return F[gi] > S[gi] if side == "up" else F[gi] < S[gi]

def cross_event(day, pos, rule, pair, buf):
    """Cross event at day-position pos for the rule, or None."""
    gi = day_idx[day][pos]
    if rule == "A":
        return vwap_cross(day, pos, buf)
    if rule == "B":
        return ema_cross(pair, gi)
    if rule == "C":
        cr = ema_cross(pair, gi)
        if cr and vwap_side(day, gi, cr, buf):
            return cr
        return None
    if rule == "C2":
        cr = vwap_cross(day, pos, buf)
        if cr and ema_aligned(pair, gi, cr):
            return cr
        return None
    raise ValueError(rule)

def persists(day, pos, rule, pair, buf, side):
    """Hold=1 confirmation test at day-position pos (the confirm bar)."""
    gi = day_idx[day][pos]
    if rule == "A":
        return vwap_side(day, gi, side, buf)
    if rule == "B":
        return ema_aligned(pair, gi, side)
    return ema_aligned(pair, gi, side) and vwap_side(day, gi, side, buf)

def gen_signal(day, rule, pair, hold, buf):
    """First signal of the day. Returns (decision_gi, side, status):
    status 'OK' (decision bar set), 'LATE', or None (no event)."""
    idxs = day_idx[day]
    late_seen = False
    for pos, gi in enumerate(idxs):
        side = cross_event(day, pos, rule, pair, buf)
        if side is None:
            continue
        t = TIMES[gi]
        if t > "15:10":
            late_seen = True
            break
        if hold == 0:
            if pos + 1 < len(idxs) and TIMES[idxs[pos + 1]] <= "15:15":
                return gi, side, "OK"
            return gi, side, "LATE"
        # hold == 1: confirm bar = next bar
        if pos + 1 >= len(idxs):
            continue
        cg = idxs[pos + 1]
        if TIMES[cg] > "15:10":
            return gi, side, "LATE"
        if not persists(day, pos + 1, rule, pair, buf, side):
            continue  # failed confirmation does not consume the day
        if pos + 2 < len(idxs) and TIMES[idxs[pos + 2]] <= "15:15":
            return cg, side, "OK"
        return cg, side, "LATE"
    return None, None, ("LATE" if late_seen else None)

# ---------------- trade scoring ----------------
def score_trade(day, entry_pos, ref_close, side, exit_cfg, pair):
    if pair is None:
        pair = BASE_PAIR  # Rule A: E4 exit uses the (9,21) base pair
    idxs = day_idx[day]
    strike = int(math.floor(ref_close / STEP + 0.5)) * STEP
    typ = "CE" if side == "up" else "PE"
    exp = EXP[day]
    prem = prem_store(exp, strike, typ, day)
    if not prem:
        return None
    et = TIMES[idxs[entry_pos]]
    if et not in prem:
        return None
    entry_px = prem[et][0]
    vw = day_vwap(day)
    exit_px = reason = xt = None
    m = tmin(et)
    while m <= tmin(SQ):
        t = tstr(m)
        bar = prem.get(t)
        if bar is None:
            return None
        o, h, l, c = bar
        if exit_cfg in EXIT_LVL:
            stop, target = EXIT_LVL[exit_cfg]
            if l <= entry_px - stop:
                exit_px, reason, xt = entry_px - stop, "stop", t
                break
            if h >= entry_px + target:
                exit_px, reason, xt = entry_px + target, "target", t
                break
            if t == SQ:
                exit_px, reason, xt = c, "squareoff", t
                break
        else:
            if l <= entry_px - HARD_STOP:
                exit_px, reason, xt = entry_px - HARD_STOP, "hard_stop", t
                break
            sp = TPOS[day].get(t)
            fire = False
            if sp is not None:
                sgi = idxs[sp]
                if exit_cfg == "E3":
                    v = vw.get(t) if vw else None
                    if v is not None:
                        fire = (C[sgi] < v) if side == "up" else (C[sgi] > v)
                else:  # E4: opposite EMA cross at this bar
                    cr = ema_cross(pair, sgi)
                    fire = (cr == "down") if side == "up" else (cr == "up")
            if fire:
                exit_px, reason, xt = c, ("vwap_exit" if exit_cfg == "E3"
                                          else "ema_exit"), t
                break
            if t == SQ:
                exit_px, reason, xt = c, "squareoff", t
                break
        m += 5
    if exit_px is None:
        return None
    return dict(date=day, side=side, strike=strike, typ=typ, expiry=exp,
                entry_time=et, entry_px=entry_px, exit_time=xt,
                exit_px=exit_px, exit_reason=reason,
                net=(exit_px - entry_px) * LOT - COST)

def run_row(days, rule, pair, hold, buf, exit_cfg):
    trades, audit = [], []
    cnt = dict(signals=0, nc=0, late=0)
    for day in days:
        dgi, side, status = gen_signal(day, rule, pair, hold, buf)
        if status == "LATE":
            cnt["late"] += 1
            continue
        if status != "OK":
            continue
        cnt["signals"] += 1
        audit.append(dgi)
        idxs = day_idx[day]
        entry_pos = POS[dgi] + 1
        tr = score_trade(day, entry_pos, C[dgi], side, exit_cfg, pair)
        if tr is None:
            cnt["nc"] += 1
        else:
            tr["decision_time"] = TIMES[dgi]
            trades.append(tr)
    return trades, cnt, audit

def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = sum(t["net"] for t in trades)
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                net=round(total, 2))

def row_stats(gate_trades, nov_trades):
    h1 = [t for t in gate_trades if t["date"] <= "2026-06-30"]
    h2 = [t for t in gate_trades if t["date"] >= "2026-07-01"]
    return dict(jan_jun=stats(h1), jul_oct=stats(h2),
                jan_oct=stats(gate_trades), nov_cf=stats(nov_trades))

# ---------------- sequential dial path ----------------
ROWS = []          # every scored row (dicts)
ROW_TRADES = {}    # row_id -> (gate_trades, nov_trades, audit bars)
_n = [0]
def score_row(step, rule, pair, hold, buf, exit_cfg):
    gt, gc, ga = run_row(GATE_DAYS, rule, pair, hold, buf, exit_cfg)
    nt, nc, na = run_row(NOV_DAYS, rule, pair, hold, buf, exit_cfg)
    _n[0] += 1
    rid = f"r{_n[0]:02d}"
    row = dict(id=rid, step=step, rule=rule,
               ema_pair=list(pair) if pair else None, hold=hold,
               buffer_pct=(buf * 100), exit=exit_cfg,
               counts_gate=gc, counts_nov=nc,
               **row_stats(gt, nt))
    ROWS.append(row)
    ROW_TRADES[rid] = (gt, nt, ga + na)
    return row

def carry(rows):
    """Highest full Jan-Oct net; tie -> earliest scored (listed first)."""
    return max(rows, key=lambda r: r["jan_oct"]["net"])

carried = {}   # rule -> dict(pair, hold, buf, exit)

# Dial 1 — EMA pair (hold 0, buffer 0, exit E2); Rule A base row once.
step_rows = {"A": [score_row(1, "A", None, 0, 0.0, "E2")]}
for rule in ("B", "C", "C2"):
    step_rows[rule] = [score_row(1, rule, p, 0, 0.0, "E2") for p in PAIRS]
for rule in ("A", "B", "C", "C2"):
    best = carry(step_rows[rule])
    carried[rule] = dict(pair=(tuple(best["ema_pair"]) if best["ema_pair"]
                               else BASE_PAIR),
                         hold=0, buf=0.0, exit="E2",
                         row_id=best["id"])

# Dial 2 — hold 0 vs 1 (pair carried, buffer 0, exit E2).
for rule in ("A", "B", "C", "C2"):
    cur = carried[rule]
    pair_arg = None if rule == "A" else cur["pair"]
    r1 = score_row(2, rule, pair_arg, 1, 0.0, "E2")
    prev = next(r for r in ROWS if r["id"] == cur["row_id"])
    best = carry([prev, r1])
    cur["hold"] = best["hold"]; cur["row_id"] = best["id"]

# Dial 3 — buffer 0 / 0.05% / 0.10% (pair + hold carried, exit E2).
for rule in ("A", "C", "C2"):
    cur = carried[rule]
    pair_arg = None if rule == "A" else cur["pair"]
    new = [score_row(3, rule, pair_arg, cur["hold"], b, "E2")
           for b in BUFFERS[1:]]
    prev = next(r for r in ROWS if r["id"] == cur["row_id"])
    best = carry([prev] + new)
    cur["buf"] = best["buffer_pct"] / 100.0; cur["row_id"] = best["id"]
# Rule B: no VWAP test — carried row stands.

# Dial 4 — exit E1/E2/E3/E4 (pair + hold + buffer carried).
for rule in ("A", "B", "C", "C2"):
    cur = carried[rule]
    pair_arg = None if rule == "A" else cur["pair"]
    e4_pair = cur["pair"]  # A uses the (9,21) base stored in carried
    new = []
    for ex in EXITS:
        if ex == "E2":
            continue
        new.append(score_row(4, rule, pair_arg, cur["hold"], cur["buf"], ex))
    prev = next(r for r in ROWS if r["id"] == cur["row_id"])
    best = carry([prev] + new)
    cur["exit"] = best["exit"]; cur["row_id"] = best["id"]

# ---------------- final rows: best full-year row per rule ----------------
finals = {}
for rule in ("A", "B", "C", "C2"):
    finals[rule] = carry([r for r in ROWS if r["rule"] == rule])

# ---------------- timing audit on final rows ----------------
def audit_row(row):
    gt, nt, bars = ROW_TRADES[row["id"]]
    pair = tuple(row["ema_pair"]) if row["ema_pair"] else BASE_PAIR
    bad = 0; checked = 0
    for gi in sorted(set(bars)):
        checked += 1
        f_full, s_full = emas(pair)
        f_t = ema_series(C[:gi + 1], pair[0])
        s_t = ema_series(C[:gi + 1], pair[1])
        ok = (abs(f_t[-1] - f_full[gi]) < 1e-9 and
              abs(s_t[-1] - s_full[gi]) < 1e-9)
        day = DATES[gi]
        vw = day_vwap(day)
        fd = fut_day(EXP[day], day)
        if vw is not None and fd:
            t = TIMES[gi]
            cpv = cv = 0.0; v_at = None
            for ft in sorted(fd):
                if ft > t:
                    break
                o, h, l, c, v = fd[ft]
                cpv += (h + l + c) / 3.0 * v; cv += v
                v_at = cpv / cv if cv > 0 else None
            ok = ok and (v_at is not None and vw.get(t) is not None and
                         abs(v_at - vw[t]) < 1e-6)
        # entry bar must be decision bar + 1 within the day
        ok = ok and POS[gi] + 1 < len(day_idx[day])
        if not ok:
            bad += 1
    return dict(bars_checked=checked, mismatches=bad,
                result="PASS" if bad == 0 else "FAIL")

audits = {rule: audit_row(finals[rule]) for rule in finals}

# ---------------- placebo on final rows ----------------
def placebo(row):
    gt, _, _ = ROW_TRADES[row["id"]]
    pair = tuple(row["ema_pair"]) if row["ema_pair"] else BASE_PAIR
    real = row["jan_oct"]["net"]
    rng = random.Random(SEED)
    totals, drops = [], 0
    for _ in range(500):
        tot = 0.0
        for rt in gt:
            tr = None
            for _a in range(51):
                d = rng.choice(GATE_DAYS)
                idxs = day_idx[d]
                cand = [p for p, gi in enumerate(idxs)
                        if "09:20" <= TIMES[gi] <= "15:15"]
                ep = rng.choice(cand)
                tr = score_trade(d, ep, C[idxs[ep - 1]], rt["side"],
                                 row["exit"], pair)
                if tr:
                    break
            if tr:
                tot += tr["net"]
            else:
                drops += 1
        totals.append(tot)
    totals.sort()
    pct = round(100.0 * sum(1 for x in totals if x < real) / len(totals), 1)
    return dict(percentile=pct, drops=drops, p50=totals[250],
                p95=totals[474], max=totals[-1], real=real)

placebos = {rule: placebo(finals[rule]) for rule in finals}

out = dict(spec="vwap_ema_smalltunes_bank_SPEC.md",
           basis="paper, 1 lot (30), Rs220/trade, buying only",
           gate_days=len(GATE_DAYS), rows=ROWS, carried=carried,
           finals={k: v for k, v in finals.items()},
           audits=audits, placebos=placebos,
           final_trades={rule: ROW_TRADES[finals[rule]["id"]][0]
                         for rule in finals})
json.dump(out, open(TR / "vwap_ema_smalltunes_bank_results.json", "w"),
          indent=1)
print("rows scored:", len(ROWS))
for rule in ("A", "B", "C", "C2"):
    f = finals[rule]
    print(rule, "final:", f["ema_pair"], "hold", f["hold"], "buf",
          f["buffer_pct"], f["exit"], "| jan-oct", f["jan_oct"],
          "| nov", f["nov_cf"], "| placebo pct",
          placebos[rule]["percentile"], "| audit", audits[rule]["result"])
