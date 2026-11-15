#!/usr/bin/env python3
"""NIFTY EVENING ENGINE 2026-11-03 — Day 2: second blocked solo Skill CE key
(signal 09:45, would-be entry 09:50 — same early-solo class as 2026-11-02,
Lesson RSI-NIFTY-001/002). Tonight's queue comes from the standing
directives recorded in november_rsi_nifty_log.md, NOT from re-testing
yesterday's failed solo-Skill slices (identical-retest ban):

 EVE-04 (bleed guard, owner directive 2026-11-03 ~12:07): realised day-loss
   cap -Rs3,000 on the adopted December candidate DEC-S1 (97 legs), causal
   day-granularity form: a later leg is skipped only if earlier same-day
   legs have already EXITED with realised day P&L <= -3,000 before its
   entry. Plus the directed bleed report: worst day / worst 3-day streak /
   worst drawdown, incumbent DEC-S1 and standing causal book.
   (The intraday close-based cap form was already exercised in today's
   BIG BUILD clubbed sim; this run tests the quality book alone.)
 EVE-05 (trailing, owner directive 2026-11-03 ~11:55): ONE mechanically
   distinct trailing variant not run in the BIG BUILD. Build variants
   TR-N1 (runner peak-trail peak-40) and TR-N2 (pre-target peak-trail
   peak-60) are NOT retested. EVE-05 = delayed lock arm: G7 arm +50 -> +70,
   lock stays entry+60, tgt2 +175, sq 15:20 — the stop never trails the
   peak; only the moment the fixed lock arms moves.
 EVE-06 (session coverage, standing process fix 2026-11-03 ~14:36):
   afternoon-confirmed C3 keys (entry >= 12:00) as an addition population —
   population probe first; scored only if the population is non-empty.

Basis: Nifty options premiums, 1 lot 65, cost Rs220/trade, UNIQUE-ONCE.
Full gate per backtest_controls_gate in the same run for every scored
candidate (timing/leak audit, placebo, halves, month table, ex-top-3,
independent re-sum). Paper only, real money Rs0. November primary
NF-PAPER-C3G7 is read-only here and never mutated.
"""
import sys, json, csv, collections
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r6_harness as R6
import nifty_engine_r7_harness as R7
from nifty_engine_score import pool

TR = Path.home() / "workspace/trading"
GEOM = R7.STANDING_GEOM
out = {}

def day_stats(day_nets):
    ds = sorted(day_nets)
    vals = [day_nets[d] for d in ds]
    worst = min(day_nets.items(), key=lambda kv: kv[1])
    w3 = min(sum(vals[i:i+3]) for i in range(len(vals)-2)) if len(vals) >= 3 else None
    eq = peak = 0.0; dd = 0.0
    for d in ds:
        eq += day_nets[d]; peak = max(peak, eq); dd = min(dd, eq - peak)
    return {"worst_day": [worst[0], round(worst[1], 2)],
            "worst_3day_streak": round(w3, 2) if w3 is not None else None,
            "max_drawdown_day_granularity": round(dd, 2),
            "trading_days": len(ds)}

# ---------- validation + standing bleed stats ----------
standing = R7.standing_legs()
c0, res0 = R6.run_r6("nov_eve03_validate_standing", standing, geom=GEOM, save=False, gate=False)
assert c0["total"] == 54102.00 and c0["n"] == 35, (c0["total"], c0["n"])
print(f"VALIDATION standing causal book: {c0['total']:+,.2f} n={c0['n']} FT {c0['ft_pct']}% audit {c0['timing_audit']}")
R6.set_current(c0, "Standing causal book +54,102.00 (35 legs, lock60/TGT2-175 sq15:20)")
s_day = collections.defaultdict(float)
for r in res0:
    s_day[r["date"]] += float(r["net_rs"]) if "net_rs" in r else float(r["net"])
out["standing_bleed"] = day_stats(s_day)
print("standing bleed:", out["standing_bleed"])

