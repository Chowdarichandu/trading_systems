#!/usr/bin/env python3
"""BANK NIFTY FAST-EARNER TUNING 2026-11-12 (owner directive 2026-11-12
20:57 IST: Bank Nifty is the FIRST AND SOLE EARNER focus; trades must
make money FAST — resolved within minutes; Nifty gets no programme).
Paper only, real money Rs 0. Basis: Bank Nifty option premiums per
1 lot (30), Rs 220/trade, UNIQUE-ONCE. Frozen November primaries are
never modified; output = December candidates only.

================ SPEC FROZEN BEFORE ANY SCORING =================
DATA-RESOLUTION HONESTY: premium data is 5-minute candles. A "1-3
minute" hold is NOT verifiable on this data — intrabar ordering is
unknowable. The verifiable form of the owner's spec: exits resolved
on the entry bar or the next 1-2 bars (<= ~10 minutes from the entry
bar's open). Nothing finer is claimed anywhere in this programme.
Intrabar convention (the workspace's frozen one, shared by the
incumbent machinery): within a bar the STOP is checked before the
TARGET; level exits fill AT the level; time-stop exits fill at the
bar's close.

ENTRY STREAMS (both causal, existing, frozen — entries never change;
the incumbent re-entry set is part of stream A exactly as recorded,
the ladder build's own rule: entries unchanged, only exits change):
  (A) TUNED STACK v2's 111 legs (anchor: rebuilt leg-for-leg vs
      bank_positive_tuning_2026-11-10_eve19_trades.csv, +Rs 127,351.50
      Jan-Oct, asserted BEFORE any variant is scored).
  (B) The NS1 second-leg stream standalone: the NS1_second legs of
      the frozen causal pipeline (assemble6/rows21 — the same
      generator the November legacy book draws from), INCLUDING the
      3 early legs EVE-19 skips inside the stack (the standalone
      stream has no EVE-19 layer). FE-4 anchor: each leg's recorded
      pipeline exit reproduced exactly before scoring.

EXIT VARIANTS (pre-registered, frozen, identical on both streams;
FE-1..FE-3 REPLACE the exit geometry of every leg in the stream —
incumbent params play no role; bars counted positionally from the
entry bar = bar 0):
  FE-1: target +50 / stop -50 premium points; if neither hits during
        bars 0-2, exit at the CLOSE of bar 2 (2nd bar after entry).
  FE-2: target +30 / stop -40; time-stop at the close of bar 2.
  FE-3: stop -50 until some bar's HIGH reaches +30, which ARMS a
        breakeven stop at the entry premium effective from the NEXT
        bar (the frozen replay_mod arm semantics); target +90;
        hard time-stop at the CLOSE of bar 3 (3rd bar after entry).
  FE-4: CONTROL — the incumbent exit geometry of each stream
        (stack: the frozen eve19 rows; NS1: the recorded pipeline
        exits). No re-simulation: the recorded rows ARE FE-4.
  Series-end rule (all FE variants): bars are scanned only while
  bar time <= 15:10; if the day/series ends before the time-stop bar
  without a hit, exit at the close of the last scanned bar
  (reason time_stop_eod).

GATE (standing controls gate, same run, bars unmoved), per variant
per stream, candidate vs that stream's FE-4 control:
  total must BEAT FE-4; total must BEAT the delay-1-bar placebo twin
  (same variant geometry, entry shifted 1 bar; a leg with no delayed
  entry counts at its candidate net — the workspace convention;
  delay-6 twin also computed and reported as the secondary placebo);
  halves rule (verbatim from the aggressive tune's gate_check);
  ex-top-3 legs AND days must be > 0 and >= FE-4's; no month that is
  green under FE-4 flips red; no exit-before-entry; NC == 0.
  Audits, all in-run: (i) timing — exit_time >= entry_time and
  bars_held >= 0 for every leg; (ii) admission — variant leg keys and
  entry premiums identical to FE-4's (exits only); (iii) feature
  timing / causality — every leg re-simulated on its candle series
  TRUNCATED at its own exit bar must reproduce the identical exit
  (no post-exit data can influence the exit); (iv) fill audit —
  every exit premium is one of the variant's own levels (entry-stop /
  entry / entry+target) or the exit bar's close for time-stop exits;
  (v) independent re-sum — trades CSVs written, re-read, re-summed.
  Reported for every variant: total, legs, Rs/month, win rate, and
  the HOLD-TIME distribution (median bars to exit; % resolved on the
  entry bar / within 1 bar / within 2 bars; exit-reason counts) —
  the "fast" property is demonstrated, not asserted.

OWNER'S ACCEPTANCE TEST (in addition to the gate, applied exactly):
  November counterfactual over Nov 2-10 — trading days Nov 2, 3, 4,
  5, 6, 9 (Nov 10 = Diwali holiday, market closed) — computed by the
  helper tuning_bank_fast_2026-11-12_nov.py from the frozen November
  records (stream A: november_shadow_stack_bank_log.csv legs in the
  window; stream B: the NS1 legs of november_paper_bank_log.csv in
  the window) on real November premium candles, FE-4 = the recorded
  log nets. A variant "works" for the owner only if its window net
  is PROFITABLE (> 0). GATE PASS + owner-test FAIL = NOT promoted.
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
# THE FAST-EXIT SIMULATOR (spec frozen in the header)
# =====================================================================
FE_PARAMS = {"FE-1": dict(stop=50.0, tgt=50.0, tstop=2, arm=None),
             "FE-2": dict(stop=40.0, tgt=30.0, tstop=2, arm=None),
             "FE-3": dict(stop=50.0, tgt=90.0, tstop=3, arm=30.0)}
FE_LABELS = {"FE-1": "FAST +50/-50, time-stop close of bar 2",
             "FE-2": "FAST +30/-40, time-stop close of bar 2",
             "FE-3": "FAST arm-BE at +30, target +90, stop -50, time-stop close of bar 3",
             "FE-4": "CONTROL — incumbent geometry of the stream"}

def sim_fast(cs, entry_time, variant, delay=0):
    """Bar-by-bar fast-exit simulation on a candle list. Stop checked
    before target within a bar (frozen convention); FE-3's breakeven
    arm takes effect from the NEXT bar (frozen replay_mod arm
    semantics). Returns dict or None (no entry possible)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs) or cs[i0][0] > "15:10": return None
    entry = cs[i0][1]
    prm = FE_PARAMS[variant]
    stop_lvl, tgt_lvl = entry - prm["stop"], entry + prm["tgt"]
    armed = False
    last = None
    for k in range(0, prm["tstop"] + 1):
        i = i0 + k
        if i >= len(cs): break
        t, o, h, l, cl, v = cs[i]
        if t > "15:10": break
        last = (i, cs[i])
        eff_stop = entry if armed else stop_lvl
        if l <= eff_stop:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=eff_stop,
                        exit_reason="be_stop" if armed else "stop", bars_held=i - i0)
        if h >= tgt_lvl:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=tgt_lvl,
                        exit_reason="target", bars_held=i - i0)
        if prm["arm"] is not None and h >= entry + prm["arm"]:
            armed = True
        if k == prm["tstop"]:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=cl,
                        exit_reason="time_stop", bars_held=i - i0)
    if last is None: return None
    i, b = last
    return dict(entry_time=cs[i0][0], entry=entry, exit_time=b[0], exit=b[4],
                exit_reason="time_stop_eod", bars_held=i - i0)

