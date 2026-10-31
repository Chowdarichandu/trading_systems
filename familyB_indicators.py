"""Family B — INDICATORS, index OPTIONS, paper only, no orders.
Window: full October 2026, 1-28 Oct (18 trading days), Nifty and Bank separately.
Cache only: ~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv
+ spot_daily.csv (NO volume column -> B1 VWAP and B5 volume are NOT TESTABLE,
reported as such, never proxied and never labelled as tested).

FROZEN DEFINITIONS (written before scoring; one family each, never blended):
- Base Skill v2 (S1): raw OR signal = first 5-min close beyond 09:15-09:30 OR
  (bars time < 09:30) between 09:30-11:30; S1 blocks: (a) 09:30 PE taken only
  if close < PDL; (b) CE blocked on bearish-bias day (prev-close position
  cs < 35%). Exit: entry = next bar open, stop = signal high/low,
  target = 2x risk, square-off 15:10, stop priority, 100 shares provisional,
  Rs 40/trade. Base nets cross-checked against index_options_v2_october_trades.csv.
- Base (lA) v2 (L1): day trades + signal times taken verbatim from the v2 CSV
  (Nifty 3 days, Bank 4 days); day net = morning + re-entry where applicable.
  Filter families B2/B3 remove the WHOLE day trade if the signal bar fails.
  B4-(lA) is morning-leg-only (see below); B6-(lA) is a partial re-test only.
- Indicators computed on the CONTINUOUS 5-min close series per symbol
  (all cached days, chronological), NOT reset daily, because a 09:30 signal
  has only 3 prior bars that day and daily RSI/EMA/ATR would be undefined:
  EMA9/EMA21 (seed = SMA of first n closes, k = 2/(n+1)); RSI14 Wilder;
  ATR14 Wilder on true range. Values read AT the signal bar (inclusive).
- B1 VWAP filter: PE only if signal close < session VWAP at signal bar;
  CE only if close > VWAP. NOT TESTABLE: no volume in cache.
- B2 EMA trend filter: PE kept only if close < EMA9 AND EMA9 < EMA21;
  CE kept only if close > EMA9 AND EMA9 > EMA21. Else blocked (no later signal).
- B3 RSI extremes filter: PE blocked if RSI14 <= 30; CE blocked if RSI14 >= 70;
  otherwise kept. (Extremes only; no 50-line trend rule blended in.)
- B4 ATR stops (exit replacement, NOT a filter): stop distance = 1.5 x ATR14
  at signal bar; stop = entry - 1.5*ATR (CE) / entry + 1.5*ATR (PE);
  TARGET UNCHANGED (same absolute base target price); stop priority;
  square-off 15:10; Rs 40. Scored fully on Skill tracks. On (lA) tracks,
  scored on the reconstructed MORNING leg only (entry = next open after
  signal bar, stop = signal high, target = entry - 2*risk, replay_pe rules);
  day-net B4 is NOT claimed because the re-entry leg cannot be re-scored
  from the CSV alone. Morning-leg base nets are shown alongside so the
  comparison is leg-to-leg.
- B5 Volume confirmation: signal-bar volume > 1.5 x mean volume of prior
  20 bars. NOT TESTABLE: no volume column in cache.
- B6 OR extension (Skill, full re-score): OR = bars time < 10:00
  (09:15-09:55); signal = first close outside extended OR between
  10:00-11:30; CE blocked if bearish bias; PE blocked if close >= PDL
  (S1 generalised from the 09:30 bar to the first-signal bar); room_ratio
  >= 1.5 (room >= 300*scale, scale = prev close / 55000 as in base code;
  NOT loosened below 1.5x); exit as base Skill. One trade/day max.
- B6-(lA) PARTIAL only: each base (lA) signal bar re-tested against the
  extended-OR low (PE rescan requires close < OR low). A full rescan
  re-run is NOT scored here because the confirmer-break window also shifts
  with the OR window; new later rescans under extended OR are unknown,
  not zero. Labelled partial wherever quoted.

Unit: spot provisional = points x 100 shares - Rs 40. NOT an options-lot
profit and NOT a futures profit. Premiums NOT computed (no option candles
in cache); premium route is out of scope for this subagent task.
Frequency = trades / 18 days x 5.
"""
import os, json, math
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
QTY, COST = 100, 40.0
OCT = [d for d in pd.date_range("2026-10-01", "2026-10-28")]
# trading days = days present in Nifty daily cache within window
LA_BASE = {  # (symbol, date): (signal_time, direction, day_net, exit_reason) from v2 CSV
    ("NIFTY", "2026-10-08"): ("11:25", "PE", 11690.0, "target"),
    ("NIFTY", "2026-10-21"): ("11:35", "PE", 4940.0, "target"),
    ("NIFTY", "2026-10-23"): ("10:05", "PE", 11390.0, "target"),
    ("BANKNIFTY", "2026-10-07"): ("09:35", "PE", -7475.0, "stop"),
    ("BANKNIFTY", "2026-10-08"): ("13:15", "PE", -8510.0, "stop"),
    ("BANKNIFTY", "2026-10-21"): ("11:15", "PE", 20200.0, "target"),
    ("BANKNIFTY", "2026-10-23"): ("09:55", "PE", 24060.0, "target"),
}

