#!/usr/bin/env python3
"""DIAL — BANK NIFTY standalone indicator system, Jan-Oct 2026 gate +
Nov 2-13 CF. Spec: dial_bank_SPEC.md (frozen 2026-11-14 before this
run). Local stores only — NO API calls. Research only: reads stores,
writes dial_bank_results.json + dial_bank_2026-11-14.md only."""
import csv, json, math, random, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
LOT, COST, STOP, TARGET, SQ = 30, 220.0, 50.0, 90.0, "15:20"
STEP = 100
SEED = 20261114

# ---------------- spot (continuous series) ----------------
spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot = spot[(spot["timestamp"] >= "2026-01-01") &
            (spot["timestamp"] <= "2026-11-13")].sort_values("timestamp")
spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
O = spot["open"].to_numpy(float); H = spot["high"].to_numpy(float)
L = spot["low"].to_numpy(float);  C = spot["close"].to_numpy(float)
DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
N = len(C)
day_idx = {}
for i, d in enumerate(DATES):
    day_idx.setdefault(d, []).append(i)
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
    """{time: futures session VWAP through that bar} or None."""
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

# ---------------- indicators (causal, continuous series) ----------------
def wilder_atr(h, l, c, period=7):
    n = len(c); tr = [None] * n; atr = [None] * n
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    if n > period:
        atr[period] = sum(tr[1:period + 1]) / period
        for i in range(period + 1, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def supertrend(h, l, c, period=7, mult=3.0):
    n = len(c); atr = wilder_atr(h, l, c, period)
    direc = [None] * n; fu = [None] * n; fl = [None] * n
    for i in range(n):
        if atr[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2.0
        bu = hl2 + mult * atr[i]; bl = hl2 - mult * atr[i]
        if fu[i - 1] is None:
            fu[i], fl[i] = bu, bl
            direc[i] = "up" if c[i] >= hl2 else "down"
            continue
        fu[i] = bu if (bu < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = bl if (bl > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        if direc[i - 1] == "up":
            direc[i] = "down" if c[i] < fl[i] else "up"
        else:
            direc[i] = "up" if c[i] > fu[i] else "down"
    return direc

def rsi_wilder(c, period=14):
    n = len(c); out = [None] * n
    if n <= period:
        return out
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
    ag = sum(gains[:period]) / period; al = sum(losses[:period]) / period
    def _r(ag_, al_):
        return 100.0 if al_ == 0 else 100.0 - 100.0 / (1.0 + ag_ / al_)
    out[period] = _r(ag, al)
    for i in range(period + 1, n):
        ag = (ag * (period - 1) + gains[i - 1]) / period
        al = (al * (period - 1) + losses[i - 1]) / period
        out[i] = _r(ag, al)
    return out

def bollinger_pctb(c, period=20, mult=2.0):
    n = len(c); out = [None] * n
    for i in range(period - 1, n):
        w = c[i - period + 1:i + 1]
        m = sum(w) / period
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / period)
        up, lo = m + mult * sd, m - mult * sd
        out[i] = 0.5 if up == lo else (c[i] - lo) / (up - lo)
    return out

def ema_series(c, period=50):
    n = len(c); out = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(c[:period]) / period
    for i in range(period, n):
        out[i] = c[i] * k + out[i - 1] * (1 - k)
    return out

ST_DIR = supertrend(H, L, C)
RSI = rsi_wilder(C)
PCTB = bollinger_pctb(C)
EMA50 = ema_series(C)
def ema_slope(i):
    if i < 6 or EMA50[i] is None or EMA50[i - 6] is None:
        return None
    return (EMA50[i] - EMA50[i - 6]) / EMA50[i - 6] * 100.0

# ---------------- timing audit (truncated recomputation) ----------------
def audit_signal_bars(idxs):
    bad = []
    for i in idxs:
        st = supertrend(H[:i + 1], L[:i + 1], C[:i + 1])
        rs = rsi_wilder(C[:i + 1])
        pb = bollinger_pctb(C[:i + 1])
        em = ema_series(C[:i + 1])
        ok = (st[-1] == ST_DIR[i] and
              (rs[-1] is None and RSI[i] is None or
               rs[-1] is not None and RSI[i] is not None and
               abs(rs[-1] - RSI[i]) < 1e-9) and
              (pb[-1] is None and PCTB[i] is None or
               pb[-1] is not None and PCTB[i] is not None and
               abs(pb[-1] - PCTB[i]) < 1e-9) and
              (em[-1] is None and EMA50[i] is None or
               em[-1] is not None and EMA50[i] is not None and
               abs(em[-1] - EMA50[i]) < 1e-6))
        if not ok:
            bad.append(i)
    return bad

# ---------------- helpers ----------------
import bisect
POS = {}
for d, idxs in day_idx.items():
    for p, gi in enumerate(idxs):
        POS[gi] = p

def day_vwap(day):
    raw = vwap_series(day)
    if raw is None:
        return None
    ftimes = sorted(raw)
    out = {}
    for gi in day_idx[day]:
        t = TIMES[gi]
        j = bisect.bisect_right(ftimes, t) - 1
        out[t] = raw[ftimes[j]] if j >= 0 else None
    return out

def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

def scan_day(day, vw):
    """First qualifying T and R signals of the day (strict event
    reading). Returns {comp: (global_idx, side) or 'LATE' or None}."""
    idxs = day_idx[day]
    res = {"T": None, "R": None}
    done = {"T": False, "R": False}
    for pos, gi in enumerate(idxs):
        t = TIMES[gi]
        if not done["T"]:
            if (ST_DIR[gi] is not None and gi > 0 and
                    ST_DIR[gi - 1] is not None and
                    ST_DIR[gi] != ST_DIR[gi - 1]):
                v = vw.get(t) if vw else None
                if v is not None:
                    side = ST_DIR[gi]
                    ok = (side == "up" and C[gi] > v) or \
                         (side == "down" and C[gi] < v)
                    if ok:
                        if t <= "15:10" and pos < len(idxs) - 1:
                            res["T"] = (gi, side)
                        else:
                            res["T"] = "LATE"
                        done["T"] = True
        if not done["R"]:
            r, pb, sl = RSI[gi], PCTB[gi], ema_slope(gi)
            if r is not None and pb is not None and sl is not None:
                side = None
                if r <= 30 and pb <= 0.05 and sl > -0.1:
                    side = "up"
                elif r >= 70 and pb >= 0.95 and sl < 0.1:
                    side = "down"
                if side:
                    if t <= "15:10" and pos < len(idxs) - 1:
                        res["R"] = (gi, side)
                    else:
                        res["R"] = "LATE"
                    done["R"] = True
        if done["T"] and done["R"]:
            break
    return res

def score_trade(day, entry_gi, ref_close, side):
    """Buy nearest-strike contract at entry bar open; walk exits.
    Returns trade dict or None (NC)."""
    strike = int(math.floor(ref_close / STEP + 0.5)) * STEP
    typ = "CE" if side == "up" else "PE"
    exp = EXP[day]
    prem = prem_store(exp, strike, typ, day)
    if not prem:
        return None
    et = TIMES[entry_gi]
    if et not in prem:
        return None
    entry_px = prem[et][0]
    exit_px = reason = xt = None
    m = tmin(et)
    while m <= tmin(SQ):
        t = tstr(m)
        bar = prem.get(t)
        if bar is None:
            return None
        o, h, l, c = bar
        if l <= entry_px - STOP:
            exit_px, reason, xt = entry_px - STOP, "stop", t
            break
        if h >= entry_px + TARGET:
            exit_px, reason, xt = entry_px + TARGET, "target", t
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

def run_window(days):
    trades, audit_bars = [], []
    cnt = dict(sig_T=0, sig_R=0, nc_T=0, nc_R=0, late_T=0, late_R=0,
               vwap_missing_days=0)
    for day in days:
        vw = day_vwap(day)
        if vw is None:
            cnt["vwap_missing_days"] += 1
        sig = scan_day(day, vw)
        for comp in ("T", "R"):
            s = sig[comp]
            if s is None:
                continue
            if s == "LATE":
                cnt[f"late_{comp}"] += 1
                continue
            gi, side = s
            cnt[f"sig_{comp}"] += 1
            audit_bars.append(gi)
            idxs = day_idx[day]
            entry_gi = idxs[POS[gi] + 1]
            tr = score_trade(day, entry_gi, C[gi], side)
            if tr is None:
                cnt[f"nc_{comp}"] += 1
            else:
                tr["comp"] = comp
                tr["signal_time"] = TIMES[gi]
                trades.append(tr)
    return trades, cnt, audit_bars

# ---------------- gate window ----------------
gate_trades, gcnt, audit_idx = run_window(GATE_DAYS)
nov_trades, ncnt, nov_audit_idx = run_window(NOV_DAYS)

bad = audit_signal_bars(sorted(set(audit_idx + nov_audit_idx)))
if bad:
    print("TIMING AUDIT FAILED at bars:", bad[:5])
    sys.exit(1)
print(f"timing audit: PASS ({len(set(audit_idx + nov_audit_idx))} signal bars recomputed from truncated series)")

# ---------------- placebos ----------------
def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = sum(t["net"] for t in trades)
    tdays = len(set(t["date"] for t in trades))
    months = {}
    for t in trades:
        months[t["date"][:7]] = months.get(t["date"][:7], 0.0) + t["net"]
    h1 = sum(t["net"] for t in trades if t["date"][:7] <= "2026-05")
    h2 = sum(t["net"] for t in trades if t["date"][:7] >= "2026-06")
    top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                total=round(total, 2), trade_days=tdays,
                per_td=round(total / tdays, 2) if tdays else 0.0,
                months={k: round(v, 2) for k, v in sorted(months.items())},
                h1=round(h1, 2), h2=round(h2, 2),
                ex_top3=round(total - sum(top3), 2))

comb = stats(gate_trades)
compT = stats([t for t in gate_trades if t["comp"] == "T"])
compR = stats([t for t in gate_trades if t["comp"] == "R"])

rng = random.Random(SEED)
placebo_totals, placebo_drops = [], 0
for _ in range(500):
    tot = 0.0
    for rt in gate_trades:
        tr = None
        for _a in range(51):
            d = rng.choice(GATE_DAYS)
            idxs = day_idx[d]
            cand = [gi for gi in idxs if "09:20" <= TIMES[gi] <= "15:15"]
            ei = rng.choice(cand)
            tr = score_trade(d, ei, C[idxs[POS[ei] - 1]], rt["side"])
            if tr:
                break
        if tr:
            tot += tr["net"]
        else:
            placebo_drops += 1
    placebo_totals.append(tot)
placebo_totals.sort()
real_total = comb["total"]
pct = round(100.0 * sum(1 for x in placebo_totals if x < real_total) /
            len(placebo_totals), 1)

shift_total, shift_drops, shift_scored = 0.0, 0, 0
for rt in gate_trades:
    t2 = tstr(tmin(rt["entry_time"]) + 30)
    if t2 > "15:15":
        shift_drops += 1
        continue
    prem = prem_store(rt["expiry"], rt["strike"], rt["typ"], rt["date"])
    if not prem or t2 not in prem:
        shift_drops += 1
        continue
    fake = dict(rt)
    entry_px = prem[t2][0]
    exit_px = None
    m = tmin(t2)
    while m <= tmin(SQ):
        t = tstr(m)
        bar = prem.get(t)
        if bar is None:
            break
        o, h, l, c = bar
        if l <= entry_px - STOP:
            exit_px = entry_px - STOP; break
        if h >= entry_px + TARGET:
            exit_px = entry_px + TARGET; break
        if t == SQ:
            exit_px = c; break
        m += 5
    if exit_px is None:
        shift_drops += 1
        continue
    shift_total += (exit_px - entry_px) * LOT - COST
    shift_scored += 1
shift_total = round(shift_total, 2)

# ---------------- gate verdict ----------------
red_months = sum(1 for v in comb["months"].values() if v < 0)
legs = [
    ("random-entry placebo >= 95th pct", pct >= 95.0, f"{pct}"),
    ("+30-min shift beaten", real_total > shift_total,
     f"real {real_total} vs shifted {shift_total}"),
    ("both halves positive", comb["h1"] > 0 and comb["h2"] > 0,
     f"H1 {comb['h1']} / H2 {comb['h2']}"),
    ("ex-top-3 positive", comb["ex_top3"] > 0, f"{comb['ex_top3']}"),
    ("Rs/trade-day >= 900", comb["per_td"] >= 900, f"{comb['per_td']}"),
    ("WR >= 60%", comb["wr"] >= 60.0, f"{comb['wr']}"),
    ("monthly pace >= Rs7,500", real_total / 10 >= 7500,
     f"{round(real_total / 10, 2)}"),
    ("red months <= 2", red_months <= 2, f"{red_months}"),
]
verdict = all(ok for _, ok, _ in legs)
failing = [name for name, ok, _ in legs if not ok]

nov = stats(nov_trades)
out = dict(
    spec="dial_bank_SPEC.md", basis="paper, 1 lot (30), Rs220/trade",
    gate_days=len(GATE_DAYS), counts=gcnt,
    timing_audit="PASS",
    combined=comb, comp_T=compT, comp_R=compR,
    placebo_random=dict(percentile=pct, drops=placebo_drops,
                        p50=placebo_totals[250], p95=placebo_totals[474],
                        max=placebo_totals[-1]),
    placebo_shift=dict(total=shift_total, scored=shift_scored,
                       drops=shift_drops),
    gate_legs=[dict(leg=n, passed=bool(ok), detail=d) for n, ok, d in legs],
    verdict="PASS" if verdict else "FAIL", failing=failing,
    red_months=red_months,
    gate_trades=gate_trades, nov_counts=ncnt, nov_stats=nov,
    nov_trades=nov_trades)
json.dump(out, open(TR / "dial_bank_results.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("gate_days", "counts", "combined",
                                      "comp_T", "comp_R", "verdict",
                                      "failing", "nov_stats", "nov_counts")},
                 indent=1))
print("placebo:", out["placebo_random"], "| shift:", out["placebo_shift"])
