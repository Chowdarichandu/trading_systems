#!/usr/bin/env python3
"""V2 CYCLE 24+ DIAGNOSIS (no change scored here).

Reads only: (i) the C24 freeze numbers (INV-LONG x FLAT on the C23 book,
the pair queued at C23: both-years-negative cell pair); (ii) incumbent
decompositions for challenger design — (comp x cell) both-negative pairs,
INV-ABOVE x stock both-negative pairs, P2F band buckets; (iii) population
SIZES (counts only, no P&L) for the challenger candidates: news-class
reaction candidates, INV populations discarded by the p2 filters
(round>=3, entry>=10:30). Challenger P&L is read only in score runs,
after each freeze is written.
Controls: full v2 build re-executes in-pass; ALL controls must pass;
classifier price leg asserted == below50; incumbent books == state.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import Counter, defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
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

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
books = {yr: load(state["book_files"][yr]) for yr in ("2025", "2026")}
for yr in ("2025", "2026"):
    tot = round(sum(t["net"] for t in books[yr]), 2)
    assert (len(books[yr]), tot) == (state["best_trades"][yr], state["best_by_year"][yr])
print(f"incumbent asserted: 2025 {state['best_by_year']['2025']} | 2026 {state['best_by_year']['2026']}")

out = {}

# --- (i) C24 freeze numbers: INV-LONG x FLAT -------------------------------
fz = {}
for yr in ("2025", "2026"):
    rows = [t for t in books[yr] if t["comp"] == "INV-LONG" and LABELS.get(t["date"]) == "FLAT"]
    fz[yr] = [len(rows), round(sum(t["net"] for t in rows), 2)]
out["c24_inv_long_flat"] = fz
print(f"C24 freeze numbers INV-LONG x FLAT: {fz}")

# --- (ii-a) (comp x cell) both-years-negative pairs ------------------------
pairs = {}
for yr in ("2025", "2026"):
    agg = defaultdict(list)
    for t in books[yr]:
        agg[(t["comp"], LABELS.get(t["date"]))].append(t["net"])
    for k, v in agg.items():
        pairs.setdefault(k, {})[yr] = [len(v), round(sum(v), 2)]
both_neg = {str(k): v for k, v in pairs.items()
            if v.get("2025", [0, 0])[1] < 0 and v.get("2026", [0, 0])[1] < 0}
out["comp_cell_both_negative"] = both_neg
print(f"(comp x cell) both-negative pairs: {both_neg}")

# --- (ii-b) INV-ABOVE x stock both-negative (bar: combined <= -500) --------
sa = {}
for yr in ("2025", "2026"):
    agg = defaultdict(list)
    for t in books[yr]:
        if t["comp"] == "INV-ABOVE":
            agg[t["stock"]].append(t["net"])
    for k, v in agg.items():
        sa.setdefault(k, {})[yr] = [len(v), round(sum(v), 2)]
ia_neg = {k: v for k, v in sa.items()
          if v.get("2025", [0, 0])[1] < 0 and v.get("2026", [0, 0])[1] < 0
          and v.get("2025", [0, 0])[1] + v.get("2026", [0, 0])[1] <= -500}
out["inv_above_stock_both_negative_bar"] = ia_neg
print(f"INV-ABOVE x stock both-negative at bar: {ia_neg}")

# --- (ii-c) P2F band buckets (build sets asserted == book P2F rows) --------
bk = {}
for yr, mine in (("2025", g["p2f_mine25"]), ("2026", g["p2f_mine26"])):
    key = lambda t: (t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2))
    assert Counter(map(key, mine)) == Counter(map(key, [t for t in books[yr] if t["comp"] == "P2F"])), \
        f"{yr} build P2F != book P2F rows"
    buckets = {}
    for lo, hi, name in ((2.5, 3.5, "[2.5,3.5)"), (3.5, 5.0, "[3.5,5)"), (5.0, 1e9, ">=5")):
        rows = [t for t in mine if lo <= abs(t["reaction_ret_pct"]) < hi]
        buckets[name] = [len(rows), round(sum(t["net"] for t in rows), 2)]
    bk[yr] = buckets
out["p2f_band_buckets"] = bk
print(f"P2F band buckets: {bk}")

# --- (iii-a) news-class reaction candidates (counts only) ------------------
SINGLE_NEWS = g["SINGLE_NEWS"]
STOCKS_E = g["STOCKS_E"]
def class_events(cal_path, lo, hi, types):
    evs = []
    with open(cal_path) as f:
        for r in csv.DictReader(f):
            if r["event_type"] not in types or r["stock"] not in g["SYMBOLS"]:
                continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if lo <= ds <= hi:
                evs.append({"symbol": r["stock"], "R": ds})
    return evs
nc = {}
for yr, cal, lo, hi in (("2025", g["CAL25"], g["LO25"], g["HI25"]),
                        ("2026", g["CAL26"], g["LO26"], g["HI26"])):
    n_cand, n_ge = 0, 0
    for e in class_events(cal, lo, hi, SINGLE_NEWS):
        sym, R = e["symbol"], e["R"]
        spot, daily = STOCKS_E[sym]
        didx = {d["date"]: i for i, d in enumerate(daily)}
        if R not in didx:
            continue
        ri = didx[R]
        if ri == 0 or ri + 1 >= len(daily):
            continue
        ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
        nd = daily[ri + 1]["date"]
        if nd > hi or not spot.get(nd):
            continue
        n_cand += 1
        if abs(ret) >= 2.5:
            n_ge += 1
    nc[yr] = {"news_events_in_window": len(class_events(cal, lo, hi, SINGLE_NEWS)),
              "reaction_candidates": n_cand, "band_ge_2.5": n_ge}
out["news_candidates"] = nc
print(f"news-class candidates (counts only): {nc}")

# --- (iii-b) INV discarded populations (counts only) -----------------------
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
cond_inv1, g1, SYMBOLS = g["cond_inv1"], g["g1"], g["SYMBOLS"]
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}
def p2_all(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    return rows
disc = {}
for yr, days in (("2025", g["days25"]), ("2026", g["days26"])):
    pop = p2_all(days)
    long_ok = [r for r in pop if r["direction"] == "LONG"
               and (r["adr"] or 0) >= 3.0 and not wk(r["date"])
               and r["stock"] not in BASE_EXCL and r["stock"] not in V2_LAW]
    d = {"round_dist_all": dict(Counter(r["round"] for r in pop))}
    for gname, gate in (("below", cond_inv1), ("above", g1)):
        gp = [r for r in long_ok if gate(r["date"])]
        d[gname] = {
            "kept_round_le2_early": sum(1 for r in gp if r["round"] <= 2 and r["entry_time"] < "10:30"),
            "round_ge3_early": sum(1 for r in gp if r["round"] >= 3 and r["entry_time"] < "10:30"),
            "round_le2_late": sum(1 for r in gp if r["round"] <= 2 and r["entry_time"] >= "10:30"),
            "round_ge3_late": sum(1 for r in gp if r["round"] >= 3 and r["entry_time"] >= "10:30")}
    disc[yr] = d
out["inv_discarded_counts"] = disc
print(f"INV discarded populations (counts only): {json.dumps(disc)}")

json.dump(out, open(f"{WS}/v2_out/v2_cycle24_diag.json", "w"), indent=1)
print("wrote v2_out/v2_cycle24_diag.json")
