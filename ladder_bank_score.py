#!/usr/bin/env python3
"""LADDER-BANK scorer + full gate (2026-11-03).

Locked design (owner-approved, Bank first): the 99 causal Bank v21 entries
(bank_engine_r6_v21_trades.csv) unchanged; exits replaced by the owner's
spot-stage ladder, 5-min closes, premium path from daily2leg/prem_bank.json
(post-backfill), spot from daily2leg/spot.json.

PRIMARY exits:
  - entry premium = OPEN of the entry bar (store; audited == recorded).
  - entry_spot = OPEN of the spot bar at entry_time.
  - favourable move at a bar = sign x (spot_close - entry_spot),
    sign +1 CE / -1 PE.
  - stages on spot closes: T1 +30 -> floor entry+5; T2 +58 -> entry+15;
    T3 +82 -> entry+25; T4 +100 -> EXIT at that bar's premium close.
    Floors ratchet only (highest stage reached governs).
  - before any stage: hard stop floor = entry - 20 (premium close <= floor
    exits at that close). Floors are close-based: a gap-through close can
    realise below the floor level (reported as-is).
  - checks run on every bar from the entry bar's close through 15:10;
    T4 check precedes the floor check on the same bar; no exit -> square
    off at the close of the 15:10 bar.
  - net = (exit - entry) x 30 - 220 per leg (v21 money basis: lot 30,
    cost Rs 220/trade — verified against the frozen CSV nets).

Sensitivities (non-primary, pre-registered): stop -15 / -25; locks -5
(0/10/20) / locks +5 (10/20/30). B2-subset robustness: family == BASE
(61 legs — the B2 pool as carried into v21: Skill V3 CE blocked, no
Skill-solo <=09:55 legs; verified 0 Skill CE and 0 Skill <=09:55 in BASE).
Placebos (primary params): flipped direction (opposite type, same
strike/expiry/date/time, mirrored ladder) and shifted entry +60 min
(same contract). NOT_COMPUTED legs are counted and named, never dropped
silently.
Gate in the same run: timing audit (incl. an independent second
implementation of the exit logic cross-checked leg-for-leg), halves,
month table, ex-top-3 days and legs, worst day / worst 3-leg-days /
worst drawdown, stage-reach anatomy, independent re-sum of every
headline from the written trade file.
"""
import csv, json
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU

TR = Path.home() / "workspace/trading"
LOT, COST = 30, 220.0
STAGES = (30, 58, 82, 100)
SQ = "15:10"

prem = json.load(open(TR / "daily2leg/prem_bank.json"))
spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
spot = {d: {b[0]: b for b in bars} for d, bars in spot_raw.items()}
legs = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))
pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99

ENTRIES = []
for r in legs:
    L = lbk[(r["date"], r["direction"], r["entry_time"])]
    ENTRIES.append(dict(date=r["date"], direction=r["direction"],
                        family=r["family"], rep=r["rep"],
                        entry_time=r["entry_time"],
                        recorded_premium=float(r["entry_premium"]),
                        expiry=L["expiry"], strike=int(L["strike"]),
                        original_net=float(r["net_inr"])))


def daybars(expiry, strike, typ, date):
    return prem.get(f"{expiry}|{strike}|{typ}", {}).get(date, {})


def simulate(date, direction, expiry, strike, entry_time, stop_pts, locks,
             typ_override=None, entry_time_override=None):
    """One ladder trade. Returns dict or None (NOT_COMPUTED) with reason."""
    typ = typ_override or direction
    et = entry_time_override or entry_time
    bars = daybars(expiry, strike, typ, date)
    if et not in bars:
        return None, f"entry bar {et} absent for {expiry}|{strike}|{typ} {date}"
    entry = bars[et][0]
    sb = spot[date]
    if et not in sb:
        return None, f"spot bar {et} absent {date}"
    entry_spot = sb[et][1]
    sign = 1 if direction == "CE" else -1
    floor0 = entry - stop_pts
    times = sorted(t for t in bars if et <= t <= SQ)
    if not times or times[-1] != SQ and SQ not in bars:
        return None, f"no path to {SQ} for {expiry}|{strike}|{typ} {date}"
    highest = 0
    for t in times:
        pclose = bars[t][3]
        fav = sign * (sb[t][4] - entry_spot)
        stage_now = sum(1 for s in STAGES if fav >= s)
        if stage_now > highest:
            highest = stage_now
        if highest == 4:
            return (dict(entry=entry, entry_spot=entry_spot, exit_time=t,
                         exit_premium=pclose, exit_reason="T4_EXIT",
                         highest_stage=4,
                         net=round((pclose - entry) * LOT - COST, 2))), None
        floor = floor0 if highest == 0 else entry + locks[highest - 1]
        if pclose <= floor:
            reason = "HARD_STOP" if highest == 0 else f"LOCK_FLOOR_T{highest}"
            return (dict(entry=entry, entry_spot=entry_spot, exit_time=t,
                         exit_premium=pclose, exit_reason=reason,
                         highest_stage=highest,
                         net=round((pclose - entry) * LOT - COST, 2))), None
    pclose = bars[SQ][3]
    return (dict(entry=entry, entry_spot=entry_spot, exit_time=SQ,
                 exit_premium=pclose, exit_reason="SQUARE_OFF",
                 highest_stage=highest,
                 net=round((pclose - entry) * LOT - COST, 2))), None


