#!/usr/bin/env python3
"""Phase-2 tuning, Bank Nifty — selectivity/confidence gating on TUNED STACK v2.
Spec: phase2_tuning_bank_SPEC.md (frozen before scoring). Research only."""
import csv, json, random, math
from collections import defaultdict, Counter

D = "/home/hatch/workspace/trading/"
MEDIAN_PREM = 692.50
TOTAL_DAYS = 205  # Jan-Oct 2026 trading days (bank_900 calendar)

def fnum(x):
    return float(x) if x not in ("", None) else 0.0

# ---------- load + join ----------
feat = {}
for r in csv.DictReader(open(D + "solid60_programme_2026-11-13_bank_A_stack_features.csv")):
    feat[(r["date"], r["entry_time"], float(r["entry_premium"]))] = r
legs = []
for r in csv.DictReader(open(D + "november_books_fix_anatomy_legs.csv")):
    if r["book"] != "BANK_STACK":
        continue
    k = (r["date"], r["entry_time"], float(r["entry_premium"]))
    fr = feat[k]
    legs.append({
        "date": r["date"], "side": r["side"], "family": r["family"], "rep": r["rep"],
        "entry_time": r["entry_time"], "premium": float(r["entry_premium"]),
        "gap_pct": float(r["gap_pct"]), "net": float(r["net"]),
        "agree": int(fr["agree"]), "second": int(fr["second"]), "tod": fr["tod"],
    })
assert len(legs) == 111, len(legs)

# ---------- metrics ----------
def day_map(ls):
    dm = defaultdict(float)
    for l in ls: dm[l["date"]] += l["net"]
    return dm

def metrics(ls):
    total = round(sum(l["net"] for l in ls), 2)
    dm = day_map(ls)
    wins = sum(1 for l in ls if l["net"] > 0)
    months = {}
    for m in sorted({l["date"][:7] for l in ls}):
        ml = [l for l in ls if l["date"][:7] == m]
        months[m] = round(sum(l["net"] for l in ml), 2)
    h1 = round(sum(l["net"] for l in ls if l["date"][:7] in
                   ("2026-01","2026-02","2026-03","2026-04","2026-05")), 2)
    h2 = round(total - h1, 2)
    srt = sorted(ls, key=lambda l: -l["net"])
    extop3 = round(total - sum(l["net"] for l in srt[:3]), 2) if len(ls) > 3 else None
    green = sum(1 for v in dm.values() if v > 0); red = sum(1 for v in dm.values() if v < 0)
    return {"legs": len(ls), "total": total, "trade_days": len(dm),
            "per_trade_day": round(total / len(dm), 2) if dm else 0.0,
            "win_rate_pct": round(100 * wins / len(ls), 1) if ls else 0.0,
            "green_days": green, "red_days": red, "no_trade_days": TOTAL_DAYS - len(dm),
            "months": months, "red_months": [m for m, v in months.items() if v < 0],
            "halves": {"H1": h1, "H2": h2}, "ex_top3_total": extop3}

# ---------- CONTROL ----------
ctrl = metrics(legs)
CTRL_EXPECT = {"legs": 111, "total": 127351.50, "trade_days": 89, "per_trade_day": 1430.92,
               "win_rate_pct": 59.5, "green_days": 60, "red_days": 29, "no_trade_days": 116,
               "H1": 83082.00, "H2": 44269.50, "ex_top3": 100528.50}
ctrl_ok = (ctrl["legs"] == 111 and ctrl["total"] == 127351.50 and ctrl["trade_days"] == 89
           and ctrl["per_trade_day"] == 1430.92 and ctrl["win_rate_pct"] == 59.5
           and ctrl["green_days"] == 60 and ctrl["red_days"] == 29
           and ctrl["no_trade_days"] == 116 and ctrl["halves"]["H1"] == 83082.00
           and ctrl["halves"]["H2"] == 44269.50 and ctrl["ex_top3_total"] == 100528.50
           and ctrl["red_months"] == [])
# independent re-sum (second code path: raw column sum straight off the CSVs)
raw_sum = round(sum(float(r["x1_net"]) for r in
                    csv.DictReader(open(D + "solid60_programme_2026-11-13_bank_A_stack_features.csv"))), 2)
