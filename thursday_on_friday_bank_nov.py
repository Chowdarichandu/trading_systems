#!/usr/bin/env python3
"""NOVEMBER COUNTERFACTUAL HELPER for tuning_bank_2026-11-12.py
(standalone — runs in a fresh process because the main script restricts
bank_r3_setups to Jan-Oct in its own process). For each November day
2026-11-02/03/04/05/06/09/11/12 it assembles the TUNED STACK v2 book
with the day's own machinery (bank_tuned_stack_november_backfill.
assemble_day + the live scorer's EVE-19 layer), asserts the IDENTITY
variant reproduces november_shadow_stack_bank_log.csv leg-for-leg
(day totals and the -960.00 window total), then re-sims every leg
under each tuning variant (T-B1a/T-B1b/T-B2a/T-B2b/T-B2c param
transforms via replay_mod; T-B3 via the locked owner ladder) and
re-derives the EVE-06(a) re-entry from each variant's own exits
(find_reentry + variant re-sim of any derived leg).
Prints ONE line: RESULT_JSON:{...}. Paper only, real money Rs 0.
Nothing is written or modified."""
import csv, json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"
G0 = {"stop": 50.0, "trig": 90.0, "lock": None, "tgt2": None}
DAYS8 = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
         "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
         "2026-11-13"]
VARIANTS = ["T-B1a", "T-B1b", "T-B2a", "T-B2b", "T-B2c", "T-B3"]

def replay_mod(cs, entry_time, p, delay=0, arm30=False):
    """Verbatim copy of bank_aggressive_tune_score.replay_mod
    (delay/arm50 variants unused here)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if start >= len(cs) or cs[start][0] > SQ: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    def mk(px, reason, t):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, entry=entry, exit=px)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0])
    arm_level = None
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > SQ: break
        eff_stop = entry + arm_level if arm_level is not None else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if arm_level is not None else "stop", t)
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > SQ: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == SQ: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2])
        if arm30 and h >= entry + 30.0:
            arm_level = 0.0 if arm_level is None else max(arm_level, 0.0)
        if t == SQ:
            return mk(cl, "square_off", t)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0])

def sim_variant(pd, entry_time, entry_prem, p):
    """Same dict-bar sim as the main script (== sim_g0 under G0)."""
    stop_lvl = entry_prem - p["stop"]; trig_lvl = entry_prem + p["trig"]
    times = sorted(t for t in pd if entry_time <= t <= "15:05")
    for i, t in enumerate(times):
        o, h, l, c = pd[t]
        if l <= stop_lvl: return t, stop_lvl, "stop"
        if h >= trig_lvl:
            if p["lock"] is None and p["tgt2"] is None:
                return t, trig_lvl, "target"
            stop2 = entry_prem + p["lock"] if p["lock"] is not None else stop_lvl
            tgt2 = entry_prem + p["tgt2"] if p["tgt2"] is not None else None
            for t2 in times[i + 1:]:
                o2, h2, l2, c2 = pd[t2]
                if l2 <= stop2: return t2, stop2, "runner_stop"
                if tgt2 is not None and h2 >= tgt2: return t2, tgt2, "runner_target"
            if "15:10" in pd: return "15:10", pd["15:10"][0], "runner_square_off"
            last = times[-1]; return last, pd[last][3], "runner_square_off"
    if "15:10" in pd: return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def transform(p_base, p_fin, direction, variant):
    """Identical to the main script's pre-registered transforms."""
    if variant == "identity":
        return dict(p_fin)
    if variant == "T-B1a":
        if p_base["trig"] == 90:
            return {"stop": p_fin["stop"], "trig": 90.0, "lock": 30.0, "tgt2": None}
        return dict(p_fin)
    if variant == "T-B1b":
        if p_base["trig"] == 90:
            return {"stop": p_fin["stop"], "trig": 58.0, "lock": 10.0, "tgt2": None}
        return dict(p_fin)
    if variant == "T-B2a":
        return {**p_fin, "stop": 40.0} if direction == "PE" else dict(p_fin)
    if variant == "T-B2b":
        return {**p_fin, "stop": 60.0} if direction == "PE" else dict(p_fin)
    if variant == "T-B2c":
        if direction == "PE" and p_base["lock"] is None and p_base["tgt2"] is None:
            return {"stop": p_fin["stop"], "trig": 50.0, "lock": 0.0, "tgt2": 90.0}
        return dict(p_fin)
    raise ValueError(variant)

