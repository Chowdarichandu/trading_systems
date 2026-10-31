#!/usr/bin/env python3
"""V2 CYCLE 6 SCORE — CHALLENGER CH-V2-2 "P2F-NEWS" under the cross-year gate.

Frozen in stocks_engine_frozen.md (V2-CYCLE-6) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass. The challenger adds ONE new component (R+1 follow of
NEWS-event reactions, band >=2.5%, score_lag verbatim at lag 1) to the
post-Cycle-5 incumbent books. Banking standard (pre-registered): the v2
cross-year gate AND the Lesson 21 full test on the component (standalone
expectancy > 0 AND beats its flip placebo per-trade).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-2-P2F-NEWS", "cycle": 6, "challenger": True}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
STOCKS_E, wk, score_lag = g["STOCKS_E"], g["wk"], g["score_lag"]
SINGLE_NEWS, SYMBOLS = g["SINGLE_NEWS"], g["SYMBOLS"]

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

def news_candidates(cal_path, lo, hi):
    """Mirror of the build's results candidate path, over SINGLE_NEWS rows."""
    evs = []
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            if r["event_type"] not in SINGLE_NEWS or r["stock"] not in SYMBOLS:
                continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                evs.append({"symbol": r["stock"], "R": ds,
                            "event_type": r["event_type"]})
    cands = []
    for e in evs:
        sym, R = e["symbol"], e["R"]
        spot, daily = STOCKS_E[sym]
        didx = {d["date"]: i for i, d in enumerate(daily)}
        if R not in didx:
            continue
        ri = didx[R]
        if ri == 0 or ri + 1 >= len(daily):
            continue
        reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
        nd = daily[ri + 1]["date"]
        if nd > hi or not spot.get(nd):
            continue
        # independent recomputation of the reaction return from the raw CSV
        with open(f"{WS}/data/full_hist/{sym}/spot_daily.csv") as f:
            rows = list(csv.DictReader(f))
        j = [i for i, r in enumerate(rows) if r["date"][:10] == R][0]
        chk = round((float(rows[j]["close"]) / float(rows[j - 1]["close"]) - 1) * 100, 2)
        assert chk == reaction_ret, f"reaction recompute mismatch {sym} {R}"
        cands.append({"symbol": sym, "R": R, "ri": ri,
                      "reaction_ret_pct": reaction_ret,
                      "direction": "LONG" if reaction_ret > 0 else "SHORT",
                      "event_type": e["event_type"],
                      "entry_date": nd})
    return cands

def build_component(cal, lo, hi, book):
    cands = news_candidates(cal, lo, hi)
    inband = [c for c in cands if abs(c["reaction_ret_pct"]) >= 2.5]
    p2f_keys = {(t["date"], t["stock"], t["dir"]) for t in book if t["comp"] == "P2F"}
    trades, dropped_dupe, dropped_nobar = [], 0, 0
    placebo = []
    for c in inband:
        t = score_lag(c, 1)
        if t is None:
            dropped_nobar += 1
            continue
        if wk(t["date"]):
            continue
        if (t["date"], t["symbol"], t["direction"]) in p2f_keys:
            dropped_dupe += 1
            continue
        # timing: entry is the trading day strictly after R by construction
        assert t["date"] == c["entry_date"] and t["date"] > c["R"]
        trades.append({"date": t["date"], "stock": t["symbol"], "comp": "P2F-NEWS",
                       "dir": t["direction"], "entry_time": t["entry_time"],
                       "net": t["net_rs"], "R": c["R"],
                       "reaction_ret_pct": c["reaction_ret_pct"]})
        fc = dict(c, direction=("SHORT" if c["direction"] == "LONG" else "LONG"))
        pt = score_lag(fc, 1)
        if pt is not None and not wk(pt["date"]):
            placebo.append(pt["net_rs"])
    return cands, inband, trades, placebo, dropped_dupe, dropped_nobar

CAL26, CAL25 = g["CAL26"], g["CAL25"]
res = {}
for yr, cal, lo, hi, book in (("2025", CAL25, "2025-01-01", "2025-12-31", book25),
                              ("2026", CAL26, "2026-01-01", "2026-10-28", book26)):
    cands, inband, trades, placebo, dd, dn = build_component(cal, lo, hi, book)
    net = round(sum(t["net"] for t in trades), 2)
    pnet = round(sum(placebo), 2)
    res[yr] = {"news_candidates": len(cands), "inband": len(inband),
               "trades": trades, "net": net,
               "expectancy": round(net / len(trades), 2) if trades else 0.0,
               "winners": sum(t["net"] > 0 for t in trades),
               "placebo_net": pnet, "placebo_trades": len(placebo),
               "placebo_expectancy": round(pnet / len(placebo), 2) if placebo else 0.0,
               "dropped_dupe": dd, "dropped_nobar": dn}
    print(f"{yr}: news candidates {len(cands)} -> in-band {len(inband)} -> "
          f"trades {len(trades)} / net {net} / exp {res[yr]['expectancy']} / "
          f"w {res[yr]['winners']} | placebo {len(placebo)} tr / {pnet} / "
          f"exp {res[yr]['placebo_expectancy']} | dupes dropped {dd}, no-bar {dn}")
    for t in trades:
        print(f"   {t['date']} {t['stock']:<11} {t['dir']:<5} R {t['R']} "
              f"ret {t['reaction_ret_pct']:+.2f}% net {t['net']:+.2f}")

comb_exp = round((res["2025"]["net"] + res["2026"]["net"]) /
                 max(1, len(res["2025"]["trades"]) + len(res["2026"]["trades"])), 2)
comb_pexp = round((res["2025"]["placebo_net"] + res["2026"]["placebo_net"]) /
                  max(1, res["2025"]["placebo_trades"] + res["2026"]["placebo_trades"]), 2)
lesson21 = {"expectancy_positive": comb_exp > 0,
            "beats_placebo_per_trade": comb_exp > comb_pexp}
print(f"component combined expectancy {comb_exp} vs placebo {comb_pexp} | L21: {lesson21}")

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
nb25 = book25 + res["2025"]["trades"]
nb26 = book26 + res["2026"]["trades"]
s25, s26 = year_stats(nb25, M25), year_stats(nb26, M26)
o25, o26 = year_stats(book25, M25), year_stats(book26, M26)
comb_b = round(EXP25[1] + EXP26[1], 2)
comb_a = round(s25["total"] + s26["total"], 2)
gate = {"a_combined_rises": comb_a > comb_b,
        "b_neither_year_falls": s25["total"] >= EXP25[1] and s26["total"] >= EXP26[1],
        "c_neither_year_negative": s25["total"] >= 0 and s26["total"] >= 0}
banked = all(gate.values()) and all(lesson21.values())
OUT.update({
    "incumbent": {"y2025": EXP25[1], "y2026": EXP26[1], "combined": comb_b},
    "component": {yr: {k: v for k, v in res[yr].items() if k != "trades"} |
                  {"trade_rows": res[yr]["trades"]} for yr in res},
    "component_combined_expectancy": comb_exp,
    "component_placebo_expectancy": comb_pexp,
    "lesson21": lesson21,
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
print("GATE:", gate, "| L21:", lesson21, "-> BANKED:", banked)
if banked:
    for fn, book in (("stocks_engine_v2_c6_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c6_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-6 book CSVs (new incumbent, SEVEN components)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle6_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle6_result.json")
