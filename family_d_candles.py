"""Family D — DIFFERENT CANDLES, index OPTIONS, paper only, no orders.
FROZEN BEFORE SCORING (written before any D number was computed):
- Window: full October 2026, 1-28 Oct, 18 trading days. Nifty and Bank
  separately, never pooled, never deduped across indices/versions.
- Unit: spot provisional = points x 100 shares - Rs 40 per leg, labelled
  NOT an options-lot profit and NOT a futures profit. Premiums NOT
  computed here (no live-browser route in this subagent; option candles
  in workspace are Bank-only 5-min and do not cover all D trades) —
  premium gap stated, never converted from spot.
- Room floor: D-primary admits NO trade with room ratio < 1.5
  (room / (200*scale) >= 1.5, i.e. room >= 300*scale). This is a
  TIGHTENING vs base floors (base (lA)/V4/Skill-filtered = 1.0; base S1
  had no room filter). A sensitivity row with base room rules is shown
  alongside, so the pure candle effect is visible separately from the
  candle+1.5-room effect. Room is never loosened below 1.5 in primary.
- Grids (all from the progressive 5-min spot cache unless stated):
  * 5-min base: as cached, labels 09:15..15:25.
  * 15-min: aggregate consecutive 3x5-min bars anchored 09:15
    (labels 09:15,09:30,...,15:15; 09:15 bucket == the 5-min OR exactly;
    15:00 bucket close == 15:10 5-min close exactly). OR = bars <09:30
    (single 09:15 bucket). Signal windows use labels: OR signals
    09:30..11:30, (lA) rescan ..13:30 (L1), V4 setups ..11:30 (setup2)
    / ..14:30 (setup3/4). COARSENING FLAGGED: a 15-min bucket labelled
    HH:MM covers HH:MM..HH:MM+15, so window edges extend up to 15 min
    past the 5-min edge (e.g. 11:30 bucket closes ~11:45).
  * 1-min: TRUE 1-min data only — workspace data/1min has ONLY
    2026-10-08 and 2026-10-23 per index. No 1-min bars are invented.
    1-min replay covers those 2 days only (subset, no /week extrapolation).
  * 3-min: CANNOT be built from 5-min bars (a 5-min bar cannot be split
    into 3-min bars without inventing intra-bar data). October-wide
    3-min is therefore NOT scored. Genuine 3-min bars ARE built by
    aggregating the true 1-min files for 8 & 23 Oct only (subset).
- Replay conventions (all grids, mirroring base engines):
  * Entry = next bar open after signal. Stop checked BEFORE target on
    every bar including the entry bar. Square-off at the close of the
    grid bar containing 15:10: 5-min label 15:10, 15-min label 15:00
    (close == 15:10 5-min close), 1-min label 15:10, 3-min label 15:09
    (bucket 15:09-15:12, close == 15:11 1-min close; flagged).
  * Skill: OR-only signal (first close beyond ORH/ORL, 09:30..11:30).
    Outcome: CE stop = entry-(entry-sig low), target = entry+2*risk;
    PE stop = entry+(sig high-entry), target = entry-2*risk.
    S1 blocks: CE blocked on bearish-bias day (prev close position
    <35%); a signal bar labelled 09:30 for PE taken ONLY if its close
    < PDL. D-primary adds room ratio >= 1.5; sensitivity = S1 only.
  * (lA) L1: confirmer break = first confirmer bar 09:30..11:30 with
    close < confirmer OR low (OR-low only, mirroring bn_break_time
    mode 'orl' / nifty_break_time). Rescan = first traded-index bar
    >= confirmer break, <= 13:30, close < OR low AND < PDL,
    OR width <= 360*scale, room >= 300*scale (primary) / >= 200*scale
    (sensitivity). Morning PE replay: entry next open, stop = signal
    high, target = entry-2*risk. Re-entry (only after morning stop):
    scan_reentry 'lA' — candidates close < OR low, risk in
    [10, rescan risk], morning (<=11:30) skip band-fails, afternoon
    (>11:30) first band-fail ends scan, window <= 15:05 (grid label
    rule: 15-min last candidate label 15:00, 3-min 15:03), Rs 40/leg.
    Day net = morning + re-entry; counted as ONE day-trade.
  * V4: find_signal ported verbatim in logic (setup4 reclaim/pullback,
    setup2 OR break, setup3 bounce rejection; internal room >= 200*
    scale per setup; bias-allowed directions; setup2 OR width cap,
    setup3 wide-OR + bearish). Replay: stop = signal low (CE) / high
    (PE) directly, target = entry +/- 2*|entry-stop|. D-primary adds
    room ratio >= 1.5 post-signal; sensitivity = find_signal as-is.
  * V5-15min: pool = V4-15min (primary) + Skill-15min FILTERED variant
    (base V5 pool used filtered Skill, not S1: bias-allowed, CE sig
    close < PDH, PE sig close < PDL, room ratio >= 1.5 primary),
    dedup same symbol+date by setup rank (setup4=3, setup3=2,
    setup2=1, skill=0), prospective target net >= Rs 500, cap max 1
    trade per index track per ISO week, ranked setup_rank,
    bias_strong, room_ratio, target_net.
  * Volrix: daily-close trigger, candle-invariant. October scan in
    base report: 0 triggers (min prev-day close -1.64% Nifty,
    -1.16% Bank, both above -2%). Not re-scored as trades on any grid.
- Frequency: trades / 18 days x 5 for full-October tracks. 1-min/3-min
  subsets: trades on 2 days only, NO weekly rate claimed.
- Audit (1-min question): for every base 5-min trade leg, classify the
  exit bar: entry-bar exit? exit bar touched ONLY the exit level, or
  BOTH stop and target (ordering ambiguous under 5-min bars)? A stop
  on a bar touching only the stop is definitively real at any finer
  grid; a both-levels bar is ambiguous (base convention: stop first).
"""
import os, sys, math, json
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
ONE_MIN = os.path.expanduser("~/workspace/trading/data/1min")
QTY, COST = 100, 40.0
OCT_DAYS = ["2026-10-01", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08",
            "2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15",
            "2026-10-16", "2026-10-19", "2026-10-21", "2026-10-22", "2026-10-23",
            "2026-10-26", "2026-10-27", "2026-10-28"]
