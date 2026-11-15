#!/usr/bin/env python3
"""BANK POSITIVE-TUNING SESSION 2026-11-10 (owner-directed: "work on Bank
and tune it in a way that it turns positive"; market holiday — historical
gate run only). Paper only, real money Rs 0. Basis: Bank Nifty option
premiums per 1 lot (30), Rs 220/trade, UNIQUE-ONCE. The frozen primary
BNF-PAPER-V1 and all existing logs/specs/trade files are never modified.

Incumbent: the TUNED STACK (v22 frame + EVE-06(a) re-entry + c4 runner
extension + v1 NS3/S3 band add-ons; 115 legs, +Rs 123,471.50 Jan-Oct 2026;
frozen record bank_aggr_final_trades.csv). LEG 0: this script rebuilds the
stack from the audited pipeline machinery (the aggressive tune's own
builders, copied — the original scorer is never re-run because it would
rewrite its log/final files) and must match bank_aggr_final_trades.csv
leg-for-leg, and the after-c4 intermediate (+Rs 102,969.50 / 106) and the
phase-1 v22 book (+Rs 91,450.50 / 90), before any candidate is scored.

Candidates (registered in november_rsi_candidates.md BEFORE this run):
  BANK-EVE-18 (Axis A) — ride past the second target: legs with tgt2 no
    longer exit at tgt2; they ride under their own runner lock as floor
    to the floor or the 15:20 square-off. Placebos: P1 leg-identical
    delay-6 twin under the same rule; P2 same ride armed at entry+120.
  BANK-EVE-19 (Axis B) — EVE-09's skip of NS1 legs entering < 10:30,
    applied to the stack frame, with the EVE-06(a) re-entry set
    RE-DERIVED against the skipped book (phase-2 logic, first asserted
    to reproduce the frozen 16 statics on the unmodified book).
  BANK-EVE-20 (Axis C) — ablation set: minus re-entry / minus c4 /
    minus v1, each under the pre-registered simplification gate.
Gate: the aggressive tune's own banking gate (gate_check copied verbatim).
November counterfactuals (Nov 2-9) are evidence only, never the gate.
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"
OUT = {"session": "bank_positive_tuning_2026-11-10"}

def mins(t):
    h, m = map(int, str(t).split(":")[:2]); return h * 60 + m

# =====================================================================
# machinery (copied from bank_aggressive_tune_score.py / phase-2 scorer;
# the originals are never executed — they would rewrite their own files)
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

def replay_ride(cs, entry_time, p, delay=0, arm30=False, ride_arm=None):
    """replay_mod with BANK-EVE-18's runner-phase change ONLY: the tgt2
    exit is removed once the ride is armed — at entry+ride_arm if given
    (placebo P2), else at the leg's own tgt2. The runner lock (entry+lock)
    remains the floor; exits become runner_ride_stop (floor, after tgt2
    was touched) / runner_ride_square_off (15:20 close, after tgt2 was
    touched); untouched legs keep the frozen reason labels."""
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
            arm_lvl = entry + ride_arm if ride_arm is not None else tgt2
            armed = False; touched = False; rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > SQ: break
                if l2 <= stop2:
                    rest = (stop2, "runner_ride_stop" if touched else "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: touched = True
                if not armed and arm_lvl is not None and h2 >= arm_lvl: armed = True
                if not armed and tgt2 is not None and h2 >= tgt2:
                    rest = (tgt2, "runner_target", t2); break
                if t2 == SQ:
                    rest = (cl2, "runner_ride_square_off" if touched else "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]
                rest = (lb[4], "runner_ride_square_off" if touched else "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1, dev30, maxfav)
        if arm30 and h >= entry + 30.0:
            arm_level = 0.0 if arm_level is None else max(arm_level, 0.0)
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

# ---- book builders -------------------------------------------------------
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
        if ride:
            s = replay_ride(meta["cs"], meta["entry_time"], p, delay=delay,
                            arm30=arm30, ride_arm=ride_arm)
        else:
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
    if ride:
        s = replay_ride(cs, leg["entry_time"], p_use, delay=delay, arm30=a30, ride_arm=ride_arm)
    else:
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

def build_placebo_ride(ride_arm=None):
    """EVE-18 P1: leg-identical delay-6 twin of the ride book (aggressive
    tune build_placebo construction): pipe/addon legs re-replayed at
    delay 6 under the same ride rule (a leg with no delay-6 entry counts
    at its candidate net); re-entries replaced by shifted statics."""
    cand = build_stack(ride=True, ride_arm=ride_arm, reentry_statics=A_STATICS,
                       addons_from=STACK_ADDONS)
    addon_map = {a[0] and (a[0]["date"], a[0]["direction"], a[0]["entry_time"]): a
                 for a in STACK_ADDONS}
    out = []
    for r in cand:
        if r["src"] == "reentry": continue
        if r["src"] == "pipe":
            meta = LEG[r["leg_key"]]
            p = meta["p"]
            if p["lock"] is None and meta["date"] != meta["expiry"]:
                p = {**p, "lock": 90.0, "tgt2": 180.0}
            s = replay_ride(meta["cs"], meta["entry_time"], p, delay=6,
                            arm30=meta["family"] == "NS1_second", ride_arm=ride_arm)
            if s is None: out.append(r); continue
            out.append(dict(r, entry_premium=s["entry"], exit_time=s["exit_time"],
                            exit_premium=s["exit"], exit_reason=s["exit_reason"],
                            net=s["net"], dev30=s["dev30"], maxfav=s["maxfav"]))
        else:
            leg, p = addon_map[r["leg_key"]]
            rr = replay_addon(leg, p, runner_ext=True, ride=True,
                              ride_arm=ride_arm, delay=6)
            out.append(rr if rr is not None else r)
    out += resim_reentry(A_SHIFT_STATICS)
    return out

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

# =====================================================================
# LEG 0 — reproduce the incumbent stack before scoring anything
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
# capture the admitted add-on set for placebo/ablation reuse
_, STACK_ADDONS, _nc_adm = admit_addons(after_c4)
assert len(STACK_ADDONS) == 9, len(STACK_ADDONS)
STACK_BATT = battery(STACK)
resum_stack = write_trades(STACK, "bank_positive_tuning_2026-11-10_stack_trades.csv")
assert resum_stack["n"] == 115 and abs(resum_stack["net"] - 123471.50) < 0.005
OUT["leg0"] = dict(v22="90 legs +91,450.50 leg-for-leg", after_c4="106 legs +102,969.50 leg-for-leg",
                   stack="115 legs +123,471.50 leg-for-leg vs bank_aggr_final_trades.csv",
                   stack_battery=STACK_BATT, independent_resum=resum_stack)
print(f"LEG 0c: TUNED STACK reproduced leg-for-leg (115 legs, +123,471.50); "
      f"H1 {STACK_BATT['H1']} / H2 {STACK_BATT['H2']}; exT3 {STACK_BATT['ex_top3_legs']}")

# re-derivation check (EVE-19 machinery): phase-2 logic on the UNMODIFIED
# v22 book must reproduce the frozen statics exactly
v22_csvform = [dict(date=r["date"], direction=r["direction"], exit_reason=r["exit_reason"],
                    exit_time=r["exit_time"], net=r["net"]) for r in v22_rows]
der0, blk0, nc0 = derive_reentries(v22_csvform, 0, "A_reentry")
der0s, blk0s, nc0s = derive_reentries(v22_csvform, 60, "A_shift60")
def statics_match(derived, frozen):
    if len(derived) != len(frozen): return False
    fr = {(r["date"], r["entry_time"]): r for r in frozen}
    for d in derived:
        f = fr.get((d["date"], d["entry_time"]))
        if f is None: return False
        if (d["direction"] != f["direction"] or d["exit_time"] != f["exit_time"]
                or d["exit_reason"] != f["exit_reason"]
                or abs(d["net_inr"] - float(f["net_inr"])) > 0.005
                or abs(d["entry_premium"] - float(f["entry_premium"])) > 0.005):
            return False
    return True
assert statics_match(der0, A_static) and statics_match(der0s, A_shift_static), \
    (len(der0), len(der0s))
print("RE-DERIVATION CHECK: phase-2 logic on the unmodified v22 book reproduces "
      "the frozen re-entry statics exactly (16 real + 15 shifted)")
OUT["leg0"]["rederivation_check"] = "16 real + 15 shifted statics reproduced exactly"

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
# BANK-EVE-18 — ride past the second target (Axis A)
# =====================================================================
cand18 = build_stack(ride=True, reentry_statics=A_STATICS, addons_from=STACK_ADDONS)
p1_18 = build_placebo_ride(None)
p2_18 = build_stack(ride=True, ride_arm=120.0, reentry_statics=A_STATICS,
                    addons_from=STACK_ADDONS)
p1_total = round(sum(r["net"] for r in p1_18), 2)
p2_total = round(sum(r["net"] for r in p2_18), 2)
cb18, fails18 = gate_check(cand18, STACK_BATT, max(p1_total, p2_total))
ch18 = changed_legs(cand18, STACK)
# fill audit on changed legs: a ride exit must be the leg's lock level or
# the 15:20 bar close of its own candle series
viol18 = []
for c in ch18:
    r = next(x for x in cand18 if x["date"] == c["date"] and x["entry_time"] == c["entry_time"]
             and x["direction"] == c["direction"])
    if r["src"] == "pipe":
        cs = LEG[r["leg_key"]]["cs"]; p = LEG[r["leg_key"]]["p"]
        if p["lock"] is None: p = {**p, "lock": 90.0, "tgt2": 180.0}
    else:
        leg, p = next(a for a in STACK_ADDONS if a[0]["date"] == r["date"]
                      and a[0]["direction"] == r["direction"]
                      and a[0]["entry_time"] == r["entry_time"])
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        if p["lock"] is None and leg["date"] != leg["expiry"]:
            p = {**p, "lock": 90.0, "tgt2": 180.0}
    bars = {b[0]: b for b in cs}
    if r["exit_reason"] == "runner_ride_stop" and abs(r["exit_premium"] - (r["entry_premium"] + p["lock"])) > 1e-9:
        viol18.append(("ride_stop_not_lock_level", c["date"]))
    if r["exit_reason"] == "runner_ride_square_off" and abs(r["exit_premium"] - bars[SQ][4]) > 1e-9:
        viol18.append(("ride_sq_not_sq_close", c["date"]))
if viol18: fails18.append(f"fill audit violations: {viol18}")
resum18 = write_trades(cand18, "bank_positive_tuning_2026-11-10_eve18_trades.csv")
if not (resum18["n"] == cb18["n_legs"] and abs(resum18["net"] - cb18["total"]) < 0.005):
    fails18.append(f"re-sum mismatch {resum18} vs {cb18['total']}")
verdict18 = "PASS" if not fails18 else "FAIL"
OUT["eve18"] = dict(candidate=cb18, placebo_p1_delay6_total=p1_total,
                    placebo_p2_arm120_total=p2_total, changed_legs=ch18,
                    months_delta=months_delta(cb18, STACK_BATT),
                    fill_audit_violations=viol18, gate_fails=fails18,
                    independent_resum=resum18, verdict=verdict18)
print(f"EVE-18 ride-past-tgt2: stack {STACK_BATT['total']} -> candidate {cb18['total']} "
      f"(P1 delay-6 {p1_total}, P2 arm+120 {p2_total}); changed legs {len(ch18)}; "
      f"verdict {verdict18}; fails={fails18}")

# =====================================================================
# BANK-EVE-19 — EVE-09 early-NS1 skip on the stack frame (Axis B)
# =====================================================================
ns1_early = [r for r in STACK if r["family"] == "NS1_second" and mins(r["entry_time"]) < mins("10:30")]
assert len(ns1_early) == 3, [(r["date"], r["entry_time"]) for r in ns1_early]
skip_keys = frozenset(r["leg_key"] for r in ns1_early)
skipped_net = round(sum(r["net"] for r in ns1_early), 2)
# interaction (i): re-derive the re-entry set against the skipped v22 book
# (built directly from v22_rows, which carry leg_key)
v22_skipped = [r for r in v22_rows if r["leg_key"] not in skip_keys]
v22_skipped_form = [dict(date=r["date"], direction=r["direction"], exit_reason=r["exit_reason"],
                         exit_time=r["exit_time"], net=r["net"]) for r in v22_skipped]
der19, blk19, nc19 = derive_reentries(v22_skipped_form, 0, "A_reentry")
der19_statics = [{**d, "strike": int(d["strike"])} for d in der19]
lost_reentry = [r for r in A_static
                if (r["date"], r["entry_time"]) not in {(d["date"], d["entry_time"]) for d in der19}]
# interaction (ii): v1 candidates on the skipped (date, direction) keys
skipped_keys_dd = {(r["date"], r["direction"]) for r in ns1_early}
stack_keys_dd = {(r["date"], r["direction"]) for r in STACK}
bd_on_skipped = [(leg, p) for leg, p in BD_LEGS
                 if (leg["date"], leg["direction"]) in skipped_keys_dd
                 and (leg["date"], leg["direction"]) not in stack_keys_dd]
cand19 = build_stack(skip_ns1_keys=skip_keys, reentry_statics=der19_statics,
                     addons_from=STACK_ADDONS)
extra19 = []
for leg, p in bd_on_skipped:
    row = replay_addon(leg, p, runner_ext=True)
    if row is not None:
        cand19.append(row); extra19.append(row)
# placebo: skip the same count (3) of latest-entry NS1 legs, book-level
ns1_all = sorted([r for r in STACK if r["family"] == "NS1_second"],
                 key=lambda r: r["entry_time"], reverse=True)
latest3_keys = {r["leg_key"] for r in ns1_all[:3]}
plac19_rows = [r for r in STACK if r["leg_key"] not in latest3_keys]
plac19_total = round(sum(r["net"] for r in plac19_rows), 2)
cb19, fails19 = gate_check(cand19, STACK_BATT, plac19_total, nc=len(nc19))
resum19 = write_trades(cand19, "bank_positive_tuning_2026-11-10_eve19_trades.csv")
if not (resum19["n"] == cb19["n_legs"] and abs(resum19["net"] - cb19["total"]) < 0.005):
    fails19.append(f"re-sum mismatch {resum19} vs {cb19['total']}")
verdict19 = "PASS" if not fails19 else "FAIL"
OUT["eve19"] = dict(candidate=cb19, placebo_latest_ns1_skip_total=plac19_total,
                    skipped_legs=[dict(date=r["date"], direction=r["direction"],
                                       entry_time=r["entry_time"], exit_reason=r["exit_reason"],
                                       net=r["net"]) for r in ns1_early],
                    skipped_net=skipped_net,
                    rederived_reentries=len(der19), reentry_blocked=blk19,
                    reentry_nc=nc19,
                    lost_reentry_legs=[dict(date=r["date"], direction=r["direction"],
                                            entry_time=r["entry_time"], net=float(r["net_inr"]))
                                       for r in lost_reentry],
                    v1_candidates_on_skipped_keys=len(bd_on_skipped),
                    v1_admitted_extra=[dict(date=r["date"], direction=r["direction"],
                                            entry_time=r["entry_time"], net=r["net"]) for r in extra19],
                    months_delta=months_delta(cb19, STACK_BATT),
                    gate_fails=fails19, independent_resum=resum19, verdict=verdict19)
print(f"EVE-19 NS1-early-skip on stack: stack {STACK_BATT['total']} -> candidate {cb19['total']} "
      f"(placebo latest-NS1-skip {plac19_total}); skipped net {skipped_net}; "
      f"re-derived re-entries {len(der19)} (lost: {[ (r['date']) for r in lost_reentry ]}); "
      f"verdict {verdict19}; fails={fails19}")

# =====================================================================
# BANK-EVE-20 — ablation set (Axis C)
# =====================================================================
def simplification_gate(sub_rows, n_dropped, label):
    sb = battery(sub_rows)
    chrono = sorted(STACK, key=lambda x: (x["date"], x["entry_time"]))
    plac = round(STACK_BATT["total"] - sum(r["net"] for r in chrono[:n_dropped]), 2)
    fails = []
    if not sb["total"] >= STACK_BATT["total"]:
        fails.append(f"net {sb['total']} < incumbent {STACK_BATT['total']}")
    for m, v in STACK_BATT["months"].items():
        if v > 0 and sb["months"][m] < 0:
            fails.append(f"month {m} flips green->red ({v} -> {sb['months'][m]})")
    if not sb["ex_top3_legs"] >= STACK_BATT["ex_top3_legs"]:
        fails.append(f"ex-top3 legs {sb['ex_top3_legs']} < incumbent {STACK_BATT['ex_top3_legs']}")
    if not (sb["H1"] >= STACK_BATT["H1"] and sb["H2"] >= STACK_BATT["H2"]):
        fails.append(f"halves {sb['H1']}/{sb['H2']} vs incumbent {STACK_BATT['H1']}/{STACK_BATT['H2']}")
    if not sb["total"] > plac:
        fails.append(f"chrono placebo not beaten: sub {sb['total']} vs placebo {plac}")
    tv = [r for r in sub_rows if r["exit_time"] < r["entry_time"]]
    if tv: fails.append(f"timing violations: {len(tv)}")
    return sb, plac, fails

sub_a = build_stack(reentry_statics=[], addons_from=STACK_ADDONS)          # minus EVE-06(a)
sub_b = build_stack(runner_ext=False, reentry_statics=A_STATICS,
                    addons_from=STACK_ADDONS)                              # minus c4
sub_c = build_stack(reentry_statics=A_STATICS, addons_on=False)            # minus v1
OUT["eve20"] = {}
for label, sub, fname in (("minus_reentry", sub_a, "bank_positive_tuning_2026-11-10_eve20a_trades.csv"),
                          ("minus_c4", sub_b, "bank_positive_tuning_2026-11-10_eve20b_trades.csv"),
                          ("minus_v1", sub_c, "bank_positive_tuning_2026-11-10_eve20c_trades.csv")):
    n_drop = STACK_BATT["n_legs"] - len(sub)
    sb, plac, fails = simplification_gate(sub, n_drop, label)
    rs = write_trades(sub, fname)
    if not (rs["n"] == sb["n_legs"] and abs(rs["net"] - sb["total"]) < 0.005):
        fails.append(f"re-sum mismatch {rs} vs {sb['total']}")
    OUT["eve20"][label] = dict(battery=sb, n_dropped=n_drop,
                               layer_contribution_in_book=round(STACK_BATT["total"] - sb["total"], 2),
                               chrono_placebo_total=plac, gate_fails=fails,
                               independent_resum=rs,
                               verdict="PASS" if not fails else "FAIL")
    print(f"EVE-20 {label}: sub-book {sb['total']} ({len(sub)} legs) vs stack "
          f"{STACK_BATT['total']}; layer contribution {round(STACK_BATT['total'] - sb['total'], 2)}; "
          f"chrono placebo {plac}; verdict {'PASS' if not fails else 'FAIL'}; fails={fails}")

# =====================================================================
# November counterfactuals (Nov 2-9) — evidence only, never the gate
# =====================================================================
nov = {"stack_backfill_total": 760.00}
bf_rows = list(csv.DictReader(open(TR / "bank_tuned_stack_november_backfill_trades.csv")))
nov["backfill_legs"] = [dict(date=r["date"], component=r["component"], family=r["family"],
                             direction=r["direction"], entry_time=r["entry_time"],
                             exit_reason=r["exit_reason"], net=float(r["net_inr"]))
                        for r in bf_rows if r["net_inr"] not in ("", None)]
# EVE-19: the November stack holds no NS1 leg -> rule cannot fire
nov["eve19"] = (dict(total=760.00, note="no NS1_second leg in the November stack "
                    "(legs: S3-R1 + BASE) — the skip has nothing to act on; unchanged")
                if not any(r["family"] == "NS1_second" for r in nov["backfill_legs"])
                else dict(total=None, note="NS1 leg present — counterfactual not computed"))
# EVE-20: November layer populations
nov["eve20"] = dict(
    minus_reentry=dict(total=760.00, note="0 EVE-06(a) legs in November — unchanged")
    if not any(r["component"].startswith("EVE-06") for r in nov["backfill_legs"]) else
    dict(total=None, note="re-entry leg present — not computed"),
    minus_v1=dict(total=760.00, note="0 v1 add-on legs in November — unchanged")
    if not any(r["component"].startswith("v1") for r in nov["backfill_legs"]) else
    dict(total=None, note="v1 leg present — not computed"),
    minus_c4=dict(total=760.00, note="backfill scored c4_changed = 0 on all six days "
                  "(no PLAIN November leg reached +90) — unchanged")
    if not any(r["component"] == "v22 + c4 runner extension" for r in nov["backfill_legs"]) else
    dict(total=None, note="c4 changed a November leg — not computed"))
# EVE-18: re-sim the two November stack days — run in a subprocess
# (bank_positive_tuning_2026-11-10_nov18.py) because this process has
# restricted bank_r3_setups to Jan-Oct; the helper assembles the
# November days fresh and asserts its incumbent replays first.
try:
    import subprocess
    proc = subprocess.run([sys.executable, str(TR / "bank_positive_tuning_2026-11-10_nov18.py")],
                          capture_output=True, text=True, timeout=900)
    line = [l for l in proc.stdout.strip().splitlines() if l.startswith("{")]
    if proc.returncode == 0 and line:
        nov["eve18"] = json.loads(line[-1])
    else:
        nov["eve18"] = dict(total=None, note=f"NOT_COMPUTED — November helper failed "
                            f"(rc={proc.returncode}): {proc.stderr.strip()[-300:]}")
except BaseException as e:
    nov["eve18"] = dict(total=None, note=f"NOT_COMPUTED — November re-sim unavailable: "
                        f"{type(e).__name__}: {e}")
OUT["november_counterfactual"] = nov
print(f"NOVEMBER counterfactuals: EVE-18 total={nov['eve18'].get('total')} "
      f"({nov['eve18'].get('note', '')[:80]}); EVE-19 {nov['eve19']['total']}; "
      f"EVE-20 all sub-books 760.00 by empty November layer populations")

# =====================================================================
# verdicts + promotion statement
# =====================================================================
OUT["eve18_verdict"] = verdict18
OUT["eve19_verdict"] = verdict19
OUT["eve20_verdicts"] = {k: v["verdict"] for k, v in OUT["eve20"].items()}
passes = []
if verdict18 == "PASS": passes.append("BANK-EVE-18")
if verdict19 == "PASS": passes.append("BANK-EVE-19")
for k, v in OUT["eve20"].items():
    if v["verdict"] == "PASS": passes.append(f"BANK-EVE-20 ({k})")
OUT["promotion"] = (
    f"PROMOTED as TUNED STACK v2: {', '.join(passes)} — recorded in the registry's "
    f"Bank shadow ledger, effective the next trading day, Wed 2026-11-11 (the "
    f"stack shadow's first live day runs v2 rules; v1 stands as the definition "
    f"of the Nov 2-9 backfill rows), logged as a rule replacement, not a restart."
    if passes else
    "NONE — no candidate passed the full gate. The TUNED STACK stays v1 as it "
    "goes live on Wed 2026-11-11; the stack's layers and exits are unchanged.")
print("PROMOTION:", OUT["promotion"])
json.dump(OUT, open(TR / "bank_positive_tuning_2026-11-10_summary.json", "w"), indent=1, default=str)
print("WROTE bank_positive_tuning_2026-11-10_summary.json + candidate trade CSVs")
