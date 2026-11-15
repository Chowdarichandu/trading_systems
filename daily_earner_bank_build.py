#!/usr/bin/env python3
"""Daily Earner build — Milestone 1: BANK NIFTY.
Assembly pre-registered in daily_earner_build_2026-11-16.md §1.1 before this ran.
Streams: LEGACY = bank_engine_r6_v21_trades.csv (frozen BNF-PAPER-V1 ledger);
SKILL/VOLRIX increments = historical_proof_bank_B2_trades.csv pool legs carrying
Skill V3 / Volrix (b) sources, deduped vs legacy BASE on (date, direction).
All nets premium basis, 1 lot (30), Rs 220/trade already inside stored nets.
"""
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
random.seed(20261113)

def fnum(x):
    return float(x) if x not in ("", None) else 0.0

# ---------- Jan-Oct streams ----------
v21 = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))
legacy_total = sum(fnum(r["net_inr"]) for r in v21)
assert abs(legacy_total - 83650.50) < 0.01, legacy_total

pool = list(csv.DictReader(open(TR / "historical_proof_bank_B2_trades.csv")))
assert len(pool) == 89 and all(r["status"] == "COMPUTED" for r in pool)
pool_total = sum(fnum(r["net_rs"]) for r in pool)
assert abs(pool_total - 18731.50) < 0.01, pool_total

base_keys = {(r["date"], r["direction"]) for r in v21 if r["family"] == "BASE"}
all_v21_keys = {(r["date"], r["direction"]) for r in v21}

skill_rows = [r for r in pool if "Skill V3" in r["source_systems"]]
volrix_rows = [r for r in pool if "Volrix (b)" in r["source_systems"]]
union_rows = [r for r in pool if ("Skill V3" in r["source_systems"] or "Volrix (b)" in r["source_systems"])]

incr, dropped = [], []
for r in union_rows:
    (incr if (r["date"], r["direction"]) not in base_keys else dropped).append(r)

def stream_label(r):
    s = r["source_systems"]
    if "Skill V3" in s and "Volrix (b)" in s: return "SKILL+VOLRIX"
    if "Skill V3" in s: return "SKILL"
    return "VOLRIX"

assembly = []
for r in v21:
    assembly.append({"date": r["date"], "index": "BANKNIFTY", "stream": "LEGACY",
                     "source": r["rep"], "family": r["family"], "direction": r["direction"],
                     "entry_time": r["entry_time"], "entry_premium": r["entry_premium"],
                     "exit_time": r["exit_time"], "exit_premium": r["exit_premium"],
                     "exit_reason": r["exit_reason"], "net_inr": fnum(r["net_inr"])})
for r in incr:
    assembly.append({"date": r["date"], "index": "BANKNIFTY", "stream": stream_label(r),
                     "source": r["source_systems"], "family": "POOL-G0",
                     "direction": r["direction"], "entry_time": r["entry_time"],
                     "entry_premium": r["entry_premium"], "exit_time": r["exit_time"],
                     "exit_premium": r["exit_premium"], "exit_reason": r["exit_reason"],
                     "net_inr": fnum(r["net_rs"])})
assembly.sort(key=lambda x: (x["date"], x["entry_time"]))

incr_total = sum(x["net_inr"] for x in assembly if x["stream"] != "LEGACY")
asm_total = sum(x["net_inr"] for x in assembly)
skill_stream_total = sum(fnum(r["net_rs"]) for r in skill_rows)
volrix_stream_total = sum(fnum(r["net_rs"]) for r in volrix_rows)

# ---------- gate computations ----------
months = [f"2026-{m:02d}" for m in range(1, 11)]
def month_table(rows, key="net_inr"):
    t = {m: 0.0 for m in months}
    for r in rows: t[r["date"][:7]] += r[key]
    return t