SUBSET_DAYS = ["2026-10-08", "2026-10-23"]
SQ = {"5m": "15:10", "15m": "15:00", "1m": "15:10", "3m": "15:09"}


def load(sym):
    spot = pd.read_csv(os.path.join(BASE, sym, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, sym, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")


def day_bars(spot, daily, ds):
    """Return (list-of-dict 5-min bars, pdh, pdc, pdl, bias, scale) or None."""
    d = pd.Timestamp(ds)
    day = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day.empty or prev.empty:
        return None
    y = prev.iloc[-1]
    pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    bars = [{"time": r["time"], "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"])} for _, r in day.iterrows()]
    return bars, pdh, pdc, pdl, bias, scale


def agg(bars, n):
    """Aggregate consecutive n bars (n must divide the bar count per bucket
    only in the 5m->15m case; for 1m->3m the day has 375 bars = 125x3)."""
    out = []
    for i in range(0, len(bars) - n + 1, n):
        w = bars[i:i + n]
        out.append({"time": w[0]["time"], "open": w[0]["open"],
                    "high": max(x["high"] for x in w), "low": min(x["low"] for x in w),
                    "close": w[-1]["close"]})
    return out


def load_1m(sym, ds):
    df = pd.read_csv(os.path.join(ONE_MIN, sym, f"spot_1m_{ds}.csv"))
    df["time"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M")
    df = df.sort_values("time").reset_index(drop=True)
    return [{"time": r["time"], "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"])} for _, r in df.iterrows()]


def or_levels(bars):
    oc = [b for b in bars if b["time"] < "09:30"]
    return max(b["high"] for b in oc), min(b["low"] for b in oc)


def room_ratio(sig_close, direction, pdh, pdc, pdl, scale):
    levels = sorted(set([pdh, pdc, pdl]))
    if direction == "CE":
        nxt = [l for l in levels if l > sig_close]
        room = (min(nxt) - sig_close) if nxt else math.inf
    else:
        nxt = [l for l in levels if l < sig_close]
        room = (sig_close - max(nxt)) if nxt else math.inf
    return (room / (200 * scale) if scale else 0.0), room


