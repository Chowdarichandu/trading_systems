#!/usr/bin/env python3
"""PREMIUM-TAPE — BANK NIFTY. Signals off the option premium's own
chart. Spec: premium_tape_bank_SPEC.md (frozen 2026-11-14 before this
run). Local stores only — NO API calls. Research only: reads stores,
writes premium_tape_bank_results.json + premium_tape_bank_2026-11-14.md
+ premium_tape_bank_trades.csv only."""
import csv, json, math, random, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
LOT, COST, SQ = 30, 220.0, "15:20"
STEP = 100
SEED = 20261114
TIMES = []
_m = 9 * 60 + 15
while _m <= 15 * 60 + 20:
    TIMES.append(f"{_m // 60:02d}:{_m % 60:02d}")
    _m += 5
TIDX = {t: i for i, t in enumerate(TIMES)}
OR_TIMES = TIMES[:7]           # 09:15..09:45
SQ_IDX = TIDX[SQ]

def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])

# ---------------- spot (09:15 selection only) ----------------
spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot = spot[(spot["timestamp"] >= "2026-01-01") &
            (spot["timestamp"] < "2026-11-14")].sort_values("timestamp")
spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
SPOT915 = {}
for _, r in spot.iterrows():
    if r["time"] == "09:15":
        SPOT915[r["date"]] = float(r["close"])
ALL_DAYS = sorted(SPOT915)
GATE_DAYS = [d for d in ALL_DAYS if d <= "2026-10-31"]
NOV_DAYS = [d for d in ALL_DAYS if "2026-11-02" <= d <= "2026-11-13"]

# ---------------- expiry map ----------------
EXP = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        EXP[r["date"]] = r["expiry"]
for d in NOV_DAYS:
    EXP[d] = "2026-11-23"

# ---------------- premium stores ----------------
_c5 = {}
def prem_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = TR / f"round5_history/C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (
                    float(r[2]), float(r[3]), float(r[4]), float(r[5]),
                    float(r[6]))
        _c5[ck] = byd
    return _c5[ck].get(day)

def prem_perday(exp, strike, typ, day):
    for folder in ("btst_data", "november_shadow_data",
                   "nifty_weekly_expiry_chain", "oi_buildup_data"):
        fn = TR / folder / f"candles_BANKNIFTY_{int(strike)}{typ}_{exp}_{day}.json"
        if fn.exists():
            body = json.loads(fn.read_text())
            rows = [c for c in ((body.get("data") or {}).get("candles")
                                or []) if c[0][:10] == day]
            if rows:
                return {c[0][11:16]: (float(c[1]), float(c[2]),
                                      float(c[3]), float(c[4]),
                                      float(c[5])) for c in rows}
    return None

PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
def prem_daily2leg(exp, strike, typ, day):
    cd = PREM_B.get(f"{exp}|{int(strike)}|{typ}", {}).get(day)
    if cd:
        return {t: (float(v[0]), float(v[1]), float(v[2]), float(v[3]),
                    None) for t, v in cd.items()}
    return None

def load_side(day, typ):
    """Selected contract-day series -> dict with aligned arrays over
    TIMES or None (NC). Source priority frozen in the spec."""
    exp = EXP[day]
    strike = int(math.floor(SPOT915[day] / STEP + 0.5)) * STEP
    raw = prem_c5(exp, strike, typ, day)
    src = "c5"
    if not raw:
        raw = prem_perday(exp, strike, typ, day)
        src = "perday"
    if not raw:
        raw = prem_daily2leg(exp, strike, typ, day)
        src = "daily2leg"
    if not raw:
        return None
    if any(t not in raw for t in TIMES):
        return None
    O = [raw[t][0] for t in TIMES]; H = [raw[t][1] for t in TIMES]
    L = [raw[t][2] for t in TIMES]; C = [raw[t][3] for t in TIMES]
    V = [raw[t][4] for t in TIMES]
    has_vol = all(v is not None for v in V) and sum(V) > 0
    # premium VWAP (trailing, within-day)
    vw = []
    cum_pv = cum_v = cum_tp = 0.0
    for i in range(len(TIMES)):
        tp = (H[i] + L[i] + C[i]) / 3.0
        cum_tp += tp
        if has_vol:
            cum_pv += tp * V[i]; cum_v += V[i]
            vw.append(cum_pv / cum_v if cum_v > 0 else tp)
        else:
            vw.append(cum_tp / (i + 1))
    # premium RSI(14), Wilder, within-day closes
    rsi = [None] * len(TIMES)
    if len(C) > 14:
        gains = [max(C[i] - C[i - 1], 0.0) for i in range(1, len(C))]
        losses = [max(C[i - 1] - C[i], 0.0) for i in range(1, len(C))]
        ag = sum(gains[:14]) / 14; al = sum(losses[:14]) / 14
        def _r(a, b):
            return 100.0 if b == 0 else 100.0 - 100.0 / (1.0 + a / b)
        rsi[14] = _r(ag, al)
        for i in range(15, len(C)):
            ag = (ag * 13 + gains[i - 1]) / 14
            al = (al * 13 + losses[i - 1]) / 14
            rsi[i] = _r(ag, al)
    return dict(day=day, typ=typ, strike=strike, expiry=exp, src=src,
                vwap_mode="volume" if has_vol else "ew_proxy",
                O=O, H=H, L=L, C=C, V=V, VWAP=vw, RSI=rsi,
                or_high=max(H[:7]), or_low=min(L[:7]))

