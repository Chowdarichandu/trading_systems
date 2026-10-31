#!/usr/bin/env python3
"""ENGINE SAT-17 DIAGNOSIS: book-wide (component x stock x direction)
slice registry re-derived FROM SCRATCH at the CURRENT five-component
book (Lesson 16 -- SAT-13's registry is stale: the book has since
gained P2F-R2, the SAT-14 HINDALCO-LONG removal and the SAT-15 N4
exit rebuild). Anchor: incumbent union == state (812 tr /
+176,231.95 / month table / ex-top-3 56,308.12), N4 anchored on the
SAT-15 T150/S080 dump (book law -- M1.load_n4() is the stale
T125/S050 dump and is NOT used).

Qualification (cycle brief): slice negative full-period AND negative
in at least one thin month (Apr/Jun/Jul/Aug) AND October slice
<= 2,247.76 (the October headroom -- removing a slice whose October
net is positive costs October that amount).
Feasibility for banking: removal leaves every month > 0 AND the
razors (Aug 309.08 / Jul 1,262.53 / Jun 1,382.01) with >= Rs100
margin (Aug_after >= 100 -> slice Aug net <= 209.08, etc.), AND
union ex-top-3 not worse (gate leg d).
Quality bar (Lesson 5/15 shape + brief): the slice must be
GENUINELY negative full-period -- the GLENMARK-SHORT pattern
(Aug -4,744.78 vs full only -136.98, 10/20 winners) is a one-month
story with a near-zero full period and is BELOW the bar; such rows
are flagged and skipped in favour of the next qualifying row.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
import csv, sys, json
from collections import defaultdict
from datetime import date
import importlib.util

BASE = "/home/hatch/workspace/trading"
sys.path.insert(0, BASE)
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 25923.78, "2026-02": 17465.71, "2026-03": 19259.91,
         "2026-04": 7534.13, "2026-05": 33304.29, "2026-06": 1382.01,
         "2026-07": 1262.53, "2026-08": 309.08, "2026-09": 17542.75,
         "2026-10": 52247.76}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 176231.95, 812, 56308.12
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
THIN = ["2026-04", "2026-06", "2026-07", "2026-08"]
RAZOR_FLOOR = {"2026-08": 100.0, "2026-07": 100.0, "2026-06": 100.0}
OCT_HEADROOM = 2247.76

# ---------- incumbent book (verbatim SAT-16 construction) ----------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT")}
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")]
book = inv + n4 + p2f + f4 + r2

def mt(trades):
    m = defaultdict(float)
    for t in trades: m[t["date"][:7]] += t["net"]
    return {k: round(m.get(k, 0.0), 2) for k in MONTHS}

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

bt = mt(book)
ex0, top3_0 = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
comp_counts = defaultdict(int)
for t in book: comp_counts[t["comp"]] += 1
print(f"ANCHOR A: incumbent union == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0} | "
      f"components {dict(comp_counts)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- registry: (comp x stock x dir) ----------
slices = defaultdict(list)
for t in book:
    slices[(t["comp"], t["stock"], t["dir"])].append(t)

rows = []
for (comp, stock, d), trs in sorted(slices.items()):
    full = round(sum(t["net"] for t in trs), 2)
    per_m = {}
    for m in MONTHS:
        per_m[m] = round(sum(t["net"] for t in trs if t["date"][:7] == m), 2)
    thin_neg = [m for m in THIN if per_m[m] < 0]
    rows.append({"comp": comp, "stock": stock, "dir": d,
                 "trades": len(trs),
                 "win": sum(1 for t in trs if t["net"] > 0),
                 "full": full, "months": per_m,
                 "thin_neg": thin_neg,
                 "oct_slice": per_m["2026-10"]})

qual = [r for r in rows if r["full"] < 0 and r["thin_neg"]
        and r["oct_slice"] <= OCT_HEADROOM]
qual.sort(key=lambda r: r["full"])

def removal_effect(r):
    """month table + ex-top-3 after deleting exactly this slice."""
    keep = [t for t in book
            if not (t["comp"] == r["comp"] and t["stock"] == r["stock"]
                    and t["dir"] == r["dir"])]
    nm = mt(keep)
    ex1, _ = extop3(keep)
    return nm, ex1

print(f"\nREGISTRY: {len(rows)} (comp x stock x dir) slices total; "
      f"{len(qual)} qualify (full < 0 AND thin-month-negative AND "
      f"October slice <= {OCT_HEADROOM})")
print(f"\n{'slice':32} {'tr':>3} {'win':>3} {'full':>10} "
      f"{'thin-neg months':22} {'Oct':>9} {'feas':>5} {'bar':>4}")
out_rows = []
for r in qual:
    nm, ex1 = removal_effect(r)
    feas = (all(v > 0 for v in nm.values())
            and all(nm[m] >= RAZOR_FLOOR[m] for m in RAZOR_FLOOR)
            and nm["2026-10"] >= 50000 and ex1 >= ex0)
    # quality bar: genuinely negative full period -- a near-zero full
    # (>-500) riding one thin month is the GLENMARK pattern: below bar
    bar = r["full"] <= -500.0
    r2_ = dict(r, feasible=feas, quality_bar=bar,
               after_months=nm, after_extop3=ex1,
               after_total=round(STATE_TOTAL - r["full"], 2))
    out_rows.append(r2_)
    print(f"{r['comp']+' x '+r['stock']+' x '+r['dir']:32} "
          f"{r['trades']:>3} {r['win']:>3} {r['full']:>10.2f} "
          f"{','.join(m[5:] for m in r['thin_neg']):22} "
          f"{r['oct_slice']:>9.2f} {str(feas):>5} {str(bar):>4}")

picked = next((r for r in out_rows if r["feasible"] and r["quality_bar"]),
              None)
print("\nTOP by full-period value (most negative first), after "
      "feasibility + quality bar:")
for r in out_rows[:6]:
    print(f"  {r['comp']} x {r['stock']} x {r['dir']}: full {r['full']} "
          f"({r['trades']} tr, win {r['win']}), thin-neg {r['thin_neg']}, "
          f"Oct slice {r['oct_slice']}, feasible {r['feasible']}, "
          f"quality bar {r['quality_bar']}")
if picked:
    print(f"\nPICKED (top feasible, quality-bar-passing): "
          f"{picked['comp']} x {picked['stock']} x {picked['dir']} -- "
          f"{picked['trades']} tr / {picked['full']} / win {picked['win']}")
    print("month nets of the picked slice:",
          {m: picked["months"][m] for m in MONTHS
           if picked["months"][m] != 0.0})
    print("union after removal:", picked["after_months"],
          "| total", picked["after_total"],
          "| ex-top-3", picked["after_extop3"])
    print("picked slice trades:")
    for t in sorted(book, key=lambda x: x["date"]):
        if (t["comp"], t["stock"], t["dir"]) == \
                (picked["comp"], picked["stock"], picked["dir"]):
            print(f"  {t['date']} {t['stock']} {t['dir']} {t['net']}")
else:
    print("\nNO feasible quality-bar-passing slice -- registry frontier "
          "exhausted at this book.")

json.dump({"anchor_ok": a_ok, "registry_rows": len(rows),
           "qualifying": out_rows,
           "picked": (picked if picked is None else
                      {k: picked[k] for k in
                       ("comp", "stock", "dir", "trades", "win", "full",
                        "months", "thin_neg", "oct_slice", "feasible",
                        "quality_bar", "after_months", "after_extop3",
                        "after_total")})},
          open(f"{BASE}/stocks_engine_sat17_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat17_diag.json")
