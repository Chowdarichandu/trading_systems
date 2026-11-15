#!/usr/bin/env python3
"""BANK AGGRESSIVE TUNE (2026-11-04) — recursive gated cycles on the Bank
book. Owner direction: tune v21/v22 MORE aggressively; phase 1/2 assembly
was too timid. BASE = v22 + EVE-06(a) = +Rs 97,569.50 / 106 legs /
Rs 9,756.95 per month. Target Rs 15,000/month (Rs 1,50,000 Jan-Oct).
Frozen files are never modified; each banked improvement writes a NEW
candidate trade file. Nothing armed, no crons, no November changes.

Machinery: the audited pipeline (assemble6) + the phase-1 replay
(replay_overlay, verified 0-mismatch vs the frozen v21 CSV) extended with
arm flags, + phase-2 store machinery (spot/prem stores, G0) for the
re-entry legs. Basis: Bank Nifty premiums per 1 lot (30), Rs 220/trade,
UNIQUE-ONCE, square-off 15:20 (pipeline legs) / G0 15:10 (re-entry legs).
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
import bank_r6_core
from bank_r6_core import assemble6, v20_inputs
from bank_r7_core import P21, GDGU
from bank_r5_core import (component_legs, volrix_gen_legs, pool_b2,
                          ns1_gen_legs, stream_states, state_at, enrich,
                          _params_for_addon)
from bank_r2_core import seg_of, LOT, COST, WEEKS
from bank_r2_ns1 import V15
from bank_r3_core import admit, BAND
from bank_engine_cycle import FILTERS, _entry_premium

TR = Path.home() / "workspace/trading"
SQ = "15:20"
LOG = TR / "bank_aggressive_tune_2026-11-04.md"

def log(text):
    with open(LOG, "a") as f:
        f.write(text + "\n")
    print(text, flush=True)

def mins(t):
    h, m = map(int, t.split(":")); return h * 60 + m

# ================= replay (phase-1 replay_overlay + arm flags + diagnostics)
def replay_mod(cs, entry_time, p, delay=0, arm30=False, arm50=False,
              arm50_level=0.0, armL=False):
    """Verbatim phase-1 replay_overlay semantics (mode 'open', SQ 15:20)
    with two optional pre-target break-even/give-back arms:
      arm30: bar high >= entry+30 -> stop = entry for subsequent bars
             (the EVE-04 FC-2 lock; incumbent on NS1 legs in the base)
      arm50: bar high >= entry+50 -> stop = entry for subsequent bars
             (this tune's BE-arm family)
    Arms are evaluated at the same loop position as the fc2 check in the
    original (after stop/target checks of the current bar; effective from
    the next bar). Returns the phase-1 fields + diagnostics:
    dev30 = some bar strictly before the exit bar had high >= entry+30;
    maxfav = max high over bars strictly before the exit bar, minus entry.
    """
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

# ================= build the incumbent pipeline + verify =================
pooled, ns1_aud = v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1_aud, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99
prows21, pnc21, _pl, _pd, _p2 = assemble6(
    pooled, ns1_aud, delay=6, ns3_causal_form=True, ns3_filter=GDGU,
    ns3_params=P21, plan=plan)
print(f"pipeline native delay-6 twin (reference only): {len(prows21)} legs, "
      f"{round(sum(r['net'] for r in prows21), 2)} — its taken-set differs by "
      "construction; this tune's placebo is the leg-identical delayed twin")

LEG = {}   # leg_key -> dict(cs, p, family, rep, date, direction, entry_time, expiry)
for r in rows21:
    leg = lbk[r["leg_key"]]
    LEG[r["leg_key"]] = dict(
        cs=candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"]),
        p=r["_params"], family=r["family"], rep=r["rep"], date=r["date"],
        direction=r["direction"], entry_time=r["entry_time"], expiry=leg["expiry"])

# verify replay_mod (delay 0) reproduces the frozen pipeline exactly;
# delay-6 equivalence on the leg-identical twin is spot-verified below
mm0 = 0
for r in rows21:
    s = replay_mod(LEG[r["leg_key"]]["cs"], r["entry_time"], r["_params"])
    if abs(s["net"] - r["net"]) > 0.005 or s["exit_time"] != r["exit_time"] or s["exit_reason"] != r["exit_reason"]:
        mm0 += 1
print(f"REPLAY CHECK: delay0 mismatches={mm0}")
assert mm0 == 0

# ================= v22 assembly (Steps A/B, as phase 1) =================
def is_or_pe_early_row(r):
    return r["rep"] == "Skill V3" and r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")

def pipeline_book(arm30_ns1=True, skip_or_pe=True, delay=0, extra=None, arm50_level=0.0):
    """extra: fn(leg_key, meta) -> dict(arm30=bool, arm50=bool, armL=bool, p_override)
    Returns rows for the 99-leg pipeline after Step A/B (delay twin aware)."""
    out = []
    for r in rows21:
        k = r["leg_key"]; meta = LEG[k]
        if skip_or_pe and is_or_pe_early_row(r):
            continue
        arm30 = arm30_ns1 and meta["family"] == "NS1_second"
        p = meta["p"]; a30, a50, aL = arm30, False, False
        if extra:
            ex = extra(k, meta) or {}
            a30 = ex.get("arm30", a30); a50 = ex.get("arm50", a50); aL = ex.get("armL", aL)
            p = ex.get("p", p)
        s = replay_mod(meta["cs"], meta["entry_time"], p, delay=delay, arm30=a30, arm50=a50,
                       arm50_level=arm50_level, armL=aL)
        assert s is not None, k
        out.append(dict(date=meta["date"], direction=meta["direction"], family=meta["family"],
                        rep=meta["rep"], entry_time=meta["entry_time"], entry_premium=s["entry"],
                        exit_time=s["exit_time"], exit_premium=s["exit"], exit_reason=s["exit_reason"],
                        net=s["net"], leg_key=k, dev30=s["dev30"], maxfav=s["maxfav"], src="pipe"))
    return out

v21_rows = pipeline_book(arm30_ns1=False, skip_or_pe=False)
assert round(sum(r["net"] for r in v21_rows), 2) == 83650.50
stepA_rows = pipeline_book(arm30_ns1=True, skip_or_pe=False)
assert round(sum(r["net"] for r in stepA_rows), 2) == 87370.50, round(sum(r["net"] for r in stepA_rows), 2)
v22_rows = pipeline_book()
assert len(v22_rows) == 90 and round(sum(r["net"] for r in v22_rows), 2) == 91450.50

# ================= re-entry legs (EVE-06a, static from phase 2) =================
inc = list(csv.DictReader(open(TR / "bank_v22_phase2_increments.csv")))
A_static = [r for r in inc if r["set"] == "A_reentry"]
A_shift_static = [r for r in inc if r["set"] == "A_shift60"]
assert len(A_static) == 16 and round(sum(float(r["net_inr"]) for r in A_static), 2) == 6119.00
A_shift_total = round(sum(float(r["net_inr"]) for r in A_shift_static), 2)

def reentry_rows(static):
    return [dict(date=r["date"], direction=r["direction"], family="EVE06_REENTRY",
                 rep="EVE06a", entry_time=r["entry_time"], entry_premium=float(r["entry_premium"]),
                 exit_time=r["exit_time"], exit_premium=float(r["exit_premium"]),
                 exit_reason=r["exit_reason"], net=float(r["net_inr"]),
                 leg_key=(r["date"], r["direction"], r["entry_time"]), dev30=None,
                 maxfav=None, src="reentry", strike=int(float(r["strike"])), expiry=r["expiry"],
                 trigger_time=r["trigger_time"]) for r in static]

BASE_ROWS = v22_rows + reentry_rows(A_static)
assert len(BASE_ROWS) == 106 and round(sum(r["net"] for r in BASE_ROWS), 2) == 97569.50
print(f"BASE VERIFIED: 106 legs, +97,569.50, {97569.50/10:.2f}/month")

# (placebo twin is built in the state section below: leg-identical
# delay-6 replays of the current book + the +60-min shifted re-entries)

# stream/states of the frozen pool, for add-on geometry
from aggressive_score import unique_once
_pool = unique_once(list(pooled) + list(ns1_aud))
_pool = FILTERS["drop_ns1_ce"](_pool)
_pool = FILTERS["drop_prem_400_550"](_pool)
_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in _pool}
STREAM, STATES, TAKEN, _nc0 = stream_states(_by_key, delay=0)

def addon_params(leg):
    """Base-book geometry for an add-on leg: stream-state segment params
    (V15), PLAIN on expiry day — build_base_rows/_params_for_addon rule."""
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    if not cs: return None, None
    probe = replay_mod(cs, leg["entry_time"], dict(stop=50.0, trig=90.0, lock=None, tgt2=None))
    if probe is None: return None, None
    n, tnet = state_at(STREAM, leg["date"], leg["entry_time"])
    seg = seg_of(probe["entry"], n, tnet)
    if leg["date"] == leg["expiry"]:
        return dict(stop=50.0, trig=90.0, lock=None, tgt2=None), seg
    return dict(V15[seg]), seg

def score_addon_leg(leg, delay=0, p=None):
    if p is None:
        p, seg = addon_params(leg)
        if p is None: return None
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    s = replay_mod(cs, leg["entry_time"], p, delay=delay)
    if s is None: return None
    return dict(date=leg["date"], direction=leg["direction"], family=leg.get("family", "BASE"),
                rep=leg["rep"], entry_time=leg["entry_time"], entry_premium=s["entry"],
                exit_time=s["exit_time"], exit_premium=s["exit"], exit_reason=s["exit_reason"],
                net=s["net"], leg_key=(leg["date"], leg["direction"], leg["entry_time"]),
                dev30=s["dev30"], maxfav=s["maxfav"], src="addon")

# ================= battery + gate =================
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

# ================= G0 store machinery (phase-2 copies + BE arm) =================
import json as _json
spot_raw = _json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
prem_store = _json.load(open(TR / "daily2leg/prem_bank.json"))
DAYS = sorted(d for d in spot_raw if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
SPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in spot_raw[d]} for d in DAYS}
TIMES = {d: [b[0] for b in spot_raw[d]] for d in DAYS}
_chain_days = defaultdict(set)
for k, v in prem_store.items():
    for d in v: _chain_days[k.split("|")[0]].add(d)
MONTHLY = sorted(e for e, ds in _chain_days.items() if len(ds) >= 10)

def store_expiry_for(d):
    for e in MONTHLY:
        if d <= e: return e
    present = {k.split("|")[0] for k, v in prem_store.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None

def atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def prem_day(exp, strike, typ, d):
    cd = prem_store.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None: return None
    return {t: tuple(float(x) for x in v) for t, v in cd.items()}

def sim_g0_arm(pd, entry_time, entry_prem, arm_pts=None, arm_level=0.0):
    """Phase-2 sim_g0 + optional BE arm: after a bar whose high reaches
    entry+arm_pts (checked after that bar's stop/target), the stop for
    subsequent bars is the entry premium + arm_level. Stop checked before
    target, fills at the level; square-off at the 15:10 bar open."""
    armed = False
    for t in sorted(pd):
        if t < entry_time or t > "15:05": continue
        o, h, l, c = pd[t]
        eff_stop = entry_prem + arm_level if armed else entry_prem - 50.0
        if l <= eff_stop:
            return t, eff_stop, "lock_stop" if armed else "stop"
        if h >= entry_prem + 90.0:
            return t, entry_prem + 90.0, "target"
        if arm_pts is not None and h >= entry_prem + arm_pts:
            armed = True
    if "15:10" in pd:
        return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def resim_reentry(static_rows, arm_pts=None, arm_level=0.0):
    """Re-simulate recorded re-entry legs (entry fixed) under an optional
    BE arm. Returns rows in book format."""
    out = []
    for r in static_rows:
        pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
        assert pd is not None and r["entry_time"] in pd, r
        xt, xp, reason = sim_g0_arm(pd, r["entry_time"], float(r["entry_premium"]), arm_pts, arm_level)
        out.append(dict(date=r["date"], direction=r["direction"], family="EVE06_REENTRY",
                        rep=r.get("rep", "EVE06a"), entry_time=r["entry_time"],
                        entry_premium=float(r["entry_premium"]), exit_time=xt, exit_premium=xp,
                        exit_reason=reason, net=round((xp - float(r["entry_premium"])) * LOT - COST, 2),
                        leg_key=(r["date"], r["direction"], r["entry_time"]), dev30=None,
                        maxfav=None, src="reentry", strike=r["strike"], expiry=r["expiry"],
                        trigger_time=r["trigger_time"]))
    return out

# verify: un-armed re-simulation reproduces the phase-2 statics exactly
_rs = resim_reentry([{**r, "strike": int(float(r["strike"]))} for r in A_static])
for a, b in zip(_rs, A_static):
    assert a["net"] == float(b["net_inr"]) and a["exit_time"] == b["exit_time"] \
        and a["exit_reason"] == b["exit_reason"], (a, b)
print("RE-ENTRY RE-SIM: reproduces phase-2 statics exactly (16/16)")

A_STATICS = [{**r, "strike": int(float(r["strike"]))} for r in A_static]
A_SHIFT_STATICS = [{**r, "strike": int(float(r["strike"]))} for r in A_shift_static]

# ================= state + book builders =================
STATE = dict(arm50=False, arm50_level=0.0, lock_families=set(), lock_thresh50=False,
             runner_ext=False, runner_ext_any=False,
             addons=[], reentry2=[], ns1_ce_banked=False, band_banked=False,
             consec_nobank=0, banks=[], cycles=[])

def pipe_extra(state):
    def ex(k, meta):
        out = {}
        fam = meta["family"]
        if fam == "NS1_second":
            out["arm30"] = True
        elif fam in state["lock_families"]:
            out["armL" if state["lock_thresh50"] else "arm30"] = True
        if state["arm50"]:
            out["arm50"] = True
        if state["runner_ext"] and meta["p"]["lock"] is None and \
                (meta["date"] != meta["expiry"] or state["runner_ext_any"]):
            out["p"] = {**meta["p"], "lock": 90.0, "tgt2": 180.0}
        return out
    return ex

def build_book(state, delay=0, reentry_mode="real"):
    rows = pipeline_book(delay=delay, extra=pipe_extra(state), arm50_level=state["arm50_level"])
    for ad in state["addons"]:
        leg, p = ad["leg"], ad["p"]
        fam = leg.get("family", "BASE")
        a30 = fam == "NS1_second" or (fam in state["lock_families"] and not state["lock_thresh50"])
        aL = fam in state["lock_families"] and state["lock_thresh50"]
        p_use = p
        if state["runner_ext"] and p["lock"] is None and \
                (leg["date"] != leg["expiry"] or state["runner_ext_any"]):
            p_use = {**p, "lock": 90.0, "tgt2": 180.0}
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        s = replay_mod(cs, leg["entry_time"], p_use, delay=delay,
                       arm30=a30, arm50=state["arm50"], arm50_level=state["arm50_level"], armL=aL)
        assert s is not None, leg
        rows.append(dict(date=leg["date"], direction=leg["direction"], family=fam,
                         rep=leg["rep"], entry_time=leg["entry_time"], entry_premium=s["entry"],
                         exit_time=s["exit_time"], exit_premium=s["exit"], exit_reason=s["exit_reason"],
                         net=s["net"], leg_key=(leg["date"], leg["direction"], leg["entry_time"]),
                         dev30=s["dev30"], maxfav=s["maxfav"], src="addon"))
    arm = 50.0 if state["arm50"] else None
    if delay == 0:
        rows += resim_reentry(A_STATICS, arm, state["arm50_level"])
        rows += resim_reentry(state["reentry2"], arm, state["arm50_level"]) if state["reentry2"] else []
    return rows

def build_placebo(state):
    """Leg-identical delayed twin of the current book, under the same
    mods: pipeline/add-on legs re-replayed at delay 6 (a leg with no
    delay-6 entry bar counts at its candidate net — no timing edge
    assumed); first re-entries replaced by their +60-min shifted twins;
    second re-entries (if any) count at par."""
    base = build_book(state)
    ex_fn = pipe_extra(state)
    out = []
    for r in base:
        if r["src"] == "reentry":
            continue
        if r["src"] == "reentry2":
            out.append(r); continue
        if r["src"] == "pipe":
            meta = LEG[r["leg_key"]]
            ex = ex_fn(r["leg_key"], meta) or {}
            a30 = ex.get("arm30", meta["family"] == "NS1_second")
            s = replay_mod(meta["cs"], meta["entry_time"], ex.get("p", meta["p"]),
                           delay=6, arm30=a30, arm50=ex.get("arm50", False),
                           arm50_level=state["arm50_level"], armL=ex.get("armL", False))
            if s is None:
                out.append(r); continue
            out.append(dict(r, entry_premium=s["entry"], exit_time=s["exit_time"],
                            exit_premium=s["exit"], exit_reason=s["exit_reason"],
                            net=s["net"], dev30=s["dev30"], maxfav=s["maxfav"]))
        else:  # addon
            ad = next(a for a in state["addons"]
                      if (a["leg"]["date"], a["leg"]["direction"],
                          a["leg"]["entry_time"]) == r["leg_key"])
            rr = replay_addon(ad["leg"], ad["p"], state, delay=6)
            out.append(rr if rr is not None else r)
    arm = 50.0 if state["arm50"] else None
    out += resim_reentry(A_SHIFT_STATICS, arm, state["arm50_level"])
    return out

BASE_BATT = battery(build_book(STATE))
assert BASE_BATT["total"] == 97569.50 and BASE_BATT["n_legs"] == 106, BASE_BATT
PB = build_placebo(STATE)
PB_TOTAL = round(sum(r["net"] for r in PB), 2)
print(f"STATE BASE OK: {BASE_BATT['total']} | placebo twin {PB_TOTAL}")
print(f"BASE battery: H1={BASE_BATT['H1']} H2={BASE_BATT['H2']} "
      f"exT3legs={BASE_BATT['ex_top3_legs']} exT3days={BASE_BATT['ex_top3_days']} "
      f"months={BASE_BATT['months']}")

# ================= cycle framework =================
RESULTS = {}

def replay_addon(leg, p, state, delay=0):
    fam = leg.get("family", "BASE")
    a30 = fam == "NS1_second" or (fam in state["lock_families"] and not state["lock_thresh50"])
    aL = fam in state["lock_families"] and state["lock_thresh50"]
    p_use = p
    if state["runner_ext"] and p["lock"] is None and \
            (leg["date"] != leg["expiry"] or state["runner_ext_any"]):
        p_use = {**p, "lock": 90.0, "tgt2": 180.0}
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    s = replay_mod(cs, leg["entry_time"], p_use, delay=delay, arm30=a30, arm50=state["arm50"],
                   arm50_level=state["arm50_level"], armL=aL)
    if s is None: return None
    return dict(date=leg["date"], direction=leg["direction"], family=fam, rep=leg["rep"],
                entry_time=leg["entry_time"], entry_premium=s["entry"], exit_time=s["exit_time"],
                exit_premium=s["exit"], exit_reason=s["exit_reason"], net=s["net"],
                leg_key=(leg["date"], leg["direction"], leg["entry_time"]),
                dev30=s["dev30"], maxfav=s["maxfav"], src="addon")

def admit_candidates(cand_legs, state):
    """UNIQUE-ONCE admission vs the current book (earliest leg per
    (date,direction) wins, as in bank_r3_core.admit). Returns
    (admitted=[(leg,p,row)], key_dropped, nc). Geometry = base-book
    geometry via addon_params; scoring under the current state's mods."""
    book_rows = build_book(state)
    taken = {(r["date"], r["direction"]) for r in book_rows}
    seen, admitted, kd, nc = set(), [], 0, 0
    for leg in sorted(cand_legs, key=lambda x: (x["date"], x["entry_time"])):
        key = (leg["date"], leg["direction"])
        if key in seen: continue
        seen.add(key)
        if key in taken: kd += 1; continue
        p, seg = addon_params(leg)
        if p is None: nc += 1; continue
        row = replay_addon(leg, p, state)
        if row is None: nc += 1; continue
        admitted.append((leg, p, row))
    return admitted, kd, nc

def addon_placebo_total(admitted, state, base_total):
    """Base total + the admitted legs re-scored at delay 6 (shifted-entry
    placebo). A leg with no delay-6 twin counts at its candidate net
    (no timing edge assumed — conservative)."""
    inc = 0.0
    for leg, p, row in admitted:
        r6 = replay_addon(leg, p, state, delay=6)
        inc += r6["net"] if r6 is not None else row["net"]
    return round(base_total + inc, 2)

def run_cycle(cid, title, freeze, november_line, candidate_fn, placebo_fn, on_bank):
    log(f"\n## {cid} — {title}\n\n**Freeze (before scoring):** {freeze}\n")
    base_rows = build_book(STATE)
    base_batt = battery(base_rows)
    cand_rows, nc, extra = candidate_fn()
    placebo_total = placebo_fn(cand_rows, extra)
    cb, fails = gate_check(cand_rows, base_batt, placebo_total, nc)
    resum = write_trades(cand_rows, f"bank_aggr_{cid}_trades.csv")
    if not (resum["n"] == cb["n_legs"] and abs(resum["net"] - cb["total"]) < 0.005):
        fails.append(f"re-sum mismatch {resum} vs {cb['n_legs']}/{cb['total']}")
    banked = not fails
    res = dict(cid=cid, title=title, banked=banked, fails=fails, battery=cb,
               base_total=base_batt["total"], placebo_total=placebo_total,
               delta=round(cb["total"] - base_batt["total"], 2),
               november=november_line, extra=extra)
    RESULTS[cid] = res
    (TR / f"bank_aggr_{cid}_results.json").write_text(json.dumps(res, indent=1, default=str))
    log(f"**Verdict: {'BANKED' if banked else 'REJECTED'}** — candidate "
        f"{cb['total']:+,.2f} ({cb['n_legs']} legs, {cb['per_month']:,.2f}/mo) vs base "
        f"{base_batt['total']:+,.2f}; delta {res['delta']:+,.2f}; placebo {placebo_total:+,.2f}; "
        f"H1 {cb['H1']:+,.2f} / H2 {cb['H2']:+,.2f}; exT3 legs {cb['ex_top3_legs']:+,.2f} / "
        f"days {cb['ex_top3_days']:+,.2f}; worst DD {cb['worst_drawdown']:+,.2f}.")
    if fails:
        log("Gate failures: " + "; ".join(fails))
    log(f"November implication: {november_line}")
    if banked:
        on_bank(extra)
        STATE["consec_nobank"] = 0
        STATE["banks"].append(cid)
        nb = battery(build_book(STATE))
        write_trades(build_book(STATE), f"bank_aggr_base_after_{cid}_trades.csv")
        log(f"New base after {cid}: {nb['total']:+,.2f} ({nb['n_legs']} legs, "
            f"{nb['per_month']:,.2f}/mo). Gap to Rs 1,50,000: {150000 - nb['total']:,.2f}.")
    else:
        STATE["consec_nobank"] += 1
        log(f"No-bank. Consecutive no-bank count: {STATE['consec_nobank']}.")
    STATE["cycles"].append(cid)
    return banked

FAMILY_OF = {"c1a": "F1", "c1b": "F1", "c1c": "F1", "c1d": "F1",
             "c2": "F2", "c3": "F3", "c4": "F4", "c5": "F5", "c6": "F6",
             "v1": "F1", "v2": "F2", "v3": "F3", "v4": "F4", "v5": "F5",
             "v6": "F6"}
# first run's cycles seed the streak history (all Family 1, all no-bank)
HISTORY = [("c1a", "F1", False), ("c1b", "F1", False), ("c1c", "F1", False)]

def stop_check():
    """CLARIFIED rule: SUCCESS at base >= Rs 1,50,000 at any point;
    SATURATED only once every family has been cycled at least once AND
    the trailing no-bank streak is >= 3 cycles spanning >= 2 families."""
    tot = battery(build_book(STATE))["total"]
    if tot >= 150000: return "SUCCESS"
    if len({f for _, f, _ in HISTORY}) >= 6:
        streak = []
        for cid, fam, banked in reversed(HISTORY):
            if banked: break
            streak.append(fam)
        if len(streak) >= 3 and len(set(streak)) >= 2:
            return "SATURATED"
    return None

# ================= FAMILY 1 — entry expansion =================
comps = component_legs(volrix=volrix_gen_legs(-0.01, 15))
_byk = defaultdict(list)
for l in comps: _byk[(l["date"], l["direction"])].append(l)
_drop_ids = set()
for l in comps:
    if l["rep"] != "Skill V3" or l["entry_time"] > "09:55": continue
    if l.get("_readmit"): continue
    others = [o["entry_time"] for o in _byk[(l["date"], l["direction"])] if o["rep"] != "Skill V3"]
    if not others or min(others) > l["entry_time"]:
        _drop_ids.add(id(l))
SOLO_DROPPED = [l for l in comps if id(l) in _drop_ids]
_work2 = [l for l in comps if id(l) not in _drop_ids]
_groups = defaultdict(list)
for l in _work2: _groups[(l["date"], l["direction"])].append(l)
_preblock = []
for k, ls in _groups.items():
    rep = dict(sorted(ls, key=lambda x: x["entry_time"])[0])
    rep["_systems"] = sorted({x["rep"] for x in ls})
    _preblock.append(rep)
CE_BLOCKED = [l for l in _preblock if l["rep"] == "Skill V3" and l["direction"] == "CE"
              and not l.get("_readmit")]
NS1_CE = [l for l in ns1_aud if l["direction"] == "CE"]
_pool_all = unique_once(list(pooled) + list(ns1_aud))
_pool_f1 = FILTERS["drop_ns1_ce"](_pool_all)
_pool_f2 = FILTERS["drop_prem_400_550"](_pool_f1)
_f2_keys = {(x["date"], x["direction"], x["entry_time"]) for x in _pool_f2}
BAND_DROPPED = [l for l in _pool_f1 if (l["date"], l["direction"], l["entry_time"]) not in _f2_keys]
print(f"F1 populations: solo_dropped={len(SOLO_DROPPED)} ce_blocked={len(CE_BLOCKED)} "
      f"ns1_ce={len(NS1_CE)} band_dropped={len(BAND_DROPPED)}")

def f1_candidate(cand_legs):
    def fn():
        admitted, kd, nc = admit_candidates(cand_legs, STATE)
        rows = build_book(STATE) + [r for _, _, r in admitted]
        return rows, nc, dict(admitted=admitted, key_dropped=kd)
    def pl(cand_rows, extra):
        return addon_placebo_total(extra["admitted"], STATE, battery(build_book(STATE))["total"])
    def onb(extra):
        for leg, p, row in extra["admitted"]:
            STATE["addons"].append(dict(leg=leg, p=p))
    return fn, pl, onb

# ================= FAMILY 2 — BE-arm =================
def f2_fns():
    trial = dict(STATE, arm50=True)
    def fn():
        return build_book(trial), 0, dict()
    def pl(cand_rows, extra):
        return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(extra):
        STATE["arm50"] = True
    return fn, pl, onb

# ================= FAMILY 3 — scope-restricted give-back lock =================
def dev_stop_scope(state):
    rows = build_book(state)
    sums = defaultdict(float); counts = defaultdict(int)
    for r in rows:
        if r["src"] in ("pipe", "addon") and r["dev30"] and r["exit_reason"] == "stop":
            sums[r["family"]] += r["net"]; counts[r["family"]] += 1
    scope = {f for f, v in sums.items() if v < 0}
    return scope, dict(sums), dict(counts)

def f3_fns():
    scope, sums, counts = dev_stop_scope(STATE)
    new_scope = scope - {"NS1_second"}
    trial = dict(STATE, lock_families=set(STATE["lock_families"]) | scope)
    def fn():
        return build_book(trial), 0, dict(scope=sorted(scope), dev_stop_sums=sums,
                                         dev_stop_counts=counts)
    def pl(cand_rows, extra):
        return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(extra):
        STATE["lock_families"] |= scope
    return fn, pl, onb, scope, sums, counts

# ================= FAMILY 4 — runner extension =================
def f4_fns():
    trial = dict(STATE, runner_ext=True)
    base_rows = build_book(STATE)
    scoped = [r for r in base_rows if r["src"] in ("pipe", "addon")]
    n_scoped = 0
    for r in scoped:
        if r["src"] == "pipe":
            meta = LEG[r["leg_key"]]
            if meta["p"]["lock"] is None and meta["date"] != meta["expiry"]: n_scoped += 1
        else:
            n_scoped += 1  # addons: counted generously; exact split in results json
    def fn():
        return build_book(trial), 0, dict(scoped_legs_upper=n_scoped)
    def pl(cand_rows, extra):
        return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(extra):
        STATE["runner_ext"] = True
    return fn, pl, onb

# ================= FAMILY 5 — NS1 widening =================
def ns1_widen_candidates(room_from, room_to):
    g_to, _ = ns1_gen_legs(room_to, "15:10")
    g_from, _ = ns1_gen_legs(room_from, "15:10")
    from_keys = {(l["date"], l["direction"], l["entry_time"]) for l in g_from}
    cand = [l for l in g_to if (l["date"], l["direction"], l["entry_time"]) not in from_keys]
    if not STATE["ns1_ce_banked"]:
        cand = [l for l in cand if l["direction"] != "CE"]
    if not STATE["band_banked"]:
        kept = []
        for l in cand:
            ep = _entry_premium(l)
            if ep is not None and BAND[0] <= ep < BAND[1]: continue
            kept.append(l)
        cand = kept
    return cand

def f5_fns(room_from=1.5, room_to=1.25):
    cand = ns1_widen_candidates(room_from, room_to)
    return f1_candidate(cand)

# ================= FAMILY 6 — second re-entry =================
def add_min(t, m):
    h, mm = int(t[:2]), int(t[3:]); mm += m; h += mm // 60; mm %= 60
    return f"{h:02d}:{mm:02d}"

def find_second_reentry(d, first, book_rows, shift_min=0, any_exit=False):
    """first: the day's first re-entry row (current book). Fresh-cross
    search strictly after the first re-entry's exit bar (optionally
    shifted +60 min): first bar whose close is beyond the morning
    extreme while the previous bar's close was not."""
    if first["exit_reason"] != "stop" and not any_exit:
        return None
    if any_exit and first["exit_reason"] == "target":
        return None
    side = first["direction"]
    b, ts = SPOT[d], TIMES[d]
    mh = max(b[t][1] for t in ts if t <= "11:55")
    ml = min(b[t][2] for t in ts if t <= "11:55")
    start = add_min(first["exit_time"], shift_min)
    for i, t in enumerate(ts):
        if t <= start or i == 0: continue
        c, pc = b[t][3], b[ts[i - 1]][3]
        if side == "CE" and c > mh and pc <= mh:
            trig = t; break
        if side == "PE" and c < ml and pc >= ml:
            trig = t; break
    else:
        return None
    realised = round(sum(r["net"] for r in book_rows
                         if r["date"] == d and r["exit_time"] <= trig), 2)
    if realised <= -3000.0:
        return dict(blocked=True, trig=trig, realised=realised)
    et_i = ts.index(trig) + 1
    if et_i >= len(ts): return None
    et = ts[et_i]
    if et > "15:05": return dict(no_time=True, trig=trig)
    exp = store_expiry_for(d)
    strike = atm100(b[et][0])
    pd = prem_day(exp, strike, side, d)
    if pd is None or et not in pd:
        return dict(nc=True, trig=trig, why=f"no_contract {exp}|{strike}|{side}")
    entry_prem = pd[et][0]
    arm = 50.0 if STATE["arm50"] else None
    xt, xp, reason = sim_g0_arm(pd, et, entry_prem, arm, STATE["arm50_level"])
    static = dict(date=d, direction=side, expiry=exp, strike=strike,
                  trigger_time=trig, entry_time=et, entry_premium=entry_prem,
                  rep="EVE06a2")
    row = dict(date=d, direction=side, family="EVE06_REENTRY", rep="EVE06a2",
               entry_time=et, entry_premium=entry_prem, exit_time=xt, exit_premium=xp,
               exit_reason=reason, net=round((xp - entry_prem) * LOT - COST, 2),
               leg_key=(d, side, et), dev30=None, maxfav=None, src="reentry2")
    return dict(row=row, static=static, trig=trig)

def f6_fns(any_exit=False):
    def fn():
        book = build_book(STATE)
        arm = 50.0 if STATE["arm50"] else None
        firsts = {r["date"]: r for r in resim_reentry(A_STATICS, arm, STATE["arm50_level"])}
        new_rows, statics, blocked, nc, notime = [], [], 0, 0, 0
        for d in DAYS:
            f = firsts.get(d)
            if f is None: continue
            res = find_second_reentry(d, f, book, any_exit=any_exit)
            if res is None: continue
            if res.get("blocked"): blocked += 1; continue
            if res.get("no_time"): notime += 1; continue
            if res.get("nc"): nc += 1; continue
            new_rows.append(res["row"]); statics.append(res["static"])
        return book + new_rows, nc, dict(new_rows=new_rows, statics=statics,
                                         cap_blocked=blocked, no_time=notime,
                                         first_stop_days=len(new_rows) + blocked + notime + nc)
    def pl(cand_rows, extra):
        book = build_book(STATE)
        base_total = battery(book)["total"]
        arm = 50.0 if STATE["arm50"] else None
        firsts = {r["date"]: r for r in resim_reentry(A_STATICS, arm, STATE["arm50_level"])}
        inc = 0.0
        for d in DAYS:
            f = firsts.get(d)
            if f is None: continue
            res = find_second_reentry(d, f, book, shift_min=60, any_exit=any_exit)
            if res and "row" in res: inc += res["row"]["net"]
        return round(base_total + inc, 2)
    def onb(extra):
        STATE["reentry2"] += extra["statics"]
    return fn, pl, onb

# ================= PASS-2 VARIANTS =================
from bank_r5_core import ns3_legs, _params_for_addon as r5_params_for_addon
from bank_r3_setups import generate as gen_setups

def v1_fns():
    """Add-on band-dropped legs (NS3/S3 candidates dropped by admit()'s
    premium band in the v21 assembly) — a different pool from F1's."""
    taken = {(r["date"], r["direction"]) for r in rows21 if r["family"] in ("BASE", "NS1_second")}
    bd_legs = []  # (leg, params)
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
    def fn():
        book = build_book(STATE)
        taken_now = {(r["date"], r["direction"]) for r in book}
        seen, rows, nc = set(), list(book), 0
        admitted = []
        for leg, p in sorted(bd_legs, key=lambda x: (x[0]["date"], x[0]["entry_time"])):
            key = (leg["date"], leg["direction"])
            if key in seen: continue
            seen.add(key)
            if key in taken_now: continue
            row = replay_addon(leg, p, STATE)
            if row is None: nc += 1; continue
            admitted.append((leg, p, row)); rows.append(row)
        return rows, nc, dict(admitted=admitted, key_dropped=0)
    def pl(cand_rows, extra):
        return addon_placebo_total(extra["admitted"], STATE, battery(build_book(STATE))["total"])
    def onb(extra):
        for leg, p, row in extra["admitted"]:
            STATE["addons"].append(dict(leg=leg, p=p))
    return fn, pl, onb, len(bd_legs)

def v2_fns():
    trial = dict(STATE, arm50=True, arm50_level=10.0)
    def fn(): return build_book(trial), 0, dict()
    def pl(c, e): return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(e): STATE["arm50"] = True; STATE["arm50_level"] = 10.0
    return fn, pl, onb

def v3_fns():
    scope, sums, counts = dev_stop_scope(STATE)
    trial = dict(STATE, lock_families=set(STATE["lock_families"]) | scope, lock_thresh50=True)
    def fn(): return build_book(trial), 0, dict(scope=sorted(scope), dev_stop_sums=sums)
    def pl(c, e): return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(e): STATE["lock_families"] |= scope; STATE["lock_thresh50"] = True
    return fn, pl, onb, scope, sums, counts

def v4_fns():
    trial = dict(STATE, runner_ext=True, runner_ext_any=True)
    def fn(): return build_book(trial), 0, dict()
    def pl(c, e): return round(sum(r["net"] for r in build_placebo(trial)), 2)
    def onb(e): STATE["runner_ext"] = True; STATE["runner_ext_any"] = True
    return fn, pl, onb

def v5_fns():
    room_from = 1.25 if "c5" in STATE["banks"] else 1.5
    cand = ns1_widen_candidates(room_from, 1.0)
    fn, pl, onb = f1_candidate(cand)
    return fn, pl, onb, room_from, len(cand)

# ================= MAIN =================
log("\n# RESUME — clarified stop rule (2026-11-04)\n\n"
    "The first run stopped after c1c on a literal reading of stop rule (ii) "
    "(3 consecutive no-banks, all inside Family 1). Owner clarification, "
    "which supersedes that reading: stop at SUCCESS (base >= Rs 1,50,000) "
    "at any point; otherwise cycle ALL six families; declare SATURATED "
    "only if, after every family has been cycled at least once, the last 3 "
    "consecutive cycles banked nothing AND those 3 span at least 2 "
    "different families. A bank resets the streak and becomes the new "
    "base; families not yet run are built against the then-current base "
    "(the lazy builders already do this — F3's scope, F5's filters and "
    "F6's arm state all read STATE at build time). Families already "
    "cycled are not re-run in this pass; Pass 2 runs each family's "
    "distinct variant per the original brief's condition (iii). Cycles "
    "c1a/c1b/c1c stand as scored above (all rejected; base unchanged). "
    "This resume runs c1d, then Families 2-6, back-to-back, same scorer "
    "machinery, same banking gate.\n\n"
    f"Resume base re-verified in-run: H1 {BASE_BATT['H1']:+,.2f} / H2 "
    f"{BASE_BATT['H2']:+,.2f}; ex-top-3 legs {BASE_BATT['ex_top3_legs']:+,.2f} "
    f"/ days {BASE_BATT['ex_top3_days']:+,.2f}; placebo twin of the base "
    f"{PB_TOTAL:+,.2f}.")

NOV_ADD = ("No — the running November v22 shadow runs the frozen v22 spec; "
           "this mechanism is outside that spec. Nothing is wired into November.")
NOV_EXIT = ("Not wired — the running November v22 shadow keeps the frozen v22 "
            "exits; if the owner adopted this candidate, shadow exits on legs "
            "it takes would change. Nothing is wired into November.")

def b_c1a():
    fn, pl, onb = f1_candidate(SOLO_DROPPED)
    return ("c1a", "F1a entry expansion — causal solo-dropped Skill legs (<=09:55)",
            "Re-admit the component Skill V3 legs the pool_b2 causal solo rule dropped "
            "(entry <= 09:55 with no other-system leg on the key at/before it — the "
            "construction's own first filter, so this is the first excluded family in "
            "construction order). Admission: UNIQUE-ONCE vs the current book, earliest "
            "leg per (date,direction). Exits: base-book geometry (stream-state segment "
            "params, PLAIN on expiry day). Placebo: the same legs entered 6 bars later.",
            NOV_ADD, fn, pl, onb)

def b_c1b():
    fn, pl, onb = f1_candidate(CE_BLOCKED)
    return ("c1b", "F1b entry expansion — Skill CE pooled reps (CE block)",
            "Re-admit the pooled representative legs pool_b2's CE block removed "
            "(rep == Skill V3, direction CE). Same admission/geometry/placebo as c1a.",
            NOV_ADD, fn, pl, onb)

def b_c1c():
    fn, pl, onb0 = f1_candidate(NS1_CE)
    def onb(extra):
        onb0(extra); STATE["ns1_ce_banked"] = True
    return ("c1c", "F1c entry expansion — NS1 CE second legs (drop_ns1_ce filter)",
            "Re-admit the audited NS1 second legs FILTERS[drop_ns1_ce] removed from "
            "the assembly pool (all CE second legs). Same admission/geometry/placebo "
            "as c1a (NS1 legs take base-row segment geometry in build_base_rows).",
            NOV_ADD, fn, pl, onb)

def b_c1d():
    fn, pl, onb0 = f1_candidate(BAND_DROPPED)
    def onb(extra):
        onb0(extra); STATE["band_banked"] = True
    return ("c1d", "F1d entry expansion — premium-band [400,550) dropped pool legs",
            "Re-admit the pooled/NS1 legs FILTERS[drop_prem_400_550] removed after "
            "the CE filter (entry premium in [400,550)). Same admission/geometry/"
            "placebo as c1a.", NOV_ADD, fn, pl, onb)

def b_c2():
    fn, pl, onb = f2_fns()
    return ("c2", "F2 BE-arm — pre-target break-even arm at +50 (all base legs)",
            "Once any bar's high >= entry+50 premium, the stop for subsequent bars "
            "moves -50 -> entry (arm evaluated after that bar's stop/target checks, "
            "exactly the pipeline's overlay position). Applied to every base leg: "
            "pipeline/add-on legs via the replay, EVE-06 re-entry legs via the G0 "
            "sim. This is Nifty's banked BE50 analogue, never tested in this form on "
            "Bank; EVE-04 was a post-arm +30 lock on NS1 legs only — mechanically "
            "distinct (threshold +50 vs +30, all legs vs NS1-only). Placebo: the "
            "delay-6 twin book under the same arm + shifted re-entries.",
            NOV_EXIT, fn, pl, onb)

def b_c3():
    fn, pl, onb, scope, sums, counts = f3_fns()
    return ("c3", "F3 give-back lock — scope-restricted to net-negative developed->stop families",
            "Developed->stop legs in the CURRENT base (stop exit with a prior bar's "
            f"high >= entry+30), net by family: { {k: round(v, 2) for k, v in sums.items()} } "
            f"(counts {counts}). The FC-2 lock (bar high >= entry+30 -> stop = entry "
            "for subsequent bars) is applied ONLY to families whose developed->stop "
            f"legs are net-negative: scope = {sorted(scope)}. Book-wide FC-2 failed "
            "before (dip-shaped winners share the shape); NS1 already carries this "
            "lock via EVE-04. Placebo: delay-6 twin under the same scoped lock.",
            NOV_EXIT, fn, pl, onb)

def b_c4():
    fn, pl, onb = f4_fns()
    return ("c4", "F4 runner extension — plain-target legs run with the warm runner",
            "Legs whose params are PLAIN (lock/tgt2 None — the ge400_cold segment) "
            "and which are NOT expiry-day legs currently exit flat at the +90 target. "
            "Variant: when such a leg reaches +90 it does not exit; it runs under "
            "the book's own runner convention for its premium band (ge400_warm: "
            "lock +90, second target +180), phase 1 unchanged. Motivation: the "
            "ladder build's T4 anatomy — profit concentrates in full-hunt legs. "
            "Placebo: delay-6 twin under the same extension.", NOV_EXIT, fn, pl, onb)

def b_c5():
    fn, pl, onb = f5_fns()
    return ("c5", "F5 NS1 second-leg widening — room_ratio 1.5 -> 1.25",
            "One step down the registered ladder: NS1 second legs admitted at "
            "room_ratio >= 1.25 instead of >= 1.5 (principle: admit the near-miss "
            "band — the 2026-11-02 primary day fell into it at 1.49). All other NS1 "
            "conditions unchanged (first leg resolved target/stop by 13:30, crossing "
            "after the first leg's exit, CE-on-bearish still blocked by the "
            "generator; standing construction filters — NS1-CE block and premium "
            "band — apply unless those families banked earlier in this tune). "
            "Candidates = gen(1.25) minus gen(1.5) under the generator that "
            "reproduces the audited NS1 population. Geometry: base-row segment "
            "params. Placebo: admitted legs entered 6 bars later.",
            NOV_ADD, fn, pl, onb)

def b_c6():
    fn, pl, onb = f6_fns()
    return ("c6", "F6 second re-entry — a second same-day reclaim after a stopped re-entry",
            "On days whose EVE-06(a) re-entry leg itself stopped: if spot later "
            "makes a FRESH close back through the morning-range extreme (previous "
            "bar's close not beyond it) strictly after the re-entry's exit bar, "
            "re-enter once more (max 2 re-entries/day), ATM at next bar open, G0 "
            "exits, day-cap -Rs 3,000 on realised-to-trigger nets still governs. "
            "Placebo: the same search started +60 min after the re-entry's exit.",
            NOV_ADD, fn, pl, onb)

def b_v1():
    fn, pl, onb, n_bd = v1_fns()
    return ("v1", "F1 variant — add-on band-dropped legs (NS3/S3 pool)",
            f"Mechanically distinct population from F1a-d: the {n_bd} NS3/S3 add-on "
            "candidates admit() band-dropped in the v21 assembly (premium in "
            "[400,550)), re-admitted with their own family geometry (NS3 @ P21; "
            "S3 @ stream-state addon params), UNIQUE-ONCE vs the current book. "
            "Placebo: admitted legs entered 6 bars later.", NOV_ADD, fn, pl, onb)

def b_v2():
    fn, pl, onb = v2_fns()
    return ("v2", "F2 variant — BE-arm at +50 with the armed stop at entry+10",
            "Same +50 arm as F2, but the armed stop locks entry+10 instead of "
            "entry+0 (principle: cover the Rs 220 cost + slippage, ~7.3 premium "
            "points, rounded to 10 — the locked floor is a true net-positive). "
            "Placebo: delay-6 twin under the same arm.", NOV_EXIT, fn, pl, onb)

def b_v3():
    fn, pl, onb, scope, sums, counts = v3_fns()
    return ("v3", "F3 variant — scoped give-back lock arming at +50 instead of +30",
            "The scoped lock of F3 (same scope rule: families whose developed->stop "
            f"legs are net-negative in the current base; scope now {sorted(scope)}) "
            "but the lock arms only once a bar's high >= entry+50 — a developed-more "
            "lock that leaves shallow dips un-locked. NS1's EVE-04 lock stays at +30. "
            "Placebo: delay-6 twin under the same lock.", NOV_EXIT, fn, pl, onb)

def b_v4():
    fn, pl, onb = v4_fns()
    return ("v4", "F4 variant — runner extension extended to expiry-day PLAIN legs",
            "F4's runner treatment (lock +90 / target2 +180 after +90) applied "
            "also to expiry-day PLAIN legs, the one population F4 excluded (the "
            "book's construction keeps expiry-day legs plain; this variant tests "
            "that convention). Placebo: delay-6 twin under the same extension.",
            NOV_EXIT, fn, pl, onb)

def b_v5():
    fn, pl, onb, room_from, n_c = v5_fns()
    return ("v5", "F5 variant — NS1 room_ratio -> 1.00",
            f"Second step down the registered ladder: room_ratio >= 1.00 (from "
            f"{room_from}; principle: room at least equal to the risk itself, "
            "1:1 to the room boundary). All other conditions and standing filters "
            "as in F5. Placebo: admitted legs entered 6 bars later.",
            NOV_ADD, fn, pl, onb)

def b_v6():
    fn, pl, onb = f6_fns(any_exit=True)
    return ("v6", "F6 variant — second re-entry after any non-target first re-entry exit",
            "F6's fresh-cross second re-entry, but the first re-entry need only "
            "have exited without reaching target (stop, lock-stop or square-off) "
            "instead of stop-only. Same trigger, cap and max-2/day rule. Placebo: "
            "search started +60 min after the first re-entry's exit.",
            NOV_ADD, fn, pl, onb)

PASS1R = [b_c1d, b_c2, b_c3, b_c4, b_c5, b_c6]
PASS2 = [b_v1, b_v2, b_v3, b_v4, b_v5, b_v6]

STATE["cycles"] = ["c1a", "c1b", "c1c"]  # first run's cycles stand in the record
verdict = None
for builders, passname in ((PASS1R, "PASS 1 (resumed)"), (PASS2, "PASS 2")):
    if verdict: break
    log(f"\n# {passname}")
    for build in builders:
        cid, title, freeze, nov, fn, pl, onb = build()
        banked = run_cycle(cid, title, freeze, nov, fn, pl, onb)
        HISTORY.append((cid, FAMILY_OF[cid], banked))
        verdict = stop_check()
        if verdict:
            log(f"\n**STOP: {verdict}** after {cid}.")
            break

final_rows = build_book(STATE)
FB = battery(final_rows)
resum = write_trades(final_rows, "bank_aggr_final_trades.csv")
assert resum["n"] == FB["n_legs"] and abs(resum["net"] - FB["total"]) < 0.005
gap = round(150000 - FB["total"], 2)
need_legs_pm = 15000 / FB["per_leg"] if FB["per_leg"] > 0 else float("inf")
need_per_leg = 15000 / FB["legs_per_month"]
summary = dict(verdict=verdict or "TWO_PASSES_COMPLETE", banks=STATE["banks"],
               cycles=STATE["cycles"], final=FB, gap_total=gap,
               needed_legs_per_month_at_current_per_leg=round(need_legs_pm, 2),
               extra_legs_per_month_needed=round(need_legs_pm - FB["legs_per_month"], 2),
               needed_per_leg_at_current_frequency=round(need_per_leg, 2),
               extra_per_leg_needed=round(need_per_leg - FB["per_leg"], 2))
(TR / "bank_aggr_summary.json").write_text(json.dumps(summary, indent=1, default=str))
log(f"\n# FINAL SUMMARY\n\n**Verdict: {summary['verdict']}**\n\n"
    f"Cycles run: {STATE['cycles']}. Banked: {STATE['banks']}.\n\n"
    f"Final book: **{FB['total']:+,.2f}** ({FB['n_legs']} legs, "
    f"{FB['per_month']:,.2f}/month, {FB['per_leg']:,.2f}/leg, "
    f"{FB['legs_per_month']} legs/month). Remaining gap to Rs 1,50,000: "
    f"**{gap:,.2f}** ({round(gap / 10, 2):,.2f}/month).\n\n"
    f"Gap arithmetic at the final book's rates: needs "
    f"{summary['needed_legs_per_month_at_current_per_leg']} legs/month at "
    f"{FB['per_leg']:,.2f}/leg (extra {summary['extra_legs_per_month_needed']}/month), "
    f"or {summary['needed_per_leg_at_current_frequency']:,.2f}/leg at "
    f"{FB['legs_per_month']} legs/month (extra "
    f"{summary['extra_per_leg_needed']:,.2f}/leg), or a mix.\n\n"
    f"Final battery: H1 {FB['H1']:+,.2f} / H2 {FB['H2']:+,.2f}; ex-top-3 legs "
    f"{FB['ex_top3_legs']:+,.2f} / days {FB['ex_top3_days']:+,.2f}; months "
    f"{FB['months']}; worst day {FB['worst_day']}; worst drawdown "
    f"{FB['worst_drawdown']:+,.2f}; positive days {FB['pct_positive_days']}%. "
    f"Independent re-sum of bank_aggr_final_trades.csv: {resum}.")
print(json.dumps(summary, indent=1, default=str))