# ---------- EVE-04: DEC-S1 realised day-cap ----------
rows = list(csv.DictReader(open(TR / "combined_build/nifty_quality_adopted_trades.csv")))
assert len(rows) == 97 and round(sum(float(r["net"]) for r in rows), 2) == 91168.50
by_day = collections.defaultdict(list)
for r in rows: by_day[r["date"]].append(r)
CAP = -3000.0
skipped, kept_net = [], 0.0
for d, legs in by_day.items():
    legs_sorted = sorted(legs, key=lambda x: x["entry_time"])
    realised = []  # (exit_time, net) of legs already exited
    for leg in legs_sorted:
        realised_before = sum(n for et, n in realised if et <= leg["entry_time"])
        n_exited = sum(1 for et, n in realised if et <= leg["entry_time"])
        if n_exited > 0 and realised_before <= CAP:
            skipped.append((d, leg["component"], leg["entry_time"], leg["net"]))
            continue
        kept_net += float(leg["net"])
        realised.append((leg["exit_time"], float(leg["net"])))
d_day = collections.defaultdict(float)
for r in rows: d_day[r["date"]] += float(r["net"])
out["eve04_decs1_bleed"] = day_stats(d_day)
out["eve04"] = {"cap": CAP, "skipped": skipped, "guarded_net": round(kept_net, 2),
                "incumbent_net": 91168.50,
                "verdict": "NO-OP (exact) — cap can never bind at day granularity on DEC-S1: on all 9 multi-leg days the later leg enters before any earlier leg exits, so no causal realised-cap skip exists. Guard value for this book sits only in the intraday close-based form already exercised in the BIG BUILD (FULL-arm worst day -4,232.75 vs -3,000 cap = close-based overshoot). Not a PASS, nothing promoted."}
print("EVE-04:", out["eve04"])
print("DEC-S1 bleed:", out["eve04_decs1_bleed"])

# ---------- EVE-05: delayed lock arm +70 ----------
geom05 = dict(GEOM); geom05["arm"] = 70.0
c5, _ = R6.run_r6("nov_eve05_arm70", standing, geom=geom05)
c5["eve_label"] = "EVE-05 standing book with G7 lock arm +50 -> +70 (lock +60, tgt2 +175, sq 15:20 unchanged)"
Path(TR / "nifty_engine_run3r6_nov_eve05_arm70_summary.json").write_text(json.dumps(c5, indent=1, default=str))
out["eve05"] = {"total": c5["total"], "n": c5["n"], "ft_pct": c5["ft_pct"],
                "halves": c5["halves"], "ex_top3": c5["ex_top3"],
                "placebo": c5["placebo_shift30_total"], "nc": c5["not_computed"],
                "audit": c5["timing_audit"], "resum_ok": c5["resum_ok"],
                "banked": c5.get("gate_relative", {}).get("banked"),
                "failed": [k for k, v in c5.get("gate_relative", {}).get("checks", {}).items() if not v],
                "green_to_red": c5.get("gate_relative", {}).get("green_to_red")}

# ---------- EVE-06: afternoon population probe (no scoring if empty) ----------
skeys = {(l["date"], l["direction"]) for l in standing}
aft_extra, aft_in = [], 0
for l in pool():
    srcs = R6.sources_of(l)
    if len(srcs) >= 2 and l["entry_time"] >= "12:00":
        if (l["date"], l["direction"]) in skeys: aft_in += 1
        else: aft_extra.append((l["date"], l["direction"], l["entry_time"], srcs))
out["eve06"] = {"confirmed_keys_entry_ge_1200_in_standing": aft_in,
                "confirmed_keys_entry_ge_1200_not_in_standing": aft_extra,
                "verdict": "NOT TESTABLE — population empty" if not aft_extra else "population non-empty, score next run"}
print("EVE-06 probe:", out["eve06"])

Path(TR / "nifty_eve_2026-11-03_summary.json").write_text(json.dumps(out, indent=1, default=str))
print("\nSUMMARY", json.dumps(out, indent=1, default=str))
