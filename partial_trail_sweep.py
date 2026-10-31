"""Partial / trail + bias/room + narrow-OR sweeps for NIFTY Cluster 1.
Paper only. Replays bar-by-bar from Upstox 5-min cache, same signal scan
as timing_sweep.py / stop_sweep.py: V4 setup2 PE breakdown (close<OR low,
close<PDL, room>=200*scale, OR width<=360*scale, signal<=11:30), except
2026-04-02 Skill (close<OR low, close<PDL, no width/room cap).
Entry = next bar open. 100 shares equivalent, Rs40/trade total cost.
PE net = -(exit-entry)*100-40 for a full trade; for partial trades the
100 shares are split 50/50 and cost is charged once (Rs40 total).

Bar order, stated so results are reproducible: on each bar, the adverse
level (stop / trailed stop) is checked BEFORE the favourable level
(partial / target), matching the original engine's stop-before-target
order. A bar that hits both is therefore a stop, not a partial/target.

Family A variants (one at a time, not combined):
 A1 partial50_trailBE: when low <= entry - 1.0*risk (50% of the 2x target
    distance), book 50 shares at that level, move remaining stop to
    breakeven (entry). Remaining then exits on target, breakeven stop,
    or 15:10 square-off.
 A2 partial25_trailBE: same, partial level = entry - 0.5*risk (25% of
    target distance), 50 shares booked there, remaining stop to breakeven.
 A3 trail100: when low <= entry - 100 points (v4 activation, index
    points), move stop to breakeven (entry). No partial booking. If the
    100-point move is never reached before the original stop, the trade
    is exactly the baseline trade. (Trail destination is moot if never
    triggered; this is checked, not assumed.)
 A4 trail50_noPartial: when low <= entry - 1.0*risk, move stop to
    breakeven, no partial booked. A reversed trade then exits at
    breakeven = net -Rs40 (scratch, NOT green); a continued trade
    reaches the full target.
 A5 partial50_noTrail: book 50 at entry - 1.0*risk, remaining keeps the
    ORIGINAL stop. A reversed remaining leg then nets 50*partialProfit
    - 50*risk - 40 = -40 (scratch), not green.

Family B (filters applied to the baseline signal; a filtered day is
no-trade, counted separately from green):
 B1 room_abs200: baseline signal only counts if room to the next PD
    level below the signal close is >= 200 points absolute (not scaled).
    Room is computed exactly as in the original scan.
 B2 bias_strong: baseline signal only counts if the previous-day bias
    score (close position in PD range, %) is < 20 (strong bearish).
    Cluster 1 scores are in the failing-cases report.
 B3 room_scaled300: room >= 300*scale (stricter than the original
    200*scale). If no bar passes, no-trade (scan continues to 11:30,
    as in the distance sweep, so later signals can appear).

Family C (no-trade rule for the morning shape):
 C1 narrowOR80: no trade if OR width <= 80 points.
 C2 narrowOR100: no trade if OR width <= 100 points.
 C3 narrowOR150: no trade if OR width <= 150 points.
 C variants keep the baseline signal otherwise; a wide-OR day trades
 normally and can still lose, so C can only avoid, never convert.

Green = net > Rs0. Square-off positives are flagged separately and
are NOT counted as targets, but they ARE net>0 so they count as green
in the green column (as in prior sweeps, where this was stated);
the tables separate target vs square-off vs partial outcomes.
"""
import pandas as pd, json, math, os
BASE = os.path.expanduser("~/workspace/trading/data/progressive/NIFTY")
QTY, COST = 100, 40.0

