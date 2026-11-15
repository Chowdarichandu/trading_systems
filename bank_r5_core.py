#!/usr/bin/env python3
"""ROUND 5 core (BANKNIFTY ONLY). Definitions frozen in bank_engine_frozen.md
(ROUND 5 appendix) BEFORE scoring.

Provides:
- component leg builders replicating u1_janoct_merge.py's inputs in its
  append order ((lA)/V5 Jan-Sep, Skill Jan-Sep, Volrix Jan-Sep, (lA)/V5 Oct,
  Skill Oct, Volrix Oct), with the frozen strike/expiry conventions;
- B2 pooling under the EOD rule (verified exactly vs B1->B2 in WS0) or the
  WS0 causal solo rule (a Skill leg <=09:55 is dropped pre-pool iff no other
  system's leg on its key enters at or before it);
- NS1 second legs: frozen CSV form (entry_time as recorded, V-NS form),
  causal CSV form (entry = signal+5), or regenerated (gen, causal entries)
  at (room, window) parameters;
- NS3 candidate legs in recorded or causal (signal+5) entry form;
- the dynamic book pipeline: unique-once -> NS1-CE block -> premium band ->
  book-v4 scored stream -> anchored trailing states -> cold-(lA) skip ->
  v17 assembly at square-off 15:20 -> sequential stack admission
  NS3(GD+GU)@GEO -> S3-A -> S3-E -> S3-D;
- judge() under the full controls gate vs a supplied reference.

Sanity (run as __main__): the EOD/frozen path reproduces B1, B2, v17 and v19
exactly; the causal path is then built and controlled."""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score
from aggressive_score import candles, unique_once, EXPIRIES
from bank_engine_cycle import _entry_premium, FILTERS
from bank_engine_run2 import score_all, trailing_state
from bank_engine_run2_cycle14 import stream_keys
from bank_r2_core import controls, gate, seg_of, write_trades
from bank_r2_ns1 import V15
from bank_r3_core import admit
from bank_r3_setups import generate as gen_setups
from bank_r3_ws1 import build as build_ns3_file
from bank_r3_ws3 import replay_x
import newsetups_score as ns

TR = Path.home() / "workspace/trading"
SYM = "BANKNIFTY"
SQ = "15:20"
PLAIN = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
GEO = dict(stop=50.0, trig=90.0, lock=65.0, tgt2=175.0)
GDGU = lambda l: l["_subleg"] in ("NS3-GD", "NS3-GU")

def t_plus5(t):
    hh, mm = map(int, t.split(":"))
    return f"{hh + (mm + 5) // 60:02d}:{(mm + 5) % 60:02d}"

def load_csv(name):
    return list(csv.DictReader(open(TR / name)))

# ---------- spot helpers ----------
_spot = ns.DATA[SYM][0]
SPOT_OPEN = {}
for ts, o in zip(_spot["timestamp"], _spot["open"]):
    SPOT_OPEN[(str(ts)[:10], str(ts)[11:16])] = float(o)
_daily = ns.DATA[SYM][1]
DAY_CLOSE = {str(d)[:10]: float(c) for d, c in zip(_daily["date"], _daily["close"])}
DAY_LIST = sorted(DAY_CLOSE)

def atm(x):
    return int(round(x / 100.0) * 100)

def expiry_for(date):
    return next(e for e in EXPIRIES if e >= date)

def mkleg(date, direction, entry_time, strike, expiry, system, **kw):
    l = dict(date=date, index=SYM, direction=direction, entry_time=entry_time,
             strike=int(strike), expiry=expiry, lot=30, rep=system,
             sources=system, family="BASE")
    l.update(kw)
    return l

# ---------- Volrix ----------
def volrix_frozen_legs():
    # Strike convention as built by the premium proof: ATM at the ENTRY
    # spot (the 09:20 bar open), NOT the trigger-day close — verified
    # against historical_proof_bank_B2_trades.csv strikes (WS0 addendum).
    legs = []
    for r in load_csv("index_options_U1_volrixB_jansep_spot.csv"):
        if r["index"] != SYM: continue
        legs.append(mkleg(r["entry_date"], "CE", "09:20",
                          atm(float(r["entry_spot"])),
                          expiry_for(r["entry_date"]), "Volrix (b)",
                          _trigger=r["trigger_date"]))
    legs.append(mkleg("2026-10-26", "CE", "09:20", 54300, "2026-10-27",
                      "Volrix (b)", _trigger="2026-10-23"))
    return legs

