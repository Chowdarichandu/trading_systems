#!/usr/bin/env python3
"""STOCK ENGINE — CAUSAL-THREE TUNING PROGRAMME, STAGE 1 (screen).

Owner order 2026-11-12 06:52 IST: tune the causal three (F4-C /
INV-LONG-C / INV-ABOVE-C) to make the combined Stock Engine
profitable. The failed gate set (stock_engine_causal3_2026-11-12.md)
is NOT retested identically — every variant below differs
mechanically from it and from each other. The 4-live chassis
(reaction family + N4-V3 + production selection economics) is fixed;
only how the causal chain comps earn slots changes.

Pools are rebuilt with the causal3 gate's own builders (identical
code path) and the harness is validated BEFORE any variant is
scored: (a) 4-live baseline via SIM.derive_day must reproduce
39 tr / +Rs8,724.39 / ex-top-3 -Rs3,256.65 exactly; (b) the failed
combined config (stream percentiles, price cap, floor 90) via the
tuned derive must reproduce 162 tr / -Rs4,267.84 / ex-top-3
-Rs18,321.31 exactly. If either fails, the script aborts — no
variant numbers are trusted on an unvalidated harness.

VARIANTS (all keep: causal locks only, max 6 picks/day, each stock
once, Rs40/trade, per-100 primary + Rs25k lens):
  T1 ABSOLUTE-STRENGTH RANKING (chain comps): percentiles dropped.
     A chain candidate's strength = its detector signal's own
     absolute magnitude (%): F4-C -> |premove_pct| (the F4
     construction's own signal magnitude); INV-LONG-C / INV-ABOVE-C
     -> |signal-candle close / prior-day close - 1| x 100 (the
     signal candle is the candle immediately before the entry
     candle — the construction enters at sig_idx+1 open).
     Eligibility floor per comp = 90th percentile (nearest-rank) of
     that comp's FROZEN TWIN's taken trades' absolute magnitudes
     over this same 27-day wide window. Floor applies to the owner
     rep. Score = confluence x 100 + owner strength (strength =
     abs magnitude for chain-owned, norm percentile for reaction /
     N4-owned, as in the chassis).
  T2 SLOT RESERVATION: chain comps <= 2 of the 6 daily slots;
     reaction family + N4 keep first claim at their own decision
     points (09:10 / 09:35); chain candidates are considered only
     at a single 13:30 decision point, with so-far percentiles
     computed on the full morning pool (all chain pool rows enter
     before 10:30, so the 13:30 population is the complete pool).
     Floor 90, price cap Rs5,000 (chassis).
  T3 LATE LOCK + HIGHER FLOOR: as T2's 13:30 chain decision point,
     but no slot cap and the chain floor is the 97th so-far
     percentile (reaction floor stays 90).
  T4 RISK-BASED CAP (chain comps): the Rs5,000 price cap is
     replaced for chain-owned picks by a per-trade risk cap.
     Stop-distance definition (from the construction,
     replay_plain): stop = entry x (1 - sign x SP/100), so the
     stop distance per 100 shares = entry x SP where SP is the
     construction's stop % — INV-LONG-C / INV-ABOVE-C: SP = 0.5
     (PLAIN cell 1.25/0.5) -> risk = entry x 0.5; F4-C: SP = 0.95
     (build2 TP/SP 1.50/0.95) -> risk = entry x 0.95. Cap:
     risk <= Rs1,500 per 100 shares. Reaction / N4 owners keep
     the Rs5,000 price cap. (Arithmetic consequence, stated up
     front: for %-stop constructions the risk cap is a tighter
     effective price cap — INV <= Rs3,000, F4-C <= Rs1,578.95 —
     it cannot admit >Rs5,000 names; it rations chain slots to
     low-rupee-risk trades instead.)
  T5 INV-LONG-C CONFIRMATION: the failed-gate config, except an
     INV-LONG-C-owned pick locks only if the signal is confirmed
     by lock time by either (a) another component's rep for the
     same stock-day in the same direction (LONG) determined by
     the lock decision point — excluding the same underlying
     chain trade under INV-ABOVE-C — or (b) the second detector
     head: at the rep's own chain round, the head that did NOT
     produce the rep's signal (v4 = setup2/3/4, skor = skill_or_*)
     also had a signal in the same direction completing no later
     than the rep's signal candle. An unconfirmed INV-LONG-C
     owner skips the stock-day (chassis owner semantics).

SCREEN PASS BAR (pre-registered): combined ex-top-3 > 0 AND
combined ex-top-3 > -Rs3,256.65 (4-live baseline) AND October
ex-top-3 >= -Rs6,897.97 AND November ex-top-3 >= -Rs1,352.29
(the baseline's same-month ex-top-3; neither month worse).

Paper only, real money Rs0.
Outputs: stock_engine_tuning_2026-11-12_summary.json,
stock_engine_tuning_2026-11-12_picks_<variant>.csv,
stock_engine_tuning_2026-11-12_pools.csv (rebuilt pools, for
Stage 2 / follow-up reuse).
"""
import csv, json, math, sys, time
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import sarvasetu_top3_build as V1
import stock_engine_live_sim as SIM
import stock_engine_causal3_gate as G3
import stocks_sarvaritu_logger as L

