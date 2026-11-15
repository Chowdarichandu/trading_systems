#!/usr/bin/env python3
"""BANK 2000/DAY PROGRAMME — scoring run (2026-11-13).
Pre-registration: bank_2000_programme_2026-11-13.md §0 (written before this ran).
Parents are frozen ledgers, read-only. Outputs: per-config trade CSVs,
bank_2000_results.json, and a results block printed for the report.
"""
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace" / "trading"
SEED = 42
N_DRAWS = 2000

# ---------- parents ----------
stack_raw = list(csv.DictReader(open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
legacy_raw = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))

def s_leg(r):
    return {"date": r["date"], "direction": r["direction"], "family": r["family"],
            "rep": r.get("rep", ""), "entry_time": r["entry_time"],
            "entry_premium": float(r["entry_premium"]), "exit_time": "", "exit_premium": "",
            "exit_reason": "", "net_inr": float(r["x1_net"]), "parent": "STACK"}
def l_leg(r):
    return {"date": r["date"], "direction": r["direction"], "family": r["family"],
            "rep": r.get("rep", ""), "entry_time": r["entry_time"],
            "entry_premium": float(r["entry_premium"]), "exit_time": r["exit_time"],
            "exit_premium": float(r["exit_premium"]), "exit_reason": r["exit_reason"],
            "net_inr": float(r["net_inr"]), "parent": "LEGACY"}

STACK = [s_leg(r) for r in stack_raw]
LEGACY = [l_leg(r) for r in legacy_raw]
stack_total = sum(l["net_inr"] for l in STACK)
legacy_total = sum(l["net_inr"] for l in LEGACY)
assert len(STACK) == 111 and abs(stack_total - 127351.50) < 0.01, (len(STACK), stack_total)
assert len(LEGACY) == 99 and abs(legacy_total - 83650.50) < 0.01, (len(LEGACY), legacy_total)
print(f"ANCHORS OK: STACK 111 legs {stack_total:+.2f} · LEGACY 99 legs {legacy_total:+.2f}")

