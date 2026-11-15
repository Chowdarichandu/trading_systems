#!/usr/bin/env python3
"""LIVE signal producer for the November 2026 index paper primaries.

PAPER ONLY. Real money Rs 0. No broker orders anywhere — this program only
READS market data (Upstox script-token route) and writes entry directives to
~/workspace/trading/live_shadow_signals.json for live_shadow_runner.py.

It evaluates the FROZEN U1 component systems CAUSALLY on completed 5-min spot
bars and assembles the pools exactly as the frozen EOD construction does:

  Components (one leg per system per index-day at most):
    * Skill V3  - Day Trader Skill S1 with the CE bearish-bias block REMOVED
                  (index_options_skill_tuned_oct30_frozen.md, variant V3).
                  First close beyond the opening range in 09:30-11:30;
                  a 09:30 PE is taken only if its close < PDL (else the day
                  ends for Skill). Source label in directives: "Skill".
    * (lA) v2   - L1 rescan, PE only (index_options_la_tuned_oct30_frozen.md).
                  Confirmer (other index) first close < own OR low in
                  09:30-11:30 = break time bt; rescan cutoff 13:30 if
                  bt < 11:30 (strict) else 11:30; rescan signal = first bar
                  in [bt, cutoff] with close < own ORL and close < own PDL,
                  OR width <= 360*scale, room >= 200*scale; leg exists only
                  if the entry (next bar open) gives risk = signal-bar high
                  - entry > 0. Source label: "(lA)".
    * V5 v2     - capped-v2 unified index leg (progressive_capped_v2.py):
                  V4 candidate (daytrader_cash_backtest.find_signal, first
                  signal of the day, Setup 1 skipped) and Skill-OR candidate
                  (first OR break <= 11:30, bias-aligned, PD-bound,
                  room >= 200*scale) pooled per symbol+date, dedup keeps the
                  higher setup rank (setup4=3 > setup3=2 > setup2=1 > skill
                  OR=0; V4 wins ties), prospective target net
                  (= 200*risk - 40, provisional cash unit) must be >= Rs 500,
                  cap 1 trade per symbol per ISO week. Source label: "V5".
    * Volrix (b) @ -1.0% - prev trading day's close-to-close change <= -1.0%
                  -> LONG CE today, entry bar 09:20, 10-session cooldown
                  (entries >= 10 trading sessions apart). Source: "Volrix".

  Pool assembly (mirrors u1_janoct_merge.py): legs grouped by
  (index, direction); sources = all systems on the key; entry bar =
  earliest leg's signal bar + 5 min; representative = earliest leg's system
  (ties broken in merge insertion order (lA), V5, Skill, Volrix).

  BANK primary (BNF-PAPER-V1) = B2 keys + NS1 second legs, unique-once.
    B2 filter (verified leg-for-leg against index_options_U1_B2_bank_trades
    .csv, 183/183 Jan-Oct keys): drop a merged key iff
      (direction == CE and representative == Skill V3) or
      (sources == {Skill V3} alone and entry_time <= 09:55).
    Causal emission: a Bank CE key whose FIRST leg is Skill's is dead on
    arrival (no directive ever). A Skill-solo key with entry <= 09:55 is
    held pending; it is emitted only if a second system joins the key
    (entry then = the confirming leg's entry bar — the documented
    confirmation-lag class), otherwise never. All other keys are emitted
    at their first leg's entry bar.
    NS1 second leg (index_options_newsetup_ns1_second_frozen.md +
    newsetups_score.py, Bank only): base = Skill v2 S1 (WITH the CE
    bearish block) spot trade; if it exits by target/stop with exit bar
    <= 13:30, scan bars strictly after the exit bar for the first fresh
    OR crossing (close beyond a level, previous close not beyond it),
    signal <= 14:30; first-candidate discipline: a CE crossing on a
    bearish-bias day, an un-replayable candidate, or room_ratio < 1.5
    ends the search with no leg. Emitted as kind=NS1_SECOND with
    room_ratio and bias for the runner's own gate.

  NIFTY primary (NF-PAPER-C3G7) = C3 confirmed-only: a key is emitted when
    its SECOND distinct source system fires (sources = all systems on the
    key at that moment). Solo keys are never emitted. (The EOD
    construction enters a confirmed key at its earliest leg; the live
    entry is at the confirming leg — the documented confirmation-lag
    class, measured by the control runs.)

Emission timing rule: a directive is emitted only while its entry bar is
still the current (in-progress) bar, so the runner's live fill stays
inside the frozen entry bar. Older signals are logged as missed, never
back-filled. In replay mode this rule is reported, not applied (the full
directive stream is reconstructed for comparison).

State: ~/workspace/trading/live_producer_state.json (per-day key state,
Volrix cooldown seeds, V5 week usage). Log: live_producer_log.md.
"""
import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, date as ddate, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
TR = Path.home() / "workspace" / "trading"
ENV_FILE = TR / "upstox_refresh" / ".env"
SIGNALS_FILE = TR / "live_shadow_signals.json"
STATE_FILE = TR / "live_producer_state.json"
LOG_FILE = TR / "live_producer_log.md"
API = "https://api.upstox.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
SPOT_KEY = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}
IDX_OF = {"NIFTY": "nifty", "BANKNIFTY": "bank"}
OTHER = {"NIFTY": "BANKNIFTY", "BANKNIFTY": "NIFTY"}
# Directive source labels (the runner tests for the exact string "Skill").
LBL = {"(lA) v2": "(lA)", "V5 v2": "V5", "Skill V3": "Skill", "Volrix (b)": "Volrix"}
MERGE_ORDER = ["(lA) v2", "V5 v2", "Skill V3", "Volrix (b)"]  # u1_janoct_merge insertion order
SETUP_RANK = {"setup4_pullback": 3, "setup4_reclaim": 3, "setup3_bounce_rejection": 2,
              "setup2_or_breakout": 1, "setup2_or_breakdown": 1,
              "or_breakout": 0, "or_breakdown": 0}

