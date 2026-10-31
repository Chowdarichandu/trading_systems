#!/usr/bin/env python3
"""V2 CYCLE 5 SCORE — V2C5-INV-UNITDSPR-EXCL under the cross-year gate.

Frozen in stocks_engine_frozen.md (V2-CYCLE-5) BEFORE this run. Inputs are
the post-Cycle-2 incumbent books. Deletion-only: the removed set must equal
the frozen diagnosis slice exactly. Gate (v2 charter): bank iff
(a) combined total rises AND (b) neither year's total falls AND
(c) neither year is negative at book level. Floor position (user mandate
2026-10-31 15:17 IST: 2025 >= 240,000 AND 2026 >= 200,000) reported.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "V2C5-INV-UNITDSPR-EXCL", "cycle": 5}

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
EXP25 = (state["best_trades"]["2025"], state["best_by_year"]["2025"])
EXP26 = (state["best_trades"]["2026"], state["best_by_year"]["2026"])

def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
book25 = load(state["book_files"]["2025"])
book26 = load(state["book_files"]["2026"])
assert (len(book25), round(sum(t["net"] for t in book25), 2)) == EXP25
assert (len(book26), round(sum(t["net"] for t in book26), 2)) == EXP26
print(f"incumbent asserted: 2025 {EXP25} | 2026 {EXP26} | combined {state['combined_best']}")

def month_table(trades, months):
    m = defaultdict(float)
    for t in trades:
        m[t["date"][:7]] += t["net"]
    return {k: round(m.get(k, 0.0), 2) for k in months}
def extop3(trades):
    per = defaultdict(float)
    for t in trades:
        per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [(k, round(v, 2)) for k, v in top3])
M25 = [f"2025-{i:02d}" for i in range(1, 13)]
M26 = [f"2026-{i:02d}" for i in range(1, 11)]

def is_target(t):
    return t["comp"] == "INV-LONG" and t["stock"] == "UNITDSPR" and t["dir"] == "LONG"
r25 = [t for t in book25 if is_target(t)]
r26 = [t for t in book26 if is_target(t)]
def sl(rs):
    return len(rs), round(sum(t["net"] for t in rs), 2), sum(t["net"] > 0 for t in rs)
diag = {"2025": (4, -470.49, 1), "2026": (2, -1361.10, 0)}
got = {"2025": sl(r25), "2026": sl(r26)}
assert got == diag, f"deleted set != frozen diagnosis: {got} vs {diag}"
print("deleted set == frozen diagnosis exactly:", got,
      f"| total removed {len(r25)+len(r26)} tr / "
      f"{round(sum(t['net'] for t in r25+r26), 2)}")

k25 = [t for t in book25 if not is_target(t)]
k26 = [t for t in book26 if not is_target(t)]
def year_stats(book, months):
    ex, top3 = extop3(book)
    mt = month_table(book, months)
    return {"trades": len(book), "total": round(sum(t["net"] for t in book), 2),
            "months": mt, "red_months": [k for k, v in mt.items() if v < 0],
            "ex_top3": ex, "top3": top3}
s25, s26 = year_stats(k25, M25), year_stats(k26, M26)
o25, o26 = year_stats(book25, M25), year_stats(book26, M26)
t25b, t26b = EXP25[1], EXP26[1]
comb_b = round(t25b + t26b, 2)
comb_a = round(s25["total"] + s26["total"], 2)
gate = {"a_combined_rises": comb_a > comb_b,
        "b_neither_year_falls": s25["total"] >= t25b and s26["total"] >= t26b,
        "c_neither_year_negative": s25["total"] >= 0 and s26["total"] >= 0}
banked = all(gate.values())
floor = {"2025_gap": round(240000 - s25["total"], 2),
         "2026_gap": round(200000 - s26["total"], 2)}
OUT.update({
    "incumbent": {"y2025": t25b, "y2026": t26b, "combined": comb_b},
    "removed": {"trades": len(r25) + len(r26),
                "net": round(sum(t["net"] for t in r25 + r26), 2), "slices": got},
    "after": {"y2025": s25, "y2026": s26, "combined": comb_a,
              "monthly_avg_22mo": round(comb_a / 22, 2)},
    "ex_top3_before": {"2025": o25["ex_top3"], "2026": o26["ex_top3"]},
    "floor_after": floor,
    "gate": gate, "banked": banked})
print(f"AFTER: 2025 {s25['trades']} tr / {s25['total']} (was {t25b}) | "
      f"2026 {s26['trades']} tr / {s26['total']} (was {t26b}) | "
      f"combined {comb_a} (was {comb_b}) | avg/mo {OUT['after']['monthly_avg_22mo']}")
print(f"2025 months after: {s25['months']} | red {s25['red_months']} | "
      f"ex-top3 {o25['ex_top3']} -> {s25['ex_top3']}")
print(f"2026 months after: {s26['months']} | red {s26['red_months']} | "
      f"ex-top3 {o26['ex_top3']} -> {s26['ex_top3']}")
print(f"FLOOR after: 2025 gap {floor['2025_gap']} | 2026 gap {floor['2026_gap']}")
print("GATE:", gate, "-> BANKED:", banked)
if banked:
    for fn, book in (("stocks_engine_v2_c5_book2025_trades.csv", k25),
                     ("stocks_engine_v2_c5_book2026_trades.csv", k26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-5 book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle5_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle5_result.json")
