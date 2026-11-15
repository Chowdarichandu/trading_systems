#!/usr/bin/env python3
"""Phase-2 confidence gating for the Stock Book. Spec: phase2_confidence_stocks_SPEC.md
(frozen before scoring). Research only - reads gated stores, writes only its own outputs.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only."""
import csv, json, random, sys
from collections import defaultdict
from bisect import bisect_left, bisect_right

WS = "/home/hatch/workspace/trading"
CONTROL = {2025: 119813.44, 2026: 247178.79}
SEED = 42

def midrank_cdf(sorted_vals, v):
    """(count_less + 0.5*count_equal)/n against a sorted reference list."""
    lo = bisect_left(sorted_vals, v); hi = bisect_right(sorted_vals, v)
    return (lo + 0.5 * (hi - lo)) / len(sorted_vals)

# ---------- regime machinery (book's own, replicated exactly) ----------
def regime_from_closes(dates, closes):
    """regime_maps_from + REGIME-CLASSIFIER-1. Returns {date: (label, prev_close, ma50)}."""
    reg = {}
    for i, d in enumerate(dates):
        if i == 0: continue
        ma50 = sum(closes[i-50:i]) / 50 if i >= 50 else None
        reg[d] = {"prev_close": closes[i-1], "ma50": ma50}
    axis = sorted(d for d in reg if reg[d]["ma50"] is not None)
    out = {}
    for j, d in enumerate(axis):
        if j < 5: continue
        pc, m = reg[d]["prev_close"], reg[d]["ma50"]
        s = m - reg[axis[j-5]]["ma50"]
        lab = "UP" if (pc > m and s >= 0) else ("DOWN" if (pc <= m and s <= 0) else "FLAT")
        out[d] = (lab, pc, m)
    return out

def load_closes(path, date_slice=10):
    rows = list(csv.DictReader(open(path)))
    rows = [(r["date"][:date_slice], float(r["close"])) for r in rows]
    rows.sort()
    return [r[0] for r in rows], [r[1] for r in rows]

volrix = regime_from_closes(*load_closes(f"{WS}/volrix/nifty_daily_2019_2026.csv"))
prog   = regime_from_closes(*load_closes(f"{WS}/data/progressive/NIFTY/spot_daily.csv"))

# ---------- load November log first (validation target + application) ----------
nov = list(csv.DictReader(open(f"{WS}/stocks_sarvaritu_paper_log.csv")))
nov = [r for r in nov if "2026-11-02" <= r["date"] <= "2026-11-13"]

# validation (a): series labels vs the log's own regime values, dates volrix covers
val_a = []
for d in ("2026-11-02", "2026-11-03"):
    log_lab = {r["regime"] for r in nov if r["date"] == d}
    val_a.append((d, volrix.get(d, (None,))[0], sorted(log_lab)))
# validation (b): volrix vs progressive label agreement on Jan-Oct 2026 dates
common = [d for d in volrix if d.startswith("2026-") and d <= "2026-10-30" and d in prog]
agree = sum(1 for d in common if volrix[d][0] == prog[d][0])
val_b = (len(common), agree, round(100.0 * agree / max(1, len(common)), 2))

# ---------- volume store ----------
vol = defaultdict(dict)          # stock -> {date: volume}
vol_dates = defaultdict(list)    # stock -> sorted dates
for r in csv.DictReader(open(f"{WS}/stocks_daily_volume.csv")):
    vol[r["stock"]][r["date"]] = float(r["volume"])
for s in vol: vol_dates[s] = sorted(vol[s])

# master trading calendar = the volrix NIFTY daily series dates (2019-2026-11-03;
# covers every book leg date incl. special sessions; Jan-Oct S4 values are identical
# to the volume store's own predecessor dates - verified in-run by 100% coverage)
CAL = load_closes(f"{WS}/volrix/nifty_daily_2019_2026.csv")[0]
CAL_IDX = {d: i for i, d in enumerate(CAL)}

