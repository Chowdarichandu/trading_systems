#!/usr/bin/env python3
"""STOCK ENGINE — THE INVENTION: "SECOND-HALF GATE" (Deliverable 2,
owner order 2026-11-12 07:10 IST: "invent something which compensates
us… I don't want to lose this, that's the main motto").

DESIGN INTENT: the frozen pool_pick discarded early signals that the
rest of the day invalidated — with hindsight. The causal substitute
is TIME + VALIDITY: a causal chain component may only trade inside
the session window(s) where its entries actually earn (Deliverable
1's map, pre-registered verdict rule), and a signal armed before its
window must still be valid when the window opens.

S1 SESSION WINDOWS: each causal chain comp (F4-C / INV-LONG-C /
INV-ABOVE-C) may lock picks ONLY if its rep's entry_time falls
inside one of its PROFITABLE buckets (from
stock_engine_timeofday_2026-11-12_verdicts.json — the causal
variant's OWN 2026 25-universe map; a comp with no PROFITABLE bucket
sits out entirely). Windows: F4-C [10:30-12:00], INV-LONG-C
[09:15-10:30], INV-ABOVE-C [] (sits out). Everything else is the
failed-gate chassis verbatim (stream percentiles, floor 90, price
cap Rs5,000, max 6/day, reaction family unchanged).

S2 = S1 + STILL-VALID CONFIRMATION for candidates armed BEFORE
their window: if a chain rep's entry_time precedes the start W0 of
its comp's first profitable bucket that opens after the arm, then at
W0 the candidate is checked for validity and, if valid, ENTERED AT
W0 (the trade is re-priced: entry = open of the first candle >= W0,
exits replayed with the comp's own TP/SP geometry — F4-C 1.50/0.95,
INV 1.25/0.5 — via replay_plain; net = gross - Rs40). If invalid it
is discarded and never re-armed (the stock-comp's day is over; later
rows of that comp are NOT promoted — chassis rep semantics).
VALIDITY (uniform, from the construction's own levels): the signal
candle is the candle immediately preceding the candidate's original
entry candle (both chain constructions enter at sig_idx+1 open).
Invalidation level = signal candle LOW for a LONG, HIGH for a
SHORT. Price at window start = close of the last candle with
time < W0. LONG valid iff price >= signal low; SHORT valid iff
price <= signal high. Missing signal/pre-window/entry candle ->
cannot validate -> discarded. Candidates entering inside a window
are S1's (no deferral). INV-LONG-C's window opens 09:15 — nothing
can be armed before it, so its S2 == S1 by construction.

CAUSALITY: eligibility uses entry_time only; validity uses candles
< W0; the deferred entry is the first candle >= W0; percentiles are
the chassis' stream percentiles (data <= det). Asserted in code
(lock_time <= entry_time for every pick) + truncation spot-proof on
2026-10-16 and 2026-11-11 at slices 10:30/12:00/13:30/15:00 (picks
with lock < slice must be identical — identity, direction, entry —
between the full-day run and the candle-truncated rebuild).

HARNESS VALIDATION (before any variant is scored): (a) 4-live
baseline via SIM.derive_day must reproduce 39 tr / +Rs8,724.39 /
ex-top-3 -Rs3,256.65; (b) this script's derive with windows=None
(all buckets allowed, S1 flavour) must reproduce the failed-gate
combined EXACTLY (162 tr / -Rs4,267.84 / ex-top-3 -Rs18,321.31).
Abort if either fails.

WINDOW PLACEBO (mandatory): each comp's window set is replaced by a
same-cardinality RANDOM other bucket set (seeded RNG 20261112, drawn
once, applied identically to S1 and S2; a comp with an empty real
set keeps an empty placebo set). The real windows must beat the
placebo windows on combined ex-top-3 for the variant to pass,
regardless of headline.

STAGE-1 SCREEN (pre-registered, same as the tuning programme):
combined ex-top-3 > 0 AND > -Rs3,256.65 AND October ex-top-3 >=
-Rs6,897.97 AND November ex-top-3 >= -Rs1,352.29 — AND the placebo
leg above. Stage 2 (full controls gate) runs only for a variant
passing Stage 1, in the companion script.

Paper only, real money Rs0. Basis: provisional per 100 shares,
Rs40/trade; Rs25,000 lens on combined engines.
Outputs: stock_engine_secondhalf_2026-11-12_summary.json,
stock_engine_secondhalf_2026-11-12_picks_<S1|S2|PS1|PS2>.csv.
"""
import csv, importlib.util, json, random, sys, time
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stock_engine_live_sim as SIM
import stock_engine_causal3_gate as G3
import stocks_sarvaritu_logger as L

