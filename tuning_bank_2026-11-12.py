#!/usr/bin/env python3
"""BANK NIFTY TUNING PROGRAMME 2026-11-12 (owner order 2026-11-12 16:23
IST: "I need tuning all 3"). Paper only, real money Rs 0. Basis: Bank
Nifty option premiums per 1 lot (30), Rs 220/trade, UNIQUE-ONCE.
Frozen November primary logs/specs are never modified; output =
December candidates only.

INCUMBENT: TUNED STACK v2 (bank_positive_tuning_2026-11-10 BANK-EVE-19:
v22 frame + EVE-19 early-NS1 skip with re-derived EVE-06(a) re-entries
+ c4 runner extension + v1 NS3/S3 band add-ons; 111 legs,
+Rs 127,351.50 Jan-Oct 2026, all 10 months positive). ANCHOR: this
script rebuilds v2 leg-for-leg against
bank_positive_tuning_2026-11-10_eve19_trades.csv and asserts the
battery equals the frozen session summary BEFORE any variant is
scored. Machinery is copied from bank_positive_tuning_2026-11-10.py
(the original is never executed — it would rewrite its own files).

PRE-REGISTERED VARIANTS (all EXIT-SIDE / geometry; admission frozen —
pipe+add-on leg sets identical to the incumbent's; the EVE-06(a)
re-entry set is re-derived by the frozen phase-2 rule from each
variant's own exits, exactly as EVE-19 re-derived it from the skipped
book; re-entry legs are scored under the variant geometry via
sim_variant, a dict-bar generalisation of the frozen sim_g0 that is
asserted to reproduce sim_g0 exactly under G0 params):
  T-B1a LOCK30-TRAIL : legs whose assembly params have trig == 90 get
      {stop: own, trig: 90, lock: 30, tgt2: None} — at +90 no exit;
      from the next bar the floor is entry+30, ride to the 15:20 SQ.
  T-B1b LOCK10-AT-58 : legs with trig == 90 get
      {stop: own, trig: 58, lock: 10, tgt2: None} — trigger arms at
      +58, floor entry+10 from the next bar, ride to SQ.
  T-B2a PE-STOP40    : PE legs only — stop 40 (was 50); rest unchanged.
  T-B2b PE-STOP60    : PE legs only — stop 60 (was 50); rest unchanged.
  T-B2c PE-BE50      : PE legs whose assembly params are PLAIN
      (lock/tgt2 None) get {stop: own, trig: 50, lock: 0, tgt2: 90} —
      arm at +50, floor = entry, target +90. PE runner legs unchanged.
  T-B3  LADDER-STACK : the owner ladder (locked design 2026-11-03:
      spot stages T1 +30 / T2 +58 / T3 +82 / T4 +100 on 5-min spot
      closes; hard stop = premium close <= entry-20; floors entry+5 /
      +15 / +25; T4 exits at that bar's premium close; SQ = close of
      the 15:10 bar) applied to all 111 incumbent legs, entries frozen
      INCLUDING the incumbent re-entry set (the ladder build's own
      rule: entries unchanged, only exits change).

GATE (standing controls gate, same run, bars unmoved): the aggressive
tune's gate_check verbatim — total must BEAT the incumbent (the task
bar additionally records a total that matches with no other gate-leg
failure as MATCH), total must beat the placebo, halves, ex-top-3 legs
and days, no green month flips red, no exit-before-entry, NC == 0 —
plus a fill audit on every changed leg (exit premium must be one of
the variant's own level fills or the exit bar's close for close
exits) and an admission audit (pipe/add-on entry keys and entry
premiums identical to the incumbent's; re-entry deltas reported).
Placebos for T-B1/T-B2: leg-identical delay-6 twin under the same
variant geometry (a leg with no delay-6 entry counts at its candidate
net) + re-entries replaced by the +60-min shifted derivation under
the variant (the build_placebo_ride construction). T-B3 placebos:
flipped-direction and +60-min shifted-entry, candidate-net fill for
NC legs (disclosed).

November counterfactuals (Nov 2-12) run in a subprocess helper
(tuning_bank_2026-11-12_nov.py) because the November assembly needs a
process without the Jan-Oct s3mod restriction; the helper asserts its
identity book equals the scored stack ledger (november_shadow_stack_
bank_log.csv, total -Rs 960) before applying any variant.
"""
import csv, json, subprocess, sys
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"
OUT = {"session": "tuning_bank_2026-11-12"}

def mins(t):
    h, m = map(int, str(t).split(":")[:2]); return h * 60 + m

# =====================================================================
# machinery (copied from bank_positive_tuning_2026-11-10.py, which
# copied it from bank_aggressive_tune_score.py / the phase-2 scorer;
# originals are never executed)
# =====================================================================
import bank_r3_setups as s3mod
s3mod.SPOT = s3mod.SPOT[s3mod.SPOT["date"] <= "2026-10-31"].reset_index(drop=True)
s3mod.DAYS = sorted(s3mod.SPOT["date"].unique())
s3mod.DAY_BARS = {d: g.reset_index(drop=True) for d, g in s3mod.SPOT.groupby("date")}
s3mod.DAILY = {k: v for k, v in s3mod.DAILY.items() if k <= "2026-10-31"}

from aggressive_score import candles, unique_once
import bank_r6_core
from bank_r6_core import assemble6, v20_inputs
from bank_r7_core import P21, GDGU
from bank_r5_core import ns3_legs, stream_states, enrich, _params_for_addon as r5_params_for_addon
from bank_r2_core import seg_of, WEEKS
from bank_r3_setups import generate as gen_setups
from bank_r3_core import admit
from bank_engine_cycle import FILTERS