def prior_relvol(stock, date):
    """prior trading day volume / mean of 20 trading days ending on the prior day.
    The prior TRADING day (per the master calendar) must itself be present in the
    volume store - otherwise the factor is unavailable (None), never filled from
    an older date."""
    ci = CAL_IDX.get(date)
    if ci is None or ci == 0: return None
    prior = CAL[ci - 1]
    ds = vol_dates.get(stock, [])
    i = bisect_left(ds, prior)
    if i >= len(ds) or ds[i] != prior: return None   # prior day not in the store
    if i < 19: return None
    window = [vol[stock][d] for d in ds[i-19:i+1]]
    m = sum(window) / 20.0
    return vol[stock][prior] / m if m > 0 else None

def et_min(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)

# ---------- load book populations, Jan-Oct per year ----------
def load_book(yr):
    rows = list(csv.DictReader(open(f"{WS}/stocks_engine_adoptedC_book{yr}_trades.csv")))
    rows = [r for r in rows if f"{yr}-01-01" <= r["date"] <= f"{yr}-10-31"]
    for r in rows: r["net"] = float(r["net"])
    return rows

books, controls = {}, {}
for yr in (2025, 2026):
    rows = load_book(yr)
    tot = round(sum(r["net"] for r in rows), 2)
    if abs(tot - CONTROL[yr]) > 0.01:
        print(f"CONTROL FAIL {yr}: store total {tot} != adopted {CONTROL[yr]} - STOP")
        sys.exit(1)
    months = defaultdict(float)
    for r in rows: months[r["date"][:7]] += r["net"]
    books[yr] = rows
    controls[yr] = {
        "n": len(rows), "total": tot,
        "wr": round(100.0 * sum(1 for r in rows if r["net"] > 0) / len(rows), 2),
        "trade_days": len({r["date"] for r in rows}),
        "red_months": sorted(k for k, v in months.items() if v < 0),
        "months": {k: round(v, 2) for k, v in sorted(months.items())},
    }

# ---------- factor construction per year ----------
def build_factors(rows):
    """Returns list of dicts of raw factor values (None = unavailable) per leg."""
    by_ss = defaultdict(list)   # (date, stock) -> entry minutes list
    for r in rows: by_ss[(r["date"], r["stock"])].append(et_min(r["entry_time"]))
    out = []
    for r in rows:
        lab = volrix.get(r["date"])
        f = {"S1_raw": et_min(r["entry_time"]),
             "S2_lab": lab[0] if lab else None,
             "S3_raw": (abs(lab[1] / lab[2] - 1.0) if lab else None),
             "S4_raw": prior_relvol(r["stock"], r["date"]),
             "S5_raw": sum(1 for t in by_ss[(r["date"], r["stock"])] if t <= et_min(r["entry_time"]))}
        out.append(f)
    return out

def coverage(facs):
    cov = {}
    for k in ("S2_lab", "S3_raw", "S4_raw"):
        cov[k] = round(100.0 * sum(1 for f in facs if f[k] is not None) / len(facs), 2)
    cov["S1_raw"] = cov["S5_raw"] = 100.0
    return cov

def score_year(rows, facs):
    pools = {k: sorted(f[k] for f in facs if f[k] is not None) for k in ("S1_raw", "S3_raw", "S4_raw", "S5_raw")}
    scores = []
    for f in facs:
        parts = [1.0 - midrank_cdf(pools["S1_raw"], f["S1_raw"]),
                 (1.0 if (f["S2_lab"] == "UP") else 0.5 if f["S2_lab"] == "FLAT" else 0.0),  # dir applied below
                 midrank_cdf(pools["S3_raw"], f["S3_raw"]),
                 midrank_cdf(pools["S4_raw"], f["S4_raw"]),
                 midrank_cdf(pools["S5_raw"], f["S5_raw"])]
        scores.append(parts)
    # S2 needs the leg's direction: rebuild with dir
    for i, r in enumerate(rows):
        lab = facs[i]["S2_lab"]
        aligned = (r["dir"] == "LONG" and lab == "UP") or (r["dir"] == "SHORT" and lab == "DOWN")
        scores[i][1] = 1.0 if aligned else (0.5 if lab == "FLAT" else 0.0)
    comp = [sum(p) / len(p) for p in scores]
    return comp, pools