spec = importlib.util.spec_from_file_location(
    "tuning", f"{WS}/stock_engine_tuning_2026-11-12.py")
TUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TUN)
pick_stats, variant_report = TUN.pick_stats, TUN.variant_report

ROOT = V1.ROOT
MERGED_CAL = V1.MERGED_CAL
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = SIM.OCT_DAYS
NOV_DAYS = SIM.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
CHAIN = {"F4-C", "INV-LONG-C", "INV-ABOVE-C"}
INV_C = {"INV-LONG-C", "INV-ABOVE-C"}
TP_SP = {"F4-C": (1.50, 0.95), "INV-LONG-C": (1.25, 0.5),
         "INV-ABOVE-C": (1.25, 0.5)}
BUCKETS4 = ["09:15-10:30", "10:30-12:00", "12:00-13:30", "13:30-15:10"]
BSTART = {"09:15-10:30": "09:15", "10:30-12:00": "10:30",
          "12:00-13:30": "12:00", "13:30-15:10": "13:30"}
BASELINE = TUN.BASELINE
FAILED = TUN.FAILED


def bucket_of(t):
    if "09:15" <= t < "10:30":
        return "09:15-10:30"
    if "10:30" <= t < "12:00":
        return "10:30-12:00"
    if "12:00" <= t < "13:30":
        return "12:00-13:30"
    if "13:30" <= t <= "15:10":
        return "13:30-15:10"
    return "OUTSIDE"


