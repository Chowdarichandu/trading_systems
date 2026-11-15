#!/usr/bin/env python3
"""SOLID-60 PROGRAMME 2026-11-13 (owner directive 2026-11-13 06:33 IST).
The owner's simple spec, built and gated exactly as he set it:
entries must be SOLID (nobody has perfect entries/exits, but the
trades entered should be good); book profit at the target, then
TRAIL; win rate at least 60-70% - NOT 50-50. Bank Nifty first
(sole-earner priority), then Nifty. Paper only, real money Rs 0.
December candidates only; frozen November books untouched.

================ SPEC FROZEN BEFORE ANY SCORING =================
ENTRY STREAMS (causal, existing, frozen - entries never change):
  BANK-A: TUNED STACK v2's 111 legs (anchor: rebuilt leg-for-leg vs
    bank_positive_tuning_2026-11-10_eve19_trades.csv, +Rs 127,351.50
    Jan-Oct, asserted in-run before any variant is scored).
  BANK-B: the NS1 second-leg stream standalone (16 legs of the frozen
    pipeline, incl. the 3 early legs EVE-19 skips inside the stack;
    anchor = its recorded pipeline exits, asserted leg-for-leg).
  NIFTY: TUNED v1's 74 legs (DEC-S1 minus component-B PE legs;
    anchor +Rs 103,050.25 via the R7/R8 harness assembly + score_r6,
    cross-checked against nifty_next_phase_trades.csv, asserted).
  Lots/costs: Bank 30, Nifty 65, Rs 220/trade, UNIQUE-ONCE.
  Intrabar convention (frozen): within a bar the STOP is checked
  before the TARGET; level exits fill AT the level.

PART A - ENTRY QUALITY (features knowable AT ENTRY, registered):
  agree  = number of the four U1 systems ((lA) v2, V5 v2, Skill V3,
           Volrix (b)) whose FIRST signal that day in the leg's
           direction has entry_time <= the leg's entry_time (sysmap:
           Bank build_sysmap_bank, Nifty build_sysmap - the exact
           builders of the prior programmes). Causal by construction.
  second = 1 for confirmation legs by construction: Bank family in
           {NS1_second, EVE06_REENTRY}; Nifty: compA = (component==A)
           plays the anchor-leg role (v1 has no second-leg class).
  tod    = entry_time band: early <=10:30, mid 10:31-12:30,
           late >12:30.
  prem   = entry-premium band: Bank <500 / 500-750 / >750;
           Nifty <150 / 150-300 / >300.
  room_ratio is NOT a stored field on the Jan-Oct streams (it exists
  only in the November legacy spec) - recorded here as an honest
  absence; it is not reconstructed or estimated.
  TIERS (nested, at most 3, rule frozen here):
    ALL     = every leg of the stream.
    SOLID   = agree >= 2 AND entry_time <= 13:30.
    SOLIDS+ = SOLID AND (agree >= 3 OR second==1 [Bank] /
              component==A [Nifty]).
  Part A reports, under the incumbent exits (X-1), every tier's legs,
  win rate, total, expectancy, PLUS one-feature concentration cuts
  (agree / family-or-component / direction / tod / prem / second) -
  the table that shows where the wins actually concentrate.

PART B - TRAIL EXITS (applied on each tier; headline tier = SOLID):
  X-1 CONTROL: the stream's recorded incumbent exits (no re-sim).
  X-2 BOOK-AND-TRAIL: initial stop entry-50. Rungs arm on bar
    CLOSES, effective from the NEXT bar: once the best close reaches
    entry+90 the stop locks to entry+50; thereafter for every
    further +25 of best-close progress beyond +90 the stop steps up
    +25 (stop = entry + 50 + 25*floor((best_close-entry-90)/25)).
    No hard target. Square-off 15:10 (close; series-end: last bar
    <= 15:10 close).
  X-3 OWNER-LADDER TRAIL: initial stop entry-50. Rungs arm on bar
    HIGHS (excursion - the owner's ladder semantics and the frozen
    replay_mod arm convention), effective from the NEXT bar:
    high >= entry+30 -> stop >= entry; high >= entry+58 -> stop >=
    entry+30; high >= entry+82 -> stop >= entry+58; high >=
    entry+100 -> stop >= entry+82 AND the tight trail arms: stop
    steps +10 for every +10 of best-high progress beyond +100
    (stop = entry + 82 + 10*floor((best_high-entry-100)/10)).
    Square-off 15:10 (same series-end rule).
  Within a bar the effective stop is checked (bar low) BEFORE any
  rung update from that bar - a bar can never arm a rung and be
  stopped by it on the same bar.

GATE (standing controls gate, same run, bars unmoved) for every
tier x exit configuration C on stream S (incumbent battery B(S)):
  (a) audits clean: admission (candidate entries identical to the
      stream's), feature-timing/causality (every leg re-simulated on
      its series TRUNCATED at its own exit bar reproduces the
      identical exit), fill audit (every non-square-off exit premium
      is a stop level the variant can produce), NC == 0;
  (b) placebos beaten: delay-1-bar twin of C (same tier, entry
      shifted 1 bar, same exit variant; a leg with no delayed entry
      counts at its candidate net) - X-2/X-3 configs only (X-1's
      geometry is recorded, not simulated; the random placebo binds
      for X-1); AND random-subset placebo: total(C) must exceed the
      95th percentile of 1000 random subsets of S's ALL legs of the
      same size scored under the same exit variant (seed 20261113);
  (c) halves: (H1(C) >= H1(B) and H2(C) >= H2(B)) or (H1(C) >= 0 and
      H2(C) >= 0) - battery() convention of the prior programmes
      (H1 = Jan-May, H2 = Jun-Oct);
  (d) months: no month green under the incumbent flips red under C;
  (e) ex-top-3 legs >= 0; (f) independent re-sum exact.
OWNER'S PASS BARS (pre-registered from his spec, never moved):
  a configuration PASSES only if the gate passes AND win rate
  >= 60% AND total > 0 AND total >= 60% of its stream's incumbent
  total. If nothing passes, the report leads with that plus the
  closest configurations - no bar moved, no waiver language.

NOVEMBER LENS (reported, cannot promote): Nov 2-12 legs of each
stream from the frozen November logs (Bank-A: november_shadow_
stack_bank_log.csv, anchor full-period -960.00; Bank-B: NS1 rows of
november_paper_bank_log.csv, anchor +1,520.00; Nifty: DEC-S1 shadow
log minus B-PE rows, anchor +3,036.50), features from the recorded
November sysmaps (tuning_daily_baseload_2026-11-12_nov_results.json,
cross-validated in its own run), re-exited under X-1/X-2/X-3 on real
November premium candles (november_shadow_data store). Per
configuration: legs, win rate, net.
==================================================================
"""
import csv, json, subprocess, sys
from pathlib import Path
from collections import defaultdict
from statistics import median

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"
OUT = {"session": "tuning_bank_fast_2026-11-12"}

