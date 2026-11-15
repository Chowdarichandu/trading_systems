#!/usr/bin/env python3
"""Bank segment engine evening 2026-11-05 — gated candidate EVE-09 + EVE-10 population check.
Basis: Bank option premiums per 1 lot (30), cost Rs220/trade in stored nets, UNIQUE-ONCE.
Incumbent: causal v21 book (99 legs), frozen trades file. Full controls in the same run.
Paper only, real money Rs0.
Context: 2026-11-05 primary = no-trade day (no new loser). EVE-09 attacks the remaining
end of the NS1 timing axis (EVE-08 tested >=13:00 and FAILED; <10:30 is mechanically
distinct). EVE-10 checks whether the blocked Skill-CE-solo population exists in stored
files at all before any scoring is attempted.
"""
import csv, json
from collections import defaultdict

TR = "/home/hatch/workspace/trading/"

def load(path):
    return list(csv.DictReader(open(TR + path)))

def net(rows): return round(sum(float(r["net_inr"]) for r in rows), 2)

def battery(rows, label):
    months = defaultdict(float)
    for r in rows: months[r["date"][:7]] += float(r["net_inr"])
    h1 = round(sum(float(r["net_inr"]) for r in rows if r["date"] <= "2026-05-31"), 2)
    h2 = round(sum(float(r["net_inr"]) for r in rows if r["date"] >= "2026-06-01"), 2)
    srt = sorted(rows, key=lambda r: -float(r["net_inr"]))
    extop3 = round(net(rows) - sum(float(r["net_inr"]) for r in srt[:3]), 2)
    return {"label": label, "n": len(rows), "net": net(rows), "halves": {"H1": h1, "H2": h2},
            "months": {k: round(v, 2) for k, v in sorted(months.items())}, "ex_top3": extop3}

def flips(base_b, var_b):
    return [m for m, v in base_b["months"].items() if v > 0 and var_b["months"].get(m, 0) < 0]

results = {}

# ---------- EVE-09: skip NS1 second legs entering before 10:30 (v21 basis) ----------
v21 = load("bank_engine_r6_v21_trades.csv")
base = battery(v21, "v21 frozen book")
assert base["net"] == 83650.50 and len(v21) == 99, (base["net"], len(v21))  # independent re-sum
target = [r for r in v21 if r["family"] == "NS1_second" and r["entry_time"] < "10:30"]
var_rows = [r for r in v21 if r not in target]
var = battery(var_rows, "EVE-09 skip early NS1 (<10:30)")
# placebo: skip the same count of NS1 legs, chosen as the LATEST-entry NS1 legs
ns1 = [r for r in v21 if r["family"] == "NS1_second"]
ns1_latest = sorted(ns1, key=lambda r: (r["entry_time"], r["date"]), reverse=True)[:len(target)]
placebo_rows = [r for r in v21 if r not in ns1_latest]
placebo = battery(placebo_rows, "placebo (skip same count, latest-entry NS1 legs)")
results["EVE-09"] = {
    "base": base, "variant": var,
    "skipped": [(r["date"], r["direction"], r["entry_time"], r["exit_reason"], r["net_inr"]) for r in target],
    "skipped_net": net(target), "placebo": placebo,
    "placebo_skipped": [(r["date"], r["entry_time"], r["net_inr"]) for r in ns1_latest],
    "green_flips": flips(base, var),
    "timing_audit": "skip input is entry_time, known at entry — 0 violations by construction",
    "verdict": "PASS" if (var["net"] > base["net"] and var["net"] > placebo["net"]
                          and var["halves"]["H1"] >= 0 and var["halves"]["H2"] >= 0
                          and not flips(base, var) and var["ex_top3"] > 0) else "FAIL"}

# ---------- EVE-10: late Skill-CE-solo admission — population check before scoring ----------
b2 = load("historical_proof_bank_B2_trades.csv")
ce_solo_in_b2 = [r for r in b2 if r.get("direction") == "CE"]
results["EVE-10"] = {
    "b2_pool_legs": len(b2),
    "b2_pool_columns": list(b2[0].keys()) if b2 else [],
    "note": "The stored B2 pool holds only legs the frozen B2 rule KEPT; blocked Skill V3 CE "
            "solo keys were never logged as trades in any stored Bank file, so the admission "
            "population for a late-CE-solo candidate does not exist in the stored record.",
    "verdict": "NOT TESTABLE — no score quoted"}

# ---------- 2026-11-04 S3-R1 winner (SHADOW v21 + v22): MFE / give-back from stored candles ----------
cand = json.load(open(TR + "november_shadow_data/candles_BANKNIFTY_55800PE_2026-11-04_2026-11-23.json"))
bars = sorted(cand["data"]["candles"])  # [ts, o, h, l, c, vol, oi]
entry = 715.30
path = [b for b in bars if "09:55" <= b[0][11:16] <= "10:25"]
results["nov4_s3_winner"] = {
    "entry": entry, "exit": 805.30, "exit_reason": "runner_stop",
    "mfe_pts": round(max(b[2] for b in path) - entry, 2),
    "mae_pts": round(min(b[3] for b in path) - entry, 2),
    "path_bars": [(b[0][11:16], b[1], b[2], b[3], b[4]) for b in path]}

# ---------- 2026-11-05 TUNED SHADOW v2 would-be ----------
results["today_tuned_shadow_v2"] = {
    "primary_legs_today": 0,
    "note": "Primary frame produced no B2 base leg and no NS1 second leg on 2026-11-05 "
            "(only key: Skill V3 CE solo 11:15/11:20, blocked by the frozen Skill-CE block, "
            "which v2 does not alter; NS1: S1 base exited by target 11:30, no fresh OR "
            "crossing after). TUNED SHADOW v2 therefore also has no trade today."}

print(json.dumps(results, indent=1))
with open(TR + "bank_segment_engine_evening_2026-11-05.json", "w") as f:
    json.dump(results, f, indent=1)