# ---------- trading-day calendar (205) ----------
daily = list(csv.DictReader(open(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv")))
DAYS = sorted({r["date"][:10] for r in daily if "2026-01-01" <= r["date"][:10] <= "2026-10-31"})
assert len(DAYS) == 205, len(DAYS)
print(f"CALENDAR OK: {len(DAYS)} trading days Jan-Oct 2026")

# ---------- union pool (dedupe: identity key, STACK copy kept) ----------
def key(l): return (l["date"], l["direction"], l["entry_time"], l["entry_premium"])
smap = {key(l): l for l in STACK}
lmap = {key(l): l for l in LEGACY}
collisions = sorted(set(smap) & set(lmap))
net_mismatch = [(k, smap[k]["net_inr"], lmap[k]["net_inr"]) for k in collisions
                if abs(smap[k]["net_inr"] - lmap[k]["net_inr"]) > 0.01]
UNION = list(STACK) + [l for l in LEGACY if key(l) not in smap]
union_total = sum(l["net_inr"] for l in UNION)
print(f"UNION: {len(UNION)} legs {union_total:+.2f} · collisions {len(collisions)} · net-mismatch {len(net_mismatch)}")
for k, a, b in net_mismatch: print("  MISMATCH", k, "stack", a, "legacy", b)

# ---------- configurations (pre-registered list, nothing else) ----------
CONFIGS = {
    "PB1_stack_lt500":  [l for l in STACK if l["entry_premium"] < 500],
    "PB2_stack_lt650":  [l for l in STACK if l["entry_premium"] < 650],
    "PB0_legacy_lt500": [l for l in LEGACY if l["entry_premium"] < 500],
    "PB3_union_lt500":  [l for l in UNION if l["entry_premium"] < 500],
    "PB4_union_lt650":  [l for l in UNION if l["entry_premium"] < 650],
    "U1_union_all":     list(UNION),
}
PARENT_POOL = {"PB1_stack_lt500": STACK, "PB2_stack_lt650": STACK,
               "PB0_legacy_lt500": LEGACY, "PB3_union_lt500": UNION,
               "PB4_union_lt650": UNION, "U1_union_all": UNION}

# ---------- metrics + gate ----------
def month_table(legs):
    m = defaultdict(float)
    for l in legs: m[l["date"][:7]] += l["net_inr"]
    return {k: round(m.get(k, 0.0), 2) for k in
            ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]}

def day_series(legs):
    d = defaultdict(float); traded = set()
    for l in legs: d[l["date"]] += l["net_inr"]; traded.add(l["date"])
    return [round(d.get(day, 0.0), 2) for day in DAYS], traded

def score(name, legs):
    legs = sorted(legs, key=lambda l: (l["date"], l["entry_time"]))
    total = sum(l["net_inr"] for l in legs)
    nets = sorted((l["net_inr"] for l in legs), reverse=True)
    ex_top3 = total - sum(nets[:3])
    months = month_table(legs)
    red_months = [k for k, v in months.items() if v < 0]
    worst_month = min(months, key=months.get)
    h1 = sum(v for k, v in months.items() if k <= "2026-05")
    h2 = sum(v for k, v in months.items() if k >= "2026-06")
    days, traded = day_series(legs)
    sdays = sorted(days)
    worst_decile = sdays[: max(1, len(sdays) // 10)]
    wr = (sum(1 for l in legs if l["net_inr"] > 0) / len(legs) * 100) if legs else 0.0
    out = {"legs": len(legs), "wr_pct": round(wr, 1), "total": round(total, 2),
           "per_day": round(total / 205, 2),
           "gap_to_2000_per_day": round(2000 - total / 205, 2),
           "months": months, "red_months": red_months, "worst_month": worst_month,
           "h1": round(h1, 2), "h2": round(h2, 2), "ex_top3": round(ex_top3, 2),
           "pct_days_ge2000": round(sum(1 for v in days if v >= 2000) / 205 * 100, 1),
           "days_ge2000": sum(1 for v in days if v >= 2000),
           "pct_days_pos": round(sum(1 for v in days if v > 0) / 205 * 100, 1),
           "pct_zero_trade_days": round((205 - len(traded)) / 205 * 100, 1),
           "median_day": round(statistics.median(days), 2),
           "worst_decile_mean_day": round(sum(worst_decile) / len(worst_decile), 2),
           "worst_day": round(min(days), 2), "best_day": round(max(days), 2)}
    # gate
    fails = []
    if not total > 0: fails.append("C total<=0")
    if not (h1 > 0 and h2 > 0): fails.append(f"D halves (H1 {h1:+.2f} / H2 {h2:+.2f})")
    if not ex_top3 > 0: fails.append(f"E ex-top-3 {ex_top3:+.2f}")
    if len(red_months) > 4: fails.append(f"F red months {len(red_months)}")
    pool = PARENT_POOL[name]
    if name == "U1_union_all":
        if not (total > stack_total and total > legacy_total):
            fails.append(f"G/U1 total {total:+.2f} does not beat both parents "
                         f"(stack {stack_total:+.2f}, legacy {legacy_total:+.2f})")
        out["placebo"] = "n/a (100% density); binding leg = beat-both-parents"
    else:
        rng = random.Random(SEED)
        pool_nets = [l["net_inr"] for l in pool]; k = len(legs)
        draws = sorted(sum(rng.sample(pool_nets, k)) for _ in range(N_DRAWS))
        p95 = draws[int(0.95 * N_DRAWS)]
        pct = sum(1 for d in draws if d < total) / N_DRAWS * 100
        out["placebo"] = {"parent_pool_legs": len(pool), "k": k, "p95": round(p95, 2),
                          "config_pct_rank": round(pct, 1)}
        if not total > p95: fails.append(f"G random-density placebo (total {total:+.2f} <= p95 {p95:+.2f})")
    out["gate"] = "PASS" if not fails else "FAIL"
    out["gate_fails"] = fails
    out["legs_sorted"] = legs
    return out

results = {}
for name, legs in CONFIGS.items():
    results[name] = score(name, legs)
    r = results[name]
    print(f"\n{name}: {r['legs']} legs WR {r['wr_pct']}% total {r['total']:+.2f} "
          f"({r['per_day']:+.2f}/day) days>=2000 {r['days_ge2000']} ({r['pct_days_ge2000']}%) "
          f"gate {r['gate']} {r['gate_fails']}")

# adjacent-band descriptive (reported, not a gate leg)
for nm, pool in [("STACK", STACK), ("LEGACY", LEGACY)]:
    mid = [l for l in pool if 500 <= l["entry_premium"] < 750]
    print(f"ADJACENT BAND {nm} 500-750: {len(mid)} legs {sum(l['net_inr'] for l in mid):+.2f}")

# ---------- write trade CSVs ----------
FIELDS = ["date", "direction", "family", "rep", "entry_time", "entry_premium",
          "exit_time", "exit_premium", "exit_reason", "net_inr", "parent"]
for name, r in results.items():
    p = TR / f"bank_2000_{name}_trades.csv"
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for l in r["legs_sorted"]: w.writerow({k: l[k] for k in FIELDS})

# ---------- November counterfactual (Nov 2-12 frozen logs) ----------
stack_nov = [r for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv"))
             if r["date"] <= "2026-11-12" and r["net_inr"]]
legacy_nov = [r for r in csv.DictReader(open(TR / "november_paper_bank_log.csv"))
              if r["date"] <= "2026-11-12" and r.get("channel") == "PRIMARY" and r["net_inr"]]
def nov_leg(r, parent):
    return {"date": r["date"], "direction": r["direction"], "entry_time": r["entry_time"],
            "entry_premium": float(r["entry_premium"]), "net_inr": float(r["net_inr"]), "parent": parent}
SN = [nov_leg(r, "STACK") for r in stack_nov]
LN = [nov_leg(r, "LEGACY") for r in legacy_nov]
print(f"\nNOVEMBER parents: STACK {len(SN)} legs {sum(l['net_inr'] for l in SN):+.2f} · "
      f"LEGACY {len(LN)} legs {sum(l['net_inr'] for l in LN):+.2f}")
smapN = {key(l): l for l in SN}
UNION_N = SN + [l for l in LN if key(l) not in smapN]
NOV_DAYS = ["2026-11-02","2026-11-03","2026-11-04","2026-11-05","2026-11-06",
            "2026-11-09","2026-11-11","2026-11-12"]
NOV_CONFIGS = {
    "PB1_stack_lt500": [l for l in SN if l["entry_premium"] < 500],
    "PB2_stack_lt650": [l for l in SN if l["entry_premium"] < 650],
    "PB0_legacy_lt500": [l for l in LN if l["entry_premium"] < 500],
    "PB3_union_lt500": [l for l in UNION_N if l["entry_premium"] < 500],
    "PB4_union_lt650": [l for l in UNION_N if l["entry_premium"] < 650],
    "U1_union_all": list(UNION_N),
    "REF_stack_all": list(SN), "REF_legacy_all": list(LN),
}
nov_out = {}
for name, legs in NOV_CONFIGS.items():
    d = defaultdict(float)
    for l in legs: d[l["date"]] += l["net_inr"]
    cum, line = 0.0, []
    for day in NOV_DAYS:
        cum += d.get(day, 0.0); line.append(round(cum, 2))
    nov_out[name] = {"legs": len(legs), "total": round(sum(l["net_inr"] for l in legs), 2),
                     "cumulative_by_day": dict(zip(NOV_DAYS, line)),
                     "leg_detail": [{k: l[k] for k in ("date","direction","entry_time","entry_premium","net_inr","parent")} for l in legs]}
    print(f"NOV {name}: {len(legs)} legs total {nov_out[name]['total']:+.2f} cum {line}")

# ---------- independent re-sum of written CSVs ----------
resum = {}
for name in CONFIGS:
    rows = list(csv.DictReader(open(TR / f"bank_2000_{name}_trades.csv")))
    resum[name] = round(sum(float(r["net_inr"]) for r in rows), 2)
    assert resum[name] == results[name]["total"], (name, resum[name], results[name]["total"])
print("\nRE-SUM: all config CSVs match scored totals to the paisa:", resum)

dump = {"anchors": {"stack": stack_total, "legacy": legacy_total, "union": union_total,
                    "collisions": len(collisions), "net_mismatch": net_mismatch},
        "configs": {k: {kk: vv for kk, vv in v.items() if kk != "legs_sorted"}
                    for k, v in results.items()},
        "november": nov_out, "resum": resum}
with open(TR / "bank_2000_results.json", "w") as fh: json.dump(dump, fh, indent=1)
print("WROTE bank_2000_results.json + 6 trade CSVs")
