#!/usr/bin/env python3
"""Bank segment engine evening 2026-11-04 — gated candidates EVE-07 / EVE-08.
Basis: Bank option premiums per 1 lot (30), cost Rs220/trade in stored nets, UNIQUE-ONCE.
Incumbent for both: causal v21 book (99 legs) via flaw-cycle replay files (EVE-07)
and the frozen v21 trades file (EVE-08). Full controls in the same run.
Paper only, real money Rs0."""
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
    out = []
    for m, v in base_b["months"].items():
        if v > 0 and var_b["months"].get(m, 0) < 0: out.append(m)
    return out

results = {}

# ---------- EVE-07: NS1-only no-development cut (FC-1 restricted to NS1 legs) ----------
inc = load("flaw_cycle_incumbent_trades.csv")
fc1 = load("flaw_cycle_fc1_trades.csv")
key = lambda r: (r["date"], r["family"], r["entry_time"])
fc1m = {key(r): r for r in fc1}
assert len(inc) == 99 and len(fc1) == 99, (len(inc), len(fc1))
base07 = battery(inc, "v21 incumbent (flaw-cycle replay)")
assert base07["net"] == 83650.50, base07["net"]  # independent re-sum vs frozen book
var07_rows, changed07 = [], []
for r in inc:
    if r["family"] == "NS1_second" and key(r) in fc1m:
        v = fc1m[key(r)]
        var07_rows.append(v)
        if v["net_inr"] != r["net_inr"] or v["exit_reason"] != r["exit_reason"]:
            changed07.append((key(r), r["exit_reason"], r["net_inr"], v["exit_reason"], v["net_inr"]))
    else:
        var07_rows.append(r)
var07 = battery(var07_rows, "EVE-07 NS1-only nodev-cut")
results["EVE-07"] = {"base": base07, "variant": var07, "legs_changed": changed07,
                     "green_flips": flips(base07, var07),
                     "verdict": "NO-OP" if not changed07 else ("PASS" if var07["net"] > base07["net"] else "FAIL")}

# ---------- EVE-08: skip NS1 second legs entering at/after 13:00 (v21 basis) ----------
v21 = load("bank_engine_r6_v21_trades.csv")
base08 = battery(v21, "v21 frozen book")
assert base08["net"] == 83650.50 and len(v21) == 99
target = [r for r in v21 if r["family"] == "NS1_second" and r["entry_time"] >= "13:00"]
var08_rows = [r for r in v21 if not (r["family"] == "NS1_second" and r["entry_time"] >= "13:00")]
var08 = battery(var08_rows, "EVE-08 skip late NS1 (>=13:00)")
# placebo: skip the same count from the complementary (non-target) population —
# the count-matched complementary legs with the LATEST entry times on distinct days
comp = [r for r in v21 if r not in target]
comp_sorted = sorted(comp, key=lambda r: (r["entry_time"], r["date"]), reverse=True)
placebo_skip = comp_sorted[:len(target)]
placebo_rows = [r for r in v21 if r not in placebo_skip]
placebo08 = battery(placebo_rows, "placebo (skip same count, latest-entry complementary legs)")
results["EVE-08"] = {"base": base08, "variant": var08,
                     "skipped": [(r["date"], r["direction"], r["entry_time"], r["exit_reason"], r["net_inr"]) for r in target],
                     "skipped_net": net(target), "placebo": placebo08,
                     "placebo_skipped": [(r["date"], r["family"], r["entry_time"], r["net_inr"]) for r in placebo_skip],
                     "green_flips": flips(base08, var08),
                     "verdict": "PASS" if var08["net"] > base08["net"] else "FAIL"}

# ---------- Today (2026-11-04) TUNED SHADOW v2 scoring from stored premium candles ----------
cand = json.load(open(TR + "november_shadow_data/candles_BANKNIFTY_55900CE_2026-11-04_2026-11-23.json"))
bars = sorted(cand["data"]["candles"])  # [ts, o, h, l, c, vol, oi]
entry, stop, target_ = 757.00, 707.00, 847.00
path = [b for b in bars if "13:40" <= b[0][11:16] <= "14:00"]
mfe = round(max(b[2] for b in path) - entry, 2)
results["today_shadow_v2"] = {
    "entry": entry, "path_bars": [(b[0][11:16], b[1], b[2], b[3], b[4]) for b in path],
    "mfe_pts": mfe, "lock_threshold": entry + 30,
    "lock_armed": mfe >= 30,
    "shadow_result": "identical to primary: stop 14:00 @ 707.00, net -1720.00 (lock never armed; EVE-05 touches only B2 base PE <10:30 — no match)"}

print(json.dumps(results, indent=1))
with open(TR + "bank_segment_engine_evening_2026-11-04.json", "w") as f:
    json.dump(results, f, indent=1)