def metrics(rows, idxs, trade_days):
    sub = [rows[i] for i in idxs]
    tot = sum(r["net"] for r in sub)
    months = defaultdict(float)
    for r in sub: months[r["date"][:7]] += r["net"]
    h1 = sum(r["net"] for r in sub if r["date"][5:7] <= "05")
    h2 = tot - h1
    top3 = sum(sorted((r["net"] for r in sub), reverse=True)[:3])
    return {"kept": len(sub), "total": round(tot, 2),
            "wr": round(100.0 * sum(1 for r in sub if r["net"] > 0) / max(1, len(sub)), 2),
            "rs_per_trading_day": round(tot / trade_days, 2),
            "red_months": sorted(k for k, v in months.items() if v < 0),
            "months": {k: round(v, 2) for k, v in sorted(months.items())},
            "h1_jan_may": round(h1, 2), "h2_jun_oct": round(h2, 2),
            "ex_top3": round(tot - top3, 2)}

results = {"control": controls, "validation": {"nov_log_labels": val_a, "volrix_vs_progressive_janoct2026": val_b},
           "basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only, real Rs0"}
grid_levels = {"T70": 0.70, "T60": 0.60, "T50": 0.50}
cuts_2026 = {}
rng = random.Random(SEED)

for yr in (2025, 2026):
    rows = books[yr]; facs = build_factors(rows)
    cov = coverage(facs)
    comp, pools = score_year(rows, facs)
    if yr == 2026: pools_2026 = pools
    order = sorted(range(len(rows)), key=lambda i: -comp[i])
    yr_res = {"coverage_pct": cov, "full": metrics(rows, list(range(len(rows))), controls[yr]["trade_days"]), "levels": {}}
    for name, frac in grid_levels.items():
        k = round(frac * len(rows))
        cut = comp[order[k - 1]]
        kept = [i for i in range(len(rows)) if comp[i] >= cut]
        if yr == 2026: cuts_2026[name] = cut
        m = metrics(rows, kept, controls[yr]["trade_days"])
        draws = []
        for _ in range(200):
            draws.append(sum(rows[i]["net"] for i in rng.sample(range(len(rows)), len(kept))))
        pct = round(100.0 * sum(1 for d in draws if d < m["total"]) / len(draws), 1)
        legs = {"wr_above_full": m["wr"] > controls[yr]["wr"],
                "total_ge_60pct": m["total"] >= 0.60 * controls[yr]["total"],
                "no_new_red_month": set(m["red_months"]) <= set(controls[yr]["red_months"]),
                "halves_positive": m["h1_jan_may"] > 0 and m["h2_jun_oct"] > 0,
                "ex_top3_positive": m["ex_top3"] > 0,
                "placebo_ge_95": pct >= 95.0}
        m.update({"cut_score": round(cut, 4), "placebo_pct": pct, "legs": legs,
                  "PASS": all(legs.values()),
                  "failing": [k2 for k2, v in legs.items() if not v]})
        yr_res["levels"][name] = m
    results[f"year_{yr}"] = yr_res

# ---------- November application (descriptive) ----------
# S3 raw for November dates from the logger's own progressive NIFTY store
def prog_strength(date):
    e = prog.get(date)
    return abs(e[1] / e[2] - 1.0) if e else None

