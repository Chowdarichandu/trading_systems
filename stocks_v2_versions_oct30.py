#!/usr/bin/env python3
"""Stocks v2 versions, Oct 30 2026. PAPER ONLY, cash intraday only, 100 shares
provisional, Rs 40/trade, square-off 15:10. NO options, NO orders.
Reads ONLY ~/workspace/trading/data/progressive/ cache (ends 2026-10-28).
No fetches, no re-tuning on the scored window. All definitions FROZEN below
before any result is read.

FROZEN DEFINITIONS
V5-stock: pool of V4-baseline trades + Skill-v2 OR-only trades (same tuning
  engine, daytrader_cash_tuning.find_signal, BASE params: ratio 2, stop_scale 1,
  room 0.0036, bias on for V4; skill_or ignores bias/room). Dedup same
  symbol+date: higher setup rank wins (setup4=3 > setup3=2 > setup2=1 >
  skill_or=0), then higher prospective full-target net, then earlier signal.
  Filter: prospective full-target net >= Rs 500 (per 100 shares, provisional).
  1/day cap (portfolio): rank by prospective net desc, setup rank desc,
  signal time asc; top 1 per trading day.
Skill-v2 (FROZEN variant: "Skill-v2 OR-only" from daytrader_tuning_v5_v2_results.md):
  first 5-min close beyond stock OR (09:15-09:30 bars) after 09:30 up to 11:30,
  no bias, no room, no PD check. Entry next bar open, stop = signal-bar extreme
  level (CE: signal low; PE: signal high), target = 2x risk, stop-before-target
  per bar incl. entry bar, square-off 15:10. NOTE: this variant PASSED the
  Jul-Sep capped check in the tuning doc but was NOT ADOPTED (Oct context
  -4,588, cap doing the work). It is frozen here as specified, not re-tuned.
(lA)-v2-stock (adaptation of DOCUMENTED_V5_LA_BANKNIFTY.md (lA), frozen):
  Original: BN-confirmed rescan morning + band-filtered re-entry, morning
  scan-skip to 11:30, afternoon stop-on-first-fail to 15:05, target 2x risk,
  PE-only in original Cluster 1 form.
  Stock adaptation: NIFTY confirms the stock (instead of Bank Nifty confirming
  Nifty); both directions allowed (stocks are not a PE-only cluster); morning
  candidate = earliest pooled V4/Skill-v2 signal for that stock-day with
  signal time >= Nifty break time, <= 11:30, same direction as Nifty's first
  OR break that day (Nifty OR = 09:15-09:30 bars; break = first 09:30+ close
  beyond Nifty OR). Entry next bar open, stop = signal-bar extreme level,
  target 2x risk, stop-before-target, square-off 15:10.
  Re-entry (max 1/stock-day, only if morning trade stops): rescan suffix bars
  after the stop bar with both engines, same direction as morning, risk band
  RELATIVE (adapted: index-point band [10, rescan risk] does not scale to
  rupee stocks) = [0.5x, 1.0x] morning risk. Morning phase (<=11:30): failing
  candidates are skipped, scan continues. Afternoon phase (>11:30): first
  candidate failing the band ENDS the scan (stop-on-first-fail, to 15:05).
  Re-entry replay uses the same exit rules. Re-entry is reported separately.
Volrix-v2-stock (FROZEN, adapted to cash intraday): trigger = previous trading
  day's close <= -2% vs the trading day before it. Entry next session at
  09:15 open, LONG ONLY, exit = 15:10 square-off (15:10 bar close; last bar
  <=15:10 if absent), NO intraday stop/target (pure rebound square-off).
  This exit is frozen here and NOT optimised after seeing results.
  1 lot equivalent = per 100 shares PROVISIONAL ONLY, never a lot profit.
NO-EVENT filter (stock_event_gate_v1_frozen.md window definition): a stock-day
  is NO-EVENT only if it lies OUTSIDE every event window for that stock, where
  a window = 7th trading day before the event date through 7th trading day
  after the effective reaction date, inclusive. Effective reaction =
  reaction_date if within event_date..event_date+7 calendar days, else the
  event date (this drops the 2026-01-01 placeholders on 2025 events). All
  calendar rows (results + large orders, FDA, management, dividends, policy,
  pricing, block deals, corporate actions) count. Volrix is filtered on its
  ENTRY day only (trigger day may itself be an event day; stated).
1/day cap ranking (frozen, no outcome look-ahead): prospective full-target net
  desc, setup rank desc, signal time asc. Volrix has no target: in the
  combined ranking it sorts last; in its own 1/day cap it ranks by
  |previous-day drop| desc (strongest rebound setup first, known at open).
Full-target win = exit_reason == 'target'. Net>0 win = net_rs > 0.
Legs used in the report: 1/day (capped series <= 1 trade/day by construction),
  net positive, full-target rate > 19.7%, month cumulative rising month by
  month, no forcing (no trade on a no-signal day).
"""
import csv, json, math, os, sys
from collections import defaultdict, Counter

