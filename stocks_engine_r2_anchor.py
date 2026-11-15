#!/usr/bin/env python3
"""ROUND 2 — STAGE 0: ANCHORS.
Rebuild the v2 book via the audited logger machinery on data/full_hist,
apply v3 law + FLOOR-2/FLOOR-4, and assert per-component multiset equality
with the FLOOR-C4 books of record. Also build INV-R3 from run_chain to pin
its exact law. No scoring of any variant happens here.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import sys, json
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_floor_lib as FL

g = L.load_machinery(L.FULLHIST, "2026-10-28")
DAYCTX = g["DAYCTX"]
days25 = sorted({d for (s, d) in DAYCTX if d.startswith("2025")})
days26 = sorted({d for (s, d) in DAYCTX if d.startswith("2026")})
print("days:", len(days25), "2025 /", len(days26), "2026")

CAL25 = f"{WS}/stock_event_calendar_2025.csv"
CAL26 = f"{WS}/stock_event_calendar_jan_oct_2026.csv"

# v3 exclusions (state v3.law_added), beyond the logger's v2 apply_law
V3_DROP = {
    ("INV-ABOVE", "PFC", "LONG"), ("INV-ABOVE", "RECLTD", "LONG"),
    ("N4-V3", "INDUSTOWER", "LONG"), ("N4-V3", "OIL", "SHORT"),
    ("N4-V3", "VEDL", "SHORT"),
    ("P2F", "OBEROIRLTY", "LONG"), ("P2F", "GODREJCP", "LONG"),
    ("P2F", "UNITDSPR", "LONG"),
    ("P2F-R2", "OBEROIRLTY", "LONG"), ("P2F-R2", "BDL", "LONG"),
    ("P2F-R2", "GODREJCP", "LONG"), ("P2F-R2", "TVSMOTOR", "SHORT"),
    ("P2F-R2", "GLENMARK", "LONG"),
    ("R2-LOWBAND", "TVSMOTOR", "LONG"),
}
# v2 N4 exclusions NOT in the logger's EXCL_V2 (from state v2.law_added) —
# tested empirically below: applied only if the anchor fails without them.
V2_N4_DROP = {
    ("N4-V3", "GLENMARK", "SHORT"), ("N4-V3", "BDL", "SHORT"),
    ("N4-V3", "HINDALCO", "SHORT"), ("N4-V3", "HINDZINC", "LONG"),
    ("N4-V3", "UNITDSPR", "LONG"), ("N4-V3", "RECLTD", "LONG"),
    ("N4-V3", "WIPRO", "SHORT"),
}

def ms(rows):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2)) for t in rows)

def load_c4(yr):
    return FL.load(f"stocks_engine_floor_c4_book{yr}_trades.csv")

def floor_law(rows):
    """FLOOR-4 (N4 x HDFCBANK x LONG out) + FLOOR-2 (N4 LONG signed
    move-by-09:30 >= +3.0% out). Returns filtered rows."""
    out = []
    for t in rows:
        if t["comp"] == "N4-V3" and t["stock"] == "HDFCBANK" and t["dir"] == "LONG":
            continue
        if t["comp"] == "N4-V3" and t["dir"] == "LONG":
            mv = FL.n4_move(t["stock"], t["date"])
            if mv is not None and mv >= 3.0:
                continue
        out.append(t)
    return out

def build_year(cal, lo, hi, days):
    rows = L.build_book(g, cal, lo, hi, days)
    return [{**t} for t in rows]

report = {}
for yr, cal, lo, hi, days in ((2025, CAL25, "2025-01-01", "2025-12-31", days25),
                              (2026, CAL26, "2026-01-01", "2026-10-28", days26)):
    built = build_year(cal, lo, hi, days)
    c4 = load_c4(yr)
    # INV-R3 is not built by the logger path; compare the other comps first
    built_x = [t for t in built]
    c4_x = [t for t in c4 if t["comp"] != "INV-R3"]
    # try WITHOUT V2_N4_DROP first, then with it
    for label, extra in (("no_v2n4", set()), ("with_v2n4", V2_N4_DROP)):
        drop = V3_DROP | extra
        var = [t for t in built_x if (t["comp"], t["stock"], t["dir"]) not in drop]
        var = floor_law(var)
        a, b = ms(var), ms(c4_x)
        diff_ab, diff_ba = a - b, b - a
        ok = not diff_ab and not diff_ba
        print(f"{yr} [{label}]: built {len(var)} vs C4 {len(c4_x)} — "
              f"extra {sum(diff_ab.values())}, missing {sum(diff_ba.values())}, EQUAL={ok}")
        if not ok:
            byc = defaultdict(int)
            for k, v in diff_ab.items(): byc[k[0]] += v
            for k, v in diff_ba.items(): byc[k[0]] -= v
            print("   net row diff by comp (built-C4):", dict(byc))
        else:
            report[yr] = label
            break
    # per-comp check for the winning variant
    if yr in report:
        drop = V3_DROP | (V2_N4_DROP if report[yr] == "with_v2n4" else set())
        var = floor_law([t for t in built_x if (t["comp"], t["stock"], t["dir"]) not in drop])
        for comp in sorted({t["comp"] for t in c4_x}):
            aa = ms([t for t in var if t["comp"] == comp])
            bb = ms([t for t in c4_x if t["comp"] == comp])
            print(f"   {comp}: {'EQUAL' if aa == bb else 'MISMATCH'} "
                  f"({sum(bb.values())} rows, net {round(sum(float(t['net']) for t in c4_x if t['comp']==comp), 2)})")

print("anchor law variant:", report)

# --- INV-R3 law discovery: round>=3 population under cond_inv1 --------------
def build_inv_r3(days, flat_aside):
    labels = FL.LABELS
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] >= 3 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    out = []
    for r in pop:
        if not g["cond_inv1"](r["date"]): continue
        if r["direction"] != "LONG": continue
        if g["wk"](r["date"]): continue
        if r["stock"] in {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}: continue
        if r["stock"] in {"HINDALCO", "UNITDSPR", "TATASTEEL"}: continue
        if flat_aside and labels.get(r["date"]) == "FLAT": continue
        out.append({"comp": "INV-R3", "date": r["date"], "stock": r["stock"],
                    "dir": "LONG", "entry_time": r["entry_time"],
                    "net": round(float(r["net"]), 2)})
    return out

for flat_aside in (True, False):
    ok_all = True
    for yr, days in ((2025, days25), (2026, days26)):
        built = build_inv_r3(days, flat_aside)
        built = [t for t in built if t["date"].startswith(str(yr))]
        c4r3 = [t for t in load_c4(yr) if t["comp"] == "INV-R3"]
        eq = ms(built) == ms(c4r3)
        ok_all = ok_all and eq
        print(f"INV-R3 flat_aside={flat_aside} {yr}: built {len(built)} vs C4 {len(c4r3)} EQUAL={eq}")
    if ok_all:
        print("INV-R3 law pinned: flat_aside =", flat_aside)
        break