by_ss_nov = defaultdict(list)
for r in nov: by_ss_nov[(r["date"], r["stock"])].append(et_min(r["entry_time"]))
nov_rows = []
for r in nov:
    s4 = prior_relvol(r["stock"], r["date"])
    s3 = prog_strength(r["date"])
    missing = []
    if s4 is None: missing.append("S4_prior_day_relative_volume (volume store ends 2026-10-30)")
    if s3 is None: missing.append("S3_trend_strength")
    if missing:
        nov_rows.append({"date": r["date"], "comp": r["comp"], "stock": r["stock"], "dir": r["dir"],
                         "entry_time": r["entry_time"], "net": float(r["net"]), "score": None,
                         "missing": missing})
        continue
    lab = r["regime"]
    aligned = (r["dir"] == "LONG" and lab == "UP") or (r["dir"] == "SHORT" and lab == "DOWN")
    parts = [1.0 - midrank_cdf(pools_2026["S1_raw"], et_min(r["entry_time"])),
             1.0 if aligned else (0.5 if lab == "FLAT" else 0.0),
             midrank_cdf(pools_2026["S3_raw"], s3),
             midrank_cdf(pools_2026["S4_raw"], s4),
             midrank_cdf(pools_2026["S5_raw"], sum(1 for t in by_ss_nov[(r["date"], r["stock"])] if t <= et_min(r["entry_time"])))]
    nov_rows.append({"date": r["date"], "comp": r["comp"], "stock": r["stock"], "dir": r["dir"],
                     "entry_time": r["entry_time"], "net": float(r["net"]),
                     "score": round(sum(parts) / 5.0, 4), "missing": []})

nov_actual = round(sum(r["net"] for r in nov_rows), 2)
nov_res = {"actual_total": nov_actual, "levels": {}}
for name in grid_levels:
    cut = cuts_2026[name]
    kept = [r for r in nov_rows if r["score"] is not None and r["score"] >= cut]
    idled = [r for r in nov_rows if r["score"] is not None and r["score"] < cut]
    unsc = [r for r in nov_rows if r["score"] is None]
    days = {}
    for d in sorted({r["date"] for r in nov_rows}):
        dr = [r for r in nov_rows if r["date"] == d]
        days[d] = {"actual": round(sum(r["net"] for r in dr), 2),
                   "kept": round(sum(r["net"] for r in dr if r["score"] is not None and r["score"] >= cut), 2),
                   "idled": round(sum(r["net"] for r in dr if r["score"] is not None and r["score"] < cut), 2),
                   "unscored": round(sum(r["net"] for r in dr if r["score"] is None), 2),
                   "n_kept": sum(1 for r in dr if r["score"] is not None and r["score"] >= cut),
                   "n_idled": sum(1 for r in dr if r["score"] is not None and r["score"] < cut),
                   "n_unscored": sum(1 for r in dr if r["score"] is None)}
    nov_res["levels"][name] = {
        "cut_score": round(cut, 4),
        "filtered_total_unscored_kept": round(sum(r["net"] for r in kept) + sum(r["net"] for r in unsc), 2),
        "filtered_total_unscored_excluded": round(sum(r["net"] for r in kept), 2),
        "n_kept": len(kept), "n_idled": len(idled), "n_unscored": len(unsc), "days": days}
results["november"] = nov_res
results["november_legs"] = nov_rows
results["cuts_2026"] = {k: round(v, 4) for k, v in cuts_2026.items()}

json.dump(results, open(f"{WS}/phase2_confidence_stocks_results.json", "w"), indent=1)
print(json.dumps({k: results[k] for k in ("control", "validation")}, indent=1))
for yr in (2025, 2026):
    y = results[f"year_{yr}"]
    print(yr, "coverage", y["coverage_pct"], "full", y["full"]["total"], y["full"]["wr"])
    for name, m in y["levels"].items():
        print(" ", name, "kept", m["kept"], "total", m["total"], "WR", m["wr"], "pct", m["placebo_pct"],
              "PASS" if m["PASS"] else "FAIL", m["failing"])
print("NOV actual", nov_actual, "scored legs:", sum(1 for r in nov_rows if r["score"] is not None),
      "unscored:", sum(1 for r in nov_rows if r["score"] is None))
for name, lv in nov_res["levels"].items():
    print(" ", name, "cut", lv["cut_score"], "unscored-kept total", lv["filtered_total_unscored_kept"],
          "unscored-excluded total", lv["filtered_total_unscored_excluded"],
          "kept/idled/unscored", lv["n_kept"], lv["n_idled"], lv["n_unscored"])