def replay(bars, start_idx, entry, stop, target, direction, grid):
    """Generic stop-first replay. Returns dict with exit, exit_time,
    exit_is_entry_bar, exit_bar_both_levels, net."""
    risk = (entry - stop) if direction == "CE" else (stop - entry)
    if risk <= 0:
        return {"exit": "invalid_risk", "exit_time": None, "net": None,
                "exit_is_entry_bar": None, "exit_bar_both": None, "risk": round(risk, 2)}
    sq = SQ[grid]
    for j in range(start_idx, len(bars)):
        b = bars[j]
        hi, lo, cl = b["high"], b["low"], b["close"]
        if direction == "CE":
            hit_stop = lo <= stop
            hit_tgt = hi >= target
            if hit_stop or hit_tgt:
                both = hit_stop and hit_tgt
                ex, price = ("stop", stop) if hit_stop else ("target", target)
                return {"exit": ex, "exit_time": b["time"], "exit_price": price,
                        "net": round((price - entry) * QTY - COST, 2) if ex == "target"
                        else round(-risk * QTY - COST, 2),
                        "exit_is_entry_bar": j == start_idx, "exit_bar_both": both,
                        "risk": round(risk, 2)}
        else:
            hit_stop = hi >= stop
            hit_tgt = lo <= target
            if hit_stop or hit_tgt:
                both = hit_stop and hit_tgt
                ex, price = ("stop", stop) if hit_stop else ("target", target)
                return {"exit": ex, "exit_time": b["time"], "exit_price": price,
                        "net": round((entry - price) * QTY - COST, 2) if ex == "target"
                        else round(-risk * QTY - COST, 2),
                        "exit_is_entry_bar": j == start_idx, "exit_bar_both": both,
                        "risk": round(risk, 2)}
        if b["time"] == sq:
            d = 1 if direction == "CE" else -1
            return {"exit": "square_off", "exit_time": b["time"], "exit_price": cl,
                    "net": round(d * (cl - entry) * QTY - COST, 2),
                    "exit_is_entry_bar": j == start_idx, "exit_bar_both": False,
                    "risk": round(risk, 2)}
    b = bars[-1]
    d = 1 if direction == "CE" else -1
    return {"exit": "square_off", "exit_time": b["time"], "exit_price": b["close"],
            "net": round(d * (b["close"] - entry) * QTY - COST, 2),
            "exit_is_entry_bar": False, "exit_bar_both": False, "risk": round(risk, 2)}


def skill_outcome(bars, sig_idx, direction, grid):
    """Skill outcome: entry next open, stop entry-adjusted from signal extreme."""
    post = [b for b in bars if b["time"] >= "09:30"]
    # sig_idx is index into post
    if sig_idx + 1 >= len(post):
        return None
    sig = post[sig_idx]
    entry = post[sig_idx + 1]["open"]
    if direction == "CE":
        stop = entry - (entry - sig["low"])
        target = entry + 2 * (entry - stop)
    else:
        stop = entry + (sig["high"] - entry)
        target = entry - 2 * (stop - entry)
    if entry == stop:
        return None
    r = replay(post, sig_idx + 1, entry, stop, target, direction, grid)
    r.update({"entry": entry, "stop": stop, "target": round(target, 2),
              "signal": sig["time"]})
    return r


def find_skill_or(bars):
    orh, orl = or_levels(bars)
    post = [b for b in bars if b["time"] >= "09:30"]
    for i, b in enumerate(post):
        if b["time"] > "11:30":
            break
        if b["close"] > orh:
            return "or_breakout", "CE", i, b
        if b["close"] < orl:
            return "or_breakdown", "PE", i, b
    return None, None, None, None


def skill_s1(bars, pdh, pdc, pdl, bias, scale, grid, room_floor):
    """Returns (trade_dict_or_None, blocked_reason_or_None)."""
    setup, direction, sig_idx, sig = find_skill_or(bars)
    if setup is None:
        return None, None
    if direction == "CE" and bias == "bearish":
        return None, "S1_CE_bearish"
    if direction == "PE" and sig["time"] == "09:30" and not (sig["close"] < pdl):
        return None, "S1_0930_PE_not_below_PDL"
    if room_floor is not None:
        rr, _ = room_ratio(sig["close"], direction, pdh, pdc, pdl, scale)
        if rr < room_floor:
            return None, f"room_ratio_{rr:.2f}<{room_floor}"
    out = skill_outcome(bars, sig_idx, direction, grid)
    if out is None:
        return None, "invalid_risk"
    out.update({"setup": setup, "direction": direction, "room_ratio":
                round(room_ratio(sig["close"], direction, pdh, pdc, pdl, scale)[0], 3)})
    return out, None


def skill_filtered(bars, pdh, pdc, pdl, bias, scale, grid, room_floor):
    """Base V5-pool Skill filter: bias-allowed, CE sig_close < PDH,
    PE sig_close < PDL, room ratio >= floor."""
    setup, direction, sig_idx, sig = find_skill_or(bars)
    if setup is None:
        return None, None
    allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
    if direction not in allowed:
        return None, "bias_block"
    if direction == "CE" and not (sig["close"] < pdh):
        return None, "CE_not_below_PDH"
    if direction == "PE" and not (sig["close"] < pdl):
        return None, "PE_not_below_PDL"
    rr, _ = room_ratio(sig["close"], direction, pdh, pdc, pdl, scale)
    if rr < room_floor:
        return None, f"room_ratio_{rr:.2f}<{room_floor}"
    out = skill_outcome(bars, sig_idx, direction, grid)
    if out is None:
        return None, "invalid_risk"
    out.update({"setup": setup, "direction": direction, "room_ratio": round(rr, 3)})
    return out, None


