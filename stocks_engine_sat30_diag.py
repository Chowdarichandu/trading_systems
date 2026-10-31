#!/usr/bin/env python3
"""ENGINE SAT-30 DIAGNOSIS: re-derive the book-wide
(component x stock x direction) slice registry FROM SCRATCH at the
CURRENT book (post-SAT-29: 670 tr / +195,842.99) and pick the TOP
qualifying slice for freezing (Lesson 16 -- SAT-29's registry named
F4 x RECLTD x SHORT -503.97 (Aug -342.58, Oct +477.00) as the last
qualifying row, but that number is stale until re-measured here;
SAT-29 intervened only on an F4 PFC-SHORT leg, disjoint from
RECLTD-SHORT, so invariance is expected -- and verified, not
assumed.) Also checks whether the registry EMPTIES of qualifying
rows after the picked removal (the deletion frontier question).
Anchor: incumbent union == state (670 tr / +195,842.99 / month
table / ex-top-3 70,753.50), N4 anchored on the SAT-15 T150/S080
dump MINUS the SAT-17 TVSMOTOR-LONG and SAT-24 OIL-LONG
exclusions, F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT +
SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT
+ SAT-29 PFC-SHORT exclusions, INV-LONG minus BDL + SAT-19 VEDL +
SAT-20 HINDZINC + SAT-23 INDUSTOWER + SAT-28 KALYANKJIL
exclusions, P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion
(book law), NOT M1.load_n4().

Qualifying (cycle brief): full-period <= -500 AND negative in
>= 1 thin month (Apr/Jun/Jul/Aug) AND October slice <= headroom
(3,321.37). Quality bar (Lesson 5/15 + the GLENMARK precedent):
skip near-zero full-period rows (covered by the -500 bar).
Feasible: removal -> union total rises AND all ten months > 0 AND
razors Aug/Jul/Jun keep >= 100 AND October >= 50,000 AND ex-top-3
not worse. Pick = top qualifying row by full-period value that is
feasible. ONE slice only.
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

STATE = {"2026-01": 28393.86, "2026-02": 18619.56, "2026-03": 21165.37,
         "2026-04": 9559.14, "2026-05": 34504.27, "2026-06": 3823.22,
         "2026-07": 6543.43, "2026-08": 769.28, "2026-09": 19143.49,
         "2026-10": 53321.37}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 195842.99, 670, 70753.50
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
THIN = ["2026-04", "2026-06", "2026-07", "2026-08"]
RAZOR_FLOOR = {"2026-08": 100.0, "2026-07": 100.0, "2026-06": 100.0}
OCT_HEADROOM = 3321.37

# ---------- incumbent book (post-SAT-29 construction) -------------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"
       and t["stock"] != "VEDL" and t["stock"] != "HINDZINC"
       and t["stock"] != "INDUSTOWER" and t["stock"] != "KALYANKJIL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"
      and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")
      and not (r["stock"] == "OIL" and r["direction"] == "LONG")]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
        ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
        ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
        ("PFC", "SHORT")}
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
      if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
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
            [(k, round(v, 2)) for k, v in top3])

bt = mt(book)
ex0, top3_0 = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
comp_counts = defaultdict(int)
for t in book: comp_counts[t["comp"]] += 1
print(f"ANCHOR A: incumbent union == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0} | "
      f"top3 {top3_0} | components {dict(comp_counts)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- registry re-derived from scratch -----------------------
def derive_registry(bk, base_total, base_months, base_ex0, headroom):
    slices = defaultdict(list)
    for t in bk:
        slices[(t["comp"], t["stock"], t["dir"])].append(t)
    rows = []
    for key, trs in sorted(slices.items()):
        full = round(sum(t["net"] for t in trs), 2)
        per_m = {m: round(sum(t["net"] for t in trs
                              if t["date"][:7] == m), 2) for m in MONTHS}
        thin_neg = [m for m in THIN if per_m[m] < 0]
        keep = [t for t in bk
                if (t["comp"], t["stock"], t["dir"]) != key]
        nm = mt(keep)
        ex1, _ = extop3(keep)
        feas = (all(v > 0 for v in nm.values())
                and all(nm[m] >= RAZOR_FLOOR[m] for m in RAZOR_FLOOR)
                and nm["2026-10"] >= 50000 and ex1 >= base_ex0
                and round(base_total - full, 2) > base_total)
        rows.append({"comp": key[0], "stock": key[1], "dir": key[2],
                     "trades": len(trs),
                     "win": sum(1 for t in trs if t["net"] > 0),
                     "full": full, "months": per_m, "thin_neg": thin_neg,
                     "oct_slice": per_m["2026-10"],
                     "qualifies": (full <= -500.0 and bool(thin_neg)
                                   and per_m["2026-10"] <= headroom),
                     "feasible": feas, "quality_bar": full <= -500.0,
                     "after_months": nm, "after_extop3": ex1,
                     "after_total": round(base_total - full, 2)})
    return rows

rows = derive_registry(book, STATE_TOTAL, STATE, ex0, OCT_HEADROOM)
qual = [r for r in rows if r["qualifies"]]
qual.sort(key=lambda r: r["full"])
print(f"\nREGISTRY: {len(rows)} slices total; {len(qual)} qualify "
      f"(full <= -500 AND thin-month-negative AND Oct slice <= "
      f"{OCT_HEADROOM})")
print("\nALL qualifying rows by full-period value:")
for r in qual:
    print(f"  {r['comp']} x {r['stock']} x {r['dir']}: full {r['full']} "
          f"({r['trades']} tr, win {r['win']}), thin-neg "
          f"{r['thin_neg']}, Oct {r['oct_slice']}, Aug "
          f"{r['months']['2026-08']}, feas {r['feasible']}, "
          f"bar {r['quality_bar']}")

# ---------- pick -----------------------------------------------------
picked = next((r for r in qual
               if r["feasible"] and r["quality_bar"]), None)
post_qual = None
if picked:
    pk = (picked["comp"], picked["stock"], picked["dir"])
    ptrades = sorted((t for t in book
                      if (t["comp"], t["stock"], t["dir"]) == pk),
                     key=lambda x: x["date"])
    print(f"\nPICK: {pk} -- top qualifying row, feasible, "
          f"quality-bar-passing.")
    print(f"  trades {picked['trades']} | win {picked['win']} | full "
          f"{picked['full']} | thin-neg {picked['thin_neg']}")
    print(f"  month profile (non-zero): "
          f"{ {m: picked['months'][m] for m in MONTHS if picked['months'][m] != 0.0} }")
    print(f"  August slice {picked['months']['2026-08']} (removal "
          f"leaves August {picked['after_months']['2026-08']}; "
          f"guard >= 100: {picked['after_months']['2026-08'] >= 100})")
    print(f"  October slice {picked['oct_slice']} (<= headroom "
          f"{OCT_HEADROOM}); removal leaves October "
          f"{picked['after_months']['2026-10']}")
    print(f"  union after removal: total {picked['after_total']} | "
          f"ex-top-3 {picked['after_extop3']} | months "
          f"{picked['after_months']}")
    print("  picked slice trades (date, net):")
    for t in ptrades:
        print(f"    {t['date']} {t['stock']} {t['dir']} {t['net']}")
    other = [t for t in book
             if t["comp"] == pk[0] and t["stock"] == pk[1]
             and t["dir"] != pk[2]]
    if other:
        print(f"  opposite-direction half kept: {len(other)} tr / "
              f"{round(sum(t['net'] for t in other), 2)}")
    same_stock_other_comp = [t for t in book
                             if t["comp"] != pk[0] and t["stock"] == pk[1]]
    if same_stock_other_comp:
        per_comp = defaultdict(float)
        for t in same_stock_other_comp: per_comp[t["comp"]] += t["net"]
        print(f"  same stock in other components (kept): "
              f"{ {k: round(v,2) for k, v in sorted(per_comp.items())} }")
    # ---------- does the registry empty after this removal? --------
    new_book = [t for t in book
                if (t["comp"], t["stock"], t["dir"]) != pk]
    new_headroom = round(picked["after_months"]["2026-10"] - 50000, 2)
    rows2 = derive_registry(new_book, picked["after_total"],
                            picked["after_months"],
                            picked["after_extop3"], new_headroom)
    post_qual = [r for r in rows2 if r["qualifies"]]
    post_qual.sort(key=lambda r: r["full"])
    print(f"\nPOST-REMOVAL REGISTRY: {len(rows2)} slices; "
          f"{len(post_qual)} qualifying rows remain "
          f"(headroom re-based to {new_headroom})")
    for r in post_qual:
        print(f"  {r['comp']} x {r['stock']} x {r['dir']}: full "
              f"{r['full']} ({r['trades']} tr), thin-neg "
              f"{r['thin_neg']}, Oct {r['oct_slice']}, feas "
              f"{r['feasible']}")
    print("REGISTRY EMPTIES AFTER THIS REMOVAL:"
          if not post_qual else "REGISTRY NOT EMPTY AFTER REMOVAL:",
          len(post_qual) == 0)
else:
    print("\nPICK: NONE -- no qualifying slice is feasible at the "
          "quality bar; registry frontier exhausted at this book.")
    ptrades = []

json.dump({"anchor_ok": a_ok,
           "registry_rows": len(rows), "qualifying_count": len(qual),
           "top_qualifying": [
               {k: r[k] for k in ("comp", "stock", "dir", "trades",
                                  "win", "full", "months", "thin_neg",
                                  "oct_slice", "feasible",
                                  "quality_bar", "after_months",
                                  "after_extop3", "after_total")}
               for r in qual],
           "picked": (None if picked is None else
                      {k: picked[k] for k in
                       ("comp", "stock", "dir", "trades", "win",
                        "full", "months", "thin_neg", "oct_slice",
                        "feasible", "quality_bar", "after_months",
                        "after_extop3", "after_total")}),
           "picked_trades": [(t["date"], t["net"]) for t in ptrades],
           "post_removal_qualifying": (
               None if post_qual is None else
               [{k: r[k] for k in ("comp", "stock", "dir", "trades",
                                   "win", "full", "thin_neg",
                                   "oct_slice", "feasible")}
                for r in post_qual]),
           "registry_empties_after_removal": (
               None if post_qual is None else len(post_qual) == 0)},
          open(f"{BASE}/stocks_engine_sat30_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat30_diag.json")
