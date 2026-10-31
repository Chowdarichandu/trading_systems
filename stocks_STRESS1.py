#!/usr/bin/env python3
"""LINE STRESS-1: robustness stresses on the frozen all-green incumbent.
Measurement only — no tuning, no new rules. Rebuild follows
stocks_engine_jn1_score.py exactly; anchors asserted against
stocks_engine_state.json before any stress is computed.
Paper only, real Rs0, provisional per 100 shares, home 25, Jan-Oct 2026.
All dump nets are after Rs40/trade; cost stress subtracts the delta
per trade (F4 dumps carry explicit gross/net — asserted == Rs40)."""
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

STATE = json.load(open(f"{BASE}/stocks_engine_state.json"))
SM = STATE["month_table"]; STOT = STATE["total"]; STR = STATE["trades"]
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]

# ---------- rebuild the incumbent (jn1 recipe, final exclusions) ----------
inv_raw = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4_raw  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f_raw = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
for t in inv_raw: t["comp"] = "INV-LONG"
for t in n4_raw:  t["comp"] = "N4-V3"
for t in p2f_raw: t["comp"] = "P2F"

f4_oc4 = rd("stocks_engine_oc4_f4s080_trades.csv")
assert all(abs((float(r["gross"]) - float(r["net"])) - 40.0) < 0.011 for r in f4_oc4), "F4 net != gross-40"
f4 = [{"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
      for r in f4_oc4 if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]

inv = [t for t in inv_raw if t["stock"] != "BDL"]
n4  = [t for t in n4_raw if t["stock"] != "ASTRAL"]
p2f = [t for t in p2f_raw if t["stock"] not in ("ASTRAL", "HINDUNILVR")]
book = inv + n4 + p2f + f4

def mtable(trades):
    m = {k: 0.0 for k in MONTHS}; c = {k: 0 for k in MONTHS}
    for t in trades:
        m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in MONTHS}, c

bt, bc = mtable(book)
btot = round(sum(t["net"] for t in book), 2)
anchor_ok = bt == SM and btot == STOT and len(book) == STR
print(f"ANCHOR: {anchor_ok} | trades {len(book)} (state {STR}) | total {btot} (state {STOT})")
print("month table == state:", bt == SM)
assert anchor_ok, "REBUILD DOES NOT MATCH STATE — STOP"
json.dump({"anchor_ok": anchor_ok}, open(f"{BASE}/stocks_STRESS1_anchor.json", "w"))

def green(mt): return sum(1 for v in mt.values() if v > 0)
out = {"base": {"total": btot, "trades": len(book), "months": bt, "green": green(bt)}}

# ---------- STRESS 1: cost sensitivity ----------
for C in (60, 80):
    d = C - 40
    mt = {k: round(bt[k] - d * bc[k], 2) for k in MONTHS}
    out[f"cost_{C}"] = {"total": round(btot - d * len(book), 2), "months": mt, "green": green(mt)}
    print(f"\nCOST Rs{C}: total {out[f'cost_{C}']['total']} | green {green(mt)}/10")
    print(" ", mt)

# ---------- STRESS 2: concentration ----------
per_stock = defaultdict(float); per_stock_n = defaultdict(int)
for t in book:
    per_stock[t["stock"]] += t["net"]; per_stock_n[t["stock"]] += 1
rank = sorted(per_stock.items(), key=lambda kv: -kv[1])
print("\nSTOCK RANKING (full period):")
for s, v in rank: print(f"  {s:12} {round(v,2):>12}  ({per_stock_n[s]} tr)")
def ex(stocks):
    b = [t for t in book if t["stock"] not in stocks]
    mt, _ = mtable(b)
    return {"removed": list(stocks), "total": round(sum(t["net"] for t in b), 2),
            "months": mt, "green": green(mt), "trades": len(b)}
