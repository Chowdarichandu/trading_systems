#!/usr/bin/env python3
"""V2 CYCLE 27 — CH-V2-12 "P2F-NEWS" (frozen in stocks_engine_frozen.md
BEFORE this run).

Additive challenger: the audited P2F machinery verbatim (reaction
close-to-close on the reaction day, direction = reaction sign, band
>= 2.5%, entry R+1 09:15 open, T125/S050 via score_lag lag 1, RF-1,
P2F's frozen exclusions) with the event universe switched from results
to the SINGLE_NEWS classes (the set N4-V3 trades; dividend excluded).
Frozen counts (cycle diagnosis): candidates 10 (2025) / 11 (2026);
at band 3 / 4. Anchor asserted in-pass: the generalised candidate
builder restricted to {results} reproduces the build's
reaction_candidates exactly in both years.
Decision (Cycle-6 additive standard + C24 cell guard): bank iff the
cross-year gate passes AND component combined expectancy > 0 AND it
beats the flip placebo per-trade AND no regime cell flips negative.
Basis: equity cash LONG/SHORT, home 25, provisional per 100 shares,
Rs40/trade, paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from datetime import date, timedelta
from statistics import pstdev

WS = "/home/hatch/workspace/trading"
FROZEN_CANDS = {"2025": (9, 2), "2026": (11, 4)}   # post-dedup (freeze construction note)

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
STOCKS_E, SYMBOLS, wk = g["STOCKS_E"], g["SYMBOLS"], g["wk"]
SINGLE_NEWS, score_lag = g["SINGLE_NEWS"], g["score_lag"]
reaction_candidates = g["reaction_candidates"]

NIFTY_REG, below50 = g["NIFTY_REG"], g["below50"]
axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
LABELS = {}
for j, d in enumerate(axis):
    if j < 5:
        continue
    pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
    s = m - NIFTY_REG[axis[j - 5]]["ma50"]
    LABELS[d] = "UP" if (pc > m and s >= 0) else ("DOWN" if (pc <= m and s <= 0) else "FLAT")
for d in axis:
    if "2025-01-01" <= d <= "2026-10-30":
        assert (NIFTY_REG[d]["prev_close"] <= NIFTY_REG[d]["ma50"]) == below50(d)
print("classifier asserted: price leg == below50 on all window days")

def class_candidates(cal_path, lo, hi, types):
    """reaction_candidates verbatim, with the event-class filter open."""
    evs = []
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            if r["event_type"] not in types or r["stock"] not in SYMBOLS:
                continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                evs.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
    evs.sort(key=lambda e: (e["symbol"], e["R"]))
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
        if nd > hi:
            continue
        if not spot.get(nd):
            continue
        cands.append({"symbol": sym, "announce": e["announce"], "R": R,
                      "reaction_ret_pct": reaction_ret, "ri": ri,
                      "direction": "LONG" if reaction_ret > 0 else "SHORT"})
    return cands

def news_book(cands, flip=False):
    raw = []
    for c in cands:
        if abs(c["reaction_ret_pct"]) < 2.5:
            continue
        cc = dict(c)
        if flip:
            cc["direction"] = "SHORT" if c["direction"] == "LONG" else "LONG"
        t = score_lag(cc, 1)
        if t:
            raw.append(t)
    return [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-NEWS",
             "dir": t["direction"], "net": t["net_rs"],
             "entry_time": t["entry_time"], "R": t["R"],
             "reaction_ret_pct": t["reaction_ret_pct"]}
            for t in raw
            if not wk(t["date"]) and t["symbol"] != "ASTRAL"
            and t["symbol"] != "HINDUNILVR"
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
books = {yr: load(state["book_files"][yr]) for yr in ("2025", "2026")}
inc = {}
for yr in ("2025", "2026"):
    inc[yr] = round(sum(t["net"] for t in books[yr]), 2)
    assert (len(books[yr]), inc[yr]) == (state["best_trades"][yr], state["best_by_year"][yr])
print(f"incumbent asserted: 2025 {inc['2025']} ({len(books['2025'])} tr) | 2026 {inc['2026']} ({len(books['2026'])} tr)")

def cells(book):
    o = {}
    for cell in ("UP", "DOWN", "FLAT"):
        ts = [t for t in book if LABELS.get(t["date"]) == cell]
        o[cell] = [len(ts), round(sum(t["net"] for t in ts), 2)]
    return o
def summ(rs):
    net = round(sum(r["net"] for r in rs), 2)
    return {"trades": len(rs), "net": net,
            "expectancy": round(net / len(rs), 2) if rs else None,
            "winners": sum(r["net"] > 0 for r in rs)}

out = {"cycle": 27, "challenger": "CH-V2-12 P2F-NEWS", "detail": {}}
comp_rows = {}
for yr, cal, lo, hi in (("2025", g["CAL25"], g["LO25"], g["HI25"]),
                        ("2026", g["CAL26"], g["LO26"], g["HI26"])):
    anchor = class_candidates(cal, lo, hi, {"results"})
    base = reaction_candidates(cal, lo, hi)
    akey = sorted((c["symbol"], c["R"], c["reaction_ret_pct"], c["direction"]) for c in anchor)
    bkey = sorted((c["symbol"], c["R"], c["reaction_ret_pct"], c["direction"]) for c in base)
    assert akey == bkey, f"{yr} generalised builder != reaction_candidates"
    cands_all = class_candidates(cal, lo, hi, SINGLE_NEWS)
    res_keys = {(c["symbol"], c["R"]) for c in base}
    # Dedup (freeze construction note): the results machinery owns a
    # reaction day it already trades; news candidates on such a day drop.
    cands = [c for c in cands_all if (c["symbol"], c["R"]) not in res_keys]
    n_band = sum(1 for c in cands if abs(c["reaction_ret_pct"]) >= 2.5)
    assert (len(cands), n_band) == FROZEN_CANDS[yr], \
        f"{yr} candidate counts {(len(cands), n_band)} != frozen {FROZEN_CANDS[yr]}"
    assert not ({(c["symbol"], c["R"]) for c in cands} & res_keys), \
        f"{yr} post-dedup news candidates still overlap results candidates"
    comp = news_book(cands)
    placebo = news_book(cands, flip=True)
    comp_rows[yr] = comp
    out["detail"][yr] = {"component": summ(comp), "placebo": summ(placebo),
                         "component_rows": comp}
    print(f"{yr} P2F-NEWS: {len(comp)} tr net {out['detail'][yr]['component']['net']} "
          f"exp {out['detail'][yr]['component']['expectancy']} | "
          f"placebo: {len(placebo)} tr net {out['detail'][yr]['placebo']['net']} "
          f"exp {out['detail'][yr]['placebo']['expectancy']}")

new_books, out_y = {}, {}
for yr in ("2025", "2026"):
    nb = books[yr] + [{k: t[k] for k in ("comp", "date", "stock", "dir", "entry_time", "net")}
                      for t in comp_rows[yr]]
    new_books[yr] = nb
    out_y[yr] = {"before": inc[yr], "after": round(sum(t["net"] for t in nb), 2),
                 "trades": len(nb)}
    out[yr] = out_y[yr]

comb_old = round(inc["2025"] + inc["2026"], 2)
comb_new = round(out_y["2025"]["after"] + out_y["2026"]["after"], 2)
ntr = sum(out["detail"][yr]["component"]["trades"] for yr in ("2025", "2026"))
nnet = round(sum(out["detail"][yr]["component"]["net"] for yr in ("2025", "2026")), 2)
ptr = sum(out["detail"][yr]["placebo"]["trades"] for yr in ("2025", "2026"))
pnet = round(sum(out["detail"][yr]["placebo"]["net"] for yr in ("2025", "2026")), 2)
comp_exp = round(nnet / ntr, 2) if ntr else None
pla_exp = round(pnet / ptr, 2) if ptr else None
gate = {"combined_rises": comb_new > comb_old,
        "y2025_not_fall": out_y["2025"]["after"] >= inc["2025"],
        "y2026_not_fall": out_y["2026"]["after"] >= inc["2026"],
        "neither_negative": out_y["2025"]["after"] >= 0 and out_y["2026"]["after"] >= 0}
l21 = {"component_expectancy_positive": (comp_exp or -1) > 0,
       "beats_flip_placebo_per_trade": (comp_exp or -1e9) > (pla_exp if pla_exp is not None else -1e9)}
cells_after = {yr: cells(new_books[yr]) for yr in ("2025", "2026")}
cell_guard = all(v[1] > 0 for yr in ("2025", "2026") for v in cells_after[yr].values())
banked = all(gate.values()) and all(l21.values()) and cell_guard
out.update({"gate": gate, "l21_standard": l21, "cell_guard_all_positive": cell_guard,
            "component_combined": {"trades": ntr, "net": nnet, "expectancy": comp_exp},
            "placebo_combined": {"trades": ptr, "net": pnet, "expectancy": pla_exp},
            "combined": {"before": comb_old, "after": comb_new}, "banked": banked})
print(f"gate: {gate} | L21: {l21} | cell guard: {cell_guard}")
print(f"component combined {ntr} tr {nnet} exp {comp_exp} | placebo {ptr} tr {pnet} exp {pla_exp}")
print(f"combined {comb_old} -> {comb_new} | BANKED: {banked}")

if banked:
    def dump(rows, fn):
        rows = sorted(rows, key=lambda t: (t["date"], t.get("entry_time", "09:15"),
                                           t["stock"], t["comp"]))
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["comp", "date", "stock", "dir",
                                              "entry_time", "net"])
            w.writeheader(); w.writerows(rows)
    dump(new_books["2025"], "stocks_engine_v2_c27_book2025_trades.csv")
    dump(new_books["2026"], "stocks_engine_v2_c27_book2026_trades.csv")
    def months(book, ms):
        m = defaultdict(float)
        for t in book:
            m[t["date"][:7]] += t["net"]
        return {k: round(m.get(k, 0.0), 2) for k in ms}
    def extop3(book):
        p = defaultdict(float)
        for t in book:
            p[t["stock"]] += t["net"]
        top = {k for k, _ in sorted(p.items(), key=lambda kv: -kv[1])[:3]}
        return round(sum(t["net"] for t in book if t["stock"] not in top), 2)
    m25 = months(new_books["2025"], [f"2025-{i:02d}" for i in range(1, 13)])
    m26 = months(new_books["2026"], [f"2026-{i:02d}" for i in range(1, 11)])
    av = list(m25.values()) + list(m26.values())
    out["new_book"] = {"cells2025": cells_after["2025"], "cells2026": cells_after["2026"],
                       "months2025": m25, "months2026": m26,
                       "red_months2025": [k for k, v in m25.items() if v < 0],
                       "red_months2026": [k for k, v in m26.items() if v < 0],
                       "spread": {"min": min(av), "max": max(av),
                                  "range": round(max(av) - min(av), 2),
                                  "stdev": round(pstdev(av), 2),
                                  "months_in_band_20k_pm1k": sum(1 for v in av if 19000 <= v <= 21000)},
                       "ex_top3": {"2025": extop3(new_books["2025"]),
                                   "2026": extop3(new_books["2026"])}}
    print(f"new book cells 2025 {cells_after['2025']} | 2026 {cells_after['2026']}")
    print("wrote c27 book CSVs")
json.dump(out, open(f"{WS}/v2_out/v2_cycle27_result.json", "w"), indent=1, default=str)
print("wrote v2_out/v2_cycle27_result.json")