def find_v4(bars, pdh, pdc, pdl, bias, scale):
    """Port of daytrader_cash_backtest.find_signal to dict bars."""
    allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
    orh, orl = or_levels(bars)
    or_width = orh - orl
    post = [b for b in bars if b["time"] >= "09:30"]
    levels = sorted(set([pdh, pdc, pdl]))
    day_open = bars[0]["open"]
    reclaimed = None
    bounced = False
    for i, c in enumerate(post):
        t = c["time"]
        if t > "14:30":
            break
        close, high, low, opn = c["close"], c["high"], c["low"], c["open"]
        prev_close = post[i - 1]["close"] if i > 0 else opn
        if day_open < pdc and day_open < pdl and reclaimed is None:
            if close > orh and close > pdc and close > pdl:
                reclaimed = close
        if reclaimed is not None and "CE" in allowed:
            for lvl in (pdc, pdl):
                if abs(low - lvl) <= 40 * scale and close > lvl and close > opn:
                    nxt = [l for l in levels if l > close]
                    room = (min(nxt) - close) if nxt else math.inf
                    if room >= 200 * scale:
                        return "setup4_pullback", "CE", i, c
        if day_open < pdc and "CE" in allowed and close > orh and close > pdc and close < pdh:
            nxt = [l for l in levels if l > close]
            room = (min(nxt) - close) if nxt else math.inf
            if room >= 200 * scale:
                return "setup4_reclaim", "CE", i, c
        if or_width <= 360 * scale and t <= "11:30":
            if close > orh and close < pdh and "CE" in allowed:
                res = [l for l in [pdh, pdc, pdl] if l > prev_close]
                if not res or close > min(res):
                    nxt = [l for l in levels if l > close]
                    room = (min(nxt) - close) if nxt else math.inf
                    if room >= 200 * scale:
                        return "setup2_or_breakout", "CE", i, c
            if close < orl and close < pdl and "PE" in allowed:
                nxt = [l for l in levels if l < close]
                room = (close - max(nxt)) if nxt else math.inf
                if room >= 200 * scale:
                    return "setup2_or_breakdown", "PE", i, c
        if orh <= high <= orh + 100 * scale:
            bounced = True
        if or_width >= 400 * scale and bias == "bearish" and "PE" in allowed:
            if bounced and close < opn and close < orh:
                blocking = pdc if close > pdc else pdl
                room = close - blocking
                if room >= 200 * scale:
                    return "setup3_bounce_rejection", "PE", i, c
    return None, None, None, None


def v4_trade(bars, pdh, pdc, pdl, bias, scale, grid, room_floor):
    setup, direction, sig_idx, sig = find_v4(bars, pdh, pdc, pdl, bias, scale)
    if setup is None:
        return None, None
    if room_floor is not None:
        rr, _ = room_ratio(sig["close"], direction, pdh, pdc, pdl, scale)
        if rr < room_floor:
            return None, f"room_ratio_{rr:.2f}<{room_floor}"
    post = [b for b in bars if b["time"] >= "09:30"]
    if sig_idx + 1 >= len(post):
        return None, "no_next_bar"
    entry = post[sig_idx + 1]["open"]
    stop = sig["low"] if direction == "CE" else sig["high"]
    risk = (entry - stop) if direction == "CE" else (stop - entry)
    if risk <= 0:
        return None, "invalid_risk"
    target = entry + 2 * risk if direction == "CE" else entry - 2 * risk
    r = replay(post, sig_idx + 1, entry, stop, target, direction, grid)
    r.update({"setup": setup, "direction": direction, "signal": sig["time"],
              "entry": entry, "stop": stop, "target": round(target, 2),
              "room_ratio": round(room_ratio(sig["close"], direction, pdh, pdc, pdl, scale)[0], 3)})
    return r, None


def confirmer_break(bars):
    """First bar 09:30..11:30 with close < confirmer OR low (OR-low only)."""
    _, orl = or_levels(bars)
    for b in bars:
        if "09:30" <= b["time"] <= "11:30" and b["close"] < orl:
            return b["time"], orl
    return None, orl