def load_sym(sym):
    spot = pd.read_csv(os.path.join(BASE, sym, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, sym, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp").reset_index(drop=True), daily.sort_values("date")

def add_indicators(spot):
    c = spot["close"].astype(float).values
    h = spot["high"].astype(float).values
    l = spot["low"].astype(float).values
    n = len(c)
    def ema(period):
        out = [None]*n
        if n <= period: return out
        sma = sum(c[:period])/period
        out[period-1] = sma
        k = 2/(period+1)
        for i in range(period, n):
            out[i] = c[i]*k + out[i-1]*(1-k)
        return out
    e9, e21 = ema(9), ema(21)
    rsi = [None]*n
    if n > 14:
        gains = [max(c[i]-c[i-1], 0.0) for i in range(1, 15)]
        losses = [max(c[i-1]-c[i], 0.0) for i in range(1, 15)]
        ag, al = sum(gains)/14, sum(losses)/14
        rsi[14] = 100-100/(1+ag/al) if al else 100.0
        for i in range(15, n):
            d = c[i]-c[i-1]
            ag = (ag*13+max(d, 0.0))/14; al = (al*13+max(-d, 0.0))/14
            rsi[i] = 100-100/(1+ag/al) if al else 100.0
    atr = [None]*n
    tr = [0.0]*n
    for i in range(1, n):
        tr[i] = max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
    if n > 14:
        atr[14] = sum(tr[1:15])/14
        for i in range(15, n):
            atr[i] = (atr[i-1]*13+tr[i])/14
    spot = spot.copy()
    spot["ema9"], spot["ema21"], spot["rsi14"], spot["atr14"] = e9, e21, rsi, atr
    return spot

def day_rows(spot, d):
    return spot[spot["date"] == d].reset_index(drop=True)

def prev_daily(daily, d):
    prev = daily[daily["date"] < d]
    return prev.iloc[-1] if len(prev) else None

def bias_cs(y):
    rng = float(y["high"])-float(y["low"])
    cs = (float(y["close"])-float(y["low"]))/rng*100 if rng else 50.0
    return ("bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"), cs

def skill_signal(day, or_cut="09:30", sig_from="09:30", sig_to="11:30"):
    or_c = day[day["time"] < or_cut]
    if or_c.empty: return None
    orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
    cand = day[(day["time"] >= sig_from) & (day["time"] <= sig_to)]
    for _, row in cand.iterrows():
        if float(row["close"]) > orh: return "or_breakout", "CE", row, orh, orl
        if float(row["close"]) < orl: return "or_breakdown", "PE", row, orh, orl
    return None

def skill_outcome(day, sig_row, direction):
    cand = day[day["time"] >= "09:30"].reset_index(drop=True)
    idx = cand.index[cand["timestamp"] == sig_row["timestamp"]]
    if len(idx) == 0: return None
    si = int(idx[0])
    if si+1 >= len(cand): return None
    entry = float(cand.iloc[si+1]["open"])
    if direction == "CE":
        stop = entry - (entry - float(sig_row["low"])); target = entry + 2*(entry-stop)
    else:
        stop = entry + (float(sig_row["high"]) - entry); target = entry - 2*(stop-entry)
    if entry == stop: return None
    d = 1 if direction == "CE" else -1
    for j in range(si+1, len(cand)):
        row = cand.iloc[j]
        if direction == "CE":
            if float(row["low"]) <= stop: return {"entry": entry, "stop": stop, "target": target, "exit_reason": "stop", "exit_price": stop, "net_rs": round(-(entry-stop)*QTY-COST, 2)}
            if float(row["high"]) >= target: return {"entry": entry, "stop": stop, "target": target, "exit_reason": "target", "exit_price": target, "net_rs": round(2*(entry-stop)*QTY-COST, 2)}
        else:
            if float(row["high"]) >= stop: return {"entry": entry, "stop": stop, "target": target, "exit_reason": "stop", "exit_price": stop, "net_rs": round(-(stop-entry)*QTY-COST, 2)}
            if float(row["low"]) <= target: return {"entry": entry, "stop": stop, "target": target, "exit_reason": "target", "exit_price": target, "net_rs": round(2*(stop-entry)*QTY-COST, 2)}
        if row["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": target, "exit_reason": "square_off", "exit_price": float(row["close"]), "net_rs": round(d*(float(row["close"])-entry)*QTY-COST, 2)}
    row = cand.iloc[-1]
    return {"entry": entry, "stop": stop, "target": target, "exit_reason": "square_off", "exit_price": float(row["close"]), "net_rs": round(d*(float(row["close"])-entry)*QTY-COST, 2)}

def atr_outcome(day, sig_row, direction, base):
    """B4: same entry/target as base, stop replaced by 1.5*ATR14 at signal bar."""
    cand = day[day["time"] >= "09:30"].reset_index(drop=True)
    idx = cand.index[cand["timestamp"] == sig_row["timestamp"]]
    si = int(idx[0])
    atr = float(sig_row["atr14"])
    entry, target = base["entry"], base["target"]
    stop = entry - 1.5*atr if direction == "CE" else entry + 1.5*atr
    d = 1 if direction == "CE" else -1
    for j in range(si+1, len(cand)):
        row = cand.iloc[j]
        if direction == "CE":
            if float(row["low"]) <= stop: return {"exit_reason": "stop", "exit_price": stop, "net_rs": round(-(entry-stop)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}
            if float(row["high"]) >= target: return {"exit_reason": "target", "exit_price": target, "net_rs": round(d*(target-entry)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}
        else:
            if float(row["high"]) >= stop: return {"exit_reason": "stop", "exit_price": stop, "net_rs": round(-(stop-entry)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}
            if float(row["low"]) <= target: return {"exit_reason": "target", "exit_price": target, "net_rs": round(d*(target-entry)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}
        if row["time"] == "15:10":
            return {"exit_reason": "square_off", "exit_price": float(row["close"]), "net_rs": round(d*(float(row["close"])-entry)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}
    row = cand.iloc[-1]
    return {"exit_reason": "square_off", "exit_price": float(row["close"]), "net_rs": round(d*(float(row["close"])-entry)*QTY-COST, 2), "atr_stop": round(stop, 2), "atr14": round(atr, 2)}

def replay_pe_leg(cand, start_idx, entry, stop, target):
    """Mirror of close_reentry_sweep.replay_pe (PE only, stop before target, 15:10 sq-off)."""
    risk = stop - entry
    for j in range(start_idx, len(cand)):
        row = cand.iloc[j]
        if float(row["high"]) >= stop: return {"exit": "stop", "net": round(-risk*QTY-COST, 2), "exit_time": row["time"]}
        if float(row["low"]) <= target: return {"exit": "target", "net": round(2*risk*QTY-COST, 2), "exit_time": row["time"]}
        if row["time"] == "15:10": return {"exit": "square_off", "net": round((entry-float(row["close"]))*QTY-COST, 2), "exit_time": row["time"]}
    row = cand.iloc[-1]
    return {"exit": "square_off", "net": round((entry-float(row["close"]))*QTY-COST, 2), "exit_time": row["time"]}

def room_ratio(sig_close, direction, pdh, pdc, pdl, scale):
    levels = sorted(set([pdh, pdc, pdl]))
    if direction == "CE":
        nxt = [lv for lv in levels if lv > sig_close]
        room = (min(nxt)-sig_close) if nxt else float("inf")
    else:
        nxt = [lv for lv in levels if lv < sig_close]
        room = (sig_close-max(nxt)) if nxt else float("inf")
    return (room/(200*scale) if scale else 0.0), room

def summ(rows):
    if not rows: return {"trades": 0, "targets": 0, "green": 0, "net": 0.0, "per_week": 0.0}
    net = round(sum(r["net_rs"] for r in rows), 2)
    return {"trades": len(rows), "targets": sum(1 for r in rows if r["exit_reason"] == "target"),
            "green": sum(1 for r in rows if r["net_rs"] > 0), "net": net,
            "per_week": round(len(rows)/18*5, 2)}

def main():
    out_rows = []
    report = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        spot_raw, daily = load_sym(sym)
        print(f"{sym} columns: {list(spot_raw.columns)}  (volume present: {'volume' in spot_raw.columns})")
        spot = add_indicators(spot_raw)
        by_ts = {ts: row for ts, row in spot.iterrows()}  # not used; use timestamp match below
        oct_days = sorted(d for d in daily["date"] if d.year == 2026 and d.month == 10)
        print(f"{sym} October days in daily cache: {len(oct_days)} {[d.date().isoformat() for d in oct_days]}")
        # ---- Skill base (S1) recompute ----
        skill_taken, skill_blocked = [], []
        for d in oct_days:
            day = day_rows(spot, d)
            y = prev_daily(daily, d)
            if y is None: continue
            pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
            bias, cs = bias_cs(y)
            sig = skill_signal(day)
            if sig is None: continue
            setup, direction, srow, orh, orl = sig
            blocked = None
            if direction == "CE" and bias == "bearish": blocked = "S1_CE_bearish"
            if direction == "PE" and srow["time"] == "09:30" and not (float(srow["close"]) < pdl): blocked = "S1_0930_PE_not_below_PDL"
            rec = {"date": d.date().isoformat(), "setup": setup, "direction": direction,
                   "signal_time": srow["time"], "sig_close": round(float(srow["close"]), 2),
                   "ema9": round(float(srow["ema9"]), 2) if srow["ema9"] is not None else None,
                   "ema21": round(float(srow["ema21"]), 2) if srow["ema21"] is not None else None,
                   "rsi14": round(float(srow["rsi14"]), 2) if srow["rsi14"] is not None else None,
                   "atr14": round(float(srow["atr14"]), 2) if srow["atr14"] is not None else None,
                   "bias": bias, "cs": round(cs, 1)}
            oc = skill_outcome(day, srow, direction)
            rec["exit_reason"] = oc["exit_reason"]; rec["net_rs"] = oc["net_rs"]
            rec["entry"] = round(oc["entry"], 2); rec["stop"] = round(oc["stop"], 2); rec["target"] = round(oc["target"], 2)
            if blocked:
                rec["blocked"] = blocked; skill_blocked.append(rec)
            else:
                skill_taken.append((rec, day, srow, oc))
        # cross-check vs v2 CSV nets
        csv_nets = {"NIFTY": {"2026-10-05": -2220.0, "2026-10-06": 4240.0, "2026-10-07": -2725.0, "2026-10-08": 5440.0, "2026-10-12": -4605.0, "2026-10-26": 16550.0, "2026-10-27": -2790.0, "2026-10-28": -5470.0},
                    "BANKNIFTY": {"2026-10-01": 16640.0, "2026-10-05": 25690.0, "2026-10-06": -1435.0, "2026-10-07": -7475.0, "2026-10-08": -11070.0, "2026-10-12": -4640.0, "2026-10-14": -16660.0, "2026-10-23": 14860.0, "2026-10-27": -7235.0}}[sym]
        mism = [(r["date"], r["net_rs"], csv_nets.get(r["date"])) for r, _, _, _ in skill_taken if abs(r["net_rs"]-csv_nets.get(r["date"], 999999)) > 0.01]
        print(f"{sym} Skill S1 taken={len(skill_taken)} blocked={len(skill_blocked)} cross-check mismatches vs v2 CSV: {mism}")
        base_skill = [r for r, _, _, _ in skill_taken]
        report[f"Skill {sym} base"] = summ(base_skill)
        # ---- B2 EMA filter on Skill taken ----
        kept = []
        for r, day, srow, oc in skill_taken:
            if r["direction"] == "PE" and float(srow["close"]) < float(srow["ema9"]) and float(srow["ema9"]) < float(srow["ema21"]): kept.append(r)
            if r["direction"] == "CE" and float(srow["close"]) > float(srow["ema9"]) and float(srow["ema9"]) > float(srow["ema21"]): kept.append(r)
        report[f"Skill {sym} B2 EMA"] = summ(kept)
        print(f"{sym} B2 Skill kept {[ (r['date'], r['direction'], r['exit_reason'], r['net_rs']) for r in kept]}")
        # ---- B3 RSI extremes filter on Skill taken ----
        kept3 = [r for r, _, _, _ in skill_taken if not ((r["direction"] == "PE" and r["rsi14"] <= 30) or (r["direction"] == "CE" and r["rsi14"] >= 70))]
        report[f"Skill {sym} B3 RSI"] = summ(kept3)
        print(f"{sym} B3 Skill blocked-out {[ (r['date'], r['direction'], r['rsi14'], r['exit_reason'], r['net_rs']) for r, _, _, _ in skill_taken if r not in kept3]}")
        # ---- B4 ATR stops on Skill taken ----
        b4 = []
        for r, day, srow, oc in skill_taken:
            a = atr_outcome(day, srow, r["direction"], oc)
            b4.append({"date": r["date"], "direction": r["direction"], "exit_reason": a["exit_reason"], "net_rs": a["net_rs"],
                       "base_exit": r["exit_reason"], "base_net": r["net_rs"], "atr14": a["atr14"], "atr_stop": a["atr_stop"], "base_stop": r["stop"]})
        report[f"Skill {sym} B4 ATR"] = summ(b4)
        print(f"{sym} B4 Skill {[(b['date'], b['direction'], b['base_exit'], b['base_net'], '->', b['exit_reason'], b['net_rs'], 'ATR', b['atr14']) for b in b4]}")
        # ---- B6 extended OR on Skill (full re-score) ----
        b6, b6_rejects = [], []
        for d in oct_days:
            day = day_rows(spot, d)
            y = prev_daily(daily, d)
            if y is None: continue
            pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
            bias, cs = bias_cs(y); scale = pdc/55000.0 if pdc else 1.0
            sig = skill_signal(day, or_cut="10:00", sig_from="10:00", sig_to="11:30")
            if sig is None: continue
            setup, direction, srow, orh, orl = sig
            reason = None
            if direction == "CE" and bias == "bearish": reason = "CE_bearish"
            if direction == "PE" and not (float(srow["close"]) < pdl): reason = "PE_not_below_PDL"
            rr, room = room_ratio(float(srow["close"]), direction, pdh, pdc, pdl, scale)
            if reason is None and rr < 1.5: reason = f"room_ratio_{rr:.2f}<1.5"
            if reason:
                b6_rejects.append({"date": d.date().isoformat(), "direction": direction, "signal_time": srow["time"], "reason": reason, "room_ratio": round(rr, 2)})
                continue
            oc = skill_outcome(day, srow, direction)
            if oc is None: continue
            b6.append({"date": d.date().isoformat(), "direction": direction, "signal_time": srow["time"],
                       "ema9": round(float(srow["ema9"]), 2), "ema21": round(float(srow["ema21"]), 2),
                       "rsi14": round(float(srow["rsi14"]), 2), "exit_reason": oc["exit_reason"], "net_rs": oc["net_rs"],
                       "room_ratio": round(rr, 2)})
        report[f"Skill {sym} B6 extOR"] = summ(b6)
        print(f"{sym} B6 Skill kept {[(b['date'], b['direction'], b['signal_time'], b['exit_reason'], b['net_rs']) for b in b6]} rejects {b6_rejects}")
        # ---- (lA) base: indicator values at signal bars + morning-leg reconstruction ----
        la_rows = []
        for (s, ds), (st, direction, day_net, exit_r) in sorted(LA_BASE.items()):
            if s != sym: continue
            d = pd.Timestamp(ds)
            day = day_rows(spot, d)
            srow = day[day["time"] == st]
            if srow.empty:
                print(f"!! {sym} {ds} signal bar {st} NOT FOUND in cache day rows"); continue
            srow = srow.iloc[0]
            cand = day[day["time"] >= "09:30"].reset_index(drop=True)
            idx = cand.index[cand["time"] == st]
            si = int(idx[0])
            entry = float(cand.iloc[si+1]["open"]) if si+1 < len(cand) else None
            stop = float(srow["high"]); risk = stop-entry if entry else None
            target = entry-2*risk if entry else None
            morning = replay_pe_leg(cand, si+1, entry, stop, target) if entry else None
            # extended OR low for B6 partial
            or_c = day[day["time"] < "09:30"]; orl = float(or_c["low"].min()); orh = float(or_c["high"].max())
            ext = day[day["time"] < "10:00"]; ext_orl = float(ext["low"].min()); ext_orh = float(ext["high"].max())
            la_rows.append({"date": ds, "signal_time": st, "direction": direction, "day_net": day_net,
                            "day_exit": exit_r, "sig_close": round(float(srow["close"]), 2),
                            "ema9": round(float(srow["ema9"]), 2), "ema21": round(float(srow["ema21"]), 2),
                            "rsi14": round(float(srow["rsi14"]), 2), "atr14": round(float(srow["atr14"]), 2),
                            "morning_exit": morning["exit"] if morning else None, "morning_net": morning["net"] if morning else None,
                            "entry": round(entry, 2) if entry else None, "stop": round(stop, 2), "target": round(target, 2) if target else None,
                            "orl": round(orl, 2), "ext_orl": round(ext_orl, 2),
                            "b6_partial_survives": bool(float(srow["close"]) < ext_orl)})
        report[f"(lA) {sym} base"] = {"trades": len(la_rows), "targets": sum(1 for r in la_rows if r["day_exit"] == "target"),
                                      "green": sum(1 for r in la_rows if r["day_net"] > 0), "net": round(sum(r["day_net"] for r in la_rows), 2),
                                      "per_week": round(len(la_rows)/18*5, 2)}
        # B2/B3 on (lA): whole-day removal
        for fam, cond in (("B2 EMA", lambda r: r["sig_close"] < r["ema9"] and r["ema9"] < r["ema21"]),
                          ("B3 RSI", lambda r: not (r["rsi14"] <= 30))):  # all (lA) are PE
            kept_la = [r for r in la_rows if cond(r)]
            report[f"(lA) {sym} {fam}"] = {"trades": len(kept_la), "targets": sum(1 for r in kept_la if r["day_exit"] == "target"),
                                           "green": sum(1 for r in kept_la if r["day_net"] > 0),
                                           "net": round(sum(r["day_net"] for r in kept_la), 2), "per_week": round(len(kept_la)/18*5, 2)}
        # B4-(lA) morning-leg only
        b4la = []
        for r in la_rows:
            day = day_rows(spot, pd.Timestamp(r["date"]))
            srow = day[day["time"] == r["signal_time"]].iloc[0]
            cand = day[day["time"] >= "09:30"].reset_index(drop=True)
            si = int(cand.index[cand["time"] == r["signal_time"]][0])
            atr = float(srow["atr14"]); entry = r["entry"]; target = r["target"]
            atr_stop = entry + 1.5*atr
            leg = replay_pe_leg(cand, si+1, entry, atr_stop, target)
            # replay_pe_leg computes net with stop=atr_stop: risk=atr_stop-entry; net stop = -risk*100-40; target net uses 2*risk -- WRONG for B4 (target unchanged in points, not 2x new risk).
            # Recompute properly: target net = (entry-target)*100-40; stop net = -(atr_stop-entry)*100-40; sq-off = (entry-exit_close)*100-40.
            if leg["exit"] == "stop": net4 = round(-(atr_stop-entry)*QTY-COST, 2)
            elif leg["exit"] == "target": net4 = round((entry-target)*QTY-COST, 2)
            else:
                # find sq-off close at exit_time
                erow = cand[cand["time"] == leg["exit_time"]].iloc[0]
                net4 = round((entry-float(erow["close"]))*QTY-COST, 2)
            b4la.append({"date": r["date"], "signal_time": r["signal_time"], "morning_base_exit": r["morning_exit"],
                         "morning_base_net": r["morning_net"], "atr14": r["atr14"], "atr_stop": round(atr_stop, 2),
                         "base_stop": r["stop"], "b4_exit": leg["exit"], "b4_net": net4, "day_net_base": r["day_net"]})
        report[f"(lA) {sym} B4 ATR morning-leg"] = {"morning_base": {"trades": len(la_rows), "net": round(sum(r["morning_net"] for r in la_rows), 2),
                                                                     "targets": sum(1 for r in la_rows if r["morning_exit"] == "target")},
                                                    "morning_b4": {"trades": len(b4la), "net": round(sum(b["b4_net"] for b in b4la), 2),
                                                                     "targets": sum(1 for b in b4la if b["b4_exit"] == "target")}}
        print(f"{sym} (lA) rows:")
        for r in la_rows: print("   ", r)
        print(f"{sym} (lA) B4 morning-leg: {b4la}")
        # detail rows for CSV
        for r, day, srow, oc in skill_taken:
            out_rows.append({"track": f"Skill {sym}", "date": r["date"], "direction": r["direction"], "signal_time": r["signal_time"],
                             "sig_close": r["sig_close"], "ema9": r["ema9"], "ema21": r["ema21"], "rsi14": r["rsi14"], "atr14": r["atr14"],
                             "base_exit": r["exit_reason"], "base_net": r["net_rs"],
                             "B2_keep": bool((r["direction"] == "PE" and r["sig_close"] < r["ema9"] and r["ema9"] < r["ema21"]) or (r["direction"] == "CE" and r["sig_close"] > r["ema9"] and r["ema9"] > r["ema21"])),
                             "B3_keep": bool(not ((r["direction"] == "PE" and r["rsi14"] <= 30) or (r["direction"] == "CE" and r["rsi14"] >= 70)))})
        for r in la_rows:
            out_rows.append({"track": f"(lA) {sym}", "date": r["date"], "direction": r["direction"], "signal_time": r["signal_time"],
                             "sig_close": r["sig_close"], "ema9": r["ema9"], "ema21": r["ema21"], "rsi14": r["rsi14"], "atr14": r["atr14"],
                             "base_exit": r["day_exit"], "base_net": r["day_net"],
                             "B2_keep": bool(r["sig_close"] < r["ema9"] and r["ema9"] < r["ema21"]),
                             "B3_keep": bool(not (r["rsi14"] <= 30)), "morning_net": r["morning_net"], "morning_exit": r["morning_exit"],
                             "ext_orl": r["ext_orl"], "b6_partial_survives": r["b6_partial_survives"]})
        report[f"Skill {sym} B6 rejects"] = b6_rejects
        report[f"Skill {sym} B6 kept"] = b6
        report[f"Skill {sym} B4 detail"] = b4
        report[f"(lA) {sym} B4 morning detail"] = b4la
        report[f"(lA) {sym} detail"] = la_rows
    print("\n=== SUMMARY ===")
    print(json.dumps(report, indent=2, default=str))
    pd.DataFrame(out_rows).to_csv(os.path.expanduser("~/workspace/trading/index_options_familyB_indicators_detail.csv"), index=False)
    with open("/tmp/familyB_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

if __name__ == "__main__":
    main()