def mins(t):
    h, m = map(int, str(t).split(":")[:2]); return h * 60 + m

# =====================================================================
# machinery (copied from tuning_bank_2026-11-12.py, which copied it
# from bank_positive_tuning_2026-11-10.py / bank_aggressive_tune_score;
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
assert mm0 == 0, f"replay_mod mismatches vs frozen pipeline: {mm0}"
print("REPLAY CHECK: replay_mod reproduces the frozen pipeline 99/99 "
      "(plain assembly params — the pipeline's recorded exits carry no "
      "arm30; the arm30 breakeven arm enters only at the v22/stack "
      "phase, inside stream A's own recorded rows)")

# ---- G0 store machinery (phase-2 copies, for re-entry legs) ----------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
prem_store = json.load(open(TR / "daily2leg/prem_bank.json"))
DAYS = sorted(d for d in spot_raw if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
SPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in spot_raw[d]} for d in DAYS}
TIMES = {d: [b[0] for b in spot_raw[d]] for d in DAYS}
_chain_days = defaultdict(set)
for k, v in prem_store.items():
    for d in v: _chain_days[k.split("|")[0]].add(d)
MONTHLY = sorted(e for e, ds in _chain_days.items() if len(ds) >= 10)

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

def expiry_for(d):
    for e in MONTHLY:
        if d <= e: return e
    present = {k.split("|")[0] for k, v in prem_store.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None

def atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def derive_reentries(base_rows, shift_min=0, set_name="A_reentry"):
    """Phase-2 find_reentry logic (verbatim from tuning_bank_2026-11-12)."""
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
assert len(A_static) == 16 and round(sum(float(r["net_inr"]) for r in A_static), 2) == 6119.00
A_STATICS = [{**r, "strike": int(float(r["strike"]))} for r in A_static]

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

# ---- battery (copied verbatim from bank_aggressive_tune_score.py) -----
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

def write_trades(rows, fname):
    fields = ["date", "direction", "family", "rep", "entry_time", "entry_premium",
              "exit_time", "exit_premium", "exit_reason", "bars_held", "net_inr"]
    with open(TR / fname, "w", newline="") as f:
        w = csv.writer(f); w.writerow(fields)
        for r in sorted(rows, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry_premium"], r["exit_time"], r["exit_premium"],
                        r["exit_reason"], r["bars_held"], r["net"]])
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

# ---- book builders (verbatim from the positive-tuning session) -------
def is_or_pe_early_row(r):
    return r["rep"] == "Skill V3" and r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")

def pipe_rows(delay=0, runner_ext=True, skip_ns1_keys=frozenset()):
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

def replay_addon(leg, p, runner_ext=True, delay=0):
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

def admit_addons(book_rows):
    taken_now = {(r["date"], r["direction"]) for r in book_rows}
    seen, rows, admitted, nc = set(), [], [], 0
    for leg, p in sorted(BD_LEGS, key=lambda x: (x[0]["date"], x[0]["entry_time"])):
        key = (leg["date"], leg["direction"])
        if key in seen: continue
        seen.add(key)
        if key in taken_now: continue
        row = replay_addon(leg, p)
        if row is None: nc += 1; continue
        admitted.append((leg, p)); rows.append(row)
    return rows, admitted, nc

def build_stack(reentry_statics=None, addons_from=None, addons_on=True,
                skip_ns1_keys=frozenset()):
    rows = pipe_rows(runner_ext=True, skip_ns1_keys=skip_ns1_keys)
    if addons_from is not None:
        for leg, p in addons_from:
            row = replay_addon(leg, p)
            assert row is not None, leg
            rows.append(row)
    elif addons_on:
        arows, _, nc = admit_addons(rows)
        assert nc == 0, f"addon NC in build_stack: {nc}"
        rows += arows
    if reentry_statics is not None:
        rows += resim_reentry(reentry_statics)
    return rows

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

_, STACK_ADDONS, _nc_adm = admit_addons(after_c4)
assert len(STACK_ADDONS) == 9, len(STACK_ADDONS)
STACK1 = build_stack(reentry_statics=A_STATICS)
okst, whyst = leg_for_leg(STACK1, "bank_aggr_final_trades.csv")
assert okst and len(STACK1) == 115 and round(sum(r["net"] for r in STACK1), 2) == 123471.50, whyst
print("LEG 0c: TUNED STACK v1 reproduced leg-for-leg (115 legs, +123,471.50)")

ns1_early = [r for r in STACK1 if r["family"] == "NS1_second" and mins(r["entry_time"]) < mins("10:30")]
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
                     total=INC_BATT["total"],
                     leg_for_leg="exact vs bank_positive_tuning_2026-11-10_eve19_trades.csv")
print(f"ANCHOR OK: stream A incumbent rebuilt leg-for-leg — 111 legs, "
      f"+{INC_BATT['total']:.2f}; all months positive")

