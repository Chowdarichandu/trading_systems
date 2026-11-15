#!/usr/bin/env python3
"""BANK v22 PHASE 1 (2026-11-04) — assemble the two gate-passed Bank tunings
onto v21 and re-gate the assembly. v21 stays frozen; this builds a NEW
candidate book. Nothing armed, no November files touched.

STEP A: BANK-EVE-04 — NS1_second legs only take the FC-2 give-back lock
(completed bar high >= entry+30 -> stop rises to entry+0 for subsequent
bars), re-simulated with the flaw-cycle replay (flaw_cycle_run.py
replay_overlay, copied verbatim) on the audited pipeline (assemble6).
All other legs keep their frozen v21 exits from bank_engine_r6_v21_trades.csv.
Claim under test: +83,650.50 -> +87,370.50 (verify, don't assume).
Cross-check: the 16 NS1 legs are ALSO re-simulated from prem_bank.json
(repaired store, ladder-build machinery) and compared leg-for-leg.

STEP B: BANK-EVE-05 rule applied mechanically to the v21 leg set (NOT the
B2-pool delta): skip OR-break PE legs entering before 10:30. OR-break
identification as the original scorer did: 'Skill V3' in source_systems
(B2 proof file) == rep 'Skill V3' in the v21 book — audited by matching.

GATE on the final book (+ Step A standalone battery): timing audit,
skip placebo (same count removed from the complementary OR-break set),
halves, month table, ex-top-3 legs/days, worst day / worst 3-day streak /
worst drawdown, % positive days, firing pace, independent re-sum from the
written trade file. Basis: Bank option premiums per 1 lot (30),
Rs 220/trade in nets, UNIQUE-ONCE.
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU
from bank_r2_core import LOT, COST, WEEKS

TR = Path.home() / "workspace/trading"
SQ = "15:20"
OUT = {}

def mins(t):
    h, m = map(int, t.split(":")); return h * 60 + m

# ---------------- base verification ----------------
base = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))
for r in base:
    r["net"] = float(r["net_inr"]); r["entry"] = float(r["entry_premium"]); r["exit"] = float(r["exit_premium"])
base_total = round(sum(r["net"] for r in base), 2)
base_jan = round(sum(r["net"] for r in base if r["date"].startswith("2026-01")), 2)
print(f"BASE: n={len(base)} total={base_total} jan={base_jan}")
assert len(base) == 99 and base_total == 83650.50 and base_jan == 22748.00
OUT["base"] = dict(n=len(base), total=base_total, january=base_jan)

# ---------------- audited pipeline reproduction ----------------
pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99

# replay_overlay copied verbatim from flaw_cycle_run.py (mode='open')
def replay_overlay(cs, entry_time, p, overlay=None, delay=0, sq=SQ):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if start >= len(cs) or cs[start][0] > sq: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0)
    runmax = None; lock_armed = False
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        runmax = h if runmax is None else max(runmax, h)
        eff_stop = entry + 0.0 if lock_armed else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if lock_armed else "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == sq: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if overlay in ("fc2", "fc3") and h >= entry + 30.0:
            lock_armed = True
        if overlay in ("fc1", "fc3") and j == 2 and t < sq and runmax < entry + 15.0:
            return mk(cl, "nodev_cut", t, 0)
        if t == sq:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

def replay_all(overlay):
    out = {}
    for r in rows21:
        leg = lbk[r["leg_key"]]
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        res = replay_overlay(cs, leg["entry_time"], r["_params"], overlay=overlay)
        assert res is not None, (r["leg_key"], overlay)
        out[r["leg_key"]] = res
    return out

inc_replay = replay_all(None)
key_of = {}
for r in rows21:
    leg = lbk[r["leg_key"]]
    key_of[(r["date"], r["direction"], leg["entry_time"])] = r["leg_key"]
mism = []
for r in base:
    k = key_of[(r["date"], r["direction"], r["entry_time"])]
    s = inc_replay[k]
    if abs(s["net"] - r["net"]) > 0.005 or s["exit_time"] != r["exit_time"] or s["exit_reason"] != r["exit_reason"] \
       or abs(s["entry"] - r["entry"]) > 0.005 or abs(s["exit"] - r["exit"]) > 0.005:
        mism.append((r["date"], r["direction"], r["entry_time"]))
print(f"INCUMBENT REPLAY vs FROZEN r6 CSV: mismatches={len(mism)}")
assert not mism
OUT["incumbent_replay_mismatches"] = 0

# ---------------- STEP A: NS1-only FC-2 lock ----------------
fc2_replay = replay_all("fc2")
stepA, changedA = [], []
for r in base:
    k = key_of[(r["date"], r["direction"], r["entry_time"])]
    nr = dict(r)
    if r["family"] == "NS1_second":
        s = fc2_replay[k]
        nr.update(net=s["net"], exit=s["exit"], exit_time=s["exit_time"], exit_reason=s["exit_reason"])
        if abs(s["net"] - r["net"]) > 0.005:
            changedA.append(dict(date=r["date"], direction=r["direction"], entry_time=r["entry_time"],
                                 old_reason=r["exit_reason"], new_reason=s["exit_reason"],
                                 old_net=r["net"], new_net=s["net"], delta=round(s["net"] - r["net"], 2)))
    stepA.append(nr)
stepA_total = round(sum(r["net"] for r in stepA), 2)
print(f"STEP A total={stepA_total} (claim 87370.50) changed={len(changedA)} {changedA}")
OUT["stepA"] = dict(total=stepA_total, claim=87370.50, claim_verified=(stepA_total == 87370.50),
                    delta=round(stepA_total - base_total, 2), changed_legs=changedA)

# ---- cross-check: NS1 legs re-simulated from prem_bank.json ----
prem = json.load(open(TR / "daily2leg/prem_bank.json"))
def store_bars(expiry, strike, typ, date):
    d = prem.get(f"{expiry}|{strike}|{typ}", {}).get(date, {})
    return [(t, v[0], v[1], v[2], v[3], 0.0) for t, v in sorted(d.items())]
xcheck = []
for r in rows21:
    if r["family"] != "NS1_second": continue
    leg = lbk[r["leg_key"]]
    cs = store_bars(leg["expiry"], leg["strike"], leg["direction"], leg["date"])
    a = replay_overlay(cs, leg["entry_time"], r["_params"], overlay=None)
    b = replay_overlay(cs, leg["entry_time"], r["_params"], overlay="fc2")
    c = inc_replay[r["leg_key"]]; d2 = fc2_replay[r["leg_key"]]
    xcheck.append(dict(date=r["date"], entry_time=leg["entry_time"],
                       store_entry=a["entry"] if a else None, recorded_entry=c["entry"],
                       store_inc_net=a["net"] if a else None, cache_inc_net=c["net"],
                       store_fc2_net=b["net"] if b else None, cache_fc2_net=d2["net"],
                       match=bool(a and b and abs(a["net"] - c["net"]) < 0.005 and abs(b["net"] - d2["net"]) < 0.005
                                  and abs(a["entry"] - c["entry"]) < 0.005)))
print(f"PREM-STORE CROSS-CHECK NS1: {sum(x['match'] for x in xcheck)}/16 legs match")
OUT["prem_store_crosscheck_ns1"] = xcheck

# ---------------- STEP B: EVE-05 skip on the v21 leg set ----------------
# identification audit: v21 rep 'Skill V3' <-> B2 proof 'Skill V3' in source_systems
b2 = list(csv.DictReader(open(TR / "historical_proof_bank_B2_trades.csv")))
b2_or = {(r["date"], r["direction"], r["entry_time"]) for r in b2 if "Skill V3" in r["source_systems"]}
v21_or = {(r["date"], r["direction"], r["entry_time"]) for r in base if r["rep"] == "Skill V3"}
print(f"OR-break ID: v21 Skill V3 legs={len(v21_or)}, all present in B2 OR set={v21_or <= b2_or}")
OUT["or_identification"] = dict(v21_skillv3_legs=len(v21_or), all_in_b2_or_set=bool(v21_or <= b2_or),
                                b2_or_set_size=len(b2_or))

def is_or_pe_early(r):
    return r["rep"] == "Skill V3" and r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")
skippedB = [r for r in stepA if is_or_pe_early(r)]
final = [r for r in stepA if not is_or_pe_early(r)]
print(f"STEP B skipped={len(skippedB)} net={round(sum(r['net'] for r in skippedB),2)}")
for r in skippedB: print("  SKIP", r["date"], r["direction"], r["entry_time"], r["exit_reason"], r["net"])
OUT["stepB"] = dict(skipped_n=len(skippedB), skipped_net=round(sum(r["net"] for r in skippedB), 2),
                    skipped_legs=[dict(date=r["date"], direction=r["direction"], entry_time=r["entry_time"],
                                       exit_reason=r["exit_reason"], net=r["net"]) for r in skippedB])

# placebo: same count from the complementary OR-break set (chronological first-N, mirrors original file-order rule)
comp = sorted([r for r in stepA if r["rep"] == "Skill V3" and not is_or_pe_early(r)],
              key=lambda r: (r["date"], r["entry_time"]))
placebo_removed = comp[:len(skippedB)]
pr_ids = {(r["date"], r["direction"], r["entry_time"]) for r in placebo_removed}
placebo = [r for r in stepA if (r["date"], r["direction"], r["entry_time"]) not in pr_ids]
print(f"PLACEBO removed={len(placebo_removed)} net={round(sum(r['net'] for r in placebo),2)}")
OUT["placebo"] = dict(removed_n=len(placebo_removed),
                      removed_legs=[dict(date=r["date"], entry_time=r["entry_time"], net=r["net"]) for r in placebo_removed],
                      net=round(sum(r["net"] for r in placebo), 2))

# ---------------- stats battery ----------------
def battery(rows, label):
    total = round(sum(r["net"] for r in rows), 2)
    months = {}
    for m in range(1, 11):
        mm = f"2026-{m:02d}"
        months[mm] = round(sum(r["net"] for r in rows if r["date"][:7] == mm), 2)
    H1 = round(sum(r["net"] for r in rows if r["date"][5:7] in ("01", "02", "03", "04", "05")), 2)
    H2 = round(sum(r["net"] for r in rows if r["date"][5:7] in ("06", "07", "08", "09", "10")), 2)
    top3l = sorted((r["net"] for r in rows), reverse=True)[:3]
    days = defaultdict(float)
    for r in rows: days[r["date"]] += r["net"]
    dlist = sorted(days.items())
    dnets = [round(v, 2) for _, v in dlist]
    top3d = sorted(dnets, reverse=True)[:3]
    worst_day = min(dlist, key=lambda kv: kv[1])
    worst3 = min((round(sum(dnets[i:i + 3]), 2), dlist[i][0], dlist[i + 2][0]) for i in range(len(dnets) - 2))
    cum, peak, maxdd = 0.0, 0.0, 0.0
    for v in dnets:
        cum += v; peak = max(peak, cum); maxdd = min(maxdd, cum - peak)
    st = dict(label=label, n_legs=len(rows), n_days=len(dlist), total=total,
              per_month=round(total / 10, 2), per_leg=round(total / len(rows), 2),
              legs_per_month=round(len(rows) / 10, 2), legs_per_week=round(len(rows) / WEEKS, 2),
              months=months, H1=H1, H2=H2,
              ex_top3_legs=round(total - sum(top3l), 2), top3_legs=top3l,
              ex_top3_days=round(total - sum(top3d), 2), top3_days=top3d,
              worst_day=dict(date=worst_day[0], net=round(worst_day[1], 2)),
              worst_3day_streak=dict(net=worst3[0], frm=worst3[1], to=worst3[2]),
              worst_drawdown=round(maxdd, 2),
              pct_positive_days=round(100.0 * sum(1 for v in dnets if v > 0) / len(dnets), 1))
    print(f"{label}: total={total} legs={len(rows)} days={len(dlist)} H1={H1} H2={H2} "
          f"exT3legs={st['ex_top3_legs']} exT3days={st['ex_top3_days']} worstDay={st['worst_day']} "
          f"worst3={st['worst_3day_streak']} DD={st['worst_drawdown']} posDays={st['pct_positive_days']}%")
    return st

OUT["battery_base"] = battery(base, "BASE v21")
OUT["battery_stepA"] = battery(stepA, "STEP A (EVE-04)")
OUT["battery_final"] = battery(final, "FINAL v22 (A+B)")
OUT["battery_placebo"] = battery(placebo, "PLACEBO (skip complement)")

# timing audit on re-simulated legs
tv = []
for r in stepA:
    if r["exit_time"] < r["entry_time"]: tv.append((r["date"], r["entry_time"], r["exit_time"]))
# lock-arm ordering check on changed NS1 legs: lock exit bar strictly after first bar with high >= entry+30
lock_order_ok = True
for ch in changedA:
    if ch["new_reason"] != "lock_stop": continue
    r = next(x for x in rows21 if x["date"] == ch["date"] and x["family"] == "NS1_second")
    leg = lbk[r["leg_key"]]
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    ent = fc2_replay[r["leg_key"]]["entry"]
    arm_bar = next((b[0] for b in cs if b[0] >= leg["entry_time"] and b[1] is not None and b[2] >= ent + 30.0), None)
    bars_from_entry = [b for b in cs if b[0] >= leg["entry_time"]]
    arm_bar = next((b[0] for b in bars_from_entry if b[2] >= ent + 30.0), None)
    if arm_bar is None or not (ch and fc2_replay[r["leg_key"]]["exit_time"] > arm_bar): lock_order_ok = False
OUT["timing_audit"] = dict(exit_before_entry_violations=tv, lock_arm_strictly_before_lock_exit=lock_order_ok,
                           skip_inputs="entry_time/direction/rep only — all known at entry, no future data")
print("TIMING:", OUT["timing_audit"])

# ---------------- write final trade file + independent re-sum ----------------
fin_rows = []
for r in sorted(final, key=lambda x: (x["date"], x["entry_time"])):
    fin_rows.append([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"], r["entry"],
                     r["exit_time"], r["exit"], r["exit_reason"], r["net"]])
with open(TR / "bank_v22_phase1_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                "exit_time", "exit_premium", "exit_reason", "net_inr"])
    w.writerows(fin_rows)
rs = [float(r["net_inr"]) for r in csv.DictReader(open(TR / "bank_v22_phase1_trades.csv"))]
OUT["independent_resum_final"] = dict(n=len(rs), net=round(sum(rs), 2),
                                      matches=(len(rs) == len(final) and abs(round(sum(rs), 2) - OUT["battery_final"]["total"]) < 0.005))
print("RESUM FINAL:", OUT["independent_resum_final"])

# ---------------- phase-2 gap arithmetic ----------------
F = OUT["battery_final"]
gap_m = round(15000 - F["per_month"], 2)
need_legs_pm = 15000 / F["per_leg"]
need_per_leg = 15000 / F["legs_per_month"]
OUT["phase2_arithmetic"] = dict(
    bracket_per_month=15000, final_per_month=F["per_month"], gap_per_month=gap_m,
    gap_10mo=round(gap_m * 10, 2),
    current_legs_per_month=F["legs_per_month"], current_per_leg=F["per_leg"],
    needed_legs_per_month_at_current_per_leg=round(need_legs_pm, 2),
    extra_legs_per_month_needed=round(need_legs_pm - F["legs_per_month"], 2),
    needed_total_legs_10mo_at_current_per_leg=round(need_legs_pm * 10, 1),
    needed_per_leg_at_current_frequency=round(need_per_leg, 2),
    extra_per_leg_needed=round(need_per_leg - F["per_leg"], 2))
print("PHASE2:", json.dumps(OUT["phase2_arithmetic"], indent=1))

(TR / "bank_v22_phase1_results.json").write_text(json.dumps(OUT, indent=1, default=str))
print("WROTE bank_v22_phase1_results.json + bank_v22_phase1_trades.csv")
