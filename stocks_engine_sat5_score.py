#!/usr/bin/env python3
"""ENGINE SAT-5 SCORE: frozen fix = F4 excludes HINDUNILVR SHORT.
Rebuild incumbent (anchor asserted vs state), delete exactly the
frozen slice, recompute month table + saturation gate + ex-top-3.
Deletion-only from the pre-audited F4 dump -> timing validity
inherited (JN-1 precedent). Paper, real Rs0, per 100 sh, Rs40/tr."""
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

inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
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
print(f"ANCHOR: {anchor_ok} | trades {len(book)} total {tot}")
assert anchor_ok

def ex_top3(trades):
    by = defaultdict(float)
    for t in trades: by[t["stock"]] += t["net"]
    top = sorted(by.items(), key=lambda kv: -kv[1])[:3]
    names = {k for k, _ in top}
    rest = [t for t in trades if t["stock"] not in names]
    return {"top3": [(k, round(v, 2)) for k, v in top],
            "ex_total": round(sum(t["net"] for t in rest), 2)}

ext_before = ex_top3(book)

# --- frozen fix ---
def is_slice(t):
    return (t["comp"] == "F4" and t["stock"] == "HINDUNILVR"
            and t["dir"] == "SHORT")
removed = [t for t in book if is_slice(t)]
newbook = [t for t in book if not is_slice(t)]
assert len(removed) == 9, f"frozen slice must be 9 trades, got {len(removed)}"
assert all(t["stock"] == "HINDUNILVR" and t["dir"] == "SHORT"
           for t in removed)
sl_net = round(sum(t["net"] for t in removed), 2)
assert sl_net == -2664.00, f"slice net {sl_net} != frozen -2664.00"

nt = mt(newbook)
ntot = round(sum(t["net"] for t in newbook), 2)
ext_after = ex_top3(newbook)
legs = {"a_total_rises": ntot > STATE_TOTAL,
        "b_all_green": all(v > 0 for v in nt.values()),
        "c_october_floor": nt["2026-10"] >= 50000}
banked = all(legs.values())
print(f"REMOVED {len(removed)} tr, net {sl_net}")
print(f"NEW total {ntot} (delta {round(ntot-STATE_TOTAL,2):+}) | "
      f"trades {len(newbook)} | months {nt}")
print(f"GATE {legs} -> {'BANKED' if banked else 'REJECTED'}")
print(f"ex-top-3 before {ext_before} | after {ext_after}")

res = {"anchor_ok": anchor_ok, "removed": [
           {"date": t["date"], "net": t["net"],
            "exit_reason": t["exit_reason"], "setup": t["setup"]}
           for t in sorted(removed, key=lambda x: x["date"])],
       "removed_net": sl_net, "month_table_after": nt,
       "total_after": ntot, "trades_after": len(newbook),
       "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
       "gate": legs, "banked": banked,
       "ex_top3_before": ext_before, "ex_top3_after": ext_after}
json.dump(res, open(f"{BASE}/stocks_engine_sat5_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat5_result.json")