def load():
    spot = pd.read_csv(os.path.join(BASE, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def day_data(spot, daily, datestr):
    d = pd.Timestamp(datestr)
    day_spot = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day_spot.empty or prev.empty: return None
    y = prev.iloc[-1]
    pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    return day_spot, pdh, pdc, pdl, bias, scale, cs

def find_signal(day_spot, pdh, pdc, pdl, scale, mode="v4", room_min_scaled=None, room_min_abs=None, bias_score=None, bias_max=None):
    or_c = day_spot[day_spot["time"] < "09:30"]
    if or_c.empty: return None, None, None, None
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i in range(len(candles)):
        c = candles.iloc[i]; t = c["time"]
        if t > "11:30": continue
        close = float(c["close"])
        if close < orl and close < pdl:
            if bias_max is not None and not (bias_score < bias_max):
                continue
            nxt = [l for l in levels if l < close]
            room = (close - max(nxt)) if nxt else math.inf
            if room_min_abs is not None and room < room_min_abs: continue
            if room_min_scaled is not None and room < room_min_scaled * scale: continue
            if mode == "skill":
                return i, candles, (orl, orh), room
            if (orh - orl) <= 360 * scale and room >= 200 * scale:
                return i, candles, (orl, orh), room
    return None, candles, (orl, orh), None

def baseline_props(spot, daily, ds, mode):
    dd = day_data(spot, daily, ds)
    if not dd: return None
    day_spot, pdh, pdc, pdl, bias, scale, cs = dd
    sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None: return None
    sig = candles.iloc[sig_idx]; entry = float(candles.iloc[sig_idx+1]["open"])
    return {"signal": sig["time"], "entry": entry, "stop": float(sig["high"]),
            "risk": float(sig["high"]) - entry, "orl": orl, "orh": orh,
            "or_width": orh - orl, "room": room, "bias": bias, "bias_score": cs,
            "scale": scale, "pdh": pdh, "pdc": pdc, "pdl": pdl}

def run_partial_trail(candles, sig_idx, orl, orh, variant):
    """Returns trade dict. variant in A1..A5. Entry bar included, stop first."""
    if sig_idx is None or sig_idx + 1 >= len(candles): return None
    sig = candles.iloc[sig_idx]
    entry = float(candles.iloc[sig_idx+1]["open"])
    stop = float(sig["high"]); risk = stop - entry
    if risk <= 0:
        return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
    target = entry - 2 * risk
    # partial / activation levels
    if variant == "A1":
        partial_level, trail_be = entry - 1.0 * risk, True
    elif variant == "A2":
        partial_level, trail_be = entry - 0.5 * risk, True
    elif variant == "A3":
        partial_level, trail_be = None, False
        act_level = entry - 100.0
    elif variant == "A4":
        partial_level, trail_be = None, True
        act_level = entry - 1.0 * risk
    elif variant == "A5":
        partial_level, trail_be = entry - 1.0 * risk, False
    else:
        raise ValueError(variant)
    partial_booked = False; partial_net = 0.0; partial_time = None
    trailed = False; cur_stop = stop; activated = False
    for j in range(sig_idx+1, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        # adverse check first
        if hi >= cur_stop:
            if partial_booked:
                # remaining 50 exit at cur_stop (breakeven if trailed, else original stop -- only A5 keeps original, but A5 has no trail so cur_stop==stop)
                rem_net = -(cur_stop - entry) * 50
                return finish(sig, entry, stop, target, risk, "stop_after_partial", cur_stop, t, partial_net + rem_net - COST, partial_booked, partial_time, trailed)
            # trail-only: exit at the TRAILED stop (breakeven if activated), not the original stop
            return finish(sig, entry, stop, target, risk, "trailed_stop" if trailed else "stop", cur_stop, t, -(cur_stop-entry)*QTY-COST, False, None, trailed)
        # activation / partial check (favourable)
        if variant in ("A1", "A2", "A5") and not partial_booked and lo <= partial_level:
            partial_booked = True; partial_time = t
            partial_net = (entry - partial_level) * 50  # PE profit per share * 50
            if trail_be:
                cur_stop = entry; trailed = True
            # same bar: target check for remaining happens below (low<=target would be a bigger move; partial bar cannot also be target unless target<=partial, which it is not)
            if lo <= target:
                rem_net = (entry - target) * 50
                return finish(sig, entry, stop, target, risk, "target_same_bar_as_partial", target, t, partial_net + rem_net - COST, True, partial_time, trailed)
        elif variant in ("A3", "A4") and not activated and lo <= act_level:
            activated = True; trailed = True; cur_stop = entry
            if lo <= target:
                return finish(sig, entry, stop, target, risk, "target", target, t, (entry-target)*QTY-COST, False, None, True)
        # target check for remaining / full
        if lo <= target:
            if partial_booked:
                rem_net = (entry - target) * 50
                return finish(sig, entry, stop, target, risk, "target_after_partial", target, t, partial_net + rem_net - COST, True, partial_time, trailed)
            return finish(sig, entry, stop, target, risk, "target", target, t, (entry-target)*QTY-COST, False, None, trailed)
        if t == "15:10":
            if partial_booked:
                rem_net = (entry - cl) * 50
                return finish(sig, entry, stop, target, risk, "square_off_after_partial", cl, t, partial_net + rem_net - COST, True, partial_time, trailed)
            return finish(sig, entry, stop, target, risk, "square_off", cl, t, (entry-cl)*QTY-COST, False, None, trailed)
    c = candles.iloc[-1]
    if partial_booked:
        rem_net = (entry - float(c["close"])) * 50
        return finish(sig, entry, stop, target, risk, "square_off_after_partial", float(c["close"]), c["time"], partial_net + rem_net - COST, True, partial_time, trailed)
    return finish(sig, entry, stop, target, risk, "square_off", float(c["close"]), c["time"], (entry-float(c["close"]))*QTY-COST, False, None, trailed)

def finish(sig, entry, stop, target, risk, exit_reason, exit_price, exit_time, net, partial_booked, partial_time, trailed):
    return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2),
            "risk": round(risk,2), "exit": exit_reason, "exit_time": exit_time,
            "exit_price": exit_price, "net": round(net,2),
            "partial_booked": partial_booked, "partial_time": partial_time, "trailed": trailed}

def replay_A(spot, daily, ds, mode, variant):
    dd = day_data(spot, daily, ds)
    if not dd: return None
    day_spot, pdh, pdc, pdl, bias, scale, cs = dd
    sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode)
    if sig_idx is None: return None
    r = run_partial_trail(candles, sig_idx, orl, orh, variant)
    if r: r.update({"orl": orl, "orh": orh, "room": room})
    return r