# ---------------- day cache ----------------
_day = {}
def get_day(day):
    if day not in _day:
        _day[day] = {typ: load_side(day, typ) for typ in ("CE", "PE")}
    return _day[day]

# ---------------- signals ----------------
def side_triggers(s):
    """First P1 and first P2 trigger indices for one contract-day."""
    p1 = p2 = None
    C, VW, RSI = s["C"], s["VWAP"], s["RSI"]
    for i, t in enumerate(TIMES):
        if p1 is None and t >= "09:50":
            if C[i] > s["or_high"] and C[i] > VW[i]:
                p1 = i
        if p2 is None and i >= 15 and RSI[i] is not None and RSI[i - 1] is not None:
            if C[i] > VW[i] and (C[i] - C[i - 3]) > 0 and \
                    RSI[i - 1] <= 50 and RSI[i] > 50:
                p2 = i
        if p1 is not None and p2 is not None:
            break
    return p1, p2

def day_triggers(day):
    """All triggers of the day: list of (time, rule_priority, side,
    rule, signal_idx, side_series). Plus late flags per book."""
    sides = get_day(day)
    trigs = []
    for typ in ("CE", "PE"):
        s = sides[typ]
        if s is None:
            continue
        p1, p2 = side_triggers(s)
        if p1 is not None:
            trigs.append((TIMES[p1], 0, typ, "P1", p1, s))
        if p2 is not None:
            trigs.append((TIMES[p2], 1, typ, "P2", p2, s))
    trigs.sort(key=lambda x: (x[0], x[1], x[2]))
    return trigs

def pick(trigs, rule=None):
    """First tradeable trigger (signal <= 15:10) for a book.
    Returns (trigger, late_flag)."""
    cand = [t for t in trigs if rule is None or t[3] == rule]
    if not cand:
        return None, False
    first = cand[0]
    if first[0] > "15:10":
        return None, True
    return first, False

# ---------------- exits ----------------
def score_exit(s, sig_i, exit_kind):
    ei = sig_i + 1
    if ei > SQ_IDX:
        return None
    entry_px = s["O"][ei]
    VW = s["VWAP"]
    for j in range(ei, SQ_IDX + 1):
        o, h, l, c = s["O"][j], s["H"][j], s["L"][j], s["C"][j]
        if exit_kind == "X1":
            if l <= entry_px - 50.0:
                return entry_px, entry_px - 50.0, TIMES[j], "stop"
            if h >= entry_px + 90.0:
                return entry_px, entry_px + 90.0, TIMES[j], "target"
            if j == SQ_IDX:
                return entry_px, c, TIMES[j], "squareoff"
        else:  # X2
            if l <= entry_px - 60.0:
                return entry_px, entry_px - 60.0, TIMES[j], "hard_stop"
            if c < VW[j]:
                return entry_px, c, TIMES[j], "vwap_loss"
            if j == SQ_IDX:
                return entry_px, c, TIMES[j], "squareoff"
    return None