def replay_mod(cs, entry_time, p, delay=0, arm30=False, arm50=False,
               arm50_level=0.0, armL=False):
    """Verbatim copy of bank_aggressive_tune_score.replay_mod."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if start >= len(cs) or cs[start][0] > SQ: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft, dev30, maxfav):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px,
                    dev30=dev30, maxfav=maxfav)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0, False, 0.0)
    runmax = None; arm_level = None
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > SQ: break
        dev30 = runmax is not None and runmax >= entry + 30.0
        maxfav = 0.0 if runmax is None else runmax - entry
        eff_stop = entry + arm_level if arm_level is not None else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if arm_level is not None else "stop", t, 0, dev30, maxfav)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1, dev30, maxfav)
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
            return mk(rest[0], rest[1], rest[2], 1, dev30, maxfav)
        if arm30 and h >= entry + 30.0:
            arm_level = 0.0 if arm_level is None else max(arm_level, 0.0)
        if armL and h >= entry + 50.0:
            arm_level = 0.0 if arm_level is None else max(arm_level, 0.0)
        if arm50 and h >= entry + 50.0:
            arm_level = arm50_level if arm_level is None else max(arm_level, arm50_level)
        runmax = h if runmax is None else max(runmax, h)
        if t == SQ:
            return mk(cl, "square_off", t, 0, dev30, maxfav)
    lb = bars[-1]
    dev30 = runmax is not None and runmax >= entry + 30.0
    maxfav = 0.0 if runmax is None else runmax - entry
    return mk(lb[4], "square_off", lb[0], 0, dev30, maxfav)

# ---- pipeline assembly (rows21 / LEG), as the aggressive tune builds it
pooled, ns1_aud = v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1_aud, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99
LEG = {}
for r in rows21:
    leg = lbk[r["leg_key"]]
    LEG[r["leg_key"]] = dict(
        cs=candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"]),
        p=r["_params"], family=r["family"], rep=r["rep"], date=r["date"],
        direction=r["direction"], entry_time=r["entry_time"], expiry=leg["expiry"])
mm0 = 0
for r in rows21:
    s = replay_mod(LEG[r["leg_key"]]["cs"], r["entry_time"], r["_params"])
    if abs(s["net"] - r["net"]) > 0.005 or s["exit_time"] != r["exit_time"] or s["exit_reason"] != r["exit_reason"]:
        mm0 += 1
assert mm0 == 0, f"replay_mod delay-0 mismatches vs frozen pipeline: {mm0}"
print("REPLAY CHECK: replay_mod reproduces the frozen pipeline 99/99")

def is_or_pe_early_row(r):
    return r["rep"] == "Skill V3" and r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")

# ---- G0 store machinery (phase-2 copies) --------------------------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
prem_store = json.load(open(TR / "daily2leg/prem_bank.json"))
DAYS = sorted(d for d in spot_raw if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
SPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in spot_raw[d]} for d in DAYS}
TIMES = {d: [b[0] for b in spot_raw[d]] for d in DAYS}
_chain_days = defaultdict(set)
for k, v in prem_store.items():
    for d in v: _chain_days[k.split("|")[0]].add(d)
MONTHLY = sorted(e for e, ds in _chain_days.items() if len(ds) >= 10)

def expiry_for(d):
    for e in MONTHLY:
        if d <= e: return e
    present = {k.split("|")[0] for k, v in prem_store.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None

def atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def add_min(t, m):
    h, mm = int(t[:2]), int(t[3:]); mm += m; h += mm // 60; mm %= 60
    return f"{h:02d}:{mm:02d}"

def prem_day(exp, strike, typ, d):
    cd = prem_store.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None: return None
    return {t: tuple(float(x) for x in v) for t, v in cd.items()}

def sim_g0(pd, entry_time, entry_prem):
    stop_lvl, tgt_lvl = entry_prem - 50.0, entry_prem + 90.0
    for t in sorted(pd):
        if t < entry_time or t > "15:05": continue
        o, h, l, c = pd[t]
        if l <= stop_lvl: return t, stop_lvl, "stop"
        if h >= tgt_lvl: return t, tgt_lvl, "target"
    if "15:10" in pd: return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def sim_variant(pd, entry_time, entry_prem, p):
    """Dict-bar generalisation of the frozen sim_g0 to arbitrary
    {stop, trig, lock, tgt2} geometry, following replay_mod's phase
    semantics but keeping the phase-2 square-off convention of the
    frozen re-entry book (bars to 15:05, then the 15:10 bar OPEN;
    runner legs label that exit runner_square_off). Under G0 params
    this must equal sim_g0 exactly (asserted in the anchor leg)."""
    stop_lvl = entry_prem - p["stop"]; trig_lvl = entry_prem + p["trig"]
    times = sorted(t for t in pd if entry_time <= t <= "15:05")
    for i, t in enumerate(times):
        o, h, l, c = pd[t]
        if l <= stop_lvl: return t, stop_lvl, "stop"
        if h >= trig_lvl:
            if p["lock"] is None and p["tgt2"] is None:
                return t, trig_lvl, "target"
            stop2 = entry_prem + p["lock"] if p["lock"] is not None else stop_lvl
            tgt2 = entry_prem + p["tgt2"] if p["tgt2"] is not None else None
            for t2 in times[i + 1:]:
                o2, h2, l2, c2 = pd[t2]
                if l2 <= stop2: return t2, stop2, "runner_stop"
                if tgt2 is not None and h2 >= tgt2: return t2, tgt2, "runner_target"
            if "15:10" in pd: return "15:10", pd["15:10"][0], "runner_square_off"
            last = times[-1]; return last, pd[last][3], "runner_square_off"
    if "15:10" in pd: return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def build_reentry_leg(d, side, trig_time, entry_time, set_name):
    exp = expiry_for(d)
    s_open = SPOT[d][entry_time][0]
    strike = atm100(s_open)
    pd = prem_day(exp, strike, side, d)
    if pd is None: return None, f"NC:no_contract {exp}|{strike}|{side}"
    if entry_time not in pd: return None, f"NC:no_entry_bar {exp}|{strike}|{side}@{entry_time}"
    entry_prem = pd[entry_time][0]
    xt, xp, reason = sim_g0(pd, entry_time, entry_prem)
    net = round((xp - entry_prem) * LOT - COST, 2)
    return {"date": d, "set": set_name, "direction": side, "expiry": exp,
            "strike": strike, "trigger_time": trig_time, "entry_time": entry_time,
            "entry_premium": entry_prem, "exit_time": xt, "exit_premium": xp,
            "exit_reason": reason, "net_inr": net}, "ok"

def derive_reentries(base_rows, shift_min=0, set_name="A_reentry"):
    """Phase-2 find_reentry logic against a supplied v22-form book
    (rows with date/exit_reason/exit_time/net). Returns (legs, blocked, nc)."""
    by_day = defaultdict(list)
    for r in base_rows: by_day[r["date"]].append(r)
    legs, blocked, nc = [], [], []
    for d in DAYS:
        stops = [r for r in by_day.get(d, []) if r["exit_reason"] == "stop"]
        if not stops: continue
        leg0 = sorted(stops, key=lambda r: r["exit_time"])[0]
        side = leg0["direction"]
        b, ts = SPOT[d], TIMES[d]
        mh = max(b[t][1] for t in ts if t <= "11:55")
        ml = min(b[t][2] for t in ts if t <= "11:55")
        start = add_min(max("12:00", leg0["exit_time"]), shift_min)
        trig = None
        for t in ts:
            if t < start: continue
            c = b[t][3]
            if (side == "CE" and c > mh) or (side == "PE" and c < ml):
                trig = t; break
        if trig is None: continue
        realised = round(sum(r["net"] for r in by_day.get(d, []) if r["exit_time"] <= trig), 2)
        if realised <= -3000.0:
            if shift_min == 0: blocked.append({"date": d, "trigger": trig, "realised": realised})
            continue
        i = ts.index(trig)
        et = ts[i + 1] if i + 1 < len(ts) else None
        if et is None or et > "15:05":
            nc.append({"date": d, "why": "trigger_no_time", "trigger": trig}); continue
        leg, st = build_reentry_leg(d, side, trig, et, set_name)
        if leg: legs.append(leg)
        else: nc.append({"date": d, "why": st, "trigger": trig})
    return legs, blocked, nc

inc_csv = list(csv.DictReader(open(TR / "bank_v22_phase2_increments.csv")))
A_static = [r for r in inc_csv if r["set"] == "A_reentry"]
A_shift_static = [r for r in inc_csv if r["set"] == "A_shift60"]
assert len(A_static) == 16 and round(sum(float(r["net_inr"]) for r in A_static), 2) == 6119.00
A_STATICS = [{**r, "strike": int(float(r["strike"]))} for r in A_static]
A_SHIFT_STATICS = [{**r, "strike": int(float(r["strike"]))} for r in A_shift_static]

def resim_reentry(static_rows):
    out = []
    for r in static_rows:
        pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
        assert pd is not None and r["entry_time"] in pd, r
        xt, xp, reason = sim_g0(pd, r["entry_time"], float(r["entry_premium"]))
        out.append(dict(date=r["date"], direction=r["direction"], family="EVE06_REENTRY",
                        rep="EVE06a", entry_time=r["entry_time"],
                        entry_premium=float(r["entry_premium"]), exit_time=xt,
                        exit_premium=xp, exit_reason=reason,
                        net=round((xp - float(r["entry_premium"])) * LOT - COST, 2),
                        leg_key=(r["date"], r["direction"], r["entry_time"]),
                        dev30=None, maxfav=None, src="reentry",
                        strike=r["strike"], expiry=r["expiry"],
                        trigger_time=r["trigger_time"]))
    return out

_rs = resim_reentry(A_STATICS)
for a, b in zip(_rs, A_static):
    assert a["net"] == float(b["net_inr"]) and a["exit_time"] == b["exit_time"] \
        and a["exit_reason"] == b["exit_reason"], (a, b)
print("RE-ENTRY RE-SIM: reproduces phase-2 statics exactly (16/16)")

# sim_variant identity check: under G0 it must equal sim_g0 on every
# frozen static AND on the shifted statics
G0 = {"stop": 50.0, "trig": 90.0, "lock": None, "tgt2": None}
for r in A_STATICS + A_SHIFT_STATICS:
    pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
    a = sim_g0(pd, r["entry_time"], float(r["entry_premium"]))
    b = sim_variant(pd, r["entry_time"], float(r["entry_premium"]), G0)
    assert a == b, (r, a, b)
print("SIM_VARIANT CHECK: equals sim_g0 under G0 on 31/31 frozen statics")

# ---- stream (for S3 add-on geometry), as the aggressive tune builds it
_pool = unique_once(list(pooled) + list(ns1_aud))
_pool = FILTERS["drop_ns1_ce"](_pool)
_pool = FILTERS["drop_prem_400_550"](_pool)
_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in _pool}
STREAM, STATES, TAKEN0, _nc0 = stream_states(_by_key, delay=0)

# ---- v1 band-dropped candidates (v1_fns construction, verbatim logic)
def build_bd_legs():
    taken = {(r["date"], r["direction"]) for r in rows21 if r["family"] in ("BASE", "NS1_second")}
    bd_legs = []
    ns3c = [enrich(l) for l in ns3_legs(causal=True)]
    ns3c = [l for l in ns3c if GDGU(l)]
    adm, kd, bd, ncl = admit(ns3c, taken)
    taken |= {(l["date"], l["direction"]) for l in adm}
    for l in bd: bd_legs.append((l, dict(P21)))
    gen = gen_setups()
    for fam in ("S3A", "S3E", "S3D"):
        cand = [enrich(l) for l in gen[fam]]
        adm, kd, bd, ncl = admit(cand, taken)
        taken |= {(l["date"], l["direction"]) for l in adm}
        for l in bd:
            p, seg = r5_params_for_addon(l, STREAM)
            if p is not None: bd_legs.append((l, p))
    return bd_legs
BD_LEGS = build_bd_legs()
print(f"v1 band-dropped candidate pool: {len(BD_LEGS)} legs")

# ---- book builders (verbatim from the positive-tuning session) -------
def pipe_rows(delay=0, runner_ext=True, ride=False, ride_arm=None,
              skip_ns1_keys=frozenset()):
    out = []
    for r in rows21:
        k = r["leg_key"]; meta = LEG[k]
        if is_or_pe_early_row(r): continue
        if k in skip_ns1_keys: continue
        p = meta["p"]
        if runner_ext and p["lock"] is None and meta["date"] != meta["expiry"]:
            p = {**p, "lock": 90.0, "tgt2": 180.0}
        arm30 = meta["family"] == "NS1_second"
        s = replay_mod(meta["cs"], meta["entry_time"], p, delay=delay, arm30=arm30)
        assert s is not None, k
        out.append(dict(date=meta["date"], direction=meta["direction"], family=meta["family"],
                        rep=meta["rep"], entry_time=meta["entry_time"],
                        entry_premium=s["entry"], exit_time=s["exit_time"],
                        exit_premium=s["exit"], exit_reason=s["exit_reason"],
                        net=s["net"], leg_key=k, dev30=s["dev30"],
                        maxfav=s["maxfav"], src="pipe"))
    return out

def replay_addon(leg, p, runner_ext=True, ride=False, ride_arm=None, delay=0):
    fam = leg.get("family", "BASE")
    p_use = p
    if runner_ext and p["lock"] is None and leg["date"] != leg["expiry"]:
        p_use = {**p, "lock": 90.0, "tgt2": 180.0}
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    a30 = fam == "NS1_second"
    s = replay_mod(cs, leg["entry_time"], p_use, delay=delay, arm30=a30)
    if s is None: return None
    return dict(date=leg["date"], direction=leg["direction"], family=fam,
                rep=leg["rep"], entry_time=leg["entry_time"], entry_premium=s["entry"],
                exit_time=s["exit_time"], exit_premium=s["exit"], exit_reason=s["exit_reason"],
                net=s["net"], leg_key=(leg["date"], leg["direction"], leg["entry_time"]),
                dev30=s["dev30"], maxfav=s["maxfav"], src="addon")

def admit_addons(book_rows, runner_ext=True, ride=False, ride_arm=None):
    """v1 admission vs a supplied book (v1_fns fn logic). Returns
    (addon_rows, admitted_(leg,p)_list, nc)."""
    taken_now = {(r["date"], r["direction"]) for r in book_rows}
    seen, rows, admitted, nc = set(), [], [], 0
    for leg, p in sorted(BD_LEGS, key=lambda x: (x[0]["date"], x[0]["entry_time"])):
        key = (leg["date"], leg["direction"])
        if key in seen: continue
        seen.add(key)
        if key in taken_now: continue
        row = replay_addon(leg, p, runner_ext=runner_ext, ride=ride, ride_arm=ride_arm)
        if row is None: nc += 1; continue
        admitted.append((leg, p)); rows.append(row)
    return rows, admitted, nc

STACK_ADDONS = []  # (leg, p) admitted into the incumbent stack — set at leg 0

def build_stack(runner_ext=True, ride=False, ride_arm=None,
                skip_ns1_keys=frozenset(), reentry_statics=None,
                addons_on=True, addons_from=None):
    """The TUNED STACK under the given switches. reentry_statics=None
    means the frozen phase-2 statics (A_STATICS)."""
    rows = pipe_rows(runner_ext=runner_ext, ride=ride, ride_arm=ride_arm,
                     skip_ns1_keys=skip_ns1_keys)
    if addons_on:
        if addons_from is not None:
            for leg, p in addons_from:
                row = replay_addon(leg, p, runner_ext=runner_ext, ride=ride,
                                   ride_arm=ride_arm)
                assert row is not None, leg
                rows.append(row)
        else:
            arows, _, nc = admit_addons(rows, runner_ext=runner_ext, ride=ride,
                                        ride_arm=ride_arm)
            assert nc == 0, f"addon NC in build_stack: {nc}"
            rows += arows
    if reentry_statics is not None:
        rows += resim_reentry(reentry_statics)
    return rows

# ---- battery + gate (copied verbatim from bank_aggressive_tune_score.py)
def battery(rows):
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
    dlist = sorted(days.items()); dnets = [round(v, 2) for _, v in dlist]
    top3d = sorted(dnets, reverse=True)[:3]
    worst_day = min(dlist, key=lambda kv: kv[1])
    cum, peak, maxdd = 0.0, 0.0, 0.0
    for v in dnets:
        cum += v; peak = max(peak, cum); maxdd = min(maxdd, cum - peak)
    return dict(n_legs=len(rows), n_days=len(dlist), total=total,
                per_month=round(total / 10, 2), per_leg=round(total / len(rows), 2),
                legs_per_month=round(len(rows) / 10, 2), legs_per_week=round(len(rows) / WEEKS, 2),
                months=months, H1=H1, H2=H2,
                ex_top3_legs=round(total - sum(top3l), 2), top3_legs=top3l,
                ex_top3_days=round(total - sum(top3d), 2), top3_days=top3d,
                worst_day=dict(date=worst_day[0], net=round(worst_day[1], 2)),
                worst_drawdown=round(maxdd, 2),
                pct_positive_days=round(100.0 * sum(1 for v in dnets if v > 0) / len(dnets), 1))

def gate_check(cand_rows, base_batt, placebo_total, nc=0):
    cb = battery(cand_rows)
    fails = []
    if not cb["total"] > base_batt["total"]:
        fails.append(f"total {cb['total']} !> base {base_batt['total']}")
    if not cb["total"] > placebo_total:
        fails.append(f"placebo not beaten: cand {cb['total']} vs placebo {placebo_total}")
    halves_ok = (cb["H1"] >= base_batt["H1"] and cb["H2"] >= base_batt["H2"]) or \
                (cb["H1"] >= 0 and cb["H2"] >= 0)
    if not halves_ok:
        fails.append(f"halves {cb['H1']}/{cb['H2']} vs base {base_batt['H1']}/{base_batt['H2']}")
    if not (cb["ex_top3_legs"] > 0 and cb["ex_top3_legs"] >= base_batt["ex_top3_legs"]):
        fails.append(f"ex-top3 legs {cb['ex_top3_legs']} vs base {base_batt['ex_top3_legs']}")
    if not (cb["ex_top3_days"] > 0 and cb["ex_top3_days"] >= base_batt["ex_top3_days"]):
        fails.append(f"ex-top3 days {cb['ex_top3_days']} vs base {base_batt['ex_top3_days']}")
    for m, v in base_batt["months"].items():
        if v > 0 and cb["months"][m] < 0:
            fails.append(f"month {m} flips green->red ({v} -> {cb['months'][m]})")
    tv = [r for r in cand_rows if r["exit_time"] < r["entry_time"]]
    if tv: fails.append(f"timing violations: {len(tv)} exit-before-entry")
    if nc: fails.append(f"NOT_COMPUTED {nc}")
    return cb, fails

def write_trades(rows, fname):
    fields = ["date", "direction", "family", "rep", "entry_time", "entry_premium",
              "exit_time", "exit_premium", "exit_reason", "net_inr"]
    with open(TR / fname, "w", newline="") as f:
        w = csv.writer(f); w.writerow(fields)
        for r in sorted(rows, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry_premium"], r["exit_time"], r["exit_premium"],
                        r["exit_reason"], r["net"]])
    rs = [float(r["net_inr"]) for r in csv.DictReader(open(TR / fname))]
    return dict(n=len(rs), net=round(sum(rs), 2))

def leg_for_leg(rows, fname):
    ref = {(r["date"], r["direction"], r["entry_time"]): r
           for r in csv.DictReader(open(TR / fname))}
    mine = {(r["date"], r["direction"], r["entry_time"]): r for r in rows}
    if set(mine) != set(ref): return False, f"key sets differ: mine {len(mine)} vs ref {len(ref)}"
    for k, r in mine.items():
        f = ref[k]
        if (abs(r["entry_premium"] - float(f["entry_premium"])) > 0.005
                or abs(r["exit_premium"] - float(f["exit_premium"])) > 0.005
                or abs(r["net"] - float(f["net_inr"])) > 0.005
                or r["exit_time"] != f["exit_time"] or r["exit_reason"] != f["exit_reason"]
                or r["family"] != f["family"] or r["rep"] != f["rep"]):
            return False, f"mismatch at {k}: {r} vs {f}"
    return True, "exact"

def changed_legs(cand_rows, base_rows):
    base = {r["leg_key"]: r for r in base_rows}
    out = []
    for r in cand_rows:
        b = base.get(r["leg_key"])
        if b is not None and (abs(r["net"] - b["net"]) > 0.005 or r["exit_reason"] != b["exit_reason"]):
            out.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                            rep=r["rep"], entry_time=r["entry_time"],
                            old_reason=b["exit_reason"], new_reason=r["exit_reason"],
                            old_exit_time=b["exit_time"], new_exit_time=r["exit_time"],
                            old_net=b["net"], new_net=r["net"],
                            delta=round(r["net"] - b["net"], 2)))
    return out

def months_delta(cb, bb):
    return {m: round(cb["months"][m] - bb["months"][m], 2) for m in bb["months"]}

# =====================================================================
# LEG 0 — reproduce the incumbent stack v2 before scoring anything
# (v22 -> after-c4 -> stack v1 -> EVE-19, the positive-tuning chain)
# =====================================================================
v22_rows = pipe_rows(runner_ext=False)
ok22, why22 = leg_for_leg(v22_rows, "bank_v22_phase1_trades.csv")
assert ok22 and len(v22_rows) == 90 and round(sum(r["net"] for r in v22_rows), 2) == 91450.50, why22
print("LEG 0a: v22 intermediate reproduced leg-for-leg (90 legs, +91,450.50)")

after_c4 = build_stack(reentry_statics=A_STATICS, addons_on=False)
okc4, whyc4 = leg_for_leg(after_c4, "bank_aggr_base_after_c4_trades.csv")
assert okc4 and len(after_c4) == 106 and round(sum(r["net"] for r in after_c4), 2) == 102969.50, whyc4
print("LEG 0b: after-c4 intermediate reproduced leg-for-leg (106 legs, +102,969.50)")

STACK = build_stack(reentry_statics=A_STATICS)
okst, whyst = leg_for_leg(STACK, "bank_aggr_final_trades.csv")
assert okst and len(STACK) == 115 and round(sum(r["net"] for r in STACK), 2) == 123471.50, whyst
_, STACK_ADDONS, _nc_adm = admit_addons(after_c4)
assert len(STACK_ADDONS) == 9, len(STACK_ADDONS)
print("LEG 0c: TUNED STACK v1 reproduced leg-for-leg (115 legs, +123,471.50)")

# EVE-19 construction (verbatim from the positive-tuning session)
ns1_early = [r for r in STACK if r["family"] == "NS1_second" and mins(r["entry_time"]) < mins("10:30")]
assert len(ns1_early) == 3, [(r["date"], r["entry_time"]) for r in ns1_early]
skip_keys = frozenset(r["leg_key"] for r in ns1_early)
v22_skipped = [r for r in v22_rows if r["leg_key"] not in skip_keys]
v22_skipped_form = [dict(date=r["date"], direction=r["direction"], exit_reason=r["exit_reason"],
                         exit_time=r["exit_time"], net=r["net"]) for r in v22_skipped]
der19, blk19, nc19 = derive_reentries(v22_skipped_form, 0, "A_reentry")
assert len(der19) == 15 and len(nc19) == 0, (len(der19), nc19)
der19_statics = [{**d, "strike": int(d["strike"])} for d in der19]
INCUMBENT = build_stack(skip_ns1_keys=skip_keys, reentry_statics=der19_statics,
                        addons_from=STACK_ADDONS)
oki, whyi = leg_for_leg(INCUMBENT, "bank_positive_tuning_2026-11-10_eve19_trades.csv")
assert oki, whyi
INC_BATT = battery(INCUMBENT)
_summ = json.load(open(TR / "bank_positive_tuning_2026-11-10_summary.json"))
_eb = _summ["eve19"]["candidate"]
for fld in ("total", "H1", "H2", "ex_top3_legs", "ex_top3_days"):
    assert abs(INC_BATT[fld] - _eb[fld]) < 0.005, (fld, INC_BATT[fld], _eb[fld])
assert INC_BATT["n_legs"] == 111 and abs(INC_BATT["total"] - 127351.50) < 0.005
assert all(v > 0 for v in INC_BATT["months"].values()), INC_BATT["months"]
OUT["anchor"] = dict(incumbent="TUNED STACK v2 (EVE-19)", legs=111,
                     total=INC_BATT["total"], battery=INC_BATT,
                     leg_for_leg="exact vs bank_positive_tuning_2026-11-10_eve19_trades.csv",
                     summary_battery_match="total/H1/H2/ex-top3 legs+days equal the frozen session summary")
print(f"ANCHOR OK: incumbent TUNED STACK v2 rebuilt leg-for-leg — 111 legs, "
      f"+{INC_BATT['total']:.2f}; H1 {INC_BATT['H1']} / H2 {INC_BATT['H2']}; "
      f"exT3 legs {INC_BATT['ex_top3_legs']}; all months positive")


# =====================================================================
# VARIANT MACHINERY — transforms + variant-aware book builder
# =====================================================================
def c4_ext(p, date, expiry):
    if p["lock"] is None and date != expiry:
        return {**p, "lock": 90.0, "tgt2": 180.0}
    return dict(p)

def transform(p_base, p_fin, direction, variant):
    """The pre-registered exit-geometry transforms. p_base = assembly
    params; p_fin = c4-extended final incumbent params. Returns the
    variant's final params for the leg."""
    if variant == "identity":
        return dict(p_fin)
    if variant == "T-B1a":
        if p_base["trig"] == 90:
            return {"stop": p_fin["stop"], "trig": 90.0, "lock": 30.0, "tgt2": None}
        return dict(p_fin)
    if variant == "T-B1b":
        if p_base["trig"] == 90:
            return {"stop": p_fin["stop"], "trig": 58.0, "lock": 10.0, "tgt2": None}
        return dict(p_fin)
    if variant == "T-B2a":
        if direction == "PE":
            return {**p_fin, "stop": 40.0}
        return dict(p_fin)
    if variant == "T-B2b":
        if direction == "PE":
            return {**p_fin, "stop": 60.0}
        return dict(p_fin)
    if variant == "T-B2c":
        if direction == "PE" and p_base["lock"] is None and p_base["tgt2"] is None:
            return {"stop": p_fin["stop"], "trig": 50.0, "lock": 0.0, "tgt2": 90.0}
        return dict(p_fin)
    raise ValueError(variant)

