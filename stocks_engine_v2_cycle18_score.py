#!/usr/bin/env python3
"""V2 CYCLE 18 SCORE — CHALLENGER CH-V2-6 "P2F-EXITS" (T125/S050 -> T150/S080).

Frozen in stocks_engine_frozen.md (V2-CYCLE-18) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass. The parameterised score_lag copy must reproduce the
build's incumbent P2F sets at (1.25, 0.50) in both years, and those sets
must equal the incumbent books' P2F rows; the challenger entry set must
equal the incumbent's. Gate (v2 charter): bank iff (a) combined rises
AND (b) neither year falls AND (c) neither year negative at book level.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-6-P2F-EXITS", "cycle": 18, "challenger": True}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
STOCKS_E, replay, wk, net_of = g["STOCKS_E"], g["replay"], g["wk"], g["net_of"]

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

def score_lag_x(cand, lag, tgt_pct, stp_pct):
    """The build's score_lag verbatim, exits parameterised."""
    sym = cand["symbol"]; spot, daily = STOCKS_E[sym]
    ri = cand["ri"]
    if ri + lag >= len(daily): return None
    d = daily[ri + lag]["date"]
    bars = spot.get(d, [])
    if not bars: return None
    entry = bars[0]["open"]
    r = replay(bars, 0, entry, cand["direction"], tgt_pct, stp_pct)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d, "direction": cand["direction"],
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(cand["direction"], entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"]}

def p2f_book_x(cands, tgt, stp):
    raw = [t for t in (score_lag_x(c, 1, tgt, stp) for c in cands
                       if abs(c["reaction_ret_pct"]) >= 2.5) if t]
    return [{"date": t["date"], "stock": t["symbol"], "comp": "P2F",
             "dir": t["direction"], "net": t["net_rs"],
             "entry_time": t["entry_time"]}
            for t in raw
            if not wk(t["date"]) and t["symbol"] != "ASTRAL"
            and t["symbol"] != "HINDUNILVR"
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

KEY = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2))
EKEY = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"])
ch = {}
for yr, cands, mine, book in (("2025", g["cands25"], g["p2f_mine25"], book25),
                              ("2026", g["cands26"], g["p2f_mine26"], book26)):
    base = p2f_book_x(cands, 1.25, 0.50)
    assert sorted(KEY(t) for t in base) == sorted(KEY(t) for t in mine), \
        f"parameterised copy at (1.25,0.50) != build P2F {yr}"
    rows = [t for t in book if t["comp"] == "P2F"]
    assert sorted(KEY(t) for t in base) == sorted(KEY(t) for t in rows), \
        f"incumbent P2F anchor mismatch {yr}"
    chset = p2f_book_x(cands, 1.50, 0.80)
    assert sorted(EKEY(t) for t in chset) == sorted(EKEY(t) for t in rows), \
        f"entry-set mismatch {yr}"
    ch[yr] = chset
    OUT[f"p2f_{yr}"] = {
        "incumbent": [len(rows), round(sum(t["net"] for t in rows), 2)],
        "challenger": [len(chset), round(sum(t["net"] for t in chset), 2)]}
    print(f"{yr}: P2F T125/S050 {len(rows)} tr / {OUT[f'p2f_{yr}']['incumbent'][1]} -> "
          f"T150/S080 {len(chset)} tr / {OUT[f'p2f_{yr}']['challenger'][1]} | "
          f"anchors PASS, entries identical")
print("anchors PASS: copy@(1.25,0.50) == build P2F == incumbent P2F rows, both years")

def swap(book, chset):
    return [t for t in book if t["comp"] != "P2F"] + chset
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
    for fn, book in (("stocks_engine_v2_c18_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c18_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-18 challenger book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle18_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle18_result.json")