def replay_filtered(spot, daily, ds, mode, kind, param):
    """Baseline full trade (no partial) after a filter; returns trade or None.
    kind: B_room_abs, B_bias, B_room_scaled, C_or_width."""
    dd = day_data(spot, daily, ds)
    if not dd: return None
    day_spot, pdh, pdc, pdl, bias, scale, cs = dd
    if kind == "C_or_width":
        or_c = day_spot[day_spot["time"] < "09:30"]
        orw = float(or_c["high"].max()) - float(or_c["low"].min())
        if orw <= param: return None
        sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode)
    elif kind == "B_room_abs":
        sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode, room_min_abs=param)
    elif kind == "B_bias":
        sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode, bias_score=cs, bias_max=param)
    elif kind == "B_room_scaled":
        sig_idx, candles, (orl, orh), room = find_signal(day_spot, pdh, pdc, pdl, scale, mode, room_min_scaled=param)
    else: raise ValueError(kind)
    if sig_idx is None: return None
    # baseline full trade: reuse A-variant machinery with no partial/trail by calling run with a dummy? Use simple loop here.
    sig = candles.iloc[sig_idx]; entry = float(candles.iloc[sig_idx+1]["open"])
    stop = float(sig["high"]); risk = stop - entry; target = entry - 2*risk
    if risk <= 0: return {"signal": sig["time"], "entry": entry, "stop": stop, "target": None, "exit": "invalid_risk", "net": None, "risk": round(risk,2)}
    for j in range(sig_idx+1, len(candles)):
        c = candles.iloc[j]
        if float(c["high"]) >= stop:
            return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "stop", "exit_time": c["time"], "exit_price": stop, "net": round(-(stop-entry)*QTY-COST,2), "orl": orl, "orh": orh, "room": room}
        if float(c["low"]) <= target:
            return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "target", "exit_time": c["time"], "exit_price": target, "net": round((entry-target)*QTY-COST,2), "orl": orl, "orh": orh, "room": room}
        if c["time"] == "15:10":
            return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry-float(c["close"]))*QTY-COST,2), "orl": orl, "orh": orh, "room": room}
    c = candles.iloc[-1]
    return {"signal": sig["time"], "entry": entry, "stop": stop, "target": round(target,2), "risk": round(risk,2), "exit": "square_off", "exit_time": c["time"], "exit_price": float(c["close"]), "net": round((entry-float(c["close"]))*QTY-COST,2), "orl": orl, "orh": orh, "room": room}