sys.path.insert(0, "/home/hatch/workspace/trading")
from daytrader_cash_tuning import find_signal, bias_of

BASE = "/home/hatch/workspace/trading/data/progressive"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
V4P = {"entry_mode": "v4", "room_pct": 0.0036, "bias_on": True, "signal_end": "baseline",
       "target_ratio": 2.0, "stop_scale": 1.0}
SKP = {"entry_mode": "skill_or", "room_pct": 0.0036, "bias_on": True, "signal_end": "baseline",
       "target_ratio": 2.0, "stop_scale": 1.0}
RANK = {"setup4_pullback": 3, "setup4_reclaim": 3, "setup3_bounce_rejection": 2,
        "setup2_or_breakout": 1, "setup2_or_breakdown": 1,
        "skill_or_breakout": 0, "skill_or_breakdown": 0}
LO, HI = "2026-01-01", "2026-10-28"

def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def norm_time(ts):
    # '2026-01-01 09:15:00+05:30' -> '09:15'
    return ts[11:16]

def load_stock(sym):
    spot, daily = {}, []
    for r in load_csv(f"{BASE}/{sym}/spot_5m.csv"):
        d = r["timestamp"][:10]
        spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19],
            "time": norm_time(r["timestamp"]), "open": float(r["open"]),
            "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    for r in load_csv(f"{BASE}/{sym}/spot_daily.csv"):
        daily.append({"date": r["date"][:10], "open": float(r["open"]),
                      "high": float(r["high"]), "low": float(r["low"]),
                      "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot:
        spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

def replay(candles, sig_idx, direction):
    """candles: >=09:30 list; sig_idx index of signal bar. Returns trade dict or None."""
    if sig_idx + 1 >= len(candles):
        return None
    sig = candles[sig_idx]
    entry = float(candles[sig_idx + 1]["open"])
    if direction == "CE":
        stop = float(sig["low"]); risk = entry - stop
        target = entry + 2.0 * risk
    else:
        stop = float(sig["high"]); risk = stop - entry
        target = entry - 2.0 * risk
    if risk == 0:
        return None
    er = ep = et = None; stop_idx = None
    for j in range(sig_idx + 1, len(candles)):
        c = candles[j]
        if direction == "CE":
            if float(c["low"]) <= stop: er, ep, et, stop_idx = "stop", stop, c["timestamp"], j; break
            if float(c["high"]) >= target: er, ep, et = "target", target, c["timestamp"]; break
        else:
            if float(c["high"]) >= stop: er, ep, et, stop_idx = "stop", stop, c["timestamp"], j; break
            if float(c["low"]) <= target: er, ep, et = "target", target, c["timestamp"]; break
        if c["time"] == "15:10": er, ep, et = "square_off", float(c["close"]), c["timestamp"]; break
    if er is None:
        c = candles[-1]; er, ep, et = "square_off", float(c["close"]), c["timestamp"]
    d = 1 if direction == "CE" else -1
    net = round(d * (ep - entry) * 100 - 40.0, 2)
    prosp = round(2.0 * risk * 100 - 40.0, 2)
    return {"entry": entry, "stop": stop, "target": target, "risk": risk,
            "exit_reason": er, "exit_price": ep, "exit_time": et,
            "stop_bar_idx": stop_idx, "net_rs": net, "prospective_net": prosp}

def day_signals(raw, prev):
    """Returns (candles, orh, orl, or_width, day_open, ctx) and engine signals."""
    pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
    bias, _ = bias_of(prev)
    candles = [c for c in raw if c["time"] >= "09:30"]
    or_c = [c for c in raw if c["time"] < "09:30"]
    if not or_c or not candles:
        return None
    orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
    ctx = dict(pdh=pdh, pdc=pdc, pdl=pdl, bias=bias, orh=orh, orl=orl,
               or_width=orh - orl, day_open=raw[0]["open"])
    out = {}
    for name, p in (("v4", V4P), ("skill", SKP)):
        setup, direction, sig = find_signal(candles, orh, orl, orh - orl,
                                            raw[0]["open"], pdh, pdc, pdl, bias, p)
        if setup is None:
            continue
        idx = next((i for i, c in enumerate(candles) if c["timestamp"] == sig["timestamp"]), None)
        if idx is None:
            continue
        out[name] = (setup, direction, sig, idx)
    return candles, ctx, out

# ---------- load all ----------
stocks = {}
for sym in SYMBOLS:
    stocks[sym] = load_stock(sym)
nifty_spot, nifty_daily = load_stock("NIFTY")
trade_days = sorted(d["date"] for d in nifty_daily if LO <= d["date"] <= HI)
trade_day_set = set(trade_days)
n_trading_days = len(trade_day_set)

def nifty_break(day):
    """(direction, break_time) or (None, None) for a NIFTY day."""
    raw = nifty_spot.get(day, [])
    or_c = [c for c in raw if c["time"] < "09:30"]
    candles = [c for c in raw if c["time"] >= "09:30"]
    if not or_c or not candles:
        return None, None
    orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
    for c in candles:
        if c["close"] > orh: return "CE", c["time"]
        if c["close"] < orl: return "PE", c["time"]
    return None, None

# ---------- event windows ----------
def trading_days_list(daily):
    return [d["date"] for d in daily]

def build_windows(sym):
    _, daily = stocks[sym]
    tdays = trading_days_list(daily)
    idx = {d: i for i, d in enumerate(tdays)}
    windows = set()
    from datetime import date, timedelta
    def parse(s):
        return date.fromisoformat(s[:10]) if s else None
    for r in load_csv(f"{OUT}/stock_event_calendar_jan_oct_2026.csv"):
        if r["stock"] != sym:
            continue
        ev = parse(r["event_date"]); react = parse(r["reaction_date"]) if r["reaction_date"] else None
        eff = react if (react and ev and (ev <= react <= ev + timedelta(days=7))) else ev
        ev_s, eff_s = ev.isoformat(), eff.isoformat()
        if ev_s not in idx or eff_s not in idx:
            continue
        a = max(0, idx[ev_s] - 7); b = min(len(tdays) - 1, idx[eff_s] + 7)
        for d in tdays[a:b + 1]:
            windows.add(d)
    return windows

WINDOWS = {sym: build_windows(sym) for sym in SYMBOLS}
def is_noevent(sym, d):
    return d not in WINDOWS[sym]

# ---------- generate version trades ----------
v4_trades, skill_trades, v5_trades, la_trades, volrix_trades = [], [], [], [], []
for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: d for d in daily}
    for day in sorted(spot):
        if not (LO <= day <= HI):
            continue
        prevs = [d for d in daily if d["date"] < day]
        if not prevs:
            continue
        prev = prevs[-1]
        ds = day_signals(spot[day], prev)
        if ds is None:
            continue
        candles, ctx, sigs = ds
        day_trades = {}
        for name, (setup, direction, sig, idx) in sigs.items():
            rp = replay(candles, idx, direction)
            if rp is None:
                continue
            t = {"symbol": sym, "date": day, "version": "v4" if name == "v4" else "skill_v2",
                 "setup": setup, "direction": direction, "signal_time": sig["timestamp"],
                 "entry_price": rp["entry"], "stop_price": rp["stop"],
                 "target_price": rp["target"], "exit_reason": rp["exit_reason"],
                 "exit_price": rp["exit_price"], "exit_time": rp["exit_time"],
                 "net_rs": rp["net_rs"], "prospective_net": rp["prospective_net"],
                 "setup_rank": RANK[setup]}
            day_trades[name] = t
            (v4_trades if name == "v4" else skill_trades).append(t)
        # V5-stock: dedup same symbol+date, rank then prospective then earlier
        if day_trades:
            best = sorted(day_trades.values(),
                          key=lambda t: (-t["setup_rank"], -t["prospective_net"], t["signal_time"]))[0]
            if best["prospective_net"] >= 500:
                v5_trades.append({**best, "version": "v5_stock"})
        # (lA)-v2-stock
        nb_dir, nb_time = nifty_break(day)
        if nb_dir:
            cands = []
            for name, (setup, direction, sig, idx) in sigs.items():
                if direction == nb_dir and sig["timestamp"][11:16] >= nb_time \
                        and sig["timestamp"][11:16] <= "11:30":
                    cands.append((sig["timestamp"], name, setup, direction, sig, idx))
            cands.sort()
            if cands:
                _, mname, msetup, mdir, msig, midx = cands[0]
                rp = replay(candles, midx, mdir)
                if rp is not None:
                    la_trades.append({"symbol": sym, "date": day, "version": "la_v2",
                        "setup": msetup + "|la_morning", "direction": mdir,
                        "signal_time": msig["timestamp"], "entry_price": rp["entry"],
                        "stop_price": rp["stop"], "target_price": rp["target"],
                        "exit_reason": rp["exit_reason"], "exit_price": rp["exit_price"],
                        "exit_time": rp["exit_time"], "net_rs": rp["net_rs"],
                        "prospective_net": rp["prospective_net"],
                        "setup_rank": RANK[msetup], "leg": "morning"})
                    # re-entry only if morning stopped
                    if rp["exit_reason"] == "stop" and rp["stop_bar_idx"] is not None:
                        morn_risk = rp["risk"]
                        suffix_start = rp["stop_bar_idx"] + 1
                        tries = 0
                        while suffix_start < len(candles) and tries < 5:
                            tries += 1
                            suf = candles[suffix_start:]
                            found = None
                            for nm, p in (("v4", V4P), ("skill", SKP)):
                                s2, d2, sg2 = find_signal(
                                    suf, ctx["orh"], ctx["orl"], ctx["or_width"],
                                    ctx["day_open"], ctx["pdh"], ctx["pdc"], ctx["pdl"],
                                    ctx["bias"], p)
                                if s2 is None or d2 != mdir:
                                    continue
                                i2 = next((i for i, c in enumerate(suf)
                                           if c["timestamp"] == sg2["timestamp"]), None)
                                if i2 is not None:
                                    found = (suf[i2]["timestamp"], nm, s2, d2, sg2, i2, suf)
                                    break
                            if found is None:
                                break
                            ts2, nm2, s2, d2, sg2, i2, suf = found
                            # replay on suffix with absolute index mapping
                            abs_idx = suffix_start + i2
                            rp2 = replay(candles, abs_idx, d2)
                            if rp2 is None:
                                break
                            in_band = 0.5 * morn_risk <= rp2["risk"] <= 1.0 * morn_risk
                            if in_band:
                                la_trades.append({"symbol": sym, "date": day, "version": "la_v2",
                                    "setup": s2 + "|la_reentry", "direction": d2,
                                    "signal_time": sg2["timestamp"],
                                    "entry_price": rp2["entry"], "stop_price": rp2["stop"],
                                    "target_price": rp2["target"],
                                    "exit_reason": rp2["exit_reason"],
                                    "exit_price": rp2["exit_price"],
                                    "exit_time": rp2["exit_time"], "net_rs": rp2["net_rs"],
                                    "prospective_net": rp2["prospective_net"],
                                    "setup_rank": RANK[s2], "leg": "reentry"})
                                break
                            else:
                                if ts2[11:16] > "11:30":
                                    break  # afternoon stop-on-first-fail
                                suffix_start = abs_idx + 1  # morning: skip, continue
                                continue
    # Volrix-v2 (uses daily closes + 5m open/15:10 close)
    for i in range(2, len(daily)):
        entry_day = daily[i]["date"]
        if not (LO <= entry_day <= HI):
            continue
        prev, prev2 = daily[i - 1], daily[i - 2]
        ret = prev["close"] / prev2["close"] - 1 if prev2["close"] else 0
        if ret > -0.02:
            continue
        bars = spot.get(entry_day, [])
        if not bars:
            continue
        entry = bars[0]["open"]
        sq = [b for b in bars if b["time"] <= "15:10"]
        if not sq:
            continue
        exitp = sq[-1]["close"]; exitt = sq[-1]["timestamp"]
        volrix_trades.append({"symbol": sym, "date": entry_day, "version": "volrix_v2",
            "setup": "volrix_rebound", "direction": "CE",
            "signal_time": bars[0]["timestamp"], "entry_price": entry,
            "stop_price": "", "target_price": "",
            "exit_reason": "square_off", "exit_price": exitp, "exit_time": exitt,
            "net_rs": round((exitp - entry) * 100 - 40.0, 2),
            "prospective_net": "", "setup_rank": 0, "leg": "",
            "prev_day_return_pct": round(ret * 100, 2)})

ALL = {"v5_stock": v5_trades, "skill_v2": skill_trades, "la_v2": la_trades,
       "volrix_v2": volrix_trades}

def noevent_filter(trades):
    return [t for t in trades if is_noevent(t["symbol"], t["date"])]

def cap_1day(trades, volrix=False):
    byday = defaultdict(list)
    for t in trades:
        byday[t["date"]].append(t)
    out = []
    for d, ts in byday.items():
        if volrix:
            ts = sorted(ts, key=lambda t: (-abs(t.get("prev_day_return_pct", 0)), t["signal_time"]))
        else:
            ts = sorted(ts, key=lambda t: (-t["prospective_net"], -t["setup_rank"], t["signal_time"]))
        out.append(ts[0])
    return sorted(out, key=lambda t: (t["date"], t["signal_time"], t["symbol"]))

def combined_pool(trades_by_version):
    """Dedup same symbol+date across versions, then 1/day."""
    best = {}
    for ver, ts in trades_by_version.items():
        for t in ts:
            k = (t["symbol"], t["date"])
            rank_key = (t["prospective_net"] if t["prospective_net"] != "" else -1e18)
            cur = best.get(k)
            cur_key = (cur["prospective_net"] if cur and cur["prospective_net"] != "" else -1e18)
            if cur is None or rank_key > cur_key:
                best[k] = {**t, "version": "combined", "source_version": ver}
    deduped = sorted(best.values(), key=lambda t: (t["date"], t["signal_time"], t["symbol"]))
    byday = defaultdict(list)
    for t in deduped:
        byday[t["date"]].append(t)
    capped = []
    for d, ts in byday.items():
        ts = sorted(ts, key=lambda t: (-(t["prospective_net"] if t["prospective_net"] != "" else -1e18),
                                       t["signal_time"], t["symbol"]))
        capped.append(ts[0])
    return deduped, sorted(capped, key=lambda t: (t["date"], t["signal_time"], t["symbol"]))

def metrics(trades, ndays):
    if not trades:
        return {"trades": 0, "net_pos": 0, "net_pos_pct": 0.0, "targets": 0,
                "target_pct": 0.0, "net_rs": 0.0, "expectancy": 0.0,
                "trades_per_day": 0.0, "stops": 0, "square_offs": 0}
    return {"trades": len(trades),
            "net_pos": sum(1 for t in trades if t["net_rs"] > 0),
            "net_pos_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "targets": sum(1 for t in trades if t["exit_reason"] == "target"),
            "target_pct": round(100 * sum(1 for t in trades if t["exit_reason"] == "target") / len(trades), 1),
            "net_rs": round(sum(t["net_rs"] for t in trades), 2),
            "expectancy": round(sum(t["net_rs"] for t in trades) / len(trades), 2),
            "trades_per_day": round(len(trades) / ndays, 3) if ndays else 0.0,
            "stops": sum(1 for t in trades if t["exit_reason"] == "stop"),
            "square_offs": sum(1 for t in trades if t["exit_reason"] == "square_off")}

def setup_split(trades):
    s = defaultdict(lambda: [0, 0.0])
    for t in trades:
        s[t["setup"]][0] += 1; s[t["setup"]][1] += t["net_rs"]
    return {k: {"trades": v[0], "net_rs": round(v[1], 2)} for k, v in sorted(s.items())}

def month_cum(trades):
    cum, out = 0.0, {}
    for m in range(1, 11):
        mm = sum(t["net_rs"] for t in trades if int(t["date"][5:7]) == m)
        cum += mm
        out[f"2026-{m:02d}"] = {"month_net": round(mm, 2), "cumulative": round(cum, 2)}
    return out

def write_csv(path, trades):
    cols = ["symbol", "date", "version", "setup", "direction", "signal_time",
            "entry_price", "stop_price", "target_price", "exit_reason",
            "exit_price", "exit_time", "net_rs", "prospective_net"]
    extra = ["leg", "prev_day_return_pct", "source_version"]
    use_extra = [e for e in extra if any(e in t for t in trades)]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols + use_extra, extrasaction="ignore")
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["signal_time"], x["symbol"])):
            w.writerow(t)

