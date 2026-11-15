#!/usr/bin/env python3
"""ROUND 3 WORKSTREAM 2 (BANKNIFTY ONLY): mechanical regeneration of the
unbuilt setups from stored 5-min spot. Definitions frozen in
bank_engine_frozen.md (ROUND 3 appendix) BEFORE scoring:
- S3-A/B/C/D/E: Setup 3 wide-candle bounce rejection variants (PE).
- S4: Setup 4 gap-down bear-trap / Blue-Line reclaim (CE), v4 rules isolated.
- S1RB: Setup 1 retest-hold on Red bands DERIVED from intraday spot.
Common: bias from prior-day closing strength; entry = open of the first
5-min option candle strictly after the signal candle; strike ATM at the
signal close (100 ITM on the expiry day); entry window <= 14:30; room >= 200.
Emits candidate legs in the standard leg format; fetching/scoring is done by
the driver (bank_r3_ws2.py) through bank_r3_core.judge."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import EXPIRIES

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"

def load_spot():
    frames = []
    for d in sorted((TR / "data").glob("banknifty-2026-*")):
        f = d / "spot_5m.csv"
        if f.exists():
            frames.append(pd.read_csv(f, parse_dates=["timestamp"]))
    spot = pd.concat(frames).sort_values("timestamp").reset_index(drop=True)
    spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    daily = {}
    for d in sorted((TR / "data").glob("banknifty-2026-*")):
        f = d / "spot_daily.csv"
        if f.exists():
            for r in pd.read_csv(f).to_dict("records"):
                daily[str(r["date"])[:10]] = r
    return spot, daily

SPOT, DAILY = load_spot()
DAYS = sorted(SPOT["date"].unique())
DAY_BARS = {d: g.reset_index(drop=True) for d, g in SPOT.groupby("date")}

def day_ctx(date):
    i = DAYS.index(date)
    if i == 0: return None
    prev = DAILY.get(DAYS[i - 1])
    if prev is None: return None
    pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    allowed = {"PE"} if cs < 35 else ({"CE"} if cs >= 80 else {"CE", "PE"})
    bars = DAY_BARS[date]
    orc = bars[bars["time"] < "09:30"]
    if orc.empty: return None
    return dict(pdh=pdh, pdc=pdc, pdl=pdl, cs=cs, allowed=allowed, bars=bars,
                orh=float(orc["high"].max()), orl=float(orc["low"].min()),
                day_open=float(bars.iloc[0]["open"]))

def mkleg(date, direction, sig_bar, variant):
    close = float(sig_bar["close"])
    expiry = next(e for e in EXPIRIES if e >= date)
    strike = int(round(close / 100.0) * 100)
    if date == expiry:
        strike += -100 if direction == "CE" else 100
    hh, mm = map(int, sig_bar["time"].split(":"))
    entry_time = f"{hh + (mm + 5) // 60:02d}:{(mm + 5) % 60:02d}"
    return dict(date=date, index=SYM, direction=direction, entry_time=entry_time,
                signal_time=f"{date} {sig_bar['time']}:00", strike=strike,
                expiry=expiry, lot=30, rep=variant, sources="R3WS2",
                family=variant, entry_spot=close)

# ---------------- Setup 3 variants ----------------
def setup3(date, width_lo, width_hi, mode):
    """mode: R1 (v4 close rejection), WICK (bounce candle is the signal),
    PDC (close back below PDC). Returns a leg or None."""
    ctx = day_ctx(date)
    if ctx is None or "PE" not in ctx["allowed"]: return None
    width = ctx["orh"] - ctx["orl"]
    if not (width_lo <= width <= width_hi): return None
    bars = ctx["bars"]; orh, pdc, pdl = ctx["orh"], ctx["pdc"], ctx["pdl"]
    bounce_hi = orh + 100.0
    bounced = False
    day_low = float("inf")
    for _, b in bars.iterrows():
        t = b["time"]
        if t < "09:30": continue
        if t > "14:30": break
        hi, lo, op, cl = float(b["high"]), float(b["low"]), float(b["open"]), float(b["close"])
        day_low = min(day_low, lo)
        if mode == "WICK":
            if orh <= hi <= bounce_hi:
                body = abs(cl - op); wick = hi - max(op, cl)
                if body > 0 and wick >= 1.5 * body and cl < orh and cl < op:
                    room = cl - (pdc if cl > pdc else pdl)
                    if room >= 200: return mkleg(date, "PE", b, "S3-WICK")
                bounced = True
            continue
        if orh <= hi <= bounce_hi: bounced = True
        if not bounced: continue
        if mode == "R1":
            if cl < op and cl < orh:
                room = cl - (pdc if cl > pdc else pdl)
                if room >= 200: return mkleg(date, "PE", b, "S3-R1")
        elif mode == "PDC":
            if cl < op and cl < pdc:
                room = (cl - pdl) if cl > pdl else (cl - day_low)
                if room >= 200: return mkleg(date, "PE", b, "S3-PDC")
    return None

# ---------------- Setup 4 ----------------
def setup4(date, both_lines=True):
    ctx = day_ctx(date)
    if ctx is None or "CE" not in ctx["allowed"]: return None
    if ctx["day_open"] >= ctx["pdc"]: return None
    if both_lines and ctx["day_open"] >= ctx["pdl"]: return None
    bars = ctx["bars"]; orh, pdc, pdl, pdh = ctx["orh"], ctx["pdc"], ctx["pdl"], ctx["pdh"]
    levels = [pdh, pdc, pdl]
    reclaimed = False
    for _, b in bars.iterrows():
        t = b["time"]
        if t < "09:30": continue
        if t > "14:30": break
        lo, op, cl = float(b["low"]), float(b["open"]), float(b["close"])
        tag = "S4" if both_lines else "S4B"
        if reclaimed:
            for lvl in (pdc, pdl):
                if abs(lo - lvl) <= 40 and cl > lvl and cl > op:
                    above = [l for l in levels if l > cl]
                    room = (min(above) - cl) if above else float("inf")
                    if room >= 200: return mkleg(date, "CE", b, tag + "-PULLBACK")
        if cl > orh and cl > pdc and cl > pdl:
            if not reclaimed and cl < pdh:
                above = [l for l in levels if l > cl]
                room = (min(above) - cl) if above else float("inf")
                if room >= 200: return mkleg(date, "CE", b, tag + "-RECLAIM")
            reclaimed = True
    return None

# ---------------- Red bands from intraday spot + Setup 1 ----------------
def derive_bands(date, lookback_days=10):
    i = DAYS.index(date)
    if i < 1: return []
    window_days = DAYS[max(0, i - lookback_days):i]
    bars = pd.concat([DAY_BARS[d] for d in window_days]).reset_index(drop=True)
    highs = bars["high"].tolist(); closes = bars["close"].tolist(); lows = bars["low"].tolist()
    prints = []  # (swing_value, swing_idx)
    for j in range(3, len(bars) - 3):
        h = highs[j]
        if all(h > highs[j - k] for k in (1, 2, 3)) and all(h > highs[j + k] for k in (1, 2, 3)):
            ok = False
            for k in range(j + 1, min(j + 13, len(bars))):
                if closes[k] > h: break
                if h - lows[k] >= 150.0: ok = True; break
            if ok: prints.append((h, j))
    prints.sort()
    clusters = []
    for val, j in prints:
        if clusters and val - clusters[-1][-1][0] <= 50.0:
            clusters[-1].append((val, j))
        else:
            clusters.append([(val, j)])
    day_open = float(DAY_BARS[date].iloc[0]["open"])
    live = []
    for cl_ in clusters:
        lo = min(v for v, _ in cl_) - 15.0; hi = max(v for v, _ in cl_) + 15.0
        newest = max(j for _, j in cl_)
        if hi <= day_open: continue
        if any(closes[k] > hi for k in range(newest + 1, len(bars))): continue
        live.append((lo, hi))
    live.sort()
    return live[:3]

def setup1rb(date):
    ctx = day_ctx(date)
    if ctx is None or "CE" not in ctx["allowed"]: return None
    bands = derive_bands(date)
    if not bands: return None
    bars = ctx["bars"]; orh = ctx["orh"]
    levels = sorted(set([ctx["pdh"], ctx["pdc"], ctx["pdl"]] + [v for b in bands for v in b]))
    orc = bars[bars["time"] < "09:30"]
    band_broken = None
    for _, c in orc.iterrows():
        for lo, hi in bands:
            if float(c["close"]) >= lo - 10: band_broken = (lo, hi)
    if band_broken is None: return None
    lo_b, hi_b = band_broken
    retest = False
    for _, b in bars.iterrows():
        t = b["time"]
        if t < "09:30": continue
        if t > "14:30": break
        lo, op, cl = float(b["low"]), float(b["open"]), float(b["close"])
        if not retest and lo <= hi_b and lo >= lo_b - 50 and cl > hi_b:
            retest = True; continue
        if retest and cl > orh and cl > op:
            above = [l for l in levels if l > cl]
            room = (min(above) - cl) if above else float("inf")
            if room >= 200:
                leg = mkleg(date, "CE", b, "S1-RB")
                leg["band"] = f"{lo_b}-{hi_b}"
                return leg
    return None

FAMILIES = {
    "S3A": lambda d: setup3(d, 400.0, float("inf"), "R1"),
    "S3B": lambda d: setup3(d, 350.0, 580.0, "R1"),
    "S3C": lambda d: setup3(d, 400.0, 650.0, "R1"),
    "S3D": lambda d: setup3(d, 400.0, 580.0, "WICK"),
    "S3E": lambda d: setup3(d, 400.0, 580.0, "PDC"),
    "S4": lambda d: setup4(d, both_lines=True),
    "S4B": lambda d: setup4(d, both_lines=False),
    "S1RB": setup1rb,
}

def generate():
    out = {k: [] for k in FAMILIES}
    for d in DAYS:
        if DAILY.get(d) is None: continue
        for name, fn in FAMILIES.items():
            leg = fn(d)
            if leg: out[name].append(leg)
    return out

if __name__ == "__main__":
    g = generate()
    for k, v in g.items():
        print(k, len(v), "legs")