L_STAGES = (30, 58, 82, 100); L_LOCKS = (5, 15, 25); L_STOP = 20.0; L_SQ = "15:10"

def ladder_sim(bars, spotday, direction, entry_time):
    """Locked owner ladder (same semantics as the main script)."""
    et = entry_time
    if et not in bars or et not in spotday or L_SQ not in bars:
        return None
    entry = bars[et][0]
    entry_spot = spotday[et][0]
    sign = 1 if direction == "CE" else -1
    floor0 = entry - L_STOP
    times = sorted(t for t in bars if et <= t <= L_SQ)
    if not times:
        return None
    highest = 0
    for t in times:
        if t not in spotday:
            return None
        pclose = bars[t][3]
        fav = sign * (spotday[t][3] - entry_spot)
        stage_now = sum(1 for s in L_STAGES if fav >= s)
        if stage_now > highest:
            highest = stage_now
        if highest == 4:
            return t, pclose, "T4_EXIT", 4
        floor = floor0 if highest == 0 else entry + L_LOCKS[highest - 1]
        if pclose <= floor:
            return t, pclose, ("HARD_STOP" if highest == 0 else f"LOCK_FLOOR_T{highest}"), highest
    return L_SQ, bars[L_SQ][3], "SQUARE_OFF", highest