VARIANTS = ["T-B1a", "T-B1b", "T-B2a", "T-B2b", "T-B2c"]
VARIANT_LABELS = {
    "T-B1a": "LOCK30-TRAIL (trig-90 legs: at +90 lock entry+30, trail to SQ)",
    "T-B1b": "LOCK10-AT-58 (trig-90 legs: arm at +58, lock entry+10, trail to SQ)",
    "T-B2a": "PE-STOP40 (PE legs only: stop -40 vs -50)",
    "T-B2b": "PE-STOP60 (PE legs only: stop -60 vs -50)",
    "T-B2c": "PE-BE50 (PLAIN PE legs: arm +50, floor entry, target +90)",
}

def pipe_rows_v(variant, delay=0, cand_map=None):
    out = []
    for r in rows21:
        k = r["leg_key"]; meta = LEG[k]
        if is_or_pe_early_row(r): continue
        if k in skip_keys: continue
        p_fin = c4_ext(meta["p"], meta["date"], meta["expiry"])
        p_v = transform(meta["p"], p_fin, meta["direction"], variant)
        s = replay_mod(meta["cs"], meta["entry_time"], p_v, delay=delay,
                       arm30=meta["family"] == "NS1_second")
        if s is None:
            assert delay and cand_map is not None and k in cand_map, k
            out.append(dict(cand_map[k])); continue
        out.append(dict(date=meta["date"], direction=meta["direction"], family=meta["family"],
                        rep=meta["rep"], entry_time=meta["entry_time"],
                        entry_premium=s["entry"], exit_time=s["exit_time"],
                        exit_premium=s["exit"], exit_reason=s["exit_reason"],
                        net=s["net"], leg_key=k, dev30=s["dev30"],
                        maxfav=s["maxfav"], src="pipe",
                        _pbase=dict(meta["p"]), _pfin=p_fin, _pv=p_v))
    return out

