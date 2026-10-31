#!/usr/bin/env python3
"""V2 CYCLE 3 SCORE — CHALLENGER CH-V2-1 "P2F-3.0" under the cross-year gate.

Frozen in stocks_engine_frozen.md (V2-CYCLE-3) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass before any challenger number is read. The challenger swaps
ONLY the P2F component (lo_band 2.5 -> 3.0, build machinery verbatim) in
the post-Cycle-2 incumbent books. Gate (v2 charter): bank iff
(a) combined total rises AND (b) neither year's total falls AND
(c) neither year is negative at book level.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-1-P2F-BAND30", "cycle": 3, "challenger": True}

# --- controls: re-execute the audited build in-process -----------------
g = {"__name__": "v2_build_exec"}
src = open(f"{WS}/stocks_engine_v2_build.py").read()
exec(compile(src, "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass (plateau assembly, rebuilds, "
      "event anchors, 2025 anchors, audits 0)")

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
# build's incumbent P2F sets == post-C2 books' P2F rows (C1/C2 touched none)
for yr, mine, book in (("2025", g["p2f_mine25"], book25), ("2026", g["p2f_mine26"], book26)):
    rows = [t for t in book if t["comp"] == "P2F"]
    assert sorted(KEY(t) for t in mine) == sorted(KEY(t) for t in rows), f"P2F anchor mismatch {yr}"
print("P2F anchors: build incumbent P2F == post-C2 book P2F rows, both years")

# --- challenger component ----------------------------------------------
ch25 = g["p2f_book"](g["cands25"], lo_band=3.0)
ch26 = g["p2f_book"](g["cands26"], lo_band=3.0)
for yr, ch, mine in (("2025", ch25, g["p2f_mine25"]), ("2026", ch26, g["p2f_mine26"])):
    assert {KEY(t) for t in ch} <= {KEY(t) for t in mine}, f"challenger not a subset {yr}"
    dropped = [t for t in mine if KEY(t) not in {KEY(x) for x in ch}]
    print(f"{yr}: P2F-2.5 {len(mine)} tr / {round(sum(t['net'] for t in mine),2)} -> "
          f"P2F-3.0 {len(ch)} tr / {round(sum(t['net'] for t in ch),2)} | "
          f"dropped slice [2.5,3.0): {len(dropped)} tr / {round(sum(t['net'] for t in dropped),2)}")
    OUT[f"p2f_{yr}"] = {
        "incumbent": [len(mine), round(sum(t["net"] for t in mine), 2)],
        "challenger": [len(ch), round(sum(t["net"] for t in ch), 2)],
        "dropped_slice": [len(dropped), round(sum(t["net"] for t in dropped), 2)]}

def swap(book, ch):
    rest = [t for t in book if t["comp"] != "P2F"]
    new = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
            "dir": t["dir"], "entry_time": t["entry_time"], "net": t["net"]}
           for t in ch]
    return rest + new
nb25, nb26 = swap(book25, ch25), swap(book26, ch26)

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
    "gate": gate, "banked": banked})
print(f"CHALLENGER BOOK: 2025 {s25['trades']} tr / {s25['total']} (was {EXP25[1]}) | "
      f"2026 {s26['trades']} tr / {s26['total']} (was {EXP26[1]}) | "
      f"combined {comb_a} (was {comb_b}) | avg/mo {OUT['after']['monthly_avg_22mo']}")
print(f"2025 months: {s25['months']} | red {s25['red_months']} | ex-top3 {o25['ex_top3']} -> {s25['ex_top3']}")
print(f"2026 months: {s26['months']} | red {s26['red_months']} | ex-top3 {o26['ex_top3']} -> {s26['ex_top3']}")
print("GATE:", gate, "-> BANKED:", banked)
if banked:
    for fn, book in (("stocks_engine_v2_c3_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c3_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-3 challenger book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle3_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle3_result.json")