ROOT = V1.ROOT
MERGED_CAL = V1.MERGED_CAL
LO, HI = "2026-09-30", "2026-11-11"
OCT_DAYS = SIM.OCT_DAYS
NOV_DAYS = SIM.NOV_DAYS
ALL_DAYS = OCT_DAYS + NOV_DAYS
CHAIN = {"F4-C", "INV-LONG-C", "INV-ABOVE-C"}
INV_C = {"INV-LONG-C", "INV-ABOVE-C"}
SP_PCT = {"F4-C": 0.95, "INV-LONG-C": 0.5, "INV-ABOVE-C": 0.5}
BASELINE = {"trades": 39, "net": 8724.39, "ex_top3": -3256.65,
            "oct_ex_top3": -6897.97, "nov_ex_top3": -1352.29}
FAILED = {"trades": 162, "net": -4267.84, "ex_top3": -18321.31}


# =====================================================================
# magnitudes
# =====================================================================
def signal_displacement(g, stock, day, entry_time):
    """|signal-candle close / prior close - 1| x 100, signed value
    returned; signal candle = candle immediately before the entry
    candle in the >=09:30 list (entry = sig_idx+1 open)."""
    ctx = g["DAYCTX"].get((stock, day))
    if ctx is None:
        return None
    candles = ctx["candles"]
    idx = next((i for i, c in enumerate(candles)
                if c["time"] == entry_time), None)
    if idx is None or idx == 0 or not ctx["pdc"]:
        return None
    return (candles[idx - 1]["close"] / ctx["pdc"] - 1) * 100


def pct90(vals):
    """90th percentile, nearest-rank."""
    s = sorted(vals)
    return s[max(0, math.ceil(0.9 * len(s)) - 1)]