# Volrix (b) last premium-scored entries Jan-Oct 2026 (u1_janoct_merge.py +
# index_options_U1_volrixB_jansep_spot.csv); used for the 10-session cooldown.
VOLRIX_LAST_ENTRY = {"NIFTY": "2026-10-09", "BANKNIFTY": "2026-10-26"}
VOLRIX_COOLDOWN_SESSIONS = 10


# ------------------------------------------------------------------ bars
# A bar is a dict: {"time": "HH:MM", "open","high","low","close": float}
def or_levels(bars):
    orc = [b for b in bars if b["time"] < "09:30"]
    if not orc:
        return None, None
    return max(b["high"] for b in orc), min(b["low"] for b in orc)


def bias_of(prev):
    rng = prev["high"] - prev["low"]
    cs = (prev["close"] - prev["low"]) / rng * 100 if rng else 50.0
    return ("bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"), cs


def next_bar(bars, time_str):
    for i, b in enumerate(bars):
        if b["time"] == time_str:
            return bars[i + 1] if i + 1 < len(bars) else None
    return None


def bar_at(bars, time_str):
    for b in bars:
        if b["time"] == time_str:
            return b
    return None


def plus5(time_str):
    h, m = int(time_str[:2]), int(time_str[3:5])
    m += 5
    if m >= 60:
        h, m = h + 1, m - 60
    return f"{h:02d}:{m:02d}"


# ------------------------------------------------------------------ components
def skill_signal(bars):
    """First OR break in 09:30-11:30. Returns (idx, direction) or (None, None)."""
    orh, orl = or_levels(bars)
    if orh is None:
        return None, None
    for i, b in enumerate(bars):
        if b["time"] < "09:30" or b["time"] > "11:30":
            continue
        if b["close"] > orh:
            return i, "CE"
        if b["close"] < orl:
            return i, "PE"
    return None, None


def entry_bar_after(bars_done, sig_time, bars_nxt=None):
    """The bar after sig_time, from completed bars or the partial next bar."""
    nb = next_bar(bars_done, sig_time)
    if nb is not None:
        return nb
    if bars_nxt is not None and bars_done and plus5(bars_done[-1]["time"]) == bars_nxt["time"]:
        # sig_time is the last completed bar; the partial bar is its next bar
        if bar_at(bars_done, sig_time) is bars_done[-1]:
            return bars_nxt
    return None


def skill_v3_leg(bars, prev, bars_nxt=None):
    """Tuned Skill V3 (CE no-block). bars = completed bars; bars_nxt = the
    in-progress next bar (only its open is ever used). Returns leg or None."""
    i, d = skill_signal(bars)
    if i is None:
        return None, "no OR break 09:30-11:30"
    sig = bars[i]
    if d == "PE" and sig["time"] == "09:30" and not (sig["close"] < prev["low"]):
        return None, "blocked: 09:30 PE close >= PDL (day ends for Skill)"
    if entry_bar_after(bars, sig["time"], bars_nxt) is None:
        return None, "signal on last bar (no entry bar yet)"
    return {"system": "Skill V3", "direction": d, "signal_time": sig["time"]}, "fired"


def skill_s1_base(bars, prev):
    """Skill v2 S1 base trade for NS1 (CE bearish block APPLIES here).
    Returns (trade, signal_idx, direction) or (None, reason). Spot replay per
    newsetups_score.py: entry = next bar open, stop = signal low/high,
    target = entry +/- 2*risk, stop before target, square-off 15:10."""
    bias, _ = bias_of(prev)
    i, d = skill_signal(bars)
    if i is None:
        return None, "no S1 signal"
    sig = bars[i]
    if d == "CE" and bias == "bearish":
        return None, "S1 CE blocked on bearish-bias day"
    if d == "PE" and sig["time"] == "09:30" and not (sig["close"] < prev["low"]):
        return None, "S1 09:30 PE blocked (close >= PDL)"
    tr = spot_replay(bars, i, d)
    if tr is None:
        return None, "S1 replay: no entry bar or risk 0"
    return (tr, i, d), "taken"