def addon_rows_v(variant, delay=0, cand_map=None):
    out = []
    for leg, p in STACK_ADDONS:
        p_fin = c4_ext(p, leg["date"], leg["expiry"])
        p_v = transform(p, p_fin, leg["direction"], variant)
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        s = replay_mod(cs, leg["entry_time"], p_v, delay=delay,
                       arm30=leg.get("family", "BASE") == "NS1_second")
        key = (leg["date"], leg["direction"], leg["entry_time"])
        if s is None:
            assert delay and cand_map is not None and key in cand_map, key
            out.append(dict(cand_map[key])); continue
        out.append(dict(date=leg["date"], direction=leg["direction"],
                        family=leg.get("family", "BASE"), rep=leg["rep"],
                        entry_time=leg["entry_time"], entry_premium=s["entry"],
                        exit_time=s["exit_time"], exit_premium=s["exit"],
                        exit_reason=s["exit_reason"], net=s["net"], leg_key=key,
                        dev30=s["dev30"], maxfav=s["maxfav"], src="addon",
                        _pbase=dict(p), _pfin=p_fin, _pv=p_v))
    return out

def reentry_rows_v(variant, der_legs):
    out = []
    for lg in der_legs:
        pd = prem_day(lg["expiry"], lg["strike"], lg["direction"], lg["date"])
        assert pd is not None and lg["entry_time"] in pd, lg
        p_v = transform(G0, G0, lg["direction"], variant)
        xt, xp, reason = sim_variant(pd, lg["entry_time"], float(lg["entry_premium"]), p_v)
        out.append(dict(date=lg["date"], direction=lg["direction"], family="EVE06_REENTRY",
                        rep="EVE06a", entry_time=lg["entry_time"],
                        entry_premium=float(lg["entry_premium"]), exit_time=xt,
                        exit_premium=xp, exit_reason=reason,
                        net=round((xp - float(lg["entry_premium"])) * LOT - COST, 2),
                        leg_key=(lg["date"], lg["direction"], lg["entry_time"]),
                        dev30=None, maxfav=None, src="reentry",
                        strike=lg["strike"], expiry=lg["expiry"],
                        trigger_time=lg["trigger_time"],
                        _pbase=dict(G0), _pfin=dict(G0), _pv=p_v))
    return out