def la_trade(bars, conf_bars, pdh, pdc, pdl, bias, scale, grid, room_floor):
    """(lA) L1: rescan <= 13:30, re-entry 'lA'. Returns day dict or None."""
    bt, _ = confirmer_break(conf_bars)
    if bt is None:
        return None, "no_confirmer_break"
    orh, orl = or_levels(bars)
    or_width = orh - orl
    levels = sorted(set([pdh, pdc, pdl]))
    post = [b for b in bars if b["time"] >= "09:30"]
    sig_idx = None
    for i, b in enumerate(post):
        t = b["time"]
        if t > "13:30" or t < bt:
            continue
        cl = b["close"]
        if cl < orl and cl < pdl:
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                sig_idx = i
                break
    if sig_idx is None:
        return None, "no_rescan"
    sig = post[sig_idx]
    if room_floor is not None:
        rr, _ = room_ratio(sig["close"], "PE", pdh, pdc, pdl, scale)
        if rr < room_floor:
            return None, f"room_ratio_{rr:.2f}<{room_floor}"
    if sig_idx + 1 >= len(post):
        return None, "no_next_bar"
    entry = post[sig_idx + 1]["open"]
    stop = sig["high"]
    risk = stop - entry
    target = entry - 2 * risk
    m = replay(post, sig_idx + 1, entry, stop, target, "PE", grid)
    if m["net"] is None:
        return None, "invalid_risk"
    m.update({"signal": sig["time"], "entry": entry, "stop": stop,
              "target": round(target, 2), "confirmer_break": bt})
    if m["exit"] != "stop":
        return {"morning": m, "re": None, "day_net": m["net"],
                "signal": sig["time"], "confirmer_break": bt}, None
    # re-entry scan 'lA'
    exit_idx = next(i for i, b in enumerate(post) if b["time"] == m["exit_time"])
    re = None
    skipped = []
    for k in range(exit_idx + 1, len(post)):
        c = post[k]
        t = c["time"]
        if t > "15:05":
            break
        if c["close"] >= orl:
            continue
        if k + 1 >= len(post):
            skipped.append((t, "no_next_bar"))
            break
        rentry = post[k + 1]["open"]
        rstop = c["high"]
        rrisk = rstop - rentry
        afternoon = t > "11:30"
        band_ok = rrisk > 0 and 10 <= rrisk <= risk
        if afternoon and not band_ok:
            skipped.append((t, f"afternoon_first_fail_risk={rrisk:.2f}"))
            break
        if not band_ok:
            skipped.append((t, f"band_fail_risk={rrisk:.2f}"))
            continue
        re = replay(post, k + 1, rentry, rstop, rentry - 2 * rrisk, "PE", grid)
        re.update({"re_signal": t, "entry": rentry, "stop": rstop,
                   "target": round(rentry - 2 * rrisk, 2)})
        break
    day_net = round(m["net"] + re["net"], 2) if (re and re["net"] is not None) else m["net"]
    return {"morning": m, "re": re, "day_net": day_net,
            "signal": sig["time"], "confirmer_break": bt}, None


def summarise(rows):
    """rows: list of dicts with net + exit (day or single-trade)."""
    rows = [r for r in rows if r is not None]
    if not rows:
        return {"trades": 0, "targets": 0, "stops": 0, "square_offs": 0,
                "green": 0, "net": 0.0, "per_week": 0.0}
    net = round(sum(r["net"] for r in rows), 2)
    return {"trades": len(rows),
            "targets": sum(1 for r in rows if r["exit"] == "target"),
            "stops": sum(1 for r in rows if r["exit"] == "stop"),
            "square_offs": sum(1 for r in rows if r["exit"] == "square_off"),
            "green": sum(1 for r in rows if r["net"] > 0),
            "net": net, "per_week": round(len(rows) / 18 * 5, 2)}