# =====================================================================
# T5 — second-head confirmation replay
# =====================================================================
def chain_round_meta(g, sym, day):
    """run_chain_causal replayed with per-round head capture.
    Returns rounds with both heads' raw signals at the round start."""
    NS = g["NS"]
    ctx = g["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    rounds, start = [], 0
    while True:
        v4 = NS["v4_head"](ctx, start)
        skor = NS["skor_head"](ctx, start)
        chosen = G3.pool_pick_causal(NS, ctx, v4, skor)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        sign = 1 if dirc == "CE" else -1
        _er, _ep, _et, exit_idx, _gr = g["replay_plain"](
            candles, entry_idx, sign, entry, 1.25, 0.5)
        rounds.append({"round": len(rounds) + 1, "setup": setup,
                       "dir": "LONG" if dirc == "CE" else "SHORT",
                       "sig_idx": idx,
                       "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "v4": v4, "skor": skor})
        start = exit_idx
    return rounds


def head_family(setup):
    return "skor" if setup.startswith("skill") else "v4"


def build_confirm_set(g, var_rows, live4_rows, chains_c):
    """Set of (date, stock, round, entry_time) of INV-LONG-C reps
    confirmed per T5 branches (a)/(b)."""
    all_rows = live4_rows + var_rows

    def det_of(r):
        if r["comp"] in SIM.REACTION_COMPS:
            return "09:10"
        if r["comp"] == "N4-V3":
            return "09:35"
        return r["entry_time"]

    confirmed = {}
    reps = [r for r in var_rows if r["comp"] == "INV-LONG-C"]
    meta_cache = {}
    for r in reps:
        key = (r["date"], r["stock"], r["round"], r["entry_time"])
        # branch (a): another component, same stock-day, LONG, by lock
        a = False
        for q in all_rows:
            if q["date"] != r["date"] or q["stock"] != r["stock"]:
                continue
            if q["comp"] == "INV-LONG-C" or q["dir"] != "LONG":
                continue
            if q["comp"] in INV_C and q.get("round") == r["round"] \
                    and q["entry_time"] == r["entry_time"]:
                continue          # same underlying chain trade
            if det_of(q) <= r["entry_time"]:
                a = True
                break
        # branch (b): second detector head at the rep's own round
        b = False
        mk = (r["stock"], r["date"])
        if mk not in meta_cache:
            meta_cache[mk] = chain_round_meta(g, r["stock"], r["date"])
        for rd in meta_cache[mk]:
            if rd["round"] != r["round"]:
                continue
            # fidelity: the meta round must be the rep's chain trade
            assert rd["setup"] == r["setup"] and \
                rd["entry_time"] == r["entry_time"] and \
                rd["dir"] == "LONG", (r, rd)
            fam = head_family(rd["setup"])
            other = rd["skor"] if fam == "v4" else rd["v4"]
            if other[0] is not None and other[1] == "CE" \
                    and other[3] <= rd["sig_idx"]:
                b = True
            break
        if a or b:
            confirmed[key] = {"a_other_component": a,
                              "b_second_head": b}
    return confirmed


# =====================================================================
# tuned selection (SIM.derive_day chassis + variant knobs)
# =====================================================================
def derive_day_tuned(day, pool_day, chain_day, RANK, cfg, confirm=None):
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
            rep["strength"] = -1.0        # never batched (past chain DP)
            rep["norm_pct_live"] = -1.0
            continue
        if comp in INV_C:
            if cfg["chain_rank"] == "absolute":
                rep["strength"] = rep["abs_mag"]
            else:
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
            if cfg["chain_rank"] == "absolute":
                rep["strength"] = rep["abs_mag"]
            else:
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
            # cap
            if owner["entry"] is not None:
                if is_chain and cfg["chain_cap_mode"] == "risk":
                    if owner["entry"] * SP_PCT[owner["comp"]] > \
                            cfg["risk_cap"]:
                        continue
                elif owner["entry"] > SIM.PRICE_CAP:
                    continue
            # floor
            if is_chain and cfg["chain_rank"] == "absolute":
                if owner["strength"] < cfg["abs_floor"][owner["comp"]]:
                    continue
            else:
                thr = cfg["chain_floor"] if is_chain else SIM.FLOOR_PCT
                if owner["strength"] < thr:
                    continue
            # T5 confirmation
            if cfg["invl_confirm"] and owner["comp"] == "INV-LONG-C":
                if (day, stock, owner.get("round"),
                        owner["entry_time"]) not in (confirm or {}):
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


# =====================================================================
# scoring helpers (gate-identical)
# =====================================================================
def pick_stats(recs):
    a = V1.agg(recs)
    ex3, top3 = V1.extop3(recs)
    fc = round(sum(r["fc_net"] for r in recs), 2)
    return {**a, "expectancy": (round(a["net"] / a["trades"], 2)
                                if a["trades"] else 0.0),
            "ex_top3": ex3, "top3_stocks": top3, "fc_net": fc}


def run_variant(days, pool_by_day, chain_by_day, RANK, labels, cfg,
                confirm=None):
    picks_all = []
    for day in days:
        _reps, picks = derive_day_tuned(day, pool_by_day[day],
                                        chain_by_day[day], RANK, cfg,
                                        confirm)
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


def variant_report(recs):
    oct_r = [r for r in recs if r["date"] in OCT_DAYS]
    nov_r = [r for r in recs if r["date"] in NOV_DAYS]
    chain_attr, react_attr = {}, {"picks": 0, "net": 0.0}
    for c in sorted(CHAIN):
        cr = [r for r in recs if r["comp"] == c]
        chain_attr[c] = {"picks": len(cr),
                         "net": round(sum(r["net"] for r in cr), 2)}
    rr = [r for r in recs if r["comp"] not in CHAIN]
    react_attr = {"picks": len(rr),
                  "net": round(sum(r["net"] for r in rr), 2)}
    s, so, sn = pick_stats(recs), pick_stats(oct_r), pick_stats(nov_r)
    screen = {"combined_ex_top3_gt_0": s["ex_top3"] > 0,
              "combined_ex_top3_beats_baseline":
                  s["ex_top3"] > BASELINE["ex_top3"],
              "oct_not_worse": so["ex_top3"] >= BASELINE["oct_ex_top3"],
              "nov_not_worse": sn["ex_top3"] >= BASELINE["nov_ex_top3"]}
    return {"stats": s, "october": so, "november": sn,
            "chain_attribution": chain_attr,
            "reaction_attribution": react_attr,
            "screen": screen,
            "screen_pass": all(screen.values())}


BASE_CFG = {"chain_rank": "stream", "chain_dp": None,
            "chain_floor": 90.0, "chain_slot_cap": None,
            "chain_cap_mode": "price", "risk_cap": 1500.0,
            "abs_floor": None, "invl_confirm": False}


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
    print(f"live4 {len(live4)} rows; causal variant {len(var_rows)} "
          f"rows; chain pop {len(causal_pop)} ({time.time()-t0:.0f}s)",
          flush=True)

    # ---- absolute magnitudes on causal chain rows ----
    n_missing = 0
    for t in var_rows:
        if t["comp"] == "F4-C":
            t["abs_mag"] = abs(t["magnitude"])
        else:
            d = signal_displacement(g, t["stock"], t["date"],
                                    t["entry_time"])
            if d is None:
                n_missing += 1
                t["abs_mag"] = 0.0
            else:
                t["abs_mag"] = round(abs(d), 3)
    print(f"abs_mag attached; missing displacement rows: {n_missing}",
          flush=True)
    assert n_missing == 0

    # ---- T1 floors from the frozen twins' taken trades ----
    frozen_pool = list(csv.DictReader(
        open(f"{WS}/sarvasetu_top3_v2_2026-11-11_pool.csv")))
    floors, floor_detail = {}, {}
    for vc, fc in (("F4-C", "F4"), ("INV-LONG-C", "INV-LONG"),
                   ("INV-ABOVE-C", "INV-ABOVE")):
        mags = []
        for t in frozen_pool:
            if t["comp"] != fc:
                continue
            if fc == "F4":
                mags.append(abs(float(t["magnitude"])))
            else:
                d = signal_displacement(g, t["stock"], t["date"],
                                        t["entry_time"])
                assert d is not None, (fc, t)
                mags.append(abs(d))
        floors[vc] = round(pct90(mags), 3)
        floor_detail[vc] = {"twin_trades": len(mags),
                            "abs_floor_pct": floors[vc],
                            "median": round(sorted(mags)[len(mags) // 2], 3),
                            "max": round(max(mags), 3)}
    print(f"T1 floors: {floor_detail}", flush=True)
    out["t1_floors"] = floor_detail

    # ---- pools by day ----
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

    # ---- harness validation (a): 4-live baseline via SIM.derive_day
    print("validating harness: baseline via SIM.derive_day...",
          flush=True)
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
    print(f"baseline: {bs['trades']} tr {bs['net']:+.2f} ex3 "
          f"{bs['ex_top3']:+.2f} — repro {ok_a}", flush=True)
    assert ok_a, "baseline reproduction FAILED — abort"

    # ---- harness validation (b): failed combined via tuned derive
    print("validating harness: failed combined via tuned derive...",
          flush=True)
    fail_picks = run_variant(days, pool_by_day7, chain_by_day, RANK,
                             labels, dict(BASE_CFG))
    fs = pick_stats(fail_picks)
    ok_b = (fs["trades"] == FAILED["trades"] and fs["net"] == FAILED["net"]
            and fs["ex_top3"] == FAILED["ex_top3"])
    print(f"failed combined: {fs['trades']} tr {fs['net']:+.2f} ex3 "
          f"{fs['ex_top3']:+.2f} — repro {ok_b}", flush=True)
    assert ok_b, "failed-combined reproduction FAILED — abort"
    out["harness_validation"] = {"baseline_repro": ok_a,
                                 "failed_combined_repro": ok_b}

    # ---- T5 confirmation set ----
    print("building T5 confirmation set...", flush=True)
    confirm = build_confirm_set(g, var_rows, live4, chains_c)
    invl_reps = {(r["date"], r["stock"], r["round"], r["entry_time"])
                 for r in var_rows if r["comp"] == "INV-LONG-C"}
    print(f"INV-LONG-C reps: {len(invl_reps)}; confirmed: "
          f"{len(confirm)} (a: "
          f"{sum(1 for v in confirm.values() if v['a_other_component'])}, "
          f"b: {sum(1 for v in confirm.values() if v['b_second_head'])})",
          flush=True)
    out["t5_confirmation"] = {"invl_reps": len(invl_reps),
                              "confirmed": len(confirm)}

    # ---- variants ----
    variants = {}
    cfgs = {
        "T1": {**BASE_CFG, "chain_rank": "absolute", "abs_floor": floors},
        "T2": {**BASE_CFG, "chain_dp": "13:30", "chain_slot_cap": 2},
        "T3": {**BASE_CFG, "chain_dp": "13:30", "chain_floor": 97.0},
        "T4": {**BASE_CFG, "chain_cap_mode": "risk"},
        "T5": {**BASE_CFG, "invl_confirm": True},
    }
    fields = ["date", "lock_order", "lock_time", "stock", "comp", "dir",
              "confluence", "components", "norm_pct", "score",
              "entry_time", "entry", "exit_time", "exit", "exit_reason",
              "net", "fc_shares", "fc_net", "regime"]
    for name, cfg in cfgs.items():
        print(f"scoring {name}...", flush=True)
        recs = run_variant(days, pool_by_day7, chain_by_day, RANK,
                           labels, cfg,
                           confirm if name == "T5" else None)
        rep = variant_report(recs)
        variants[name] = rep
        with open(f"{WS}/stock_engine_tuning_2026-11-12_picks_{name}.csv",
                  "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in recs:
                w.writerow({k: r[k] for k in fields})
        s, so, sn = rep["stats"], rep["october"], rep["november"]
        print(f"{name}: {s['trades']} tr net {s['net']:+.2f} WR "
              f"{s['win_rate']} exp {s['expectancy']:+.2f} ex3 "
              f"{s['ex_top3']:+.2f} | Oct ex3 {so['ex_top3']:+.2f} | "
              f"Nov ex3 {sn['ex_top3']:+.2f} | chain "
              f"{rep['chain_attribution']} | SCREEN PASS: "
              f"{rep['screen_pass']} {rep['screen']}", flush=True)
    out["stage1_variants"] = variants
    out["baseline"] = BASELINE
    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/stock_engine_tuning_2026-11-12_summary.json",
              "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"STAGE 1 DONE in {out['elapsed_secs']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
