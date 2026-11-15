#!/usr/bin/env python3
"""BANK-EVE-18 November counterfactual (standalone helper for
bank_positive_tuning_2026-11-10.py — runs in a fresh process because the
main script restricts bank_r3_setups to Jan-Oct in its own process).
Re-sims the two November TUNED STACK days (2026-11-04, 2026-11-09) with
the day's own assembly machinery (bank_tuned_stack_november_backfill),
asserts the incumbent replay equals the backfill rows, then applies
BANK-EVE-18's ride rule. Prints ONE JSON line on stdout.
Paper only, real money Rs 0. Nothing is written or modified."""
import json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"

def replay_ride(cs, entry_time, p, arm30=False):
    """Copied from bank_positive_tuning_2026-11-10.py (replay_mod with
    the tgt2 exit removed in the runner phase; floor = entry+lock)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0]
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if cs[start][0] > SQ: return None
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
            touched = False; rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > SQ: break
                if l2 <= stop2:
                    rest = (stop2, "runner_ride_stop" if touched else "runner_stop", t2); break
                if tgt2 is not None and h2 >= tgt2: touched = True
                if t2 == SQ:
                    rest = (cl2, "runner_ride_square_off" if touched else "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]
                rest = (lb[4], "runner_ride_square_off" if touched else "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2])
        if arm30 and h >= entry + 30.0:
            arm_level = 0.0 if arm_level is None else max(arm_level, 0.0)
        if t == SQ:
            return mk(cl, "square_off", t)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0])

def main():
    import november_shadow_score as S
    import bank_tuned_stack_november_backfill as B
    import aggressive_score as AGG
    st = S.load_state()
    S.prep_bank_spot_dir("2026-11-09")
    S._PREPPED_UPTO = "2026-11-09"
    legs = []
    for day in ("2026-11-04", "2026-11-09"):
        asm = B.assemble_day(day, st)
        if "nc_day" in asm:
            print(json.dumps({"total": None, "note": f"NOT_COMPUTED — {day}: {asm['nc_day']}"}))
            return 0
        for r in asm["kept"]:
            leg = asm["lbk"][r["leg_key"]]
            cs = AGG.candles("BANKNIFTY", leg["strike"], leg["direction"], day, leg["expiry"])
            inc = S.replay_overlay(cs, leg["entry_time"], r["_params"],
                                   overlay="fc2" if r["family"] == "NS1_second" else None)
            assert inc is not None and abs(inc["net"] - r["net"]) < 0.005, (day, r["leg_key"])
            # c4 state of the November stack row (backfill applies c4 to
            # PLAIN non-expiry legs before the counterfactual comparison)
            p = r["_params"]
            if p["lock"] is None and day != leg["expiry"]:
                p = {**p, "lock": 90.0, "tgt2": 180.0}
                inc2 = S.replay_overlay(cs, leg["entry_time"], p,
                                        overlay="fc2" if r["family"] == "NS1_second" else None)
                if inc2 is not None and abs(inc2["net"] - r["net"]) < 0.005:
                    pass  # row already carries c4 in its stored net only if it changed; params govern the ride either way
            ride = replay_ride(cs, leg["entry_time"], p,
                               arm30=r["family"] == "NS1_second")
            legs.append(dict(date=day, family=r["family"], direction=r["direction"],
                             strike=int(leg["strike"]), entry_time=r["entry_time"],
                             params=dict(stop=p["stop"], trig=p["trig"],
                                         lock=p["lock"], tgt2=p["tgt2"]),
                             incumbent_reason=r["exit_reason"], incumbent_net=r["net"],
                             ride_reason=ride["exit_reason"] if ride else None,
                             ride_net=ride["net"] if ride else None))
    total = round(sum(l["ride_net"] for l in legs), 2) if all(l["ride_net"] is not None for l in legs) else None
    print(json.dumps({"total": total, "legs": legs,
                      "note": "November stack legs re-simmed under the ride rule with the "
                              "day's own assembly params (c4 extension applied to PLAIN "
                              "non-expiry legs, mirroring the backfill); incumbent replays "
                              "asserted equal to the written backfill rows first."}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
