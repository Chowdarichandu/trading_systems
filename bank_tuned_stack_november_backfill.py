#!/usr/bin/env python3
"""RETROSPECTIVE BACKFILL — Bank Nifty TUNED STACK, November 2026 days
2026-11-02/03/04/05/06/09. Owner ask 2026-11-10: "run the tune stack
from November 1 to November 9th so we can see how it is going."

This is a RETROSPECTIVE backfill: scored after the days traded, from
stored/served candles. It is NOT a live run and NOT a gate.

THE STACK (frozen definition, bank_aggressive_tune_2026-11-04.md;
banked cycles c4 + v1 on top of v22 + EVE-06(a); final Jan-Oct book
+Rs 123,471.50 / 115 legs):
  = SHADOW v22 frame (v21 assembly + EVE-04 NS1 FC-2 give-back lock
    + EVE-05 pre-10:30 OR-break PE skip)
  + EVE-06(a) re-entry (bank_v22_phase2_2026-11-04.md method, verbatim:
    on a day with a v22 leg exited `stop`, first 5-min spot close back
    through the morning-range extreme (09:15-11:59 spot high/low) on
    the stopped leg's side, bar at/after 12:00 and at/after the stop's
    exit bar; entry = ATM (phase-2 atm) at next bar open, monthly
    expiry; G0 exits (stop -50 / target +90, stop before target, entry
    bar incl., fills at level, square-off at the 15:10 bar open);
    max 1/day; skipped if the day's realised v22 net (legs exited
    on/before the trigger bar) <= -Rs 3,000)
  + c4 runner extension (legs whose params are PLAIN — lock/tgt2 None —
    and which are NOT expiry-day legs: at +90 they do not exit; they
    run with lock +90 / target2 +180, phase 1 unchanged)
  + v1 add-ons (the NS3/S3 add-on candidates admit() band-dropped in
    the assembly — entry premium in [400,550) — re-admitted UNIQUE-ONCE
    vs the current book, NS3 @ P21, S3 @ stream-state segment params,
    scored under the then-current book state, i.e. WITH c4 active).

METHOD: the day's assembly is replicated line-for-line from
november_shadow_score.score_bank_v22 (same inputs, same assemble6
call, same Step A/B). SANITY ANCHOR: the replicated v22 rows (and the
raw v21 rows) must reproduce november_shadow_v22_bank_log.csv (and the
v21 log) exactly for every day before any stack layer is applied; any
mismatch aborts the run. Re-sims use november_shadow_score.
replay_overlay — the same function the anchor-verified v22 path uses
(the aggressive tune's replay_mod is its verbatim twin). The v1
stream for S3 params is the assembly's own stream (combined pool,
Jan-Oct + that day, exactly as assemble6 builds it), mirroring how
the November assembly itself params November S3 legs.

Paper only, real money Rs0. Basis: premiums per 1 lot (30),
Rs 220/trade. No frozen log/spec is modified; the shadow state file
is loaded read-only (mutations stay in memory, never saved).
"""
import copy, csv, json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import november_shadow_score as S
import november_shadow_fetch as F

DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
        "2026-11-06", "2026-11-09"]
LOT, COST = 30, 220.0
BANK_EXPIRY_NOV = "2026-11-23"