def build_book_v(variant, delay=0, cand_map=None):
    """Full stack book under a variant. delay=6 builds the placebo twin:
    pipe/add-on legs re-replayed at delay 6 under the same geometry
    (no delayed entry -> candidate net via cand_map); the re-entry set
    is the +60-min shifted derivation from the variant's own v22-form
    book, scored under the variant geometry."""
    # v22-form rows (no c4) under the variant, undelayed — derivation base
    form_rows = []
    for r in rows21:
        k = r["leg_key"]; meta = LEG[k]
        if is_or_pe_early_row(r): continue
        if k in skip_keys: continue
        p_v = transform(meta["p"], meta["p"], meta["direction"], variant)
        s = replay_mod(meta["cs"], meta["entry_time"], p_v,
                       arm30=meta["family"] == "NS1_second")
        assert s is not None, k
        form_rows.append(dict(date=meta["date"], direction=meta["direction"],
                              exit_reason=s["exit_reason"], exit_time=s["exit_time"],
                              net=s["net"]))
    der, blk, nc = derive_reentries(form_rows, 60 if delay else 0, "TB")
    rows = pipe_rows_v(variant, delay=delay, cand_map=cand_map)
    rows += addon_rows_v(variant, delay=delay, cand_map=cand_map)
    rows += reentry_rows_v(variant, der)
    info = dict(der_legs=[(d["date"], d["direction"], d["entry_time"]) for d in der],
                blocked=[(b["date"], b["trigger"], b["realised"]) for b in blk],
                nc=nc, form_rows=len(form_rows))
    return rows, info