def make_trade(day, trig, exit_kind):
    t, _prio, typ, rule, sig_i, s = trig
    r = score_exit(s, sig_i, exit_kind)
    if r is None:
        return None
    entry_px, exit_px, xt, reason = r
    return dict(book=None, rule=rule, exit=exit_kind, date=day, side=typ,
                strike=s["strike"], expiry=s["expiry"], src=s["src"],
                vwap_mode=s["vwap_mode"], signal_time=t,
                entry_time=TIMES[sig_i + 1], entry_px=entry_px,
                exit_time=xt, exit_px=exit_px, exit_reason=reason,
                net=round((exit_px - entry_px) * LOT - COST, 2))

# ---------------- run a window ----------------
BOOKS = [("P1", "P1"), ("P2", "P2"), ("COMB", None)]
def run_window(days):
    trades = {f"{b}-{x}": [] for b, _ in BOOKS for x in ("X1", "X2")}
    cnt = dict(days=len(days), side_nc_CE=0, side_nc_PE=0,
               both_nc_days=0, late={f"{b}": 0 for b, _ in BOOKS},
               unscored={f"{b}-{x}": 0 for b, _ in BOOKS
                         for x in ("X1", "X2")},
               triggers_audited=0)
    audit_keys = set()
    for day in days:
        sides = get_day(day)
        if sides["CE"] is None:
            cnt["side_nc_CE"] += 1
        if sides["PE"] is None:
            cnt["side_nc_PE"] += 1
        if sides["CE"] is None and sides["PE"] is None:
            cnt["both_nc_days"] += 1
            continue
        trigs = day_triggers(day)
        for bname, rule in BOOKS:
            trig, late = pick(trigs, rule)
            if late:
                cnt["late"][bname] += 1
                continue
            if trig is None:
                continue
            audit_keys.add((day, trig[2], trig[3], trig[4]))
            for x in ("X1", "X2"):
                tr = make_trade(day, trig, x)
                if tr is None:
                    cnt["unscored"][f"{bname}-{x}"] += 1
                else:
                    tr["book"] = bname
                    trades[f"{bname}-{x}"].append(tr)
    cnt["triggers_audited"] = len(audit_keys)
    return trades, cnt, audit_keys

# ---------------- timing audit (truncated recomputation) ----------------
def audit(audit_keys):
    bad = []
    for day, typ, rule, sig_i in sorted(audit_keys):
        s = get_day(day)[typ]
        sub = dict(s)
        sub["C"] = s["C"][:sig_i + 1]; sub["H"] = s["H"][:sig_i + 1]
        sub["L"] = s["L"][:sig_i + 1]; sub["V"] = s["V"][:sig_i + 1]
        # recompute VWAP + RSI on truncated arrays
        C, H, L, V = sub["C"], sub["H"], sub["L"], sub["V"]
        has_vol = all(v is not None for v in V) and sum(V) > 0
        cum_pv = cum_v = cum_tp = 0.0; vw = None
        for i in range(len(C)):
            tp = (H[i] + L[i] + C[i]) / 3.0
            cum_tp += tp
            if has_vol:
                cum_pv += tp * V[i]; cum_v += V[i]
                vw = cum_pv / cum_v if cum_v > 0 else tp
            else:
                vw = cum_tp / (i + 1)
        ok = abs(vw - s["VWAP"][sig_i]) < 1e-9
        if rule == "P1":
            ok = ok and abs(max(H[:7]) - s["or_high"]) < 1e-9
        if rule == "P2":
            gains = [max(C[i] - C[i - 1], 0.0) for i in range(1, len(C))]
            losses = [max(C[i - 1] - C[i], 0.0) for i in range(1, len(C))]
            ag = sum(gains[:14]) / 14; al = sum(losses[:14]) / 14
            def _r(a, b):
                return 100.0 if b == 0 else 100.0 - 100.0 / (1.0 + a / b)
            rsi = _r(ag, al)
            for i in range(15, len(C)):
                ag = (ag * 13 + gains[i - 1]) / 14
                al = (al * 13 + losses[i - 1]) / 14
                rsi = _r(ag, al)
            ok = ok and abs(rsi - s["RSI"][sig_i]) < 1e-9
        if not ok:
            bad.append((day, typ, rule, sig_i))
    return bad

# ---------------- stats ----------------
def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = sum(t["net"] for t in trades)
    tdays = len(set(t["date"] for t in trades))
    months = {}
    for t in trades:
        months[t["date"][:7]] = months.get(t["date"][:7], 0.0) + t["net"]
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                total=round(total, 2), trade_days=tdays,
                per_td=round(total / tdays, 2) if tdays else 0.0,
                jan_jun=round(sum(t["net"] for t in trades
                                  if t["date"][:7] <= "2026-06"), 2),
                jul_oct=round(sum(t["net"] for t in trades
                                  if t["date"][:7] >= "2026-07"), 2),
                months={k: round(v, 2) for k, v in sorted(months.items())})

