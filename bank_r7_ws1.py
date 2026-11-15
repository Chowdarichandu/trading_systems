#!/usr/bin/env python3
"""ROUND 7 WS1 — V5 KNOBS (Cycles 150-154).

V5 v2's construction (index_options_v2_frozen.md + progressive_capped_v2):
pool = V4 index candidates + Skill index candidates (all symbols feed the
shared caps), dedup same symbol+date by setup rank, then cap_select_v2:
filter prospective target net >= min_target (frozen 500), weekly caps
cap_index (frozen 3) / cap_stock (3), max 1 trade/symbol/week, ranking by
setup_rank, bias_strong, room_ratio, target_net (all prospective).
The two material knobs: min_target and cap_index. Grid, one axis at a
time: min_target {250, 1000} at cap 3; cap_index {2, 5} at target 500.

REGENERATION PATH (validated before scoring): selections are rebuilt with
progressive_capped_v2.candidates_for_month + the run_v2_month dedup +
cap_select_v2; Bank signal times are resolved exactly as o1_janoct.py
resolved them (V4 uncapped / Skill-filtered recomputation on the same
functions), entry = next bar after the signal; legs are built with
bank_r5_core.mkleg conventions (strike = ATM of the entry bar's spot
open, expiry in force) and injected into the component list at the same
append positions component_legs uses. The frozen-parameter regeneration
(min_target 500, cap_index 3) must reproduce the frozen V5 leg set
exactly before any variant is trusted (Cycle 150 validation).

CAUSALITY CERTIFICATE: a V5 leg's admission depends only on its own
system's signal bar and prior-day levels (bias/PDH/PDL/room are prior-day
or signal-bar quantities); the leg enters at the bar after its signal —
the same causal basis as the frozen V5 legs already in the book. The
selection caps are prospective (signal-time) quantities, never realised
outcomes (cap_select_v2 ranks on target_net_rs = prospective target,
setup rank, bias, room — all known at the signal bar)."""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r7_core as c7
from bank_r7_core import judge7, v21_ref
from progressive_capped import load, room_ratio, skill_or_outcome
from progressive_capped_v2 import candidates_for_month, cap_select_v2
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal

SYM = "BANKNIFTY"
TR = Path.home() / "workspace/trading"

# ---------- signal-time maps (o1_janoct.py's index-only recomputation) ----------
def build_sigmaps():
    cache = TR / "bank_r7_ws1_sigmaps.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return ({tuple(k.split("|")): v for k, v in d["v4"].items()},
                {tuple(k.split("|")): v for k, v in d["filt"].items()},
                {k: v for k, v in d["times"].items()})
    v4_sig, filt_sig, times_map = {}, {}, {}
    for sym in ("NIFTY", "BANKNIFTY"):
        spot, daily = load(sym)
        for d, grp in spot.groupby("date"):
            times_map[f"{sym}|{d.date().isoformat()}"] = list(grp.sort_values("timestamp")["time"])
        dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != 2026 or d.month > 10 or i == 0:
                continue
            if str(d.date()) > "2026-10-28":
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            ds = d.date().isoformat()
            r = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40.0)
            if r["exit_reason"] in ("target", "stop", "square_off"):
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                if sig is not None:
                    v4_sig[(sym, ds)] = str(sig["time"])
            raw = day_spot.to_dict("records")
            for c in raw:
                c["timestamp"] = str(c["timestamp"])
            setup, direction, sig = find_skill_signal(raw, ("or",))
            if setup is None:
                continue
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            if direction not in allowed:
                continue
            sig_close = float(sig["close"])
            if direction == "CE" and not (sig_close < pdh):
                continue
            if direction == "PE" and not (sig_close < pdl):
                continue
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            if rr < 1.0:
                continue
            out = skill_or_outcome(raw, sig, direction)
            if out is None:
                continue
            filt_sig[(sym, ds)] = str(sig["time"])
    cache.write_text(json.dumps({
        "v4": {f"{k[0]}|{k[1]}": v for k, v in v4_sig.items()},
        "filt": {f"{k[0]}|{k[1]}": v for k, v in filt_sig.items()},
        "times": times_map}))
    return v4_sig, filt_sig, times_map

V4_SIG, FILT_SIG, TIMES = build_sigmaps()

def entry_after(sym, date, sig_time):
    times = TIMES.get(f"{sym}|{date}")
    if not times or sig_time not in times:
        return None
    i = times.index(sig_time)
    return times[i + 1] if i + 1 < len(times) else None

_CAND_CACHE = {}

def _candidates(month):
    """candidates_for_month does not depend on the cap knobs — compute
    once per month and cache. (The first WS1 run re-ran it for every
    variant: 5 full passes over the candidate universe, ~25 min and
    still not done; killed and fixed here.)"""
    if month not in _CAND_CACHE:
        _CAND_CACHE[month] = candidates_for_month(2026, month)
    return _CAND_CACHE[month]