def main():
    import november_shadow_score as S
    import bank_tuned_stack_november_backfill as B
    import aggressive_score as AGG
    st = S.load_state()
    S.prep_bank_spot_dir("2026-11-13")
    S._PREPPED_UPTO = "2026-11-13"
    log = {}
    for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv")):
        if r["net_inr"] not in ("", None):
            log.setdefault(r["date"], []).append(
                (r["direction"], int(r["strike"]), r["entry_time"],
                 float(r["entry_premium"]), r["exit_time"],
                 float(r["exit_premium"]), r["exit_reason"], float(r["net_inr"])))
    out = {"identity": {"days": {}}, "variants": {v: {"days": {}, "flags": []}
                                                  for v in VARIANTS},
           "eve19_skips": [], "v1_addon_rows": [], "reentry_events": {}}
    id_total = 0.0
    var_totals = {v: 0.0 for v in VARIANTS}
    for day in DAYS8:
        asm = B.assemble_day(day, st)
        if "nc_day" in asm:
            raise SystemExit(f"NOT_COMPUTED day {day}: {asm['nc_day']}")
        lbk = asm["lbk"]
        kept2 = []
        for r in asm["kept"]:
            if r["family"] == "NS1_second" and r["entry_time"] < "10:30":
                out["eve19_skips"].append((day, r["direction"], r["entry_time"]))
                continue
            kept2.append(r)
        spotmap = {b["time"]: (b["open"], b["high"], b["low"], b["close"])
                   for b in asm["ctx"]["own"]}
        day_books = {}
        for v in ["identity"] + VARIANTS:
            rows = []
            for r in kept2:
                leg = lbk[r["leg_key"]]
                cs = AGG.candles("BANKNIFTY", leg["strike"], leg["direction"],
                                 day, leg["expiry"])
                assert cs, (day, r["leg_key"])
                p_base = r["_params"]
                p_fin = ({**p_base, "lock": 90.0, "tgt2": 180.0}
                         if p_base["lock"] is None and day != leg["expiry"]
                         else dict(p_base))
                if v == "T-B3":
                    bars = {b[0]: (b[1], b[2], b[3], b[4]) for b in cs}
                    assert abs(bars[r["entry_time"]][0] - r["entry"]) < 0.005, \
                        (day, r["leg_key"], "ladder entry reconstruction")
                    s = ladder_sim(bars, spotmap, r["direction"], r["entry_time"])
                    assert s is not None, (day, r["leg_key"], "ladder NC")
                    xt, xp, reason, stage = s
                    rows.append(dict(family=r["family"], rep=r["rep"],
                                     direction=r["direction"],
                                     strike=int(leg["strike"]),
                                     entry_time=r["entry_time"], entry=r["entry"],
                                     exit_time=xt, exit=xp, exit_reason=reason,
                                     net=round((xp - r["entry"]) * LOT - COST, 2)))
                else:
                    p_v = transform(p_base, p_fin, r["direction"], v)
                    s = replay_mod(cs, r["entry_time"], p_v,
                                   arm30=r["family"] == "NS1_second")
                    assert s is not None, (day, r["leg_key"])
                    rows.append(dict(family=r["family"], rep=r["rep"],
                                     direction=r["direction"],
                                     strike=int(leg["strike"]),
                                     entry_time=r["entry_time"], entry=s["entry"],
                                     exit_time=s["exit_time"], exit=s["exit"],
                                     exit_reason=s["exit_reason"], net=s["net"]))
            # EVE-06(a) re-entry re-derived from THIS variant's exits
            kept_map = [dict(exit_reason=("stop" if x["exit_reason"] == "HARD_STOP"
                                          else x["exit_reason"]),
                             exit_time=x["exit_time"], net=x["net"],
                             direction=x["direction"]) for x in rows]
            ev, rleg = B.find_reentry(day, kept_map, asm["ctx"]["own"])
            ev_key = f"{day}|{v}"
            if ev is not None:
                out["reentry_events"][ev_key] = ev
            if rleg is not None:
                cs = AGG.candles("BANKNIFTY", rleg["strike"], rleg["direction"],
                                 day, rleg["expiry"])
                pd = {b[0]: (b[1], b[2], b[3], b[4]) for b in cs}
                assert abs(pd[rleg["entry_time"]][0] - rleg["entry"]) < 0.005
                if v == "T-B3":
                    s = ladder_sim(pd, spotmap, rleg["direction"], rleg["entry_time"])
                    assert s is not None, (day, "reentry ladder NC")
                    xt, xp, reason, stage = s
                    net = round((xp - rleg["entry"]) * LOT - COST, 2)
                else:
                    p_v = transform(G0, G0, rleg["direction"], v)
                    xt, xp, reason = sim_variant(pd, rleg["entry_time"],
                                                 rleg["entry"], p_v)
                    net = round((xp - rleg["entry"]) * LOT - COST, 2)
                rows.append(dict(family="EVE06_REENTRY", rep="EVE06a",
                                 direction=rleg["direction"],
                                 strike=int(rleg["strike"]),
                                 entry_time=rleg["entry_time"],
                                 entry=rleg["entry"], exit_time=xt, exit=xp,
                                 exit_reason=reason, net=net))
            # v1 add-ons (incumbent geometry inside v1_addons; admission
            # vs this variant's stack keys)
            stack_keys = {(day, x["direction"]) for x in rows}
            v1_rows, v1_events = B.v1_addons(day, asm, set(stack_keys))
            for x in v1_rows:
                out["v1_addon_rows"].append((day, v, x["rep"], x["direction"],
                                             x["entry_time"], x["net"]))
                rows.append(dict(family=x["family"], rep=x["rep"],
                                 direction=x["direction"],
                                 strike=int(x["strike"]),
                                 entry_time=x["entry_time"], entry=x["entry"],
                                 exit_time=x["exit_time"], exit=x["exit"],
                                 exit_reason=x["exit_reason"], net=x["net"]))
                if v != "identity":
                    out["variants"][v]["flags"].append(
                        f"{day}: v1 add-on {x['rep']} carried at incumbent net "
                        f"(v1_addons scores incumbent geometry internally)")
            day_books[v] = rows
        # identity assertion vs the scored stack ledger
        mine = sorted((x["direction"], x["strike"], x["entry_time"], x["entry"],
                       x["exit_time"], x["exit"], x["exit_reason"], x["net"])
                      for x in day_books["identity"])
        theirs = sorted(log.get(day, []))
        assert len(mine) == len(theirs), (day, mine, theirs)
        for a, b in zip(mine, theirs):
            assert a[:3] == b[:3] and abs(a[3] - b[3]) < 0.005 and a[4] == b[4] \
                and abs(a[5] - b[5]) < 0.005 and a[6] == b[6] \
                and abs(a[7] - b[7]) < 0.005, (day, a, b)
        d_id = round(sum(x["net"] for x in day_books["identity"]), 2)
        id_total = round(id_total + d_id, 2)
        out["identity"]["days"][day] = dict(net=d_id, rows=day_books["identity"])
        for v in VARIANTS:
            d_v = round(sum(x["net"] for x in day_books[v]), 2)
            var_totals[v] = round(var_totals[v] + d_v, 2)
            out["variants"][v]["days"][day] = dict(net=d_v, rows=day_books[v])
    assert abs(id_total - (-2680.00)) < 0.005, id_total
    out["identity"]["total"] = id_total
    for v in VARIANTS:
        out["variants"][v]["total"] = var_totals[v]
    print("RESULT_JSON:" + json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