def win_stats(trades, lo, hi):
    sel = [t for t in trades if lo <= t["date"][:7] <= hi]
    return stats(sel)

# ---------------- main ----------------
gate_trades, gcnt, audit_keys = run_window(GATE_DAYS)
nov_trades, ncnt, nov_audit_keys = run_window(NOV_DAYS)
bad = audit(audit_keys | nov_audit_keys)
if bad:
    print("TIMING AUDIT FAILED:", bad[:5])
    sys.exit(1)
print(f"timing audit: PASS ({len(audit_keys | nov_audit_keys)} triggers recomputed from truncated series)")

results = {}
for bk, trs in gate_trades.items():
    results[bk] = dict(
        full=stats(trs),
        jan_jun=win_stats(trs, "2026-01", "2026-06"),
        jul_oct=win_stats(trs, "2026-07", "2026-10"),
        nov=stats(nov_trades[bk]))
ORDER = ["P1-X1", "P1-X2", "P2-X1", "P2-X2", "COMB-X1", "COMB-X2"]
best_book = max(ORDER, key=lambda b: results[b]["full"]["total"])

# ---------------- placebo on the best book ----------------
best_trades = gate_trades[best_book]
exit_kind = best_book.split("-")[1]
scoreable_days = []
for d in GATE_DAYS:
    sides = get_day(d)
    ok = [typ for typ in ("CE", "PE") if sides[typ] is not None]
    if ok:
        scoreable_days.append((d, ok))
rng = random.Random(SEED)
entry_idxs = [i for i, t in enumerate(TIMES) if "09:20" <= t <= "15:15"]
p_totals, p_drops = [], 0
for _ in range(500):
    tot = 0.0
    for _rt in best_trades:
        got = None
        for _a in range(51):
            d, oks = rng.choice(scoreable_days)
            typ = rng.choice(oks)
            ei = rng.choice(entry_idxs)
            s = get_day(d)[typ]
            r = score_exit(s, ei - 1, exit_kind)  # entry at bar ei
            if r is not None:
                got = (r[1] - r[0]) * LOT - COST
                break
        if got is None:
            p_drops += 1
        else:
            tot += got
    p_totals.append(round(tot, 2))
p_totals.sort()
real = results[best_book]["full"]["total"]
pct = round(100.0 * sum(1 for x in p_totals if x < real) / len(p_totals), 1)

out = dict(spec="premium_tape_bank_SPEC.md",
           basis="paper, buying only, 1 lot (30), Rs220/trade",
           gate_days=len(GATE_DAYS), counts=gcnt, nov_counts=ncnt,
           timing_audit=f"PASS ({len(audit_keys | nov_audit_keys)} triggers)",
           books=results, best_book=best_book,
           placebo=dict(book=best_book, percentile=pct, drops=p_drops,
                        p50=p_totals[250], p95=p_totals[474],
                        max=p_totals[-1]),
           trades={bk: trs for bk, trs in gate_trades.items()},
           nov_trades={bk: trs for bk, trs in nov_trades.items()})
json.dump(out, open(TR / "premium_tape_bank_results.json", "w"), indent=1)
with open(TR / "premium_tape_bank_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["book", "rule", "exit", "date", "side", "strike",
                "expiry", "src", "vwap_mode", "signal_time", "entry_time",
                "entry_px", "exit_time", "exit_px", "exit_reason", "net"])
    for bk in ORDER:
        for t in gate_trades[bk]:
            w.writerow([t["book"], t["rule"], t["exit"], t["date"],
                        t["side"], t["strike"], t["expiry"], t["src"],
                        t["vwap_mode"], t["signal_time"], t["entry_time"],
                        t["entry_px"], t["exit_time"], t["exit_px"],
                        t["exit_reason"], t["net"]])
print(json.dumps({bk: results[bk]["full"] for bk in ORDER}, indent=1))
print("counts:", json.dumps(gcnt))
print("nov:", json.dumps({bk: results[bk]["nov"] for bk in ORDER}, indent=1))
print("best:", best_book, "| placebo:", out["placebo"])
