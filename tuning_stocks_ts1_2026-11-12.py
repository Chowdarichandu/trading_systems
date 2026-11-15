#!/usr/bin/env python3
"""STOCKS TUNING PROGRAMME T-S1 (owner order 2026-11-12 16:23 IST:
"I need tuning all 3") — THE ONE UNTESTED COMBINATION.

T-S1 = Stock Engine S1 session windows (F4-C -> [10:30-12:00],
INV-LONG-C -> [09:15-10:30], INV-ABOVE-C excluded; from
stock_engine_timeofday_2026-11-12.md) WITH T2's slot reservation
(chain <= 2 of the 6 daily slots; chain candidates decided at a
single 13:30 decision point; from stock_engine_tuning_2026-11-12.md)
applied together. Mechanically distinct from all 8 failed
configurations (causal-3 raw gate, T1-T5, S1, S2).

Implementation: derive_day_tuned (the tuning programme's chassis,
verbatim) + ONE added step in the chain determination block: a chain
rep whose entry_time bucket is outside its comp's S1 window is dead
(det=None) BEFORE the T2 13:30 assignment. Rep semantics preserved:
the rep (earliest row per stock-comp) is chosen first; an
out-of-window rep sits out and later rows are NOT promoted (S-derive
chassis semantics). Chain percentiles/base magnitudes are T2's
(chain_base_pct evaluated at det=13:30 over the full causal chain
population with entry_time <= 13:30). Reaction family (09:10) and
N4-V3 (09:35) are untouched; chain floor 90, price cap Rs5,000,
max 6 picks/day — all chassis values.

HARNESS VALIDATIONS (abort if any fails, before T-S1 is scored):
 (a) 4-live baseline via SIM.derive_day == 39 tr / +Rs8,724.39 /
     ex-top-3 -Rs3,256.65.
 (b) TS1 derive, windows OFF + stream + no slot cap == failed-gate
     combined 162 tr / -Rs4,267.84 / ex-top-3 -Rs18,321.31.
 (c) TS1 derive, windows OFF + 13:30 + cap 2 == T2 exactly:
     93 tr / +Rs3,023.65 / ex-top-3 -Rs8,957.39 (Oct ex3
     -Rs14,228.64, Nov ex3 -Rs1,879.38).
 (d) TS1 derive, windows ON + stream + no slot cap == S1 exactly:
     131 tr / +Rs11,673.55 / ex-top-3 -Rs1,762.49.

PRE-REGISTERED PASS BAR (task, unmoved): combined ex-top-3 >
baseline ex-top-3 (-Rs3,256.65) AND headline net > baseline net
(+Rs8,724.39) AND neither month worse (Oct ex-top-3 >= -Rs6,897.97,
Nov ex-top-3 >= -Rs1,352.29) AND T-S1 beats its placebo (identical
cfg, placebo windows from the secondhalf programme — seed 20261112
draw, stored in stock_engine_secondhalf_2026-11-12_summary.json).
Full-gate extras in the same run: truncation spot-proof on
2026-10-16 and 2026-11-11 at slices 10:30/12:00/13:30/15:00 (picks
with lock_time < slice identical between full-day and
candle-truncated rebuilds) and an independent re-sum of the written
picks CSV (fresh aggregation, no harness code).

NOTE on the 13:30 decision point (inherited from T2 verbatim): chain
picks lock at 13:30 on information timestamped <= 13:30 only
(windowed chain entries are all <= 12:00; base magnitudes and
percentile populations are evaluated at det=13:30), while the fill
remains the chassis morning entry — the same selection semantics
under which T2/T3 were screened. The truncation proof is the
causality instrument applied here.

Paper only, real money Rs0. Basis: provisional per 100 shares,
Rs40/trade; Rs25,000 lens (fc_net) secondary.
Outputs: tuning_stocks_2026-11-12_picks_<TS1|PTS1>.csv,
tuning_stocks_2026-11-12_ts1_summary.json.
"""
import csv, importlib.util, json, sys, time
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
pick_stats = TUN.pick_stats

ROOT = V1.ROOT
MERGED_CAL = V1.MERGED_CAL
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = SIM.OCT_DAYS
NOV_DAYS = SIM.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
CHAIN = {"F4-C", "INV-LONG-C", "INV-ABOVE-C"}
INV_C = {"INV-LONG-C", "INV-ABOVE-C"}
BASELINE = TUN.BASELINE
FAILED = TUN.FAILED
T2_PUBLISHED = {"trades": 93, "net": 3023.65, "ex_top3": -8957.39,
                "oct_ex_top3": -14228.64, "nov_ex_top3": -1879.38}
