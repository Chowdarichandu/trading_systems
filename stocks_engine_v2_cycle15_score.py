#!/usr/bin/env python3
"""V2 CYCLE 15 SCORE — CHALLENGER CH-V2-5 "N4-RESULTS-ONLY".

Frozen in stocks_engine_frozen.md (V2-CYCLE-15) BEFORE this run. The full
v2 build is re-executed in-process first: ALL its controls must pass in
this same pass. The parameterised n4 copy tags every trade with its
event-day class (results vs news-only); at the full combined set it must
reproduce the SAT-15 dump (2026 raw) and, after filters + the FULL
current v2 book law, the incumbent books' N4 rows in both years. The
challenger drops the news-only-day trades. Gate (v2 charter): bank iff
(a) combined rises AND (b) neither year falls AND (c) neither negative.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
OUT = {"fix_id": "CH-V2-5-N4-RESULTS-ONLY", "cycle": 15, "challenger": True}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
STOCKS_E, NIFTY_DAILY_E = g["STOCKS_E"], g["NIFTY_DAILY_E"]
replay, wk, SYMBOLS, SINGLE_NEWS = g["replay"], g["wk"], g["SYMBOLS"], g["SINGLE_NEWS"]
sametrades, rd, COST = g["sametrades"], g["rd"], g["COST"]

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

def n4_raw_tagged(cal_path, lo, hi):
    """The build's n4_raw verbatim (floor >=1.0, T150/S080) + day class."""
    res_set = {s: set() for s in SYMBOLS}
    news_set = {s: set() for s in SYMBOLS}
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in res_set: continue
            et = r["event_type"]
            if et != "results" and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                (res_set if et == "results" else news_set)[sym].add(ds)
    all_days = sorted(d["date"] for d in NIFTY_DAILY_E if lo <= d["date"] <= hi)
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        dmap = {d["date"]: i for i, d in enumerate(daily)}
        for day in all_days:
            if day not in res_set[sym] and day not in news_set[sym]: continue
            if day not in dmap or dmap[day] == 0: continue
            raw = spot.get(day, [])
            if not raw: continue
            prev_close = daily[dmap[day] - 1]["close"]
            if not prev_close: continue
            by_time = {c["time"]: c for c in raw}
            idx_of = {c["timestamp"]: i for i, c in enumerate(raw)}
            b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
            if b0925 is None or b0930 is None: continue
            move_pct = (b0925["close"] / prev_close - 1) * 100
            if abs(move_pct) >= 1.0:
                direction = "LONG" if move_pct > 0 else "SHORT"
                ei = idx_of[b0930["timestamp"]]
                entry = b0930["close"]
                r = replay(raw, ei, entry, direction, 1.50, 0.80)
                if r is None: continue
                er, ep, et = r
                sign = 1 if direction == "LONG" else -1
                out.append({"symbol": sym, "date": day, "direction": direction,
                            "entry_time": "09:35", "entry": round(entry, 2),
                            "exit_reason": er, "exit_price": round(ep, 2),
                            "exit_time": et,
                            "net": round(sign * (ep - entry) * 100 - COST, 2),
                            "day_class": "results" if day in res_set[sym] else "news"})
    return out

EXCL_WHOLE = {"ASTRAL"}
EXCL_DIR = {("TVSMOTOR", "LONG"), ("OIL", "LONG"), ("GLENMARK", "SHORT"),
            ("BDL", "SHORT"), ("HINDALCO", "SHORT"), ("HINDZINC", "LONG"),
            ("UNITDSPR", "LONG"), ("RECLTD", "LONG")}
def n4_book_law(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "N4-V3",
             "dir": t["direction"], "net": t["net"], "entry_time": t["entry_time"],
             "day_class": t["day_class"]}
            for t in raw
            if not wk(t["date"]) and t["symbol"] not in EXCL_WHOLE
            and (t["symbol"], t["direction"]) not in EXCL_DIR]

KEY = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2))
CAL26, CAL25 = g["CAL26"], g["CAL25"]
raw26 = n4_raw_tagged(CAL26, "2026-01-01", "2026-10-28")
sat15 = rd("stocks_engine_sat15_n4_t150s080_trades.csv")
assert sametrades(
    [{"date": t["date"], "stock": t["symbol"], "dir": t["direction"],
      "net": t["net"], "entry_time": t["entry_time"]} for t in raw26],
    sat15, ("date", "stock", "dir", "entry_time", "net"),
    ("date", "stock", "direction", "entry_time", "net")), "tagged copy != SAT-15 dump"
print("anchor 1 PASS: tagged copy == SAT-15 dump per-trade (2026 raw)")
raw25 = n4_raw_tagged(CAL25, "2025-01-01", "2025-12-31")
full = {}
for yr, raw, book in (("2025", raw25, book25), ("2026", raw26, book26)):
    mine = n4_book_law(raw)
    rows = [t for t in book if t["comp"] == "N4-V3"]
    assert sorted(KEY(t) for t in mine) == sorted(KEY(t) for t in rows), f"N4 anchor mismatch {yr}"
    full[yr] = mine
print("anchor 2 PASS: tagged copy + filters + full v2 law == incumbent N4 rows, both years")

ch = {}
for yr, book in (("2025", book25), ("2026", book26)):
    mine = full[yr]
    news = [t for t in mine if t["day_class"] == "news"]
    chset = [t for t in mine if t["day_class"] == "results"]
    inc = [t for t in book if t["comp"] == "N4-V3"]
    assert {KEY(t) for t in chset} <= {KEY(t) for t in inc}
    ch[yr] = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
               "dir": t["dir"], "entry_time": t["entry_time"], "net": t["net"]}
              for t in chset]
    OUT[f"n4_{yr}"] = {
        "incumbent": [len(inc), round(sum(t["net"] for t in inc), 2)],
        "challenger_results_only": [len(chset), round(sum(t["net"] for t in chset), 2)],
        "news_only_slice": [len(news), round(sum(t["net"] for t in news), 2),
                            sum(t["net"] > 0 for t in news)]}
    print(f"{yr}: N4 full {len(inc)} tr / {OUT[f'n4_{yr}']['incumbent'][1]} | "
          f"news-only slice {len(news)} tr / {OUT[f'n4_{yr}']['news_only_slice'][1]} "
          f"({OUT[f'n4_{yr}']['news_only_slice'][2]} w) | "
          f"results-only {len(chset)} tr / {OUT[f'n4_{yr}']['challenger_results_only'][1]}")
    for t in news:
        print(f"   news-only: {t['date']} {t['stock']:<11} {t['dir']:<5} net {t['net']:+.2f}")

def swap(book, chset):
    return [t for t in book if t["comp"] != "N4-V3"] + chset
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
    for fn, book in (("stocks_engine_v2_c15_book2025_trades.csv", nb25),
                     ("stocks_engine_v2_c15_book2026_trades.csv", nb26)):
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "stock", "comp", "dir", "entry_time", "net"])
            for t in sorted(book, key=lambda x: (x["date"], x["entry_time"],
                                                 x["stock"], x["comp"])):
                w.writerow([t["date"], t["stock"], t["comp"], t["dir"],
                            t["entry_time"], t["net"]])
    print("wrote post-Cycle-15 challenger book CSVs (new incumbent)")
json.dump(OUT, open(f"{WS}/v2_out/v2_cycle15_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle15_result.json")