results = {}
for ver, ts in ALL.items():
    ne = noevent_filter(ts)
    capped = cap_1day(ne, volrix=(ver == "volrix_v2"))
    results[ver] = {
        "all_days_uncapped": metrics(ts, n_trading_days),
        "noevent_uncapped": metrics(ne, n_trading_days),
        "noevent_1day": metrics(capped, n_trading_days),
        "excluded_event_trades": len(ts) - len(ne),
        "noevent_1day_setup_split": setup_split(capped),
        "noevent_1day_month_cumulative": month_cum(capped),
        "noevent_uncapped_setup_split": setup_split(ne),
        "la_leg_split": None,
    }
    if ver == "la_v2":
        for leg in ("morning", "reentry"):
            lt = [t for t in capped if t.get("leg") == leg]
            results[ver]["la_leg_split"] = results[ver].get("la_leg_split") or {}
            results[ver]["la_leg_split"][leg] = metrics(lt, n_trading_days)
        # uncapped leg counts too
        results[ver]["la_leg_split"]["morning_uncapped"] = metrics(
            [t for t in ne if t.get("leg") == "morning"], n_trading_days)
        results[ver]["la_leg_split"]["reentry_uncapped"] = metrics(
            [t for t in ne if t.get("leg") == "reentry"], n_trading_days)
    write_csv(f"{OUT}/stocks_v2_{ver}_noevent_all.csv", ne)
    write_csv(f"{OUT}/stocks_v2_{ver}_noevent_1day.csv", capped)

