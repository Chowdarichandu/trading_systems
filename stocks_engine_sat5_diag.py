#!/usr/bin/env python3
"""ENGINE SAT-5 STEP 1 (diagnosis): verify incumbent anchor vs state
(878 tr, +143,747.36, October +51,364.74, headroom 1,364.74), then
weigh three candidate directions:
 (1) WD-5 pending candidate: F4 x HINDUNILVR x SHORT exclusion
     (watchdog froze it pre-SAT-3; NEVER scored; re-measure at the
     CURRENT book per Lesson 16);
 (2) INV-LONG exit rebuild: load INV-LONG from the tuning loop's
     full exit-grid dumps (same entries, exits T100..T200 x
     S050..S080 + trails) and compare at component + union level;
 (3) P2F exit rebuild: prior evidence only (Lesson 4 / CH-1).
Paper, real Rs0, per 100 sh, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 11378.22, "2026-02": 6130.34, "2026-03": 20269.77,
         "2026-04": 2043.12, "2026-05": 28714.75, "2026-06": 1853.72,
         "2026-07": 3196.63, "2026-08": 878.69, "2026-09": 17917.38,
         "2026-10": 51364.74}
STATE_TOTAL, STATE_TRADES = 143747.36, 878

def filters_inv(trades):
    return [t for t in trades if not wk(t["date"]) and t["stock"] != "BDL"]

inv = filters_inv(M1.load_inv_long())
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "round": r["round"], "entry_time": r["entry_time"],
        "exit_reason": r["exit_reason"], "net": float(r["net"]),
        "premove_pct": float(r["premove_pct"]), "event": r["event"]}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")]
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(float)
    for t in trades: m[t["date"][:7]] += t["net"]
    return {k: round(m[k], 2) for k in sorted(STATE)}

bt = mt(book)
tot = round(sum(t["net"] for t in book), 2)
anchor_ok = bt == STATE and tot == STATE_TOTAL and len(book) == STATE_TRADES
print(f"ANCHOR: {anchor_ok} | trades {len(book)} total {tot} "
      f"| October {bt['2026-10']} headroom {round(bt['2026-10']-50000,2)}")
assert anchor_ok
comp_tot = {c: round(sum(t['net'] for t in book if t['comp'] == c), 2)
            for c in ("INV-LONG", "N4-V3", "P2F", "F4")}
comp_n = {c: sum(1 for t in book if t['comp'] == c)
          for c in ("INV-LONG", "N4-V3", "P2F", "F4")}
print(f"COMPONENTS: {comp_tot} | counts {comp_n}")

out = {"anchor_ok": anchor_ok, "comp_tot": comp_tot, "comp_n": comp_n}

# ---------- (1) WD-5 candidate: F4 x HINDUNILVR x SHORT ----------
sl = [t for t in f4 if t["stock"] == "HINDUNILVR" and t["dir"] == "SHORT"]
sl_m = mt(sl)
rest = [t for t in book
        if not (t["comp"] == "F4" and t["stock"] == "HINDUNILVR"
                and t["dir"] == "SHORT")]
after = mt(rest)
gate1 = {"total": round(sum(t["net"] for t in rest), 2),
         "all_green": all(v > 0 for v in after.values()),
         "october": after["2026-10"],
         "min_month": min(after.values())}
gate1["pass"] = (gate1["total"] > STATE_TOTAL and gate1["all_green"]
                 and gate1["october"] >= 50000)
print(f"\n(1) WD-5 F4 x HINDUNILVR x SHORT: {len(sl)} tr, "
      f"net {round(sum(t['net'] for t in sl),2)}, "
      f"winners {sum(1 for t in sl if t['net']>0)}, months {sl_m}")
print(f"    union-after: total {gate1['total']} | months {after} | GATE {gate1}")
out["wd5"] = {"n": len(sl), "net": round(sum(t["net"] for t in sl), 2),
              "win": sum(1 for t in sl if t["net"] > 0), "months": sl_m,
              "after": after, "gate": gate1,
              "trades": sorted([(t["date"], t["net"], t["exit_reason"])
                                for t in sl])}

# ---------- (2) INV-LONG exit grid ----------
grid_files = ["T100_S050", "T100_S065", "T100_S080",
              "T125_S050", "T125_S065", "T125_S080",
              "T150_S050", "T150_S065", "T150_S080",
              "T175_S050", "T175_S065", "T175_S080",
              "T200_S050", "T200_S065", "T200_S080", "TRA", "TRB"]
base_inv_total = comp_tot["INV-LONG"]
others = n4 + p2f + f4
grid = {}
for g in grid_files:
    fn = (f"tuning_inv_T2_{g}_trades.csv" if g in ("TRA", "TRB")
          else f"tuning_inv_T1_{g}_trades.csv")
    alt = filters_inv(M1.load_inv_long(fn))
    ctot = round(sum(t["net"] for t in alt), 2)
    h1 = round(sum(t["net"] for t in alt if t["date"] <= "2026-05-31"), 2)
    h2 = round(sum(t["net"] for t in alt if t["date"] >= "2026-06-01"), 2)
    rec = {"n": len(alt), "comp_total": ctot, "h1": h1, "h2": h2,
           "delta_vs_T125_S050": round(ctot - base_inv_total, 2)}
    if ctot > base_inv_total:
        u = mt(alt + others)
        utot = round(sum(t["net"] for t in alt + others), 2)
        rec["union_total"] = utot
        rec["union_months"] = u
        rec["gate_pass"] = (utot > STATE_TOTAL
                            and all(v > 0 for v in u.values())
                            and u["2026-10"] >= 50000)
    grid[g] = rec
    flag = " <-- beats incumbent component" if ctot > base_inv_total else ""
    print(f"(2) INV {g:10} n={len(alt)} comp {ctot:10.2f} "
          f"(H1 {h1:9.2f} / H2 {h2:9.2f}) delta {rec['delta_vs_T125_S050']:+9.2f}{flag}")
    if "union_total" in rec:
        print(f"      union total {rec['union_total']} gate {rec['gate_pass']} "
              f"months {rec['union_months']}")
out["inv_grid"] = grid

# ---------- (3) P2F exits: prior evidence ----------
p2f_tr = [t for t in book if t["comp"] == "P2F"]
out["p2f_prior"] = {
    "n": len(p2f_tr), "total": comp_tot["P2F"],
    "expectancy": round(comp_tot["P2F"] / max(len(p2f_tr), 1), 2),
    "evidence": ("Lesson 4 (stocks_T2): removing the +1.25% target "
                 "destroyed P2F's edge (two-day stop-only hold DEAD). "
                 "CH-1: S065 vs S050 hurt P2F inside the challenger. "
                 "No excursion build run: signal is the opposite of "
                 "overwhelming.")}
print(f"\n(3) P2F: {len(p2f_tr)} tr, total {comp_tot['P2F']}, "
      f"expectancy {out['p2f_prior']['expectancy']} — prior evidence "
      f"AGAINST an exit rebuild (Lesson 4 / CH-1); not built.")

json.dump(out, open(f"{BASE}/stocks_engine_sat5_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat5_diag.json")