def simulate_v2(date, direction, expiry, strike, entry_time, stop_pts, locks):
    """Independent re-implementation for the timing audit: build the full
    stage timeline first, then walk it for the exit."""
    bars = daybars(expiry, strike, direction, date)
    entry = bars[entry_time][0]
    sb = spot[date]
    entry_spot = sb[entry_time][1]
    sign = 1 if direction == "CE" else -1
    times = sorted(t for t in bars if entry_time <= t <= SQ)
    timeline = []
    run_max = 0
    for t in times:
        fav = sign * (sb[t][4] - entry_spot)
        run_max = max(run_max, sum(1 for s in STAGES if fav >= s))
        timeline.append((t, bars[t][3], run_max))
    for t, pclose, h in timeline:
        if h == 4:
            return t, pclose, "T4_EXIT", 4, round((pclose - entry) * LOT - COST, 2)
        floor = entry - stop_pts if h == 0 else entry + locks[h - 1]
        if pclose <= floor:
            return t, pclose, ("HARD_STOP" if h == 0 else f"LOCK_FLOOR_T{h}"), h, \
                round((pclose - entry) * LOT - COST, 2)
    return SQ, bars[SQ][3], "SQUARE_OFF", timeline[-1][2], \
        round((bars[SQ][3] - entry) * LOT - COST, 2)


def add60(hm):
    m = int(hm[:2]) * 60 + int(hm[3:]) + 60
    return f"{m // 60:02d}:{m % 60:02d}"


def aggregates(rows):
    """rows: list of dicts with date + net (+ original_net optional)."""
    total = round(sum(r["net"] for r in rows), 2)
    months = {}
    for m in sorted({r["date"][:7] for r in rows}):
        months[m] = round(sum(r["net"] for r in rows if r["date"][:7] == m), 2)
    h1 = round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2)
    h2 = round(total - h1, 2)
    leg_sorted = sorted((r["net"] for r in rows), reverse=True)
    ex_top3_legs = round(total - sum(leg_sorted[:3]), 2)
    byday = defaultdict(float)
    for r in rows:
        byday[r["date"]] += r["net"]
    days = sorted(byday)
    daynets = [round(byday[d], 2) for d in days]
    day_sorted = sorted(daynets, reverse=True)
    ex_top3_days = round(sum(daynets) - sum(day_sorted[:3]), 2)
    worst_day = (days[int(min(range(len(days)), key=lambda i: daynets[i]))],
                 min(daynets))
    worst3 = min(sum(daynets[i:i + 3]) for i in range(len(daynets) - 2))
    cum, peak, dd = 0.0, 0.0, 0.0
    for v in daynets:
        cum += v
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return dict(legs=len(rows), total=total,
                mean_per_leg=round(total / len(rows), 2) if rows else None,
                win_rate_pct=round(100.0 * sum(1 for r in rows if r["net"] > 0)
                                   / len(rows), 1) if rows else None,
                months=months, halves=dict(H1_Jan_May=h1, H2_Jun_Oct=h2),
                ex_top3_legs=ex_top3_legs, ex_top3_days=ex_top3_days,
                days=len(days),
                positive_days_pct=round(100.0 * sum(1 for v in daynets if v > 0)
                                        / len(daynets), 1),
                worst_day=dict(date=worst_day[0], net=worst_day[1]),
                worst_3_leg_days=round(worst3, 2),
                worst_drawdown=round(dd, 2))


PRIMARY = dict(stop=20, locks=(5, 15, 25))
VARIANTS = {
    "PRIMARY_stop20_locks5_15_25": PRIMARY,
    "SENS_stop15": dict(stop=15, locks=(5, 15, 25)),
    "SENS_stop25": dict(stop=25, locks=(5, 15, 25)),
    "SENS_locks_minus5": dict(stop=20, locks=(0, 10, 20)),
    "SENS_locks_plus5": dict(stop=20, locks=(10, 20, 30)),
}

