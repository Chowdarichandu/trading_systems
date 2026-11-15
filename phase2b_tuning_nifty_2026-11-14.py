#!/usr/bin/env python3
"""Phase-2B tuning — Nifty FAMILY-WISE confidence (selectivity) on TUNED v1.
Implements phase2b_tuning_nifty_SPEC.md (frozen 2026-11-14 09:02 IST) exactly.
Research only: reads the gated store, writes results JSON. Changes nothing else.
"""
import csv, json, math, random, statistics
from collections import defaultdict
from datetime import date as ddate

TR = "/home/hatch/workspace/trading"
MEDIAN_PREM = 213.025  # frozen constant from the gated store (verified in-run)

# ---------- load store ----------
rows = list(csv.DictReader(open(f"{TR}/november_books_fix_repair_nifty_legs.csv")))
legs = []
for i, r in enumerate(rows):
    legs.append({
        "idx": i,
        "date": r["date"], "side": r["side"], "family": r["family"],
        "rep": r["rep"], "entry_time": r["entry_time"], "bucket": r["bucket"],
        "prem": float(r["entry_premium"]), "gap": float(r["gap_pct"]),
        "net": float(r["net_inr"]), "stood_down": r["stood_down"] == "YES",
    })
assert len(legs) == 74, len(legs)
assert not any(l["family"] == "B" and l["side"] == "PE" for l in legs), "B-PE in v1 store"

# ---------- Step 0: control (must reproduce phase 2 exactly) ----------
total = round(sum(l["net"] for l in legs), 2)
wins = sum(1 for l in legs if l["net"] > 0)
tdays = sorted(set(l["date"] for l in legs))
months = defaultdict(float)
for l in legs:
    months[l["date"][:7]] += l["net"]
months = {k: round(v, 2) for k, v in sorted(months.items())}
control = {
    "legs": len(legs), "total": total, "wins": wins,
    "wr_pct": round(100 * wins / len(legs), 1),
    "trade_days": len(tdays), "per_trade_day": round(total / len(tdays), 2),
    "months": months, "march": months["2026-03"],
}
assert control["total"] == 103050.25, control
assert control["wr_pct"] == 51.4 and control["trade_days"] == 66
assert control["per_trade_day"] == 1561.37 and control["march"] == -1216.50
assert [m for m, v in months.items() if v < 0] == ["2026-03"]
nfix_idled = [l for l in legs if l["stood_down"]]
assert len(nfix_idled) == 8 and round(sum(l["net"] for l in nfix_idled), 2) == -14119.75
assert round(total - sum(l["net"] for l in nfix_idled), 2) == 117170.00
med = statistics.median([l["prem"] for l in legs])
assert abs(med - MEDIAN_PREM) < 0.01, med
print("CONTROL OK:", json.dumps(control))

# ---------- calendar (205 trading days Jan-Oct 2026) ----------
cal = [r["date"] for r in csv.DictReader(open(f"{TR}/volrix/nifty_daily_2019_2026.csv"))
       if "2026-01-01" <= r["date"] <= "2026-10-31"]
assert len(cal) == 205, len(cal)

# ---------- raw factors: phase-2 formulas unchanged ----------
def raw_factors(side, family, bucket, prem, gap, date_s):
    f_time = {"pre-11:00": 1.00, "11:00-12:30": 0.60, "post-12:30": 0.30}[bucket]
    if abs(gap) < 0.10:
        f_gap = 0.50
    elif (side == "CE" and gap > 0) or (side == "PE" and gap < 0):
        f_gap = 1.00
    else:
        f_gap = 0.20
    r = prem / MEDIAN_PREM
    f_prem = 1 - 0.7 * min(1.0, abs(math.log(r)) / math.log(4))
    tue = ddate.fromisoformat(date_s).weekday() == 1
    f_exp = 0.70 if (tue and family != "C") else 1.00
    return {"f_time": f_time, "f_gap": f_gap, "f_prem": round(f_prem, 4), "f_exp": f_exp}

for l in legs:
    l.update(raw_factors(l["side"], l["family"], l["bucket"], l["prem"], l["gap"], l["date"]))