def volrix_gen_legs(thr, cd):
    """Regenerate Volrix (b): trigger = prior session close-to-close return
    <= thr; entry next session 09:20; strike ATM(entry-day 09:20 open);
    cooldown: entry session indices >= cd apart."""
    legs, last_entry_idx = [], None
    for i in range(1, len(DAY_LIST)):
        trig_day, prev = DAY_LIST[i], DAY_LIST[i - 1]
        ret = DAY_CLOSE[trig_day] / DAY_CLOSE[prev] - 1.0
        if ret > thr: continue
        j = i + 1
        if j >= len(DAY_LIST): break
        entry_day = DAY_LIST[j]
        if not ("2026-01-01" <= entry_day <= "2026-10-28"): continue
        if last_entry_idx is not None and j - last_entry_idx < cd: continue
        espot = SPOT_OPEN.get((entry_day, "09:20"))
        if espot is None: continue
        last_entry_idx = j
        legs.append(mkleg(entry_day, "CE", "09:20", atm(espot),
                          expiry_for(entry_day), "Volrix (b)", _trigger=trig_day))
    return legs

# ---------- component legs (merge append order) ----------
def component_legs(volrix=None):
    legs = []
    for r in load_csv("index_options_o1_janoct_trades.csv"):
        if r["index"] != SYM or r["track"] not in ("(lA) v2", "V5-v2"): continue
        if r["date"] >= "2026-10-01": continue  # merge takes Oct (lA)/V5 from the premium file
        sysname = "(lA) v2" if r["track"] == "(lA) v2" else "V5 v2"
        so = SPOT_OPEN.get((r["date"], r["entry_time"]))
        if so is None: continue
        legs.append(mkleg(r["date"], r["direction"], r["entry_time"], atm(so),
                          expiry_for(r["date"]), sysname, _signal=r["signal_time"]))
    for r in load_csv("index_options_U1_skillV3_jansep_spot.csv"):
        if r["index"] != SYM: continue
        legs.append(mkleg(r["date"], r["direction"], r["entry_time"],
                          atm(float(r["entry_spot"])), expiry_for(r["date"]),
                          "Skill V3", _signal=r["signal_time"]))
    legs.extend(volrix_frozen_legs() if volrix is None else volrix)
    for r in load_csv("index_options_premium_october_trades.csv"):
        if r["index"] != SYM or r["premium_status"] != "COMPUTED": continue
        ver = r["version"]
        if ver.startswith("(lA)"): sysname = "(lA) v2"
        elif ver.startswith("V5"): sysname = "V5 v2"
        else: continue
        legs.append(mkleg(r["date"], r["direction"], r["entry_time"],
                          int(float(r["strike"])), r["expiry"], sysname,
                          _signal=r.get("signal_time", "")))
    for r in load_csv("index_options_skill_tuned_oct30_trades.csv"):
        if r["index"] != SYM or r["variant"] != "V3" or r["premium_status"] != "COMPUTED": continue
        legs.append(mkleg(r["date"], r["direction"], r["entry_time"],
                          int(float(r["strike"])), r["expiry"], "Skill V3",
                          _signal=r.get("signal_time", "")))
    return legs

# ---------- B2 pooling ----------
def pool_b2(legs, solo_rule="eod"):
    """Returns the pooled B2 base legs (representative legs only).
    solo_rule 'eod': drop pooled leg iff rep==Skill and (CE or (solo and
    entry<=09:55)) — verified exact vs B1->B2. 'causal': first remove every
    Skill leg (not flagged _readmit) with entry<=09:55 that has no
    other-system leg on its key entering at or before it, then pool, then
    the CE block (readmit-flagged legs are exempt from both Skill rules)."""
    work = list(legs)
    if solo_rule == "causal":
        by_key = defaultdict(list)
        for l in work: by_key[(l["date"], l["direction"])].append(l)
        drop = set()
        for l in work:
            if l["rep"] != "Skill V3" or l["entry_time"] > "09:55": continue
            if l.get("_readmit"): continue
            others = [o["entry_time"] for o in by_key[(l["date"], l["direction"])]
                      if o["rep"] != "Skill V3"]
            if not others or min(others) > l["entry_time"]:
                drop.add(id(l))
        work = [l for l in work if id(l) not in drop]
    groups = defaultdict(list)
    for l in work: groups[(l["date"], l["direction"])].append(l)
    pooled = []
    for k, ls in groups.items():
        rep = sorted(ls, key=lambda x: x["entry_time"])[0]
        rep = dict(rep)
        rep["_systems"] = sorted({x["rep"] for x in ls})
        pooled.append(rep)
    out = []
    for rep in pooled:
        if rep["rep"] == "Skill V3" and not rep.get("_readmit"):
            if rep["direction"] == "CE":
                continue
            if solo_rule == "eod" and rep["_systems"] == ["Skill V3"] \
                    and rep["entry_time"] <= "09:55":
                continue
        out.append(rep)
    return sorted(out, key=lambda x: (x["date"], x["entry_time"]))

