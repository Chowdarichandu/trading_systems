#!/usr/bin/env python3
"""PILLAR 2 (OPTION B) — Regime-Aware Index Option Convexity Engine.

Clean, non-overfit 5-rule index option buying engine (BANKNIFTY monthly +
NIFTY weekly/monthly) replacing fragmented 10-leg cell patches (B-FIX-1 /
N-FIX-1) with structural accuracy & execution upgrades from
AUDIT_AND_FIXES_2026-11-25.md:

  Rule 1 — Clean Opening-Range Breakout (09:30-11:30, 09:30 PE requires < PDL)
  Rule 2 — Bank Nifty Heavyweight Constituent Breadth (>= 60% weighted
           agreement across HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK)
  Rule 3 — Signal-Candle Exhaustion Guard (skip or wait for pullback when
           signal bar range > 1.8x 5-min ATR(14))
  Rule 4 — Macro Trend Regime (Spot vs 20-DMA + 5-day slope blocks counter-
           trend fades into strong thrusts) + Asymmetric Moneyness
           (1-strike ITM CE for lower theta/IV drag; ATM PE for convexity)
  Rule 5 — Volatility-Normalized Option Stops (-18% stop, +18% BE arm,
           +35% -> runner locking +20% / target +75%, min premium >= Rs 80,
           gap-aware bar-open fills, realistic NSE option taxes + 2pt/side
           slippage) + optional defined-risk Vertical Debit Spread mode.

Live mode also records real Upstox Bid/Ask spread telemetry at signal time
(pillar2_slippage_log.csv) and honors tripped circuit breakers.

PAPER ONLY. Real money Rs 0. Places ZERO broker orders.

Usage:
  # Offline deterministic self-test (verifies all 5 rules + spread + telemetry)
  python3 pillar2_index_options_apex.py --mode selftest

  # Historical backtest on live machine local stores (Baseline vs Apex vs Spread)
  python3 pillar2_index_options_apex.py --mode backtest --index BANKNIFTY
  python3 pillar2_index_options_apex.py --mode backtest --index ALL

  # Intraday live paper scan (09:30-11:35 IST; logs live Bid/Ask slippage)
  python3 pillar2_index_options_apex.py --mode live --index ALL

  # Same-evening EOD candle scorer (after 15:35 IST; v3 intraday fallback)
  python3 pillar2_index_options_apex.py --mode score --date 2026-11-26
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date as ddate, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import execution_risk_utils as ERU

IST = ZoneInfo("Asia/Kolkata")
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
INSTRUMENTS_URL = (
    "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
)

INDEX_CFG: Dict[str, Dict[str, Any]] = {
    "BANKNIFTY": {
        "spot_key": "NSE_INDEX|Nifty Bank",
        "master_name": "BANKNIFTY",
        "lot_size": 30,
        "strike_step": 100,
        "itm_offset_ce": 100,
        "spread_wing": 400,
        "prefer_monthly": True,
    },
    "NIFTY": {
        "spot_key": "NSE_INDEX|Nifty 50",
        "master_name": "NIFTY",
        "lot_size": 65,
        "strike_step": 50,
        "itm_offset_ce": 50,
        "spread_wing": 200,
        "prefer_monthly": False,
    },
}

BANK_HEAVYWEIGHTS = list(ERU.BANKNIFTY_TOP5_WEIGHTS.keys())

PAPER_LOG_COLS = [
    "trade_key", "date", "index", "structure", "direction", "strike",
    "wing_strike", "expiry", "signal_time", "entry_time", "spot_at_sig",
    "regime_label", "breadth_frac", "sig_atr_mult", "entry_premium",
    "stop_px", "target1_px", "exit_time", "exit_premium", "exit_reason",
    "lot_size", "gross_inr", "cost_inr", "net_inr", "status", "notes",
]

SLIPPAGE_COLS = [
    "timestamp_ist", "date", "index", "direction", "strike", "expiry",
    "instrument_key", "bar_open", "live_ltp", "best_bid", "best_ask",
    "spread_pts", "ask_minus_bar_open", "status",
]


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "data").exists():
        return live
    return THIS_DIR


def round_strike(spot: float, step: int) -> int:
    return int(round(spot / float(step)) * step)


def select_strikes(
    index: str, spot: float, direction: str, regime_label: str
) -> Tuple[int, int]:
    """Asymmetric moneyness: 1-strike ITM CE (lower IV/theta drag), ATM PE."""
    cfg = INDEX_CFG[index]
    step = cfg["strike_step"]
    atm = round_strike(spot, step)
    if direction == "CE":
        # ITM CE in bullish/neutral regimes; ATM in deep bear bounce
        long_k = atm - cfg["itm_offset_ce"] if regime_label != "STRONG_BEAR" else atm
        wing_k = long_k + cfg["spread_wing"]
    else:
        long_k = atm
        wing_k = long_k - cfg["spread_wing"]
    return long_k, wing_k


def plus5(t: str) -> str:
    h, m = int(t[:2]), int(t[3:5])
    m += 5
    if m >= 60:
        h, m = h + 1, m - 60
    return f"{h:02d}:{m:02d}"


# ---------------------------------------------------------------------------
# Upstox API Helpers (Read-only, Browser UA, HTTP 429 Hard Stop)
# ---------------------------------------------------------------------------
def _load_token(root: Path) -> str:
    env_p = root / "upstox_refresh" / ".env"
    if not env_p.exists():
        raise FileNotFoundError(f"Upstox token file not found: {env_p}")
    for line in env_p.read_text().splitlines():
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            tok = line.split("=", 1)[1].strip().strip('"').strip("'")
            if tok:
                return tok
    raise RuntimeError(f"UPSTOX_ACCESS_TOKEN missing in {env_p}")


def _api_get(path: str, token: str) -> Dict[str, Any]:
    url = "https://api.upstox.com" + path
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": UA,
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"HTTP 429 on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def load_nse_master(root: Path, force: bool = False) -> List[Dict[str, str]]:
    out_dir = root / "november_shadow_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    master = out_dir / "instruments_NSE.csv"
    stamp = out_dir / "instruments_stamp.txt"
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    if force or not master.exists() or (
        stamp.exists() and stamp.read_text().strip() != today_s
    ):
        req = urllib.request.Request(
            INSTRUMENTS_URL,
            headers={"Accept": "application/gzip", "User-Agent": UA},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            master.write_bytes(gzip.decompress(r.read()))
        stamp.write_text(today_s)
    with open(master, newline="") as f:
        return list(csv.DictReader(f))


def resolve_expiry_and_key(
    master_rows: Sequence[Dict[str, str]],
    index: str,
    trade_day: str,
    strike: int,
    direction: str,
    prefer_monthly: Optional[bool] = None,
) -> Tuple[Optional[str], Optional[str], int]:
    """Find active expiry >= trade_day, instrument_key, and lot_size from master."""
    cfg = INDEX_CFG[index]
    want_monthly = cfg["prefer_monthly"] if prefer_monthly is None else prefer_monthly
    uname = cfg["master_name"]

    exps = sorted({
        r["expiry"] for r in master_rows
        if r.get("name") == uname
        and r.get("instrument_type") == "OPTIDX"
        and (r.get("expiry") or "") >= trade_day
    })
    if not exps:
        return None, None, cfg["lot_size"]

    if want_monthly:
        # Monthly expiry = last expiry in the trade_day's calendar month (or next month)
        ym = trade_day[:7]
        in_month = [e for e in exps if e[:7] == ym]
        if in_month:
            chosen_exp = in_month[-1]
        else:
            nxt_ym = exps[0][:7]
            chosen_exp = [e for e in exps if e[:7] == nxt_ym][-1]
    else:
        chosen_exp = exps[0]

    for r in master_rows:
        if (
            r.get("name") == uname
            and r.get("expiry") == chosen_exp
            and r.get("instrument_type") == "OPTIDX"
            and (r.get("tradingsymbol") or "").endswith(direction)
            and abs(float(r.get("strike") or 0) - float(strike)) < 0.01
        ):
            lot = int(float(r.get("lot_size") or cfg["lot_size"]))
            return chosen_exp, r["instrument_key"], lot
    return chosen_exp, None, cfg["lot_size"]


def resolve_equity_keys(
    root: Path, master_rows: Optional[Sequence[Dict[str, str]]] = None
) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    uni = root / "universe_daily" / "universe.csv"
    if uni.exists():
        with open(uni, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("symbol") and r.get("instrument_key"):
                    keys[r["symbol"].strip()] = r["instrument_key"].strip()
    if master_rows:
        for r in master_rows:
            if r.get("exchange") == "NSE_EQ" and r.get("instrument_type") == "EQUITY":
                s = (r.get("tradingsymbol") or "").strip()
                k = (r.get("instrument_key") or "").strip()
                if s and k and s not in keys:
                    keys[s] = k
    return keys


def _parse_upstox_5m(payload: Dict[str, Any], day_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = (payload.get("data") or {}).get("candles") or []
    out: List[Dict[str, Any]] = []
    for r in rows:
        ts = str(r[0])
        d = ts[:10]
        if day_filter and d != day_filter:
            continue
        t = ts[11:16]
        if t < "09:15" or t > "15:25":
            continue
        out.append({
            "date": d, "time": t,
            "open": float(r[1]), "high": float(r[2]),
            "low": float(r[3]), "close": float(r[4]),
            "volume": float(r[5]) if len(r) > 5 and r[5] is not None else 0.0,
        })
    out.sort(key=lambda b: (b["date"], b["time"]))
    return out


def fetch_5m_day(
    instrument_key: str, day_s: str, token: str
) -> List[Dict[str, Any]]:
    """Fetch 5-min bars for `day_s`, using v3 intraday fallback when day_s == today."""
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    enc = urllib.parse.quote(instrument_key, safe="")
    if day_s == today_s:
        ip = _api_get(f"/v3/historical-candle/intraday/{enc}/minutes/5", token)
        bars = _parse_upstox_5m(ip, day_filter=day_s)
        if bars:
            return bars
    hp = _api_get(f"/v3/historical-candle/{enc}/minutes/5/{day_s}/{day_s}", token)
    return _parse_upstox_5m(hp, day_filter=day_s)


def fetch_live_option_quote(
    instrument_key: str, token: str
) -> Optional[Dict[str, float]]:
    """Query live market quote for Bid/Ask spread telemetry (paper-only read)."""
    enc = urllib.parse.quote(instrument_key, safe="")
    try:
        payload = _api_get(f"/v2/market-quote/quotes?instrument_key={enc}", token)
        data = payload.get("data") or {}
        if not data:
            return None
        q = next(iter(data.values()))
        ltp = float(q.get("last_price") or 0.0)
        depth = q.get("depth") or {}
        buys = depth.get("buy") or []
        sells = depth.get("sell") or []
        bid = float(buys[0].get("price") or 0.0) if buys else 0.0
        ask = float(sells[0].get("price") or 0.0) if sells else 0.0
        spread = round(ask - bid, 2) if (ask > 0 and bid > 0) else -1.0
        return {"ltp": ltp, "bid": bid, "ask": ask, "spread": spread}
    except RateLimited:
        raise
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Local Historical Store Loaders (for Backtesting on Live Machine)
# ---------------------------------------------------------------------------
def load_local_5m_by_day(root: Path, sym: str) -> Dict[str, List[Dict[str, Any]]]:
    candidates = [
        root / "data" / "progressive" / sym / "spot_5m.csv",
        root / "data" / "sarvaritu_fwd" / sym / "spot_5m.csv",
        root / "data" / "tarang_vol" / sym / "spot_5m_vol.csv",
        root / "data" / "sapta_vol" / sym / "spot_5m_vol.csv",
    ]
    by_day: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for p in candidates:
        if not p.exists():
            continue
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                ts = r.get("timestamp") or ""
                if len(ts) < 16:
                    continue
                d, t = ts[:10], ts[11:16]
                if t < "09:15" or t > "15:25":
                    continue
                by_day[d][t] = {
                    "date": d, "time": t,
                    "open": float(r["open"]), "high": float(r["high"]),
                    "low": float(r["low"]), "close": float(r["close"]),
                    "volume": float(r.get("volume") or 0.0),
                }
    return {
        d: [by_day[d][t] for t in sorted(by_day[d])]
        for d in sorted(by_day)
    }


def load_local_option_bars(
    root: Path, index: str, strike: int, direction: str, day_s: str, expiry: Optional[str] = None
) -> Tuple[Optional[str], List[Tuple[str, float, float, float, float]]]:
    """Search local option caches (oi_buildup_data, november_shadow_data, aggressive_data)."""
    search_dirs = [
        root / "november_shadow_data",
        root / "oi_buildup_data",
        root / "aggressive_data",
        root / "daily2leg",
    ]
    patterns = []
    if expiry:
        patterns.extend([
            f"candles_{index}_{int(strike)}{direction}_{day_s}_{expiry}.json",
            f"candles_{index}_{int(strike)}{direction}_{expiry}_{day_s}.json",
        ])
    else:
        patterns.extend([
            f"candles_{index}_{int(strike)}{direction}_{day_s}_*.json",
            f"candles_{index}_{int(strike)}{direction}_*_{day_s}.json",
        ])

    for d in search_dirs:
        if not d.exists():
            continue
        for pat in patterns:
            matches = sorted(d.glob(pat))
            if not matches:
                continue
            p = matches[0]
            try:
                body = json.loads(p.read_text())
                raw = (body.get("data") or {}).get("candles") or []
                bars = []
                for c in raw:
                    if str(c[0])[:10] == day_s:
                        bars.append((
                            str(c[0])[11:16], float(c[1]), float(c[2]),
                            float(c[3]), float(c[4]),
                        ))
                if bars:
                    bars.sort(key=lambda x: x[0])
                    # Extract expiry from filename if not provided
                    exp_found = expiry
                    if not exp_found:
                        parts = p.stem.split("_")
                        cands = [x for x in parts if len(x) == 10 and x != day_s and x[4] == "-"]
                        exp_found = cands[0] if cands else "UNKNOWN"
                    return exp_found, bars
            except Exception:
                continue
    return None, []


# ---------------------------------------------------------------------------
# Core Causal Signal & Execution Engine (Rules 1-5)
# ---------------------------------------------------------------------------
def compute_macro_regime(
    daily_closes: Sequence[Tuple[str, float]], target_day: str
) -> Dict[str, Any]:
    """Compute causal macro trend regime strictly from completed days < target_day."""
    prior = [c for d, c in daily_closes if d < target_day]
    if len(prior) < 20:
        return {"label": "NEUTRAL", "sma20": None, "ret_5d_pct": 0.0, "prev_close": prior[-1] if prior else None}
    prev_c = prior[-1]
    sma20 = sum(prior[-20:]) / 20.0
    ret_5d = ((prev_c / prior[-6]) - 1.0) * 100.0 if len(prior) >= 6 else 0.0
    if prev_c > sma20 and ret_5d >= 1.5:
        lbl = "STRONG_BULL"
    elif prev_c < sma20 and ret_5d <= -1.5:
        lbl = "STRONG_BEAR"
    elif prev_c >= sma20:
        lbl = "BULL"
    else:
        lbl = "BEAR"
    return {
        "label": lbl,
        "prev_close": round(prev_c, 2),
        "sma20": round(sma20, 2),
        "ret_5d_pct": round(ret_5d, 2),
    }


def compute_5m_atr(
    prior_day_bars: Sequence[Dict[str, Any]],
    today_bars_before_sig: Sequence[Dict[str, Any]],
    period: int = 14,
) -> float:
    """Compute causal 5-min ATR(14) strictly BEFORE the signal bar."""
    seq = list(prior_day_bars[-20:]) + list(today_bars_before_sig)
    if len(seq) < 3:
        return 0.0
    trs: List[float] = [seq[0]["high"] - seq[0]["low"]]
    for i in range(1, len(seq)):
        h, l, pc = seq[i]["high"], seq[i]["low"], seq[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if len(trs) <= period:
        return sum(trs) / len(trs)
    val = sum(trs[:period]) / period
    for tr in trs[period:]:
        val = (val * (period - 1) + tr) / period
    return val


def score_constituent_votes(
    constituent_bars: Dict[str, List[Dict[str, Any]]],
    upto_time: str,
) -> Dict[str, int]:
    """Score Bank Nifty top-5 constituents (+1 bullish, -1 bearish, 0 neutral)
    causally using completed bars <= upto_time."""
    votes: Dict[str, int] = {}
    for sym, bars in constituent_bars.items():
        sub = [b for b in bars if b["time"] <= upto_time]
        if not sub:
            continue
        open_915 = sub[0]["open"]
        # Session VWAP (or typical-price average if volume missing)
        tot_v = sum(b.get("volume", 0.0) for b in sub)
        if tot_v > 0:
            vwap = sum(((b["high"] + b["low"] + b["close"]) / 3.0) * b.get("volume", 0.0) for b in sub) / tot_v
        else:
            vwap = sum((b["high"] + b["low"] + b["close"]) / 3.0 for b in sub) / len(sub)
        or_sub = [b for b in sub if b["time"] < "09:30"]
        or_mid = (
            (max(b["high"] for b in or_sub) + min(b["low"] for b in or_sub)) / 2.0
            if or_sub else open_915
        )
        last_c = sub[-1]["close"]
        if last_c > vwap and last_c > open_915 and last_c >= or_mid:
            votes[sym] = 1
        elif last_c < vwap and last_c < open_915 and last_c <= or_mid:
            votes[sym] = -1
        else:
            votes[sym] = 0
    return votes


def evaluate_day_signal(
    index: str,
    today_bars: Sequence[Dict[str, Any]],
    prev_daily: Dict[str, float],
    prior_5m_bars: Sequence[Dict[str, Any]],
    macro_regime: Dict[str, Any],
    constituent_bars: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    *,
    use_breadth: bool = True,
    min_breadth_share: float = 0.60,
    max_atr_mult: float = 1.8,
    use_regime_guard: bool = True,
    exhaustion_mode: str = "skip",
) -> Dict[str, Any]:
    """Evaluate Rules 1-4 strictly causally on completed 5-min spot bars."""
    or_bars = [b for b in today_bars if b["time"] < "09:30"]
    if not or_bars:
        return {"decision": "NO_SIGNAL", "reason": "no_opening_range"}
    orh = max(b["high"] for b in or_bars)
    orl = min(b["low"] for b in or_bars)

    # Rule 1: First OR break in 09:30..11:30
    sig_idx = None
    direction = None
    for i, b in enumerate(today_bars):
        if b["time"] < "09:30" or b["time"] > "11:30":
            continue
        if b["close"] > orh:
            sig_idx, direction = i, "CE"
            break
        if b["close"] < orl:
            sig_idx, direction = i, "PE"
            break
    if sig_idx is None or direction is None:
        return {"decision": "NO_SIGNAL", "reason": "no_or_break_0930_1130"}

    sig = today_bars[sig_idx]
    sig_time = sig["time"]

    # 09:30 PE first-bar guard
    if direction == "PE" and sig_time == "09:30" and sig["close"] >= prev_daily["low"]:
        return {
            "decision": "BLOCKED", "reason": "0930_pe_above_pdl",
            "direction": direction, "signal_time": sig_time,
        }

    # Rule 2: Bank Nifty Top-5 Constituent Breadth
    breadth_frac: Optional[float] = None
    breadth_votes: Dict[str, int] = {}
    if index == "BANKNIFTY" and use_breadth:
        if constituent_bars:
            breadth_votes = score_constituent_votes(constituent_bars, sig_time)
            avail_w = sum(
                ERU.BANKNIFTY_TOP5_WEIGHTS[s]
                for s in breadth_votes
                if s in ERU.BANKNIFTY_TOP5_WEIGHTS
            )
            if avail_w >= 0.40:
                ok_b, breadth_frac = ERU.banknifty_breadth_aligned(
                    breadth_votes, direction, min_weight_share=min_breadth_share
                )
                if not ok_b:
                    return {
                        "decision": "BLOCKED",
                        "reason": f"breadth_disagree_{breadth_frac:.2f}",
                        "direction": direction, "signal_time": sig_time,
                        "breadth_frac": breadth_frac, "breadth_votes": breadth_votes,
                    }

    # Rule 3: Signal-Candle Exhaustion Guard
    atr_5m = compute_5m_atr(prior_5m_bars, today_bars[:sig_idx], period=14)
    bar_rng = sig["high"] - sig["low"]
    atr_mult = round(bar_rng / atr_5m, 2) if atr_5m > 0 else 0.0
    entry_time = plus5(sig_time)
    exhausted = ERU.is_signal_bar_exhausted(
        sig["high"], sig["low"], atr_5m, max_atr_multiple=max_atr_mult
    )
    if exhausted:
        if exhaustion_mode == "skip":
            return {
                "decision": "BLOCKED",
                "reason": f"exhausted_bar_{atr_mult:.2f}x_atr",
                "direction": direction, "signal_time": sig_time,
                "breadth_frac": breadth_frac, "sig_atr_mult": atr_mult,
            }
        # Optional retrace mode: wait up to 3 bars for 35% pullback into signal bar
        retrace_lvl = (
            sig["high"] - 0.35 * bar_rng if direction == "CE"
            else sig["low"] + 0.35 * bar_rng
        )
        found_retrace = False
        for k in range(sig_idx + 1, min(sig_idx + 4, len(today_bars))):
            bk = today_bars[k]
            if (direction == "CE" and bk["low"] <= retrace_lvl) or (
                direction == "PE" and bk["high"] >= retrace_lvl
            ):
                entry_time = plus5(bk["time"])
                found_retrace = True
                break
        if not found_retrace:
            return {
                "decision": "BLOCKED",
                "reason": f"exhausted_no_retrace_{atr_mult:.2f}x_atr",
                "direction": direction, "signal_time": sig_time,
                "breadth_frac": breadth_frac, "sig_atr_mult": atr_mult,
            }

    # Rule 4: Macro Trend Regime Counter-Trend Guard
    reg_lbl = macro_regime.get("label", "NEUTRAL")
    if use_regime_guard:
        if reg_lbl == "STRONG_BULL" and direction == "PE":
            strong_bear_override = (
                sig["close"] < prev_daily["low"]
                and (breadth_frac is None or breadth_frac >= 0.75)
            )
            if not strong_bear_override:
                return {
                    "decision": "BLOCKED",
                    "reason": "counter_trend_pe_in_strong_bull",
                    "direction": direction, "signal_time": sig_time,
                    "regime_label": reg_lbl, "breadth_frac": breadth_frac,
                    "sig_atr_mult": atr_mult,
                }
        elif reg_lbl == "STRONG_BEAR" and direction == "CE":
            strong_bull_override = (
                sig["close"] > prev_daily["high"]
                and (breadth_frac is None or breadth_frac >= 0.75)
            )
            if not strong_bull_override:
                return {
                    "decision": "BLOCKED",
                    "reason": "counter_trend_ce_in_strong_bear",
                    "direction": direction, "signal_time": sig_time,
                    "regime_label": reg_lbl, "breadth_frac": breadth_frac,
                    "sig_atr_mult": atr_mult,
                }

    long_k, wing_k = select_strikes(index, sig["close"], direction, reg_lbl)
    return {
        "decision": "SIGNAL",
        "reason": "passed_all_rules",
        "index": index,
        "direction": direction,
        "signal_time": sig_time,
        "entry_time": entry_time,
        "spot_at_sig": round(sig["close"], 2),
        "strike": long_k,
        "wing_strike": wing_k,
        "regime_label": reg_lbl,
        "breadth_frac": breadth_frac,
        "breadth_votes": breadth_votes,
        "sig_atr_mult": atr_mult,
    }


def replay_apex_option(
    bars: Sequence[Tuple[str, float, float, float, float]],
    entry_time: str,
    lot_size: int,
    *,
    stop_pct: float = 0.18,
    target_pct: float = 0.35,
    be_arm_pct: float = 0.18,
    runner_lock_pct: float = 0.20,
    runner_tgt2_pct: float = 0.75,
    min_premium: float = 80.0,
    sq_time: str = "15:15",
    slippage_pts_per_side: float = 2.0,
) -> Dict[str, Any]:
    """Rule 5: Volatility-normalized option levels + gap-aware realistic replay."""
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return {"status": "NC", "reason": "missing_entry_bar"}
    entry = float(bs[0][1])
    lvls = ERU.normalized_option_levels(
        entry, stop_pct=stop_pct, target_pct=target_pct, min_premium_inr=min_premium
    )
    if lvls is None:
        return {
            "status": "BLOCKED",
            "reason": f"low_premium_{entry:.2f}_lt_{min_premium:.0f}",
            "entry": entry,
        }
    stop_px, target1_px = lvls
    res = ERU.replay_option_realistic(
        bars=bars,
        entry_time=entry_time,
        lot_size=lot_size,
        stop_px=stop_px,
        target_px=target1_px,
        sq_time=sq_time,
        be_arm_pts=round(entry * be_arm_pct, 2),
        runner_lock_pts=round(entry * runner_lock_pct, 2),
        runner_target2_pts=round(entry * runner_tgt2_pct, 2),
        slippage_pts_per_side=slippage_pts_per_side,
    )
    if res is None:
        return {"status": "NC", "reason": "replay_none"}
    return {
        "status": "TAKEN",
        "stop_px": stop_px,
        "target1_px": target1_px,
        **res,
    }


def replay_debit_spread(
    long_bars: Sequence[Tuple[str, float, float, float, float]],
    short_bars: Sequence[Tuple[str, float, float, float, float]],
    entry_time: str,
    lot_size: int,
    *,
    stop_debit_pct: float = 0.35,
    target_debit_pct: float = 0.65,
    min_debit: float = 35.0,
    sq_time: str = "15:15",
    slippage_pts_per_side: float = 1.5,
) -> Dict[str, Any]:
    """Defined-risk vertical debit spread (long K1 + short OTM wing K2)."""
    lm = {b[0]: b for b in long_bars if b[0] >= entry_time}
    sm = {b[0]: b for b in short_bars if b[0] >= entry_time}
    times = sorted(t for t in lm if t in sm and t <= sq_time)
    if not times or times[0] != entry_time:
        return {"status": "NC", "reason": "missing_spread_entry_bar"}

    l_en = float(lm[entry_time][1])
    s_en = float(sm[entry_time][1])
    debit = round(l_en - s_en, 2)
    if debit < min_debit:
        return {"status": "BLOCKED", "reason": f"spread_debit_{debit:.2f}_lt_{min_debit:.0f}"}

    stop_val = max(round(debit * (1.0 - stop_debit_pct), 2), 0.05)
    target_val = round(debit * (1.0 + target_debit_pct), 2)

    def _finish(l_ex: float, s_ex: float, reason: str, t: str) -> Dict[str, Any]:
        c1 = ERU.index_option_cost(l_en, max(l_ex, 0.05), lot_size, slippage_pts_per_side=slippage_pts_per_side)
        c2 = ERU.index_option_cost(max(s_ex, 0.05), s_en, lot_size, slippage_pts_per_side=slippage_pts_per_side)
        total_cost = round(c1["total_cost_inr"] + c2["total_cost_inr"], 2)
        exit_spread = round(l_ex - s_ex, 2)
        gross = round((exit_spread - debit) * lot_size, 2)
        return {
            "status": "TAKEN",
            "entry": debit,
            "stop_px": stop_val,
            "target1_px": target_val,
            "exit": exit_spread,
            "exit_time": t,
            "exit_reason": reason,
            "gross_inr": gross,
            "cost_inr": total_cost,
            "net_inr": round(gross - total_cost, 2),
        }

    for t in times:
        _, lo, lh, ll, lc = lm[t]
        _, so, sh, sl, sc = sm[t]
        sp_open = lo - so
        sp_close = lc - sc
        # Conservative bar check using open then close (spread legs aren't synchronized at extremes)
        if sp_open <= stop_val:
            return _finish(lo, so, "spread_gap_stop", t)
        if sp_close <= stop_val:
            return _finish(lc, sc, "spread_stop", t)
        if sp_open >= target_val:
            return _finish(lo, so, "spread_target", t)
        if sp_close >= target_val:
            return _finish(lc, sc, "spread_target", t)
        if t == sq_time:
            return _finish(lc, sc, "spread_square_off", t)
    lt = times[-1]
    return _finish(lm[lt][4], sm[lt][4], "spread_square_off", lt)


# ---------------------------------------------------------------------------
# Backtest Mode (runs on live machine local stores: Baseline vs Apex)
# ---------------------------------------------------------------------------
def _summarize_opt(trades: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    taken = [t for t in trades if t.get("status") == "TAKEN"]
    if not taken:
        return {"trades": 0, "win_rate_pct": None, "gross_inr": 0.0, "cost_inr": 0.0,
                "net_inr": 0.0, "max_dd_inr": 0.0, "worst_inr": 0.0}
    nets = [float(t["net_inr"]) for t in taken]
    wins = sum(1 for x in nets if x > 0)
    eq = peak = mdd = 0.0
    for x in nets:
        eq += x
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    return {
        "trades": len(taken),
        "win_rate_pct": round(100.0 * wins / len(taken), 2),
        "gross_inr": round(sum(float(t["gross_inr"]) for t in taken), 2),
        "cost_inr": round(sum(float(t["cost_inr"]) for t in taken), 2),
        "net_inr": round(sum(nets), 2),
        "max_dd_inr": round(mdd, 2),
        "worst_inr": round(min(nets), 2),
        "ce_net": round(sum(float(t["net_inr"]) for t in taken if t["direction"] == "CE"), 2),
        "pe_net": round(sum(float(t["net_inr"]) for t in taken if t["direction"] == "PE"), 2),
        "exit_reasons": dict(Counter(t["exit_reason"] for t in taken)),
    }


def run_backtest(
    root: Path,
    indices: Sequence[str],
    date_from: str,
    date_to: str,
    structure: str = "naked",
) -> int:
    # Load Bank Nifty top-5 constituent 5-min bars once
    const_by_sym: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for sym in BANK_HEAVYWEIGHTS:
        m = load_local_5m_by_day(root, sym)
        if m:
            const_by_sym[sym] = m

    report: Dict[str, Any] = {
        "generated_at": datetime.now(IST).isoformat(),
        "root": str(root),
        "date_range": [date_from, date_to],
        "structure": structure,
        "constituents_loaded": sorted(const_by_sym.keys()),
        "indices": {},
    }
    all_apex_rows: List[Dict[str, Any]] = []

    for idx in indices:
        cfg = INDEX_CFG[idx]
        by_day = load_local_5m_by_day(root, idx)
        if not by_day:
            print(f"NO LOCAL 5-MIN SPOT DATA for {idx} under {root}/data/progressive/{idx}/spot_5m.csv")
            report["indices"][idx] = {"status": "NO_LOCAL_DATA"}
            continue
        days = sorted(by_day.keys())
        daily_ohlc = {
            d: {
                "open": by_day[d][0]["open"],
                "high": max(b["high"] for b in by_day[d]),
                "low": min(b["low"] for b in by_day[d]),
                "close": by_day[d][-1]["close"],
            }
            for d in days
        }
        daily_closes = [(d, daily_ohlc[d]["close"]) for d in days]

        base_trades: List[Dict[str, Any]] = []
        apex_trades: List[Dict[str, Any]] = []
        block_counts = Counter()

        for di in range(1, len(days)):
            d = days[di]
            if d < date_from or d > date_to:
                continue
            prev_d = days[di - 1]
            prev_daily = daily_ohlc[prev_d]
            prior_5m = by_day[prev_d]
            today_5m = by_day[d]
            macro = compute_macro_regime(daily_closes, d)
            day_const = (
                {s: m[d] for s, m in const_by_sym.items() if d in m}
                if idx == "BANKNIFTY" else None
            )

            # 1. Baseline raw ORB (no breadth, no exhaustion, no regime guard, fixed -50/+90)
            sig_base = evaluate_day_signal(
                idx, today_5m, prev_daily, prior_5m, macro, None,
                use_breadth=False, max_atr_mult=99.0, use_regime_guard=False,
            )
            if sig_base["decision"] == "SIGNAL":
                k_atm = round_strike(sig_base["spot_at_sig"], cfg["strike_step"])
                exp_b, opt_b = load_local_option_bars(root, idx, k_atm, sig_base["direction"], d)
                if opt_b:
                    bs = [b for b in opt_b if b[0] >= sig_base["entry_time"]]
                    if bs and bs[0][0] == sig_base["entry_time"]:
                        en = bs[0][1]
                        rr = ERU.replay_option_realistic(
                            opt_b, sig_base["entry_time"], cfg["lot_size"],
                            stop_px=max(en - 50.0, 0.05), target_px=en + 90.0,
                            sq_time="15:10",
                        )
                        if rr:
                            base_trades.append({
                                "date": d, "index": idx, "direction": sig_base["direction"],
                                "status": "TAKEN", **rr,
                            })

            # 2. Apex Pillar 2 (all 5 rules)
            sig_ap = evaluate_day_signal(
                idx, today_5m, prev_daily, prior_5m, macro, day_const,
                use_breadth=True, min_breadth_share=0.60,
                max_atr_mult=1.8, use_regime_guard=True,
            )
            if sig_ap["decision"] != "SIGNAL":
                block_counts[sig_ap["reason"]] += 1
                continue

            exp_a, opt_a = load_local_option_bars(
                root, idx, sig_ap["strike"], sig_ap["direction"], d
            )
            if not opt_a:
                # Fallback to ATM if ITM-100 wasn't cached historically
                k_atm = round_strike(sig_ap["spot_at_sig"], cfg["strike_step"])
                exp_a, opt_a = load_local_option_bars(root, idx, k_atm, sig_ap["direction"], d)
                if opt_a:
                    sig_ap["strike"] = k_atm
            if not opt_a:
                block_counts["option_cache_missing"] += 1
                continue

            if structure == "debit_spread":
                _, wing_b = load_local_option_bars(
                    root, idx, sig_ap["wing_strike"], sig_ap["direction"], d, expiry=exp_a
                )
                if not wing_b:
                    block_counts["wing_cache_missing"] += 1
                    continue
                res = replay_debit_spread(opt_a, wing_b, sig_ap["entry_time"], cfg["lot_size"])
            else:
                res = replay_apex_option(opt_a, sig_ap["entry_time"], cfg["lot_size"])

            if res["status"] != "TAKEN":
                block_counts[res.get("reason", res["status"])] += 1
                continue

            row = {
                "trade_key": f"P2|{d}|{idx}|{sig_ap['direction']}|{sig_ap['strike']}",
                "date": d, "index": idx, "structure": structure,
                "direction": sig_ap["direction"], "strike": sig_ap["strike"],
                "wing_strike": sig_ap["wing_strike"] if structure == "debit_spread" else "",
                "expiry": exp_a or "", "signal_time": sig_ap["signal_time"],
                "entry_time": sig_ap["entry_time"], "spot_at_sig": sig_ap["spot_at_sig"],
                "regime_label": sig_ap["regime_label"],
                "breadth_frac": sig_ap["breadth_frac"] if sig_ap["breadth_frac"] is not None else "",
                "sig_atr_mult": sig_ap["sig_atr_mult"],
                "entry_premium": res["entry"], "stop_px": res["stop_px"],
                "target1_px": res["target1_px"], "exit_time": res["exit_time"],
                "exit_premium": res["exit"], "exit_reason": res["exit_reason"],
                "lot_size": cfg["lot_size"], "gross_inr": res["gross_inr"],
                "cost_inr": res["cost_inr"], "net_inr": res["net_inr"],
                "status": "TAKEN", "notes": "paper backtest, realistic NSE costs",
            }
            apex_trades.append(row)
            all_apex_rows.append(row)

        report["indices"][idx] = {
            "days_scanned": sum(1 for d in days if date_from <= d <= date_to),
            "baseline_raw_orb": _summarize_opt(base_trades),
            "apex_pillar2": _summarize_opt(apex_trades),
            "blocked_breakdown": dict(block_counts.most_common(12)),
        }

    (root / "pillar2_backtest_report.json").write_text(json.dumps(report, indent=2))
    if all_apex_rows:
        with open(root / "pillar2_backtest_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=PAPER_LOG_COLS)
            w.writeheader()
            for r in all_apex_rows:
                w.writerow(r)

    print(f"\nPILLAR 2 BACKTEST ({date_from} -> {date_to}, structure={structure}, constituents={report['constituents_loaded']})")
    for idx, blk in report["indices"].items():
        if blk.get("status") == "NO_LOCAL_DATA":
            continue
        b, a = blk["baseline_raw_orb"], blk["apex_pillar2"]
        print(f"\n  {idx} ({blk['days_scanned']} sessions):")
        print(f"    BASELINE RAW ORB (-50/+90, real cost): {b['trades']:>3} tr | WR {str(b['win_rate_pct']):>5}% | Net Rs {b['net_inr']:>+10,.0f} | MaxDD Rs {b['max_dd_inr']:>+9,.0f}")
        print(f"    APEX PILLAR 2 (5 rules, real cost)   : {a['trades']:>3} tr | WR {str(a['win_rate_pct']):>5}% | Net Rs {a['net_inr']:>+10,.0f} | MaxDD Rs {a['max_dd_inr']:>+9,.0f} (CE {a.get('ce_net',0):+,.0f} / PE {a.get('pe_net',0):+,.0f})")
        print(f"    Blocked/filtered breakdown           : {blk['blocked_breakdown']}")
    return 0


# ---------------------------------------------------------------------------
# Live Intraday Scanner & Same-Evening EOD Scorer
# ---------------------------------------------------------------------------
def _breaker_paused(root: Path) -> Tuple[bool, str]:
    for fname in ("pillar2_breaker_state.json", "breaker_state_stack.json"):
        p = root / fname
        if p.exists():
            try:
                st = json.loads(p.read_text())
                if st.get("currently_paused"):
                    return True, f"{fname}:{st.get('pause_kind') or 'PAUSED'}"
            except Exception:
                pass
    return False, ""


def _append_csv_idempotent(path: Path, fieldnames: Sequence[str], key_col: str, rows: List[Dict[str, Any]]) -> int:
    seen = set()
    existing: List[Dict[str, Any]] = []
    if path.exists():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                seen.add(r[key_col])
                existing.append(r)
    added = 0
    for r in rows:
        if r[key_col] in seen:
            continue
        seen.add(r[key_col])
        existing.append(r)
        added += 1
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in existing:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    os.replace(tmp, path)
    return added


def _fetch_recent_daily_index(index: str, target_day: str, token: str) -> List[Tuple[str, float, float, float]]:
    """Fetch last ~45 calendar days of index daily bars (strictly < target_day)."""
    enc = urllib.parse.quote(INDEX_CFG[index]["spot_key"], safe="")
    frm = (ddate.fromisoformat(target_day) - timedelta(days=50)).isoformat()
    to_d = (ddate.fromisoformat(target_day) - timedelta(days=1)).isoformat()
    payload = _api_get(f"/v3/historical-candle/{enc}/days/1/{to_d}/{frm}", token)
    rows = (payload.get("data") or {}).get("candles") or []
    out = [
        (str(r[0])[:10], float(r[2]), float(r[3]), float(r[4]))
        for r in rows if str(r[0])[:10] < target_day
    ]
    out.sort(key=lambda x: x[0])
    return out


def run_live_or_score(
    root: Path,
    mode: str,
    indices: Sequence[str],
    target_day: str,
    structure: str = "naked",
    max_spread_pts: float = 4.0,
    dry_run: bool = False,
) -> int:
    token = _load_token(root)
    master = load_nse_master(root)
    eq_keys = resolve_equity_keys(root, master)
    paused, pause_src = _breaker_paused(root)

    # Fetch Bank Nifty top-5 constituents once if BANKNIFTY is requested
    const_bars: Dict[str, List[Dict[str, Any]]] = {}
    if "BANKNIFTY" in indices:
        for sym in BANK_HEAVYWEIGHTS:
            ik = eq_keys.get(sym)
            if not ik:
                continue
            const_bars[sym] = fetch_5m_day(ik, target_day, token)
            time.sleep(0.20)

    out_signals: List[Dict[str, Any]] = []
    scored_rows: List[Dict[str, Any]] = []
    slip_rows: List[Dict[str, Any]] = []
    now_ist = datetime.now(IST)

    for idx in indices:
        cfg = INDEX_CFG[idx]
        today_bars = fetch_5m_day(cfg["spot_key"], target_day, token)
        time.sleep(0.20)
        # Exclude in-progress 5-min bar in live mode (strictly causal!)
        if mode == "live" and target_day == now_ist.strftime("%Y-%m-%d"):
            cur_slot = f"{now_ist.hour:02d}:{(now_ist.minute // 5) * 5:02d}"
            completed = [b for b in today_bars if b["time"] < cur_slot]
        else:
            completed = list(today_bars)

        daily_hist = _fetch_recent_daily_index(idx, target_day, token)
        time.sleep(0.20)
        if not daily_hist:
            print(f"[{idx}] NC: unable to fetch prior daily candles")
            continue
        prev_day_s, prev_h, prev_l, prev_c = daily_hist[-1]
        prev_daily = {"high": prev_h, "low": prev_l, "close": prev_c}
        prior_5m = fetch_5m_day(cfg["spot_key"], prev_day_s, token)
        time.sleep(0.20)
        macro = compute_macro_regime([(d, c) for d, _, _, c in daily_hist], target_day)

        sig = evaluate_day_signal(
            idx, completed, prev_daily, prior_5m, macro,
            const_bars if idx == "BANKNIFTY" else None,
        )
        print(f"[{idx} {target_day}] {sig['decision']} ({sig['reason']}) | regime={macro['label']} "
              f"breadth={sig.get('breadth_frac')} atr_mult={sig.get('sig_atr_mult')}")

        if sig["decision"] != "SIGNAL":
            if mode == "score":
                scored_rows.append({
                    "trade_key": f"P2|{target_day}|{idx}|NONE",
                    "date": target_day, "index": idx, "structure": structure,
                    "direction": "", "strike": "", "wing_strike": "", "expiry": "",
                    "signal_time": sig.get("signal_time", ""), "entry_time": "",
                    "spot_at_sig": "", "regime_label": macro["label"],
                    "breadth_frac": sig.get("breadth_frac", ""),
                    "sig_atr_mult": sig.get("sig_atr_mult", ""),
                    "entry_premium": "", "stop_px": "", "target1_px": "",
                    "exit_time": "", "exit_premium": "", "exit_reason": "",
                    "lot_size": cfg["lot_size"], "gross_inr": "", "cost_inr": "",
                    "net_inr": "", "status": sig["decision"],
                    "notes": f"{sig['reason']} · paper only, real money Rs0",
                })
            continue

        exp, opt_key, lot = resolve_expiry_and_key(
            master, idx, target_day, sig["strike"], sig["direction"]
        )
        if not opt_key:
            print(f"  [{idx}] NC: option instrument_key not found for {sig['strike']}{sig['direction']} {exp}")
            continue

        if mode == "live":
            q = fetch_live_option_quote(opt_key, token)
            opt_bars_now = fetch_5m_day(opt_key, target_day, token)
            eb = next((b for b in opt_bars_now if b["time"] == sig["entry_time"]), None)
            bar_open = eb["open"] if eb else (q["ltp"] if q else 0.0)
            ref_px = q["ask"] if (q and q["ask"] > 0) else bar_open
            lvls = ERU.normalized_option_levels(ref_px, stop_pct=0.18, target_pct=0.35, min_premium_inr=80.0)
            status = "ACTIVE"
            cur_slot = f"{now_ist.hour:02d}:{(now_ist.minute // 5) * 5:02d}"
            if paused:
                status = f"BREAKER_PAUSED({pause_src})"
            elif target_day == now_ist.strftime("%Y-%m-%d") and cur_slot > sig["entry_time"]:
                status = f"STALE_SIGNAL(entry_was_{sig['entry_time']})"
            elif lvls is None:
                status = f"BLOCKED_LOW_PREM({ref_px:.2f})"
            elif q and q["spread"] > max_spread_pts:
                status = f"BLOCKED_WIDE_SPREAD({q['spread']:.2f})"
            directive = {
                "timestamp_ist": now_ist.isoformat(),
                "date": target_day, "index": idx, "structure": structure,
                "direction": sig["direction"], "strike": sig["strike"],
                "wing_strike": sig["wing_strike"], "expiry": exp,
                "instrument_key": opt_key, "lot_size": lot,
                "signal_time": sig["signal_time"], "entry_time": sig["entry_time"],
                "regime_label": macro["label"], "breadth_frac": sig.get("breadth_frac"),
                "breadth_votes": sig.get("breadth_votes"),
                "sig_atr_mult": sig.get("sig_atr_mult"),
                "ref_premium": round(ref_px, 2),
                "stop_px": lvls[0] if lvls else None,
                "target1_px": lvls[1] if lvls else None,
                "live_quote": q, "status": status,
                "paper_only": True,
            }
            out_signals.append(directive)
            if q:
                slip_rows.append({
                    "timestamp_ist": now_ist.isoformat(), "date": target_day,
                    "index": idx, "direction": sig["direction"],
                    "strike": sig["strike"], "expiry": exp,
                    "instrument_key": opt_key, "bar_open": round(bar_open, 2),
                    "live_ltp": q["ltp"], "best_bid": q["bid"], "best_ask": q["ask"],
                    "spread_pts": q["spread"],
                    "ask_minus_bar_open": round(q["ask"] - bar_open, 2) if (q["ask"] > 0 and bar_open > 0) else "",
                    "status": status,
                })
            print(f"  -> DIRECTIVE [{status}]: BUY {idx} {sig['strike']}{sig['direction']} ({exp}) "
                  f"ref={ref_px:.2f} stop={directive['stop_px']} tgt1={directive['target1_px']} quote={q}")
        else:
            # EOD candle score mode
            opt_5m = fetch_5m_day(opt_key, target_day, token)
            opt_tuples = [(b["time"], b["open"], b["high"], b["low"], b["close"]) for b in opt_5m]
            if structure == "debit_spread":
                _, wing_key, _ = resolve_expiry_and_key(
                    master, idx, target_day, sig["wing_strike"], sig["direction"]
                )
                wing_5m = fetch_5m_day(wing_key, target_day, token) if wing_key else []
                wing_tuples = [(b["time"], b["open"], b["high"], b["low"], b["close"]) for b in wing_5m]
                res = replay_debit_spread(opt_tuples, wing_tuples, sig["entry_time"], lot)
            else:
                res = replay_apex_option(opt_tuples, sig["entry_time"], lot)
            scored_rows.append({
                "trade_key": f"P2|{target_day}|{idx}|{sig['direction']}|{sig['strike']}",
                "date": target_day, "index": idx, "structure": structure,
                "direction": sig["direction"], "strike": sig["strike"],
                "wing_strike": sig["wing_strike"] if structure == "debit_spread" else "",
                "expiry": exp or "", "signal_time": sig["signal_time"],
                "entry_time": sig["entry_time"], "spot_at_sig": sig["spot_at_sig"],
                "regime_label": macro["label"],
                "breadth_frac": sig.get("breadth_frac", ""),
                "sig_atr_mult": sig.get("sig_atr_mult", ""),
                "entry_premium": res.get("entry", ""),
                "stop_px": res.get("stop_px", ""),
                "target1_px": res.get("target1_px", ""),
                "exit_time": res.get("exit_time", ""),
                "exit_premium": res.get("exit", ""),
                "exit_reason": res.get("exit_reason", res.get("reason", "")),
                "lot_size": lot, "gross_inr": res.get("gross_inr", ""),
                "cost_inr": res.get("cost_inr", ""), "net_inr": res.get("net_inr", ""),
                "status": res["status"],
                "notes": f"breaker_paused={paused} · paper only, real money Rs0",
            })
            print(f"  -> SCORED [{res['status']}]: {idx} {sig['strike']}{sig['direction']} "
                  f"en={res.get('entry')} ex={res.get('exit')} ({res.get('exit_reason', res.get('reason'))}) "
                  f"Net Rs {res.get('net_inr')}")

    if not dry_run:
        if mode == "live":
            sig_p = root / "pillar2_live_signals.json"
            sig_p.write_text(json.dumps({
                "updated_at": now_ist.isoformat(), "date": target_day,
                "breaker_paused": paused, "breaker_source": pause_src,
                "signals": out_signals,
            }, indent=2))
            if slip_rows:
                _append_csv_idempotent(
                    root / "pillar2_slippage_log.csv", SLIPPAGE_COLS,
                    "timestamp_ist", slip_rows,
                )
        elif scored_rows:
            _append_csv_idempotent(
                root / "pillar2_paper_log.csv", PAPER_LOG_COLS,
                "trade_key", scored_rows,
            )
    return 0


# ---------------------------------------------------------------------------
# Deterministic Offline Self-Test
# ---------------------------------------------------------------------------
def run_selftest() -> int:
    print("=== PILLAR 2 (OPTION B) DETERMINISTIC SELF-TEST ===")
    prior_5m = [
        {"date": "2026-11-24", "time": f"14:{m:02d}", "open": 61000.0, "high": 61040.0, "low": 60980.0, "close": 61010.0, "volume": 1000.0}
        for m in range(0, 60, 5)
    ]
    prev_daily = {"high": 61150.0, "low": 60700.0, "close": 61010.0}
    daily_closes = [(f"2026-11-{d:02d}", 55000.0 + d * 260.0) for d in range(1, 25)]
    macro_bull = compute_macro_regime(daily_closes, "2026-11-25")
    assert macro_bull["label"] == "STRONG_BULL", macro_bull

    # Clean CE breakout at 09:35 (normal bar range 55 pts vs ~60 pt ATR)
    bars_ce = [
        {"time": "09:15", "open": 61050.0, "high": 61120.0, "low": 61020.0, "close": 61090.0},
        {"time": "09:20", "open": 61090.0, "high": 61150.0, "low": 61070.0, "close": 61110.0},
        {"time": "09:25", "open": 61110.0, "high": 61140.0, "low": 61080.0, "close": 61120.0},
        {"time": "09:30", "open": 61120.0, "high": 61148.0, "low": 61100.0, "close": 61140.0},
        {"time": "09:35", "open": 61140.0, "high": 61190.0, "low": 61135.0, "close": 61180.0},
    ]
    # Test 1: Breadth disagrees (heavyweights bearish) -> BLOCKED
    bear_const = {
        sym: [
            {"time": "09:15", "open": 1000.0, "high": 1002.0, "low": 990.0, "close": 992.0, "volume": 500.0},
            {"time": "09:35", "open": 992.0, "high": 993.0, "low": 980.0, "close": 982.0, "volume": 500.0},
        ]
        for sym in BANK_HEAVYWEIGHTS
    }
    s_blk = evaluate_day_signal("BANKNIFTY", bars_ce, prev_daily, prior_5m, macro_bull, bear_const)
    assert s_blk["decision"] == "BLOCKED" and "breadth_disagree" in s_blk["reason"], s_blk

    # Test 2: Top 3 banks (HDFC+ICICI+SBI = 78% of top-5 weight) bullish -> PASSES + selects ITM-100 CE!
    bull_const = dict(bear_const)
    for sym in ("HDFCBANK", "ICICIBANK", "SBIN"):
        bull_const[sym] = [
            {"time": "09:15", "open": 1000.0, "high": 1010.0, "low": 998.0, "close": 1008.0, "volume": 500.0},
            {"time": "09:35", "open": 1008.0, "high": 1020.0, "low": 1007.0, "close": 1018.0, "volume": 500.0},
        ]
    s_ok = evaluate_day_signal("BANKNIFTY", bars_ce, prev_daily, prior_5m, macro_bull, bull_const)
    assert s_ok["decision"] == "SIGNAL" and s_ok["direction"] == "CE"
    assert s_ok["strike"] == 61100, f"Expected ITM-100 strike 61100 vs spot 61180, got {s_ok['strike']}"

    # Test 3: Exhausted breakout bar (250 pt spike vs ~60 pt ATR) -> BLOCKED
    bars_exh = list(bars_ce[:-1]) + [
        {"time": "09:35", "open": 61140.0, "high": 61390.0, "low": 61135.0, "close": 61380.0},
    ]
    s_exh = evaluate_day_signal("BANKNIFTY", bars_exh, prev_daily, prior_5m, macro_bull, bull_const)
    assert s_exh["decision"] == "BLOCKED" and "exhausted_bar" in s_exh["reason"], s_exh

    # Test 4: Counter-trend PE fade in STRONG_BULL (close > PDL) -> BLOCKED
    bars_pe = [
        {"time": "09:15", "open": 61050.0, "high": 61120.0, "low": 61020.0, "close": 61090.0},
        {"time": "09:20", "open": 61090.0, "high": 61120.0, "low": 61030.0, "close": 61050.0},
        {"time": "09:25", "open": 61050.0, "high": 61070.0, "low": 61020.0, "close": 61030.0},
        {"time": "09:35", "open": 61025.0, "high": 61030.0, "low": 60975.0, "close": 60980.0},
    ]
    s_pe = evaluate_day_signal("BANKNIFTY", bars_pe, prev_daily, prior_5m, macro_bull, bear_const)
    assert s_pe["decision"] == "BLOCKED" and s_pe["reason"] == "counter_trend_pe_in_strong_bull", s_pe

    # Test 5: Low-premium expiry option (< Rs 80) rejected; realistic runner & debit spread pass
    r_low = replay_apex_option([("09:40", 38.80, 45.0, 20.0, 25.0)], "09:40", lot_size=65)
    assert r_low["status"] == "BLOCKED" and "low_premium" in r_low["reason"], r_low

    opt_bars = [
        ("09:40", 300.0, 320.0, 290.0, 315.0),
        ("09:45", 315.0, 410.0, 310.0, 408.0),  # hits +35% (405) -> arms runner (+20% lock=360, tgt2=525)
        ("09:50", 408.0, 535.0, 405.0, 530.0),  # hits runner tgt2 (525)!
    ]
    r_run = replay_apex_option(opt_bars, "09:40", lot_size=30)
    assert r_run["status"] == "TAKEN" and r_run["exit_reason"] == "runner_target" and r_run["net_inr"] > 6000.0, r_run

    wing_bars = [
        ("09:40", 120.0, 130.0, 115.0, 128.0),
        ("09:45", 128.0, 180.0, 125.0, 175.0),
        ("09:50", 175.0, 225.0, 170.0, 220.0),  # spread 300-120=180 -> 530-220=310 (+72% > +65% target!)
    ]
    r_sp = replay_debit_spread(opt_bars, wing_bars, "09:40", lot_size=30)
    assert r_sp["status"] == "TAKEN" and r_sp["exit_reason"] == "spread_target" and r_sp["net_inr"] > 3000.0, r_sp

    print("  OK  Rule 2 constituent breadth blocked fakeout & passed 78% aligned thrust")
    print(f"  OK  Rule 4 asymmetric moneyness selected ITM-100 CE ({s_ok['strike']}) & blocked bull-trend PE fade")
    print(f"  OK  Rule 3 signal-bar exhaustion blocked 250pt spike ({s_exh['sig_atr_mult']}x ATR)")
    print(f"  OK  Rule 5 rejected Rs 38.80 lottery ticket; runner net=Rs {r_run['net_inr']:+.2f}; debit spread net=Rs {r_sp['net_inr']:+.2f}")
    print("PILLAR 2 SELF-TEST PASSED!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "backtest", "live", "score"), default="live")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--index", choices=("BANKNIFTY", "NIFTY", "ALL"), default="ALL")
    ap.add_argument("--date", default=datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--date-from", default="2026-01-01")
    ap.add_argument("--date-to", default="2026-12-31")
    ap.add_argument("--structure", choices=("naked", "debit_spread"), default="naked")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if a.mode == "selftest":
        return run_selftest()

    root = Path(a.root)
    indices = ["BANKNIFTY", "NIFTY"] if a.index == "ALL" else [a.index]
    if a.mode == "backtest":
        return run_backtest(root, indices, a.date_from, a.date_to, structure=a.structure)
    try:
        return run_live_or_score(
            root, a.mode, indices, a.date,
            structure=a.structure, dry_run=a.dry_run,
        )
    except RateLimited as e:
        print(f"HARD STOP (HTTP 429): {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
