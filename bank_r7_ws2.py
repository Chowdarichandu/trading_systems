#!/usr/bin/env python3
"""ROUND 7 WS2 — (lA) CE MIRROR, BANK (Cycle 155).

CONSTRUCTION (exact mirror image of the frozen (lA) v2 L1 Bank engine,
o1_la_l1.rescan_bank_l1; every inequality, window and threshold flipped
in direction and nothing else):
- Confirmer (Nifty): first Nifty bar 09:30-11:30 with close > Nifty OR
  HIGH (PE engine: close < OR low). L1 cutoff: 13:30 where the confirmer
  broke before 11:30 (strict <), else 11:30.
- Bank rescan: first bar >= confirmer break and <= cutoff with
  close > own OR HIGH AND close > own PDH (PE: < OR low AND < PDL);
  OR width <= 360*scale; room = distance to the next PD level ABOVE the
  close (PE: below) >= 200*scale.
- Morning trade: entry = next bar's open; stop = signal bar LOW
  (PE: high); risk = entry - stop; target = entry + 2*risk (PE: -2*risk);
  replay with stop checked before target, square-off 15:10 (replay_ce,
  the line-by-line mirror of close_reentry_sweep.replay_pe).
- Sleeve leg: one options leg per firing day at the morning entry
  (bar after the rescan signal), strike ATM at the entry bar's spot
  open, expiry in force — exactly how the PE (lA) legs enter the book.
  A day contributes a leg iff the mirrored morning replay produces a
  trade with a net (the same existence rule o1_la_l1.run applies:
  morning present and day_net not None; the re-entry scan affects the
  spot day net's value, never the morning leg's existence).
Admission/exits: the pipeline's add-on machinery (sequential
UNIQUE-ONCE vs the book, premium-band drop, stream-state segment
geometry, PLAIN on expiry day) — the same treatment as the Round-6
gap/expiry sleeves.
CAUSALITY CERTIFICATE: every input (confirmer break bar, own OR, PDH,
room levels) is printed at or before the rescan signal bar; the leg
enters at the NEXT bar's open. No end-of-day set membership is used.
Nifty's Round-7 verdict on its own mirror is NOT imported — Bank's
population is scored on Bank data alone."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r7_core as c7
from bank_r7_core import judge7, v21_ref
from bank_r6_core import v20_inputs
from merged_skill_la_october import load_bank, day_data_bank
from timing_sweep import load as load_nifty, day_data as day_data_nifty

QTY, COST = 100, 40.0

def nifty_break_time_up(day_nifty):
    """Mirror of merged_skill_la_october.nifty_break_time: first Nifty bar
    09:30-11:30 close > Nifty OR high. Returns (time, orl, orh)."""
    day_spot, pdh, pdc, pdl = day_nifty
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    cand = day_spot[(day_spot["time"] >= "09:30") & (day_spot["time"] <= "11:30")]
    for _, c in cand.iterrows():
        if float(c["close"]) > orh:
            return c["time"], orl, orh
    return None, orl, orh

def replay_ce(candles, start_idx, entry, stop, target):
    """Line-by-line mirror of close_reentry_sweep.replay_pe."""
    risk = entry - stop
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk",
                "exit_time": None, "exit_idx": None, "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        if lo <= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if hi >= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if c["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": c["time"], "exit_idx": j, "exit_price": cl,
                    "net": round((cl - entry) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1,
            "exit_price": float(c["close"]),
            "net": round((float(c["close"]) - entry) * QTY - COST, 2),
            "risk": round(risk, 2)}

def rescan_bank_l1_up(dd_bank, day_nifty):
    """Mirror of o1_la_l1.rescan_bank_l1 (strict cutoff reading)."""
    day_spot, pdh, pdc, pdl, bias, scale = dd_bank
    bt, nf_orl, nf_orh = nifty_break_time_up(day_nifty)
    if bt is None:
        return None
    cutoff = "13:30" if bt < "11:30" else "11:30"
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > cutoff or t < bt:
            continue
        cl = float(c["close"])
        if cl > orh and cl > pdh:
            nxt = [l for l in levels if l > cl]
            room = (min(nxt) - cl) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                if i + 1 >= len(cand):
                    return None
                s = cand.iloc[i]
                entry = float(cand.iloc[i + 1]["open"])
                stop = float(s["low"])
                risk = entry - stop
                tr = replay_ce(cand, i + 1, entry, stop, entry + 2 * risk)
                tr.update({"signal": s["time"], "nifty_break": bt, "orh": orh})
                return {"signal": s["time"],
                        "entry_time": cand.iloc[i + 1]["time"], "trade": tr}
    return None

def mirror_legs():
    spot_n, daily_n = load_nifty()
    bank_spot, bank_daily = load_bank()
    legs, skipped = [], 0
    days = [d.date().isoformat() for d in daily_n["date"]
            if d.year == 2026 and d.month <= 10]
    for ds in days:
        dd_n = day_data_nifty(spot_n, daily_n, ds)
        dd_b = day_data_bank(bank_spot, bank_daily, ds)
        if not (dd_b and dd_n):
            continue
        day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3])
        r = rescan_bank_l1_up(dd_b, day_nifty_tuple)
        if r is None or r["trade"] is None or r["trade"].get("net") is None:
            continue
        et = r["entry_time"]
        so = c5.SPOT_OPEN.get((ds, et))
        if so is None:
            skipped += 1
            continue
        legs.append(c5.mkleg(ds, "CE", et, c5.atm(so), c5.expiry_for(ds),
                             "(lA) v2 CE mirror", family="LAMIR",
                             _signal=r["signal"]))
    return legs, skipped

ref = v21_ref()
pooled, ns1 = v20_inputs()
legs, skipped = mirror_legs()
print(f"C155 population: {len(legs)} mirror legs, {skipped} skipped (no spot open)")
still = c5.fetch_missing(pooled + ns1 + legs)
print("still missing:", still)
assert not still
r = judge7("C155 (lA) CE MIRROR sleeve", ref, pooled, ns1,
           extra_families=[("LAMIR", legs, None)])
print("   detail:", [d for d in r["detail"] if d["family"] == "LAMIR"])