ctrl_ok = ctrl_ok and raw_sum == 127351.50
print("CONTROL:", json.dumps(ctrl), "| re-sum:", raw_sum, "| OK:", ctrl_ok)
if not ctrl_ok:
    raise SystemExit("CONTROL FAILED — stopping per spec, no scoring performed.")

# ---------- F6 anchor resolution ----------
v21 = list(csv.DictReader(open(D + "bank_engine_r6_v21_trades.csv")))
def t2m(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)
f6_resolved = f6_unresolved = 0
for l in legs:
    l["f6"] = 0.0
    if l["second"] != 1:
        continue
    anchor_net = None
    if l["family"] == "EVE06_REENTRY":
        prior = [x for x in legs if x["date"] == l["date"] and t2m(x["entry_time"]) < t2m(l["entry_time"])]
        if prior:
            anchor_net = sorted(prior, key=lambda x: t2m(x["entry_time"]))[-1]["net"]
    elif l["family"] == "NS1_second":
        cand = [x for x in v21 if x["date"] == l["date"] and x["family"] == "BASE"
                and t2m(x["exit_time"]) <= t2m(l["entry_time"])]
        if cand:
            anchor_net = float(sorted(cand, key=lambda x: t2m(x["exit_time"]))[-1]["net_inr"])
    if anchor_net is None:
        f6_unresolved += 1
    else:
        f6_resolved += 1
        l["f6"] = 0.5 if anchor_net > 0 else -0.5
print(f"F6 anchor resolution: {f6_resolved} resolved, {f6_unresolved} unresolved of "
      f"{sum(1 for l in legs if l['second']==1)} second legs")

# ---------- composite score (weights per frozen spec) ----------
def score_leg(l):
    f1 = 1.0 if l["agree"] >= 2 else (0.5 if l["agree"] == 1 else 0.0)
    r = l["premium"] / MEDIAN_PREM
    f2 = 1.0 if r < 0.75 else (0.5 if r < 1.0 else (0.0 if r < 1.45 else -0.5))
    f3 = {"early": 0.5, "mid": 0.0, "late": -0.5}[l["tod"]]
    aligned = (l["side"] == "CE" and l["gap_pct"] > 0) or (l["side"] == "PE" and l["gap_pct"] < 0)
    against = (l["side"] == "CE" and l["gap_pct"] < 0) or (l["side"] == "PE" and l["gap_pct"] > 0)
    ag = abs(l["gap_pct"])
    f4 = 0.0 if ag < 0.05 else (0.5 if (aligned and ag >= 0.30) else
                                (0.25 if aligned else -0.5 if against else 0.0))
    f5 = 0.5 if l["second"] == 1 else 0.0
    return f1 + f2 + f3 + f4 + f5 + l["f6"]
for l in legs:
    l["score"] = score_leg(l)

# ---------- B-FIX-1 kept set (for overlap) ----------
bfix1_kept = [l for l in legs if not (l["side"] == "PE" and l["gap_pct"] < 0
                                      and 500 <= l["premium"] <= 800)]
bfix1_keys = {(l["date"], l["entry_time"], l["premium"]) for l in bfix1_kept}
print("B-FIX-1 kept:", len(bfix1_kept))

# ---------- thresholds + placebo + pass bar ----------
random.seed(42)
ranked = sorted(legs, key=lambda l: -l["score"])
results = {"control": ctrl, "control_ok": ctrl_ok,
           "f6": {"resolved": f6_resolved, "unresolved": f6_unresolved},
           "thresholds": {}}