# ---------- Step 1: family split ----------
FAMS = ["A", "B", "C"]
fam_legs = {f: [l for l in legs if l["family"] == f] for f in FAMS}
fam_info = {}
for f in FAMS:
    sub = fam_legs[f]
    fam_info[f] = {
        "legs": len(sub), "reps": sorted(set(l["rep"] for l in sub)),
        "net": round(sum(l["net"] for l in sub), 2),
        "gated": len(sub) >= 8,
    }
    print("FAMILY", f, json.dumps(fam_info[f]))
assert all(fam_info[f]["gated"] for f in FAMS), "spec froze all three gated (>=8 legs)"

# ---------- Step 2: within-family percentile score ----------
FACTORS = ["f_time", "f_gap", "f_prem", "f_exp"]
def midrank_pct(value, ref_values):
    less = sum(1 for v in ref_values if v < value)
    equal = sum(1 for v in ref_values if v == value)
    return (less + 0.5 * equal) / len(ref_values)

for f in FAMS:
    sub = fam_legs[f]
    for l in sub:
        pcts = {fac: round(midrank_pct(l[fac], [o[fac] for o in sub]), 4) for fac in FACTORS}
        l["pcts"] = pcts
        l["wf_score"] = round(sum(pcts.values()) / 4, 4)

# diagnostics: correlation of wf_score with net (pooled + per family)
def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return round(cov / math.sqrt(vx * vy), 3) if vx > 0 and vy > 0 else None

diag = {
    "pooled_corr_wfscore_net": pearson([l["wf_score"] for l in legs], [l["net"] for l in legs]),
    "per_family_corr": {f: pearson([l["wf_score"] for l in fam_legs[f]],
                                   [l["net"] for l in fam_legs[f]]) for f in FAMS},
}
print("DIAG:", json.dumps(diag))

# ---------- subset statistics (same definitions as phase 2) ----------
def subset_stats(sub):
    tot = round(sum(l["net"] for l in sub), 2)
    tds = sorted(set(l["date"] for l in sub))
    day_net = defaultdict(float)
    for l in sub:
        day_net[l["date"]] += l["net"]
    green = sum(1 for d in tds if day_net[d] > 0)
    red = sum(1 for d in tds if day_net[d] < 0)
    mo = defaultdict(float)
    for l in sub:
        mo[l["date"][:7]] += l["net"]
    mo = {k: round(v, 2) for k, v in sorted(mo.items())}
    h1 = round(sum(l["net"] for l in sub if l["date"] < "2026-06-01"), 2)
    h2 = round(sum(l["net"] for l in sub if l["date"] >= "2026-06-01"), 2)
    top3 = sorted((l["net"] for l in sub), reverse=True)[:3]
    return {
        "legs": len(sub), "total": tot,
        "trade_days": len(tds),
        "wr_pct": round(100 * sum(1 for l in sub if l["net"] > 0) / len(sub), 1) if sub else 0.0,
        "per_trade_day": round(tot / len(tds), 2) if tds else 0.0,
        "green_days": green, "red_days": red, "no_trade_days": 205 - len(tds),
        "months": mo, "red_months": [k for k, v in mo.items() if v < 0],
        "h1": h1, "h2": h2,
        "ex_top3": round(tot - sum(top3), 2), "top3": top3,
    }

# ---------- Steps 3+4: per-family keep grid + stratified placebo ----------
def round_half_up(x):
    return math.floor(x + 0.5)

ranked_fam = {f: sorted(fam_legs[f], key=lambda l: (-l["wf_score"], l["date"], l["entry_time"]))
              for f in FAMS}
nfix_kept_idx = {l["idx"] for l in legs if not l["stood_down"]}
rng = random.Random(20261114)
results = {"control": control, "median_premium": MEDIAN_PREM,
           "families": fam_info, "diagnostics": diag, "levels": {}}
