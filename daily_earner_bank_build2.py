#!/usr/bin/env python3
"""Daily Earner — Bank v2: fallbacks, November (both dedupe rules, disclosed),
fixed Volrix trigger scan, time-overlap diagnostic. Jan-Oct assembly as v1."""
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
random.seed(20261113)
def fnum(x): return float(x) if x not in ("", None) else 0.0
MONTHS = [f"2026-{m:02d}" for m in range(1, 11)]

v21 = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))
pool = list(csv.DictReader(open(TR / "historical_proof_bank_B2_trades.csv")))
base_keys = {(r["date"], r["direction"]) for r in v21 if r["family"] == "BASE"}

def gate_stats(legs):
    """legs: list of dicts with date, net. Returns the gate-relevant stats."""
    tot = sum(x["net"] for x in legs)
    mt = {m: 0.0 for m in MONTHS}
    for x in legs: mt[x["date"][:7]] += x["net"]
    srt = sorted((x["net"] for x in legs), reverse=True)
    return {"legs": len(legs), "total": tot, "months": mt,
            "h1": sum(v for m, v in mt.items() if m <= "2026-05"),
            "h2": sum(v for m, v in mt.items() if m >= "2026-06"),
            "ex_top3": tot - sum(srt[:3]), "top3": srt[:3],
            "red_months": [m for m, v in mt.items() if v < 0],
            "best_month": max(mt, key=mt.get), "worst_month": min(mt, key=mt.get),
            "best_share_pct": round(mt[max(mt, key=mt.get)] / tot * 100, 1) if tot > 0 else None}

legacy_legs = [{"date": r["date"], "net": fnum(r["net_inr"])} for r in v21]
def pool_leg(r): return {"date": r["date"], "net": fnum(r["net_rs"])}
skill_all = [pool_leg(r) for r in pool if "Skill V3" in r["source_systems"]]
volrix_all = [pool_leg(r) for r in pool if "Volrix (b)" in r["source_systems"]]
union_all = [pool_leg(r) for r in pool if "Skill V3" in r["source_systems"] or "Volrix (b)" in r["source_systems"]]
def not_in_frame(rows): return [pool_leg(r) for r in rows if (r["date"], r["direction"]) not in base_keys]
skill_incr = not_in_frame([r for r in pool if "Skill V3" in r["source_systems"]])
volrix_incr = not_in_frame([r for r in pool if "Volrix (b)" in r["source_systems"]])
union_incr = not_in_frame([r for r in pool if "Skill V3" in r["source_systems"] or "Volrix (b)" in r["source_systems"]])

configs = {
    "FULL (Legacy+Skill+Volrix)": legacy_legs + union_incr,
    "A1 (Legacy+Skill)": legacy_legs + skill_incr,
    "A2 (Legacy+Volrix)": legacy_legs + volrix_incr,
    "A3 (Skill+Volrix, no legacy)": union_all,
    "B1 (Legacy alone)": legacy_legs,
    "B2 (Skill alone)": skill_all,
    "B3 (Volrix alone)": volrix_all,
}
stats = {name: gate_stats(legs) for name, legs in configs.items()}

# random-subset placebo for each increment (vs its own base)
pool_nets = [fnum(r["net_rs"]) for r in pool]
def placebo(incr_legs):
    k = len(incr_legs)
    if k == 0: return None
    draws = sorted(sum(random.sample(pool_nets, k)) for _ in range(1000))
    s = sum(x["net"] for x in incr_legs)
    return {"k": k, "incr_total": s, "p50": statistics.median(draws),
            "p90": draws[int(0.9 * len(draws))],
            "pct_rank": round(sum(1 for d in draws if d < s) / len(draws) * 100, 1)}
placebos = {"FULL": placebo(union_incr), "A1": placebo(skill_incr), "A2": placebo(volrix_incr)}