# =====================================================================
# STREAM ASSEMBLY — every leg carries its own premium candle series
# =====================================================================
def incumbent_leg_ref(r):
    """(premium bars dict, strike, expiry, index) for an incumbent leg
    from its own frozen source (verbatim from tuning_bank_2026-11-12)."""
    if r["src"] == "pipe":
        m = LEG[r["leg_key"]]
        leg = lbk[r["leg_key"]]
        return ({b[0]: (b[1], b[2], b[3], b[4]) for b in m["cs"]},
                int(leg["strike"]), leg["expiry"], leg["index"])
    if r["src"] == "addon":
        leg, p = next(a for a in STACK_ADDONS
                      if (a[0]["date"], a[0]["direction"], a[0]["entry_time"]) == r["leg_key"])
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        return ({b[0]: (b[1], b[2], b[3], b[4]) for b in cs},
                int(leg["strike"]), leg["expiry"], leg["index"])
    pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
    return pd, int(r["strike"]), r["expiry"], "BANKNIFTY"

def bars_held_of(cs, entry_time, exit_time):
    times = [b[0] for b in cs]
    return times.index(exit_time) - times.index(entry_time)

def stream_legs_A():
    legs = []
    for r in INCUMBENT:
        bars_d, strike, expiry, index = incumbent_leg_ref(r)
        assert bars_d is not None and r["entry_time"] in bars_d, r
        cs = [(t,) + tuple(bars_d[t]) + (0.0,) for t in sorted(bars_d)]
        assert abs(cs[[b[0] for b in cs].index(r["entry_time"])][1]
                   - r["entry_premium"]) < 0.005, r
        legs.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                         rep=r["rep"], entry_time=r["entry_time"],
                         entry_premium=r["entry_premium"], strike=strike,
                         expiry=expiry, cs=cs, src=r["src"],
                         fe4=dict(exit_time=r["exit_time"], exit_premium=r["exit_premium"],
                                  exit_reason=r["exit_reason"], net=r["net"],
                                  bars_held=bars_held_of(cs, r["entry_time"], r["exit_time"]))))
    return legs

def stream_legs_B():
    legs = []
    for r in rows21:
        if r["family"] != "NS1_second": continue
        meta = LEG[r["leg_key"]]
        cs = meta["cs"]
        assert cs, r["leg_key"]
        s = replay_mod(cs, r["entry_time"], r["_params"])
        assert s is not None and abs(s["net"] - r["net"]) < 0.005 \
            and s["exit_time"] == r["exit_time"] and s["exit_reason"] == r["exit_reason"], r["leg_key"]
        leg = lbk[r["leg_key"]]
        legs.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                         rep=r["rep"], entry_time=r["entry_time"],
                         entry_premium=s["entry"], strike=int(leg["strike"]),
                         expiry=leg["expiry"], cs=cs, src="ns1",
                         fe4=dict(exit_time=s["exit_time"], exit_premium=s["exit"],
                                  exit_reason=s["exit_reason"], net=s["net"],
                                  bars_held=bars_held_of(cs, r["entry_time"], s["exit_time"]))))
    return legs

STREAM_A = stream_legs_A()
STREAM_B = stream_legs_B()
A_BATT = battery([dict(date=l["date"], net=l["fe4"]["net"]) for l in STREAM_A])
B_BATT = battery([dict(date=l["date"], net=l["fe4"]["net"]) for l in STREAM_B])
assert A_BATT["n_legs"] == 111 and abs(A_BATT["total"] - INC_BATT["total"]) < 0.005
OUT["streams"] = {
    "A_stack": dict(legs=len(STREAM_A), fe4_total=A_BATT["total"],
                    fe4_battery=A_BATT),
    "B_ns1": dict(legs=len(STREAM_B), fe4_total=B_BATT["total"],
                  fe4_battery=B_BATT,
                  note="NS1_second legs of the frozen pipeline (rows21), "
                       "incl. the 3 early legs EVE-19 skips inside the stack"),
}
print(f"STREAM A (stack): {len(STREAM_A)} legs, FE-4 total {A_BATT['total']}")
print(f"STREAM B (NS1 standalone): {len(STREAM_B)} legs, FE-4 total {B_BATT['total']}")

# =====================================================================
# SOLID-60 — sysmaps (agreement features). Builders copied verbatim:
# Bank = build_sysmap_bank from tuning_daily_baseload_2026-11-12.py;
# Nifty = build_sysmap from nifty_engine_r5_ws0.py (standalone form).
# =====================================================================
def build_sysmap_bank_s60():
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "BANKNIFTY" or not et: return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    for r in csv.DictReader(open(TR / "index_options_o1_janoct_trades.csv")):
        if r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2": put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["track"] == "V5-v2": put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_skillV3_jansep_spot.csv")):
        put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_volrixB_jansep_spot.csv")):
        put(r["entry_date"], r["index"], r["direction"], "Volrix (b)", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_premium_october_trades.csv")):
        if r["premium_status"] != "COMPUTED": continue
        if r["version"].startswith("(lA)"): put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["version"].startswith("V5"): put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_skill_tuned_oct30_trades.csv")):
        if r["variant"] == "V3" and r["premium_status"] == "COMPUTED":
            put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    return S

def build_sysmap_nifty_s60():
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "NIFTY" or not et: return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    for r in csv.DictReader(open(TR / "index_options_o1_janoct_trades.csv")):
        if r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2": put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["track"] == "V5-v2": put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_skillV3_jansep_spot.csv")):
        put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_volrixB_jansep_spot.csv")):
        put(r["entry_date"], r["index"], r["direction"], "Volrix (b)", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_premium_october_trades.csv")):
        if r["premium_status"] != "COMPUTED": continue
        if r["version"].startswith("(lA)"): put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["version"].startswith("V5"): put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_skill_tuned_oct30_trades.csv")):
        if r["variant"] == "V3" and r["premium_status"] == "COMPUTED":
            put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    put("2026-10-09", "NIFTY", "CE", "Volrix (b)", "09:20")  # merge hardcode
    return S

SYSMAP_BANK = build_sysmap_bank_s60()
SYSMAP_NIFTY = build_sysmap_nifty_s60()

def agree_of(S, date, direction, entry_time):
    return sum(1 for s, t in S.get((date, direction), {}).items() if t <= entry_time)

# =====================================================================
# NIFTY STREAM — TUNED v1 assembly (verbatim logic from
# tuning_daily_baseload_2026-11-12.py stage_nifty: R7 standing legs +
# R8 gap-fade + R8 expiry sleeve, component tags from the r11 dump;
# v1 = DEC-S1 minus (component B & PE)). Anchor asserted before use.
# =====================================================================
import nifty_engine_r7_harness as R7
import nifty_engine_r8_harness as R8
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import candles_exact
from nifty_engine_r5_harness import replay_r5

NGEOM = dict(R7.STANDING_GEOM)
_NA = R7.standing_legs()
_NB, _nf = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                               with_trend=False, exclude_keys=R7.keys_of(_NA))
_NC, _ne = R8.expiry_sleeve_legs(R7.keys_of(_NA) | R7.keys_of(_NB))
_NDECS1 = _NA + _NB + _NC
_ndump = json.loads((TR / "nifty_engine_r11_decs1_legs.json").read_text())
_ntag = {(d["date"], d["direction"], d["entry_time"], int(d["strike"]),
          d["expiry"]): d["component"] for d in _ndump}