# builder self-check: the identity variant must reproduce the anchored
# incumbent through THIS builder too (same legs, same nets)
_id_rows, _id_info = build_book_v("identity")
assert len(_id_rows) == 111, len(_id_rows)
_idmap = {r["leg_key"]: r for r in _id_rows}
for r in INCUMBENT:
    m = _idmap.get(r["leg_key"])
    assert m is not None and abs(m["net"] - r["net"]) < 0.005 \
        and m["exit_time"] == r["exit_time"] and m["exit_reason"] == r["exit_reason"], r
assert len(_id_info["nc"]) == 0
print("BUILDER CHECK: identity variant through build_book_v == anchored incumbent (111 legs)")

# ---- incumbent param distribution + per-variant touch counts ---------
def pkey(p):
    return (p["stop"], p["trig"], p["lock"], p["tgt2"])
dist = defaultdict(lambda: {"n": 0, "CE": 0, "PE": 0, "net": 0.0})
for r in INCUMBENT:
    m = _idmap[r["leg_key"]]
    d = dist[pkey(m["_pfin"])]
    d["n"] += 1; d[r["direction"]] += 1; d["net"] = round(d["net"] + r["net"], 2)
OUT["param_distribution_final"] = {
    f"stop{int(k[0])}/trig{int(k[1])}/lock{('None' if k[2] is None else int(k[2]))}/tgt2{('None' if k[3] is None else int(k[3]))}": v
    for k, v in sorted(dist.items(), key=lambda kv: -kv[1]["n"])}
touch = {}
for v in VARIANTS:
    n_t, n_t_pe = 0, 0
    for r in INCUMBENT:
        m = _idmap[r["leg_key"]]
        pv = transform(m["_pbase"], m["_pfin"], r["direction"], v)
        if pkey(pv) != pkey(m["_pfin"]):
            n_t += 1; n_t_pe += (r["direction"] == "PE")
    touch[v] = dict(legs_touched=n_t, pe_touched=n_t_pe)
OUT["variant_touch_counts"] = touch
print("PARAM DISTRIBUTION (final incumbent params):",
      json.dumps(OUT["param_distribution_final"]))
print("TOUCH COUNTS:", json.dumps(touch))

# ---- fill audit for param-variant books -------------------------------
def fill_audit(rows):
    """Every exit premium must be one of the variant's own level fills
    for that leg (entry - stop / + trig / + lock / + tgt2, plus the
    entry level itself for NS1_second arm30 lock_stop legs) or the
    frozen machinery's own close/open exit for that leg type:
    pipe/add-on close exits (square_off / runner_square_off) fill at
    the exit bar's CLOSE; re-entry square_off exits at the 15:10 bar
    OPEN (the frozen sim_g0 convention) and path_end at the last
    bar's close. NOTE: no exit-bar range test is applied to level
    fills — the frozen replay convention fills a stop level on a
    gap-through bar AT the level even when the level lies outside
    that bar's range (verified byte-identical in the incumbent's own
    rows, e.g. 2026-04-10 CE runner_stop at entry+90 on a bar whose
    high was below the level); incumbent and variants share the
    convention, so the gate comparison is like-for-like."""
    addon_cs = {}
    for leg, p in STACK_ADDONS:
        addon_cs[(leg["date"], leg["direction"], leg["entry_time"])] = \
            candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    viol = []
    for r in rows:
        if r["src"] == "pipe":
            cs = LEG[r["leg_key"]]["cs"]
        elif r["src"] == "addon":
            cs = addon_cs[r["leg_key"]]
        else:
            cs = None
        if cs is not None:
            bars = {b[0]: b for b in cs}
        else:
            pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
            bars = {t: (t,) + v + (0,) for t, v in pd.items()}
        b = bars.get(r["exit_time"])
        if b is None:
            viol.append((r["date"], r["entry_time"], "exit bar absent")); continue
        e, xp = r["entry_premium"], r["exit_premium"]
        pv = r["_pv"]
        levels = {e - pv["stop"], e + pv["trig"]}
        if pv["lock"] is not None: levels.add(e + pv["lock"])
        if pv["tgt2"] is not None: levels.add(e + pv["tgt2"])
        if r["family"] == "NS1_second": levels.add(e)  # arm30 BE floor
        if any(abs(xp - lv) < 1e-9 for lv in levels):
            continue
        if r["src"] == "reentry" and r["exit_time"] == "15:10":
            expect, what = b[1], "15:10 bar open (frozen re-entry SQ)"
        else:
            expect, what = b[4], "exit-bar close"
        if abs(xp - expect) > 1e-9:
            viol.append((r["date"], r["entry_time"],
                         f"exit {xp} neither a variant level nor the {what} "
                         f"{expect} ({r['exit_reason']})"))
    return viol