# ---------- NS1 second legs ----------
def ns1_recorded_legs():
    from aggressive_score import base_legs as _bl  # noqa (keeps import graph explicit)
    from bank_engine_repro import build_v1_legs
    legs, _, _ = build_v1_legs()
    return [l for l in legs if l["family"].startswith("NS1")]

def _causalise(legs, sig_by_key):
    out = []
    for l in legs:
        sig = sig_by_key.get((l["date"], l["direction"]))
        if sig is None: raise SystemExit(f"no signal time for NS leg {l['date']} {l['direction']}")
        l2 = dict(l); l2["entry_time"] = t_plus5(sig)
        out.append(l2)
    return out

def ns1_causal_legs():
    sig = {}
    for r in load_csv("index_options_newsetup_ns1_trades_jan_oct_2026.csv"):
        if r["index"] == SYM and r["leg"] == "second":
            sig[(r["date"], r["direction"])] = r["signal_time"]
    for r in load_csv("index_options_newsetup_premium_october_trades.csv"):
        if r["index"] == SYM and r["family"] == "NS1" and r["leg"] == "second":
            sig[(r["date"], r["direction"])] = r["signal_time"]
    return _causalise(ns1_recorded_legs(), sig)

def ns1_gen_legs(room_min, window_end):
    """bank_r2_ns1.gen_ns1 logic with causal entries (entry = crossing+1)."""
    from newsetups_score import day_info, replay, room_ratio, s1_trade
    legs, sigmap = [], {}
    daily = ns.DATA[SYM][1]
    for raw_date in sorted(set(daily["date"])):
        date = str(raw_date)[:10]
        if not ("2026-01-01" <= date <= "2026-10-28"): continue
        info = day_info(SYM, raw_date)
        if info is None: continue
        s1 = s1_trade(info)
        if s1[0] is None: continue
        tr, i, d, _ = s1[0]
        if not (tr["exit_reason"] in ("target", "stop") and tr["exit_time"] <= "13:30"): continue
        bars = info["bars"]
        exit_idx = next(j for j, b in enumerate(bars) if b["time"] == tr["exit_time"])
        for j in range(exit_idx + 1, len(bars)):
            b = bars[j]
            if b["time"] > window_end: break
            prev = bars[j - 1]
            d2 = None
            if b["close"] > info["orh"] and not (prev["close"] > info["orh"]): d2 = "CE"
            elif b["close"] < info["orl"] and not (prev["close"] < info["orl"]): d2 = "PE"
            if d2 is None: continue
            if d2 == "CE" and info["bias"] == "bearish": break
            tr2 = replay(bars, j, d2)
            if tr2 is None: break
            rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
            if rr < room_min: break
            strike = round(tr2["entry"] / 100.0) * 100
            entry_time = bars[j + 1]["time"] if j + 1 < len(bars) else None
            if entry_time is None: break
            legs.append(dict(date=date, index=SYM, direction=d2,
                             entry_time=entry_time, strike=strike,
                             expiry=expiry_for(date), lot=30,
                             family="NS1_second", rep="NS1_second",
                             sources="NS1", _signal=b["time"]))
            sigmap[(date, d2, entry_time)] = b["time"]
            break
    return legs, sigmap

# ---------- NS3 candidate legs ----------
def ns3_legs(causal=False):
    legs = build_ns3_file("index_options_newsetup_ns3_trades_jan_oct_2026.csv",
                          "NS3_gapclass", "NS3")
    if causal:
        for l in legs:
            l["entry_time"] = t_plus5(l["signal_time"])
    return legs