def _ncomp(l):
    return _ntag[(l["date"], l["direction"], l["entry_time"], int(l["strike"]), l["expiry"])]
_NV1 = [l for l in _NDECS1 if not (_ncomp(l) == "B" and l["direction"] == "PE")]
assert len(_NV1) == 74, len(_NV1)
_nres, _nnc, _ = R6.score_r6(_NV1, geom=NGEOM)
assert _nnc == 0 and round(sum(r["net"] for r in _nres), 2) == 103050.25
_nres_by_key = {(r["date"], r["entry_time"], int(r["strike"])): r for r in _nres}
# cross-check vs the recorded CSV stream (the gapguard programme's source)
_ncsv = [r for r in csv.DictReader(open(TR / "nifty_next_phase_trades.csv"))
         if not (r["component"] == "B" and r["direction"] == "PE")]
assert len(_ncsv) == 74 and abs(sum(float(r["net_inr"]) for r in _ncsv) - 103050.25) < 0.01
assert {(r["date"], r["entry_time"], int(r["strike"])) for r in _ncsv} == set(_nres_by_key), \
    "harness v1 leg keys != recorded CSV v1 leg keys"
_prem_nifty = json.load(open(TR / "daily2leg/prem_nifty.json"))
def nifty_bars(strike, dirn, day, exp):
    cs = candles_exact("NIFTY", strike, dirn, day, exp)
    if cs: return [tuple(b) for b in cs]
    cd = _prem_nifty.get(f"{exp}|{int(strike)}|{dirn}", {}).get(day)
    if cd is None: return None
    return [(t,) + tuple(float(x) for x in v) + (0.0,) for t, v in sorted(cd.items())]

def _bars_held(cs, entry_time, exit_time):
    times = [b[0] for b in cs]
    return times.index(exit_time) - times.index(entry_time)

STREAM_N = []
_xv_bad = 0
for l in _NV1:
    bars = nifty_bars(l["strike"], l["direction"], l["date"], l["expiry"])
    assert bars, l
    ref = _nres_by_key[(l["date"], l["entry_time"], int(l["strike"]))]
    rr = replay_r5([list(b) for b in bars], l["entry_time"], **NGEOM)
    if rr is None or abs(rr["net"] - ref["net"]) > 0.005:
        _xv_bad += 1
    times = [b[0] for b in bars]
    ei = times.index(l["entry_time"])
    assert abs(bars[ei][1] - ref["entry"]) < 0.005, l
    STREAM_N.append(dict(date=l["date"], direction=l["direction"],
                         family=f"DEC-S1 {_ncomp(l)}", component=_ncomp(l),
                         rep=ref["rep"], entry_time=l["entry_time"],
                         entry_premium=ref["entry"], strike=int(l["strike"]),
                         expiry=l["expiry"], cs=bars, src="nifty_v1",
                         rec=dict(exit_time=ref["exit_time"], exit_premium=ref["exit"],
                                  exit_reason=ref["exit_reason"], net=ref["net"],
                                  bars_held=_bars_held(bars, l["entry_time"], ref["exit_time"]))))
assert _xv_bad == 0, f"nifty loader cross-validation mismatches: {_xv_bad}"
N_BATT = battery([dict(date=l["date"], net=l["rec"]["net"]) for l in STREAM_N])
assert N_BATT["n_legs"] == 74 and abs(N_BATT["total"] - 103050.25) < 0.005
OUT["streams"]["N_nifty_v1"] = dict(legs=len(STREAM_N), x1_total=N_BATT["total"],
                                   x1_battery=N_BATT,
                                   note="TUNED v1 (DEC-S1 minus B-PE); harness anchor + "
                                        "CSV cross-check + loader cross-validation 74/74")
print(f"STREAM N (Nifty TUNED v1): {len(STREAM_N)} legs, X-1 total {N_BATT['total']}")

# =====================================================================
# UNIFY BANK STREAMS to the common leg shape (rec = recorded exits)
# =====================================================================
def unify_bank(legs, srcname):
    return [dict(date=l["date"], direction=l["direction"], family=l["family"],
                 component=None, rep=l["rep"], entry_time=l["entry_time"],
                 entry_premium=l["entry_premium"], strike=l["strike"],
                 expiry=l["expiry"], cs=l["cs"], src=srcname,
                 rec=dict(l["fe4"])) for l in legs]
STREAMS = {
    "bank_A_stack": dict(index="BANKNIFTY", lot=30, legs=unify_bank(STREAM_A, "bank_A"),
                         inc_batt=A_BATT, sysmap=SYSMAP_BANK, flavour="bank"),
    "bank_B_ns1": dict(index="BANKNIFTY", lot=30, legs=unify_bank(STREAM_B, "bank_B"),
                       inc_batt=B_BATT, sysmap=SYSMAP_BANK, flavour="bank"),
    "nifty_v1": dict(index="NIFTY", lot=65, legs=STREAM_N,
                     inc_batt=N_BATT, sysmap=SYSMAP_NIFTY, flavour="nifty"),
}