def admission_audit(cand_rows):
    """Pipe/add-on entry keys + entry premiums must equal the
    incumbent's; re-entry deltas are reported, not hidden."""
    inc_pa = {r["leg_key"]: r for r in INCUMBENT if r["src"] in ("pipe", "addon")}
    cand_pa = {r["leg_key"]: r for r in cand_rows if r["src"] in ("pipe", "addon")}
    probs = []
    if set(inc_pa) != set(cand_pa):
        probs.append(f"pipe/addon key sets differ: inc {len(inc_pa)} vs cand {len(cand_pa)}")
    for k in set(inc_pa) & set(cand_pa):
        if abs(inc_pa[k]["entry_premium"] - cand_pa[k]["entry_premium"]) > 0.005:
            probs.append(f"entry premium changed at {k}")
    inc_re = {(r["date"], r["direction"], r["entry_time"]) for r in INCUMBENT if r["src"] == "reentry"}
    cand_re = {(r["date"], r["direction"], r["entry_time"]) for r in cand_rows if r["src"] == "reentry"}
    return probs, sorted(cand_re - inc_re), sorted(inc_re - cand_re)

# =====================================================================
# T-B1 / T-B2 — gate runs
# =====================================================================
OUT["variants"] = {}
RESULTS = {}
for v in VARIANTS:
    cand, info = build_book_v(v)
    cand_map = {r["leg_key"]: r for r in cand}
    plac, pinfo = build_book_v(v, delay=6, cand_map=cand_map)
    plac_total = round(sum(r["net"] for r in plac), 2)
    cb, fails = gate_check(cand, INC_BATT, plac_total, nc=len(info["nc"]))
    viol = fill_audit(cand)
    if viol: fails.append(f"fill audit violations: {viol[:5]} (n={len(viol)})")
    aprobs, re_gained, re_lost = admission_audit(cand)
    if aprobs: fails.append(f"admission audit: {aprobs[:3]}")
    resum = write_trades(cand, f"tuning_bank_2026-11-12_{v.lower().replace('-', '')}_trades.csv")
    if not (resum["n"] == cb["n_legs"] and abs(resum["net"] - cb["total"]) < 0.005):
        fails.append(f"re-sum mismatch {resum} vs {cb['total']}")
    strict_pass = not fails
    # task bar: beat OR match the incumbent total with no other gate-leg failure
    other_fails = [f for f in fails if not f.startswith("total ")]
    match_bar = abs(cb["total"] - INC_BATT["total"]) < 0.005 and not other_fails
    verdict = "PASS" if strict_pass else ("MATCH (task bar only)" if match_bar else "FAIL")
    RESULTS[v] = dict(rows=cand, batt=cb, fails=fails, verdict=verdict,
                      placebo_total=plac_total)
    OUT["variants"][v] = dict(
        label=VARIANT_LABELS[v], battery=cb, placebo_delay6_total=plac_total,
        placebo_reentry_shifted_legs=len(pinfo["der_legs"]),
        gate_fails=fails, verdict=verdict,
        changed_legs=changed_legs(cand, INCUMBENT),
        months_delta=months_delta(cb, INC_BATT),
        reentry_gained=re_gained, reentry_lost=re_lost,
        reentry_blocked=info["blocked"], derivation_nc=info["nc"],
        fill_audit_violations=viol, independent_resum=resum)
    print(f"{v} {VARIANT_LABELS[v]}: incumbent {INC_BATT['total']} -> candidate "
          f"{cb['total']} (placebo delay-6 {plac_total}); legs {cb['n_legs']}; "
          f"changed {len(OUT['variants'][v]['changed_legs'])}; verdict {verdict}; fails={fails}")


# =====================================================================
# T-B3 — owner ladder applied to the incumbent's 111 legs
# (locked design 2026-11-03; entries frozen, exits only)
# =====================================================================
L_STAGES = (30, 58, 82, 100); L_LOCKS = (5, 15, 25); L_STOP = 20.0; L_SQ = "15:10"

def ladder_sim(bars, spotday, direction, entry_time, et_override=None):
    """ladder_bank_score.simulate semantics on dict inputs:
    bars {t: (o,h,l,c)} = the traded contract's premium bars;
    spotday {t: (o,h,l,c)} = the day's spot bars. Stage tests use
    spot CLOSES vs the entry bar's spot OPEN; floors ratchet on the
    highest stage reached; T4 (checked before the floor on the same
    bar) exits at that bar's premium close; hard stop = premium close
    <= entry-20 before any stage; no exit -> close of the 15:10 bar."""
    et = et_override or entry_time
    if et not in bars or et not in spotday or L_SQ not in bars:
        return None
    entry = bars[et][0]
    entry_spot = spotday[et][0]
    sign = 1 if direction == "CE" else -1
    floor0 = entry - L_STOP
    times = sorted(t for t in bars if et <= t <= L_SQ)
    if not times:
        return None
    highest = 0
    for t in times:
        if t not in spotday:
            return None
        pclose = bars[t][3]
        fav = sign * (spotday[t][3] - entry_spot)
        stage_now = sum(1 for s in L_STAGES if fav >= s)
        if stage_now > highest:
            highest = stage_now
        if highest == 4:
            return t, pclose, "T4_EXIT", 4
        floor = floor0 if highest == 0 else entry + L_LOCKS[highest - 1]
        if pclose <= floor:
            return t, pclose, ("HARD_STOP" if highest == 0 else f"LOCK_FLOOR_T{highest}"), highest
    return L_SQ, bars[L_SQ][3], "SQUARE_OFF", highest

def leg_bars_candles(index, strike, direction, date, expiry):
    cs = candles(index, strike, direction, date, expiry)
    if not cs:
        return {}
    return {b[0]: (b[1], b[2], b[3], b[4]) for b in cs}

def incumbent_leg_ref(r):
    """(premium bars dict, strike, expiry, index) for an incumbent leg
    from its own frozen source."""
    if r["src"] == "pipe":
        m = LEG[r["leg_key"]]
        leg = lbk[r["leg_key"]]
        return ({b[0]: (b[1], b[2], b[3], b[4]) for b in m["cs"]},
                int(leg["strike"]), leg["expiry"], leg["index"])
    if r["src"] == "addon":
        leg, p = next(a for a in STACK_ADDONS
                      if (a[0]["date"], a[0]["direction"], a[0]["entry_time"]) == r["leg_key"])
        return (leg_bars_candles(leg["index"], leg["strike"], leg["direction"],
                                 leg["date"], leg["expiry"]),
                int(leg["strike"]), leg["expiry"], leg["index"])
    pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
    return pd, int(r["strike"]), r["expiry"], "BANKNIFTY"

