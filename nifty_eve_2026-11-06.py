#!/usr/bin/env python3
"""NIFTY-EVE-13 gate run, 2026-11-06 evening engine (Nifty only, paper, Rs0).

Trigger: SHADOW DEC-S1's 2026-11-05 Component B PE leg, journalled tonight as
a full stop (-Rs3,470, Lesson RSI-NIFTY-007), is the class already removed
from the tuned line by NIFTY-EVE-07. The tuned frame is now TUNED SHADOW
BOOK v2 (DEC-S1 minus B PE, minus A CE, minus C CE; 59 legs, +Rs115,950.75,
GATE PASS 2026-11-05, live from today). Tonight's one mechanically new
candidate on that frame is the bleed-guard form the owner directed on
2026-11-03, applied to v2 for the first time:

  NIFTY-EVE-13: realised day-loss cap -Rs3,000 on TUNED v2 — legs taken in
  entry order; a later same-day leg is skipped only if earlier legs have
  already exited with realised day P&L <= -Rs3,000 before its entry
  (causal form; same form as EVE-04, which was a no-op on the 97-leg
  DEC-S1 frame — v2's different leg set makes this a distinct test, not
  an identical retest).

Full controls in the same run: independent re-sum of the DEC-S1 base
(97 legs / +91,168.50) and the v2 frame (59 legs / +115,950.75) before
scoring; timing audit (skip input = earlier legs' realised exits, known
before the later entry by construction); halves; full month table;
ex-top-3; placebo = the same cap at -Rs6,000 (a cap that can bind later).
Basis: premiums per 1 lot (65), cost Rs220/trade inside net_inr,
UNIQUE-ONCE frozen leg set.
"""
import csv, json, collections

SRC = "/home/hatch/workspace/trading/nifty_next_phase_trades.csv"
rows = [r for r in csv.DictReader(open(SRC)) if r["set"] == "BASE"]
assert len(rows) == 97 and round(sum(float(r["net_inr"]) for r in rows), 2) == 91168.50

V2 = [r for r in rows if not ((r["component"] == "B" and r["direction"] == "PE")
                              or (r["component"] == "A" and r["direction"] == "CE")
                              or (r["component"] == "C" and r["direction"] == "CE"))]
assert len(V2) == 59 and round(sum(float(r["net_inr"]) for r in V2), 2) == 115950.75

def stats(sub):
    net = round(sum(float(r["net_inr"]) for r in sub), 2)
    months, days = collections.defaultdict(float), collections.defaultdict(float)
    for r in sub:
        months[r["date"][:7]] += float(r["net_inr"]); days[r["date"]] += float(r["net_inr"])
    top3 = sorted((float(r["net_inr"]) for r in sub), reverse=True)[:3]
    cum, mrows = 0.0, []
    for m in sorted(months):
        cum += months[m]; mrows.append({"month": m, "net": round(months[m], 2), "cum": round(cum, 2)})
    return {"legs": len(sub), "net": net,
            "ft_pct": round(100.0 * sum(int(r["ft"]) for r in sub) / len(sub), 1) if sub else 0.0,
            "h1_jan_may": round(sum(float(r["net_inr"]) for r in sub if r["date"] < "2026-06-01"), 2),
            "h2_jun_oct": round(sum(float(r["net_inr"]) for r in sub if r["date"] >= "2026-06-01"), 2),
            "ex_top3": round(net - sum(top3), 2), "months": mrows,
            "worst_day": [min(days.items(), key=lambda kv: kv[1])[0], round(min(days.values()), 2)],
            "leg_days": len(days)}

def apply_cap(sub, cap):
    by_day = collections.defaultdict(list)
    for r in sub: by_day[r["date"]].append(r)
    kept, skipped = [], []
    for d, legs in by_day.items():
        legs = sorted(legs, key=lambda r: r["entry_time"])
        realised = []  # (exit_time, net)
        for leg in legs:
            prior = sum(n for xt, n in realised if xt <= leg["entry_time"])
            if prior <= cap and any(xt <= leg["entry_time"] for xt, _ in realised):
                skipped.append(leg)
            else:
                kept.append(leg); realised.append((leg["exit_time"], float(leg["net_inr"])))
    return kept, skipped

base = stats(V2)
kept, skipped = apply_cap(V2, -3000.0)
var = stats(kept)
pkept, pskipped = apply_cap(V2, -6000.0)
placebo = stats(pkept)
base_months = {m["month"]: m["net"] for m in base["months"]}
var_months = {m["month"]: m["net"] for m in var["months"]}
flips = [m for m in base_months if base_months[m] > 0 and var_months.get(m, 0.0) < 0]
out = {
  "incumbent_frame": "TUNED SHADOW v2 = DEC-S1 minus B PE, minus A CE, minus C CE (59 legs, +115,950.75)",
  "EVE-13": {
    "candidate": "NIFTY-EVE-13 — realised day-loss cap -Rs3,000 on TUNED v2 (causal skip form)",
    "skipped_legs": len(skipped),
    "skipped_detail": [{"date": r["date"], "component": r["component"], "direction": r["direction"], "entry_time": r["entry_time"], "net_inr": float(r["net_inr"])} for r in skipped],
    "incumbent_TUNED_v2": base, "variant": var, "placebo_cap_-6000": placebo,
    "green_to_red_flips": flips,
    "verdict": "NO-OP — not a PASS, nothing promoted" if len(skipped) == 0 else ("PASS" if var["net"] > base["net"] and var["net"] > placebo["net"] and not flips else "FAIL"),
  },
}
json.dump(out, open("/home/hatch/workspace/trading/nifty_eve_2026-11-06_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