out["ex_top1"] = ex([rank[0][0]])
out["ex_top3"] = ex([s for s, _ in rank[:3]])
out["ex_tvsmotor"] = ex(["TVSMOTOR"])
out["ex_tvs_glenmark"] = ex(["TVSMOTOR", "GLENMARK"])
for k in ("ex_top1", "ex_top3", "ex_tvsmotor", "ex_tvs_glenmark"):
    print(f"{k}: removed {out[k]['removed']} total {out[k]['total']} green {out[k]['green']}/10")
    print("  ", out[k]["months"])
out["stock_ranking"] = {s: round(v, 2) for s, v in rank}

# ---------- STRESS 3: exclusion fragility (removed slices by half) ----------
def half_split(trades):
    h1 = [t for t in trades if t["date"][:7] <= "2026-05"]
    h2 = [t for t in trades if t["date"][:7] >= "2026-06"]
    f = lambda ts: {"n": len(ts), "net": round(sum(t["net"] for t in ts), 2),
                    "winners": sum(1 for t in ts if t["net"] > 0)}
    return {"H1_JanMay": f(h1), "H2_JunOct": f(h2), "all": f(trades),
            "by_month": {k: round(sum(t["net"] for t in trades if t["date"][:7] == k), 2)
                         for k in sorted({t["date"][:7] for t in trades})}}
excl = {
 "N4-V3 x ASTRAL":     [t for t in n4_raw if t["stock"] == "ASTRAL"],
 "P2F x ASTRAL":       [t for t in p2f_raw if t["stock"] == "ASTRAL"],
 "P2F x HINDUNILVR":   [t for t in p2f_raw if t["stock"] == "HINDUNILVR"],
 "INV-LONG x BDL":     [t for t in inv_raw if t["stock"] == "BDL"],
}
out["exclusions"] = {}
for name, ts in excl.items():
    out["exclusions"][name] = half_split(ts)
    s = out["exclusions"][name]
    print(f"\nEXCL {name}: all {s['all']} | H1 {s['H1_JanMay']} | H2 {s['H2_JunOct']} | months {s['by_month']}")

# ---------- STRESS 4: thin months ----------
out["thin"] = {}
for mk in ("2026-06", "2026-08", "2026-04"):
    ts = sorted([t for t in book if t["date"][:7] == mk], key=lambda t: -t["net"])
    top = ts[0]
    tot = round(sum(t["net"] for t in ts), 2)
    out["thin"][mk] = {"trades": len(ts), "total": tot,
                       "top_trade": {"stock": top["stock"], "comp": top["comp"],
                                     "date": top["date"], "net": round(top["net"], 2)},
                       "top_share_pct": round(100.0 * top["net"] / tot, 1) if tot > 0 else None,
                       "month_ex_top_trade": round(tot - top["net"], 2),
                       "winners": sum(1 for t in ts if t["net"] > 0)}
    print(f"\nTHIN {mk}: {out['thin'][mk]}")

# ---------- STRESS 5: F4 at pre-tuning exits T125/S065 ----------
f4_old = [{"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
          for r in rd("stocks_M2_F4_trades.csv")
          if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
book_old = inv + n4 + p2f + f4_old
mt_old, _ = mtable(book_old)
out["f4_old_exits"] = {"total": round(sum(t["net"] for t in book_old), 2), "months": mt_old,
                       "green": green(mt_old), "trades": len(book_old),
                       "f4_trades": len(f4_old), "f4_total": round(sum(t["net"] for t in f4_old), 2),
                       "f4_incumbent_total": round(sum(t["net"] for t in f4), 2)}
print(f"\nF4@T125/S065 book: total {out['f4_old_exits']['total']} green {green(mt_old)}/10 "
      f"(incumbent {btot}, 10/10) | F4 comp {out['f4_old_exits']['f4_total']} vs {out['f4_old_exits']['f4_incumbent_total']}")
print(" ", mt_old)

json.dump(out, open(f"{BASE}/stocks_STRESS1_results.json", "w"), indent=1)
print("\nwrote stocks_STRESS1_results.json")
