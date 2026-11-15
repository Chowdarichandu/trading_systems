#!/usr/bin/env python3
"""ROUND 8 DIAGNOSIS (not a candidate, not scored for banking): re-score the
already-gated Round-7 FADE construction (threshold 0.50%, entry 09:35,
unrestricted, standing geometry) leg by leg to diagnose the March flip
(+7,895.00 -> -8,233.50 combined) before WS1(b)'s exact form is frozen.
Named ingredient under the Round-8 brief. Nifty only, paper, real Rs0."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
from nifty_engine_r4_harness import DAILY, PREV

TR = Path.home() / "workspace/trading"

standing = R7.standing_legs()
skeys = R7.keys_of(standing)
fade_legs, excluded = R7.gap_legs("fade", skeys)
print(f"fade legs regenerated: {len(fade_legs)} (excluded {len(excluded)})")
res, nc, _ = R6.score_r6(fade_legs, geom=R7.STANDING_GEOM)
tot = round(sum(r["net"] for r in res), 2)
print(f"fade standalone re-score: {tot:+,.2f} over {len(res)} legs, NC {nc} "
      f"(Round-7 record: +32,127.15 over 49 legs)")
assert tot == 32127.15 and len(res) == 49 and nc == 0, "REGENERATION MISMATCH"

gapmap = dict(R7.gap_days())  # date -> gap fraction (threshold 0.50%)

def pdret_prior_frac(d):
    p = PREV.get(d)
    if not p or not PREV.get(p): return None
    return DAILY[p]["c"] / DAILY[PREV[p]]["c"] - 1.0

def pd_intraday_frac(d):
    """Prior day's intraday direction: close/open - 1 of day P (known at D open)."""
    p = PREV.get(d)
    if not p: return None
    return DAILY[p]["c"] / DAILY[p]["o"] - 1.0

bymonth = {}
print("\n--- ALL fade legs with causal day-state features ---")
print(f"{'date':11} {'dir':4} {'gap%':>7} {'pdret%':>7} {'pdint%':>7} {'net':>10} reason")
for r in sorted(res, key=lambda x: x["date"]):
    d = r["date"]
    g = gapmap[d]
    pr = pdret_prior_frac(d)
    pi = pd_intraday_frac(d)
    bymonth[d[:7]] = bymonth.get(d[:7], 0.0) + r["net"]
    print(f"{d:11} {r['direction']:4} {g*100:+7.2f} {pr*100:+7.2f} {pi*100:+7.2f} "
          f"{r['net']:+10.2f} {r['exit_reason']}")
print("\nfade sleeve month sums:", {k: round(v, 2) for k, v in sorted(bymonth.items())})

mar = [r for r in res if r["date"].startswith("2026-03")]
print(f"\nMARCH fade legs: {len(mar)}, sum {round(sum(r['net'] for r in mar), 2):+,.2f} "
      f"(flip needs < -7,895.00 vs standing March +7,895.00)")

# Candidate (b) forms — DIAGNOSTIC splits only (no banking, no gate):
def sgn(x): return (x > 0) - (x < 0)
forms = {
    "WITH-trend (pdret c2c)": lambda d: sgn(gapmap[d]) == sgn(pdret_prior_frac(d)),
    "AGAINST-trend (pdret c2c)": lambda d: sgn(gapmap[d]) == -sgn(pdret_prior_frac(d)),
    "WITH-trend (pd intraday)": lambda d: sgn(gapmap[d]) == sgn(pd_intraday_frac(d)),
    "AGAINST-trend (pd intraday)": lambda d: sgn(gapmap[d]) == -sgn(pd_intraday_frac(d)),
}
print("\n--- diagnostic splits of the R7 fade population (all months + March) ---")
for name, f in forms.items():
    sub = [r for r in res if f(r["date"])]
    subm = [r for r in mar if f(r["date"])]
    print(f"{name:28} legs {len(sub):2} net {round(sum(r['net'] for r in sub),2):+10.2f} | "
          f"March legs {len(subm)} net {round(sum(r['net'] for r in subm),2):+10.2f}")
for thr in (0.0075, 0.0100):
    sub = [r for r in res if abs(gapmap[r["date"]]) >= thr]
    subm = [r for r in mar if abs(gapmap[r["date"]]) >= thr]
    print(f"{'threshold >=' + str(thr*100) + '%':28} legs {len(sub):2} net "
          f"{round(sum(r['net'] for r in sub),2):+10.2f} | March legs {len(subm)} net "
          f"{round(sum(r['net'] for r in subm),2):+10.2f}")
late = [r for r in res if r["entry_time"] == "09:35"]
print(f"\n(entry-time split is a construction change — scored later as Cycle 145, not here)")
