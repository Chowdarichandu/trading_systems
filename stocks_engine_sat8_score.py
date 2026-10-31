#!/usr/bin/env python3
"""ENGINE SAT-8 SCORE: F4 excludes HINDCOPPER SHORT signals. Frozen
in stocks_engine_frozen.md (SAT-8 section) BEFORE this ran. Anchor:
current-book rebuild == state (791 tr / +148,270.20 / Oct
+50,349.79) asserted first. Slice re-derived in sat8_diag and
asserted here == frozen record (12 tr / -1,094.95). Deletion-only
from the pre-audited F4 dump, so timing validity is inherited.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
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

STATE = {"2026-01": 12021.03, "2026-02": 3611.69, "2026-03": 22623.60,
         "2026-04": 3736.26, "2026-05": 27838.61, "2026-06": 4287.51,
         "2026-07": 3196.63, "2026-08": 775.60, "2026-09": 19829.48,
         "2026-10": 50349.79}
STATE_TOTAL, STATE_TRADES = 148270.20, 791
SLICE_N, SLICE_NET = 12, -1094.95   # frozen slice record (sat8 diag)

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "net": float(r["net"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and r["leg"] != "round2"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
       and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")
       and not (r["symbol"] == "UNITDSPR" and r["dir"] == "SHORT")]

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

base = inv + n4 + p2f + f4
bt, _ = mt(base)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in base), 2) == STATE_TOTAL
             and len(base) == STATE_TRADES)
print("ANCHOR (current book == state):", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok, "ANCHOR FAILED"
ex0, top3_0 = extop3(base)
print(f"incumbent ex-top-3: {ex0} (top3 {top3_0})")

slice_ = [t for t in f4 if t["stock"] == "HINDCOPPER" and t["dir"] == "SHORT"]
snet = round(sum(t["net"] for t in slice_), 2)
print(f"\nFrozen slice F4 x HINDCOPPER x SHORT in book: {len(slice_)} trades, "
      f"net {snet} -> matches frozen record "
      f"({SLICE_N} / {SLICE_NET}): {len(slice_) == SLICE_N and snet == SLICE_NET}")
assert len(slice_) == SLICE_N and snet == SLICE_NET, "SLICE MISMATCH"
for t in sorted(slice_, key=lambda t: t["date"]):
    print(f"  {t['date']} {t['setup']:22} net {t['net']:9.2f}")

new_f4 = [t for t in f4
          if not (t["stock"] == "HINDCOPPER" and t["dir"] == "SHORT")]
new_book = inv + n4 + p2f + new_f4
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'current':>10} {'SAT-8':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")

aug_after = nt["2026-08"]
n4_shortfall = round(4020.54 - aug_after, 2)
print(f"\nAugust after: Rs{aug_after} | N4-revisit August shortfall "
      f"(needs >= Rs4,020.54): Rs{n4_shortfall} (was Rs3,244.94)")
print(f"October after: Rs{nt['2026-10']} | headroom "
      f"Rs{round(nt['2026-10']-50000,2)} (unchanged, slice is October-neutral)")

print("\n=== SATURATION GATE (frozen SAT-8) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
banked = all([ga, gb, gc, gd])
print("BANKED:", banked)

json.dump({"anchor_ok": anchor_ok, "fix": "SAT-8-F4-HINDCOPPER-SHORT",
           "slice_trades": len(slice_), "slice_net": snet,
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": aug_after,
           "n4_revisit_august_shortfall_after": n4_shortfall},
          open(f"{BASE}/stocks_engine_sat8_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat8_result.json")
