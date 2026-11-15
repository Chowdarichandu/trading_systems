#!/usr/bin/env python3
"""FLOOR SESSION shared library — validated in stocks_engine_floor_baseline.py:
dump re-sums reproduce state totals to the paisa; REGIME-CLASSIFIER-1 labels
reproduce both books' published cells exactly; N4 move recomputation matches
the recorded 2026 standalone moves 56/56 and the C16-2026 N4 join 34/34.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
FH = f"{WS}/data/full_hist"

def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]

def scorecard(rows, year):
    tot = round(sum(t["net"] for t in rows), 2)
    months = defaultdict(float)
    for t in rows: months[t["date"][:7]] += t["net"]
    months = {k: round(v, 2) for k, v in sorted(months.items())}
    jo = [t for t in rows if t["date"] <= f"{year}-10-31"]
    jo_tot = round(sum(t["net"] for t in jo), 2)
    h1 = round(sum(t["net"] for t in jo if t["date"] <= f"{year}-05-31"), 2)
    by_stock = defaultdict(float)
    for t in rows: by_stock[t["stock"]] += t["net"]
    top3 = sorted(by_stock.items(), key=lambda kv: -kv[1])[:3]
    by_comp = defaultdict(float)
    for t in rows: by_comp[t["comp"]] += t["net"]
    return {"year": year, "total": tot, "trades": len(rows),
            "jan_oct_total": jo_tot, "jan_oct_trades": len(jo),
            "jan_oct_H1_jan_may": h1, "jan_oct_H2_jun_oct": round(jo_tot - h1, 2),
            "months": months,
            "ex_top3_stocks": round(tot - sum(v for _, v in top3), 2),
            "top3_stocks": [(s, round(v, 2)) for s, v in top3],
            "by_comp": {k: round(v, 2) for k, v in sorted(by_comp.items())},
            "wins": sum(1 for t in rows if t["net"] > 0)}

# --- REGIME-CLASSIFIER-1 (frozen): UP = prior close > 50DMA and 5-day 50DMA
# slope >= 0; DOWN = prior close <= 50DMA and slope <= 0; else FLAT. --------
def _nifty_labels():
    daily = []
    with open(f"{FH}/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "close": float(r["close"])})
    have = {d["date"] for d in daily}
    with open(f"{WS}/data/sarvaritu_fwd/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            d = r["date"][:10]
            if d not in have:
                daily.append({"date": d, "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    closes = [d["close"] for d in daily]
    def ma50(i):
        return sum(closes[i - 50:i]) / 50 if i >= 50 else None
    labels = {}
    for i, d in enumerate(daily):
        m, m5 = ma50(i), ma50(i - 5)
        if m is None or m5 is None: continue
        pc, slope = closes[i - 1], m - m5
        labels[d["date"]] = "UP" if (pc > m and slope >= 0) else ("DOWN" if (pc <= m and slope <= 0) else "FLAT")
    return labels

LABELS = _nifty_labels()

def cells(rows):
    out = defaultdict(float); missing = []
    for t in rows:
        lab = LABELS.get(t["date"])
        if lab is None: missing.append(t["date"]); continue
        out[lab] += t["net"]
    return {k: round(v, 2) for k, v in sorted(out.items())}, missing

# --- N4-V3 move by 09:30: close of the 09:25 bar / prior daily close - 1 ---
_spot_cache, _daily_cache = {}, {}
def _stock_data(sym):
    if sym not in _spot_cache:
        spot = {}
        with open(f"{FH}/{sym}/spot_5m.csv") as f:
            for r in csv.DictReader(f):
                spot.setdefault(r["timestamp"][:10], {})[r["timestamp"][11:16]] = float(r["close"])
        dl = []
        with open(f"{FH}/{sym}/spot_daily.csv") as f:
            for r in csv.DictReader(f):
                dl.append((r["date"][:10], float(r["close"])))
        dl.sort()
        _spot_cache[sym] = spot; _daily_cache[sym] = dl
    return _spot_cache[sym], _daily_cache[sym]

def n4_move(sym, day):
    spot, dl = _stock_data(sym)
    dates = [d for d, _ in dl]
    if day not in spot or day not in dates: return None
    i = dates.index(day)
    if i == 0: return None
    b = spot[day].get("09:25")
    if b is None: return None
    return round((b / dl[i - 1][1] - 1) * 100, 2)

def gate_eval(base, var, base_cells, var_cells, placebos_combined, timing_violations):
    """base/var: {2025: scorecard, 2026: scorecard}; placebos_combined: list of
    combined totals for the pre-registered placebos. Returns (verdict, legs)."""
    legs = {}
    b_comb = round(base[2025]["total"] + base[2026]["total"], 2)
    v_comb = round(var[2025]["total"] + var[2026]["total"], 2)
    legs["a_combined_rises"] = v_comb > b_comb
    legs["b_2025_no_fall"] = var[2025]["total"] >= base[2025]["total"] and \
                             var[2025]["jan_oct_total"] >= base[2025]["jan_oct_total"]
    legs["c_2026_no_fall"] = var[2026]["total"] >= base[2026]["total"]
    legs["d_cells_positive"] = all(v > 0 for yr in (2025, 2026) for v in var_cells[yr].values()) and \
                               len(var_cells[2025]) == 3 and len(var_cells[2026]) == 3
    legs["e_extop3"] = var[2025]["ex_top3_stocks"] >= 0 and var[2026]["ex_top3_stocks"] >= 0 and \
        round(var[2025]["ex_top3_stocks"] + var[2026]["ex_top3_stocks"], 2) >= \
        round(base[2025]["ex_top3_stocks"] + base[2026]["ex_top3_stocks"], 2)
    flip = []
    for yr in (2025, 2026):
        for m, v in base[yr]["months"].items():
            if v > 0 and var[yr]["months"].get(m, 0.0) <= 0: flip.append(f"{m}:{v}->{var[yr]['months'].get(m, 0.0)}")
    legs["f_no_green_month_flips"] = not flip
    legs["flip_detail"] = flip
    hflip = []
    for yr in (2025, 2026):
        for hk in ("jan_oct_H1_jan_may", "jan_oct_H2_jun_oct"):
            if base[yr][hk] > 0 and var[yr][hk] <= 0: hflip.append(f"{yr}:{hk}")
    legs["g_no_half_flips"] = not hflip
    legs["h_beats_placebos"] = all(v_comb > p for p in placebos_combined)
    legs["i_timing_clean"] = timing_violations == 0
    verdict = all(v for k, v in legs.items() if isinstance(v, bool))
    return verdict, legs, {"base_combined": b_comb, "variant_combined": v_comb}