def spot_replay(bars, sig_idx, direction):
    """newsetups_score.replay: common spot exit. Returns dict or None."""
    if sig_idx + 1 >= len(bars):
        return None
    entry = bars[sig_idx + 1]["open"]
    sig = bars[sig_idx]
    stop = sig["low"] if direction == "CE" else sig["high"]
    risk = abs(entry - stop)
    if risk == 0:
        return None
    target = entry + 2 * risk if direction == "CE" else entry - 2 * risk
    for j in range(sig_idx + 1, len(bars)):
        b = bars[j]
        if b["time"] > "15:10":
            break
        if direction == "CE":
            if b["low"] <= stop:
                return {"entry": entry, "stop": stop, "target": target, "risk": risk,
                        "exit": stop, "exit_time": b["time"], "exit_reason": "stop"}
            if b["high"] >= target:
                return {"entry": entry, "stop": stop, "target": target, "risk": risk,
                        "exit": target, "exit_time": b["time"], "exit_reason": "target"}
        else:
            if b["high"] >= stop:
                return {"entry": entry, "stop": stop, "target": target, "risk": risk,
                        "exit": stop, "exit_time": b["time"], "exit_reason": "stop"}
            if b["low"] <= target:
                return {"entry": entry, "stop": stop, "target": target, "risk": risk,
                        "exit": target, "exit_time": b["time"], "exit_reason": "target"}
        if b["time"] == "15:10":
            return {"entry": entry, "stop": stop, "target": target, "risk": risk,
                    "exit": b["close"], "exit_time": b["time"], "exit_reason": "square_off"}
    last = [b for b in bars if b["time"] <= "15:10"]
    if not last:
        return None
    return {"entry": entry, "stop": stop, "target": target, "risk": risk,
            "exit": last[-1]["close"], "exit_time": last[-1]["time"], "exit_reason": "square_off"}


def room_ratio_pd(close, direction, prev):
    """Room to next PD level / (200*scale) — progressive_capped.room_ratio."""
    pdh, pdc, pdl = prev["high"], prev["close"], prev["low"]
    scale = pdc / 55000.0 if pdc else 1.0
    levels = sorted({pdh, pdc, pdl})
    if direction == "CE":
        nxt = [l for l in levels if l > close]
        room = (min(nxt) - close) if nxt else math.inf
    else:
        nxt = [l for l in levels if l < close]
        room = (close - max(nxt)) if nxt else math.inf
    return (room / (200 * scale) if scale else 0.0), room


def la_v2_leg(own_bars, conf_bars, prev, own_nxt=None):
    """(lA) v2 L1 morning leg (PE only). Returns leg dict or None (+reason)."""
    # confirmer break: first bar 09:30-11:30 with close < confirmer ORL
    _, conf_orl = or_levels(conf_bars)
    if conf_orl is None:
        return None, "confirmer OR not complete"
    bt = None
    for b in conf_bars:
        if b["time"] < "09:30" or b["time"] > "11:30":
            continue
        if b["close"] < conf_orl:
            bt = b["time"]
            break
    if bt is None:
        return None, "confirmer never broke OR low 09:30-11:30"
    cutoff = "13:30" if bt < "11:30" else "11:30"
    orh, orl = or_levels(own_bars)
    if orh is None:
        return None, "own OR not complete"
    or_width = orh - orl
    pdh, pdc, pdl = prev["high"], prev["close"], prev["low"]
    scale = pdc / 55000.0 if pdc else 1.0
    levels = sorted({pdh, pdc, pdl})
    cand = [b for b in own_bars if b["time"] >= "09:30"]
    for i, b in enumerate(cand):
        t = b["time"]
        if t > cutoff or t < bt:
            continue
        cl = b["close"]
        if cl < orl and cl < pdl:
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                eb = entry_bar_after(cand, t, own_nxt)
                if eb is None:
                    return None, "rescan signal on last bar (no entry bar yet)"
                entry = eb["open"]
                risk = float(b["high"]) - entry
                if risk <= 0:
                    return None, "rescan entry risk <= 0 (invalid, no leg in EOD)"
                return {"system": "(lA) v2", "direction": "PE",
                        "signal_time": t}, f"fired (confirmer break {bt}, cutoff {cutoff})"
    return None, f"no rescan bar <= {cutoff} closed < ORL and < PDL with room/width gates"


def v4_candidate(bars, prev, bars_nxt=None):
    """V4 candidate via the ORIGINAL daytrader_cash_backtest.find_signal.
    Returns (cand or None, reason). cand: direction, signal_time, setup,
    setup_rank, risk, target_net."""
    import pandas as pd
    from daytrader_cash_backtest import find_signal
    if len(bars) < 4:
        return None, "too few bars"
    df = pd.DataFrame([{"timestamp": f"2026-01-01 {b['time']}:00", "time": b["time"],
                        "open": b["open"], "high": b["high"], "low": b["low"],
                        "close": b["close"]} for b in bars])
    bias, _ = bias_of(prev)
    scale = prev["close"] / 55000.0 if prev["close"] else 1.0
    setup, direction, sig = find_signal(df, prev["high"], prev["close"], prev["low"], bias, scale)
    if setup is None:
        return None, "find_signal: no V4 signal yet"
    sig_time = str(sig["time"])
    # entry bar = next bar after signal (run_day logic)
    nb = entry_bar_after(bars, sig_time, bars_nxt)
    if nb is None:
        return None, "V4 signal on last bar (no entry bar yet)"
    entry = nb["open"]
    stop = float(sig["low"]) if direction == "CE" else float(sig["high"])
    risk = (entry - stop) if direction == "CE" else (stop - entry)
    if risk <= 0:
        return None, "V4 candidate invalid (risk <= 0, run_day no_trade)"
    return {"method": "V4", "direction": direction, "signal_time": sig_time,
            "setup": setup, "setup_rank": SETUP_RANK.get(setup, 0),
            "risk": risk, "target_net": round(200 * risk - 40, 2)}, "fired"