for name, frac in (("F70", 0.70), ("F60", 0.60), ("F50", 0.50)):
    kept, cutoffs, per_fam = [], {}, {}
    for f in FAMS:
        k_f = round_half_up(frac * len(fam_legs[f]))
        kf = ranked_fam[f][:k_f]
        cutoffs[f] = kf[-1]["wf_score"]
        kept.extend(kf)
        per_fam[f] = {
            "family_legs": len(fam_legs[f]), "kept": k_f, "cutoff": cutoffs[f],
            "kept_net": round(sum(l["net"] for l in kf), 2),
            "idled_net": round(sum(l["net"] for l in ranked_fam[f][k_f:]), 2),
            "kept_wr_pct": round(100 * sum(1 for l in kf if l["net"] > 0) / k_f, 1),
            "kept_avg_net": round(sum(l["net"] for l in kf) / k_f, 2),
            "idled_avg_net": round(sum(l["net"] for l in ranked_fam[f][k_f:]) /
                                   max(1, len(fam_legs[f]) - k_f), 2),
        }
    st = subset_stats(kept)
    # placebo: thin EACH family by the same proportion (within-family random)
    below = 0
    for _ in range(200):
        draw_total = 0.0
        for f in FAMS:
            k_f = round_half_up(frac * len(fam_legs[f]))
            draw_total += sum(l["net"] for l in rng.sample(fam_legs[f], k_f))
        if draw_total < st["total"]:
            below += 1
    pct = below / 200
    kept_idx = {l["idx"] for l in kept}
    overlap = {
        "kept_and_nfix_kept": len(kept_idx & nfix_kept_idx),
        "kept_but_nfix_idled": sum(1 for l in kept if l["stood_down"]),
        "idled_but_nfix_kept": len(nfix_kept_idx - kept_idx),
    }
    checks = {
        "wr>=60": st["wr_pct"] >= 60.0,
        "per_td>=900": st["per_trade_day"] >= 900,
        "total>=60%": st["total"] >= 61830.15,
        "halves>0": st["h1"] > 0 and st["h2"] > 0,
        "ex_top3>0": st["ex_top3"] > 0,
        "placebo>=0.95": pct >= 0.95,
        "no_new_red_month": set(st["red_months"]) <= {"2026-03"},
    }
    results["levels"][name] = {
        "frac": frac, "per_family": per_fam, "cutoffs": cutoffs,
        "stats": st, "placebo_percentile": pct, "nfix_overlap": overlap,
        "checks": checks, "verdict": "PASS" if all(checks.values()) else "FAIL",
        "failing": [c for c, ok in checks.items() if not ok],
        "kept_legs": [{kk: l[kk] for kk in ("date", "side", "family", "rep", "entry_time",
                                             "prem", "gap", "net", "wf_score")} for l in kept],
    }
    print(name, json.dumps(st), "placebo=", pct, "verdict=", results["levels"][name]["verdict"],
          "failing=", results["levels"][name]["failing"], "per_fam=", json.dumps(per_fam))

# ---------- Step 6: November counterfactual (Nov 3 leg, family C) ----------
nov_raw = raw_factors("CE", "C", "pre-11:00", 75.90, 0.6034, "2026-11-03")
c_ref = fam_legs["C"]
nov_pcts = {fac: round(midrank_pct(nov_raw[fac], [o[fac] for o in c_ref]), 4) for fac in FACTORS}
nov_score = round(sum(nov_pcts.values()) / 4, 4)
nov_out = {"leg": "2026-11-03 CE 23600 family C entry 09:50 @75.90 gap +0.6034% net +3036.50",
           "raw_factors": nov_raw, "within_family_C_percentiles": nov_pcts,
           "wf_score": nov_score, "fate": {}}
for name in ("F70", "F60", "F50"):
    cut = results["levels"][name]["cutoffs"]["C"]
    nov_out["fate"][name] = "KEPT" if nov_score >= cut else "IDLED"
results["november"] = nov_out
print("NOVEMBER:", json.dumps(nov_out))

# full within-family ranked lists for the report appendix
results["ranked_by_family"] = {
    f: [{kk: l[kk] for kk in ("date", "side", "family", "rep", "entry_time", "bucket",
                              "prem", "gap", "net", "f_time", "f_gap", "f_prem", "f_exp",
                              "wf_score", "stood_down")} for l in ranked_fam[f]]
    for f in FAMS
}
with open(f"{TR}/phase2b_tuning_nifty_results.json", "w") as fh:
    json.dump(results, fh, indent=1)
print("WROTE phase2b_tuning_nifty_results.json")