for name, frac in (("T70", 0.70), ("T60", 0.60), ("T50", 0.50)):
    k = math.ceil(frac * len(legs))
    cut_score = ranked[k - 1]["score"]
    kept = [l for l in legs if l["score"] >= cut_score]
    m = metrics(kept)
    draws = []
    for _ in range(200):
        draws.append(round(sum(x["net"] for x in random.sample(legs, len(kept))), 2))
    draws_sorted = sorted(draws)
    p95 = draws_sorted[int(0.95 * len(draws)) - 1]
    pctile = round(100 * sum(1 for d in draws if d < m["total"]) / len(draws), 1)
    kept_keys = {(l["date"], l["entry_time"], l["premium"]) for l in kept}
    overlap = {"bfix1_kept": len(bfix1_kept),
               "intersection": len(kept_keys & bfix1_keys),
               "share_of_kept_also_bfix1_kept_pct": round(100 * len(kept_keys & bfix1_keys) / len(kept_keys), 1),
               "jaccard_pct": round(100 * len(kept_keys & bfix1_keys) /
                                    len(kept_keys | bfix1_keys), 1)}
    checks = {"wr_ge_60": m["win_rate_pct"] >= 60.0,
              "per_td_ge_900": m["per_trade_day"] >= 900,
              "total_ge_60pct": m["total"] >= 0.60 * 127351.50,
              "halves_positive": m["halves"]["H1"] > 0 and m["halves"]["H2"] > 0,
              "ex_top3_positive": (m["ex_top3_total"] or 0) > 0,
              "placebo_beats_95pct": m["total"] > p95,
              "no_red_month": m["red_months"] == []}
    results["thresholds"][name] = {"target_keep": k, "cut_score": cut_score, "metrics": m,
                                   "placebo": {"draws": 200, "p95_total": p95,
                                               "kept_percentile": pctile},
                                   "overlap_bfix1": overlap, "checks": checks,
                                   "verdict": "PASS" if all(checks.values()) else "FAIL",
                                   "failing": [c for c, v in checks.items() if not v]}
    print(name, "kept", m["legs"], "cut", cut_score, "total", m["total"], "WR", m["win_rate_pct"],
          "perTD", m["per_trade_day"], "placebo pctile", pctile, "p95", p95,
          "verdict", results["thresholds"][name]["verdict"], results["thresholds"][name]["failing"])

# ---------- November counterfactual ----------
regime_days = {}
for r in csv.DictReader(open(D + "november_regime_days_bank.csv")):
    regime_days[r["date"]] = r
print("regime_days cols:", list(next(iter(regime_days.values())).keys()))
gapkey = None
for cand in ("gap_pct", "gap", "overnight_gap_pct", "gap_pct_overnight"):
    if cand in next(iter(regime_days.values())):
        gapkey = cand
print("gap key:", gapkey, {d: regime_days[d].get(gapkey) for d in
                           ("2026-11-04", "2026-11-09", "2026-11-12", "2026-11-13") if d in regime_days})
# tod mapping inferred from the Jan-Oct store itself
tod_by_time = {}
for l in sorted(legs, key=lambda x: t2m(x["entry_time"])):
    tod_by_time.setdefault(l["entry_time"], l["tod"])
def tod_of(t):
    if t in tod_by_time: return tod_by_time[t]
    mt = t2m(t)
    known = sorted(((t2m(k), v) for k, v in tod_by_time.items()))
    prev = [v for kt, v in known if kt <= mt]
    return prev[-1] if prev else known[0][1]

nov_legs = []
for r in csv.DictReader(open(D + "november_shadow_stack_bank_log.csv")):
    if not r.get("entry_premium"):
        continue
    d = r["date"]
    gap = float(regime_days[d][gapkey]) if gapkey and d in regime_days else None
    nl = {"date": d, "side": r["direction"], "family": r["family"], "rep": r["rep"],
          "entry_time": r["entry_time"], "premium": float(r["entry_premium"]),
          "gap_pct": gap, "net": float(r["net_inr"]), "agree": 0, "second": 0,
          "tod": tod_of(r["entry_time"]), "f6": 0.0}
    nl["score"] = score_leg(nl)  # F1 neutral 0 — agree not carried in Nov shadow log (spec)
    nov_legs.append(nl)
print("November legs:", [(n["date"], n["rep"], n["premium"], n["gap_pct"], n["tod"], n["score"], n["net"]) for n in nov_legs])
nov_actual = round(sum(n["net"] for n in nov_legs), 2)
nov_out = {"actual_total": nov_actual, "legs": [{k: n[k] for k in
           ("date", "rep", "side", "entry_time", "premium", "gap_pct", "tod", "score", "net")}
           for n in nov_legs], "by_threshold": {}}
for name in ("T70", "T60", "T50"):
    cut = results["thresholds"][name]["cut_score"]
    kept = [n for n in nov_legs if n["score"] >= cut]
    nov_out["by_threshold"][name] = {"cut_score": cut, "kept_legs": len(kept),
                                     "kept_dates": [n["date"] for n in kept],
                                     "total": round(sum(n["net"] for n in kept), 2)}
    print("NOV", name, "cut", cut, "->", nov_out["by_threshold"][name])
results["november"] = nov_out

with open(D + "phase2_tuning_bank_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE phase2_tuning_bank_results.json")
