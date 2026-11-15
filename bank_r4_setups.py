#!/usr/bin/env python3
"""ROUND 4 Workstream 3: Setup-3 completion cells. A parameterised clone of
bank_r3_setups.setup3 — at (wick_ratio=1.5, depth=0) it must reproduce the
Round-3 S3-A / S3-D / S3-E leg sets exactly (asserted below). New cells vary
ONLY the wick-ratio threshold (WICK mode) or the close-back-inside depth
(R1 / PDC modes); band (400, 580) and every other rule are the frozen
Round-3 definitions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r3_setups import day_ctx, mkleg, generate as gen_r3, DAYS, DAILY

def setup3_r4(date, width_lo, width_hi, mode, wick_ratio=1.5, depth=0.0, tag="S3X"):
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
                if body > 0 and wick >= wick_ratio * body and cl < orh and cl < op:
                    room = cl - (pdc if cl > pdc else pdl)
                    if room >= 200: return mkleg(date, "PE", b, tag)
                bounced = True
            continue
        if orh <= hi <= bounce_hi: bounced = True
        if not bounced: continue
        if mode == "R1":
            if cl < op and cl < orh and (orh - cl) >= depth:
                room = cl - (pdc if cl > pdc else pdl)
                if room >= 200: return mkleg(date, "PE", b, tag)
        elif mode == "PDC":
            if cl < op and cl < pdc and (pdc - cl) >= depth:
                room = (cl - pdl) if cl > pdl else (cl - day_low)
                if room >= 200: return mkleg(date, "PE", b, tag)
    return None

CELLS = {
    "S3F": lambda d: setup3_r4(d, 400.0, 580.0, "WICK", wick_ratio=2.0, tag="S3-WICK20"),
    "S3G": lambda d: setup3_r4(d, 400.0, 580.0, "WICK", wick_ratio=1.25, tag="S3-WICK125"),
    "S3H": lambda d: setup3_r4(d, 400.0, 580.0, "R1", depth=25.0, tag="S3-R1D25"),
    "S3I": lambda d: setup3_r4(d, 400.0, 580.0, "R1", depth=50.0, tag="S3-R1D50"),
    "S3J": lambda d: setup3_r4(d, 400.0, 580.0, "PDC", depth=25.0, tag="S3-PDCD25"),
}

def generate_r4():
    out = {k: [] for k in CELLS}
    for d in DAYS:
        if DAILY.get(d) is None: continue
        for name, fn in CELLS.items():
            leg = fn(d)
            if leg: out[name].append(leg)
    return out

if __name__ == "__main__":
    r3 = gen_r3()
    rep_a = [setup3_r4(d, 400.0, float("inf"), "R1", tag="S3-R1") for d in DAYS]
    rep_d = [setup3_r4(d, 400.0, 580.0, "WICK", tag="S3-WICK") for d in DAYS]
    rep_e = [setup3_r4(d, 400.0, 580.0, "PDC", tag="S3-PDC") for d in DAYS]
    key = lambda legs: sorted((l["date"], l["entry_time"]) for l in legs if l)
    assert key(rep_a) == key(r3["S3A"]), "S3-A reproduction failed"
    assert key(rep_d) == key(r3["S3D"]), "S3-D reproduction failed"
    assert key(rep_e) == key(r3["S3E"]), "S3-E reproduction failed"
    print("parameterised clone reproduces S3-A / S3-D / S3-E exactly")
    g = generate_r4()
    for k, v in g.items():
        print(k, len(v), "candidate legs", [(l["date"], l["entry_time"]) for l in v])