def score_stream_fast(legs, variant, delay=0, cand_rows=None):
    """Score one stream under one FE variant. With delay>0 (placebo),
    a leg whose delayed entry is impossible counts at its candidate
    net (cand_rows keyed identically)."""
    out, nc_delay = [], 0
    for j, lg in enumerate(legs):
        s = sim_fast(lg["cs"], lg["entry_time"], variant, delay=delay)
        if s is None:
            assert delay and cand_rows is not None
            nc_delay += 1
            out.append(dict(cand_rows[j])); continue
        out.append(dict(date=lg["date"], direction=lg["direction"], family=lg["family"],
                        rep=lg["rep"], entry_time=s["entry_time"],
                        entry_premium=s["entry"], exit_time=s["exit_time"],
                        exit_premium=s["exit"], exit_reason=s["exit_reason"],
                        bars_held=s["bars_held"],
                        net=round((s["exit"] - s["entry"]) * LOT - COST, 2),
                        leg_idx=j))
    return out, nc_delay

def hold_stats(rows):
    hs = [r["bars_held"] for r in rows]
    reasons = defaultdict(int)
    for r in rows: reasons[r["exit_reason"]] += 1
    return dict(median_bars=median(hs), mean_bars=round(sum(hs) / len(hs), 2),
                pct_entry_bar=round(100.0 * sum(1 for x in hs if x == 0) / len(hs), 1),
                pct_within_1=round(100.0 * sum(1 for x in hs if x <= 1) / len(hs), 1),
                pct_within_2=round(100.0 * sum(1 for x in hs if x <= 2) / len(hs), 1),
                pct_within_3=round(100.0 * sum(1 for x in hs if x <= 3) / len(hs), 1),
                max_bars=max(hs), win_rate_pct=round(100.0 * sum(1 for r in rows if r["net"] > 0) / len(rows), 1),
                reasons=dict(sorted(reasons.items())))