results = {}
primary_rows = []
for name, prm in VARIANTS.items():
    rows, ncs = [], []
    for e in ENTRIES:
        out, why = simulate(e["date"], e["direction"], e["expiry"],
                            e["strike"], e["entry_time"], prm["stop"],
                            prm["locks"])
        if out is None:
            ncs.append((e["date"], e["direction"], e["entry_time"], why))
            continue
        rows.append(dict(date=e["date"], direction=e["direction"],
                         family=e["family"], rep=e["rep"], expiry=e["expiry"],
                         strike=e["strike"], entry_time=e["entry_time"],
                         entry_premium=out["entry"], entry_spot=out["entry_spot"],
                         highest_stage=out["highest_stage"],
                         exit_time=out["exit_time"],
                         exit_premium=out["exit_premium"],
                         exit_reason=out["exit_reason"], net=out["net"],
                         original_net=e["original_net"],
                         delta_vs_original=round(out["net"] - e["original_net"], 2)))
    results[name] = dict(params=dict(stop=prm["stop"], locks=list(prm["locks"])),
                         aggregates=aggregates(rows), not_computed=ncs)
    if name.startswith("PRIMARY"):
        primary_rows = rows

# ---- timing audit + independent cross-check on the primary ------------------
audit_fail = []
for e, r in zip([e for e in ENTRIES], primary_rows):
    bars = daybars(e["expiry"], e["strike"], e["direction"], e["date"])
    if abs(r["entry_premium"] - e["recorded_premium"]) > 0.005:
        audit_fail.append((e["date"], "entry premium != recorded"))
    if bars[r["exit_time"]][3] != r["exit_premium"]:
        audit_fail.append((e["date"], "exit premium != store close"))
    if r["exit_time"] < e["entry_time"] or r["exit_time"] > SQ:
        audit_fail.append((e["date"], "exit outside [entry, 15:10]"))
    v2 = simulate_v2(e["date"], e["direction"], e["expiry"], e["strike"],
                     e["entry_time"], PRIMARY["stop"], PRIMARY["locks"])
    if v2 != (r["exit_time"], r["exit_premium"], r["exit_reason"],
              r["highest_stage"], r["net"]):
        audit_fail.append((e["date"], f"v2 mismatch {v2} vs {r}"))
assert not audit_fail, audit_fail
print("timing audit + independent implementation cross-check: PASS (99 legs)")

# ---- stage anatomy (primary) -------------------------------------------------
anatomy = {}
reached = {k: 0 for k in (1, 2, 3, 4)}
for r in primary_rows:
    for k in reached:
        if r["highest_stage"] >= k:
            reached[k] += 1
for h in range(5):
    sel = [r for r in primary_rows if r["highest_stage"] == h]
    anatomy[f"highest_T{h}" if h else "no_stage"] = dict(
        legs=len(sel),
        total=round(sum(r["net"] for r in sel), 2),
        mean=round(sum(r["net"] for r in sel) / len(sel), 2) if sel else None)
exit_reasons = {}
for r in primary_rows:
    exit_reasons[r["exit_reason"]] = exit_reasons.get(r["exit_reason"], 0) + 1

# ---- B2 subset (primary params) ----------------------------------------------
b2_rows = [r for r in primary_rows if r["family"] == "BASE"]
b2_orig = round(sum(r["original_net"] for r in b2_rows), 2)

# ---- placebos (primary params) ------------------------------------------------
def run_placebo(mode):
    rows, ncs = [], []
    for e in ENTRIES:
        if mode == "flipped":
            # a true flip mirrors BOTH the contract type and the spot sign
            out, why = simulate_flip(e)
        else:
            et2 = add60(e["entry_time"])
            if et2 >= SQ:
                out, why = None, f"shifted entry {et2} not before square-off {SQ}"
            else:
                out, why = simulate(e["date"], e["direction"], e["expiry"],
                                    e["strike"], e["entry_time"],
                                    PRIMARY["stop"], PRIMARY["locks"],
                                    entry_time_override=et2)
        if out is None:
            ncs.append((e["date"], e["direction"], e["entry_time"], why))
        else:
            rows.append(dict(date=e["date"], net=out["net"]))
    return rows, ncs