# =====================================================================
# the S-derive: failed-gate chassis + session windows (+ S2 deferral)
# =====================================================================
def derive_day_s(day, pool_day, chain_day, RANK, g, windows, mode):
    """windows: {chain comp: [bucket names]} or None (all allowed).
    mode: 'S1' or 'S2'. Returns (reps, picks); reps carry s2_status
    diagnostics for chain comps."""
    reps = {}
    for t in pool_day:
        k = (t["stock"], t["comp"])
        cur = reps.get(k)
        if cur is None or (t["entry_time"], t.get("round", 0)) < \
                (cur["entry_time"], cur.get("round", 0)):
            reps[k] = dict(t)
    reps = list(reps.values())

    chain_sorted = sorted(chain_day,
                          key=lambda r: (-RANK.get(r["setup"], 0),
                                         r["entry_time"], r["stock"],
                                         r["round"]))
    chain_keys = [(r["stock"], r["round"], r["entry_time"], r["setup"])
                  for r in chain_sorted]

    def chain_base_pct(rep, det):
        so_far = [k for k in chain_keys if k[2] <= det]
        mine = (rep["stock"], rep.get("round"), rep["key_entry_time"],
                rep.get("setup"))
        assert mine in so_far, f"chain rep not in pool {mine}"
        return SIM.pct_of(so_far, mine)

    # ---- determination times (chain eligibility / deferral) ----
    for rep in reps:
        rep["key_entry_time"] = rep["entry_time"]
        rep["synthetic"] = False
        comp = rep["comp"]
        if comp in SIM.REACTION_COMPS:
            rep["det"] = "09:10"
            continue
        if comp == "N4-V3":
            rep["det"] = "09:35"
            continue
        # chain comps
        wins = None if windows is None else windows.get(comp, [])
        if wins is None or bucket_of(rep["entry_time"]) in wins:
            rep["det"] = rep["entry_time"]
            rep["s2_status"] = "in_window"
            continue
        if mode == "S1" or not wins:
            rep["det"] = None
            rep["s2_status"] = "dead_no_window"
            continue
        # S2 deferred channel: first profitable bucket opening later
        starts = sorted(BSTART[b] for b in wins
                        if BSTART[b] > rep["entry_time"])
        if not starts:
            rep["det"] = None
            rep["s2_status"] = "dead_no_window"
            continue
        W0 = starts[0]
        ctx = g["DAYCTX"].get((rep["stock"], day)) if g else None
        if ctx is None:
            rep["det"] = None
            rep["s2_status"] = "dead_no_data"
            continue
        candles = ctx["candles"]
        idx = next((i for i, c in enumerate(candles)
                    if c["time"] == rep["entry_time"]), None)
        pre = [c for c in candles if c["time"] < W0]
        ei = next((i for i, c in enumerate(candles)
                   if c["time"] >= W0), None)
        if idx is None or idx == 0 or not pre or ei is None:
            rep["det"] = None
            rep["s2_status"] = "dead_no_data"
            continue
        sig = candles[idx - 1]
        price = pre[-1]["close"]
        if rep["dir"] == "LONG":
            valid = price >= sig["low"]
        else:
            valid = price <= sig["high"]
        if not valid:
            rep["det"] = None
            rep["s2_status"] = "deferred_invalid"
            continue
        entry = float(candles[ei]["open"])
        sign = 1 if rep["dir"] == "LONG" else -1
        tp, sp = TP_SP[comp]
        er, ep, et, _xi, gross = g["replay_plain"](
            candles, ei, sign, entry, tp, sp)
        rep["orig_entry_time"] = rep["entry_time"]
        rep["orig_entry"] = rep["entry"]
        rep["orig_net"] = rep["net"]
        rep["entry_time"] = candles[ei]["time"]
        rep["entry"] = round(entry, 2)
        rep["exit"] = round(ep, 2)
        rep["exit_time"] = et
        rep["exit_reason"] = er
        rep["net"] = round(gross - 40.0, 2)
        rep["det"] = W0
        rep["synthetic"] = True
        rep["s2_status"] = "deferred_valid"

    # ---- base magnitudes (INV stream percentiles) ----
    for rep in reps:
        if rep["comp"] in INV_C:
            det = rep["det"] if rep["det"] else rep["key_entry_time"]
            rep["base_mag"] = chain_base_pct(rep, det)

    # ---- normalised percentiles (chassis stream semantics) ----
    for rep in reps:
        comp, det = rep["comp"], rep["det"]
        if det is None:
            rep["strength"] = -1.0
            rep["norm_pct_live"] = -1.0
            continue
        if comp in INV_C:
            pop = [r for r in reps if r["comp"] == comp
                   and r["det"] is not None and r["det"] <= det]
            pop.sort(key=lambda r: (-r["base_mag"], r["key_entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
        elif comp in SIM.REACTION_COMPS or comp == "N4-V3":
            pop = [r for r in reps if r["comp"] == comp]
            pop.sort(key=lambda r: (-r["magnitude"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
        else:  # F4-C: magnitude percentile among reps determined so far
            pop = [r for r in reps if r["comp"] == comp
                   and r["det"] is not None and r["det"] <= det]
            pop.sort(key=lambda r: (-r["magnitude"],
                                    r["key_entry_time"], r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
        rep["norm_pct_live"] = rep["strength"]

    # ---- decision-point loop (chassis verbatim) ----
    dps = sorted({r["det"] for r in reps if r["det"]})
    locked, picks = {}, []
    for dp in dps:
        batch = [r for r in reps if r["det"] == dp]
        by_stock = defaultdict(list)
        for r in batch:
            by_stock[r["stock"]].append(r)
        cands = []
        for stock, rs in by_stock.items():
            if stock in locked:
                continue
            owner = sorted(rs, key=lambda r: (-r["strength"],
                                              r["entry_time"],
                                              r["comp"]))[0]
            if owner["entry"] is not None \
                    and owner["entry"] > SIM.PRICE_CAP:
                continue
            if owner["strength"] < SIM.FLOOR_PCT:
                continue
            determined = [r for r in reps if r["stock"] == stock
                          and r["det"] is not None and r["det"] <= dp]
            confluence = len({r["comp"] for r in determined})
            owner_strength = max(r["strength"] for r in determined)
            cands.append({"stock": stock, "rep": owner,
                          "confluence": confluence,
                          "components": sorted({r["comp"]
                                                for r in determined}),
                          "owner_pct": owner_strength,
                          "score": confluence * 100 + owner_strength,
                          "lock_time": dp})
        cands.sort(key=lambda c: (-c["score"], c["stock"]))
        for c in cands:
            if len(picks) >= SIM.TOPN:
                break
            if c["stock"] in locked:
                continue
            locked[c["stock"]] = c
            picks.append(c)
    return reps, picks


def run_s(days, pool_by_day, chain_by_day, RANK, labels, g, windows,
          mode):
    picks_all, diag = [], defaultdict(int)
    for day in days:
        reps, picks = derive_day_s(day, pool_by_day[day],
                                   chain_by_day[day], RANK, g,
                                   windows, mode)
        for r in reps:
            if r["comp"] in CHAIN and "s2_status" in r:
                diag[r["s2_status"]] += 1
                if r.get("synthetic"):
                    diag["synthetic_reps"] += 1
        for i, p in enumerate(picks):
            t = p["rep"]
            assert p["lock_time"] <= t["entry_time"], (day, p)
            shares, fc = SIM.lens_net(t)
            picks_all.append(
                {"date": day, "lock_order": i + 1,
                 "lock_time": p["lock_time"], "stock": p["stock"],
                 "comp": t["comp"], "dir": t["dir"],
                 "confluence": p["confluence"],
                 "components": "+".join(p["components"]),
                 "norm_pct": t["norm_pct_live"],
                 "score": round(p["score"], 2),
                 "entry_time": t["entry_time"], "entry": t["entry"],
                 "exit_time": t["exit_time"], "exit": t["exit"],
                 "exit_reason": t["exit_reason"], "net": t["net"],
                 "fc_shares": shares, "fc_net": fc,
                 "regime": labels.get(day, "UNCLASSIFIED"),
                 "synthetic": bool(t.get("synthetic"))})
    return picks_all, dict(diag)


FIELDS = ["date", "lock_order", "lock_time", "stock", "comp", "dir",
          "confluence", "components", "norm_pct", "score", "entry_time",
          "entry", "exit_time", "exit", "exit_reason", "net",
          "fc_shares", "fc_net", "regime", "synthetic"]


def write_picks(name, recs):
    with open(f"{WS}/stock_engine_secondhalf_2026-11-12_picks_{name}.csv",
              "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in recs:
            w.writerow({k: r[k] for k in FIELDS})


def screen_of(recs, placebo_recs=None):
    rep = variant_report(recs)
    s = rep["stats"]
    legs = dict(rep["screen"])
    if placebo_recs is not None:
        ps = pick_stats(placebo_recs)
        legs["beats_placebo_ex_top3"] = s["ex_top3"] > ps["ex_top3"]
        rep["placebo"] = {"stats": ps,
                           "ex_top3": ps["ex_top3"]}
    rep["all_legs"] = legs
    rep["stage1_pass"] = all(legs.values())
    return rep


def main():
    t0 = time.time()
    out = {"started": time.strftime("%Y-%m-%d %H:%M UTC")}
    print("loading wide machinery...", flush=True)
    g = V1.load_machinery(ROOT, HI)
    days = [d for d in ALL_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    assert days == ALL_DAYS, days
    labels = L.regime_labels(g)

    print("rebuilding pools (gate code path)...", flush=True)
    chains_c = {}
    for sym in g["SYMBOLS"]:
        for day in days:
            chains_c[(sym, day)] = G3.run_chain_causal(g, sym, day)
    var_rows, causal_pop = G3.causal_variant_rows(g, days, chains_c)
    live4 = G3.build_live4_detailed(g, MERGED_CAL, LO, HI, days)
    live4 = L.apply_law(live4, labels)
    for t in live4:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    var_rows = G3.apply_law_mapped(var_rows, labels)
    for t in var_rows:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    chain_by_day = defaultdict(list)
    for r in causal_pop:
        chain_by_day[r["date"]].append(r)
    pool_by_day4 = defaultdict(list)
    for t in live4:
        pool_by_day4[t["date"]].append(t)
    pool_by_day7 = defaultdict(list)
    for t in live4 + var_rows:
        pool_by_day7[t["date"]].append(t)
    RANK = g["NS"]["RANK"]
    print(f"pools rebuilt ({time.time()-t0:.0f}s)", flush=True)

    # ---- harness validation (a): baseline via SIM.derive_day
    base_picks = []
    for day in days:
        _r, picks = SIM.derive_day(day, [dict(t) for t in pool_by_day4[day]],
                                   defaultdict(list), RANK)
        for p in picks:
            base_picks.append({"date": day, "stock": p["stock"],
                               "comp": p["rep"]["comp"],
                               "net": p["rep"]["net"],
                               "fc_net": SIM.lens_net(p["rep"])[1]})
    bs = pick_stats(base_picks)
    ok_a = (bs["trades"] == BASELINE["trades"]
            and bs["net"] == BASELINE["net"]
            and bs["ex_top3"] == BASELINE["ex_top3"])
    print(f"baseline repro: {ok_a} ({bs['trades']} tr {bs['net']:+.2f} "
          f"ex3 {bs['ex_top3']:+.2f})", flush=True)
    assert ok_a, "baseline reproduction FAILED — abort"

    # ---- harness validation (b): no-window S-derive == failed gate
    fail_recs, _ = run_s(days, pool_by_day7, chain_by_day, RANK, labels,
                         g, None, "S1")
    fs = pick_stats(fail_recs)
    ok_b = (fs["trades"] == FAILED["trades"] and fs["net"] == FAILED["net"]
            and fs["ex_top3"] == FAILED["ex_top3"])
    print(f"failed-gate repro via S-derive: {ok_b} ({fs['trades']} tr "
          f"{fs['net']:+.2f} ex3 {fs['ex_top3']:+.2f})", flush=True)
    assert ok_b, "failed-gate reproduction FAILED — abort"
    out["harness_validation"] = {"baseline_repro": ok_a,
                                 "failed_combined_repro": ok_b}

    # ---- windows (real + placebo)
    verd = json.load(open(
        f"{WS}/stock_engine_timeofday_2026-11-12_verdicts.json"))
    windows = verd["s1_windows"]
    print(f"real windows: {windows}", flush=True)
    rng = random.Random(20261112)
    placebo_windows = {}
    for comp in ("F4-C", "INV-LONG-C", "INV-ABOVE-C"):
        real = sorted(windows.get(comp, []))
        k = len(real)
        if k == 0:
            placebo_windows[comp] = []
            continue
        for _try in range(200):
            draw = sorted(rng.sample(BUCKETS4, k))
            if draw != real:
                placebo_windows[comp] = draw
                break
    print(f"placebo windows: {placebo_windows}", flush=True)
    out["windows"] = windows
    out["placebo_windows"] = placebo_windows

    # ---- Stage 1: real + placebo, S1 + S2
    results = {}
    recs = {}
    for name, wins, mode in (("S1", windows, "S1"),
                             ("S2", windows, "S2"),
                             ("PS1", placebo_windows, "S1"),
                             ("PS2", placebo_windows, "S2")):
        print(f"scoring {name}...", flush=True)
        r, diag = run_s(days, pool_by_day7, chain_by_day, RANK, labels,
                        g, wins, mode)
        recs[name] = r
        write_picks(name, r)
        results[name] = {"diag": diag}
        s = pick_stats(r)
        print(f"{name}: {s['trades']} tr net {s['net']:+.2f} ex3 "
              f"{s['ex_top3']:+.2f} diag {diag}", flush=True)
    for name, pname in (("S1", "PS1"), ("S2", "PS2")):
        rep = screen_of(recs[name], recs[pname])
        results[name]["report"] = rep
        print(f"{name} STAGE-1 PASS: {rep['stage1_pass']} legs "
              f"{rep['all_legs']} (placebo ex3 "
              f"{rep['placebo']['ex_top3']:+.2f})", flush=True)
    out["stage1"] = {k: {"report": results[k].get("report"),
                         "diag": results[k]["diag"]}
                     for k in ("S1", "S2")}
    out["placebo_stats"] = {k: pick_stats(recs[k]) for k in ("PS1", "PS2")}

    # ---- truncation spot-proof (S1 + S2, real windows)
    print("truncation spot-proof (2026-10-16, 2026-11-11)...",
          flush=True)
    spot = []
    for day in ("2026-10-16", "2026-11-11"):
        live4_day = [t for t in live4 if t["date"] == day]
        full = {}
        for mode in ("S1", "S2"):
            _r, picks = derive_day_s(day, pool_by_day7[day],
                                     chain_by_day[day], RANK, g,
                                     windows, mode)
            full[mode] = [{"stock": p["stock"], "comp": p["rep"]["comp"],
                           "dir": p["rep"]["dir"],
                           "entry_time": p["rep"]["entry_time"],
                           "entry": p["rep"]["entry"],
                           "lock_time": p["lock_time"]} for p in picks]
        for sl in ("10:30", "12:00", "13:30", "15:00"):
            saved = {}
            for sym in g["SYMBOLS"]:
                ctx = g["DAYCTX"].get((sym, day))
                if ctx is None:
                    continue
                saved[sym] = ctx["candles"]
                ctx["candles"] = [c for c in saved[sym]
                                  if c["time"] < sl]
            try:
                ch = {}
                for sym in g["SYMBOLS"]:
                    ch[(sym, day)] = G3.run_chain_causal(g, sym, day)
                vr, pop = G3.causal_variant_rows(g, [day], ch)
                vr = G3.apply_law_mapped(vr, labels)
                pool_t = live4_day + vr
                chain_t = [r for r in pop if r["date"] == day]
                for mode in ("S1", "S2"):
                    _r, picks = derive_day_s(day, pool_t, chain_t,
                                             RANK, g, windows, mode)
                    got = [{"stock": p["stock"],
                            "comp": p["rep"]["comp"],
                            "dir": p["rep"]["dir"],
                            "entry_time": p["rep"]["entry_time"],
                            "entry": p["rep"]["entry"],
                            "lock_time": p["lock_time"]}
                           for p in picks if p["lock_time"] < sl]
                    want = [p for p in full[mode]
                            if p["lock_time"] < sl]
                    ok = got == want
                    spot.append({"day": day, "slice": sl, "mode": mode,
                                 "checked": len(want), "pass": ok,
                                 "got": got if not ok else None,
                                 "want": want if not ok else None})
                    print(f"SPOT {day} {sl} {mode}: {len(want)} picks "
                          f"lock<slice — {'PASS' if ok else 'FAIL'}",
                          flush=True)
            finally:
                for sym, cd in saved.items():
                    g["DAYCTX"][(sym, day)]["candles"] = cd
    out["truncation_spot_proof"] = spot
    out["spot_proof_pass"] = all(s["pass"] for s in spot)
    print(f"SPOT PROOF PASS: {out['spot_proof_pass']}", flush=True)

    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/stock_engine_secondhalf_2026-11-12_summary.json",
              "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"STAGE 1 DONE in {out['elapsed_secs']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
