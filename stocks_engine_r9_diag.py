#!/usr/bin/env python3
"""ROUND 9 — diagnosis behind WS1/WS3 (audit, no candidate scored).

WS0 proved both stack flips belong to NE-REV-CERT alone. This
script decomposes NE-REV-CERT's rows (and the IDX subset's) by
state features — regime cell, signal-move band, NIFTY 10:25
state, the stock's prior-day return, name — over the full
population and inside Jan-2025 / Dec-2025, so the conditioned
variants frozen in the Round-9 pre-registration rest on stated
separators, not on month names.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r7_builders as B7
import stocks_engine_r8_builders as B8
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
cert = ing["cert"]          # raw NE-REV rows (comp NE-REV)
books = ing["books"]

# Rebuild per-row features: signal move + prior-day stock return.
g = B7.machinery()
STOCKS_E = g["STOCKS_E"]
feat = {}
for sym, (spot, daily) in STOCKS_E.items():
    didx = {d["date"]: i for i, d in enumerate(daily)}
    for day, i in didx.items():
        if i == 0:
            continue
        bars = spot.get(day, [])
        idx = {b["time"]: k for k, b in enumerate(bars)}
        pc = daily[i - 1]["close"]
        if "10:25" not in idx or not pc:
            continue
        mv = (bars[idx["10:25"]]["close"] / pc - 1) * 100
        pd = None
        if i >= 2 and daily[i - 2]["close"]:
            pd = (daily[i - 1]["close"] / daily[i - 2]["close"]
                  - 1) * 100
        feat[(sym, day)] = (mv, pd)

def enrich(rows):
    out = []
    for t in rows:
        mv, pd = feat.get((t["stock"], t["date"]), (None, None))
        out.append({**t, "move": mv, "pdret": pd,
                    "cell": R9.LABELS.get(t["date"]),
                    "nifty": B8.nifty_move(t["date"], "10:25")})
    return out

def band(mv):
    if mv is None:
        return "?"
    a = abs(mv)
    return "[2,2.5)" if a < 2.5 else ("[2.5,3.5)" if a < 3.5
                                      else ">=3.5")

def nbucket(x):
    if x is None:
        return "?"
    return "<=-0.30" if x <= -0.30 else ("(-0.30,0)" if x < 0
                                         else ">=0")

def pdbucket(x):
    if x is None:
        return "?"
    return "prior-down" if x < 0 else "prior-up/flat"

def summ(rows, keyfn, title):
    agg = {}
    for t in rows:
        k = keyfn(t)
        a = agg.setdefault(k, [0, 0.0])
        a[0] += 1
        a[1] = round(a[1] + t["net"], 2)
    print(f"  {title}: " + " | ".join(
        f"{k}: {v[0]} tr {v[1]:+.2f}" for k, v in sorted(agg.items())))

for yr in (2025, 2026):
    rows = enrich(cert[yr])
    jan = [t for t in rows if t["date"][:7] == f"{yr}-01"]
    dec = [t for t in rows if t["date"][:7] == f"{yr}-12"]
    print(f"\n##### NE-REV-CERT {yr}: {len(rows)} rows, net "
          f"{round(sum(t['net'] for t in rows), 2)}")
    summ(rows, lambda t: t["cell"], "by regime cell (full year)")
    summ(rows, lambda t: band(t["move"]), "by |move| band")
    summ(rows, lambda t: nbucket(t["nifty"]), "by NIFTY 10:25 state")
    summ(rows, lambda t: pdbucket(t["pdret"]),
         "by stock prior-day return")
    if yr == 2025:
        for nm, sub in (("JAN", jan), ("DEC", dec)):
            print(f"  -- {nm} 2025: {len(sub)} rows, net "
                  f"{round(sum(t['net'] for t in sub), 2)}")
            summ(sub, lambda t: t["cell"], "   by cell")
            summ(sub, lambda t: band(t["move"]), "   by band")
            summ(sub, lambda t: nbucket(t["nifty"]),
                 "   by NIFTY state")
            summ(sub, lambda t: pdbucket(t["pdret"]),
                 "   by prior-day")
            summ(sub, lambda t: t["stock"], "   by name")

# IDX subset, December 2025 rows in detail (WS3).
idx = {yr: enrich(ing["idx_r"][yr]) for yr in (2025, 2026)}
print("\n##### NE-REV-IDX December rows")
for yr in (2025, 2026):
    dec = [t for t in idx[yr] if t["date"][:7] == f"{yr}-12"]
    print(f"  {yr}-12: {len(dec)} rows, net "
          f"{round(sum(t['net'] for t in dec), 2)}")
    for t in sorted(dec, key=lambda x: x["date"]):
        print(f"    {t['date']} {t['stock']:12} net {t['net']:+9.2f} "
              f"cell {t['cell']} move {t['move']} "
              f"nifty {None if t['nifty'] is None else round(t['nifty'], 3)} "
              f"pdret {None if t['pdret'] is None else round(t['pdret'], 2)}")
    summ(dec, lambda t: t["cell"], "   by cell")
    summ(dec, lambda t: band(t["move"]), "   by band")

# CERT December 2025 rows in detail.
print("\n##### NE-REV-CERT December 2025 rows in detail")
dec25 = [t for t in enrich(cert[2025]) if t["date"][:7] == "2025-12"]
for t in sorted(dec25, key=lambda x: x["date"]):
    print(f"    {t['date']} {t['stock']:12} net {t['net']:+9.2f} "
          f"cell {t['cell']} move {t['move']} "
          f"nifty {None if t['nifty'] is None else round(t['nifty'], 3)} "
          f"pdret {None if t['pdret'] is None else round(t['pdret'], 2)}")
print("\n##### NE-REV-CERT January 2025 rows by name")
jan25 = [t for t in enrich(cert[2025]) if t["date"][:7] == "2025-01"]
summ(jan25, lambda t: t["stock"], "   by name")