S1_PUBLISHED = {"trades": 131, "net": 11673.55, "ex_top3": -1762.49}
BASE_CFG = dict(TUN.BASE_CFG)


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
# TS1 derive = derive_day_tuned verbatim + S1 window eligibility
# =====================================================================
def derive_day_ts1(day, pool_day, chain_day, RANK, cfg, windows=None):
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
        mine = (rep["stock"], rep.get("round"), rep["entry_time"],
                rep.get("setup"))
        assert mine in so_far, f"chain rep not in pool {mine}"
        return SIM.pct_of(so_far, mine)

    for rep in reps:
        comp = rep["comp"]
        if comp in SIM.REACTION_COMPS:
            rep["det"] = "09:10"
        elif comp == "N4-V3":
            rep["det"] = "09:35"
        elif windows is not None and \
                bucket_of(rep["entry_time"]) not in windows.get(comp, []):
            rep["det"] = None          # S1 window eligibility (T-S1 step)
        elif cfg["chain_dp"]:
            rep["det"] = "13:30" if rep["entry_time"] <= "13:30" else None
        else:
            rep["det"] = rep["entry_time"]
    for rep in reps:
        if rep["comp"] in INV_C:
            det = rep["det"] if rep["det"] else rep["entry_time"]
            rep["base_mag"] = chain_base_pct(rep, det)
    for rep in reps:
        comp, det = rep["comp"], rep["det"]
        if det is None:
            rep["strength"] = -1.0
            rep["norm_pct_live"] = -1.0
            continue
        if comp in INV_C:
            pop = [r for r in reps if r["comp"] == comp
                   and r["det"] is not None and det is not None
                   and r["det"] <= det]
            pop.sort(key=lambda r: (-r["base_mag"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
            rep["norm_pct_live"] = rep["strength"]
        elif comp in SIM.REACTION_COMPS or comp == "N4-V3":
            pop = [r for r in reps if r["comp"] == comp]
            pop.sort(key=lambda r: (-r["magnitude"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
            rep["norm_pct_live"] = rep["strength"]
        else:  # F4-C
            pop = [r for r in reps if r["comp"] == comp
                   and r["det"] is not None and det is not None
                   and r["det"] <= det]
            pop.sort(key=lambda r: (-r["magnitude"], r["entry_time"],
                                    r["stock"]))
            keys = [(r["stock"], r["comp"]) for r in pop]
            rep["strength"] = SIM.pct_of(keys, (rep["stock"], comp))
            rep["norm_pct_live"] = rep["strength"]

    dps = sorted({r["det"] for r in reps if r["det"]})
    locked, picks, chain_locked = {}, [], 0
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
            is_chain = owner["comp"] in CHAIN
            if owner["entry"] is not None:
                if owner["entry"] > SIM.PRICE_CAP:
                    continue
            thr = cfg["chain_floor"] if is_chain else SIM.FLOOR_PCT
            if owner["strength"] < thr:
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
                          "lock_time": dp, "is_chain": is_chain})
        cands.sort(key=lambda c: (-c["score"], c["stock"]))
        for c in cands:
            if len(picks) >= SIM.TOPN:
                break
            if c["stock"] in locked:
                continue
            if c["is_chain"] and cfg["chain_slot_cap"] is not None \
                    and chain_locked >= cfg["chain_slot_cap"]:
                continue
            locked[c["stock"]] = c
            picks.append(c)
            if c["is_chain"]:
                chain_locked += 1
    return reps, picks


def run_ts1(days, pool_by_day, chain_by_day, RANK, labels, cfg,
            windows=None):
    picks_all = []
    for day in days:
        _reps, picks = derive_day_ts1(day, pool_by_day[day],
                                      chain_by_day[day], RANK, cfg,
                                      windows)
        for i, p in enumerate(picks):
            t = p["rep"]
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
                 "regime": labels.get(day, "UNCLASSIFIED")})
    return picks_all


FIELDS = ["date", "lock_order", "lock_time", "stock", "comp", "dir",
          "confluence", "components", "norm_pct", "score",
          "entry_time", "entry", "exit_time", "exit", "exit_reason",
          "net", "fc_shares", "fc_net", "regime"]


def write_picks(name, recs):
    with open(f"{WS}/tuning_stocks_2026-11-12_picks_{name}.csv",
              "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in recs:
            w.writerow({k: r[k] for k in FIELDS})


def resum_check(name, recs):
    """Independent re-sum from the written CSV (plain aggregation)."""
    rows = list(csv.DictReader(
        open(f"{WS}/tuning_stocks_2026-11-12_picks_{name}.csv")))
    assert len(rows) == len(recs), (len(rows), len(recs))
    net = round(sum(float(r["net"]) for r in rows), 2)
    fc = round(sum(float(r["fc_net"]) for r in rows), 2)
    by_stock = defaultdict(float)
    for r in rows:
        by_stock[r["stock"]] += float(r["net"])
    top3 = sorted(by_stock.items(), key=lambda kv: -kv[1])[:3]
    ex3 = round(net - sum(v for _k, v in top3), 2)
    oct_net = round(sum(float(r["net"]) for r in rows
                        if r["date"] in OCT_DAYS), 2)
    nov_net = round(sum(float(r["net"]) for r in rows
                        if r["date"] in NOV_DAYS), 2)
    s = pick_stats(recs)
    ok = (net == s["net"] and fc == s["fc_net"]
          and ex3 == s["ex_top3"]
          and oct_net == pick_stats([r for r in recs
                                     if r["date"] in OCT_DAYS])["net"]
          and nov_net == pick_stats([r for r in recs
                                     if r["date"] in NOV_DAYS])["net"])
    return {"ok": ok, "net": net, "fc_net": fc, "ex_top3": ex3,
            "oct_net": oct_net, "nov_net": nov_net}


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

    verd = json.load(open(
        f"{WS}/stock_engine_timeofday_2026-11-12_verdicts.json"))
    windows = verd["s1_windows"]
    sh_sum = json.load(open(
        f"{WS}/stock_engine_secondhalf_2026-11-12_summary.json"))
    placebo_windows = sh_sum["placebo_windows"]
    print(f"windows: {windows}; placebo: {placebo_windows}", flush=True)
    out["windows"] = windows
    out["placebo_windows"] = placebo_windows

    # ---- validation (a): baseline via SIM.derive_day
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
    print(f"(a) baseline repro: {ok_a} ({bs['trades']} tr "
          f"{bs['net']:+.2f} ex3 {bs['ex_top3']:+.2f})", flush=True)
    assert ok_a, "baseline reproduction FAILED — abort"

    # ---- validation (b): failed combined via TS1 derive
    fb = run_ts1(days, pool_by_day7, chain_by_day, RANK, labels,
                 dict(BASE_CFG), None)
    fs = pick_stats(fb)
    ok_b = (fs["trades"] == FAILED["trades"] and fs["net"] == FAILED["net"]
            and fs["ex_top3"] == FAILED["ex_top3"])
    print(f"(b) failed-combined repro: {ok_b} ({fs['trades']} tr "
          f"{fs['net']:+.2f} ex3 {fs['ex_top3']:+.2f})", flush=True)
    assert ok_b, "failed-combined reproduction FAILED — abort"

    # ---- validation (c): T2 exact via TS1 derive (windows OFF)
    t2cfg = {**BASE_CFG, "chain_dp": "13:30", "chain_slot_cap": 2}
    t2 = run_ts1(days, pool_by_day7, chain_by_day, RANK, labels,
                 dict(t2cfg), None)
    t2s = pick_stats(t2)
    t2o = pick_stats([r for r in t2 if r["date"] in OCT_DAYS])
    t2n = pick_stats([r for r in t2 if r["date"] in NOV_DAYS])
    ok_c = (t2s["trades"] == T2_PUBLISHED["trades"]
            and t2s["net"] == T2_PUBLISHED["net"]
            and t2s["ex_top3"] == T2_PUBLISHED["ex_top3"]
            and t2o["ex_top3"] == T2_PUBLISHED["oct_ex_top3"]
            and t2n["ex_top3"] == T2_PUBLISHED["nov_ex_top3"])
    print(f"(c) T2 repro: {ok_c} ({t2s['trades']} tr {t2s['net']:+.2f} "
          f"ex3 {t2s['ex_top3']:+.2f})", flush=True)
    assert ok_c, "T2 reproduction FAILED — abort"

    # ---- validation (d): S1 exact via TS1 derive (stream, windows ON)
    s1 = run_ts1(days, pool_by_day7, chain_by_day, RANK, labels,
                 dict(BASE_CFG), windows)
    s1s = pick_stats(s1)
    ok_d = (s1s["trades"] == S1_PUBLISHED["trades"]
            and s1s["net"] == S1_PUBLISHED["net"]
            and s1s["ex_top3"] == S1_PUBLISHED["ex_top3"])
    print(f"(d) S1 repro: {ok_d} ({s1s['trades']} tr {s1s['net']:+.2f} "
          f"ex3 {s1s['ex_top3']:+.2f})", flush=True)
    assert ok_d, "S1 reproduction FAILED — abort"
    out["harness_validation"] = {"baseline_repro": ok_a,
                                 "failed_combined_repro": ok_b,
                                 "t2_repro": ok_c, "s1_repro": ok_d}

    # ---- T-S1 and its placebo
    print("scoring T-S1 (windows + 13:30 + cap 2)...", flush=True)
    ts1 = run_ts1(days, pool_by_day7, chain_by_day, RANK, labels,
                  dict(t2cfg), windows)
    write_picks("TS1", ts1)
    print("scoring placebo-TS1...", flush=True)
    pts1 = run_ts1(days, pool_by_day7, chain_by_day, RANK, labels,
                   dict(t2cfg), placebo_windows)
    write_picks("PTS1", pts1)
    for name, recs in (("TS1", ts1), ("PTS1", pts1)):
        s = pick_stats(recs)
        so = pick_stats([r for r in recs if r["date"] in OCT_DAYS])
        sn = pick_stats([r for r in recs if r["date"] in NOV_DAYS])
        chain_attr = {c: {"picks": len([r for r in recs
                                        if r["comp"] == c]),
                          "net": round(sum(r["net"] for r in recs
                                           if r["comp"] == c), 2)}
                      for c in sorted(CHAIN)}
        rr = [r for r in recs if r["comp"] not in CHAIN]
        out[name] = {"stats": s, "october": so, "november": sn,
                     "chain_attribution": chain_attr,
                     "reaction_attribution":
                         {"picks": len(rr),
                          "net": round(sum(r["net"] for r in rr), 2)}}
        print(f"{name}: {s['trades']} tr net {s['net']:+.2f} WR "
              f"{s['win_rate']} exp {s['expectancy']:+.2f} ex3 "
              f"{s['ex_top3']:+.2f} fc {s['fc_net']:+.2f} | Oct ex3 "
              f"{so['ex_top3']:+.2f} | Nov ex3 {sn['ex_top3']:+.2f} | "
              f"chain {chain_attr}", flush=True)

    # ---- gate legs (pre-registered)
    s, so, sn = out["TS1"]["stats"], out["TS1"]["october"], \
        out["TS1"]["november"]
    legs = {
        "combined_ex_top3_gt_baseline":
            s["ex_top3"] > BASELINE["ex_top3"],
        "headline_improvement": s["net"] > BASELINE["net"],
        "october_not_worse": so["ex_top3"] >= BASELINE["oct_ex_top3"],
        "november_not_worse": sn["ex_top3"] >= BASELINE["nov_ex_top3"],
        "beats_placebo_ex_top3":
            s["ex_top3"] > out["PTS1"]["stats"]["ex_top3"],
    }
    out["gate_legs"] = legs
    print(f"gate legs: {legs}", flush=True)

    # ---- independent re-sum
    for name, recs in (("TS1", ts1), ("PTS1", pts1)):
        rc = resum_check(name, recs)
        out[f"resum_{name}"] = rc
        print(f"re-sum {name}: {rc}", flush=True)
        assert rc["ok"], f"re-sum mismatch {name}"

    # ---- truncation spot-proof (TS1 config)
    print("truncation spot-proof (TS1)...", flush=True)
    spot = []
    for day in ("2026-10-16", "2026-11-11"):
        live4_day = [t for t in live4 if t["date"] == day]
        _r, picks = derive_day_ts1(day, pool_by_day7[day],
                                   chain_by_day[day], RANK,
                                   dict(t2cfg), windows)
        full = [{"stock": p["stock"], "comp": p["rep"]["comp"],
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
                _r, picks_t = derive_day_ts1(day, pool_t, chain_t,
                                             RANK, dict(t2cfg),
                                             windows)
                got = [{"stock": p["stock"], "comp": p["rep"]["comp"],
                        "dir": p["rep"]["dir"],
                        "entry_time": p["rep"]["entry_time"],
                        "entry": p["rep"]["entry"],
                        "lock_time": p["lock_time"]}
                       for p in picks_t if p["lock_time"] < sl]
                want = [p for p in full if p["lock_time"] < sl]
                ok = got == want
                spot.append({"day": day, "slice": sl,
                             "checked": len(want), "pass": ok,
                             "got": got if not ok else None,
                             "want": want if not ok else None})
                print(f"SPOT {day} {sl}: {len(want)} picks lock<slice "
                      f"— {'PASS' if ok else 'FAIL'}", flush=True)
            finally:
                for sym, cd in saved.items():
                    g["DAYCTX"][(sym, day)]["candles"] = cd
    out["truncation_spot_proof"] = spot
    out["spot_proof_pass"] = all(x["pass"] for x in spot)
    out["gate_legs"]["truncation_spot_proof"] = out["spot_proof_pass"]
    out["gate_pass"] = all(out["gate_legs"].values())
    print(f"SPOT PROOF PASS: {out['spot_proof_pass']}; "
          f"GATE PASS: {out['gate_pass']}", flush=True)

    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/tuning_stocks_2026-11-12_ts1_summary.json",
              "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"T-S1 DONE in {out['elapsed_secs']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
