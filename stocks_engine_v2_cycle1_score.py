#!/usr/bin/env python3
"""V2 CYCLE 1 SCORE — V2C1-FOLLOW-GLENMARK-SHORT-EXCL under the cross-year gate.

Frozen in stocks_engine_frozen.md BEFORE this run. Inputs are the
machinery-built incumbent books from stocks_engine_v2_build.py (whose own
controls all passed in their run; asserted again here from its results
JSON). Deletion-only: the removed set must equal the frozen diagnosis
slices exactly, per component x year. Gate (v2 charter): bank iff
(a) combined total rises AND (b) neither year's total falls AND
(c) neither year is negative at book level. Ex-top-3 per year and month
tables are reported (charter reporting duty).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "V2C1-FOLLOW-GLENMARK-SHORT-EXCL"}

build = json.load(open(f"{WS}/v2_out/v2_build_results.json"))
assert build["controls"]["ALL_PASS"], "build controls did not all pass"
inc25 = build["incumbent"]["y2025"]["stats"]
inc26 = build["incumbent"]["y2026"]["stats"]

def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
book25 = load("stocks_engine_v2_book2025_trades.csv")
book26 = load("stocks_engine_v2_book2026_trades.csv")
assert len(book25) == inc25["trades"] and round(sum(t["net"] for t in book25), 2) == inc25["total"]
assert len(book26) == inc26["trades"] and round(sum(t["net"] for t in book26), 2) == inc26["total"]
print(f"incumbent asserted: 2025 {len(book25)} tr / {inc25['total']} | "
      f"2026 {len(book26)} tr / {inc26['total']}")

def month_table(trades, months):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades:
        m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m.get(k, 0.0), 2) for k in months},
            {k: c.get(k, 0) for k in months})
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
# helper cross-check vs the build's own stats (months + ex-top3 must match)
for book, inc, months in ((book25, inc25, M25), (book26, inc26, M26)):
    mt, _ = month_table(book, months)
    ex, _ = extop3(book)
    assert mt == inc["months"] and ex == inc["ex_top3"], "helper mismatch vs build"
print("helpers cross-checked vs build stats: months + ex-top3 exact both years")

TARGET = {("F4", "SHORT"), ("N4-V3", "SHORT")}
def removed(book):
    return [t for t in book if t["stock"] == "GLENMARK"
            and (t["comp"], t["dir"]) in TARGET]
def kept(book):
    return [t for t in book if not (t["stock"] == "GLENMARK"
            and (t["comp"], t["dir"]) in TARGET)]
r25, r26 = removed(book25), removed(book26)
def sl(rs, comp):
    s = [t for t in rs if t["comp"] == comp]
    return len(s), round(sum(t["net"] for t in s), 2)
diag = {("2025", "F4"): (7, -3010.96), ("2025", "N4-V3"): (2, -2731.28),
        ("2026", "F4"): (20, -136.98), ("2026", "N4-V3"): (3, -494.21)}
got = {("2025", "F4"): sl(r25, "F4"), ("2025", "N4-V3"): sl(r25, "N4-V3"),
       ("2026", "F4"): sl(r26, "F4"), ("2026", "N4-V3"): sl(r26, "N4-V3")}
assert got == diag, f"deleted set != frozen diagnosis: {got} vs {diag}"
print("deleted set == frozen diagnosis exactly:", got,
      f"| total removed {len(r25)+len(r26)} tr / "
      f"{round(sum(t['net'] for t in r25+r26), 2)}")

k25, k26 = kept(book25), kept(book26)
def year_stats(book, months):
    mt, mc = month_table(book, months)
    ex, top3 = extop3(book)
    return {"trades": len(book), "total": round(sum(t["net"] for t in book), 2),
            "months": mt, "red_months": [k for k, v in mt.items() if v < 0],
            "ex_top3": ex, "top3": top3}
s25, s26 = year_stats(k25, M25), year_stats(k26, M26)
t25b, t26b = inc25["total"], inc26["total"]
comb_b = round(t25b + t26b, 2)
comb_a = round(s25["total"] + s26["total"], 2)
gate = {"a_combined_rises": comb_a > comb_b,
        "b_neither_year_falls": s25["total"] >= t25b and s26["total"] >= t26b,
        "c_neither_year_negative": s25["total"] >= 0 and s26["total"] >= 0}
banked = all(gate.values())
OUT.update({
    "incumbent": {"y2025": t25b, "y2026": t26b, "combined": comb_b,
                  "trades": len(book25) + len(book26)},
    "removed": {"trades": len(r25) + len(r26),
                "net": round(sum(t["net"] for t in r25 + r26), 2),
                "slices": {f"{y}-{c}": {"trades": v[0], "net": v[1]}
                           for (y, c), v in got.items()}},
    "after": {"y2025": s25, "y2026": s26, "combined": comb_a,
              "monthly_avg_22mo": round(comb_a / 22, 2)},
    "gate": gate, "banked": banked})
print(f"AFTER: 2025 {s25['trades']} tr / {s25['total']} (was {t25b}) | "
      f"2026 {s26['trades']} tr / {s26['total']} (was {t26b}) | "
      f"combined {comb_a} (was {comb_b}) | avg/mo {OUT['after']['monthly_avg_22mo']}")
print(f"2025 months after: {s25['months']} | red {s25['red_months']} | "
      f"ex-top3 {inc25['ex_top3']} -> {s25['ex_top3']}")
print(f"2026 months after: {s26['months']} | red {s26['red_months']} | "
      f"ex-top3 {inc26['ex_top3']} -> {s26['ex_top3']}")
print("GATE:", gate, "-> BANKED:", banked)
if banked:
    for fn, book in (("stocks_engine_v2_c1_book2025_trades.csv", k25),
                     ("stocks_engine_v2_c1_book2026_trades.csv", k26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-1 book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle1_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle1_result.json")