lad_rows, lad_nc, lad_entry_check = [], [], 0
for r in INCUMBENT:
    bars, strike, expiry, index = incumbent_leg_ref(r)
    if bars is None or r["entry_time"] not in bars or \
            abs(bars[r["entry_time"]][0] - r["entry_premium"]) > 0.005:
        lad_nc.append((r["date"], r["direction"], r["entry_time"],
                       "entry premium reconstruction failed"))
        continue
    lad_entry_check += 1
    s = ladder_sim(bars, SPOT[r["date"]], r["direction"], r["entry_time"])
    if s is None:
        lad_nc.append((r["date"], r["direction"], r["entry_time"], "ladder sim NC"))
        continue
    xt, xp, reason, stage = s
    assert abs(xp - bars[xt][3]) < 1e-9  # every ladder exit is a bar close
    lad_rows.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                         rep=r["rep"], entry_time=r["entry_time"],
                         entry_premium=r["entry_premium"], exit_time=xt,
                         exit_premium=xp, exit_reason=reason,
                         net=round((xp - r["entry_premium"]) * LOT - COST, 2),
                         leg_key=r["leg_key"], src=r["src"], stage=stage))
lad_by_key = {r["leg_key"]: r for r in lad_rows}
# placebos: flipped-direction + shifted-entry (+60 min), NC legs count
# at their candidate net (the EVE-18 P1 convention, disclosed)
def ladder_placebo(mode):
    out = []
    for r in INCUMBENT:
        cand = lad_by_key.get(r["leg_key"])
        bars, strike, expiry, index = incumbent_leg_ref(r)
        s = None
        if mode == "flipped":
            fb = leg_bars_candles(index, strike,
                                  "PE" if r["direction"] == "CE" else "CE",
                                  r["date"], expiry)
            if fb and r["entry_time"] in fb:
                s = ladder_sim(fb, SPOT[r["date"]], r["direction"], r["entry_time"])
                if s is not None:
                    entry = fb[r["entry_time"]][0]
                    out.append(dict(r, entry_premium=entry, exit_time=s[0],
                                    exit_premium=s[1], exit_reason=s[2],
                                    net=round((s[1] - entry) * LOT - COST, 2)))
                    continue
        else:
            et60 = add_min(r["entry_time"], 60)
            if bars and et60 in bars and et60 <= L_SQ:
                s = ladder_sim(bars, SPOT[r["date"]], r["direction"],
                               r["entry_time"], et_override=et60)
                if s is not None:
                    entry = bars[et60][0]
                    out.append(dict(r, entry_time=et60, entry_premium=entry,
                                    exit_time=s[0], exit_premium=s[1],
                                    exit_reason=s[2],
                                    net=round((s[1] - entry) * LOT - COST, 2)))
                    continue
        if cand is not None:
            out.append(dict(cand))  # NC -> candidate net
    return out
plac_flip = ladder_placebo("flipped")
plac_shift = ladder_placebo("shifted")
flip_total = round(sum(r["net"] for r in plac_flip), 2)
shift_total = round(sum(r["net"] for r in plac_shift), 2)
lb_batt, lb_fails = gate_check(lad_rows, INC_BATT, max(flip_total, shift_total),
                               nc=len(lad_nc))
resum_lad = write_trades(lad_rows, "tuning_bank_2026-11-12_tb3_trades.csv")
if not (resum_lad["n"] == lb_batt["n_legs"] and abs(resum_lad["net"] - lb_batt["total"]) < 0.005):
    lb_fails.append(f"re-sum mismatch {resum_lad} vs {lb_batt['total']}")
lb_other = [f for f in lb_fails if not f.startswith("total ")]
lb_verdict = "PASS" if not lb_fails else \
    ("MATCH (task bar only)" if abs(lb_batt["total"] - INC_BATT["total"]) < 0.005
     and not lb_other else "FAIL")
RESULTS["T-B3"] = dict(rows=lad_rows, batt=lb_batt, fails=lb_fails,
                       verdict=lb_verdict,
                       placebo_total=max(flip_total, shift_total))
OUT["variants"]["T-B3"] = dict(
    label="LADDER-STACK (owner ladder T1 +30/+5, T2 +58/+15, T3 +82/+25, "
          "T4 +100 exit; hard stop premium close -20; SQ 15:10 close) "
          "on all 111 incumbent legs, entries frozen",
    battery=lb_batt, placebo_flipped_total=flip_total,
    placebo_shifted_total=shift_total, gate_fails=lb_fails,
    verdict=lb_verdict, changed_legs=changed_legs(lad_rows, INCUMBENT),
    months_delta=months_delta(lb_batt, INC_BATT),
    entry_reconstruction=f"{lad_entry_check}/111 legs reproduce their recorded entry premium",
    candidate_nc=lad_nc, independent_resum=resum_lad,
    stage_distribution={s: sum(1 for r in lad_rows if r["stage"] == s) for s in range(5)})
print(f"T-B3 LADDER-STACK: incumbent {INC_BATT['total']} -> candidate {lb_batt['total']} "
      f"(placebos flipped {flip_total} / shifted {shift_total}); legs {lb_batt['n_legs']}; "
      f"NC {len(lad_nc)}; verdict {lb_verdict}; fails={lb_fails}")

# =====================================================================
# NOVEMBER COUNTERFACTUALS — subprocess helper (fresh process; the
# November assembly cannot run under this process's Jan-Oct restriction)
# =====================================================================
proc = subprocess.run([sys.executable, str(TR / "tuning_bank_2026-11-12_nov.py")],
                      capture_output=True, text=True, timeout=2400)
nov = None
for line in proc.stdout.splitlines():
    if line.startswith("RESULT_JSON:"):
        nov = json.loads(line[len("RESULT_JSON:"):])
if nov is None:
    OUT["november_error"] = dict(returncode=proc.returncode,
                                 stdout_tail=proc.stdout[-2000:],
                                 stderr_tail=proc.stderr[-2000:])
    print("NOVEMBER HELPER FAILED:", proc.returncode, proc.stderr[-500:])
else:
    OUT["november"] = nov
    assert abs(nov["identity"]["total"] - (-960.00)) < 0.005, nov["identity"]
    for v in VARIANTS + ["T-B3"]:
        OUT["variants"][v]["november_counterfactual"] = nov["variants"][v]
    print(f"NOVEMBER CF: incumbent stack Nov 2-12 = {nov['identity']['total']} "
          f"(asserted == scored ledger -960.00); " +
          "; ".join(f"{v} {nov['variants'][v]['total']}" for v in VARIANTS + ["T-B3"]))

# ---- December ranking (computed): PASS first, then MATCH, then FAIL,
# by gated total within each class; incumbent = the standing default.
_rank_class = {"PASS": 0, "MATCH (task bar only)": 1, "FAIL": 2}
ranking = sorted(RESULTS.items(),
                 key=lambda kv: (_rank_class[kv[1]["verdict"]], -kv[1]["batt"]["total"]))
OUT["december_ranking"] = [
    dict(rank=i + 1, variant=k, verdict=v["verdict"], gated_total=v["batt"]["total"],
         placebo_total=v["placebo_total"],
         november_cf=(nov["variants"][k]["total"] if nov else None))
    for i, (k, v) in enumerate(ranking)]
OUT["december_default"] = ("TUNED STACK v2 (incumbent) remains the Bank December "
                           "primary unless a variant above is a strict PASS")
(TR / "tuning_bank_2026-11-12_results.json").write_text(json.dumps(OUT, indent=1, default=str))
print("RANKING:", json.dumps(OUT["december_ranking"]))
print("DONE — tuning_bank_2026-11-12_results.json written")