def audits_fast(legs, cand_rows, variant):
    """Admission + causality (truncation) + fill audits. Returns a list
    of violation strings (empty = clean)."""
    probs = []
    prm = FE_PARAMS[variant]
    for j, (lg, r) in enumerate(zip(legs, cand_rows)):
        if r["entry_time"] != lg["entry_time"] or abs(r["entry_premium"] - lg["entry_premium"]) > 0.005:
            probs.append(f"admission: entry changed at leg {j} {lg['date']} {lg['entry_time']}")
            continue
        # causality: re-simulate on the series truncated at the exit bar
        times = [b[0] for b in lg["cs"]]
        xi = times.index(r["exit_time"])
        s2 = sim_fast(lg["cs"][:xi + 1], lg["entry_time"], variant)
        if s2 is None or s2["exit_time"] != r["exit_time"] or abs(s2["exit"] - r["exit_premium"]) > 1e-9 \
                or s2["exit_reason"] != r["exit_reason"] or s2["bars_held"] != r["bars_held"]:
            probs.append(f"causality: truncated re-sim differs at leg {j} {lg['date']}")
        # fill audit
        e, xp = r["entry_premium"], r["exit_premium"]
        levels = {e - prm["stop"], e + prm["tgt"]}
        if prm["arm"] is not None: levels.add(e)
        if not any(abs(xp - lv) < 1e-9 for lv in levels):
            b = lg["cs"][xi]
            if r["exit_reason"] not in ("time_stop", "time_stop_eod") or abs(xp - b[4]) > 1e-9:
                probs.append(f"fill: exit {xp} not a variant level nor the exit-bar "
                             f"close at leg {j} {lg['date']} ({r['exit_reason']})")
    return probs

def gate_fast(cand_rows, base_batt, placebo_total, nc=0):
    """The aggressive tune's gate_check, base = the stream's FE-4."""
    cb = battery(cand_rows)
    fails = []
    if not cb["total"] > base_batt["total"]:
        fails.append(f"total {cb['total']} !> FE-4 {base_batt['total']}")
    if not cb["total"] > placebo_total:
        fails.append(f"placebo not beaten: cand {cb['total']} vs delay-1 placebo {placebo_total}")
    halves_ok = (cb["H1"] >= base_batt["H1"] and cb["H2"] >= base_batt["H2"]) or \
                (cb["H1"] >= 0 and cb["H2"] >= 0)
    if not halves_ok:
        fails.append(f"halves {cb['H1']}/{cb['H2']} vs FE-4 {base_batt['H1']}/{base_batt['H2']}")
    if not (cb["ex_top3_legs"] > 0 and cb["ex_top3_legs"] >= base_batt["ex_top3_legs"]):
        fails.append(f"ex-top3 legs {cb['ex_top3_legs']} vs FE-4 {base_batt['ex_top3_legs']}")
    if not (cb["ex_top3_days"] > 0 and cb["ex_top3_days"] >= base_batt["ex_top3_days"]):
        fails.append(f"ex-top3 days {cb['ex_top3_days']} vs FE-4 {base_batt['ex_top3_days']}")
    for m, v in base_batt["months"].items():
        if v > 0 and cb["months"][m] < 0:
            fails.append(f"month {m} flips green->red ({v} -> {cb['months'][m]})")
    tv = [r for r in cand_rows if r["exit_time"] < r["entry_time"] or r["bars_held"] < 0]
    if tv: fails.append(f"timing violations: {len(tv)} exit-before-entry")
    if nc: fails.append(f"NOT_COMPUTED {nc}")
    return cb, fails

# =====================================================================
# GATE RUNS — per stream, per variant, vs the stream's FE-4 control
# =====================================================================
def fe4_rows(legs):
    return [dict(date=l["date"], direction=l["direction"], family=l["family"],
                 rep=l["rep"], entry_time=l["entry_time"],
                 entry_premium=l["entry_premium"],
                 exit_time=l["fe4"]["exit_time"], exit_premium=l["fe4"]["exit_premium"],
                 exit_reason=l["fe4"]["exit_reason"], bars_held=l["fe4"]["bars_held"],
                 net=l["fe4"]["net"], leg_idx=j) for j, l in enumerate(legs)]