def enrich(leg):
    ep = _entry_premium(leg)
    import datetime as _dt
    dte = (_dt.date.fromisoformat(leg["expiry"]) - _dt.date.fromisoformat(leg["date"])).days
    sub = leg["rep"].replace("NS3_", "", 1) if leg.get("rep", "").startswith("NS3_") else leg.get("rep", "")
    return dict(leg, _ep=ep, _dte=dte, _subleg=sub)

# ---------- dynamic pipeline ----------
def stream_states(pool_legs_by_key, delay=0):
    scored, nc0 = score_all(list(pool_legs_by_key.values()), delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    states, taken = {}, []
    for row in stream:
        n, net, _ = trailing_state(stream, row)
        states[row["leg_key"]] = (n, net)
        if not (n >= 10 and net < 0 and row["rep"] == "(lA) v2"):
            taken.append(row["leg_key"])
    return stream, states, taken, nc0

def state_at(stream, date, entry_time):
    known = [s for s in stream
             if s["date"] < date or (s["date"] == date and s["exit_time"] <= entry_time)]
    last = known[-10:]
    return len(last), round(sum(x["net"] for x in last), 2)

def _delayed_entry_time(leg, delay, cs=None):
    cs = cs if cs is not None else candles(leg["index"], leg["strike"], leg["direction"],
                                            leg["date"], leg["expiry"])
    if not cs: return None
    times = [b[0] for b in cs]
    if leg["entry_time"] not in times: return None
    i = times.index(leg["entry_time"]) + delay
    return times[i] if i < len(times) else None

def _params_for_addon(leg, stream, delay=0):
    et_state = leg["entry_time"]
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    if delay:
        et_state = _delayed_entry_time(leg, delay, cs)
        if et_state is None: return None, None
    n, tnet = state_at(stream, leg["date"], et_state)
    seg = seg_of(_entry_premium(leg), n, tnet)
    if leg["date"] == leg["expiry"]:
        return dict(PLAIN), seg
    return dict(V15[seg]), seg

def build_base_rows(pool_by_key, stream, states, taken, delay=0):
    rows, nc = [], 0
    for key in taken:
        l = pool_by_key[key]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        probe = replay_x(cs, l["entry_time"], 0, PLAIN, "open", SQ)
        if probe is None: nc += 1; continue
        seg = seg_of(probe["entry"], *states.get(key, (0, 0.0)))
        p = dict(PLAIN) if l["date"] == l["expiry"] else dict(V15[seg])
        r = replay_x(cs, l["entry_time"], delay, p, "open", SQ)
        if r is None: nc += 1; continue
        rows.append({**r, "date": l["date"], "direction": l["direction"],
                     "family": l["family"], "rep": l["rep"],
                     "entry_time": l["entry_time"], "leg_key": key,
                     "segment": seg, "_params": p})
    return sorted(rows, key=lambda x: (x["date"], x["entry_time"])), nc

def _assemble(base_pooled, ns1_list, delay=0, ns3_causal_form=True,
              ns3_params=None, ns3_filter=None, geometry_override=None, plan=None):
    """One delay's book. When plan is None, add-on admission is decided here
    (against THIS build's delay-0 base keys) and returned; when a plan is
    supplied (the placebo twin), the same admitted legs are scored at this
    delay with params read from this delay's stream — the frozen
    bank_r4_core placebo semantics."""
    pool = unique_once(list(base_pooled) + list(ns1_list))
    pool = FILTERS["drop_ns1_ce"](pool)
    pool = FILTERS["drop_prem_400_550"](pool)
    by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in pool}
    stream, states, taken, nc0 = stream_states(by_key, delay=delay)
    rows, nc = build_base_rows(by_key, stream, states, taken, delay=delay)
    lbk = dict(by_key)
    detail = []
    nc_total = nc0 + nc

    def score_addon(l, fam_params):
        nonlocal nc_total
        lbk[(l["date"], l["direction"], l["entry_time"])] = l
        if fam_params is not None:
            p, seg = dict(fam_params), "own"
        else:
            p, seg = _params_for_addon(l, stream, delay=delay)
            if p is None: nc_total += 1; return
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = replay_x(cs, l["entry_time"], delay, p, "open", SQ)
        if r is None: nc_total += 1; return
        rows.append({**r, "date": l["date"], "direction": l["direction"],
                     "family": l["family"], "rep": l["rep"],
                     "entry_time": l["entry_time"],
                     "leg_key": (l["date"], l["direction"], l["entry_time"]),
                     "segment": seg, "_params": p})

    if plan is None:
        plan = []
        taken_keys = {(r["date"], r["direction"]) for r in rows}

        def run_family(legs, fam_params, name):
            cand = [enrich(l) for l in legs]
            if name == "NS3" and ns3_filter is not None:
                cand = [l for l in cand if ns3_filter(l)]
            admitted, kd, bd, ncl = admit(cand, taken_keys)
            taken_keys.update((l["date"], l["direction"]) for l in admitted)
            fam0 = len(rows)
            for l in admitted:
                plan.append((name, l, fam_params))
                score_addon(l, fam_params)
            fam_rows = rows[fam0:]
            detail.append(dict(family=name, candidates=len(cand), admitted=len(admitted),
                               key_dropped=len(kd), band_dropped=len(bd),
                               nc_legs=len(ncl),
                               net=round(sum(r["net"] for r in fam_rows), 2)))

        run_family(ns3_legs(causal=ns3_causal_form), ns3_params, "NS3")
        gen = gen_setups()
        for fam in ("S3A", "S3E", "S3D"):
            run_family(gen[fam], None, fam)
    else:
        for name, l, fam_params in plan:
            score_addon(l, fam_params)
    rows = sorted(rows, key=lambda x: (x["date"], x["entry_time"]))
    if geometry_override is not None:
        for i, r in enumerate(rows):
            leg = lbk.get(r["leg_key"])
            if leg is None: continue
            p2 = geometry_override(r, leg)
            if p2 is not None:
                cs = candles(leg["index"], leg["strike"], leg["direction"],
                             leg["date"], leg["expiry"])
                nr = replay_x(cs, leg["entry_time"], delay, p2, "open", SQ)
                if nr is not None:
                    rows[i] = {**r, **nr, "_params": p2}
        rows = sorted(rows, key=lambda x: (x["date"], x["entry_time"]))
    return rows, nc_total, lbk, detail, plan

