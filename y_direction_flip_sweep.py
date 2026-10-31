"""Family (y): direction-flip AS A SEPARATE SYSTEM, not a PE fix. Nifty only, paper only.

FROZEN FLIP DEFINITION — stated before any scoring, no re-tuning after outcomes:
  Universe day = a day on which the (lA) PE system has BOTH a morning stop AND
  a re-entry stop. (lA) = BN-confirmed rescan morning (combined_confirm_sweep.
  rescan_trade) + scan_reentry variant "lA" (extended_window_sweep): morning-phase
  scan-skip to 11:30, afternoon stop-on-first-fail to 15:05, band [10, rescan risk].
  Primary scan uses V4 rescan mode for every day; the 8 documented Cluster 1 days
  are additionally run with their documented modes (2 Apr = skill) and, if the
  documented-mode result differs, the documented mode replaces V4 for that date
  (deduplicated by date, counted once). This is stated here so 2 Apr is not lost
  to a mode choice, and so the universe is not double-counted.
  FLIP trigger (ONE definition, picked before results): the FIRST 5-min bar AFTER
  the re-entry stop bar whose CLOSE is above the Nifty OR low. Entry = next bar
  open. Stop = flip signal bar low (CE, mirrored). Target = entry + 2 x risk.
  Square-off at the 15:10 close. 100 shares, Rs40/trade, one flip trade per day max.
  Scan for the flip signal runs from the bar after the re-entry stop bar through
  the 15:05 bar (so entry is at most 15:10). Stop-before-target on every bar
  including the entry bar (mirroring PE ordering). If there is no next bar after
  the flip signal bar, the day is no-trade.
  KNIFE-EDGE RULE (stated before results): a flip trade with risk < 5 points is
  flagged as an artefact, reported with its net, but EXCLUDED from the genuine
  green count and from the pass-bar green rate. It is still included in the
  reported flip total only if explicitly noted; the genuine total (artefacts
  removed) is reported alongside.
  Green = net > 0. No-trade counted separately from green throughout.
  PASS BAR FOR THE FLIP SYSTEM ITSELF: flip green >= 60% on flip days AND flip
  total positive AND no single flip trade > 50% of flip total AND every universe
  day reported (no cherry-picking). In-sample pass still needs out-of-sample
  validation (held-out year / forward paper, thresholds frozen) before adoption.
  Flip P&L is NEVER netted against PE losses to claim the PE system passes, and
  no PE trade is kept alive by a flip overlay — the flip is judged alone.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from extended_window_sweep import day_variant
QTY, COST = 100, 40.0

def replay_ce(candles, start_idx, entry, stop, target):
    risk = entry - stop
    if risk <= 0:
        return {"entry": entry, "stop": stop, "target": target, "exit": "invalid_risk",
                "exit_time": None, "exit_idx": None, "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]
        hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if lo <= stop:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "stop",
                    "exit_time": t, "exit_idx": j, "exit_price": stop,
                    "net": round(-risk * QTY - COST, 2), "risk": round(risk, 2)}
        if hi >= target:
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "target",
                    "exit_time": t, "exit_idx": j, "exit_price": target,
                    "net": round(2 * risk * QTY - COST, 2), "risk": round(risk, 2)}
        if t == "15:10":
            return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
                    "exit_time": t, "exit_idx": j, "exit_price": cl,
                    "net": round((cl - entry) * QTY - COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"entry": entry, "stop": stop, "target": round(target, 2), "exit": "square_off",
            "exit_time": c["time"], "exit_idx": len(candles) - 1, "exit_price": float(c["close"]),
            "net": round((float(c["close"]) - entry) * QTY - COST, 2), "risk": round(risk, 2)}

def flip_for_day(day_res):
    """day_res = day_variant(lA) result. Returns flip dict or None (no flip signal)."""
    if day_res is None or day_res.get("morning") is None or day_res.get("re") is None:
        return None
    # Reconstruct candles/orl via rescan_trade again is avoided: day_variant does not
    # return candles, so caller passes them. This helper is not used standalone.
    raise RuntimeError("use flip_from_rescan")

def main():
    spot, daily = load_nifty()
    bn_spot, bn_daily = load_bn()
    # All trading dates present in Nifty 5-min cache, Jan 2025 - 28 Oct 2026
    dates = sorted(spot["date"].dt.strftime("%Y-%m-%d").unique())
    dates = [d for d in dates if "2025-01-01" <= d <= "2026-10-28"]
    from combined_confirm_sweep import rescan_trade
    from extended_window_sweep import scan_reentry
    cluster1_modes = {"2026-04-02": "skill"}
    universe = []
    scanned = 0
    for ds in dates:
        dd = day_data_nifty(spot, daily, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        if dd is None or dbn is None:
            continue
        scanned += 1
        # Primary: V4 (lA)
        r = day_variant(dd, "v4", dbn, "lA")
        # Documented-mode override for Cluster 1 days
        if ds in cluster1_modes:
            r_doc = day_variant(dd, cluster1_modes[ds], dbn, "lA")
            if r_doc is not None and r_doc.get("morning") is not None:
                r = r_doc
        if r is None or r.get("morning") is None or r.get("re") is None:
            continue
        m, re_ = r["morning"], r["re"]
        if m.get("exit") != "stop" or re_.get("exit") != "stop":
            continue
        # Need candles + orl: re-run rescan to get them (same inputs, same result)
        mode = cluster1_modes.get(ds, "v4")
        rr = rescan_trade(dd, mode, dbn)
        if rr is None:
            continue
        cand, orl = rr["candles"], rr["orl"]
        re_exit_idx = re_["exit_idx"]
        # Afternoon reversal context (diagnostic only, after second stop bar)
        after = cand.iloc[re_exit_idx + 1:] if re_exit_idx + 1 < len(cand) else cand.iloc[0:0]
        min_low = float(after["low"].min()) if len(after) else None
        max_close = float(after["close"].max()) if len(after) else None
        close_1510 = None
        row1510 = cand[cand["time"] == "15:10"]
        if len(row1510):
            close_1510 = float(row1510.iloc[0]["close"])
        # Frozen flip scan
        flip = None
        for k in range(re_exit_idx + 1, len(cand)):
            c = cand.iloc[k]; t = c["time"]
            if t > "15:05":
                break
            if float(c["close"]) <= orl:
                continue
            if k + 1 >= len(cand):
                flip = {"signal": t, "exit": "no_next_bar", "net": None}
                break
            entry = float(cand.iloc[k + 1]["open"]); stop = float(c["low"]); risk = entry - stop
            target = entry + 2 * risk
            tr = replay_ce(cand, k + 1, entry, stop, target)
            tr.update({"signal": t, "orl": orl, "artefact": bool(risk < 5)})
            flip = tr
            break
        universe.append({
            "date": ds, "mode": mode, "orl": orl,
            "morning": {"signal": m.get("signal"), "entry": m.get("entry"), "stop": m.get("stop"),
                        "risk": m.get("risk"), "exit": m.get("exit"), "exit_time": m.get("exit_time"),
                        "net": m.get("net")},
            "reentry": {"signal": re_.get("re_signal"), "entry": re_.get("entry"), "stop": re_.get("stop"),
                        "risk": re_.get("risk"), "exit": re_.get("exit"), "exit_time": re_.get("exit_time"),
                        "net": re_.get("net")},
            "pe_day_net": r["day_net"],
            "after_second_stop": {"min_low": min_low, "max_close": max_close, "close_1510": close_1510,
                                  "reversal_to_1510": (round(close_1510 - min_low, 2) if (close_1510 is not None and min_low is not None) else None)},
            "flip": flip,
        })
        print(ds, "mode", mode, "orl", orl, "m", m.get("signal"), m.get("net"), "re", re_.get("re_signal"), re_.get("net"),
              "flip", (flip.get("signal"), flip.get("entry"), flip.get("stop"), flip.get("risk"), flip.get("exit"), flip.get("net"), flip.get("artefact")) if flip else None)
    traded = [u for u in universe if u["flip"] is not None and u["flip"].get("net") is not None]
    genuine = [u for u in traded if not u["flip"].get("artefact")]
    green = [u for u in genuine if u["flip"]["net"] > 0]
    print(f"\nSCANNED {scanned} days; UNIVERSE (two PE stops) {len(universe)} days; "
          f"FLIP TRADED {len(traded)} (genuine {len(genuine)}, artefact {len(traded)-len(genuine)}); "
          f"NO-TRADE {len(universe)-len(traded)}")
    print(f"FLIP genuine green {len(green)}/{len(genuine)} total {sum(u['flip']['net'] for u in genuine)}")
    print(f"FLIP all-traded total {sum(u['flip']['net'] for u in traded)}")
    if genuine:
        mx = max(genuine, key=lambda u: u["flip"]["net"])
        print(f"Largest genuine flip {mx['date']} net {mx['flip']['net']} share of genuine total "
              f"{mx['flip']['net']/sum(u['flip']['net'] for u in genuine) if sum(u['flip']['net'] for u in genuine) else 0:.1%}")
    with open(os.path.expanduser("~/workspace/trading/y_direction_flip_sweep_raw.json"), "w") as f:
        json.dump({"scanned_days": scanned, "universe": universe}, f, indent=2, default=str)

if __name__ == "__main__":
    main()