# =====================================================================
# FEATURES + TIERS (registered in the header; computed before scoring)
# =====================================================================
def tod_band(t):
    return "early" if t <= "10:30" else ("mid" if t <= "12:30" else "late")
def prem_band(flavour, p):
    if flavour == "bank":
        return "low<500" if p < 500 else ("mid500-750" if p <= 750 else "high>750")
    return "low<150" if p < 150 else ("mid150-300" if p <= 300 else "high>300")

for sname, S in STREAMS.items():
    for lg in S["legs"]:
        lg["agree"] = agree_of(S["sysmap"], lg["date"], lg["direction"], lg["entry_time"])
        if S["flavour"] == "bank":
            lg["second"] = 1 if lg["family"] in ("NS1_second", "EVE06_REENTRY") else 0
            lg["anchor_leg"] = lg["second"]
        else:
            lg["second"] = 0
            lg["anchor_leg"] = 1 if lg["component"] == "A" else 0
        lg["tod"] = tod_band(lg["entry_time"])
        lg["prem_band"] = prem_band(S["flavour"], lg["entry_premium"])
        lg["tier_solid"] = bool(lg["agree"] >= 2 and lg["entry_time"] <= "13:30")
        lg["tier_solids_plus"] = bool(lg["tier_solid"] and (lg["agree"] >= 3 or lg["anchor_leg"] == 1))
    tiers = {"ALL": S["legs"],
             "SOLID": [l for l in S["legs"] if l["tier_solid"]],
             "SOLIDS+": [l for l in S["legs"] if l["tier_solids_plus"]]}
    S["tiers"] = tiers
    print(f"{sname}: tiers ALL={len(tiers['ALL'])} SOLID={len(tiers['SOLID'])} "
          f"SOLIDS+={len(tiers['SOLIDS+'])}")

def wr_stats(rows):
    n = len(rows)
    if n == 0: return dict(legs=0, wins=0, wr_pct=None, total=0.0, expectancy=None)
    wins = sum(1 for r in rows if r["net"] > 0)
    tot = round(sum(r["net"] for r in rows), 2)
    return dict(legs=n, wins=wins, wr_pct=round(100.0 * wins / n, 1), total=tot,
                expectancy=round(tot / n, 2))

def rec_rows(legs):
    return [dict(date=l["date"], direction=l["direction"], family=l["family"],
                 rep=l["rep"], entry_time=l["entry_time"],
                 entry_premium=l["entry_premium"], exit_time=l["rec"]["exit_time"],
                 exit_premium=l["rec"]["exit_premium"],
                 exit_reason=l["rec"]["exit_reason"], bars_held=l["rec"]["bars_held"],
                 net=l["rec"]["net"], leg_id=l["leg_id"]) for l in legs]
for S in STREAMS.values():
    for i, lg in enumerate(S["legs"]): lg["leg_id"] = i

# =====================================================================
# PART A — tier table + feature concentration cuts (under X-1)
# =====================================================================
OUT["partA"] = {}
for sname, S in STREAMS.items():
    pa = {"tiers": {}, "cuts": {}}
    for tname, legs in S["tiers"].items():
        pa["tiers"][tname] = wr_stats(rec_rows(legs))
    def cut(keyfn, labels):
        d = {}
        for lab in labels:
            sub = [l for l in S["legs"] if keyfn(l) == lab]
            if sub: d[lab] = wr_stats(rec_rows(sub))
        return d
    fam_labels = sorted({l["family"] for l in S["legs"]})
    pa["cuts"]["family_or_component"] = cut(lambda l: l["family"], fam_labels)
    pa["cuts"]["agree"] = cut(lambda l: str(l["agree"]), ["0", "1", "2", "3", "4"])
    pa["cuts"]["direction"] = cut(lambda l: l["direction"], ["CE", "PE"])
    pa["cuts"]["tod"] = cut(lambda l: l["tod"], ["early", "mid", "late"])
    pb_labels = (["low<500", "mid500-750", "high>750"] if S["flavour"] == "bank"
                 else ["low<150", "mid150-300", "high>300"])
    pa["cuts"]["prem_band"] = cut(lambda l: l["prem_band"], pb_labels)
    pa["cuts"]["anchor_leg"] = cut(lambda l: str(l["anchor_leg"]), ["0", "1"])
    OUT["partA"][sname] = pa
    print(f"PART A {sname}: " + "; ".join(
        f"{t}: {v['legs']} legs WR {v['wr_pct']}% total {v['total']}"
        for t, v in pa["tiers"].items()))
    # leg-level features dump (Part A deliverable data)
    with open(TR / f"solid60_programme_2026-11-13_{sname}_features.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "component", "rep", "entry_time",
                    "entry_premium", "agree", "second", "anchor_leg", "tod", "prem_band",
                    "tier_solid", "tier_solids_plus", "x1_net"])
        for lg in S["legs"]:
            w.writerow([lg["date"], lg["direction"], lg["family"], lg["component"] or "",
                        lg["rep"], lg["entry_time"], lg["entry_premium"], lg["agree"],
                        lg["second"], lg["anchor_leg"], lg["tod"], lg["prem_band"],
                        int(lg["tier_solid"]), int(lg["tier_solids_plus"]), lg["rec"]["net"]])

