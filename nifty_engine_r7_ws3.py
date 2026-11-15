#!/usr/bin/env python3
"""ROUND 7 WS3 — (lA) CE mirror (freeze: nifty_engine_frozen.md ROUND 7).
The (lA) v2 (L1) law mirrored to the CE side, confirmer unchanged (Bank):
break-UP = first Bank bar 09:30-11:30 close > Bank OR high; cutoff rule
identical (13:30 iff break < 11:30 strict, else 11:30); Nifty rescan =
first bar >= break, <= cutoff, close > own OR high AND close > PDH, OR
width <= 360*scale, room to next level above >= 200*scale; entry at the
next bar. Machinery validation: the unmodified PE construction
(o1_la_l1.rescan_nifty_l1) is re-run here and must reproduce the recorded
Jan-Sep (lA) signal times 42/42 before the mirror output is used.
Paper only, real Rs0."""
import sys, csv, math, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from o1_la_l1 import rescan_nifty_l1

def bank_break_up(day_bn):
    """Mirror of bn_break_time(mode='orl') flipped: first BN bar 09:30-11:30
    with close > BN OR high. Returns (time, orl, orh) or (None, orl, orh)."""
    day_spot, pdh, pdc, pdlv = day_bn
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    cand = day_spot[(day_spot["time"] >= "09:30") & (day_spot["time"] <= "11:30")]
    for _, c in cand.iterrows():
        if float(c["close"]) > orh:
            return c["time"], orl, orh
    return None, orl, orh

def rescan_nifty_ce_mirror(dd, day_bn):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    bt, _, _ = bank_break_up(day_bn)
    if bt is None: return None
    cutoff = "13:30" if bt < "11:30" else "11:30"
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    times = list(cand["time"])
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > cutoff or t < bt: continue
        cl = float(c["close"])
        if cl > orh and cl > pdh:
            nxt = [l for l in levels if l > cl]
            room = (min(nxt) - cl) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                if i + 1 >= len(cand): return None
                return {"signal": t, "entry_time": times[i + 1], "bn_break": bt, "orh": orh}
    return None

def main():
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    days = [d.date().isoformat() for d in daily_n["date"] if d.year == 2026 and d.month <= 10]
    # --- machinery validation: PE original vs recorded o1 (lA) signals, Jan-Sep
    o1 = {}
    for row in csv.DictReader(open("/home/hatch/workspace/trading/index_options_o1_janoct_trades.csv")):
        if row["track"] == "(lA) v2" and row["index"] == "NIFTY" and row["date"] < "2026-10-01":
            o1[row["date"]] = row["signal_time"]
    got_pe = {}
    mirror = []
    for ds in days:
        dd = day_data_nifty(spot_n, daily_n, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        if not dd or not dbn: continue
        if ds < "2026-10-01":
            r = rescan_nifty_l1(dd, dbn, True)
            if r and r["trade"]: got_pe[ds] = r["info"]["signal"]
        m = rescan_nifty_ce_mirror(dd, dbn)
        if m: mirror.append({"date": ds, **m})
    match = sum(1 for d in o1 if got_pe.get(d) == o1[d])
    print(f"PE validation: reproduced {len(got_pe)}, recorded {len(o1)}, exact matches {match}")
    assert len(got_pe) == len(o1) == match == 42, "MACHINERY VALIDATION FAILED"
    print(f"CE mirror signals Jan-Oct: {len(mirror)}")
    for m in mirror: print(" ", m)
    json.dump(mirror, open("/tmp/r7_ws3_mirror_signals.json", "w"), indent=1)

if __name__ == "__main__":
    main()
