#!/usr/bin/env python3
"""V2 CYCLE 20 SCORE — CHALLENGER CH-V2-7 "F4-ROUND2" (round-2 legs restored).

Frozen in stocks_engine_frozen.md (V2-CYCLE-20) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass. The restoration set is isolated black-box from the
build's own audited S095 raw populations: legs f4_keep rejects SOLELY for
their round (f4_keep false as-is, true with round set to 1), passed
through the full current F4 book law and added to the incumbent book.
Gate (v2 charter): bank iff (a) combined rises AND (b) neither year
falls AND (c) neither year negative at book level.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json, sys
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-7-F4-ROUND2", "cycle": 20, "challenger": True}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
fa = g["RESULTS"]["controls"]["f4_audit"]
assert fa["s095"]["violations"] == 0 and g["RESULTS"]["controls"]["anchors_2025"]["f4_audit"]["violations"] == 0
print("BUILD CONTROLS ALL PASS in this pass; S095 timing audits 0 violations both years")
f4_keep, norm_f4 = g["f4_keep"], g["norm_f4"]

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
RKEY = lambda t: (t["date"], t["symbol"], t["dir"], round(float(t["net"]), 2), t["entry_time"])
LAW = {("GLENMARK", "SHORT"), ("HDFCBANK", "SHORT"), ("KALYANKJIL", "LONG")}
def lawdrop(rows):
    return [t for t in rows if (t["stock"], t["dir"]) not in LAW]

add = {}
for yr, raw, mine_raw, mine_norm, book in (
        ("2025", g["raw25"], g["f4_mine25"], g["f4_25"], book25),
        ("2026", g["raw095"], g["f4_mine26"], g["f4_26"], book26)):
    kept = [t for t in raw if f4_keep(t)]
    assert sorted(RKEY(t) for t in kept) == sorted(RKEY(t) for t in mine_raw), \
        f"kept-set mismatch {yr}"
    rows = [t for t in book if t["comp"] == "F4"]
    assert sorted(KEY(t) for t in lawdrop(mine_norm)) == sorted(KEY(t) for t in rows), \
        f"incumbent F4 anchor mismatch {yr}"
    add_raw = [t for t in raw if not f4_keep(t) and f4_keep({**t, "leg": "direct"})]
    if not add_raw:
        print(f"DIAGNOSIS STOP {yr}: round-flip isolation found 0 legs; "
              f"raw keys: {sorted(raw[0].keys())}")
        sys.exit(3)
    assert all(t["leg"] == "round2" and int(t["round"]) == 2 for t in add_raw)
    assert not ({RKEY(t) for t in add_raw} & {RKEY(t) for t in kept})
    addset = lawdrop(norm_f4(add_raw))
    add[yr] = [{"date": t["date"], "stock": t["stock"], "comp": "F4",
                "dir": t["dir"], "entry_time": t["entry_time"], "net": t["net"]}
               for t in addset]
    OUT[f"round2_{yr}"] = {
        "raw_population": len(raw), "kept": len(kept),
        "restoration_raw": len(add_raw),
        "restoration_after_law": [len(addset), round(sum(t["net"] for t in addset), 2)],
        "winners": sum(t["net"] > 0 for t in addset)}
    print(f"{yr}: raw {len(raw)} | kept {len(kept)} | round-blocked-only "
          f"{len(add_raw)} -> after v2 law {len(addset)} tr / "
          f"{OUT[f'round2_{yr}']['restoration_after_law'][1]} "
          f"({OUT[f'round2_{yr}']['winners']} w) | anchors PASS")
print("anchors PASS: kept sets == build F4 sets; incumbent F4 rows == kept minus v2 law")

nb25 = book25 + add["2025"]
nb26 = book26 + add["2026"]

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
    for fn, book in (("stocks_engine_v2_c20_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c20_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-20 challenger book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle20_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle20_result.json")