def skill_candidate_v5(bars, prev, bars_nxt=None):
    """Skill-OR candidate for the V5 pool (find_skill_signal OR-only +
    capped-v2 filters). Returns (cand or None, reason)."""
    bias, _ = bias_of(prev)
    allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
    i, d = skill_signal(bars)
    if i is None:
        return None, "no OR break <= 11:30"
    sig = bars[i]
    if d not in allowed:
        return None, f"Skill cand filtered: {d} not bias-aligned ({bias})"
    if d == "CE" and not (sig["close"] < prev["high"]):
        return None, "Skill cand filtered: CE close >= PDH"
    if d == "PE" and not (sig["close"] < prev["low"]):
        return None, "Skill cand filtered: PE close >= PDL"
    rr, _room = room_ratio_pd(sig["close"], d, prev)
    if rr < 1.0:
        return None, "Skill cand filtered: room < 200*scale"
    nb = entry_bar_after(bars, sig["time"], bars_nxt)
    if nb is None:
        return None, "Skill cand on last bar (no entry bar yet)"
    entry = nb["open"]
    stop = float(sig["low"]) if d == "CE" else float(sig["high"])
    risk = (entry - stop) if d == "CE" else (stop - entry)
    if risk <= 0:
        return None, "Skill cand invalid (entry == stop)"
    return {"method": "Skill", "direction": d, "signal_time": sig["time"],
            "setup": "or_breakout" if d == "CE" else "or_breakdown",
            "setup_rank": 0, "risk": risk,
            "target_net": round(200 * risk - 40, 2)}, "fired"


def v5_leg(bars, prev, week_used, bars_nxt=None):
    """V5 v2 unified index leg for the day. week_used: True if this symbol
    already has a V5 pick in this ISO week. Returns (leg or None, reason,
    cand_info)."""
    v4, r4 = v4_candidate(bars, prev, bars_nxt)
    sk, rs = skill_candidate_v5(bars, prev, bars_nxt)
    pool = [c for c in (v4, sk) if c is not None]
    if not pool:
        return None, f"no candidates (V4: {r4}; Skill: {rs})", {}
    # capped_v2 dedup: keep higher setup_rank; V4 wins ties (listed first,
    # replaced only on strictly greater rank).
    win = pool[0]
    for c in pool[1:]:
        if c["setup_rank"] > win["setup_rank"]:
            win = c
    info = {"candidates": pool, "winner": win["method"]}
    if win["target_net"] < 500:
        return None, f"V5 winner {win['method']} {win['direction']} prospective {win['target_net']} < 500", info
    if week_used:
        return None, "V5 weekly cap: symbol already picked this ISO week", info
    return {"system": "V5 v2", "direction": win["direction"],
            "signal_time": win["signal_time"]}, f"fired via {win['method']} ({win['setup']})", info


def volrix_leg(prev, prev2, sessions_apart):
    """Volrix (b) @ -1.0%: prev day close-to-close <= -1.0% -> CE today.
    Returns (leg or None, reason)."""
    if prev2 is None or not prev2["close"]:
        return None, "no prev-prev daily for trigger"
    chg = (prev["close"] - prev2["close"]) / prev2["close"] * 100
    if chg > -1.0:
        return None, f"prev-day change {chg:+.2f}% > -1.0% (no trigger)"
    if sessions_apart is not None and sessions_apart < VOLRIX_COOLDOWN_SESSIONS:
        return None, (f"trigger {chg:+.2f}% but cooldown: {sessions_apart} sessions "
                      f"since last Volrix entry < {VOLRIX_COOLDOWN_SESSIONS}")
    return {"system": "Volrix (b)", "direction": "CE", "signal_time": "09:15"}, \
        f"fired (prev-day change {chg:+.2f}%, cooldown ok)"


def ns1_second_leg(bars, prev, bars_nxt=None):
    """NS1 second leg (Bank primary only). bars = completed bars; bars_nxt =
    the in-progress bar after the last completed one (used only as the second
    leg's entry bar — its open — never for signal logic). Returns (leg,
    detail) or (None, reason). Follows newsetups_score.py exactly, incl.
    first-candidate discipline (a gated-out first crossing ends the search)."""
    base, why = skill_s1_base(bars, prev)
    if base is None:
        return None, f"no S1 base ({why})"
    tr, _i, _d = base
    if tr["exit_reason"] not in ("target", "stop"):
        return None, f"S1 base exited {tr['exit_reason']} (not target/stop)"
    if tr["exit_time"] > "13:30":
        return None, f"S1 base exit {tr['exit_time']} > 13:30"
    orh, orl = or_levels(bars)
    bias, _ = bias_of(prev)
    exit_idx = next(j for j, b in enumerate(bars) if b["time"] == tr["exit_time"])
    for j in range(exit_idx + 1, len(bars)):
        b = bars[j]
        if b["time"] > "14:30":
            break
        prv = bars[j - 1]
        d2 = None
        if b["close"] > orh and not (prv["close"] > orh):
            d2 = "CE"
        elif b["close"] < orl and not (prv["close"] < orl):
            d2 = "PE"
        if d2 is None:
            continue
        if d2 == "CE" and bias == "bearish":
            return None, "first crossing CE blocked on bearish-bias day (search ends)"
        tr2 = spot_replay(bars + ([bars_nxt] if bars_nxt else []), j, d2)
        if tr2 is None:
            if j == len(bars) - 1 and bars_nxt is None:
                return None, "first crossing is the last completed bar (entry bar not open yet)"
            return None, "first crossing un-replayable (search ends)"
        lv = sorted({prev["high"], prev["close"], prev["low"]})
        if d2 == "CE":
            nxt = [l for l in lv if l > b["close"]]
            room = (min(nxt) - b["close"]) if nxt else math.inf
        else:
            nxt = [l for l in lv if l < b["close"]]
            room = (b["close"] - max(nxt)) if nxt else math.inf
        rr = room / tr2["risk"] if tr2["risk"] else 0.0
        if rr < 1.5:
            return None, f"first crossing room_ratio {rr:.2f} < 1.5 (search ends)"
        return {"system": "NS1", "direction": d2, "signal_time": b["time"],
                "room_ratio": round(rr, 3), "bias": bias}, \
            f"fired (base exit {tr['exit_reason']} {tr['exit_time']}, room_ratio {rr:.2f})"
    return None, "no fresh OR crossing after base exit <= 14:30"


