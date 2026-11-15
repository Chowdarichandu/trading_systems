#!/usr/bin/env python3
"""NOVEMBER COUNTERFACTUAL HELPER for tuning_bank_fast_2026-11-12.py
— the OWNER'S ACCEPTANCE TEST (directive 2026-11-12 20:57 IST).
Standalone process. Takes the frozen November records and re-exits
every leg in the owner's window under the fast-exit variants FE-1/2/3
on real November premium candles; FE-4 = the recorded log nets.

  Stream A (TUNED STACK v2): legs recorded in
    november_shadow_stack_bank_log.csv (the scored stack ledger; the
    tuning_bank nov helper asserted the live assembly reproduces it
    leg-for-leg). Window identity must equal +Rs 760.00 and the full
    Nov 2-12 identity -Rs 960.00 (asserted).
  Stream B (NS1 standalone): the NS1 rows of the legacy primary in
    november_paper_bank_log.csv (channel=PRIMARY, system_source=NS1).
    Window identity -Rs 3,440.00; full Nov 2-12 identity +Rs 1,520.00
    (asserted — the corrected November composition).

Owner's window: Nov 2-10 -> trading days 2026-11-02/03/04/05/06/09
(Nov 10 = Diwali holiday, market closed). Nov 11/12 legs are computed
too and reported separately as FULL-period context — they are NOT
part of the owner's test. Paper only, real money Rs 0. Nothing is
written or modified; prints one RESULT_JSON line.
"""
import csv, json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST = 30, 220.0
WINDOW = {"2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
          "2026-11-06", "2026-11-09"}

FE_PARAMS = {"FE-1": dict(stop=50.0, tgt=50.0, tstop=2, arm=None),
             "FE-2": dict(stop=40.0, tgt=30.0, tstop=2, arm=None),
             "FE-3": dict(stop=50.0, tgt=90.0, tstop=3, arm=30.0)}

def sim_fast(cs, entry_time, variant, delay=0):
    """Identical to the main script's frozen fast-exit simulator."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs) or cs[i0][0] > "15:10": return None
    entry = cs[i0][1]
    prm = FE_PARAMS[variant]
    stop_lvl, tgt_lvl = entry - prm["stop"], entry + prm["tgt"]
    armed = False
    last = None
    for k in range(0, prm["tstop"] + 1):
        i = i0 + k
        if i >= len(cs): break
        t, o, h, l, cl, v = cs[i]
        if t > "15:10": break
        last = (i, cs[i])
        eff_stop = entry if armed else stop_lvl
        if l <= eff_stop:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=eff_stop,
                        exit_reason="be_stop" if armed else "stop", bars_held=i - i0)
        if h >= tgt_lvl:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=tgt_lvl,
                        exit_reason="target", bars_held=i - i0)
        if prm["arm"] is not None and h >= entry + prm["arm"]:
            armed = True
        if k == prm["tstop"]:
            return dict(entry_time=cs[i0][0], entry=entry, exit_time=t, exit=cl,
                        exit_reason="time_stop", bars_held=i - i0)
    if last is None: return None
    i, b = last
    return dict(entry_time=cs[i0][0], entry=entry, exit_time=b[0], exit=b[4],
                exit_reason="time_stop_eod", bars_held=i - i0)

def main():
    import aggressive_score as AGG
    # November premium candles live in november_shadow_data/ — the
    # November scorers insert it at the front of AGG.DIRS (verbatim
    # convention from november_shadow_score.py).
    _sd = TR / "november_shadow_data"
    if _sd not in AGG.DIRS:
        AGG.DIRS.insert(0, _sd)

    def load_legs(stream):
        legs = []
        if stream == "A_stack":
            for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv")):
                if r["net_inr"] in ("", None): continue
                legs.append(dict(date=r["date"], family=r["family"], rep=r["rep"],
                                 direction=r["direction"], strike=int(r["strike"]),
                                 expiry=r["expiry"], entry_time=r["entry_time"],
                                 entry_premium=float(r["entry_premium"]),
                                 exit_time=r["exit_time"],
                                 exit_premium=float(r["exit_premium"]),
                                 exit_reason=r["exit_reason"],
                                 net=float(r["net_inr"])))
        else:
            for r in csv.DictReader(open(TR / "november_paper_bank_log.csv")):
                if r["channel"] != "PRIMARY" or r["system_source"] != "NS1": continue
                legs.append(dict(date=r["date"], family="NS1_second", rep="NS1",
                                 direction=r["direction"], strike=int(r["strike"]),
                                 expiry=r["expiry"], entry_time=r["entry_time"],
                                 entry_premium=float(r["entry_premium"]),
                                 exit_time=r["exit_time"],
                                 exit_premium=float(r["exit_premium"]),
                                 exit_reason=r["exit_reason"],
                                 net=float(r["net_inr"])))
        for lg in legs:
            cs = AGG.candles("BANKNIFTY", lg["strike"], lg["direction"],
                             lg["date"], lg["expiry"])
            assert cs, (stream, lg)
            times = [b[0] for b in cs]
            ei = next(i for i, t in enumerate(times) if t >= lg["entry_time"])
            assert abs(cs[ei][1] - lg["entry_premium"]) < 0.005, (stream, lg, cs[ei])
            xi = max(i for i, t in enumerate(times) if t <= lg["exit_time"])
            lg["cs"] = cs
            lg["fe4_bars_held"] = xi - ei
        return legs

    out = {}
    for stream in ("A_stack", "B_ns1"):
        legs = load_legs(stream)
        out[stream] = {}
        for v in ("FE-4", "FE-1", "FE-2", "FE-3"):
            rows = []
            for lg in legs:
                if v == "FE-4":
                    rows.append(dict(date=lg["date"], family=lg["family"], rep=lg["rep"],
                                     direction=lg["direction"], strike=lg["strike"],
                                     entry_time=lg["entry_time"],
                                     entry_premium=lg["entry_premium"],
                                     exit_time=lg["exit_time"],
                                     exit_premium=lg["exit_premium"],
                                     exit_reason=lg["exit_reason"],
                                     bars_held=lg["fe4_bars_held"], net=lg["net"]))
                else:
                    s = sim_fast(lg["cs"], lg["entry_time"], v)
                    assert s is not None, (stream, v, lg["date"])
                    rows.append(dict(date=lg["date"], family=lg["family"], rep=lg["rep"],
                                     direction=lg["direction"], strike=lg["strike"],
                                     entry_time=s["entry_time"], entry_premium=s["entry"],
                                     exit_time=s["exit_time"], exit_premium=s["exit"],
                                     exit_reason=s["exit_reason"],
                                     bars_held=s["bars_held"],
                                     net=round((s["exit"] - s["entry"]) * LOT - COST, 2)))
            win = [r for r in rows if r["date"] in WINDOW]
            out[stream][v] = dict(
                window_legs=len(win), window_net=round(sum(r["net"] for r in win), 2),
                window_rows=win,
                full_legs=len(rows), full_net=round(sum(r["net"] for r in rows), 2),
                full_rows=rows)
    # identity assertions vs the frozen November records
    assert out["A_stack"]["FE-4"]["window_net"] == 760.00, out["A_stack"]["FE-4"]["window_net"]
    assert out["A_stack"]["FE-4"]["full_net"] == -960.00, out["A_stack"]["FE-4"]["full_net"]
    assert out["B_ns1"]["FE-4"]["window_net"] == -3440.00, out["B_ns1"]["FE-4"]["window_net"]
    assert out["B_ns1"]["FE-4"]["full_net"] == 1520.00, out["B_ns1"]["FE-4"]["full_net"]
    print("RESULT_JSON:" + json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