asm_months = month_table(assembly)
legacy_months = month_table([{"date": r["date"], "net_inr": fnum(r["net_inr"])} for r in v21])
sorted_legs = sorted((x["net_inr"] for x in assembly), reverse=True)
ex_top3 = asm_total - sum(sorted_legs[:3])
h1 = sum(v for m, v in asm_months.items() if m <= "2026-05")
h2 = sum(v for m, v in asm_months.items() if m >= "2026-06")
red_months = [m for m, v in asm_months.items() if v < 0]
best_month = max(asm_months, key=asm_months.get)
worst_month = min(asm_months, key=asm_months.get)

# placebo (a): random k-subsets of the 89 pool legs vs increment standalone sum
k = len(incr)
pool_nets = [fnum(r["net_rs"]) for r in pool]
draws = sorted(sum(random.sample(pool_nets, k)) for _ in range(1000))
p90 = draws[int(0.90 * len(draws))]
p50 = statistics.median(draws)
pct_rank = sum(1 for d in draws if d < incr_total) / len(draws) * 100

# ---------- daily line Jan-Oct ----------
daily = list(csv.DictReader(open(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv")))
trading_days = [r["date"] for r in daily if "2026-01-01" <= r["date"] <= "2026-10-31"]
day_net = defaultdict(float)
for x in assembly: day_net[x["date"]] += x["net_inr"]
day_series = [(d, day_net.get(d, 0.0)) for d in trading_days]
ge2000 = sum(1 for _, v in day_series if v >= 2000)
in_zone = sum(1 for _, v in day_series if 2000 <= v <= 3000)
ge3000 = sum(1 for _, v in day_series if v > 3000)
pos_days = sum(1 for _, v in day_series if v > 0)

# placebo (b): delay-1-day on increment legs (daily-line shape only)
td_idx = {d: i for i, d in enumerate(trading_days)}
shifted = defaultdict(float)
for x in assembly:
    d = x["date"]
    if x["stream"] != "LEGACY" and td_idx.get(d, 10**9) + 1 < len(trading_days):
        shifted[trading_days[td_idx[d] + 1]] += x["net_inr"]
    else:
        shifted[d] += x["net_inr"]
shift_ge2000 = sum(1 for d in trading_days if shifted.get(d, 0.0) >= 2000)

# ---------- November ----------
legacy_log = [r for r in csv.DictReader(open(TR / "november_paper_bank_log.csv"))
              if r["channel"] == "PRIMARY" and r["system_source"] != "none"]
skill_log = list(csv.DictReader(open(TR / "november_shadow_skill_bank_log.csv")))
legacy_nov = {(r["date"], r["direction"]): r for r in legacy_log}
nov_rows, nov_overlap = [], []
for r in legacy_log:
    nov_rows.append({"date": r["date"], "stream": "LEGACY", "direction": r["direction"],
                     "entry_time": r["entry_time"], "strike": r["strike"],
                     "entry_premium": r["entry_premium"], "exit_time": r["exit_time"],
                     "exit_premium": r["exit_premium"], "exit_reason": r["exit_reason"],
                     "net_inr": fnum(r["net_inr"])})
for r in skill_log:
    key = (r["date"], r["direction"])
    row = {"date": r["date"], "stream": "SKILL", "direction": r["direction"],
           "entry_time": r["entry_time"], "strike": r["strike"],
           "entry_premium": r["entry_premium"], "exit_time": r["exit_time"],
           "exit_premium": r["exit_premium"], "exit_reason": r["exit_reason"],
           "net_inr": fnum(r["net_inr"])}
    if key in legacy_nov:
        nov_overlap.append({**row, "legacy_entry_time": legacy_nov[key]["entry_time"],
                            "legacy_source": legacy_nov[key]["system_source"]})
    else:
        nov_rows.append(row)
nov_rows.sort(key=lambda x: (x["date"], x["entry_time"]))

# Volrix November trigger scan: daily closes (volrix CSV to Nov 3) + progressive spot closes
closes = {r["date"]: float(r["close"]) for r in daily}
spot = defaultdict(dict)
with open(TR / "data/progressive/BANKNIFTY/spot_5m.csv") as fh:
    for r in csv.DictReader(fh):
        spot[r["timestamp"][:10]][r["timestamp"][11:16]] = float(r["close"])
for d, bars in spot.items():
    if d.startswith("2026-11") and d not in closes and bars:
        closes[d] = bars[max(bars)]
nov_days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
            "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
all_days = sorted(d for d in closes if "2026-10-01" <= d <= "2026-11-13")
volrix_nov = []
last_entry_idx = all_days.index("2026-10-26")  # last (b) entry, from the Jan-Oct stream
for i, d in enumerate(all_days):
    if d not in nov_days: continue
    prev = all_days[i - 1]
    chg = (closes[d] / closes[prev] - 1) * 100 if d in closes and prev in closes else None
    # trigger is decided by PREV day close vs the day before it -> entry today
    j = i - 1
    trig = None
    if j >= 1:
        pc = (closes[all_days[j]] / closes[all_days[j - 1]] - 1) * 100
        trig = pc
    cooldown_left = max(0, 10 - (i - last_entry_idx))
    fired = bool(trig is not None and trig <= -1.0 and cooldown_left == 0)
    volrix_nov.append({"entry_day": d, "prev_day": all_days[j] if j >= 0 else None,
                       "prev_day_change_pct": None if trig is None else round(trig, 2),
                       "cooldown_left_at_open": cooldown_left, "fired": fired})
    if fired: last_entry_idx = i

nov_day_net = defaultdict(float)
for r in nov_rows: nov_day_net[r["date"]] += r["net_inr"]
nov_series = [(d, nov_day_net.get(d, 0.0)) for d in nov_days]

out = {
    "legacy_total": legacy_total, "legacy_legs": len(v21),
    "skill_stream_legs": len(skill_rows), "skill_stream_total": skill_stream_total,
    "volrix_stream_legs": len(volrix_rows), "volrix_stream_total": volrix_stream_total,
    "increment_legs": k, "increment_total": incr_total,
    "increment_by_stream": {s: [sum(x["net_inr"] for x in assembly if x["stream"] == s),
                                sum(1 for x in assembly if x["stream"] == s)]
                            for s in ("SKILL", "VOLRIX", "SKILL+VOLRIX")},
    "dropped_overlap_legs": len(dropped),
    "dropped_overlap_total": sum(fnum(r["net_rs"]) for r in dropped),
    "assembly_legs": len(assembly), "assembly_total": asm_total,
    "asm_months": asm_months, "legacy_months": legacy_months,
    "halves": [h1, h2], "ex_top3": ex_top3, "top3": sorted_legs[:3],
    "red_months": red_months, "best_month": [best_month, asm_months[best_month]],
    "worst_month": [worst_month, asm_months[worst_month]],
    "best_month_share_pct": round(asm_months[best_month] / asm_total * 100, 1) if asm_total > 0 else None,
    "placebo_random_subset": {"k": k, "p50": p50, "p90": p90, "increment_pct_rank": round(pct_rank, 1)},
    "trading_days_janoct": len(trading_days),
    "avg_per_day": round(asm_total / len(trading_days), 2),
    "legacy_avg_per_day": round(legacy_total / len(trading_days), 2),
    "days_ge2000": ge2000, "days_in_zone": in_zone, "days_gt3000": ge3000, "pos_days": pos_days,
    "delay1_days_ge2000": shift_ge2000,
    "nov_legacy_total": sum(fnum(r["net_inr"]) for r in legacy_log),
    "nov_skill_total": sum(fnum(r["net_inr"]) for r in skill_log),
    "nov_overlap": nov_overlap,
    "nov_assembly_total": sum(nov_day_net.values()),
    "nov_series": nov_series, "volrix_nov_scan": volrix_nov,
}
with open(TR / "daily_earner_bank_results.json", "w") as fh: json.dump(out, fh, indent=1)
with open(TR / "daily_earner_bank_janoct_trades.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(assembly[0].keys())); w.writeheader(); w.writerows(assembly)
with open(TR / "daily_earner_bank_november_trades.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(nov_rows[0].keys())); w.writeheader(); w.writerows(nov_rows)
print(json.dumps(out, indent=1))