# ------------------------------------------------------------------ data
def load_token():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("UPSTOX_ACCESS_TOKEN not found in .env")


def api_json(path):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {load_token()}",
        "User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def candles_to_bars(candles):
    bars = []
    for c in candles or []:
        ts = datetime.fromisoformat(str(c[0]).replace("Z", "+00:00"))
        bars.append({"time": ts.astimezone(IST).strftime("%H:%M"),
                     "open": float(c[1]), "high": float(c[2]),
                     "low": float(c[3]), "close": float(c[4])})
    bars.sort(key=lambda b: b["time"])
    return bars


def fetch_intraday(symbol):
    """Today's 5-min bars (incl. the in-progress bar) via the v3 endpoint."""
    key = urllib.parse.quote(SPOT_KEY[symbol], safe="")
    data = api_json(f"/v3/historical-candle/intraday/{key}/minutes/5")
    return candles_to_bars(data.get("data", {}).get("candles"))


def fetch_day_bars(symbol, day):
    """One completed day's 5-min bars via the v3 historical endpoint."""
    key = urllib.parse.quote(SPOT_KEY[symbol], safe="")
    d = day.isoformat()
    data = api_json(f"/v3/historical-candle/{key}/minutes/5/{d}/{d}")
    return candles_to_bars(data.get("data", {}).get("candles"))