OUT["results"] = {}
for sname, legs, base_batt in (("A_stack", STREAM_A, A_BATT), ("B_ns1", STREAM_B, B_BATT)):
    f4 = fe4_rows(legs)
    tag = sname.lower()
    resum4 = write_trades(f4, f"tuning_bank_fast_2026-11-12_{tag}_fe4_trades.csv")
    assert resum4["n"] == len(f4) and abs(resum4["net"] - base_batt["total"]) < 0.005
    OUT["results"][f"{sname}|FE-4"] = dict(
        label=FE_LABELS["FE-4"], battery=base_batt, hold=hold_stats(f4),
        verdict="CONTROL", independent_resum=resum4)
    print(f"{sname} FE-4 (control): {base_batt['n_legs']} legs, total {base_batt['total']}, "
          f"win {hold_stats(f4)['win_rate_pct']}%, median hold {hold_stats(f4)['median_bars']} bars")
    for v in ("FE-1", "FE-2", "FE-3"):
        cand, nc = score_stream_fast(legs, v)
        assert nc == 0, (sname, v, nc)
        plac1, ncd1 = score_stream_fast(legs, v, delay=1, cand_rows=cand)
        plac6, ncd6 = score_stream_fast(legs, v, delay=6, cand_rows=cand)
        p1_total = round(sum(r["net"] for r in plac1), 2)
        p6_total = round(sum(r["net"] for r in plac6), 2)
        cb, fails = gate_fast(cand, base_batt, p1_total, nc=0)
        probs = audits_fast(legs, cand, v)
        if probs: fails.append(f"audits: {probs[:4]} (n={len(probs)})")
        resum = write_trades(cand, f"tuning_bank_fast_2026-11-12_{tag}_{v.lower().replace('-', '')}_trades.csv")
        if not (resum["n"] == cb["n_legs"] and abs(resum["net"] - cb["total"]) < 0.005):
            fails.append(f"re-sum mismatch {resum} vs {cb['total']}")
        verdict = "GATE PASS" if not fails else "GATE FAIL"
        OUT["results"][f"{sname}|{v}"] = dict(
            label=FE_LABELS[v], battery=cb, hold=hold_stats(cand),
            placebo_delay1_total=p1_total, placebo_delay1_nc_legs=ncd1,
            placebo_delay6_total=p6_total, placebo_delay6_nc_legs=ncd6,
            gate_fails=fails, verdict=verdict, independent_resum=resum,
            audit_violations=probs)
        print(f"{sname} {v} {FE_LABELS[v]}: FE-4 {base_batt['total']} -> {cb['total']} "
              f"(delay-1 placebo {p1_total}; delay-6 {p6_total}); legs {cb['n_legs']}; "
              f"win {hold_stats(cand)['win_rate_pct']}%; median hold "
              f"{hold_stats(cand)['median_bars']} bars; {verdict}; fails={fails}")

# =====================================================================
# OWNER'S ACCEPTANCE TEST — November counterfactual (helper process)
# =====================================================================
p = subprocess.run([sys.executable, str(TR / "tuning_bank_fast_2026-11-12_nov.py")],
                   capture_output=True, text=True)
_lines = [l for l in p.stdout.splitlines() if l.startswith("RESULT_JSON:")]
assert _lines, p.stdout[-3000:] + "\n" + p.stderr[-3000:]
NOV = json.loads(_lines[0][len("RESULT_JSON:"):])
OUT["november"] = NOV
for sname in ("A_stack", "B_ns1"):
    for v in ("FE-1", "FE-2", "FE-3", "FE-4"):
        w = NOV[sname][v]["window_net"]
        print(f"NOV {sname} {v}: Nov 2-10 window net {w} "
              f"({NOV[sname][v]['window_legs']} legs) — owner test "
              f"{'PASS (profitable)' if w > 0 else 'FAIL'}")

# ---- final classification: gate x owner test --------------------------
for key, res in OUT["results"].items():
    if key.endswith("FE-4"): continue
    sname, v = key.split("|")
    w = NOV[sname][v]["window_net"]
    res["nov_window_net"] = w
    res["owner_test"] = "PASS" if w > 0 else "FAIL"
    gate_ok = res["verdict"] == "GATE PASS"
    res["final"] = ("PASSES BOTH" if gate_ok and w > 0 else
                    "GATE PASS / OWNER TEST FAIL" if gate_ok else
                    "OWNER TEST PASS / GATE FAIL" if w > 0 else "FAILS BOTH")
    print(f"FINAL {key}: gate {res['verdict']}, owner test {res['owner_test']} "
          f"(window {w}) -> {res['final']}")

json.dump(OUT, open(TR / "tuning_bank_fast_2026-11-12_results.json", "w"), indent=1, default=str)
print("WROTE tuning_bank_fast_2026-11-12_results.json")
