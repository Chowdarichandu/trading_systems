#!/usr/bin/env python3
"""LADDER-BANK BUILD 2026-11-03 — reconstruction audit (STOP-RULE CHECK).

Owner-approved build: Bank v21 entries (bank_engine_r6_v21_trades.csv, 99 legs)
re-scored with the owner's spot-stage ladder exits, premium paths from
daily2leg/prem_bank.json, spot from daily2leg/spot.json.

Pre-registered stop rule (from the build brief): BEFORE scoring anything,
verify the premium reconstruction reproduces each leg's recorded entry
premium. If reconstruction fails on >10% of legs, STOP and report instead
of scoring.

Contract identification (two independent routes, cross-checked):
  A) blind strike search — monthly expiry (smallest store monthly expiry
     >= leg date), direction from the CSV; the strike whose entry-bar OPEN
     in prem_bank.json matches the recorded entry_premium.
  B) the audited pipeline's leg book (bank_r6_core.assemble6 lbk, the same
     reproduction flaw_cycle_run.py verified leg-for-leg vs the frozen
     regen CSV) gives strike+expiry directly; prem store bar checked.
Result: routes agree on every leg. Where the store contains the entry bar,
the match is EXACT (68/68 legs, |diff| <= 0.005, fill = entry bar open,
the harness's mode='open' convention).

Finding (original run): prem_bank.json contains NO pre-10:00 bars for any
2026 contract-day (10,226 contract-days checked, earliest first bar 10:00).
All 31 failures are legs entered 09:20-09:55. Failure rate 31/99 = 31.3%
> 10% threshold -> STOP. No ladder number is scored or quoted.

RE-AUDIT (2026-11-03, after the declared-source backfill —
ladder_bank_backfill_merge.py added 531 pre-10:00 bars, add-only, from
data/banknifty-2026-MM/option_5m.csv + the build_store candle caches):
this script is re-run unchanged in method; the hard-coded 68/31 counts of
the stopped run are replaced by the continuation gate — proceed to
scoring only if reconstruction is exact on 99/99 legs (or >=95% with
every failure individually explained and pre-10:00 coverage complete for
the rest). Original stopped-run outputs are preserved as
ladder_bank_reconstruction_audit_pre_backfill.{csv,json}.

Benchmark verification (this run): CSV net_inr re-sum = +83,650.50,
January 2026 = +22,748.00 — both match the frozen v21 figures exactly.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU

TR = Path.home() / "workspace/trading"
prem = json.load(open(TR / "daily2leg/prem_bank.json"))
legs = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))

# benchmark verification
total = round(sum(float(r["net_inr"]) for r in legs), 2)
jan = round(sum(float(r["net_inr"]) for r in legs if r["date"][:7] == "2026-01"), 2)
assert total == 83650.50 and jan == 22748.00, (total, jan)

# leg book (route B ground truth for strike/expiry)
pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99

MONTHLY = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28", "2026-05-26",
           "2026-06-30", "2026-07-28", "2026-08-25", "2026-09-29", "2026-10-27"]
byet = {}
for k, v in prem.items():
    e, s, t = k.split("|")
    byet.setdefault((e, t), {})[int(s)] = v

audit = []
for r in legs:
    key = (r["date"], r["direction"], r["entry_time"])
    L = lbk[key]
    exp_b, strike_b = L["expiry"], int(L["strike"])
    ep = float(r["entry_premium"])
    # route A: blind search
    exp_a = next(e for e in MONTHLY if r["date"] <= e)
    hits = [s for s, dates in byet.get((exp_a, r["direction"]), {}).items()
            if abs(dates.get(r["date"], {}).get(r["entry_time"], [1e9])[0] - ep) <= 0.55]
    # route B: lbk contract in store
    day = prem.get(f"{exp_b}|{strike_b}|{r['direction']}", {}).get(r["date"], {})
    bar = day.get(r["entry_time"])
    if bar is not None and abs(bar[0] - ep) <= 0.005:
        status, diff = "RECONSTRUCTED_EXACT", round(bar[0] - ep, 4)
    elif bar is not None:
        status, diff = "VALUE_MISMATCH", round(bar[0] - ep, 4)
    else:
        ts = sorted(day)
        status = "ENTRY_BAR_ABSENT"
        diff = None
        r["_first_bar"] = ts[0] if ts else None
        r["_nbars"] = len(ts)
    audit.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                      rep=r["rep"], entry_time=r["entry_time"], entry_premium=ep,
                      expiry=exp_b, strike=strike_b, status=status,
                      store_first_bar=r.get("_first_bar"), store_n_bars=r.get("_nbars"),
                      blind_search_strikes=hits, net_inr=float(r["net_inr"])))

ok = [a for a in audit if a["status"] == "RECONSTRUCTED_EXACT"]
bad = [a for a in audit if a["status"] != "RECONSTRUCTED_EXACT"]
assert all(a["blind_search_strikes"] == [a["strike"]] for a in ok)
gate_full = len(ok) == len(audit)
gate_95 = len(ok) >= 0.95 * len(audit)
print(f"RE-AUDIT: reconstructed exact {len(ok)}/{len(audit)}; "
      f"gate 99/99 = {gate_full}; gate >=95% = {gate_95}")
fam = {}
for a in bad: fam[a["family"]] = fam.get(a["family"], 0) + 1
bad_net = round(sum(a["net_inr"] for a in bad), 2)

with open(TR / "ladder_bank_reconstruction_audit.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(audit[0].keys()))
    w.writeheader()
    for a in audit: w.writerow(a)

summary = dict(
    build="LADDER-BANK (owner ladder exits on Bank v21 entries)",
    run="RE-AUDIT after declared-source backfill (531 pre-10:00 bars added, "
        "add-only; see ladder_bank_backfill_merge.py)",
    benchmark_csv_resum=total, benchmark_january=jan,
    legs_total=len(audit), reconstructed_exact=len(ok),
    failed=len(bad), failure_rate_pct=round(100.0 * len(bad) / len(audit), 1),
    gate_full_99_of_99=gate_full, gate_95pct=gate_95,
    failed_by_family=fam,
    failed_legs_net_inr=bad_net,
    value_mismatches=sum(1 for a in audit if a["status"] == "VALUE_MISMATCH"),
    verdict=("RE-AUDIT PASS — reconstruction exact on 99/99 legs; scoring "
             "unblocked." if gate_full else
             "RE-AUDIT NOT FULL — see failed legs; scoring gate per brief."),
)
(TR / "ladder_bank_reconstruction_audit.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
print("failed legs:")
for a in bad:
    print(a["date"], a["direction"], a["family"], a["entry_time"], a["expiry"], a["strike"])
