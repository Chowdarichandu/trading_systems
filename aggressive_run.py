#!/usr/bin/env python3
"""Driver for aggressive tuning. Phase 'oct': score all frozen candidates on
October 2026 premiums. Phase 'check': Jan-Oct premium check for the top
October candidates per index. Per index separately, never pooled."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import (base_legs, ns_oct_legs, ns_jansep_legs, unique_once,
                              score_legs, agg, month_end_reds, candles, entry_bar_stats)

TR = Path.home() / "workspace/trading"
OCT_WEEKS, JANOCT_WEEKS = 3.6, 40.6
GEOMS = [
    ("G0_base_-50/+90", 50, 90, "plain"),
    ("G1_-50/+120", 50, 120, "plain"),
    ("G2_-50/+150", 50, 150, "plain"),
    ("G3_-65/+90", 65, 90, "plain"),
    ("G4_-65/+120", 65, 120, "plain"),
    ("G5_-65/+150", 65, 150, "plain"),
    ("G6_runnerBE_+150", 50, 90, "runner_be"),
    ("G7_runnerLOCK50_+150", 50, 90, "runner_lock50"),
    ("G8_partial90_trail150", 50, 90, "partial"),
]
def gate_mom(st, l): return st["bar"][4] >= st["bar"][1]
def gate_mom5(st, l): return st["bar"][4] - st["bar"][1] >= 5.0
def gate_vwap(st, l): return st["bar"][1] >= st["vwap"]

def ns_legs(sym, period):
    return ns_oct_legs(sym) if period == "oct" else ns_jansep_legs(sym)

def bases(sym, period):
    if period == "oct": return base_legs(sym, months={"10"})
    if period == "jansep": return base_legs(sym, months={"01","02","03","04","05","06","07","08","09"})
    return base_legs(sym)

def filter_aNS(pooled_base, addons):
    """Keep addon iff the day's earliest base leg (same index+date) did not exit 'stop'.
    Addons on days with no base leg are dropped (frozen, as variant4)."""
    first = {}
    for b in pooled_base:
        if b["date"] not in first or b["entry_time"] < first[b["date"]]["entry_time"]:
            first[b["date"]] = b
    return [a for a in addons if a["date"] in first and first[a["date"]]["base_reason"] != "stop"]

def filter_c(addons):
    """Keep addon iff its entry premium is NOT in the top third of the contract's
    premium range from day start to the entry bar (frozen, as variant4 (c))."""
    out = []
    for a in addons:
        cs = candles(a["index"], a["strike"], a["direction"], a["date"], a["expiry"])
        st = entry_bar_stats(cs, a["entry_time"]) if cs else None
        if st is None: continue
        thr = st["day_lo"] + (2.0 / 3.0) * (st["day_hi"] - st["day_lo"])
        if st["bar"][1] < thr: out.append(a)
    return out

def candidates(sym, period, best_geom=None):
    """Yield (name, family, legs, score_kwargs)."""
    B = bases(sym, period)
    ns1 = [l for l in ns_legs(sym, period) if l["family"].startswith("NS1")]
    ns2 = [l for l in ns_legs(sym, period) if l["family"].startswith("NS2")]
    if period == "janoct":  # pooled Jan-Oct = jansep + october legs
        B = bases(sym, "jansep") + bases(sym, "oct")
        ns1 = ns_jansep_legs(sym) and [l for l in ns_jansep_legs(sym) if l["family"].startswith("NS1")] + \
              [l for l in ns_oct_legs(sym) if l["family"].startswith("NS1")]
        ns2 = [l for l in ns_jansep_legs(sym) if l["family"].startswith("NS2")] + \
              [l for l in ns_oct_legs(sym) if l["family"].startswith("NS2")]
    # Family 1: exit geometry on base
    for name, s, t, m in GEOMS:
        yield (name, "geometry", B, dict(stop=s, target=t, mode=m))
    # Family 2: volume
    yield ("V1_base+NS1second", "volume", unique_once(B + ns1), dict())
    yield ("V2_base+NS2aft", "volume", unique_once(B + ns2), dict())
    yield ("V3_base+NS1+NS2", "volume", unique_once(B + ns1 + ns2), dict())
    yield ("V4_V3_filter-aNS", "volume", unique_once(B + filter_aNS(B, ns1 + ns2)), dict())
    yield ("V5_V3_filter-c-notextended", "volume", unique_once(B + filter_c(ns1 + ns2)), dict())
    # Family 3: entry quality on base
    yield ("E1_gate_mom_rising", "entry", B, dict(gate=gate_mom))
    yield ("E2_gate_mom_+5", "entry", B, dict(gate=gate_mom5))
    yield ("E3_gate_vwap", "entry", B, dict(gate=gate_vwap))
    yield ("E4_delay1bar", "entry", B, dict(delay=1))
    # Family 4: components (representative-based, as in U1 diagnosis)
    reps = sorted({l["rep"] for l in B})
    per_rep = {}
    for rp in reps:
        sub = [l for l in B if l["rep"] == rp]
        per_rep[rp] = sum(l["base_net"] for l in sub if l["base_net"] is not None)
    weakest = min(per_rep, key=per_rep.get) if per_rep else None
    if weakest and per_rep[weakest] < 0:
        yield (f"C1_drop_weakest[{weakest}]", "component", [l for l in B if l["rep"] != weakest], dict())
    from itertools import combinations
    for a, b in combinations(reps, 2):
        yield (f"C2_union[{a}+{b}]", "component", [l for l in B if l["rep"] in (a, b)], dict())
    yield ("C3_confirmed_only(>=2systems)", "component",
           [l for l in B if len([s for s in l["sources"].split(";") if s.strip()]) >= 2], dict())
    # Family 5: ITM strike on base
    yield ("F5_ITM100_base", "strike", B, dict(strike_shift=1))
    # Stacks (need best geometry from October)
    if best_geom:
        s, t, m = best_geom
        pooled = unique_once(B + ns1 + ns2)
        yield ("S1_V3pool+bestGeom", "stack", pooled, dict(stop=s, target=t, mode=m))
        yield ("S2_S1+mom_gate", "stack", pooled, dict(stop=s, target=t, mode=m, gate=gate_mom))
        top2 = sorted(per_rep, key=per_rep.get, reverse=True)[:2]
        sub = [l for l in B if l["rep"] in top2]
        yield (f"S3_top2union[{'+'.join(top2)}]+NS+bestGeom", "stack",
               unique_once(sub + ns1 + ns2), dict(stop=s, target=t, mode=m))

def run_oct():
    out = {}
    for sym in ("BANKNIFTY", "NIFTY"):
        rows = []
        # first pass: geometry to find best
        geom_rows = {}
        for name, fam, legs, kw in candidates(sym, "oct"):
            if fam != "geometry": continue
            res, nc = score_legs(legs, **kw)
            a = agg(res, OCT_WEEKS); a.update(name=name, family=fam, not_computed=nc)
            geom_rows[name] = a; rows.append(a)
        best = max((r for r in geom_rows.values() if r["name"] != "G0_base_-50/+90"),
                   key=lambda r: (r["net"], r["ft_pct"]))
        bg = [g for g in GEOMS if g[0] == best["name"]][0]
        best_geom = (bg[1], bg[2], bg[3])
        for name, fam, legs, kw in candidates(sym, "oct", best_geom=best_geom):
            if fam == "geometry": continue
            res, nc = score_legs(legs, **kw)
            a = agg(res, OCT_WEEKS); a.update(name=name, family=fam, not_computed=nc)
            rows.append(a)
        out[sym] = dict(best_geom=best["name"], rows=rows)
        print(sym, "best geometry:", best["name"], best["net"])
    (TR / "aggressive_results_oct.json").write_text(json.dumps(out, indent=1))
    print("wrote aggressive_results_oct.json")

def run_check():
    oct_data = json.loads((TR / "aggressive_results_oct.json").read_text())
    out = {}
    for sym in ("BANKNIFTY", "NIFTY"):
        rows = oct_data[sym]["rows"]
        base = [r for r in rows if r["name"] == "G0_base_-50/+90"][0]
        bg = [g for g in GEOMS if g[0] == oct_data[sym]["best_geom"]][0]
        best_geom = (bg[1], bg[2], bg[3])
        cand = {name: (legs, kw) for name, fam, legs, kw in candidates(sym, "janoct", best_geom=best_geom)}
        # selection: October passers (net>base, ft>=base, >=2/wk) + top3 by Oct net
        passers = [r for r in rows if r["net"] > base["net"] and r["ft_pct"] >= base["ft_pct"] and r["per_week"] >= 2.0]
        top3 = sorted(rows, key=lambda r: r["net"], reverse=True)[:3]
        sel = []
        for r in passers + top3 + [base]:
            if r["name"] not in sel: sel.append(r["name"])
        checks = {}
        for name in sel:
            legs, kw = cand[name]
            res, nc = score_legs(legs, **kw)
            a = agg(res, JANOCT_WEEKS)
            reds, tot, table = month_end_reds(res)
            a.update(not_computed=nc, red_month_ends=reds, month_table=table)
            checks[name] = a
            print(sym, name, "JanOct:", a["n"], a["net"], a["ft_pct"], "NC", nc, "reds", reds)
        out[sym] = checks
    (TR / "aggressive_results_check.json").write_text(json.dumps(out, indent=1))
    print("wrote aggressive_results_check.json")

if __name__ == "__main__":
    if sys.argv[1] == "oct": run_oct()
    else: run_check()