def simulate_flip(e):
    """Flipped-direction placebo: opposite option type at the same strike,
    same entry bar; ladder stages measured on spot moves in the FLIPPED
    direction (sign of the opposite position)."""
    flip_dir = "PE" if e["direction"] == "CE" else "CE"
    bars = daybars(e["expiry"], e["strike"], flip_dir, e["date"])
    et = e["entry_time"]
    if et not in bars:
        return None, (f"flipped entry bar {et} absent for "
                      f"{e['expiry']}|{e['strike']}|{flip_dir} {e['date']}")
    # reuse simulate() with direction=flip_dir and typ=flip_dir: entry,
    # sign and contract all follow the flipped position.
    return simulate(e["date"], flip_dir, e["expiry"], e["strike"], et,
                    PRIMARY["stop"], PRIMARY["locks"])


flip_rows, flip_ncs = run_placebo("flipped")
shift_rows, shift_ncs = run_placebo("shifted")

# ---- write per-leg CSV (primary) ----------------------------------------------
fields = ["date", "direction", "family", "rep", "expiry", "strike",
          "entry_time", "entry_premium", "entry_spot", "highest_stage",
          "exit_time", "exit_premium", "exit_reason", "net",
          "original_net", "delta_vs_original"]
with open(TR / "ladder_bank_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in primary_rows:
        w.writerow({k: r[k] for k in fields})

# ---- independent re-sum from the written file ----------------------------------
chk = list(csv.DictReader(open(TR / "ladder_bank_trades.csv")))
for r in chk:
    r["net"] = float(r["net"])
resum = aggregates(chk)
prim_agg = results["PRIMARY_stop20_locks5_15_25"]["aggregates"]
assert resum["total"] == prim_agg["total"], (resum["total"], prim_agg["total"])
assert resum["months"] == prim_agg["months"]
assert resum["halves"] == prim_agg["halves"]
assert resum["ex_top3_legs"] == prim_agg["ex_top3_legs"]
assert resum["ex_top3_days"] == prim_agg["ex_top3_days"]
assert resum["worst_day"] == prim_agg["worst_day"]
assert resum["worst_drawdown"] == prim_agg["worst_drawdown"]
orig_total = round(sum(float(r["original_net"]) for r in chk), 2)
assert orig_total == 83650.50, orig_total
print(f"independent re-sum from ladder_bank_trades.csv: PASS "
      f"(ladder total {resum['total']}, original-exit total {orig_total})")

out = dict(
    build="LADDER-BANK (owner ladder exits on Bank v21 entries)",
    date="2026-11-03",
    store="daily2leg/prem_bank.json post-backfill (531 pre-10:00 bars added)",
    benchmark_original_exits=dict(total=orig_total,
                                  january=round(sum(float(r["original_net"])
                                                    for r in chk
                                                    if r["date"][:7] == "2026-01"), 2)),
    variants=results,
    primary_stage_anatomy=dict(reached_cumulative=reached, by_highest=anatomy,
                               exit_reasons=exit_reasons),
    b2_subset=dict(definition="family == BASE (B2 pool as carried into v21)",
                   legs=len(b2_rows), ladder=aggregates(b2_rows),
                   original_exits_total=b2_orig),
    placebos=dict(
        flipped=dict(aggregates=aggregates(flip_rows) if flip_rows else None,
                     not_computed=flip_ncs,
                     leg_nets=[r["net"] for r in flip_rows]),
        shifted_plus60=dict(aggregates=aggregates(shift_rows) if shift_rows else None,
                            not_computed=shift_ncs,
                            leg_nets=[r["net"] for r in shift_rows])),
    timing_audit=dict(
        checks="entry premium == recorded (99/99, from reconstruction audit); "
               "exit premium == store close at exit bar; exit within "
               "[entry, 15:10]; independent second implementation of the "
               "exit logic reproduces exit_time/exit_premium/reason/stage/"
               "net on all 99 legs",
        passed=True),
    independent_resum=dict(passed=True, ladder_total=resum["total"],
                           original_total=orig_total),
)
(TR / "ladder_bank_results.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("benchmark_original_exits",)}, indent=1))
print("PRIMARY:", json.dumps(prim_agg, indent=1))
print("anatomy reached:", reached, "by highest:", anatomy)
print("exit reasons:", exit_reasons)
print("B2 subset ladder total:", results and aggregates(b2_rows)["total"],
      "vs original exits on same legs:", b2_orig)
print("flipped placebo:", aggregates(flip_rows)["total"] if flip_rows else None,
      "NC:", flip_ncs)
print("shifted placebo:", aggregates(shift_rows)["total"] if shift_rows else None,
      "NC:", shift_ncs)
for n in results:
    if n != "PRIMARY_stop20_locks5_15_25":
        print(n, results[n]["aggregates"]["total"])
