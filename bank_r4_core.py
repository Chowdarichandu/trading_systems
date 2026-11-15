#!/usr/bin/env python3
"""ROUND 4 core (BANKNIFTY ONLY). Base = book v17 (bank_r3_ws3.build_x,
open entry, square-off 15:20) — asserted +107,930.00 / 82 / FT90 53.7%.

Stack composition (the flagged Cycle-63 form): sequential admission
NS3 -> S3-A -> S3-E -> S3-D via bank_r3_core.admit (key-uniqueness vs the
base and earlier families, premium band [400,550) exclusion, earliest leg
per key per family); add-ons scored with replay_x at square-off 15:20
under the v17 assembly (segment V15 params / expiry-day plain G0) unless a
geometry override is supplied.

Overrides (Round-4 workstreams; definitions frozen in bank_engine_frozen.md
ROUND 4 appendix before scoring):
- ns3_params: one uniform params dict applied to EVERY admitted NS3 leg
  (the family's own geometry; replaces the segment assembly wholesale,
  including the expiry-day plain rule).
- ns3_filter: predicate on the enriched raw NS3 leg (premium/dte/subleg
  attached) applied to NS3 candidates BEFORE admission.
- extra_families: extra leg lists admitted after S3-D, book assembly.
- geometry_override: (predicate, params) — any stack leg (base or add-on)
  whose leg_key satisfies predicate(leg, row_stub) is re-scored with
  params instead of its assembly params (square-off stays 15:20).
- stack_filter: predicate on combined rows (date, entry_time) applied to
  main and placebo rows alike (entry-state admission conditions).

Gate: bank_r2_core.gate vs a supplied reference controls dict."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_cycle import _entry_premium
from bank_r2_core import controls, gate, seg_of, write_trades
from bank_r2_ns1 import V15
from bank_r2_expiry import LBK
from bank_r3_core import state_at, admit
from bank_r3_ws1 import build as build_ws1
from bank_r3_setups import generate as gen_setups
from bank_r3_ws3 import build_x, replay_x

TR = Path.home() / "workspace/trading"
SQ = "15:20"

V17_ROWS, _nc17 = build_x("open", SQ, delay=0)
V17_PROWS, _pnc17 = build_x("open", SQ, delay=6)
assert len(V17_ROWS) == 82 and abs(sum(r["net"] for r in V17_ROWS) - 107930.00) < 0.005
V17_KEYS = {(r["date"], r["direction"]) for r in V17_ROWS}
REF17 = controls(V17_ROWS, 0, LBK, V17_PROWS, 0)
BASE_BY_KEY = {r["leg_key"]: r for r in V17_ROWS}
BASE_PROW_BY_KEY = {r["leg_key"]: r for r in V17_PROWS}

import datetime as _dt
def enrich(leg):
    """Attach entry premium / DTE / subleg to a raw candidate leg."""
    ep = _entry_premium(leg)
    dte = (_dt.date.fromisoformat(leg["expiry"]) - _dt.date.fromisoformat(leg["date"])).days
    sub = leg["rep"].replace("NS3_", "", 1) if leg.get("rep", "").startswith("NS3_") else leg.get("rep", "")
    return dict(leg, _ep=ep, _dte=dte, _subleg=sub)

def _params_for_addon(leg, delay=0):
    """Book assembly params, mirroring bank_r3_stack.score_addons_sq exactly:
    segment state read at the (possibly delayed) entry time, segment premium
    from the undelayed entry premium."""
    et_state = leg["entry_time"]
    if delay:
        cs0 = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        times = [b[0] for b in cs0] if cs0 else []
        if leg["entry_time"] not in times: return None, None
        i = times.index(leg["entry_time"]) + delay
        if i >= len(times): return None, None
        et_state = times[i]
    n, tnet = state_at(leg["date"], et_state, delay=delay)
    seg = seg_of(_entry_premium(leg), n, tnet)
    if leg["date"] == leg["expiry"]:
        return dict(stop=50.0, trig=90.0, lock=None, tgt2=None), seg
    return V15[seg], seg

def score_leg(leg, params, delay=0):
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    return replay_x(cs, leg["entry_time"], delay, params, "open", SQ)

def build_stack(ns3_params=None, ns3_filter=None, extra_families=None,
                geometry_override=None, stack_filter=None, delay=0, include_s3=True):
    """Returns (rows, nc, all_legs_by_key, detail). delay=6 builds the
    placebo twin (same admission decisions, entries +30 min)."""
    base_rows = V17_PROWS if delay else V17_ROWS
    rows = [dict(r) for r in base_rows]
    all_legs = dict(LBK)
    taken = set(V17_KEYS)
    detail = []

    def run_family(legs, fam_params=None, fam_filter=None, name="?"):
        cand = [enrich(l) for l in legs]
        if fam_filter is not None:
            cand = [l for l in cand if fam_filter(l)]
        admitted, kd, bd, ncl = admit(cand, taken)
        taken.update((l["date"], l["direction"]) for l in admitted)
        nc = 0
        for l in admitted:
            all_legs[(l["date"], l["direction"], l["entry_time"])] = l
        fam_net0 = len(rows)
        for l in admitted:
            if fam_params is not None:
                p, seg = fam_params, "own"
            else:
                p, seg = _params_for_addon(l, delay=delay)
            if p is None:
                nc += 1; continue
            r = score_leg(l, p, delay=delay)
            if r is None:
                nc += 1; continue
            rows.append({**r, "date": l["date"], "direction": l["direction"],
                         "family": l["family"], "rep": l["rep"],
                         "entry_time": l["entry_time"],
                         "leg_key": (l["date"], l["direction"], l["entry_time"]),
                         "segment": seg})
        fam_rows = rows[fam_net0:]
        detail.append(dict(family=name, candidates=len(cand), admitted=len(admitted),
                           key_dropped=len(kd), band_dropped=len(bd),
                           nc_legs=len(ncl), scored_nc=nc,
                           net=round(sum(r["net"] for r in fam_rows), 2),
                           ft90_legs=int(sum(r.get("ft90", 0) for r in fam_rows))))
        return nc

    total_nc = 0
    ns3 = build_ws1("index_options_newsetup_ns3_trades_jan_oct_2026.csv", "NS3_gapclass", "NS3")
    total_nc += run_family(ns3, fam_params=ns3_params, fam_filter=ns3_filter, name="NS3")
    if include_s3:
        gen = gen_setups()
        for fam in ("S3A", "S3E", "S3D"):
            total_nc += run_family(gen[fam], name=fam)
    for i, legs in enumerate(extra_families or []):
        total_nc += run_family(legs, name=f"EXTRA{i}")

    # geometry override: re-score matching legs (base or add-on)
    if geometry_override is not None:
        pred, oparams = geometry_override
        base_by_key = BASE_PROW_BY_KEY if delay else BASE_BY_KEY
        for i, r in enumerate(rows):
            leg = all_legs.get(r["leg_key"])
            if leg is None: continue
            stub = base_by_key.get(r["leg_key"], r)
            if pred(leg, stub):
                cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
                nr = replay_x(cs, leg["entry_time"], delay, oparams, "open", SQ)
                if nr is not None:
                    rows[i] = {**r, **nr}
    rows = sorted(rows, key=lambda x: (x["date"], x["entry_time"]))
    if stack_filter is not None:
        rows = [r for r in rows if stack_filter(r)]
    return rows, total_nc, all_legs, detail

def judge_stack(label, ref=None, write=None, **kw):
    """Full Round-4 judging of one stack variant. Returns a result dict."""
    ref = REF17 if ref is None else ref
    rows, nc, lbk, detail = build_stack(delay=0, **kw)
    prows, pnc, _plbk, _pd = build_stack(delay=6, **kw)
    c = controls(rows, nc, lbk, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, why = gate(c, ref, resum=resum)
    ft_need = None
    if c["n"]:
        import math
        ft_need = math.ceil(ref["ft90_pct"] / 100.0 * c["n"] - 1e-9)
    res = dict(label=label, controls=c, banked=ok, gate_why=why, detail=detail,
               ft90_legs=int(round(c["ft90_pct"] / 100.0 * c["n"])) if c["n"] else 0,
               ft90_needed=ft_need)
    print(f"{label}: net={c['net']:+,.2f} n={c['n']} FT90={c['ft90_pct']} "
          f"({res['ft90_legs']}/{c['n']}, need {ft_need}) placebo={c['placebo']['net']:+,.2f} "
          f"banked={ok} why={why}")
    return res

# the flagged Cycle-63 stack, as reference controls (built lazily)
_STACK_REF = None
def stack_ref():
    global _STACK_REF
    if _STACK_REF is None:
        rows, nc, lbk, _d = build_stack(delay=0)
        prows, pnc, _p, _pd = build_stack(delay=6)
        assert nc == 0 and len(rows) == 108 and abs(sum(r["net"] for r in rows) - 127369.50) < 0.005, \
            f"flagged stack reproduction failed: n={len(rows)} net={sum(r['net'] for r in rows)} nc={nc}"
        _STACK_REF = controls(rows, nc, lbk, prows, pnc)
        assert _STACK_REF["ft90_pct"] == 52.8, _STACK_REF["ft90_pct"]
    return _STACK_REF

if __name__ == "__main__":
    print("v17 reproduced:", REF17["net"], REF17["n"], "FT90", REF17["ft90_pct"])
    sr = stack_ref()
    print("flagged stack reproduced:", sr["net"], sr["n"], "FT90", sr["ft90_pct"],
          "placebo", sr["placebo"]["net"])
