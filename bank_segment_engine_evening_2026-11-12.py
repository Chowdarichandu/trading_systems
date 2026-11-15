#!/usr/bin/env python3
"""Bank segment engine evening 2026-11-12 — gated candidate BANK-EVE-21.
Trigger (today, forward): TUNED SHADOW BOOK v3's EVE-04 breakeven lock converted
the legacy primary's NS1 target win into a breakeven exit. Legacy NS1 CE 61200:
entry 12:45 @ 710.00; entry-bar high 774.85 armed the +30 lock; the 12:55 bar
dipped to 700.75 (through the 710.00 breakeven stop) before the 13:05 bar hit
the +90 target @ 800.00. Legacy +Rs2,480.00; tuned v3 derivation -Rs220.00.
Candidate (pre-registered here BEFORE scoring): BANK-EVE-21 — NS1 lock floor
buffer: arm unchanged (a completed bar's high >= entry+30, armed after that
bar's own stop/trig checks, exactly as the FC-2/EVE-04 replay arms), but the
raised stop sits at entry-20 instead of entry+0. Mechanically distinct from
EVE-04 (floor level, not arm point, not sleeve); EVE-04 is never retested
identically.
Universe: causal v21 book (99 legs) reproduced leg-for-leg in-run (the spot
store now carries November days past the Jan-Oct EXPIRIES list, so the setup
generator's DAYS are trimmed back to the frozen Jan-Oct window before
assembly — the reproduction assert below is the safeguard). Gate frame = v3's
NS1 treatment: EVE-09 skip (NS1 entry <10:30 dropped) + the NS1 lock under
test, replayed per-leg with each leg's frozen _params through a floor-aware
copy of flaw_cycle_run.replay_overlay; non-NS1 legs keep frozen nets.
In-run verifications before any candidate number is used: (1) v21 assembly
reproduced 99 legs / +Rs83,650.50 / 0 field mismatches vs the frozen regen
CSV; (2) no-lock replay of all 99 legs re-sums to the frozen total; (3) the
EVE-04-scoped replay (floor 0, NS1 only, no skip) re-sums to the gated
+Rs87,370.50 of 2026-11-03.
Full controls in the same run: timing audit, two placebos (mirror-sleeve:
floor-0 lock on BASE legs with NS1 raw; shifted arm +60 with the -20 floor),
halves, full month table, ex-top-3, independent re-sum.
November counterfactual for today's leg from the stored premium candles.
Paper only, real money Rs0. Basis: premiums per 1 lot (30), cost Rs220/trade
(in stored nets / replay), UNIQUE-ONCE.
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r3_setups
bank_r3_setups.DAYS = [d for d in bank_r3_setups.DAYS if d <= "2026-10-31"]
from aggressive_score import candles
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU
from bank_r2_core import LOT, COST

TR = Path.home() / "workspace/trading"
SQ = "15:20"

# ---------- reproduce incumbent v21 (same pattern as flaw_cycle_run) ----------
pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0, nc21
ref = list(csv.DictReader(open(TR / "bank_engine_r8_v21_regen_trades.csv")))
mine = sorted(rows21, key=lambda r: (r["date"], r["entry_time"], r["leg_key"]))
ref = sorted(ref, key=lambda r: (r["date"], r["entry_time"]))
assert len(mine) == len(ref) == 99
mism = 0
for a, b in zip(mine, ref):
    for k in ("date", "direction", "family", "entry_time", "exit_time", "exit_reason"):
        if str(a[k]) != str(b[k]): mism += 1
    if abs(a["entry"] - float(b["entry_premium"])) > 0.005: mism += 1
    if abs(a["exit"] - float(b["exit_premium"])) > 0.005: mism += 1
    if abs(a["net"] - float(b["net_inr"])) > 0.005: mism += 1
inc_net = round(sum(r["net"] for r in rows21), 2)
print(f"V21 REPRODUCED: n={len(rows21)} net={inc_net} mismatches={mism}")
assert mism == 0 and inc_net == 83650.50

# ---------- floor-aware replay (copy of flaw_cycle_run.replay_overlay) ----------
def replay_flex(cs, entry_time, p, lock_floor=None, arm=30.0):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0]
    if i0 >= len(cs) or cs[i0][0] > SQ: return None
    entry = cs[i0][1]
    stop0, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[i0:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0)
    runmax = None; lock_armed = False
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > SQ: break
        runmax = h if runmax is None else max(runmax, h)
        eff_stop = entry + lock_floor if (lock_armed and lock_floor is not None) else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if (lock_armed and lock_floor is not None) else "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > SQ: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == SQ: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if lock_floor is not None and h >= entry + arm:
            lock_armed = True
        if t == SQ:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0])

def replay_leg(r, lock_floor=None, arm=30.0):
    leg = lbk[r["leg_key"]]
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    return replay_flex(cs, leg["entry_time"], r["_params"], lock_floor=lock_floor, arm=arm)

# verification (2): no-lock replay re-sums to frozen total
nolock_total = 0.0; nolock_bad = []
for r in rows21:
    res = replay_leg(r, lock_floor=None)
    if res is None or abs(res["net"] - r["net"]) > 0.005:
        nolock_bad.append((r["date"], r["family"], r["net"], None if res is None else res["net"]))
    else:
        nolock_total += res["net"]
print(f"NO-LOCK REPLAY: total={round(nolock_total,2)} mismatches={len(nolock_bad)} {nolock_bad[:5]}")
assert not nolock_bad and round(nolock_total, 2) == 83650.50

# verification (3): EVE-04 scope (floor 0 on NS1 only, no skip) == gated +87,370.50
eve04_total = 0.0
for r in rows21:
    if r["family"] == "NS1_second":
        eve04_total += replay_leg(r, lock_floor=0.0)["net"]
    else:
        eve04_total += r["net"]
print(f"EVE-04 SCOPE CHECK: total={round(eve04_total,2)} (gated record +87,370.50)")
assert round(eve04_total, 2) == 87370.50

# ---------- frames ----------
def build(floor, arm=30.0, skip_early=True, lock_family="NS1_second"):
    out = []
    for r in rows21:
        leg = lbk[r["leg_key"]]
        if r["family"] == "NS1_second" and skip_early and leg["entry_time"] < "10:30":
            continue
        if r["family"] == lock_family:
            res = replay_leg(r, lock_floor=floor, arm=arm)
            assert res is not None, r["leg_key"]
            out.append(dict(date=r["date"], family=r["family"], entry_time=leg["entry_time"],
                            net=res["net"], exit_reason=res["exit_reason"]))
        else:
            out.append(dict(date=r["date"], family=r["family"], entry_time=leg["entry_time"],
                            net=r["net"], exit_reason=r["exit_reason"]))
    return out

def battery(rows, label):
    months = defaultdict(float)
    for r in rows: months[r["date"][:7]] += r["net"]
    h1 = round(sum(r["net"] for r in rows if r["date"] <= "2026-05-31"), 2)
    h2 = round(sum(r["net"] for r in rows if r["date"] >= "2026-06-01"), 2)
    srt = sorted(rows, key=lambda r: -r["net"])
    total = round(sum(r["net"] for r in rows), 2)
    return {"label": label, "n": len(rows), "net": total,
            "halves": {"H1": h1, "H2": h2},
            "months": {k: round(v, 2) for k, v in sorted(months.items())},
            "ex_top3": round(total - sum(r["net"] for r in srt[:3]), 2),
            "top3": [(r["date"], r["net"]) for r in srt[:3]]}

def flips(base_b, var_b):
    return [m for m, v in base_b["months"].items() if v > 0 and var_b["months"].get(m, 0) < 0]

inc_rows = build(floor=0.0)                       # v3 NS1 treatment, EVE-04 lock
inc = battery(inc_rows, "incumbent frame: v21 + EVE-09 skip + EVE-04 lock (floor 0)")
print("INCUMBENT FRAME:", inc["n"], inc["net"], "(expected 96 legs / +89,530.50 from gated records)")

cand_rows = build(floor=-20.0)                    # BANK-EVE-21
cand = battery(cand_rows, "BANK-EVE-21: NS1 lock floor entry-20 (arm +30)")

pb1_rows = build(floor=0.0, lock_family="BASE")   # placebo mirror sleeve (NS1 raw, skip kept)
pb1 = battery(pb1_rows, "placebo mirror: floor-0 lock on BASE legs, NS1 raw (EVE-09 skip kept)")
pb2_rows = build(floor=-20.0, arm=60.0)           # placebo shifted arm
pb2 = battery(pb2_rows, "placebo shifted-arm: NS1 lock floor -20, arm +60")

# flaw cohort: kept NS1 legs whose outcome differs across frozen / floor0 / floor-20
frozen_by = {(r["date"], lbk[r["leg_key"]]["entry_time"]): r["net"]
             for r in rows21 if r["family"] == "NS1_second"}
inc_ns1 = [r for r in inc_rows if r["family"] == "NS1_second"]
cand_ns1 = [r for r in cand_rows if r["family"] == "NS1_second"]
cohort = []
for ri, rc in zip(inc_ns1, cand_ns1):
    fnet = frozen_by[(ri["date"], ri["entry_time"])]
    if abs(ri["net"] - fnet) > 0.005 or abs(rc["net"] - ri["net"]) > 0.005:
        cohort.append(dict(date=ri["date"], entry_time=ri["entry_time"], frozen=fnet,
                           incumbent_lock0=ri["net"], candidate_lock_m20=rc["net"],
                           inc_reason=ri["exit_reason"], cand_reason=rc["exit_reason"]))

gf = flips(inc, cand)
verdict = "PASS" if (cand["net"] > inc["net"] and cand["net"] > pb1["net"] and cand["net"] > pb2["net"]
                     and cand["halves"]["H1"] >= 0 and cand["halves"]["H2"] >= 0
                     and not gf and cand["ex_top3"] > 0) else "FAIL"
fail_legs = []
if cand["net"] <= inc["net"]: fail_legs.append("net")
if cand["net"] <= pb1["net"]: fail_legs.append("placebo-mirror")
if cand["net"] <= pb2["net"]: fail_legs.append("placebo-shifted-arm")
if cand["halves"]["H1"] < 0 or cand["halves"]["H2"] < 0: fail_legs.append("halves")
if gf: fail_legs.append(f"green-month-flip {gf}")
if cand["ex_top3"] <= 0: fail_legs.append("ex-top-3")

# November counterfactual: today's NS1 leg (61200 CE, entry 12:45 @ 710.00, plain G0)
nov = json.load(open(TR / "november_shadow_data/candles_BANKNIFTY_61200CE_2026-11-12_2026-11-23.json"))
ncs = sorted([(c[0][11:16], c[1], c[2], c[3], c[4], c[5] if len(c) > 5 else 0)
              for c in nov["data"]["candles"]])
PLAIN = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
nov_today = {}
for fl, nm in [(None, "frozen (legacy)"), (0.0, "EVE-04 floor 0 (tuned v3 derivation)"),
               (-20.0, "EVE-21 floor -20 (candidate)")]:
    nov_today[nm] = replay_flex(ncs, "12:45", PLAIN, lock_floor=fl)
print("NOV 12 counterfactual:", json.dumps(nov_today, default=str))

results = {
    "candidate": "BANK-EVE-21 — NS1 lock floor entry-20 (arm +30 unchanged), on v3's NS1 treatment (EVE-09 skip kept)",
    "verifications": {"v21_reproduction": {"n": len(rows21), "net": inc_net, "mismatches": mism},
                      "nolock_replay_total": round(nolock_total, 2),
                      "eve04_scope_total": round(eve04_total, 2)},
    "incumbent_frame": inc, "candidate_frame": cand,
    "placebo_mirror_base_lock": pb1, "placebo_shifted_arm60": pb2,
    "green_flips": gf, "flaw_cohort_changed_legs": cohort,
    "timing_audit": "lock input is completed-bar highs at/after entry; skip input is entry_time — 0 violations by construction",
    "november_counterfactual_2026-11-12": nov_today,
    "verdict": verdict, "failed_legs": fail_legs,
}
print(json.dumps(results, indent=1, default=str))
with open(TR / "bank_segment_engine_evening_2026-11-12.json", "w") as f:
    json.dump(results, f, indent=1, default=str)
print("WROTE bank_segment_engine_evening_2026-11-12.json — VERDICT:", verdict, fail_legs)