def summarise(rows):
    traded = [r for r in rows if r["trade"] is not None and r["trade"].get("net") is not None]
    green = sum(1 for r in traded if r["trade"]["net"] > 0)
    targets = sum(1 for r in traded if "target" in str(r["trade"]["exit"]))
    nt = sum(1 for r in rows if r["trade"] is None or r["trade"].get("net") is None)
    loss = sum(1 for r in traded if r["trade"]["net"] <= 0)
    total = round(sum(r["trade"]["net"] for r in traded),2)
    return {"green": green, "targets_incl_partial_targets": targets, "no_trade": nt, "still_loss_or_scratch": loss, "traded_total": total, "n_traded": len(traded)}

if __name__ == "__main__":
    spot, daily = load()
    cluster1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    orig_nets = {"2026-01-09":-3745,"2026-02-06":-2275,"2026-03-30":-2055,"2026-04-02":-2115,
                 "2026-05-13":-5075,"2026-06-29":-4740,"2026-07-08":-1985,"2026-08-19":-2300}
    modes = {"2026-04-02": "skill"}
    win_days = {"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,
                "2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,
                "2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,
                "2026-10-08":5440,"2026-10-23":11390}
    win_modes = {"2026-03-23": "skill"}
    out = {"baseline_props": {}}
    print("=== BASELINE PROPS Cluster1 ===")
    for ds in cluster1:
        p = baseline_props(spot, daily, ds, modes.get(ds,"v4"))
        out["baseline_props"][ds] = p
        print(ds, p)
    print("\n=== BASELINE PROPS Winning PE ===")
    out["winning_props"] = {}
    for ds in win_days:
        p = baseline_props(spot, daily, ds, win_modes.get(ds,"v4"))
        out["winning_props"][ds] = p
        print(ds, win_days[ds], p)
    variants = []
    for v in ["A1","A2","A3","A4","A5"]:
        variants.append((v, "A", v))
    variants += [("B1_room_abs200","B","B_room_abs"), ("B2_bias_lt20","B","B_bias"), ("B3_room_scaled300","B","B_room_scaled"),
                 ("C1_or_le80","C","C_or_width"), ("C2_or_le100","C","C_or_width"), ("C3_or_le150","C","C_or_width")]
    for name, fam, kind in variants:
        rows = []
        for ds in cluster1:
            if fam == "A":
                t = replay_A(spot, daily, ds, modes.get(ds,"v4"), kind)
            elif name == "B1_room_abs200":
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "B_room_abs", 200)
            elif name == "B2_bias_lt20":
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "B_bias", 20)
            elif name == "B3_room_scaled300":
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "B_room_scaled", 300)
            elif name == "C1_or_le80":
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "C_or_width", 80)
            elif name == "C2_or_le100":
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "C_or_width", 100)
            else:
                t = replay_filtered(spot, daily, ds, modes.get(ds,"v4"), "C_or_width", 150)
            rows.append({"date": ds, "orig_net": orig_nets[ds], "trade": t})
        out[name] = {"cluster1": rows, "summary": summarise(rows)}
        print(f"\n=== {name} Cluster1 {out[name]['summary']} ===")
        for r in rows: print(r["date"], r["orig_net"], "->", r["trade"])
        # winning impact
        wrows = []
        for ds, onet in win_days.items():
            if fam == "A":
                t = replay_A(spot, daily, ds, win_modes.get(ds,"v4"), kind)
            elif name == "B1_room_abs200":
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "B_room_abs", 200)
            elif name == "B2_bias_lt20":
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "B_bias", 20)
            elif name == "B3_room_scaled300":
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "B_room_scaled", 300)
            elif name == "C1_or_le80":
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "C_or_width", 80)
            elif name == "C2_or_le100":
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "C_or_width", 100)
            else:
                t = replay_filtered(spot, daily, ds, win_modes.get(ds,"v4"), "C_or_width", 150)
            wrows.append({"date": ds, "orig_net": onet, "trade": t})
        out[name]["winning_pe"] = wrows
        out[name]["winning_summary"] = summarise(wrows)
        print(f"--- {name} Winning PE {out[name]['winning_summary']} ---")
        for r in wrows: print(r["date"], r["orig_net"], "->", r["trade"])
    with open(os.path.expanduser("~/workspace/trading/partial_trail_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
