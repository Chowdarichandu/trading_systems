#!/usr/bin/env python3
"""ROUND 6 core (BANKNIFTY ONLY). A faithful copy of bank_r5_core._assemble
with ONE addition: `extra_families` — a list of (name, legs, fam_params)
run sequentially AFTER the S3 families under the same admission machinery
(bank_r3_core.admit: key UNIQUE-ONCE vs the book, premium-band drop) and
the same plan/placebo semantics. fam_params=None -> stream-state segment
geometry (book exits; PLAIN on expiry day), as for S3 add-ons.

Causality certification (written, per lessons 46/52/64-71): every leg fed
to this pipeline carries its TRUE entry — component legs enter at their
own system's signal+5 (or 09:20 on a prior-day trigger for Volrix); NS1
legs are regenerated at crossing+1; NS3 legs at signal+5; extra-family
legs constructed in the WS scripts carry entries strictly after every
input they depend on (each WS script states its certificate). Pooling,
states and admission all consume these same timestamps (lesson 66)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
from bank_r5_core import (SQ, PLAIN, V15, GDGU, GEO, candles, replay_x,
                          stream_states, build_base_rows, enrich,
                          ns3_legs, aud_inputs, component_legs, pool_b2,
                          volrix_gen_legs, _params_for_addon)
from aggressive_score import unique_once
from bank_engine_cycle import FILTERS
from bank_r2_core import controls, gate, seg_of, write_trades
from bank_r3_core import admit
from bank_r3_setups import generate as gen_setups

def assemble6(base_pooled, ns1_list, delay=0, ns3_causal_form=True,
              ns3_params=None, ns3_filter=None, extra_families=None,
              plan=None):
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
        for name, legs, fam_params in (extra_families or []):
            run_family(legs, fam_params, name)
    else:
        for name, l, fam_params in plan:
            score_addon(l, fam_params)
    rows = sorted(rows, key=lambda x: (x["date"], x["entry_time"]))
    return rows, nc_total, lbk, detail, plan

def judge6(label, ref, base_pooled, ns1_list, write=None, **book_kw):
    rows, nc, lbk, detail, plan = assemble6(base_pooled, ns1_list, delay=0, **book_kw)
    prows, pnc, _plbk, _pd, _p2 = assemble6(base_pooled, ns1_list, delay=6,
                                            plan=plan, **book_kw)
    ctrl = controls(rows, nc, lbk, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        ctrl["independent_resum"] = resum
        ctrl["resum_matches"] = (resum["n"] == ctrl["n"]
                                 and abs(resum["net"] - ctrl["net"]) < 0.005)
    ok, why = gate(ctrl, ref, resum=resum)
    print(f"{label}: net={ctrl['net']:+,.2f} n={ctrl['n']} FT90={ctrl['ft90_pct']} "
          f"freq={ctrl['per_week_raw']} placebo={ctrl['placebo']['net']:+,.2f} "
          f"ex_top3={ctrl['ex_top3_total']:+,.2f} nc={nc}/{pnc} banked={ok} why={why}")
    return dict(label=label, controls=ctrl, banked=ok, gate_why=why, detail=detail)

# ---------- v20 baseline ----------
_V20 = {}
def v20_inputs():
    if "pooled" not in _V20:
        comps = component_legs(volrix=volrix_gen_legs(-0.01, 15))
        _V20["pooled"] = pool_b2(comps, solo_rule="causal")
        _V20["ns1"] = aud_inputs()[1]
    return _V20["pooled"], _V20["ns1"]

def v20_ref():
    if "ref" not in _V20:
        pooled, ns1 = v20_inputs()
        rows, nc, lbk, detail, plan = assemble6(pooled, ns1, delay=0,
                                                ns3_causal_form=True,
                                                ns3_filter=GDGU, ns3_params=GEO)
        prows, pnc, _pl, _pd, _p2 = assemble6(pooled, ns1, delay=6,
                                              ns3_causal_form=True,
                                              ns3_filter=GDGU, ns3_params=GEO,
                                              plan=plan)
        _V20["ref"] = controls(rows, nc, lbk, prows, pnc)
        _V20["rows"] = rows
        _V20["detail"] = detail
    return _V20["ref"]