def fetch_daily(symbol, n_days=40):
    """Recent daily bars (oldest first) via the v3 endpoint."""
    key = urllib.parse.quote(SPOT_KEY[symbol], safe="")
    to = datetime.now(IST).date()
    frm = to - timedelta(days=n_days)
    data = api_json(f"/v3/historical-candle/{key}/days/1/{to.isoformat()}/{frm.isoformat()}")
    out = []
    for c in data.get("data", {}).get("candles") or []:
        ts = datetime.fromisoformat(str(c[0]).replace("Z", "+00:00"))
        out.append({"date": ts.astimezone(IST).date().isoformat(),
                    "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4])})
    out.sort(key=lambda r: r["date"])
    return out


def cache_bars(symbol, day):
    p = TR / "data" / "progressive" / symbol / "spot_5m.csv"
    bars = []
    for line in p.read_text().splitlines()[1:]:
        if not line.startswith(day.isoformat()):
            continue
        f = line.split(",")
        bars.append({"time": f[0][11:16], "open": float(f[1]), "high": float(f[2]),
                     "low": float(f[3]), "close": float(f[4])})
    bars.sort(key=lambda b: b["time"])
    return bars


def cache_daily(symbol):
    p = TR / "data" / "progressive" / symbol / "spot_daily.csv"
    out = []
    for line in p.read_text().splitlines()[1:]:
        f = line.split(",")
        if len(f) < 5:
            continue
        out.append({"date": f[0], "open": float(f[1]), "high": float(f[2]),
                    "low": float(f[3]), "close": float(f[4])})
    out.sort(key=lambda r: r["date"])
    return out


# ------------------------------------------------------------------ pool assembly
def evaluate_legs(symbol, own_bars, conf_bars, prev, prev2, week_used,
                  sessions_apart, bars_nxt=None):
    """All U1 component legs visible on the given completed bars.
    Returns (legs, notes): legs = [{system, direction, signal_time}]."""
    legs, notes = [], {}
    leg, why = skill_v3_leg(own_bars, prev, bars_nxt)
    notes["Skill V3"] = why
    if leg:
        legs.append(leg)
    leg, why = la_v2_leg(own_bars, conf_bars, prev, bars_nxt)
    notes["(lA) v2"] = why
    if leg:
        legs.append(leg)
    leg, why, _info = v5_leg(own_bars, prev, week_used, bars_nxt)
    notes["V5 v2"] = why
    if leg:
        legs.append(leg)
    leg, why = volrix_leg(prev, prev2, sessions_apart)
    notes["Volrix (b)"] = why
    if leg:
        legs.append(leg)
    return legs, notes


def merge_keys(legs):
    """u1_janoct_merge semantics: group by direction; entry = earliest leg's
    signal + 5; representative = earliest leg (ties: MERGE_ORDER)."""
    keys = {}
    for d in ("CE", "PE"):
        dl = [l for l in legs if l["direction"] == d]
        if not dl:
            continue
        dl.sort(key=lambda l: (l["signal_time"], MERGE_ORDER.index(l["system"])))
        keys[d] = {"direction": d, "legs": dl,
                   "sources": [l["system"] for l in sorted(
                       dl, key=lambda l: MERGE_ORDER.index(l["system"]))],
                   "entry_time": plus5(dl[0]["signal_time"]),
                   "representative": dl[0]["system"],
                   "first_leg": dl[0]}
    return keys


def b2_drop(key):
    """Frozen B2 filter (Rule B) on a full-day merged key."""
    if key["direction"] == "CE" and key["representative"] == "Skill V3":
        return True
    if set(key["sources"]) == {"Skill V3"} and key["entry_time"] <= "09:55":
        return True
    return False


# ------------------------------------------------------------------ causal engine
def causal_directives(symbol, own_full, conf_full, prev, prev2, week_used,
                      sessions_apart):
    """Step through the day bar by bar (completed bars + the next bar as the
    partial entry bar) and return the directive stream the frozen causal
    emission rules produce: [{kind, direction, signal_time, sources,
    entry_time, room_ratio?, bias?}] plus per-step component notes."""
    out = []
    emitted = set()          # (kind, direction)
    dead = set()             # directions killed by Rule B (Bank CE Skill-first)
    pending = {}             # direction -> legs dict (Skill-solo early, Bank)
    known = {}               # direction -> {system: leg}
    ns1_done = False
    last_notes = {}
    n = len(own_full)
    for k in range(3, n + 1):
        own_done = own_full[:k]
        conf_done = [b for b in conf_full if b["time"] <= (own_done[-1]["time"] if own_done else "09:15")]
        partial = own_full[k] if k < n else None
        conf_partial = None
        if partial is not None:
            conf_partial = next((b for b in conf_full if b["time"] == partial["time"]), None)
        legs, notes = evaluate_legs(symbol, own_done, conf_done, prev, prev2,
                                    week_used, sessions_apart, partial)
        last_notes = notes
        for leg in legs:
            known.setdefault(leg["direction"], {})[leg["system"]] = leg
        for d, sysmap in list(known.items()):
            if ("BASE", d) in emitted or d in dead:
                continue
            srt = sorted(sysmap.values(),
                         key=lambda l: (l["signal_time"], MERGE_ORDER.index(l["system"])))
            first = srt[0]
            srcs = [LBL[s] for s in sorted(sysmap, key=lambda s: MERGE_ORDER.index(s))]
            if symbol == "BANKNIFTY":
                if first["system"] == "Skill V3" and d == "CE":
                    dead.add(d)
                    continue
                if set(sysmap) == {"Skill V3"} and plus5(first["signal_time"]) <= "09:55":
                    pending[d] = sysmap
                    continue
                et = plus5(srt[-1]["signal_time"]) if d in pending and len(sysmap) > 1 \
                    else plus5(first["signal_time"])
                out.append({"kind": "BASE", "direction": d,
                            "signal_time": srt[-1]["signal_time"] if d in pending and len(sysmap) > 1
                            else first["signal_time"],
                            "sources": srcs, "entry_time": et})
                emitted.add(("BASE", d))
            else:  # NIFTY C3: emit when the 2nd distinct source fires
                if len(sysmap) >= 2:
                    out.append({"kind": "BASE", "direction": d,
                                "signal_time": srt[1]["signal_time"],
                                "sources": srcs,
                                "entry_time": plus5(srt[1]["signal_time"])})
                    emitted.add(("BASE", d))
        if symbol == "BANKNIFTY" and not ns1_done:
            leg, _why = ns1_second_leg(own_done, prev, partial)
            if leg:
                ns1_done = True
                if ("BASE", leg["direction"]) not in emitted:
                    out.append({"kind": "NS1_SECOND", "direction": leg["direction"],
                                "signal_time": leg["signal_time"],
                                "sources": ["Skill"], "room_ratio": leg["room_ratio"],
                                "bias": leg["bias"],
                                "entry_time": plus5(leg["signal_time"])})
                    emitted.add(("NS1_SECOND", leg["direction"]))
    return out, last_notes


# ------------------------------------------------------------------ reference (EOD construction)
def full_day_keys(symbol, own, conf, prev, prev2, week_used, sessions_apart):
    legs, notes = evaluate_legs(symbol, own, conf, prev, prev2, week_used,
                                sessions_apart, None)
    return merge_keys(legs), legs, notes


def load_merge_csv():
    import csv
    rows = []
    with open(TR / "index_options_U1_janoct_trades.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def frozen_state_for(day, symbol, daily_rows, merge_rows):
    """week_used + Volrix sessions_apart for a replay day, from the frozen
    record (merge CSV) and the daily cache — control use only."""
    iso = day.isocalendar()[:2]
    week_used = any(r["index"] == symbol and r["date"] < day.isoformat()
                    and ddate.fromisoformat(r["date"]).isocalendar()[:2] == iso
                    and "V5 v2" in r["source_systems"] for r in merge_rows)
    vol = [r["date"] for r in merge_rows
           if r["index"] == symbol and "Volrix (b)" in r["source_systems"]
           and r["date"] < day.isoformat()]
    dates = [r["date"] for r in daily_rows]
    if vol and day.isoformat() in dates:
        last = max(vol)
        if last in dates:
            return week_used, dates.index(day.isoformat()) - dates.index(last)
    return week_used, None


# ------------------------------------------------------------------ logging / state
def plog(msg):
    ts = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    line = f"- [{ts}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(st):
    STATE_FILE.write_text(json.dumps(st, indent=1))


def write_signals(new_directives):
    """Merge producer directives into live_shadow_signals.json: foreign ids
    (not prod-*) are kept; our own are replaced by the fresh set."""
    existing = []
    if SIGNALS_FILE.exists():
        try:
            existing = json.loads(SIGNALS_FILE.read_text()).get("directives") or []
        except Exception:
            existing = []
    kept = [d for d in existing if not str(d.get("id", "")).startswith("prod-")]
    payload = {"date": datetime.now(IST).date().isoformat(),
               "generated_at": datetime.now(IST).isoformat(),
               "directives": kept + new_directives}
    SIGNALS_FILE.write_text(json.dumps(payload, indent=1))
    return len(kept)


# ------------------------------------------------------------------ modes
def day_context_cache(day):
    ctx = {}
    merge_rows = load_merge_csv()
    for sym in ("NIFTY", "BANKNIFTY"):
        daily = cache_daily(sym)
        prevs = [r for r in daily if r["date"] < day.isoformat()]
        if len(prevs) < 2:
            raise RuntimeError(f"{sym}: cache lacks 2 prior daily rows for {day}")
        prev, prev2 = prevs[-1], prevs[-2]
        wu, sa = frozen_state_for(day, sym, daily, merge_rows)
        ctx[sym] = {"own": cache_bars(sym, day), "prev": prev, "prev2": prev2,
                    "week_used": wu, "sessions_apart": sa}
    return ctx


def cmd_reference(day):
    ctx = day_context_cache(day)
    merge_rows = load_merge_csv()
    b2_rows = {}
    import csv
    with open(TR / "index_options_U1_B2_bank_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["date"] == day.isoformat():
                b2_rows[r["direction"]] = r
    print(f"=== REFERENCE {day} (full-day EOD construction vs frozen files) ===")
    for sym in ("BANKNIFTY", "NIFTY"):
        c = ctx[sym]
        conf = ctx[OTHER[sym]]["own"]
        keys, legs, notes = full_day_keys(sym, c["own"], conf, c["prev"], c["prev2"],
                                          c["week_used"], c["sessions_apart"])
        print(f"-- {sym}: legs={[(l['system'], l['direction'], l['signal_time']) for l in legs]}")
        for comp, why in notes.items():
            print(f"   {comp}: {why}")
        frozen = {r["direction"]: r for r in merge_rows
                  if r["date"] == day.isoformat() and r["index"] == sym}
        all_dirs = sorted(set(keys) | set(frozen))
        if not all_dirs:
            print(f"   MERGE: no keys either side — MATCH (empty)")
        for d in all_dirs:
            mine = keys.get(d)
            ref = frozen.get(d)
            if mine and ref:
                ok = (set(mine["sources"]) == set(ref["source_systems"].split(";"))
                      and mine["entry_time"] == ref["entry_time"]
                      and mine["representative"] == ref["representative_system"])
                print(f"   MERGE {d}: mine src={mine['sources']} entry={mine['entry_time']} "
                      f"rep={mine['representative']} | frozen src={ref['source_systems']} "
                      f"entry={ref['entry_time']} rep={ref['representative_system']} "
                      f"-> {'MATCH' if ok else 'MISMATCH'}")
            elif mine:
                print(f"   MERGE {d}: mine src={mine['sources']} entry={mine['entry_time']} | frozen NONE -> MISMATCH (extra)")
            else:
                print(f"   MERGE {d}: mine NONE | frozen src={ref['source_systems']} entry={ref['entry_time']} -> MISMATCH (missing)")
        if sym == "BANKNIFTY":
            for d in sorted(set(keys) | set(b2_rows)):
                mine_in = d in keys and not b2_drop(keys[d])
                if mine_in and d in b2_rows:
                    ok = keys[d]["entry_time"] == b2_rows[d]["entry_time"]
                    print(f"   B2 {d}: in book, entry {keys[d]['entry_time']} vs frozen {b2_rows[d]['entry_time']} -> {'MATCH' if ok else 'MISMATCH'}")
                elif mine_in:
                    print(f"   B2 {d}: mine IN BOOK, frozen NOT -> MISMATCH")
                elif d in b2_rows:
                    print(f"   B2 {d}: mine NOT in book, frozen IN ({b2_rows[d]['entry_time']}) -> MISMATCH")
                else:
                    print(f"   B2 {d}: dropped both sides — MATCH")
            leg, why = ns1_second_leg(c["own"], c["prev"])
            print(f"   NS1: {why}" + (f" leg={leg}" if leg else ""))
        else:
            for d in sorted(keys):
                c3 = len(keys[d]["sources"]) >= 2
                print(f"   C3 {d}: sources={keys[d]['sources']} -> {'IN (confirmed)' if c3 else 'OUT (solo)'}")


def cmd_replay(day, source):
    if source == "cache":
        ctx = day_context_cache(day)
        get = {s: ctx[s]["own"] for s in ctx}
        meta = {s: ctx[s] for s in ctx}
    else:
        raise RuntimeError("api replay uses --reference-day bars via fetch_day_bars; "
                           "wire in cmd_replay_api")
    print(f"=== CAUSAL REPLAY {day} (source={source}) ===")
    for sym in ("BANKNIFTY", "NIFTY"):
        c = meta[sym]
        stream, notes = causal_directives(sym, get[sym], get[OTHER[sym]], c["prev"],
                                          c["prev2"], c["week_used"], c["sessions_apart"])
        print(f"-- {sym}: {len(stream)} directive(s)")
        for dv in stream:
            print(f"   {dv['kind']} {dv['direction']} signal={dv['signal_time']} "
                  f"entry_bar={dv['entry_time']} sources={dv['sources']}"
                  + (f" room_ratio={dv.get('room_ratio')} bias={dv.get('bias')}" if dv["kind"] == "NS1_SECOND" else ""))
        for comp, why in notes.items():
            print(f"   final {comp}: {why}")


def cmd_once():
    now = datetime.now(IST)
    day = now.date()
    st = load_state()
    if st.get("date") != day.isoformat():
        st = {"date": day.isoformat(), "emitted": [], "volrix_last": dict(VOLRIX_LAST_ENTRY),
              "v5_week": {}}
    bars, daily = {}, {}
    for sym in ("NIFTY", "BANKNIFTY"):
        bars[sym] = fetch_intraday(sym)
        daily[sym] = fetch_daily(sym)
    new_directives = []
    for sym in ("NIFTY", "BANKNIFTY"):
        rows = [r for r in daily[sym] if r["date"] < day.isoformat()]
        if len(rows) < 2:
            plog(f"{sym}: daily history short ({len(rows)} rows) — skipped")
            continue
        prev, prev2 = rows[-1], rows[-2]
        dates = [r["date"] for r in daily[sym]]
        last_v = st["volrix_last"].get(sym)
        sa = None
        if last_v in dates and day.isoformat() not in dates:
            sa = (len(dates) - dates.index(last_v))  # sessions from last entry to today
        elif last_v in dates:
            sa = dates.index(day.isoformat()) - dates.index(last_v)
        wk = f"{sym}:{day.isocalendar()[0]}-W{day.isocalendar()[1]:02d}"
        week_used = bool(st["v5_week"].get(wk))
        all_bars = bars[sym]
        # completed bars: bar start + 5 min <= now; the rest is the partial bar
        done = [b for b in all_bars
                if datetime.combine(day, datetime.strptime(b["time"], "%H:%M").time(), IST)
                + timedelta(minutes=5) <= now]
        if len(done) < 3:
            plog(f"{sym}: only {len(done)} completed bars — no evaluation")
            continue
        stream, notes = causal_directives(sym, _with_partial(done, all_bars),
                                          _with_partial_other(bars[OTHER[sym]], done[-1]["time"]),
                                          prev, prev2, week_used, sa)
        # persist V5 week usage + Volrix last-entry from today's full evaluation
        legs_now, _ = evaluate_legs(sym, done, bars[OTHER[sym]], prev, prev2,
                                    week_used, sa, None)
        if any(l["system"] == "V5 v2" for l in legs_now):
            st["v5_week"][wk] = True
        if any(l["system"] == "Volrix (b)" for l in legs_now):
            st["volrix_last"][sym] = day.isoformat()
        cur_partial = _current_partial(all_bars, day, now)
        plog(f"{sym}: bars_done={len(done)} last={done[-1]['time']} "
             f"partial={cur_partial['time'] if cur_partial else None} "
             f"notes={notes}")
        for dv in stream:
            did = f"prod-{IDX_OF[sym]}-{day.isoformat()}-{dv['kind']}-{dv['direction']}"
            if did in st["emitted"]:
                continue
            if cur_partial is not None and dv["entry_time"] == cur_partial["time"]:
                new_directives.append({
                    "id": did, "index": IDX_OF[sym], "kind": dv["kind"],
                    "direction": dv["direction"], "signal_time": dv["signal_time"],
                    "sources": dv["sources"],
                    **({"room_ratio": dv["room_ratio"], "bias": dv["bias"]}
                       if dv["kind"] == "NS1_SECOND" else {})})
                st["emitted"].append(did)
                plog(f"{sym}: EMIT {did} sources={dv['sources']} entry_bar={dv['entry_time']}")
            else:
                plog(f"{sym}: MISSED {did} entry_bar={dv['entry_time']} "
                     f"(current partial={cur_partial['time'] if cur_partial else None}) — not back-filled")
                st["emitted"].append(did)  # never reconsidered today
    if new_directives:
        kept = write_signals(new_directives)
        plog(f"signals file: +{len(new_directives)} producer directive(s), {kept} foreign kept")
    save_state(st)


def _current_partial(all_bars, day, now):
    for b in all_bars:
        start = datetime.combine(day, datetime.strptime(b["time"], "%H:%M").time(), IST)
        if start <= now < start + timedelta(minutes=5):
            return b
    return None


def _with_partial(done, all_bars):
    """done bars + the single next bar (the partial entry bar), if present."""
    if not done:
        return all_bars
    nxt = plus5(done[-1]["time"])
    extra = [b for b in all_bars if b["time"] == nxt]
    return done + extra[:1]


def _with_partial_other(other_bars, last_done_time):
    return [b for b in other_bars if b["time"] <= plus5(last_done_time)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="live evaluation for today")
    ap.add_argument("--reference", metavar="DATE", help="full-day EOD construction vs frozen files")
    ap.add_argument("--replay", metavar="DATE", help="causal step-through for a past day")
    ap.add_argument("--source", default="cache", choices=["cache", "api"])
    a = ap.parse_args()
    if a.once:
        cmd_once()
    elif a.reference:
        cmd_reference(ddate.fromisoformat(a.reference))
    elif a.replay:
        cmd_replay(ddate.fromisoformat(a.replay), a.source)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