# time-overlap diagnostic: increment legs vs legacy legs same day (any family)
def t2m(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)
legacy_windows = defaultdict(list)
for r in v21: legacy_windows[r["date"]].append((t2m(r["entry_time"]), t2m(r["exit_time"])))
overlap = []
for r in pool:
    if ("Skill V3" in r["source_systems"] or "Volrix (b)" in r["source_systems"]) and (r["date"], r["direction"]) not in base_keys:
        e, x = t2m(r["entry_time"]), t2m(r["exit_time"])
        for (le, lx) in legacy_windows.get(r["date"], []):
            if e < lx and le < x:
                overlap.append({"date": r["date"], "direction": r["direction"], "net": fnum(r["net_rs"])})
                break

# trading days / daily stats for the configs that matter
daily = list(csv.DictReader(open(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv")))
trading_days = [r["date"] for r in daily if "2026-01-01" <= r["date"] <= "2026-10-31"]
def daily_stats(legs):
    dn = defaultdict(float)
    for x in legs: dn[x["date"]] += x["net"]
    series = [dn.get(d, 0.0) for d in trading_days]
    return {"avg_per_day": round(sum(series) / len(series), 2),
            "days_ge2000": sum(1 for v in series if v >= 2000),
            "days_in_zone": sum(1 for v in series if 2000 <= v <= 3000),
            "days_gt3000": sum(1 for v in series if v > 3000),
            "pos_days": sum(1 for v in series if v > 0)}
dstats = {name: daily_stats(legs) for name, legs in configs.items()}

# ---------- November, fixed ----------
sd = list(csv.DictReader(open(TR / "data/banknifty-2026-11/spot_daily.csv")))
print("spot_daily cols:", list(sd[0].keys()), "rows:", len(sd), sd[0], sd[-1])
closes = {r["date"]: float(r["close"]) for r in csv.DictReader(open(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv"))}
for r in sd: closes[r["date"]] = float(r["close"])
nov_days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
            "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
all_days = sorted(d for d in closes if "2026-10-20" <= d <= "2026-11-12")
scan = []
last_idx = all_days.index("2026-10-26")
for i, d in enumerate(all_days):
    if d not in nov_days[:-1]: continue
    j = i - 1
    pc = (closes[all_days[j]] / closes[all_days[j - 1]] - 1) * 100
    cd = max(0, 10 - (i - last_idx))
    fired = pc <= -1.0 and cd == 0
    scan.append({"entry_day": d, "prev_day": all_days[j], "prev_change_pct": round(pc, 2),
                 "cooldown_left": cd, "fired": fired})
    if fired: last_idx = i

legacy_log = [r for r in csv.DictReader(open(TR / "november_paper_bank_log.csv"))
              if r["channel"] == "PRIMARY" and r["system_source"] != "none"]
skill_log = list(csv.DictReader(open(TR / "november_shadow_skill_bank_log.csv")))
def legkey(r): return (r["date"], r["direction"], r["strike"], r["entry_time"])
legacy_keys = {legkey(r) for r in legacy_log}
novA = defaultdict(float)  # pre-registered (date, direction)
legacy_dd = {(r["date"], r["direction"]) for r in legacy_log}
for r in legacy_log: novA[r["date"]] += fnum(r["net_inr"])
for r in skill_log:
    if (r["date"], r["direction"]) not in legacy_dd: novA[r["date"]] += fnum(r["net_inr"])
novB = defaultdict(float)  # identical-leg dedupe
for r in legacy_log: novB[r["date"]] += fnum(r["net_inr"])
for r in skill_log:
    if legkey(r) not in legacy_keys: novB[r["date"]] += fnum(r["net_inr"])
def series(dd): 
    out, cum = [], 0.0
    for d in nov_days:
        cum += dd.get(d, 0.0); out.append([d, dd.get(d, 0.0), cum])
    return out

out = {"configs": stats, "placebos": placebos, "daily_stats": dstats,
       "overlap_diagnostic": {"legs_overlapping_legacy_window": len(overlap), "legs": overlap},
       "trading_days": len(trading_days), "volrix_nov_scan": scan,
       "nov_series_preregistered_dedupe": series(novA),
       "nov_series_identical_leg_dedupe": series(novB),
       "nov_closes_used": {d: closes.get(d) for d in ["2026-10-30"] + nov_days[:-1]}}
with open(TR / "daily_earner_bank_results2.json", "w") as fh: json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
