#!/usr/bin/env python3
"""Daily Earner build — Milestone 2: NIFTY.
Pre-registration in daily_earner_build_2026-11-16.md §2.1 (written before totals).
FRAME = nifty_next_phase_trades.csv (DEC-S1 stored leg set, 97 legs);
SKILL/VOLRIX increments = historical_proof_nifty_N1_trades.csv pool legs,
deduped vs frame Component A on (date, direction) — Bank §1.1's rule.
All nets premium basis, 1 lot (65), Rs 220/trade already inside stored nets.
"""
import csv, json, random, re, statistics
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
random.seed(20261113)
def fnum(x): return float(x) if x not in ("", None) else 0.0
MONTHS = [f"2026-{m:02d}" for m in range(1, 11)]

# ---------- Jan-Oct streams ----------
frame = list(csv.DictReader(open(TR / "nifty_next_phase_trades.csv")))
frame_total = sum(fnum(r["net_inr"]) for r in frame)
assert len(frame) == 97 and abs(frame_total - 91168.50) < 0.01, frame_total

pool = list(csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv")))
assert len(pool) == 108 and all(r["status"] == "COMPUTED" for r in pool)
pool_total = sum(fnum(r["net_rs"]) for r in pool)
assert abs(pool_total - 25159.00) < 0.01, pool_total
assert len({(r["date"], r["direction"]) for r in pool}) == 108

a_keys = {(r["date"], r["direction"]) for r in frame if r["component"] == "A"}
all_frame_keys = {(r["date"], r["direction"]) for r in frame}
pool_keys = {(r["date"], r["direction"]) for r in pool}
assert len(a_keys) == 35 and a_keys <= pool_keys

skill_rows = [r for r in pool if "Skill V3" in r["source_systems"]]
volrix_rows = [r for r in pool if "Volrix (b)" in r["source_systems"]]
union_rows = [r for r in pool if ("Skill V3" in r["source_systems"] or "Volrix (b)" in r["source_systems"])]
oct_vx = [r for r in volrix_rows if r["date"] == "2026-10-09"]
assert len(oct_vx) == 1 and abs(fnum(oct_vx[0]["net_rs"]) - 5630.00) < 0.01  # standalone October check

def stream_label(r):
    s = r["source_systems"]
    if "Skill V3" in s and "Volrix (b)" in s: return "SKILL+VOLRIX"
    if "Skill V3" in s: return "SKILL"
    return "VOLRIX"

def increments(rows, keys):
    inc, drop = [], []
    for r in rows:
        (drop if (r["date"], r["direction"]) in keys else inc).append(r)
    return inc, drop

incr, dropped = increments(union_rows, a_keys)
incr_all_keys, dropped_all_keys = increments(union_rows, all_frame_keys)
skill_incr, _ = increments(skill_rows, a_keys)
volrix_incr, _ = increments(volrix_rows, a_keys)

def frame_leg(r, stream="FRAME"):
    return {"date": r["date"], "index": "NIFTY", "stream": stream,
            "source": f"DEC-S1 {r['component']}", "family": r["component"],
            "direction": r["direction"], "entry_time": r["entry_time"],
            "entry_premium": r["entry_premium"], "exit_time": r["exit_time"],
            "exit_premium": r["exit_premium"], "exit_reason": r["exit_reason"],
            "net_inr": fnum(r["net_inr"])}
def pool_leg(r):
    return {"date": r["date"], "index": "NIFTY", "stream": stream_label(r),
            "source": r["source_systems"], "family": "POOL-G0",
            "direction": r["direction"], "entry_time": r["entry_time"],
            "entry_premium": r["entry_premium"], "exit_time": r["exit_time"],
            "exit_premium": r["exit_premium"], "exit_reason": r["exit_reason"],
            "net_inr": fnum(r["net_rs"])}

assembly = [frame_leg(r) for r in frame] + [pool_leg(r) for r in incr]
assembly.sort(key=lambda x: (x["date"], x["entry_time"]))

v1_rows = [r for r in frame if not (r["component"] == "B" and r["direction"] == "PE")]
v2_rows = [r for r in v1_rows if not (r["component"] in ("A", "C") and r["direction"] == "CE")]
assert len(v1_rows) == 74 and abs(sum(fnum(r["net_inr"]) for r in v1_rows) - 103050.25) < 0.01
assert len(v2_rows) == 59 and abs(sum(fnum(r["net_inr"]) for r in v2_rows) - 115950.75) < 0.01

def L(rows, netkey="net_inr"):
    return [{"date": r["date"], "net": fnum(r[netkey])} for r in rows]
def LP(rows):
    return [{"date": r["date"], "net": fnum(r["net_rs"])} for r in rows]

configs = {
    "FULL (Frame+Skill+Volrix)": L(frame) + LP(incr),
    "A1 (Frame+Skill)": L(frame) + LP(skill_incr),
    "A2 (Frame+Volrix)": L(frame) + LP(volrix_incr),
    "A3 (Skill+Volrix, no frame)": LP(union_rows),
    "B1 (Frame alone, DEC-S1)": L(frame),
    "B1a (TUNED v1)": L(v1_rows),
    "B1b (TUNED v2)": L(v2_rows),
    "B2 (Skill alone)": LP(skill_rows),
    "B3 (Volrix alone)": LP(volrix_rows),
}

def gate_stats(legs):
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
stats = {name: gate_stats(legs) for name, legs in configs.items()}
frame_months = stats["B1 (Frame alone, DEC-S1)"]["months"]

pool_nets = [fnum(r["net_rs"]) for r in pool]
def placebo(incr_legs_rows):
    k = len(incr_legs_rows)
    if k == 0: return None
    draws = sorted(sum(random.sample(pool_nets, k)) for _ in range(1000))
    s = sum(fnum(r["net_rs"]) for r in incr_legs_rows)
    return {"k": k, "incr_total": s, "p50": statistics.median(draws),
            "p90": draws[int(0.9 * len(draws))],
            "pct_rank": round(sum(1 for d in draws if d < s) / len(draws) * 100, 1)}
placebos = {"FULL": placebo(incr), "A1": placebo(skill_incr), "A2": placebo(volrix_incr)}

# sensitivity: dedupe vs ALL frame components
sens_total = frame_total + sum(fnum(r["net_rs"]) for r in incr_all_keys)
sens_stats = gate_stats(L(frame) + LP(incr_all_keys))

# ---------- daily lines Jan-Oct ----------
daily = list(csv.DictReader(open(TR / "volrix/nifty_daily_2019_2026.csv")))
trading_days = [r["date"] for r in daily if "2026-01-01" <= r["date"] <= "2026-10-31"]
def daily_stats(legs):
    dn = defaultdict(float)
    for x in legs: dn[x["date"]] += x["net"]
    series = [dn.get(d, 0.0) for d in trading_days]
    return {"avg_per_day": round(sum(series) / len(series), 2),
            "days_ge2000": sum(1 for v in series if v >= 2000),
            "days_in_zone": sum(1 for v in series if 2000 <= v <= 3000),
            "days_gt3000": sum(1 for v in series if v > 3000),
            "pos_days": sum(1 for v in series if v > 0),
            "day_net": {d: dn.get(d, 0.0) for d in trading_days}}
dstats = {name: daily_stats(legs) for name, legs in configs.items()}

# delay-1-day on FULL increment (descriptive)
td_idx = {d: i for i, d in enumerate(trading_days)}
shifted = defaultdict(float)
for x in configs["FULL (Frame+Skill+Volrix)"]:
    shifted[x["date"]] += 0.0  # placeholder to keep keys
shifted = defaultdict(float)
frame_day = defaultdict(float)
for x in L(frame): frame_day[x["date"]] += x["net"]
for d in trading_days: shifted[d] += frame_day.get(d, 0.0)
for r in incr:
    d = r["date"]
    if td_idx.get(d, 10**9) + 1 < len(trading_days):
        shifted[trading_days[td_idx[d] + 1]] += fnum(r["net_rs"])
    else:
        shifted[d] += fnum(r["net_rs"])
delay1_ge2000 = sum(1 for d in trading_days if shifted.get(d, 0.0) >= 2000)

# time-overlap diagnostic: increment legs vs frame A-leg windows same day
def t2m(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)
frame_windows = defaultdict(list)
for r in frame: frame_windows[r["date"]].append((t2m(r["entry_time"]), t2m(r["exit_time"])))
overlap = []
for r in incr:
    e, x = t2m(r["entry_time"]), t2m(r["exit_time"])
    for (le, lx) in frame_windows.get(r["date"], []):
        if e < lx and le < x:
            overlap.append({"date": r["date"], "direction": r["direction"], "net": fnum(r["net_rs"])})
            break
# in-frame value of dropped pool legs (G0 worth of keys the frame took via A)
dropped_total = sum(fnum(r["net_rs"]) for r in dropped)

# ---------- November ----------
nov_days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
            "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
def load_log(name):
    rows = [r for r in csv.DictReader(open(TR / name))
            if r["system_source"] not in ("", "none") and r["net_inr"] not in ("", None)]
    return rows
frame_log = load_log("november_shadow_decs1_nifty_log.csv")
skill_log = load_log("november_shadow_skill_nifty_log.csv")
def legkey(r): return (r["date"], r["direction"], r["strike"], r["entry_time"])
frame_dd = {(r["date"], r["direction"]) for r in frame_log}
frame_full = {legkey(r) for r in frame_log}
novA, novB = defaultdict(float), defaultdict(float)
for r in frame_log:
    novA[r["date"]] += fnum(r["net_inr"]); novB[r["date"]] += fnum(r["net_inr"])
for r in skill_log:
    if (r["date"], r["direction"]) not in frame_dd: novA[r["date"]] += fnum(r["net_inr"])
    if legkey(r) not in frame_full: novB[r["date"]] += fnum(r["net_inr"])
def series(dd):
    out, cum = [], 0.0
    for d in nov_days:
        cum += dd.get(d, 0.0); out.append([d, dd.get(d, 0.0), cum])
    return out
v1_nov = [r for r in frame_log if not (r["system_source"] == "DEC-S1 B" and r["direction"] == "PE")]
primary_log = [r for r in csv.DictReader(open(TR / "november_paper_nifty_log.csv"))
               if r["channel"] == "PRIMARY" and r["system_source"] not in ("", "none") and r["net_inr"] not in ("", None)]
# Volrix November evidence: prev-day changes recorded in the primary log notes
trig = {}
for r in csv.DictReader(open(TR / "november_paper_nifty_log.csv")):
    m = re.search(r"prev-day change ([-+0-9.]+)%", r["notes"])
    if m: trig[r["date"]] = float(m.group(1))
trig["2026-11-13"] = round((25299.35 / 25255.05 - 1) * 100, 2)  # Nov 12 close change, verified closes

nov_rows = []
for r in frame_log:
    nov_rows.append({"date": r["date"], "book": "FRAME (DEC-S1 shadow)", "direction": r["direction"],
                     "strike": r["strike"], "entry_time": r["entry_time"], "entry_premium": r["entry_premium"],
                     "exit_time": r["exit_time"], "exit_premium": r["exit_premium"],
                     "exit_reason": r["exit_reason"], "net_inr": fnum(r["net_inr"]),
                     "counted_in_preregistered_assembly": "YES", "counted_in_identical_leg_assembly": "YES",
                     "note": r["system_source"]})
for r in skill_log:
    same_dd = (r["date"], r["direction"]) in frame_dd
    same_leg = legkey(r) in frame_full
    nov_rows.append({"date": r["date"], "book": "SKILL (shadow)", "direction": r["direction"],
                     "strike": r["strike"], "entry_time": r["entry_time"], "entry_premium": r["entry_premium"],
                     "exit_time": r["exit_time"], "exit_premium": r["exit_premium"],
                     "exit_reason": r["exit_reason"], "net_inr": fnum(r["net_inr"]),
                     "counted_in_preregistered_assembly": "NO — same (date,direction) as a frame leg" if same_dd else "YES",
                     "counted_in_identical_leg_assembly": "NO — identical leg already in frame" if same_leg else "YES",
                     "note": "Skill V3 standalone"})
nov_rows.sort(key=lambda x: (x["date"], x["entry_time"]))

out = {
    "frame_total": frame_total, "frame_legs": len(frame),
    "skill_stream_legs": len(skill_rows), "skill_stream_total": sum(fnum(r["net_rs"]) for r in skill_rows),
    "volrix_stream_legs": len(volrix_rows), "volrix_stream_total": sum(fnum(r["net_rs"]) for r in volrix_rows),
    "increment_legs": len(incr), "increment_total": sum(fnum(r["net_rs"]) for r in incr),
    "increment_by_stream": {s: [sum(x["net_inr"] for x in assembly if x["stream"] == s),
                                sum(1 for x in assembly if x["stream"] == s)]
                            for s in ("SKILL", "VOLRIX", "SKILL+VOLRIX")},
    "dropped_overlap_legs": len(dropped), "dropped_overlap_total": dropped_total,
    "assembly_legs": len(assembly), "assembly_total": sum(x["net_inr"] for x in assembly),
    "configs": stats, "placebos": placebos,
    "sensitivity_all_components_dedupe": {"increment_legs": len(incr_all_keys),
        "increment_total": sum(fnum(r["net_rs"]) for r in incr_all_keys),
        "assembly_total": sens_total, "stats": sens_stats},
    "trading_days_janoct": len(trading_days),
    "daily_stats": {k: {kk: vv for kk, vv in v.items() if kk != "day_net"} for k, v in dstats.items()},
    "frame_day_net": dstats["B1 (Frame alone, DEC-S1)"]["day_net"],
    "v1_day_net": dstats["B1a (TUNED v1)"]["day_net"],
    "full_day_net": dstats["FULL (Frame+Skill+Volrix)"]["day_net"],
    "delay1_days_ge2000": delay1_ge2000,
    "overlap_diagnostic": {"legs_overlapping_frame_window": len(overlap), "legs": overlap},
    "nov_frame_total": sum(fnum(r["net_inr"]) for r in frame_log), "nov_frame_legs": len(frame_log),
    "nov_skill_total": sum(fnum(r["net_inr"]) for r in skill_log), "nov_skill_legs": len(skill_log),
    "nov_series_preregistered_dedupe": series(novA),
    "nov_series_identical_leg_dedupe": series(novB),
    "nov_v1_total": sum(fnum(r["net_inr"]) for r in v1_nov), "nov_v1_legs": len(v1_nov),
    "nov_primary_total": sum(fnum(r["net_inr"]) for r in primary_log), "nov_primary_legs": len(primary_log),
    "volrix_nov_trigger_changes": trig,
}
with open(TR / "daily_earner_nifty_results.json", "w") as fh: json.dump(out, fh, indent=1)
with open(TR / "daily_earner_nifty_janoct_trades.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(assembly[0].keys())); w.writeheader(); w.writerows(assembly)
with open(TR / "daily_earner_nifty_november_trades.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(nov_rows[0].keys())); w.writeheader(); w.writerows(nov_rows)
print(json.dumps({k: v for k, v in out.items() if "day_net" not in k}, indent=1))