def main():
    data = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        spot, daily = load(sym)
        data[sym] = (spot, daily)
    other = {"NIFTY": "BANKNIFTY", "BANKNIFTY": "NIFTY"}

    def day_grids(sym, ds):
        """Return dict grid -> (bars, pdh, pdc, pdl, bias, scale), plus conf grids."""
        spot, daily = data[sym]
        d5 = day_bars(spot, daily, ds)
        if d5 is None:
            return None
        bars5, pdh, pdc, pdl, bias, scale = d5
        out = {"5m": (bars5, pdh, pdc, pdl, bias, scale),
               "15m": (agg(bars5, 3), pdh, pdc, pdl, bias, scale)}
        if ds in SUBSET_DAYS:
            b1 = load_1m(sym, ds)
            out["1m"] = (b1, pdh, pdc, pdl, bias, scale)
            out["3m"] = (agg(b1, 3), pdh, pdc, pdl, bias, scale)
        return out

    def conf_grids(sym, ds, grid):
        spot, daily = data[sym]
        d5 = day_bars(spot, daily, ds)
        if d5 is None:
            return None
        bars5 = d5[0]
        if grid == "5m":
            return bars5
        if grid == "15m":
            return agg(bars5, 3)
        if grid == "1m":
            return load_1m(sym, ds)
        if grid == "3m":
            return agg(load_1m(sym, ds), 3)
        return None

    # ---------- VERIFICATION: 5-min reproduction vs base CSV ----------
    base_skill = {  # (index, date) -> net, from index_options_v2_october_trades.csv (taken only)
        ("NIFTY", "2026-10-05"): -2220.0, ("NIFTY", "2026-10-06"): 4240.0,
        ("NIFTY", "2026-10-07"): -2725.0, ("NIFTY", "2026-10-08"): 5440.0,
        ("NIFTY", "2026-10-12"): -4605.0, ("NIFTY", "2026-10-26"): 16550.0,
        ("NIFTY", "2026-10-27"): -2790.0, ("NIFTY", "2026-10-28"): -5470.0,
        ("BANKNIFTY", "2026-10-01"): 16640.0, ("BANKNIFTY", "2026-10-05"): 25690.0,
        ("BANKNIFTY", "2026-10-06"): -1435.0, ("BANKNIFTY", "2026-10-07"): -7475.0,
        ("BANKNIFTY", "2026-10-08"): -11070.0, ("BANKNIFTY", "2026-10-12"): -4640.0,
        ("BANKNIFTY", "2026-10-14"): -16660.0, ("BANKNIFTY", "2026-10-23"): 14860.0,
        ("BANKNIFTY", "2026-10-27"): -7235.0}
    base_la = {("NIFTY", "2026-10-08"): 11690.0, ("NIFTY", "2026-10-21"): 4940.0,
               ("NIFTY", "2026-10-23"): 11390.0, ("BANKNIFTY", "2026-10-07"): -7475.0,
               ("BANKNIFTY", "2026-10-08"): -8510.0, ("BANKNIFTY", "2026-10-21"): 20200.0,
               ("BANKNIFTY", "2026-10-23"): 24060.0}
    base_v4 = {("NIFTY", "2026-10-26"): -8635.0, ("NIFTY", "2026-10-08"): 5440.0,
               ("NIFTY", "2026-10-23"): 11390.0, ("BANKNIFTY", "2026-10-01"): 16640.0,
               ("BANKNIFTY", "2026-10-26"): 10520.0, ("BANKNIFTY", "2026-10-13"): -3730.0,
               ("BANKNIFTY", "2026-10-21"): 20200.0}
    print("=== VERIFICATION 5-min reproduction vs base CSV ===")
    audit = []  # per-leg audit rows for base trades
    for sym in ("NIFTY", "BANKNIFTY"):
        for ds in OCT_DAYS:
            g = day_grids(sym, ds)
            bars, pdh, pdc, pdl, bias, scale = g["5m"]
            tr, blk = skill_s1(bars, pdh, pdc, pdl, bias, scale, "5m", None)
            if tr is not None:
                exp = base_skill.get((sym, ds))
                flag = "" if exp is None or abs(tr["net"] - exp) < 0.01 else "  <-- MISMATCH"
                print(f"SKILL-S1 5m {sym} {ds} sig={tr['signal']} {tr['direction']} "
                      f"exit={tr['exit']}@{tr['exit_time']} net={tr['net']} base={exp}{flag}")
                audit.append({"track": "Skill S1", "index": sym, "date": ds, "leg": "single",
                              "exit": tr["exit"], "exit_time": tr["exit_time"],
                              "entry_bar": tr["exit_is_entry_bar"], "both": tr["exit_bar_both"],
                              "net": tr["net"]})
            vt, _ = v4_trade(bars, pdh, pdc, pdl, bias, scale, "5m", None)
            if vt is not None:
                exp = base_v4.get((sym, ds))
                flag = "" if exp is None or abs(vt["net"] - exp) < 0.01 else "  <-- MISMATCH"
                print(f"V4 5m {sym} {ds} {vt['setup']} {vt['direction']} sig={vt['signal']} "
                      f"exit={vt['exit']}@{vt['exit_time']} net={vt['net']} base={exp}{flag}")
                audit.append({"track": "V4", "index": sym, "date": ds, "leg": "single",
                              "exit": vt["exit"], "exit_time": vt["exit_time"],
                              "entry_bar": vt["exit_is_entry_bar"], "both": vt["exit_bar_both"],
                              "net": vt["net"]})
            conf = conf_grids(other[sym], ds, "5m")
            la, _ = la_trade(bars, conf, pdh, pdc, pdl, bias, scale, "5m", None)
            if la is not None:
                exp = base_la.get((sym, ds))
                flag = "" if exp is None or abs(la["day_net"] - exp) < 0.01 else "  <-- MISMATCH"
                m = la["morning"]
                print(f"(lA)-L1 5m {sym} {ds} sig={la['signal']} conf={la['confirmer_break']} "
                      f"morn={m['exit']}@{m['exit_time']} net={m['net']} "
                      f"re={la['re']['exit'] + '@' + la['re']['re_signal'] + ' net=' + str(la['re']['net']) if la['re'] else None} "
                      f"day={la['day_net']} base={exp}{flag}")
                audit.append({"track": "(lA) L1", "index": sym, "date": ds, "leg": "morning",
                              "exit": m["exit"], "exit_time": m["exit_time"],
                              "entry_bar": m["exit_is_entry_bar"], "both": m["exit_bar_both"],
                              "net": m["net"]})
                if la["re"]:
                    audit.append({"track": "(lA) L1", "index": sym, "date": ds, "leg": "re-entry",
                                  "exit": la["re"]["exit"], "exit_time": la["re"]["exit_time"],
                                  "entry_bar": la["re"]["exit_is_entry_bar"],
                                  "both": la["re"]["exit_bar_both"], "net": la["re"]["net"]})
    print("\n=== AUDIT: base 5-min legs — entry-bar exit? both stop+target in exit bar? ===")
    for a in audit:
        print(a)
    n_both = sum(1 for a in audit if a["both"])
    n_entry = sum(1 for a in audit if a["entry_bar"])
    n_stop = sum(1 for a in audit if a["exit"] == "stop")
    n_stop_both = sum(1 for a in audit if a["exit"] == "stop" and a["both"])
    n_stop_entry = sum(1 for a in audit if a["exit"] == "stop" and a["entry_bar"])
    print(f"AUDIT SUMMARY legs={len(audit)} stops={n_stop} stops_on_entry_bar={n_stop_entry} "
          f"stops_on_both_levels_bar={n_stop_both} any_both_levels_bar={n_both} "
          f"any_entry_bar_exit={n_entry}")

    # ---------- 1-min + 3-min subsets (8 & 23 Oct, genuine data only) ----------
    print("\n=== 1-MIN REPLAY (genuine 1-min files, 8 & 23 Oct only) vs 5-min same day ===")
    for sym in ("NIFTY", "BANKNIFTY"):
        for ds in SUBSET_DAYS:
            g = day_grids(sym, ds)
            for grid in ("1m", "3m"):
                bars, pdh, pdc, pdl, bias, scale = g[grid]
                tr, blk = skill_s1(bars, pdh, pdc, pdl, bias, scale, grid, None)
                print(f"SKILL-S1 {grid} {sym} {ds} -> "
                      f"{tr['signal'] + ' ' + tr['direction'] + ' ' + tr['exit'] + '@' + tr['exit_time'] + ' net=' + str(tr['net']) if tr else 'NO_TRADE blocked=' + str(blk)}")
                conf = conf_grids(other[sym], ds, grid)
                la, lblk = la_trade(bars, conf, pdh, pdc, pdl, bias, scale, grid, None)
                print(f"(lA)-L1 {grid} {sym} {ds} -> "
                      f"{'sig=' + la['signal'] + ' conf=' + la['confirmer_break'] + ' morn=' + la['morning']['exit'] + '@' + la['morning']['exit_time'] + ' net=' + str(la['morning']['net']) + ' re=' + (la['re']['exit'] + '@' + la['re']['re_signal'] + ' net=' + str(la['re']['net']) if la['re'] else 'None') + ' day=' + str(la['day_net']) if la else 'NO_TRADE blocked=' + str(lblk)}")
                vt, _ = v4_trade(bars, pdh, pdc, pdl, bias, scale, grid, None)
                print(f"V4 {grid} {sym} {ds} -> "
                      f"{vt['setup'] + ' ' + vt['direction'] + ' sig=' + vt['signal'] + ' ' + vt['exit'] + '@' + vt['exit_time'] + ' net=' + str(vt['net']) if vt else 'NO_TRADE'}")

    # ---------- 15-min full October ----------
    print("\n=== 15-MIN full October (primary room>=1.5 + sensitivity base room) ===")
    results = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        for label, fn, room in (
                ("Skill-S1-15m-primary", "s1", 1.5), ("Skill-S1-15m-sens", "s1", None),
                ("(lA)-L1-15m-primary", "la", 1.5), ("(lA)-L1-15m-sens", "la", None),
                ("V4-15m-primary", "v4", 1.5), ("V4-15m-sens", "v4", None)):
            rows, blocked = [], []
            for ds in OCT_DAYS:
                g = day_grids(sym, ds)
                bars, pdh, pdc, pdl, bias, scale = g["15m"]
                if fn == "s1":
                    tr, blk = skill_s1(bars, pdh, pdc, pdl, bias, scale, "15m", room)
                    if tr is not None:
                        rows.append({"date": ds, "net": tr["net"], "exit": tr["exit"],
                                     "signal": tr["signal"], "direction": tr["direction"],
                                     "setup": tr["setup"]})
                    elif blk:
                        blocked.append((ds, blk))
                elif fn == "la":
                    conf = conf_grids(other[sym], ds, "15m")
                    la, blk = la_trade(bars, conf, pdh, pdc, pdl, bias, scale, "15m", room)
                    if la is not None:
                        rows.append({"date": ds, "net": la["day_net"],
                                     "exit": la["morning"]["exit"],
                                     "signal": la["signal"], "direction": "PE",
                                     "setup": "la_pe_rescan_reentry_L1",
                                     "morning_exit": la["morning"]["exit"],
                                     "morning_net": la["morning"]["net"],
                                     "re_exit": la["re"]["exit"] if la["re"] else None,
                                     "re_net": la["re"]["net"] if la["re"] else None})
                    elif blk:
                        blocked.append((ds, blk))
                else:
                    vt, blk = v4_trade(bars, pdh, pdc, pdl, bias, scale, "15m", room)
                    if vt is not None:
                        rows.append({"date": ds, "net": vt["net"], "exit": vt["exit"],
                                     "signal": vt["signal"], "direction": vt["direction"],
                                     "setup": vt["setup"]})
                    elif blk:
                        blocked.append((ds, blk))
            s = summarise(rows)
            results[f"{label} {sym}"] = {"summary": s, "rows": rows, "blocked": blocked}
            print(f"{label} {sym}: trades={s['trades']} T={s['targets']} S={s['stops']} "
                  f"SQ={s['square_offs']} green={s['green']} net={s['net']} /week={s['per_week']}")
            for r in rows:
                print(f"   {r['date']} {r['setup']} {r['direction']} sig={r['signal']} "
                      f"exit={r['exit']} net={r['net']} "
                      f"{'(morn ' + str(r.get('morning_net')) + ' re ' + str(r.get('re_net')) + ')' if 'morning_net' in r else ''}")
            print(f"   blocked/no-trade reasons: {blocked}")
        # V5-15min primary (pool V4-15 primary + Skill-filtered-15 primary)
        pool = []
        for ds in OCT_DAYS:
            g = day_grids(sym, ds)
            bars, pdh, pdc, pdl, bias, scale = g["15m"]
            wk = pd.Timestamp(ds).isocalendar()
            wkstr = f"{wk[0]}-W{wk[1]:02d}"
            vt, _ = v4_trade(bars, pdh, pdc, pdl, bias, scale, "15m", 1.5)
            if vt is not None:
                dirc = 1 if vt["direction"] == "CE" else -1
                pool.append({"symbol": sym, "date": ds, "week": wkstr, "method": "V4",
                             "setup": vt["setup"], "direction": vt["direction"],
                             "exit": vt["exit"], "net": vt["net"],
                             "target_net": round(dirc * (vt["target"] - vt["entry"]) * QTY - COST, 2),
                             "setup_rank": {"setup4_reclaim": 3, "setup4_pullback": 3,
                                            "setup3_bounce_rejection": 2,
                                            "setup2_or_breakout": 1,
                                            "setup2_or_breakdown": 1}.get(vt["setup"], 0),
                             "room_ratio": vt["room_ratio"],
                             "bias_strong": 1 if bias != "neutral" else 0})
            sf, _ = skill_filtered(bars, pdh, pdc, pdl, bias, scale, "15m", 1.5)
            if sf is not None:
                dirc = 1 if sf["direction"] == "CE" else -1
                pool.append({"symbol": sym, "date": ds, "week": wkstr, "method": "SkillFilt",
                             "setup": sf["setup"], "direction": sf["direction"],
                             "exit": sf["exit"], "net": sf["net"],
                             "target_net": round(dirc * (sf["target"] - sf["entry"]) * QTY - COST, 2),
                             "setup_rank": 0, "room_ratio": sf["room_ratio"],
                             "bias_strong": 1 if bias != "neutral" else 0})
        pool = [p for p in pool if p["target_net"] >= 500]
        dedup = {}
        for p in pool:
            k = (p["symbol"], p["date"])
            if k not in dedup or p["setup_rank"] > dedup[k]["setup_rank"]:
                dedup[k] = p
        ranked = sorted(dedup.values(), key=lambda t: (-t["setup_rank"], -t["bias_strong"],
                                                      -t["room_ratio"], -t["target_net"],
                                                      t["date"]))
        picked, seen_week = [], set()
        for p in ranked:
            if p["week"] in seen_week:
                continue
            picked.append(p)
            seen_week.add(p["week"])
        rows = [{"date": p["date"], "net": p["net"], "exit": p["exit"]} for p in picked]
        s = summarise(rows)
        results[f"V5-15m-primary {sym}"] = {"summary": s, "rows": picked, "pool": pool}
        print(f"V5-15m-primary {sym}: pool={len(pool)} dedup={len(dedup)} picked={s['trades']} "
              f"T={s['targets']} S={s['stops']} SQ={s['square_offs']} green={s['green']} "
              f"net={s['net']} /week={s['per_week']}")
        for p in picked:
            print(f"   {p['date']} {p['method']} {p['setup']} {p['direction']} "
                  f"exit={p['exit']} net={p['net']} tnet={p['target_net']}")
    with open(os.path.expanduser("~/workspace/trading/family_d_candles_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/family_d_candles_results.json")


if __name__ == "__main__":
    main()
