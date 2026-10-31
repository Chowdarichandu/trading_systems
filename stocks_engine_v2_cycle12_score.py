#!/usr/bin/env python3
"""V2 CYCLE 12 SCORE — CHALLENGER CH-V2-4 "F4-S110" (stop -0.95% -> -1.10%).

Frozen in stocks_engine_frozen.md (V2-CYCLE-12) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass. The challenger rebuilds ONLY the F4 component via the
validation machinery's collect2 at (1.50, 1.10), f4_keep verbatim, plus
the full current F4 book law. Anchors: incumbent F4 rows == build F4 sets
minus the v2-law slices (both years); S110 timing-audit deltas 0;
challenger entry set == incumbent entry set (both years). Gate (v2
charter): bank iff (a) combined rises AND (b) neither year falls AND
(c) neither year negative at book level.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-4-F4-S110", "cycle": 12, "challenger": True}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass (incl. Control B2: S095 rebuild == frozen F4 set)")
collect2, F4_CFG, f4_keep = g["collect2"], g["F4_CFG"], g["f4_keep"]
norm_f4, AUDIT = g["norm_f4"], g["_AUDIT"]

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

KEY = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2))
EKEY = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"])
LAW = {("GLENMARK", "SHORT"), ("HDFCBANK", "SHORT"), ("KALYANKJIL", "LONG")}
def lawdrop(rows):
    return [t for t in rows if (t["stock"], t["dir"]) not in LAW]

# anchor: incumbent F4 rows == build F4 sets minus v2-law slices
for yr, mine, book in (("2025", g["f4_25"], book25), ("2026", g["f4_26"], book26)):
    rows = [t for t in book if t["comp"] == "F4"]
    assert sorted(KEY(t) for t in lawdrop(mine)) == sorted(KEY(t) for t in rows), \
        f"incumbent F4 anchor mismatch {yr}"
print("anchor PASS: incumbent F4 rows == build F4 sets minus v2-law slices, both years")

# challenger F4 at S110
ch = {}
for yr, days, mine, book in (("2025", g["days25"], g["f4_25"], book25),
                             ("2026", g["days26"], g["f4_26"], book26)):
    a0 = dict(AUDIT)
    raw = collect2(days, F4_CFG, 1.50, 1.10)
    viol = AUDIT["violations"] - a0["violations"]
    assert viol == 0, f"S110 timing audit violations {yr}: {viol}"
    kept = norm_f4([t for t in raw if f4_keep(t)])
    assert sorted(EKEY(t) for t in kept) == sorted(EKEY(t) for t in mine), \
        f"entry-set mismatch {yr}: exit change altered the kept entry population"
    chset = lawdrop(kept)
    inc = [t for t in book if t["comp"] == "F4"]
    ch[yr] = chset
    OUT[f"f4_{yr}"] = {
        "incumbent": [len(inc), round(sum(t["net"] for t in inc), 2)],
        "challenger": [len(chset), round(sum(t["net"] for t in chset), 2)],
        "audit_violations": viol}
    print(f"{yr}: F4-S095 {len(inc)} tr / {OUT[f'f4_{yr}']['incumbent'][1]} -> "
          f"F4-S110 {len(chset)} tr / {OUT[f'f4_{yr}']['challenger'][1]} | "
          f"entries identical, audit violations 0")

def swap(book, chset):
    return [t for t in book if t["comp"] != "F4"] + \
           [{"date": t["date"], "stock": t["stock"], "comp": "F4",
             "dir": t["dir"], "entry_time": t["entry_time"], "net": t["net"]}
            for t in chset]
nb25, nb26 = swap(book25, ch["2025"]), swap(book26, ch["2026"])

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
def year_stats(book, months):
    ex, top3 = extop3(book)
    mt = month_table(book, months)
    return {"trades": len(book), "total": round(sum(t["net"] for t in book), 2),
            "months": mt, "red_months": [k for k, v in mt.items() if v < 0],
            "ex_top3": ex, "top3": top3}
s25, s26 = year_stats(nb25, M25), year_stats(nb26, M26)
o25, o26 = year_stats(book25, M25), year_stats(book26, M26)
comb_b = round(EXP25[1] + EXP26[1], 2)
comb_a = round(s25["total"] + s26["total"], 2)
gate = {"a_combined_rises": comb_a > comb_b,
        "b_neither_year_falls": s25["total"] >= EXP25[1] and s26["total"] >= EXP26[1],
        "c_neither_year_negative": s25["total"] >= 0 and s26["total"] >= 0}
banked = all(gate.values())
OUT.update({
    "incumbent": {"y2025": EXP25[1], "y2026": EXP26[1], "combined": comb_b},
    "after": {"y2025": s25, "y2026": s26, "combined": comb_a,
              "monthly_avg_22mo": round(comb_a / 22, 2)},
    "ex_top3_before": {"2025": o25["ex_top3"], "2026": o26["ex_top3"]},
    "floor_after": {"2025_gap": round(240000 - s25["total"], 2),
                    "2026_gap": round(200000 - s26["total"], 2)},
    "gate": gate, "banked": banked})
print(f"CHALLENGER BOOK: 2025 {s25['trades']} tr / {s25['total']} (was {EXP25[1]}) | "
      f"2026 {s26['trades']} tr / {s26['total']} (was {EXP26[1]}) | "
      f"combined {comb_a} (was {comb_b}) | avg/mo {OUT['after']['monthly_avg_22mo']}")
print(f"2025 months: {s25['months']} | red {s25['red_months']} | ex-top3 {o25['ex_top3']} -> {s25['ex_top3']}")
print(f"2026 months: {s26['months']} | red {s26['red_months']} | ex-top3 {o26['ex_top3']} -> {s26['ex_top3']}")
print("GATE:", gate, "-> BANKED:", banked)
if banked:
    for fn, book in (("stocks_engine_v2_c12_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c12_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-12 challenger book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle12_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle12_result.json")