ne_by_ver = {ver: noevent_filter(ts) for ver, ts in ALL.items()}
deduped, comb_capped = combined_pool(ne_by_ver)
results["combined"] = {
    "noevent_deduped_uncapped": metrics(deduped, n_trading_days),
    "noevent_1day": metrics(comb_capped, n_trading_days),
    "noevent_1day_setup_split": setup_split(comb_capped),
    "noevent_1day_month_cumulative": month_cum(comb_capped),
    "deduped_trades": len(deduped),
}
write_csv(f"{OUT}/stocks_v2_combined_noevent_deduped.csv", deduped)
write_csv(f"{OUT}/stocks_v2_combined_noevent_1day.csv", comb_capped)

# Oct 26-28 separate check (Oct 29 absent from cache)
oct_check = {}
for ver, ts in ALL.items():
    sub = [t for t in ts if "2026-10-26" <= t["date"] <= "2026-10-28" and is_noevent(t["symbol"], t["date"])]
    sub_c = cap_1day(sub, volrix=(ver == "volrix_v2"))
    oct_check[ver] = {"noevent_uncapped": metrics(sub, 3), "noevent_1day": metrics(sub_c, 3)}
    write_csv(f"{OUT}/stocks_v2_{ver}_oct26_28_noevent.csv", sub)
ded, comb_oct = combined_pool({ver: [t for t in ts if "2026-10-26" <= t["date"] <= "2026-10-28"
                                     and is_noevent(t["symbol"], t["date"])]
                               for ver, ts in ALL.items()})
oct_check["combined"] = {"noevent_deduped_uncapped": metrics(ded, 3),
                         "noevent_1day": metrics(comb_oct, 3)}
write_csv(f"{OUT}/stocks_v2_combined_oct26_28_noevent_1day.csv", comb_oct)

write_csv(f"{OUT}/stocks_v2_v4input_noevent_all.csv", noevent_filter(v4_trades))
results["meta"] = {"input_trade_counts_all_days": {"v4_baseline": len(v4_trades),
                   "skill_v2": len(skill_trades)},
                   "trading_days_jan_oct28": n_trading_days,
                   "window": "2026-01-01 to 2026-10-28 (cache ends 2026-10-28; 2026-10-29 NOT in cache)",
                   "oct26_28_check": oct_check,
                   "noevent_stock_days_note": "no-event = outside ALL calendar windows (see script header)"}
with open(f"{OUT}/stocks_v2_versions_oct30_summary.json", "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps(results, indent=2))
