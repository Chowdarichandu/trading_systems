#!/usr/bin/env python3
"""V3 DIAGNOSIS — incumbent (frozen post-C24 SarvaRitu book) decomposition
under the v3 maximin charter. Read-only on the incumbent + COUNTS ONLY for
challenger discard populations (no challenger P&L is read before a freeze,
per the v2 growth-phase discipline).

Reports: month vector + bottom-8 decomposition (per-comp nets/trades),
regime day counts per weak month, the maximin deletion scan ((comp x stock
x dir) slices <= 0 in BOTH years, with worst-month legs), (comp x cell)
both-years-negative scan, and INV discard population counts by month
(round >= 3 early entries, ADR >= 3.0, by gate) — whether the recorded
INV-R3 queue would have traded in the weak months at all.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
import os
os.makedirs(f"{WS}/v3_out", exist_ok=True)

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
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

state = json.load(open(f"{WS}/stocks_engine_state.json"))
v2, v3 = state["v2"], state["v3"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
books = {yr: load(v3["book_files"][yr]) for yr in ("2025", "2026")}
for yr in ("2025", "2026"):
    b = books[yr]
    assert (len(b), round(sum(t["net"] for t in b), 2)) == \
        (v2["best_trades"][yr], v2["best_by_year"][yr]), f"{yr} incumbent mismatch"
print("incumbent asserted == post-C24 dumps (745/626 tr, +27,479.24/+211,588.10)")

M25 = [f"2025-{i:02d}" for i in range(1, 13)]
M26 = [f"2026-{i:02d}" for i in range(1, 11)]
def months(book, ms):
    m = defaultdict(float)
    for t in book:
        m[t["date"][:7]] += t["net"]
    return {k: round(m.get(k, 0.0), 2) for k in ms}
mall = {**months(books["2025"], M25), **months(books["2026"], M26)}
vec = sorted(mall.values())
assert vec == v3["month_vector_sorted_asc"], "month vector != state v3 record"
print("month vector asserted == v3 state record")

def cells(book):
    o = {}
    for cell in ("UP", "DOWN", "FLAT"):
        ts = [t for t in book if LABELS.get(t["date"]) == cell]
        o[cell] = round(sum(t["net"] for t in ts), 2)
    return o
CELLS = {yr: cells(books[yr]) for yr in ("2025", "2026")}
print("cells:", CELLS)

WEAK = [m for m, _ in sorted(mall.items(), key=lambda kv: kv[1])[:8]]
print("bottom-8 months:", [(m, mall[m]) for m in WEAK])

# --- weak-month decomposition -------------------------------------------
decomp = {}
for m in WEAK:
    yr = m[:4]
    rows = [t for t in books[yr] if t["date"][:7] == m]
    pc = defaultdict(lambda: [0, 0.0])
    for t in rows:
        pc[t["comp"]][0] += 1
        pc[t["comp"]][1] += t["net"]
    days = {d for d in LABELS if d.startswith(m)}
    dc = Counter(LABELS[d] for d in days)
    traded_days = len({t["date"] for t in rows})
    decomp[m] = {"net": mall[m], "trades": len(rows), "traded_days": traded_days,
                 "calendar_days_by_cell": dict(dc),
                 "per_comp": {c: [v[0], round(v[1], 2)] for c, v in sorted(pc.items())}}
    print(f"{m}: net {mall[m]:+.2f} | {len(rows)} tr on {traded_days} days | "
          f"days by cell {dict(dc)} | per-comp {decomp[m]['per_comp']}")

# --- maximin deletion scan (incumbent's own slices) ----------------------
slices = defaultdict(lambda: {"2025": 0.0, "2026": 0.0, "n": 0,
                              "weak_legs": defaultdict(float)})
for yr in ("2025", "2026"):
    for t in books[yr]:
        s = slices[(t["comp"], t["stock"], t["dir"])]
        s[yr] += t["net"]; s["n"] += 1
        if t["date"][:7] in WEAK:
            s["weak_legs"][t["date"][:7]] += t["net"]
both_nonpos = []
for k, s in slices.items():
    if s["2025"] <= 0 and s["2026"] <= 0 and (s["2025"] < 0 or s["2026"] < 0):
        both_nonpos.append({"slice": k, "n": s["n"],
                            "y2025": round(s["2025"], 2), "y2026": round(s["2026"], 2),
                            "combined": round(s["2025"] + s["2026"], 2),
                            "weak_legs": {m: round(v, 2) for m, v in s["weak_legs"].items() if v < 0}})
both_nonpos.sort(key=lambda r: r["combined"])
print(f"\ndeletion scan: {len(both_nonpos)} (comp x stock x dir) slices <= 0 in both years")
for r in both_nonpos:
    print("  ", r)

# (comp x cell) both-years-negative scan
cc = defaultdict(lambda: {"2025": 0.0, "2026": 0.0, "n": 0})
for yr in ("2025", "2026"):
    for t in books[yr]:
        e = cc[(t["comp"], LABELS.get(t["date"]))]
        e[yr] += t["net"]; e["n"] += 1
ccneg = [{"pair": k, **{y: round(v[y], 2) for y in ("2025", "2026")}, "n": v["n"]}
         for k, v in cc.items() if v["2025"] <= 0 and v["2026"] <= 0
         and (v["2025"] < 0 or v["2026"] < 0)]
print(f"(comp x cell) both-years-nonpositive pairs: {ccneg}")

# --- INV discard populations: COUNTS ONLY --------------------------------
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
cond_inv1, g1, SYMBOLS = g["cond_inv1"], g["g1"], g["SYMBOLS"]
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}
def inv_population(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    return rows
r3_counts = {}
round_dist = Counter()
for yr, days in (("2025", g["days25"]), ("2026", g["days26"])):
    pop = inv_population(days)
    for r in pop:
        round_dist[r["round"]] += 1
    for gate_name, gate in (("below", cond_inv1), ("above", g1)):
        r3 = [r for r in pop if r["round"] >= 3 and r["entry_time"] < "10:30"
              and (r["adr"] or 0) >= 3.0 and gate(r["date"])
              and r["direction"] == "LONG" and not wk(r["date"])
              and r["stock"] not in BASE_EXCL and r["stock"] not in V2_LAW]
        by_month = Counter(r["date"][:7] for r in r3)
        r3_counts[f"{yr}-{gate_name}"] = {"total": len(r3), "by_month": dict(sorted(by_month.items())),
                                          "weak_month_rows": {m: by_month.get(m, 0) for m in WEAK}}
        print(f"INV-R3 counts {yr} gate={gate_name}: {len(r3)} rows | by month {dict(sorted(by_month.items()))}")
print("round distribution (all chain rows, both years):", dict(sorted(round_dist.items())))

# --- calendar density in weak months --------------------------------------
cal_density = {}
for m in WEAK:
    yr = m[:4]
    cal = f"{WS}/stock_event_calendar_2025.csv" if yr == "2025" else f"{WS}/stock_event_calendar_jan_oct_2026.csv"
    nres = nnews = 0
    for r in csv.DictReader(open(cal)):
        rd_ = (r["reaction_date"] or r["event_date"])[:7]
        if rd_ == m:
            if r["event_type"] == "results": nres += 1
            else: nnews += 1
    cal_density[m] = {"results_reaction_days": nres, "news_rows": nnews}
    print(f"calendar {m}: {nres} results reactions, {nnews} news rows")

json.dump({"month_vector": vec, "months": mall, "cells": CELLS,
           "weak_decomp": decomp, "deletion_scan_both_nonpos": both_nonpos,
           "comp_cell_both_nonpos": ccneg, "inv_r3_counts": r3_counts,
           "round_dist": {str(k): v for k, v in round_dist.items()},
           "calendar_density": cal_density},
          open(f"{WS}/v3_out/v3_diag.json", "w"), indent=1)
print("wrote v3_out/v3_diag.json")