# =====================================================================
# PART B — TRAIL SIMULATOR (spec frozen in the header)
# =====================================================================
def sim_trail(cs, entry_time, variant, delay=0):
    """X-2: rungs arm on bar CLOSES (effective next bar).
    X-3: rungs arm on bar HIGHS (effective next bar).
    Stop checked (bar low vs effective stop) BEFORE the rung update
    from the same bar. Initial stop entry-50 for both."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs) or cs[i0][0] > "15:10": return None
    entry = cs[i0][1]
    stop = entry - 50.0
    best_close = None; best_high = None
    last = None
    for i in range(i0, len(cs)):
        t, o, h, l, cl, v = cs[i]
        if t > "15:10": break
        last = (i, cs[i])
        if l <= stop:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=stop,
                        exit_reason="stop" if abs(stop - (entry - 50.0)) < 1e-9 else "lock_stop",
                        bars_held=i - i0)
        if t == "15:10":
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=cl,
                        exit_reason="square_off", bars_held=i - i0)
        if variant == "X-2":
            best_close = cl if best_close is None else max(best_close, cl)
            bc = best_close - entry
            if bc >= 90.0:
                stop = max(stop, entry + 50.0 + 25.0 * int((bc - 90.0) // 25.0))
        else:  # X-3
            best_high = h if best_high is None else max(best_high, h)
            bh = best_high - entry
            if bh >= 30.0: stop = max(stop, entry)
            if bh >= 58.0: stop = max(stop, entry + 30.0)
            if bh >= 82.0: stop = max(stop, entry + 58.0)
            if bh >= 100.0:
                stop = max(stop, entry + 82.0 + 10.0 * int((bh - 100.0) // 10.0))
    if last is None: return None
    i, b = last
    return dict(entry_time=cs[i0][0], entry=entry, exit_time=b[0], exit=b[4],
                exit_reason="square_off_eod", bars_held=i - i0)

def trail_rows(legs, variant, lot, delay=0, cand_by_id=None):
    out, nc_delay = [], 0
    for lg in legs:
        s = sim_trail(lg["cs"], lg["entry_time"], variant, delay=delay)
        if s is None:
            assert delay and cand_by_id is not None
            nc_delay += 1
            out.append(dict(cand_by_id[lg["leg_id"]])); continue
        out.append(dict(date=lg["date"], direction=lg["direction"], family=lg["family"],
                        rep=lg["rep"], entry_time=s["entry_time"],
                        entry_premium=s["entry"], exit_time=s["exit_time"],
                        exit_premium=s["exit"], exit_reason=s["exit_reason"],
                        bars_held=s["bars_held"],
                        net=round((s["exit"] - s["entry"]) * lot - COST, 2),
                        leg_id=lg["leg_id"]))
    return out, nc_delay

def audits_trail(legs, rows, variant):
    """Admission + truncation-causality + fill audits (empty = clean)."""
    probs = []
    by_id = {r["leg_id"]: r for r in rows}
    for lg in legs:
        r = by_id.get(lg["leg_id"])
        if r is None:
            probs.append(f"missing row for leg {lg['leg_id']}"); continue
        if r["entry_time"] != lg["entry_time"] or abs(r["entry_premium"] - lg["entry_premium"]) > 0.005:
            probs.append(f"admission: entry changed {lg['date']} {lg['entry_time']}"); continue
        times = [b[0] for b in lg["cs"]]
        xi = times.index(r["exit_time"])
        s2 = sim_trail(lg["cs"][:xi + 1], lg["entry_time"], variant)
        if s2 is None or s2["exit_time"] != r["exit_time"] or abs(s2["exit"] - r["exit_premium"]) > 1e-9 \
                or s2["exit_reason"] != r["exit_reason"] or s2["bars_held"] != r["bars_held"]:
            probs.append(f"causality: truncated re-sim differs {lg['date']} {lg['entry_time']}")
        e, xp = r["entry_premium"], r["exit_premium"]
        if r["exit_reason"] in ("square_off", "square_off_eod"):
            if abs(xp - lg["cs"][xi][4]) > 1e-9:
                probs.append(f"fill: square-off exit != exit-bar close {lg['date']}")
        else:
            if variant == "X-2":
                levels = {e - 50.0} | {e + 50.0 + 25.0 * k for k in range(0, 25)}
            else:
                levels = {e - 50.0, e, e + 30.0, e + 58.0} | {e + 82.0 + 10.0 * k for k in range(0, 31)}
            if not any(abs(xp - lv) < 1e-9 for lv in levels):
                probs.append(f"fill: exit {xp} not a {variant} stop level {lg['date']} {lg['entry_time']}")
        if r["exit_time"] < r["entry_time"] or r["bars_held"] < 0:
            probs.append(f"timing: exit-before-entry {lg['date']} {lg['entry_time']}")
    return probs

def hold_stats_s60(rows):
    if not rows: return {}
    hs = [r["bars_held"] for r in rows]
    reasons = defaultdict(int)
    for r in rows: reasons[r["exit_reason"]] += 1
    return dict(median_bars=median(hs),
                pct_within_2=round(100.0 * sum(1 for x in hs if x <= 2) / len(hs), 1),
                reasons=dict(sorted(reasons.items())))

RNG_S60 = __import__("random").Random(20261113)
def random_placebo_p95(all_rows, k, seeds=1000):
    """p95 of totals of random k-subsets of ALL-tier rows (same exit
    treatment), nets only."""
    nets = [r["net"] for r in all_rows]
    if k == 0 or k >= len(nets): return None  # k == stream size: placebo undefined (N/A)
    tots = []
    for _ in range(seeds):
        tots.append(round(sum(RNG_S60.sample(nets, k)), 2))
    tots.sort()
    return tots[int(0.95 * seeds) - 1]

def gate_solid(cand_rows, inc_batt, delay1_total, rand_p95, audit_probs, nc=0):
    if not cand_rows:
        cb = dict(n_legs=0, n_days=0, total=0.0, per_month=0.0, per_leg=0.0,
                  legs_per_month=0.0, legs_per_week=0.0,
                  months={m: 0.0 for m in inc_batt["months"]}, H1=0.0, H2=0.0,
                  ex_top3_legs=0.0, top3_legs=[], ex_top3_days=0.0, top3_days=[],
                  worst_day=dict(date=None, net=0.0), worst_drawdown=0.0,
                  pct_positive_days=0.0)
        return cb, ["tier empty — no legs satisfy the registered tier rule"]
    cb = battery(cand_rows)
    fails = []
    if audit_probs: fails.append(f"audits: {audit_probs[:4]} (n={len(audit_probs)})")
    if nc: fails.append(f"NOT_COMPUTED {nc}")
    if delay1_total is not None and not cb["total"] > delay1_total:
        fails.append(f"delay-1 placebo not beaten: {cb['total']} vs {delay1_total}")
    if rand_p95 is not None and not cb["total"] > rand_p95:
        fails.append(f"random-subset placebo not beaten: {cb['total']} vs p95 {rand_p95}")
    halves_ok = (cb["H1"] >= inc_batt["H1"] and cb["H2"] >= inc_batt["H2"]) or \
                (cb["H1"] >= 0 and cb["H2"] >= 0)
    if not halves_ok:
        fails.append(f"halves {cb['H1']}/{cb['H2']} vs incumbent {inc_batt['H1']}/{inc_batt['H2']}")
    if not cb["ex_top3_legs"] >= 0:
        fails.append(f"ex-top3 legs {cb['ex_top3_legs']} < 0")
    for m, v in inc_batt["months"].items():
        if v > 0 and cb["months"][m] < 0:
            fails.append(f"month {m} flips green->red ({v} -> {cb['months'][m]})")
    return cb, fails

# =====================================================================
# PART B SCORING — every tier x exit, per stream; gates + owner bars
# =====================================================================
OUT["results"] = {}
ALL_CONFIGS = []
for sname, S in STREAMS.items():
    inc = S["inc_batt"]; lot = S["lot"]
    x1_all = rec_rows(S["tiers"]["ALL"])
    sim_cache = {}
    for variant in ("X-2", "X-3"):
        rows_all, _ncd = trail_rows(S["tiers"]["ALL"], variant, lot)
        assert _ncd == 0
        sim_cache[variant] = {r["leg_id"]: r for r in rows_all}
    for tname, legs in S["tiers"].items():
        for variant in ("X-1", "X-2", "X-3"):
            if variant == "X-1":
                cand = rec_rows(legs)
                probs = []
                delay1_total = None  # registered: recorded geometry, random placebo binds
            else:
                cand = [sim_cache[variant][lg["leg_id"]] for lg in legs]
                probs = audits_trail(legs, cand, variant)
                cbyid = {r["leg_id"]: r for r in cand}
                twin, ncd = trail_rows(legs, variant, lot, delay=1, cand_by_id=cbyid)
                delay1_total = round(sum(r["net"] for r in twin), 2)
            all_rows_for_placebo = x1_all if variant == "X-1" else \
                [sim_cache[variant][lg["leg_id"]] for lg in S["tiers"]["ALL"]]
            rp95 = random_placebo_p95(all_rows_for_placebo, len(cand))
            cb, fails = gate_solid(cand, inc, delay1_total, rp95, probs, nc=0)
            ws = wr_stats(cand)
            owner = dict(wr_ge_60=(ws["wr_pct"] is not None and ws["wr_pct"] >= 60.0),
                         total_positive=cb["total"] > 0,
                         total_ge_60pct_incumbent=cb["total"] >= 0.6 * inc["total"])
            passed = (not fails) and all(owner.values())
            tag = f"{sname}_{tname}_{variant}".replace("+", "plus")
            resum = write_trades(cand, f"solid60_programme_2026-11-13_{tag}_trades.csv")
            if not (resum["n"] == len(cand) and abs(resum["net"] - cb["total"]) < 0.005):
                fails.append(f"re-sum mismatch {resum} vs {cb['total']}")
                passed = False
            key = f"{sname}|{tname}|{variant}"
            OUT["results"][key] = dict(
                stream=sname, tier=tname, variant=variant, battery=cb, wr=ws,
                hold=hold_stats_s60(cand), delay1_placebo_total=delay1_total,
                random_placebo_p95=rp95, gate_fails=fails,
                gate_pass=(len(fails) == 0), owner_bars=owner,
                incumbent_total=inc["total"],
                verdict="PASS" if passed else "FAIL",
                independent_resum=resum, audit_violations=probs)
            ALL_CONFIGS.append(OUT["results"][key])
            print(f"{key}: legs {cb['n_legs']} WR {ws['wr_pct']}% total {cb['total']} "
                  f"(inc {inc['total']}) delay1 {delay1_total} randp95 {rp95} "
                  f"-> {'PASS' if passed else 'FAIL'} fails={fails}")

# closest configurations (spec-registered selection, no bar moved)
_gate_profit = [c for c in ALL_CONFIGS if c["gate_pass"] and c["battery"]["total"] > 0]
CLOSEST_WR = max(_gate_profit, key=lambda c: c["wr"]["wr_pct"]) if _gate_profit else None
_wr55 = [c for c in ALL_CONFIGS if c["wr"]["wr_pct"] is not None and c["wr"]["wr_pct"] >= 55.0]
CLOSEST_PROFIT = max(_wr55, key=lambda c: c["battery"]["total"]) if _wr55 else None
def _cfg_id(c):
    return f"{c['stream']}|{c['tier']}|{c['variant']}" if c else None
OUT["closest"] = dict(
    highest_wr_among_gatepassing_profitable=(
        dict(config=_cfg_id(CLOSEST_WR), wr_pct=CLOSEST_WR["wr"]["wr_pct"],
             total=CLOSEST_WR["battery"]["total"]) if CLOSEST_WR else None),
    most_profitable_among_wr_ge_55=(
        dict(config=_cfg_id(CLOSEST_PROFIT), wr_pct=CLOSEST_PROFIT["wr"]["wr_pct"],
             total=CLOSEST_PROFIT["battery"]["total"]) if CLOSEST_PROFIT else None),
    passes=[_cfg_id(c) for c in ALL_CONFIGS if c["verdict"] == "PASS"])
print("PASSES:", OUT["closest"]["passes"])
print("CLOSEST (WR):", OUT["closest"]["highest_wr_among_gatepassing_profitable"])
print("CLOSEST (profit):", OUT["closest"]["most_profitable_among_wr_ge_55"])

# =====================================================================
# NOVEMBER LENS — Nov 2-12 counterfactual per configuration
# (frozen November logs; sysmaps from the baseload November helper's
# recorded, cross-validated output; candles from the November store)
# =====================================================================
import aggressive_score as AGG
_sd = TR / "november_shadow_data"
if _sd not in AGG.DIRS: AGG.DIRS.insert(0, _sd)
_novsys = json.loads((TR / "tuning_daily_baseload_2026-11-12_nov_results.json").read_text())["sysmaps"]
def nov_agree(sym, date, direction, entry_time):
    m = _novsys.get(f"{sym}|{date}|{direction}", {})
    return sum(1 for s, t in m.items() if t <= entry_time)

def nov_load(stream):
    legs = []
    if stream == "bank_A_stack":
        src = csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv"))
        for r in src:
            if r["net_inr"] in ("", None): continue
            legs.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                             component=None, rep=r["rep"], strike=int(r["strike"]),
                             expiry=r["expiry"], entry_time=r["entry_time"],
                             entry_premium=float(r["entry_premium"]),
                             rec=dict(exit_time=r["exit_time"],
                                      exit_premium=float(r["exit_premium"]),
                                      exit_reason=r["exit_reason"],
                                      net=float(r["net_inr"]))))
        sym = "BANKNIFTY"
    elif stream == "bank_B_ns1":
        src = csv.DictReader(open(TR / "november_paper_bank_log.csv"))
        for r in src:
            if r["channel"] != "PRIMARY" or r["system_source"] != "NS1": continue
            legs.append(dict(date=r["date"], direction=r["direction"], family="NS1_second",
                             component=None, rep="NS1", strike=int(r["strike"]),
                             expiry=r["expiry"], entry_time=r["entry_time"],
                             entry_premium=float(r["entry_premium"]),
                             rec=dict(exit_time=r["exit_time"],
                                      exit_premium=float(r["exit_premium"]),
                                      exit_reason=r["exit_reason"],
                                      net=float(r["net_inr"]))))
        sym = "BANKNIFTY"
    else:
        src = csv.DictReader(open(TR / "november_shadow_decs1_nifty_log.csv"))
        for r in src:
            if r["net_inr"] in ("", None): continue
            comp = r["system_source"].split()[-1]
            if comp == "B" and r["direction"] == "PE": continue
            legs.append(dict(date=r["date"], direction=r["direction"],
                             family=r["system_source"], component=comp,
                             rep=r["system_source"], strike=int(r["strike"]),
                             expiry=r["expiry"], entry_time=r["entry_time"],
                             entry_premium=float(r["entry_premium"]),
                             rec=dict(exit_time=r["exit_time"],
                                      exit_premium=float(r["exit_premium"]),
                                      exit_reason=r["exit_reason"],
                                      net=float(r["net_inr"]))))
        sym = "NIFTY"
    for lg in legs:
        cs = AGG.candles(sym, lg["strike"], lg["direction"], lg["date"], lg["expiry"])
        assert cs, (stream, lg["date"], lg["strike"])
        times = [b[0] for b in cs]
        ei = next(i for i, t in enumerate(times) if t >= lg["entry_time"])
        assert abs(cs[ei][1] - lg["entry_premium"]) < 0.005, (stream, lg, cs[ei])
        xi = max(i for i, t in enumerate(times) if t <= lg["rec"]["exit_time"])
        lg["cs"] = cs
        lg["rec"]["bars_held"] = xi - ei
        lg["agree"] = nov_agree(sym, lg["date"], lg["direction"], lg["entry_time"])
        if sym == "BANKNIFTY":
            lg["anchor_leg"] = 1 if lg["family"] in ("NS1_second", "EVE06_REENTRY") else 0
        else:
            lg["anchor_leg"] = 1 if lg["component"] == "A" else 0
        lg["tier_solid"] = bool(lg["agree"] >= 2 and lg["entry_time"] <= "13:30")
        lg["tier_solids_plus"] = bool(lg["tier_solid"] and (lg["agree"] >= 3 or lg["anchor_leg"] == 1))
    return legs

OUT["november"] = {}
_NOV_ANCHORS = {"bank_A_stack": -960.00, "bank_B_ns1": 1520.00, "nifty_v1": 3036.50}
for sname in ("bank_A_stack", "bank_B_ns1", "nifty_v1"):
    S = STREAMS[sname]; lot = S["lot"]
    legs = nov_load(sname)
    tot_x1 = round(sum(l["rec"]["net"] for l in legs), 2)
    assert abs(tot_x1 - _NOV_ANCHORS[sname]) < 0.005, (sname, tot_x1)
    for i, lg in enumerate(legs): lg["leg_id"] = 1000 + i
    tiers = {"ALL": legs, "SOLID": [l for l in legs if l["tier_solid"]],
             "SOLIDS+": [l for l in legs if l["tier_solids_plus"]]}
    res = {}
    for tname, tlegs in tiers.items():
        for variant in ("X-1", "X-2", "X-3"):
            if variant == "X-1":
                rows = rec_rows(tlegs)
            else:
                rows, _n = trail_rows(tlegs, variant, lot)
                assert _n == 0
            res[f"{tname}|{variant}"] = wr_stats(rows)
    OUT["november"][sname] = dict(anchor_x1_total=tot_x1, legs=len(legs), configs=res,
                                  leg_detail=[dict(date=l["date"], direction=l["direction"],
                                                   family=l["family"], entry_time=l["entry_time"],
                                                   agree=l["agree"], tier_solid=l["tier_solid"],
                                                   tier_solids_plus=l["tier_solids_plus"],
                                                   x1_net=l["rec"]["net"]) for l in legs])
    print(f"NOV {sname}: {len(legs)} legs, X-1 anchor {tot_x1} OK; "
          f"SOLID legs {len(tiers['SOLID'])}; " +
          "; ".join(f"{t}|{v}: {res[t + '|' + v]['legs']} legs WR {res[t + '|' + v]['wr_pct']} net {res[t + '|' + v]['total']}"
                    for t in ("ALL", "SOLID") for v in ("X-1", "X-2", "X-3")))

json.dump(OUT, open(TR / "solid60_programme_2026-11-13_results.json", "w"), indent=1, default=str)
print("WROTE solid60_programme_2026-11-13_results.json")
print("VERDICTS:", {k: v["verdict"] for k, v in OUT["results"].items()})