def v5_bank_legs(min_target=500.0, cap_index=3, cap_stock=3):
    """Regenerated BANKNIFTY V5 v2 legs under the given cap_select knobs."""
    legs, unresolved, skipped = [], 0, 0
    for month in range(1, 11):
        _nd, v4, _raw, skill_filt = _candidates(month)
        pool = {}
        for t in v4 + skill_filt:
            k = (t["symbol"], t["date"])
            if k not in pool or t["setup_rank"] > pool[k]["setup_rank"]:
                pool[k] = t
        picked, _ranked = cap_select_v2(list(pool.values()), min_target,
                                        cap_index, cap_stock)
        for t in picked:
            if t["symbol"] != SYM:
                continue
            sig = V4_SIG.get((SYM, t["date"])) if t["method"] == "V4" \
                else FILT_SIG.get((SYM, t["date"]))
            if not sig:
                unresolved += 1
                continue
            et = entry_after(SYM, t["date"], sig)
            so = c5.SPOT_OPEN.get((t["date"], et)) if et else None
            if et is None or so is None:
                skipped += 1
                continue
            legs.append(c5.mkleg(t["date"], t["direction"], et, c5.atm(so),
                                 c5.expiry_for(t["date"]), "V5 v2", _signal=sig))
    return legs, unresolved, skipped

def components_with_v5(v5_legs):
    """component_legs() with the V5 v2 member replaced by `v5_legs`
    (same append positions: Jan-Sep V5 after (lA) Jan-Sep; Oct V5 in the
    October block where the premium file's V5 rows sat)."""
    legs = []
    v5_js = [l for l in v5_legs if l["date"] < "2026-10-01"]
    v5_oct = [l for l in v5_legs if l["date"] >= "2026-10-01"]
    for r in c5.load_csv("index_options_o1_janoct_trades.csv"):
        if r["index"] != SYM or r["track"] != "(lA) v2":
            continue
        if r["date"] >= "2026-10-01":
            continue
        so = c5.SPOT_OPEN.get((r["date"], r["entry_time"]))
        if so is None:
            continue
        legs.append(c5.mkleg(r["date"], r["direction"], r["entry_time"],
                             c5.atm(so), c5.expiry_for(r["date"]), "(lA) v2",
                             _signal=r["signal_time"]))
    legs.extend(v5_js)
    for r in c5.load_csv("index_options_U1_skillV3_jansep_spot.csv"):
        if r["index"] != SYM:
            continue
        legs.append(c5.mkleg(r["date"], r["direction"], r["entry_time"],
                             c5.atm(float(r["entry_spot"])),
                             c5.expiry_for(r["date"]), "Skill V3",
                             _signal=r["signal_time"]))
    legs.extend(c5.volrix_gen_legs(-0.01, 15))
    for r in c5.load_csv("index_options_premium_october_trades.csv"):
        if r["index"] != SYM or r["premium_status"] != "COMPUTED":
            continue
        if not r["version"].startswith("(lA)"):
            continue
        legs.append(c5.mkleg(r["date"], r["direction"], r["entry_time"],
                             int(float(r["strike"])), r["expiry"], "(lA) v2",
                             _signal=r.get("signal_time", "")))
    legs.extend(v5_oct)
    for r in c5.load_csv("index_options_skill_tuned_oct30_trades.csv"):
        if r["index"] != SYM or r["variant"] != "V3" or r["premium_status"] != "COMPUTED":
            continue
        legs.append(c5.mkleg(r["date"], r["direction"], r["entry_time"],
                             int(float(r["strike"])), r["expiry"], "Skill V3",
                             _signal=r.get("signal_time", "")))
    return legs

def keyset(legs):
    return sorted((l["date"], l["direction"], l["entry_time"], l["strike"])
                  for l in legs)

ref = v21_ref()
print(f"v21 ref: net={ref['net']:+,.2f} n={ref['n']} FT90={ref['ft90_pct']}")

# ---------- Cycle 150: frozen-parameter regeneration validation ----------
frozen_comps = c5.component_legs(volrix=c5.volrix_gen_legs(-0.01, 15))
frozen_v5 = [l for l in frozen_comps if l["rep"] == "V5 v2"]
regen_v5, unr, skp = v5_bank_legs(500.0, 3)
a, b = keyset(frozen_v5), keyset(regen_v5)
print(f"C150 validation: frozen V5 legs {len(a)}, regenerated {len(b)}, "
      f"unresolved {unr}, skipped {skp}")
print("  only-frozen:", [x for x in a if x not in b])
print("  only-regen:  ", [x for x in b if x not in a])
assert a == b, "V5 regeneration does NOT reproduce the frozen set — variants not trusted"
print("C150 PASS: regeneration reproduces the frozen V5 leg set exactly.")

_ns1 = c5.aud_inputs()[1]
def judge_v5(label, min_target, cap_index):
    legs, unr, skp = v5_bank_legs(min_target, cap_index)
    comps = components_with_v5(legs)
    pooled = c5.pool_b2(comps, solo_rule="causal")
    r = judge7(label, ref, pooled, _ns1)
    print("   detail:", r["detail"])
    return r

judge_v5("C151 V5 min_target 250", 250.0, 3)
judge_v5("C152 V5 min_target 1000", 1000.0, 3)
judge_v5("C153 V5 cap_index 5", 500.0, 5)
judge_v5("C154 V5 cap_index 2", 500.0, 2)