def build_book(base_pooled, ns1_list, delay=0, **kw):
    rows, nc, lbk, detail, _plan = _assemble(base_pooled, ns1_list, delay=delay, **kw)
    return rows, nc, lbk, detail

def judge(label, ref, base_pooled, ns1_list, write=None, **book_kw):
    rows, nc, lbk, detail, plan = _assemble(base_pooled, ns1_list, delay=0, **book_kw)
    prows, pnc, _plbk, _pd, _p2 = _assemble(base_pooled, ns1_list, delay=6,
                                            plan=plan, **book_kw)
    c = controls(rows, nc, lbk, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, why = gate(c, ref, resum=resum)
    print(f"{label}: net={c['net']:+,.2f} n={c['n']} FT90={c['ft90_pct']} "
          f"placebo={c['placebo']['net']:+,.2f} nc={nc}/{pnc} banked={ok} why={why}")
    return dict(label=label, controls=c, banked=ok, gate_why=why, detail=detail)

# ---------- candle availability ----------
def missing_candles(legs):
    out = []
    for l in legs:
        if candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"]) is None:
            out.append((l["date"], l["direction"], int(l["strike"]), l["expiry"]))
    return sorted(set(out))

def fetch_missing(legs):
    miss = missing_candles(legs)
    if not miss: return []
    targets = json.dumps(miss)
    path = TR / "bank_r5_fetch_targets.json"
    path.write_text(targets)
    import subprocess
    res = subprocess.run([sys.executable, str(TR / "bank_r3_fetch.py"), str(path)],
                         capture_output=True, text=True)
    aggressive_score._cache.clear()
    still = missing_candles(legs)
    print(f"fetch: {len(miss)} targets -> still missing {len(still)}")
    if res.returncode != 0:
        print(res.stdout[-1500:], res.stderr[-1500:])
    return still

# ---------- baselines ----------
def frozen_components():
    return component_legs()

def causal_components():
    return component_legs()

def baseline_pools(solo_rule):
    comps = component_legs()
    return pool_b2(comps, solo_rule=solo_rule)

_AUD = {}
def aud_inputs():
    """Causal-baseline inputs: causal-solo pooled B2 + RAW causal NS1 legs
    (pooling inside build_book then competes at causal entry times — the
    WS2 sanity caught the first Cycle-115 build pooling NS1 survivors at
    their recorded (exit-bar) times; corrected here, disclosed in the log)."""
    if "pooled" not in _AUD:
        _AUD["pooled"] = pool_b2(component_legs(), solo_rule="causal")
        _AUD["ns1"] = ns1_gen_legs(1.5, "14:30")[0]
    return _AUD["pooled"], _AUD["ns1"]

def aud_ref():
    """REF_AUD: full controls of the WS0 causal rebuild (Cycle 115)."""
    if "ref" not in _AUD:
        pooled, ns1 = aud_inputs()
        rows, nc, lbk, detail, plan = _assemble(pooled, ns1, delay=0,
                                                ns3_causal_form=True,
                                                ns3_filter=GDGU, ns3_params=GEO)
        prows, pnc, _pl, _pd, _p2 = _assemble(pooled, ns1, delay=6,
                                              ns3_causal_form=True,
                                              ns3_filter=GDGU, ns3_params=GEO,
                                              plan=plan)
        _AUD["ref"] = controls(rows, nc, lbk, prows, pnc)
        _AUD["rows"] = rows
        _AUD["detail"] = detail
    return _AUD["ref"]

REF19 = None
def ref19():
    global REF19
    if REF19 is None:
        from bank_r4_core import build_stack as r4_build
        from bank_r4_ws6 import GDGU as R4GDGU, GEO as R4GEO
        rows, nc, lbk, _d = r4_build(ns3_filter=R4GDGU, ns3_params=R4GEO)
        prows, pnc, _p, _pd = r4_build(delay=6, ns3_filter=R4GDGU, ns3_params=R4GEO)
        REF19 = controls(rows, nc, lbk, prows, pnc)
    return REF19

if __name__ == "__main__":
    # S1: EOD component rebuild == B1 pooled records
    comps = component_legs()
    groups = defaultdict(list)
    for l in comps: groups[(l["date"], l["direction"])].append(l)
    b1 = {(r["date"], r["direction"]): r for r in load_csv("index_options_U1_B1_bank_trades.csv")
          if r["index"] == SYM}
    mism = []
    for k, r in b1.items():
        ls = sorted(groups.get(k, []), key=lambda x: x["entry_time"])
        if not ls: mism.append((k, "no legs")); continue
        rep = ls[0]
        if rep["rep"] != r["representative_system"] or rep["entry_time"] != r["entry_time"] \
                or sorted({x["rep"] for x in ls}) != sorted(r["source_systems"].split(";")):
            mism.append((k, rep["rep"], r["representative_system"], rep["entry_time"], r["entry_time"]))
    print(f"S1 B1 rebuild: {len(b1)} keys, mismatches {len(mism)}", mism[:5])
    # S2: EOD B2 pool == base_legs (89)
    from aggressive_score import base_legs
    pooled = pool_b2(comps, solo_rule="eod")
    want = {(l["date"], l["direction"], l["entry_time"], l["strike"], l["rep"]) for l in base_legs(SYM)}
    got = {(l["date"], l["direction"], l["entry_time"], l["strike"], l["rep"]) for l in pooled}
    print(f"S2 B2 rebuild: pooled {len(pooled)} vs file {len(want)}; only-mine {sorted(got - want)[:4]}; only-file {sorted(want - got)[:4]}")
    # S5: gen NS1 causal set == RAW recorded NS1 second-leg set (pre-pool)
    from aggressive_score import ns_jansep_legs, ns_oct_legs
    gl, _sm = ns1_gen_legs(1.5, "14:30")
    raw = [l for l in ns_jansep_legs(SYM) if l["family"].startswith("NS1")] + \
          [l for l in ns_oct_legs(SYM) if l["family"].startswith("NS1")]
    gset = {(l["date"], l["direction"], l["strike"], l["expiry"]) for l in gl}
    rset = {(l["date"], l["direction"], l["strike"], l["expiry"]) for l in raw}
    print(f"S5 NS1 gen set {len(gset)} vs raw recorded {len(rset)}; diff {sorted(gset ^ rset)[:6]}")
    # S6: Volrix gen at frozen cell vs frozen set (named calibration exception:
    # the 2026-06-01 frozen leg's trigger is -0.924% on stored daily data, so
    # regeneration fires 2026-06-02 instead — WS0 calibration note)
    fg = {(l["date"], l["strike"]) for l in volrix_gen_legs(-0.01, 10)}
    ff = {(l["date"], l["strike"]) for l in volrix_frozen_legs()}
    print(f"S6 Volrix gen {len(fg)} vs frozen {len(ff)}; diff {sorted(fg ^ ff)}")