# ---------------- assembly replication (from S.score_bank_v22) ----
def assemble_day(day, st):
    """Returns dict with raw_rows (v21), kept (v22, post Step A/B),
    skipped (EVE-05), lbk, ctx, candidate inputs, assembly detail,
    stream; or {'nc_day': reason}."""
    ctx = S.day_context("BANKNIFTY", day)
    if not S.bars_complete(ctx["own"]):
        return {"nc_day": f"Bank Nifty spot 5m candles for {day} "
                          f"unavailable ({len(ctx['own'])} bars)"}
    import aggressive_score as A
    sd = TR / "november_shadow_data"
    if sd not in A.DIRS:
        A.DIRS.insert(0, sd)
    mrows = F.master_rows()
    for e in F.expiries_for(mrows, "BANKNIFTY"):
        if e >= "2026-11-01" and e not in A.EXPIRIES:
            A.EXPIRIES.append(e)
    A.EXPIRIES.sort()
    S.extend_ns_data(day)
    import bank_r5_core as c5
    import bank_r6_core as c6
    import bank_r3_setups as s3mod
    from bank_r7_core import P21, GDGU
    from bank_r6_core import assemble6
    from aggressive_score import candles, unique_once
    assert day in s3mod.DAYS, f"bank_r3_setups store lacks {day}"
    legs_prod, notes_prod = S.producer_legs("BANKNIFTY", ctx, day, st)
    S.note_state_after(st, "BANKNIFTY", day, legs_prod)
    comp = []
    for l in legs_prod:
        et = S.plus5(l["signal_time"])
        so = S.bar_open(ctx["own"], et)
        if so is None:
            continue
        comp.append(c5.mkleg(day, l["direction"], et, S.atm100(so),
                             c5.expiry_for(day), l["system"],
                             _signal=l["signal_time"]))
    pooled_nov = c5.pool_b2(comp, solo_rule="causal")
    ns1_nov = S.ns1_gen_loop({day})
    ns3_nov = S.ns3_legs_for(day)
    gen = s3mod.generate()
    s3_nov = [l for fam in ("S3A", "S3E", "S3D")
              for l in gen[fam] if l["date"] == day]
    fetch_rep = {}
    seen = set()
    for l in comp + pooled_nov + ns1_nov + ns3_nov + s3_nov:
        k = (int(l["strike"]), l["direction"], l["expiry"])
        if k in seen:
            continue
        seen.add(k)
        fetch_rep[k] = F.fetch_premium("BANKNIFTY", l["strike"],
                                       l["direction"], day, l["expiry"],
                                       rows=mrows)
    for k, v in fetch_rep.items():
        if "429" in str(v):
            raise SystemExit(f"HTTP 429 from Upstox on {k} — hard stop")
    pooled_f, ns1_f = c6.v20_inputs()
    orig_ns3 = c6.ns3_legs

    def patched_ns3(causal=False):
        legs = orig_ns3(causal=causal)
        for l in ns3_nov:
            l2 = dict(l)
            if causal:
                l2["entry_time"] = c5.t_plus5(l2["signal_time"])
            legs.append(l2)
        return legs
    c6.ns3_legs = patched_ns3
    try:
        rows, nc, lbk, detail, plan = assemble6(
            list(pooled_f) + pooled_nov, list(ns1_f) + ns1_nov, delay=0,
            ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
    finally:
        c6.ns3_legs = orig_ns3
    jo = [r for r in rows if r["date"] < "2026-11-01"]
    jo_total = round(sum(r["net"] for r in jo), 2)
    assert len(jo) == 99 and abs(jo_total - 83650.50) < 0.01, \
        f"Jan-Oct reproduction FAILED: {len(jo)} legs, {jo_total}"
    day_rows = [r for r in rows if r["date"] == day]
    raw_rows = copy.deepcopy(day_rows)
    # Step A — EVE-04 FC-2 lock on NS1_second legs (verbatim)
    for r in day_rows:
        if r["family"] == "NS1_second":
            leg = lbk[r["leg_key"]]
            cs = candles("BANKNIFTY", leg["strike"], leg["direction"],
                         day, leg["expiry"])
            res = S.replay_overlay(cs, leg["entry_time"], r["_params"],
                                   overlay="fc2")
            if res is not None:
                r.update({k: res[k] for k in
                          ("net", "exit_reason", "exit_time", "entry",
                           "exit")})
                r["_eve04"] = True
    # Step B — EVE-05 skip (verbatim)
    kept, skipped = [], []
    for r in day_rows:
        if r["rep"] == "Skill V3" and r["direction"] == "PE" \
                and r["entry_time"] < "10:30":
            skipped.append(r)
        else:
            kept.append(r)
    # the assembly's own stream (for v1 S3 params): rebuild by_key
    # exactly as assemble6 does from the same inputs
    from bank_engine_cycle import FILTERS
    pool = unique_once(list(pooled_f) + pooled_nov + list(ns1_f) + ns1_nov)
    pool = FILTERS["drop_ns1_ce"](pool)
    pool = FILTERS["drop_prem_400_550"](pool)
    by_key = {(l["date"], l["direction"], l["entry_time"]): l
              for l in pool}
    stream, states, taken, nc0 = c5.stream_states(by_key, delay=0)
    return {"ctx": ctx, "raw_rows": raw_rows, "kept": kept,
            "skipped": skipped, "lbk": lbk, "detail": detail,
            "ns3_nov": ns3_nov, "s3_nov": s3_nov, "stream": stream,
            "notes_prod": notes_prod, "fetch_rep": fetch_rep,
            "mrows": mrows}


# ---------------- anchor vs the written shadow logs ----------------
def log_trades(logf, day):
    out = []
    skip = 0
    for r in csv.DictReader(open(logf)):
        if r["date"] != day:
            continue
        if "EVE-05-SKIP" in r["system_source"]:
            skip += 1
            continue
        if r["net_inr"] == "" or r["net_inr"] is None:
            continue
        out.append((r["direction"], int(r["strike"]), r["entry_time"],
                    float(r["entry_premium"]), float(r["exit_premium"]),
                    r["exit_time"], r["exit_reason"],
                    float(r["net_inr"])))
    return sorted(out), skip


def row_tuples(rows, lbk):
    out = []
    for r in rows:
        leg = lbk[r["leg_key"]]
        out.append((r["direction"], int(leg["strike"]), r["entry_time"],
                    round(r["entry"], 2), round(r["exit"], 2),
                    r["exit_time"], r["exit_reason"], round(r["net"], 2)))
    return sorted(out)


# ---------------- EVE-06(a) re-entry (phase-2, verbatim logic) -----
def atm_phase2(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100


def sim_g0(pd, entry_time, entry_prem):
    stop_lvl, tgt_lvl = entry_prem - 50.0, entry_prem + 90.0
    for t in sorted(pd):
        if t < entry_time or t > "15:05":
            continue
        o, h, l, c = pd[t]
        if l <= stop_lvl:
            return t, stop_lvl, "stop"
        if h >= tgt_lvl:
            return t, tgt_lvl, "target"
    if "15:10" in pd:
        return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"


def find_reentry(day, kept, spot_bars):
    """Phase-2 find_reentry against the day's v22 (kept) rows.
    Returns (event_dict, leg_or_None); event describes trigger /
    cap-block / no-time / nc outcomes for the report."""
    stops = [r for r in kept if r["exit_reason"] == "stop"]
    if not stops:
        return None, None
    leg0 = sorted(stops, key=lambda r: r["exit_time"])[0]
    side = leg0["direction"]
    times = [b["time"] for b in spot_bars]
    spot = {b["time"]: b for b in spot_bars}
    mh = max(spot[t]["high"] for t in times if t <= "11:55")
    ml = min(spot[t]["low"] for t in times if t <= "11:55")
    start = max("12:00", leg0["exit_time"])
    trig = None
    for t in times:
        if t < start:
            continue
        c = spot[t]["close"]
        if (side == "CE" and c > mh) or (side == "PE" and c < ml):
            trig = t
            break
    if trig is None:
        return {"kind": "no_trigger", "side": side,
                "stop_exit": leg0["exit_time"]}, None
    realised = round(sum(r["net"] for r in kept
                         if r["exit_time"] <= trig), 2)
    if realised <= -3000.0:
        return {"kind": "cap_blocked", "trig": trig, "side": side,
                "realised": realised}, None
    i = times.index(trig)
    et = times[i + 1] if i + 1 < len(times) else None
    if et is None or et > "15:05":
        return {"kind": "no_time", "trig": trig, "side": side}, None
    strike = atm_phase2(spot[et]["open"])
    exp = BANK_EXPIRY_NOV
    rep = F.fetch_premium("BANKNIFTY", strike, side, day, exp,
                          rows=None)
    if "429" in str(rep):
        raise SystemExit(f"HTTP 429 from Upstox (re-entry {day}) — stop")
    import aggressive_score as A
    cs = A.candles("BANKNIFTY", strike, side, day, exp)
    if not cs:
        return {"kind": "nc", "trig": trig, "side": side, "et": et,
                "why": f"no_contract {exp}|{strike}|{side} "
                       f"(fetch: {rep})"}, None
    pd = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
          for b in cs}
    if et not in pd:
        return {"kind": "nc", "trig": trig, "side": side, "et": et,
                "why": f"no_entry_bar {exp}|{strike}|{side}@{et}"}, None
    entry_prem = pd[et][0]
    xt, xp, reason = sim_g0(pd, et, entry_prem)
    leg = {"date": day, "component": "EVE-06(a) re-entry",
           "family": "EVE06_REENTRY", "rep": "EVE06a",
           "direction": side, "strike": strike, "expiry": exp,
           "entry_time": et, "entry": entry_prem, "exit_time": xt,
           "exit": xp, "exit_reason": reason,
           "net": round((xp - entry_prem) * LOT - COST, 2),
           "trigger_time": trig}
    return {"kind": "leg", "trig": trig, "side": side}, leg


# ---------------- v1 add-ons (band-dropped re-admission) -----------
def v1_addons(day, asm, stack_keys):
    """Replicates bank_aggressive_tune v1_fns scoped to this day:
    candidates = the day's NS3 (causal form, GDGU) then S3A/E/D legs;
    admit() with taken seeded from the assembly's BASE/NS1 keys plus
    earlier families' admitted keys (the assembly's own sequence);
    the band-dropped legs get params (NS3: P21; S3: _params_for_addon
    over the assembly stream) and are then admitted UNIQUE-ONCE vs
    the current stack book keys and scored WITH c4 runner extension
    active (the v1-time book state). Returns (rows, events)."""
    import bank_r5_core as c5
    from bank_r7_core import P21, GDGU
    from bank_r3_core import admit
    from aggressive_score import candles
    lbk = asm["lbk"]
    taken = {(r["date"], r["direction"]) for r in asm["raw_rows"]
             if r["family"] in ("BASE", "NS1_second")}
    ns3_cand = []
    for l in asm["ns3_nov"]:
        l2 = dict(l)
        l2["entry_time"] = c5.t_plus5(l2["signal_time"])
        ns3_cand.append(c5.enrich(l2))
    ns3_cand = [l for l in ns3_cand if GDGU(l)]
    bd_legs = []  # (leg, params)
    adm, kd, bd, ncl = admit(ns3_cand, taken)
    taken |= {(l["date"], l["direction"]) for l in adm}
    for l in bd:
        bd_legs.append((l, dict(P21)))
    gen_by_fam = {"S3A": [], "S3E": [], "S3D": []}
    for l in asm["s3_nov"]:
        gen_by_fam.setdefault(l["family"], []).append(l)
    for fam in ("S3A", "S3E", "S3D"):
        cand = [c5.enrich(l) for l in gen_by_fam.get(fam, [])]
        adm, kd, bd, ncl = admit(cand, taken)
        taken |= {(l["date"], l["direction"]) for l in adm}
        for l in bd:
            p, seg = c5._params_for_addon(l, asm["stream"])
            if p is not None:
                bd_legs.append((l, p))
    rows, events = [], []
    seen = set()
    for leg, p in sorted(bd_legs,
                         key=lambda x: (x[0]["date"], x[0]["entry_time"])):
        key = (leg["date"], leg["direction"])
        if key in seen:
            continue
        seen.add(key)
        if key in stack_keys:
            events.append(f"v1 candidate {leg['rep']} {leg['direction']} "
                          f"{leg['entry_time']} key-dropped vs stack book")
            continue
        p_use = p
        if p["lock"] is None and leg["date"] != leg["expiry"]:
            p_use = {**p, "lock": 90.0, "tgt2": 180.0}  # c4 active
        cs = candles("BANKNIFTY", leg["strike"], leg["direction"], day,
                     leg["expiry"])
        res = S.replay_overlay(cs, leg["entry_time"], p_use) if cs \
            else None
        if res is None:
            events.append(f"NOT_COMPUTED — v1 candidate {leg['rep']} "
                          f"{leg['direction']} {leg['strike']} exp "
                          f"{leg['expiry']}: premium candles unavailable")
            rows.append({"date": day, "component": "v1 add-on",
                         "family": leg["family"], "rep": leg["rep"],
                         "direction": leg["direction"],
                         "strike": int(leg["strike"]),
                         "expiry": leg["expiry"],
                         "entry_time": leg["entry_time"], "entry": None,
                         "exit_time": "", "exit": None, "exit_reason": "",
                         "net": None,
                         "nc": "premium candles unavailable"})
            continue
        rows.append({"date": day, "component": "v1 add-on",
                     "family": leg["family"], "rep": leg["rep"],
                     "direction": leg["direction"],
                     "strike": int(leg["strike"]), "expiry": leg["expiry"],
                     "entry_time": leg["entry_time"],
                     "entry": res["entry"], "exit_time": res["exit_time"],
                     "exit": res["exit"], "exit_reason": res["exit_reason"],
                     "net": res["net"]})
        stack_keys.add(key)
    return rows, events


def main():
    st = S.load_state()
    S.prep_bank_spot_dir(max(DAYS))
    S._PREPPED_UPTO = max(DAYS)
    all_rows, day_summ, problems = [], [], []
    for day in DAYS:
        asm = assemble_day(day, st)
        if "nc_day" in asm:
            day_summ.append({"date": day, "nc_day": asm["nc_day"]})
            problems.append(f"{day}: NOT_COMPUTED day — {asm['nc_day']}")
            continue
        # ---- SANITY ANCHOR: v22 + v21 reproduction ----
        log22, skip22 = log_trades(TR / "november_shadow_v22_bank_log.csv",
                                   day)
        mine22 = row_tuples(asm["kept"], asm["lbk"])
        log21, _ = log_trades(TR / "november_shadow_v21_bank_log.csv",
                              day)
        mine21 = row_tuples(asm["raw_rows"], asm["lbk"])
        anchor_ok = (log22 == mine22 and skip22 == len(asm["skipped"])
                     and log21 == mine21)
        if not anchor_ok:
            print(json.dumps({"ABORT": "anchor mismatch", "date": day,
                              "log_v22": log22, "mine_v22": mine22,
                              "log_skip": skip22,
                              "my_skip": len(asm["skipped"]),
                              "log_v21": log21, "mine_v21": mine21},
                             indent=1))
            return 1
        lbk = asm["lbk"]
        kept = asm["kept"]
        stack = []
        c4_changed = 0
        # ---- layer 1: v22 rows, with c4 applied to PLAIN legs ----
        for r in kept:
            leg = lbk[r["leg_key"]]
            p = r["_params"]
            row = {"date": day, "component": "v22 (EVE-04/05)",
                   "family": r["family"], "rep": r["rep"],
                   "direction": r["direction"],
                   "strike": int(leg["strike"]), "expiry": leg["expiry"],
                   "entry_time": r["entry_time"], "entry": r["entry"],
                   "exit_time": r["exit_time"], "exit": r["exit"],
                   "exit_reason": r["exit_reason"], "net": r["net"]}
            if p["lock"] is None and day != leg["expiry"]:
                import aggressive_score as A
                cs = A.candles("BANKNIFTY", leg["strike"],
                               leg["direction"], day, leg["expiry"])
                p2 = {**p, "lock": 90.0, "tgt2": 180.0}
                ov = "fc2" if r["family"] == "NS1_second" else None
                res = S.replay_overlay(cs, r["entry_time"], p2,
                                       overlay=ov) if cs else None
                if res is not None:
                    if abs(res["net"] - r["net"]) > 0.005 or \
                            res["exit_reason"] != r["exit_reason"]:
                        c4_changed += 1
                    row.update({"component": "v22 + c4 runner extension",
                                "entry": res["entry"],
                                "exit_time": res["exit_time"],
                                "exit": res["exit"],
                                "exit_reason": res["exit_reason"],
                                "net": res["net"]})
                else:
                    problems.append(
                        f"{day}: c4 re-sim NC for {r['family']} "
                        f"{r['direction']} {leg['strike']} — v22 values "
                        f"kept")
            stack.append(row)
        stack_keys = {(day, r["direction"]) for r in stack}
        # ---- layer 2: EVE-06(a) re-entry (vs pre-c4 v22 book) ----
        ev, rleg = find_reentry(day, kept, asm["ctx"]["own"])
        reentry_note = None
        if rleg is not None:
            stack.append(rleg)
            stack_keys.add((day, rleg["direction"]))
        elif ev is not None:
            reentry_note = (f"re-entry: {ev['kind']}"
                            + (f" trig {ev['trig']}" if "trig" in ev
                               else "")
                            + (f" realised {ev['realised']}"
                               if "realised" in ev else "")
                            + (f" — {ev['why']}" if "why" in ev else ""))
            if ev["kind"] == "nc":
                problems.append(f"{day}: re-entry NOT_COMPUTED — "
                                f"{ev['why']}")
        # ---- layer 3: v1 add-ons ----
        v1_rows, v1_events = v1_addons(day, asm, stack_keys)
        stack.extend(v1_rows)
        for e in v1_events:
            if e.startswith("NOT_COMPUTED"):
                problems.append(f"{day}: {e}")
        day_net = round(sum(r["net"] for r in stack
                            if r["net"] is not None), 2)
        day_summ.append({
            "date": day, "anchor": "v22+v21 reproduced exactly",
            "legs": len([r for r in stack if r["net"] is not None]),
            "net": day_net, "c4_changed": c4_changed,
            "reentry": reentry_note or
                       (f"leg {rleg['direction']} {rleg['strike']} "
                        f"trig {rleg['trigger_time']} net {rleg['net']}"
                        if rleg else "no stopped v22 leg"),
            "v1_events": v1_events,
            "band_dropped_pool": asm["detail"]})
        all_rows.extend(stack)
        print(json.dumps(day_summ[-1], indent=1), flush=True)
    total = round(sum(r["net"] for r in all_rows
                      if r["net"] is not None), 2)
    out_csv = TR / "bank_tuned_stack_november_backfill_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "component", "family", "rep", "direction",
                    "strike", "expiry", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "net_inr",
                    "notes"])
        for r in sorted(all_rows,
                        key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["component"], r["family"], r["rep"],
                        r["direction"], r["strike"], r["expiry"],
                        r["entry_time"],
                        "" if r["entry"] is None else f"{r['entry']:.2f}",
                        r["exit_time"],
                        "" if r["exit"] is None else f"{r['exit']:.2f}",
                        r["exit_reason"],
                        "" if r["net"] is None else f"{r['net']:.2f}",
                        ("NOT_COMPUTED — " + r["nc"]) if r.get("nc") else
                        "RETROSPECTIVE BACKFILL — Bank tuned stack "
                        "(v22 + EVE-06(a) + c4 + v1), candle-scored "
                        "2026-11-10 · paper only, real money ₹0, 1 lot"])
    print(json.dumps({"TOTAL": total, "days": day_summ,
                      "problems": problems}, indent=1))
    (TR / "bank_tuned_stack_november_backfill_result.json").write_text(
        json.dumps({"total": total, "days": day_summ,
                    "problems": problems,
                    "rows": [{k: v for k, v in r.items()}
                             for r in all_rows]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
