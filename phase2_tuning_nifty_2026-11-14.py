#!/usr/bin/env python3
"""Phase-2 tuning — Nifty selectivity (confidence-gating) on TUNED v1.
Implements phase2_tuning_nifty_SPEC.md (frozen 2026-11-14 08:56 IST) exactly.
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
for r in rows:
    legs.append({
        "date": r["date"], "side": r["side"], "family": r["family"],
        "rep": r["rep"], "entry_time": r["entry_time"], "bucket": r["bucket"],
        "prem": float(r["entry_premium"]), "gap": float(r["gap_pct"]),
        "net": float(r["net_inr"]), "stood_down": r["stood_down"] == "YES",
    })
assert len(legs) == 74, len(legs)
assert not any(l["family"] == "B" and l["side"] == "PE" for l in legs), "B-PE in v1 store"

# ---------- Step 0: control ----------
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
# N-FIX-1 anchors from the same store
nfix_idled = [l for l in legs if l["stood_down"]]
nfix_kept_keys = None
assert len(nfix_idled) == 8 and round(sum(l["net"] for l in nfix_idled), 2) == -14119.75
assert round(total - sum(l["net"] for l in nfix_idled), 2) == 117170.00
med = statistics.median([l["prem"] for l in legs])
assert abs(med - MEDIAN_PREM) < 0.01, med
print("CONTROL OK:", json.dumps(control))

# ---------- calendar (205 trading days Jan-Oct 2026) ----------
cal = [r["date"] for r in csv.DictReader(open(f"{TR}/volrix/nifty_daily_2019_2026.csv"))
       if "2026-01-01" <= r["date"] <= "2026-10-31"]
assert len(cal) == 205, len(cal)

# ---------- Step 1: confidence score ----------
def score_leg(side, family, bucket, prem, gap, date_s):
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
    return {"f_time": f_time, "f_gap": f_gap, "f_prem": round(f_prem, 4),
            "f_exp": f_exp, "score": round((f_time + f_gap + f_prem + f_exp) / 4, 4)}

for l in legs:
    l.update(score_leg(l["side"], l["family"], l["bucket"], l["prem"], l["gap"], l["date"]))

# ---------- subset statistics ----------
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

# ---------- Steps 2+3: thresholds + placebos ----------
ranked = sorted(legs, key=lambda l: (-l["score"], l["date"], l["entry_time"]))
nfix_kept_idx = {i for i, l in enumerate(legs) if not l["stood_down"]}
leg_index = {id(l): i for i, l in enumerate(legs)}
rng = random.Random(20261114)
results = {"control": control, "median_premium": MEDIAN_PREM, "thresholds": {}}
for name, frac in (("T70", 0.70), ("T60", 0.60), ("T50", 0.50)):
    k = round(frac * len(legs))
    kept = ranked[:k]
    st = subset_stats(kept)
    cutoff = kept[-1]["score"]
    # placebo: 200 random subsets of the same size
    all_nets = [l["net"] for l in legs]
    below = 0
    for _ in range(200):
        draw = rng.sample(all_nets, k)
        if sum(draw) < st["total"]:
            below += 1
    pct = below / 200
    kept_idx = {leg_index[id(l)] for l in kept}
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
    results["thresholds"][name] = {
        "k": k, "cutoff_score": cutoff, "stats": st,
        "placebo_percentile": pct, "nfix_overlap": overlap,
        "checks": checks, "verdict": "PASS" if all(checks.values()) else "FAIL",
        "failing": [c for c, ok in checks.items() if not ok],
        "kept_legs": [{kk: l[kk] for kk in ("date", "side", "family", "rep", "entry_time",
                                             "prem", "gap", "net", "score")} for l in kept],
    }
    print(name, "k=", k, "cutoff=", cutoff, json.dumps(st), "placebo=", pct,
          "verdict=", results["thresholds"][name]["verdict"],
          "failing=", results["thresholds"][name]["failing"])

# ---------- Step 5: November counterfactual ----------
nov = score_leg("CE", "C", "pre-11:00", 75.90, 0.6034, "2026-11-03")
nov_out = {"leg": "2026-11-03 CE 23600 family C entry 09:50 @75.90 gap +0.6034% net +3036.50",
           "score_detail": nov, "fate": {}}
for name in ("T70", "T60", "T50"):
    cut = results["thresholds"][name]["cutoff_score"]
    nov_out["fate"][name] = "KEPT" if nov["score"] >= cut else "IDLED"
results["november"] = nov_out
print("NOVEMBER:", json.dumps(nov_out))

# full ranked list for the report appendix
results["ranked_all"] = [{kk: l[kk] for kk in ("date", "side", "family", "rep", "entry_time",
                                               "bucket", "prem", "gap", "net", "f_time",
                                               "f_gap", "f_prem", "f_exp", "score",
                                               "stood_down")} for l in ranked]
with open(f"{TR}/phase2_tuning_nifty_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE phase2_tuning_nifty_results.json")
