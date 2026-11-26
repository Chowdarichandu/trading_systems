#!/usr/bin/env python3
"""LIVE GREEN<->RED SUDDEN REVERSAL & OI INTERPRETATION DETECTOR (NIFTY & BANKNIFTY).

Detects sudden intraday index flips (GREEN -> RED or RED -> GREEN) BEFORE or AS
they happen by fusing FIVE leading real-time Upstox data streams (zero lagging
moving-average crossovers):

  Pillar 1 (0-30 pts) — Near-ATM Option Chain OI Velocity (10-15 min rolling
      delta on ATM +- 3 strikes, NOT just vs yesterday!):
      * Detects Put Writer panic unwinding + Fresh Call Writing walls (Bearish)
      * Detects Call Writer short-covering squeeze + Fresh Put Writing floors (Bullish)
      * Tracks near-ATM PCR velocity (dPCR_15m) & Put-Call IV Skew shift
  Pillar 2 (0-20 pts) — Futures OI Quadrant & Basis Velocity (10-15 min):
      * LONG_UNWINDING -> SHORT_BUILDUP + Basis collapse (Bearish)
      * SHORT_COVERING -> LONG_BUILDUP + Basis expansion (Bullish)
  Pillar 3 (0-20 pts) — Live Order Flow, CVD, L5 OBI & Footprint Absorption:
      * Reads data/orderflow_live/orderflow_state.json automatically if running
        alongside orderflow_footprint_engine.py, OR derives L5 OBI & delta flow
        natively from its own Futures 5-level depth quotes!
  Pillar 4 (0-15 pts) — Heavyweight Constituent Lead Breadth:
      * Bank Nifty Top-5 (~81% weight): HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK
      * Nifty 50 Top-6 (~47% weight): HDFCBANK, RELIANCE, ICICIBANK, INFY, TCS, BHARTIARTL
      * Detects when heavyweights flip vs their own VWAP & 15m momentum BEFORE the index!
  Pillar 5 (0-15 pts) — Structural Pivot & Zero-Line Proximity:
      * Futures VWAP (ATP) / developing dPOC breach + proximity to exact Green/Red
        line (prev_close) and intraday flip line (day_open).

ACTIONABLE 3-STAGE STATE MACHINE (plus Fake-Cross Trap Filter):
  - EARLY_WARNING (45-69 pts, >=2 pillars): Tighten stops / pause opposing entries
  - IMMINENT_FLIP (>=70 pts, >=3 pillars, pre-zero): EXIT exposed side BEFORE flush
  - CONFIRMED_FLIP (zero crossed + score >=55): Confirmed institutional reversal
  - FAKE_CROSS_WARNING (zero crossed + score <40): Likely stop-hunt / trap!

OUTPUTS (Paper / Alerting Only — Zero Broker Orders):
  1. Strategy Position-Action Bridge: data/reversal_alerts/reversal_state.json
     (explicit flags: block_ce_entries, block_pe_entries, tighten_ce_stop,
      tighten_pe_stop, exit_ce_now, exit_pe_now)
  2. Auto-Refreshing Visual Reversal Radar Dashboard:
     http://127.0.0.1:8766/reversal_dashboard.html
  3. Instant Telegram / Webhook push notifications (optional env vars:
     TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID, or --webhook-url)
  4. Full JSONL event & snapshot archive for offline replay:
     data/reversal_alerts/YYYY-MM-DD/snapshots.jsonl

Usage:
  # 1. Run deterministic offline self-test (all 4 reversal & trap scenarios)
  python3 reversal_flip_detector.py --mode selftest

  # 2. Run live during market hours (09:15-15:30 IST, 1 cycle every 20-30s)
  python3 reversal_flip_detector.py --mode live --interval 20

  # 3. Replay a recorded session offline
  python3 reversal_flip_detector.py --mode replay --file data/reversal_alerts/2026-11-26/snapshots.jsonl
"""
from __future__ import annotations

import argparse
import csv
import functools
import gzip
import http.server
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from datetime import date as ddate, datetime, time as dtime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
API = "https://api.upstox.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
INSTRUMENTS_URL = (
    "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
)
DEPTH_WEIGHTS = (1.0, 0.70, 0.50, 0.35, 0.25)

INDEX_SPECS: Dict[str, Dict[str, Any]] = {
    "BANKNIFTY": {
        "spot_key": "NSE_INDEX|Nifty Bank",
        "step": 100,
        "basis_shift_thresh": 12.0,
        "prefer_monthly": True,
        "heavyweights": {
            "HDFCBANK": 0.28, "ICICIBANK": 0.24, "SBIN": 0.11,
            "KOTAKBANK": 0.09, "AXISBANK": 0.09,
        },
    },
    "NIFTY": {
        "spot_key": "NSE_INDEX|Nifty 50",
        "step": 50,
        "basis_shift_thresh": 6.0,
        "prefer_monthly": False,
        "heavyweights": {
            "HDFCBANK": 0.12, "RELIANCE": 0.09, "ICICIBANK": 0.085,
            "INFY": 0.06, "TCS": 0.04, "BHARTIARTL": 0.04,
        },
    },
}


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "upstox_refresh" / ".env").exists() or (live / "data").exists():
        return live
    return Path(__file__).resolve().parent


def _f(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def round_strike(spot: float, step: int) -> int:
    return int(round(spot / float(step)) * step)


# ---------------------------------------------------------------------------
# Option Chain & Order Flow Feature Extractors (Pure, Causal, Testable)
# ---------------------------------------------------------------------------
def extract_near_atm_chain_metrics(
    chain_rows: Sequence[Dict[str, Any]], spot: float, step: int, n_strikes_each_side: int = 3
) -> Dict[str, Any]:
    """Summarize ATM +- n_strikes CE/PE OI, LTP, PCR, IV skew, and top OI walls."""
    if not chain_rows or spot <= 0:
        return {"valid": False}
    atm = round_strike(spot, step)
    lo_k = atm - n_strikes_each_side * step
    hi_k = atm + n_strikes_each_side * step

    ce_oi = pe_oi = ce_prev_oi = pe_prev_oi = 0.0
    ce_ltps, pe_ltps, ce_ivs, pe_ivs = [], [], [], []
    max_ce_wall = (0, 0.0)
    max_pe_wall = (0, 0.0)
    strike_count = 0

    for row in chain_rows:
        k = int(round(_f(row.get("strike_price") or row.get("strike"))))
        if k <= 0:
            continue
        ce_leg = row.get("call_options") or {}
        pe_leg = row.get("put_options") or {}
        ce_md = ce_leg.get("market_data") or row
        pe_md = pe_leg.get("market_data") or row
        ce_gr = ce_leg.get("option_greeks") or {}
        pe_gr = pe_leg.get("option_greeks") or {}

        c_o = _f(ce_md.get("oi") if "oi" in ce_md else row.get("ce_oi"))
        p_o = _f(pe_md.get("oi") if "oi" in pe_md else row.get("pe_oi"))
        if c_o > max_ce_wall[1] and k >= atm:
            max_ce_wall = (k, c_o)
        if p_o > max_pe_wall[1] and k <= atm:
            max_pe_wall = (k, p_o)

        if lo_k <= k <= hi_k:
            strike_count += 1
            ce_oi += c_o
            pe_oi += p_o
            ce_prev_oi += _f(ce_md.get("prev_oi") if "prev_oi" in ce_md else row.get("ce_prev_oi"))
            pe_prev_oi += _f(pe_md.get("prev_oi") if "prev_oi" in pe_md else row.get("pe_prev_oi"))
            c_ltp = _f(ce_md.get("ltp") if "ltp" in ce_md else row.get("ce_ltp"))
            p_ltp = _f(pe_md.get("ltp") if "ltp" in pe_md else row.get("pe_ltp"))
            if c_ltp > 0:
                ce_ltps.append(c_ltp)
            if p_ltp > 0:
                pe_ltps.append(p_ltp)
            c_iv = _f(ce_gr.get("iv") if "iv" in ce_gr else row.get("ce_iv"))
            p_iv = _f(pe_gr.get("iv") if "iv" in pe_gr else row.get("pe_iv"))
            if c_iv > 0:
                ce_ivs.append(c_iv)
            if p_iv > 0:
                pe_ivs.append(p_iv)

    if strike_count == 0 or ce_oi <= 0:
        return {"valid": False}

    avg_ce_iv = sum(ce_ivs) / len(ce_ivs) if ce_ivs else 0.0
    avg_pe_iv = sum(pe_ivs) / len(pe_ivs) if pe_ivs else 0.0
    return {
        "valid": True,
        "atm": atm,
        "strikes_used": strike_count,
        "ce_oi": round(ce_oi, 1),
        "pe_oi": round(pe_oi, 1),
        "ce_day_doi": round(ce_oi - ce_prev_oi, 1),
        "pe_day_doi": round(pe_oi - pe_prev_oi, 1),
        "near_pcr": round(pe_oi / ce_oi, 4),
        "ce_ltp_sum": round(sum(ce_ltps), 2),
        "pe_ltp_sum": round(sum(pe_ltps), 2),
        "iv_skew": round(avg_pe_iv - avg_ce_iv, 3) if (ce_ivs and pe_ivs) else None,
        "ce_wall_strike": max_ce_wall[0],
        "pe_wall_strike": max_pe_wall[0],
    }


def classify_futures_quadrant(dp: float, doi: float) -> str:
    if abs(dp) < 1e-6 or abs(doi) < 1e-6:
        return "FLAT"
    if dp > 0:
        return "LONG_BUILDUP" if doi > 0 else "SHORT_COVERING"
    return "SHORT_BUILDUP" if doi > 0 else "LONG_UNWINDING"


# ---------------------------------------------------------------------------
# Stateful Index Reversal Monitor (1 Instance per Index: BANKNIFTY / NIFTY)
# ---------------------------------------------------------------------------
class IndexReversalMonitor:
    """Tracks rolling 10-15 min intraday OI, Futures, Order Flow & Heavyweight
    velocity for one index and outputs real-time Green<->Red flip directives."""

    def __init__(self, index_name: str, window_sec: int = 900):
        self.index_name = index_name
        self.spec = INDEX_SPECS[index_name]
        self.window_sec = window_sec  # 15-min lookback window for sudden-turn velocity
        self.history: Deque[Dict[str, Any]] = deque(maxlen=120)
        self.prev_color: Optional[str] = None
        self.prev_intraday_color: Optional[str] = None
        self.last_alert_ts: Dict[str, float] = {}
        self.recent_events: Deque[Dict[str, Any]] = deque(maxlen=25)

    def _baseline_obs(self, now_epoch: float) -> Optional[Dict[str, Any]]:
        """Return observation closest to `window_sec` ago (or oldest available if >= 2 obs)."""
        if not self.history:
            return None
        target = now_epoch - self.window_sec
        best = self.history[0]
        for obs in self.history:
            if obs["epoch"] <= target:
                best = obs
            else:
                break
        return best

    def _compute_heavyweight_lead(
        self, now_hw: Dict[str, Dict[str, float]], base_hw: Dict[str, Dict[str, float]]
    ) -> Tuple[float, float, Dict[str, str]]:
        """Weighted bullish & bearish constituent fractions (combining VWAP + 15m mom)."""
        weights = self.spec["heavyweights"]
        avail_w = 0.0
        bull_w = 0.0
        bear_w = 0.0
        states: Dict[str, str] = {}
        for sym, w in weights.items():
            cur = now_hw.get(sym)
            if not cur or cur.get("ltp", 0) <= 0:
                continue
            avail_w += w
            ltp = cur["ltp"]
            vwap = cur.get("atp") or ltp
            base_px = (base_hw.get(sym) or {}).get("ltp") or ltp
            mom_pct = ((ltp - base_px) / base_px) * 100.0 if base_px > 0 else 0.0
            if ltp < vwap and mom_pct <= -0.10:
                bear_w += w
                states[sym] = "BEAR"
            elif ltp > vwap and mom_pct >= 0.10:
                bull_w += w
                states[sym] = "BULL"
            elif mom_pct <= -0.25:
                bear_w += w
                states[sym] = "BEAR_MOM"
            elif mom_pct >= 0.25:
                bull_w += w
                states[sym] = "BULL_MOM"
            else:
                states[sym] = "NEUTRAL"
        if avail_w <= 0:
            return 0.0, 0.0, states
        return round(bull_w / avail_w, 4), round(bear_w / avail_w, 4), states

    def evaluate(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest one synchronized observation and compute 5-pillar flip analysis.

        Required keys in `obs`:
          timestamp_ist, epoch, spot_ltp, prev_close, day_open,
          fut_ltp, fut_oi, fut_atp (VWAP), fut_obi_l5, fut_cvd,
          chain_metrics (from extract_near_atm_chain_metrics),
          heavyweights ({sym: {ltp, atp}}),
          orderflow_extras (optional: absorption, stacked_buy, stacked_sell, dpoc)
        """
        spot = float(obs["spot_ltp"])
        prev_close = float(obs["prev_close"])
        day_open = float(obs.get("day_open") or prev_close)
        fut_ltp = float(obs.get("fut_ltp") or spot)
        fut_oi = float(obs.get("fut_oi") or 0.0)
        fut_vwap = float(obs.get("fut_atp") or fut_ltp)
        fut_obi = float(obs.get("fut_obi_l5") or 0.0)
        fut_cvd = float(obs.get("fut_cvd") or 0.0)
        basis = round(fut_ltp - spot, 2)
        cm = obs.get("chain_metrics") or {"valid": False}
        of_ext = obs.get("orderflow_extras") or {}
        dpoc = of_ext.get("dpoc")

        chg_prev_pct = round(((spot - prev_close) / prev_close) * 100.0, 3) if prev_close > 0 else 0.0
        chg_open_pct = round(((spot - day_open) / day_open) * 100.0, 3) if day_open > 0 else 0.0
        color = "GREEN" if spot >= prev_close else "RED"
        intraday_color = "GREEN" if spot >= day_open else "RED"

        base = self._baseline_obs(obs["epoch"])
        bear_score = 0
        bull_score = 0
        bear_reasons: List[str] = []
        bull_reasons: List[str] = []
        bear_pillars: set = set()
        bull_pillars: set = set()

        oi_interp = "INITIALIZING"
        fut_quad = "FLAT"
        d_ce_oi = d_pe_oi = d_pcr = d_basis = d_cvd = 0.0

        if base is not None:
            # --- PILLAR 1: Near-ATM Option Chain OI Velocity (0-30 pts) ---
            bcm = base.get("chain_metrics") or {"valid": False}
            if cm.get("valid") and bcm.get("valid"):
                d_ce_oi = round(cm["ce_oi"] - bcm["ce_oi"], 1)
                d_pe_oi = round(cm["pe_oi"] - bcm["pe_oi"], 1)
                ce_pct = (d_ce_oi / bcm["ce_oi"]) * 100.0 if bcm["ce_oi"] > 0 else 0.0
                pe_pct = (d_pe_oi / bcm["pe_oi"]) * 100.0 if bcm["pe_oi"] > 0 else 0.0
                d_pcr = round(cm["near_pcr"] - bcm["near_pcr"], 4)
                d_ce_ltp = cm["ce_ltp_sum"] - bcm["ce_ltp_sum"]
                d_pe_ltp = cm["pe_ltp_sum"] - bcm["pe_ltp_sum"]

                # Bearish OI velocity: PE writers unwinding + CE writers adding
                if pe_pct <= -2.5 and d_pe_ltp > 0:
                    bear_score += 12
                    bear_pillars.add("OI_CHAIN")
                    bear_reasons.append(f"PE writer panic covering (dPE_OI {d_pe_oi:+,.0f}, {pe_pct:+.1f}%)")
                elif pe_pct <= -2.5:
                    bear_score += 8
                    bear_pillars.add("OI_CHAIN")
                    bear_reasons.append(f"PE OI unwinding ({d_pe_oi:+,.0f}, {pe_pct:+.1f}%)")
                if ce_pct >= 3.0 and d_ce_ltp <= 0:
                    bear_score += 10
                    bear_pillars.add("OI_CHAIN")
                    bear_reasons.append(f"Aggressive Call writing wall (dCE_OI {d_ce_oi:+,.0f}, {ce_pct:+.1f}%)")
                elif ce_pct >= 3.0:
                    bear_score += 6
                    bear_pillars.add("OI_CHAIN")
                    bear_reasons.append(f"CE OI buildup ({d_ce_oi:+,.0f}, {ce_pct:+.1f}%)")
                if d_pcr <= -0.06:
                    bear_score += 5
                    bear_pillars.add("OI_CHAIN")
                    bear_reasons.append(f"Near-ATM PCR drop ({d_pcr:+.3f})")

                # Bullish OI velocity: CE writers covering shorts + PE writers building floor
                if ce_pct <= -2.5 and d_ce_ltp > 0:
                    bull_score += 12
                    bull_pillars.add("OI_CHAIN")
                    bull_reasons.append(f"Call short-covering squeeze (dCE_OI {d_ce_oi:+,.0f}, {ce_pct:+.1f}%)")
                elif ce_pct <= -2.5:
                    bull_score += 8
                    bull_pillars.add("OI_CHAIN")
                    bull_reasons.append(f"CE OI unwinding ({d_ce_oi:+,.0f}, {ce_pct:+.1f}%)")
                if pe_pct >= 3.0 and d_pe_ltp <= 0:
                    bull_score += 10
                    bull_pillars.add("OI_CHAIN")
                    bull_reasons.append(f"Aggressive Put writing floor (dPE_OI {d_pe_oi:+,.0f}, {pe_pct:+.1f}%)")
                elif pe_pct >= 3.0:
                    bull_score += 6
                    bull_pillars.add("OI_CHAIN")
                    bull_reasons.append(f"PE OI buildup ({d_pe_oi:+,.0f}, {pe_pct:+.1f}%)")
                if d_pcr >= 0.06:
                    bull_score += 5
                    bull_pillars.add("OI_CHAIN")
                    bull_reasons.append(f"Near-ATM PCR surge ({d_pcr:+.3f})")

                if cm.get("iv_skew") is not None and bcm.get("iv_skew") is not None:
                    d_skew = round(cm["iv_skew"] - bcm["iv_skew"], 3)
                    if d_skew >= 0.6:
                        bear_score += 3
                        bear_reasons.append(f"Put IV skew jump ({d_skew:+.2f}%)")
                    elif d_skew <= -0.6:
                        bull_score += 3
                        bull_reasons.append(f"Put IV crush / Call skew ({d_skew:+.2f}%)")

                if pe_pct <= -2.5 and ce_pct >= 3.0:
                    oi_interp = "PUT_UNWINDING_AND_CALL_WRITING (BEARISH)"
                elif ce_pct <= -2.5 and pe_pct >= 3.0:
                    oi_interp = "CALL_SHORT_COVERING_AND_PUT_WRITING (BULLISH)"
                elif ce_pct <= -2.5:
                    oi_interp = "CALL_SHORT_COVERING"
                elif pe_pct <= -2.5:
                    oi_interp = "PUT_UNWINDING"
                elif ce_pct >= 3.0:
                    oi_interp = "FRESH_CALL_WRITING"
                elif pe_pct >= 3.0:
                    oi_interp = "FRESH_PUT_WRITING"
                else:
                    oi_interp = "BALANCED_OI"

            # --- PILLAR 2: Futures OI Quadrant & Basis Shift (0-20 pts) ---
            d_fut = fut_ltp - float(base.get("fut_ltp") or fut_ltp)
            d_fut_oi = fut_oi - float(base.get("fut_oi") or fut_oi)
            d_basis = round(basis - float(base.get("basis") or basis), 2)
            fut_quad = classify_futures_quadrant(d_fut, d_fut_oi)
            b_th = self.spec["basis_shift_thresh"]

            if fut_quad == "SHORT_BUILDUP":
                bear_score += 12
                bear_pillars.add("FUT_OI")
                bear_reasons.append(f"Futures SHORT_BUILDUP (dFut {d_fut:+.1f}, dOI {d_fut_oi:+,.0f})")
            elif fut_quad == "LONG_UNWINDING":
                bear_score += 8
                bear_pillars.add("FUT_OI")
                bear_reasons.append(f"Futures LONG_UNWINDING (dFut {d_fut:+.1f}, dOI {d_fut_oi:+,.0f})")
            elif fut_quad == "SHORT_COVERING":
                bull_score += 12
                bull_pillars.add("FUT_OI")
                bull_reasons.append(f"Futures SHORT_COVERING (dFut {d_fut:+.1f}, dOI {d_fut_oi:+,.0f})")
            elif fut_quad == "LONG_BUILDUP":
                bull_score += 10
                bull_pillars.add("FUT_OI")
                bull_reasons.append(f"Futures LONG_BUILDUP (dFut {d_fut:+.1f}, dOI {d_fut_oi:+,.0f})")

            if d_basis <= -b_th:
                bear_score += 8
                bear_pillars.add("FUT_OI")
                bear_reasons.append(f"Futures basis drop ({d_basis:+.1f} pts)")
            elif d_basis >= b_th:
                bull_score += 8
                bull_pillars.add("FUT_OI")
                bull_reasons.append(f"Futures basis surge ({d_basis:+.1f} pts)")

            # --- PILLAR 3: Order Flow, CVD, OBI & Footprint Absorption (0-20 pts) ---
            d_cvd = round(fut_cvd - float(base.get("fut_cvd") or fut_cvd), 1)
            if d_cvd < -150:
                bear_score += 8
                bear_pillars.add("ORDERFLOW")
                bear_reasons.append(f"Aggressive sell flow (dCVD {d_cvd:+,.0f})")
            elif d_cvd > 150:
                bull_score += 8
                bull_pillars.add("ORDERFLOW")
                bull_reasons.append(f"Aggressive buy flow (dCVD {d_cvd:+,.0f})")

            if fut_obi <= -0.20:
                bear_score += 6
                bear_pillars.add("ORDERFLOW")
                bear_reasons.append(f"Heavy Ask depth wall (OBI-L5 {fut_obi*100:+.1f}%)")
            elif fut_obi >= 0.20:
                bull_score += 6
                bull_pillars.add("ORDERFLOW")
                bull_reasons.append(f"Heavy Bid depth support (OBI-L5 {fut_obi*100:+.1f}%)")

            if of_ext.get("bearish_absorption") or of_ext.get("stacked_sell"):
                bear_score += 6
                bear_pillars.add("ORDERFLOW")
                bear_reasons.append("Footprint Bearish Absorption / Stacked Sell Imbalance")
            if of_ext.get("bullish_absorption") or of_ext.get("stacked_buy"):
                bull_score += 6
                bull_pillars.add("ORDERFLOW")
                bull_reasons.append("Footprint Bullish Absorption / Stacked Buy Imbalance")

            # --- PILLAR 4: Heavyweight Constituent Breadth Lead (0-15 pts) ---
            bull_hw, bear_hw, hw_states = self._compute_heavyweight_lead(
                obs.get("heavyweights") or {}, base.get("heavyweights") or {}
            )
            if bear_hw >= 0.60:
                bear_score += 15
                bear_pillars.add("HEAVYWEIGHTS")
                bear_reasons.append(f"Heavyweights turned bearish ({bear_hw*100:.0f}% weight)")
            elif bear_hw >= 0.45:
                bear_score += 10
                bear_pillars.add("HEAVYWEIGHTS")
                bear_reasons.append(f"Heavyweights weakening ({bear_hw*100:.0f}% bearish)")
            if bull_hw >= 0.60:
                bull_score += 15
                bull_pillars.add("HEAVYWEIGHTS")
                bull_reasons.append(f"Heavyweights turned bullish ({bull_hw*100:.0f}% weight)")
            elif bull_hw >= 0.45:
                bull_score += 10
                bull_pillars.add("HEAVYWEIGHTS")
                bull_reasons.append(f"Heavyweights strengthening ({bull_hw*100:.0f}% bullish)")
        else:
            bull_hw, bear_hw, hw_states = 0.0, 0.0, {}

        # --- PILLAR 5: Structural Pivots (VWAP / dPOC / Zero-Line Proximity, 0-15 pts) ---
        if fut_ltp < fut_vwap and (dpoc is None or fut_ltp < dpoc):
            bear_score += 8
            bear_pillars.add("STRUCTURE")
            bear_reasons.append(f"Futures below VWAP ({fut_vwap:.1f})")
        elif fut_ltp > fut_vwap and (dpoc is None or fut_ltp > dpoc):
            bull_score += 8
            bull_pillars.add("STRUCTURE")
            bull_reasons.append(f"Futures above VWAP ({fut_vwap:.1f})")

        near_zero_from_green = (color == "GREEN" and 0.0 <= chg_prev_pct <= 0.35) or (
            intraday_color == "GREEN" and 0.0 <= chg_open_pct <= 0.35
        )
        near_zero_from_red = (color == "RED" and -0.35 <= chg_prev_pct <= 0.0) or (
            intraday_color == "RED" and -0.35 <= chg_open_pct <= 0.0
        )
        if near_zero_from_green and bear_score >= 30:
            bear_score += 7
            bear_pillars.add("STRUCTURE")
            bear_reasons.append(f"Testing Green->Red line ({chg_prev_pct:+.2f}% vs prev close)")
        if near_zero_from_red and bull_score >= 30:
            bull_score += 7
            bull_pillars.add("STRUCTURE")
            bull_reasons.append(f"Testing Red->Green line ({chg_prev_pct:+.2f}% vs prev close)")

        bear_score = min(100, bear_score)
        bull_score = min(100, bull_score)

        # --- Determine Flip Stage & Exact Position-Management Directives ---
        crossed_g2r = (self.prev_color == "GREEN" and color == "RED") or (
            self.prev_intraday_color == "GREEN" and intraday_color == "RED"
        )
        crossed_r2g = (self.prev_color == "RED" and color == "GREEN") or (
            self.prev_intraday_color == "RED" and intraday_color == "GREEN"
        )

        alert_level = "STABLE"
        flip_type = "NONE"
        active_score = max(bear_score, bull_score)
        active_reasons: List[str] = []
        directives = {
            "block_ce_entries": False, "block_pe_entries": False,
            "tighten_ce_stop": False, "tighten_pe_stop": False,
            "exit_ce_now": False, "exit_pe_now": False,
            "summary_action": "NORMAL_OPERATIONS",
        }

        if crossed_g2r:
            if bear_score >= 55 and len(bear_pillars) >= 3:
                alert_level, flip_type = "CONFIRMED_FLIP", "CONFIRMED_GREEN_TO_RED"
                active_score, active_reasons = bear_score, bear_reasons
                directives.update(
                    block_ce_entries=True, tighten_ce_stop=True, exit_ce_now=True,
                    summary_action="EXIT_CE_NOW / BLOCK_CE / BEARISH_FLIP_CONFIRMED",
                )
            elif bear_score < 40:
                alert_level, flip_type = "FAKE_CROSS_WARNING", "FAKE_GREEN_TO_RED_TRAP"
                active_score, active_reasons = bear_score, ["Spot crossed red WITHOUT OI/OrderFlow/Breadth support — possible trap!"]
                directives["summary_action"] = "CAUTION_UNCONFIRMED_RED_CROSS"
        elif crossed_r2g:
            if bull_score >= 55 and len(bull_pillars) >= 3:
                alert_level, flip_type = "CONFIRMED_FLIP", "CONFIRMED_RED_TO_GREEN"
                active_score, active_reasons = bull_score, bull_reasons
                directives.update(
                    block_pe_entries=True, tighten_pe_stop=True, exit_pe_now=True,
                    summary_action="EXIT_PE_NOW / BLOCK_PE / BULLISH_FLIP_CONFIRMED",
                )
            elif bull_score < 40:
                alert_level, flip_type = "FAKE_CROSS_WARNING", "FAKE_RED_TO_GREEN_TRAP"
                active_score, active_reasons = bull_score, ["Spot crossed green WITHOUT Call covering/Breadth support — possible trap!"]
                directives["summary_action"] = "CAUTION_UNCONFIRMED_GREEN_CROSS"

        # Pre-flip early warnings BEFORE zero-line cross (or ongoing reversal pressure)
        if alert_level == "STABLE":
            if (color == "GREEN" or intraday_color == "GREEN") and bear_score >= 70 and len(bear_pillars) >= 3:
                alert_level, flip_type = "IMMINENT_FLIP", "IMMINENT_GREEN_TO_RED"
                active_score, active_reasons = bear_score, bear_reasons
                directives.update(
                    block_ce_entries=True, tighten_ce_stop=True, exit_ce_now=True,
                    summary_action="EXIT_CE_BEFORE_FLUSH / PREPARE_RED_FLIP",
                )
            elif (color == "RED" or intraday_color == "RED") and bull_score >= 70 and len(bull_pillars) >= 3:
                alert_level, flip_type = "IMMINENT_FLIP", "IMMINENT_RED_TO_GREEN"
                active_score, active_reasons = bull_score, bull_reasons
                directives.update(
                    block_pe_entries=True, tighten_pe_stop=True, exit_pe_now=True,
                    summary_action="EXIT_PE_BEFORE_SQUEEZE / PREPARE_GREEN_FLIP",
                )
            elif (color == "GREEN" or intraday_color == "GREEN") and bear_score >= 45 and len(bear_pillars) >= 2:
                alert_level, flip_type = "EARLY_WARNING", "PRE_GREEN_TO_RED"
                active_score, active_reasons = bear_score, bear_reasons
                directives.update(
                    block_ce_entries=True, tighten_ce_stop=True,
                    summary_action="TRAIL_CE_STOP_TO_BE / PAUSE_NEW_CE",
                )
            elif (color == "RED" or intraday_color == "RED") and bull_score >= 45 and len(bull_pillars) >= 2:
                alert_level, flip_type = "EARLY_WARNING", "PRE_RED_TO_GREEN"
                active_score, active_reasons = bull_score, bull_reasons
                directives.update(
                    block_pe_entries=True, tighten_pe_stop=True,
                    summary_action="TRAIL_PE_STOP_TO_BE / PAUSE_NEW_PE",
                )

        # Record history & update color memory
        stored = dict(obs)
        stored["basis"] = basis
        self.history.append(stored)
        self.prev_color = color
        self.prev_intraday_color = intraday_color

        out = {
            "index": self.index_name,
            "timestamp_ist": obs["timestamp_ist"],
            "spot_ltp": round(spot, 2),
            "prev_close": round(prev_close, 2),
            "day_open": round(day_open, 2),
            "chg_vs_prev_pct": chg_prev_pct,
            "chg_vs_open_pct": chg_open_pct,
            "color": color,
            "intraday_color": intraday_color,
            "fut_ltp": round(fut_ltp, 2),
            "fut_vwap": round(fut_vwap, 2),
            "basis": basis,
            "d_basis_15m": d_basis,
            "fut_quadrant_15m": fut_quad,
            "oi_interpretation_15m": oi_interp,
            "d_ce_oi_15m": d_ce_oi,
            "d_pe_oi_15m": d_pe_oi,
            "d_pcr_15m": d_pcr,
            "near_pcr": cm.get("near_pcr"),
            "ce_wall": cm.get("ce_wall_strike"),
            "pe_wall": cm.get("pe_wall_strike"),
            "d_cvd_15m": d_cvd,
            "fut_obi_l5": round(fut_obi, 4),
            "heavyweight_bull_pct": round(bull_hw * 100.0, 1),
            "heavyweight_bear_pct": round(bear_hw * 100.0, 1),
            "heavyweight_states": hw_states,
            "bear_flip_score": bear_score,
            "bull_flip_score": bull_score,
            "bear_pillars": sorted(bear_pillars),
            "bull_pillars": sorted(bull_pillars),
            "alert_level": alert_level,
            "flip_type": flip_type,
            "active_score": active_score,
            "reasons": active_reasons,
            "directives": directives,
        }
        if alert_level != "STABLE":
            self.recent_events.append({
                "time": obs["timestamp_ist"][11:19],
                "level": alert_level, "flip_type": flip_type,
                "score": active_score, "spot": round(spot, 2),
                "action": directives["summary_action"],
                "reasons": active_reasons[:4],
            })
        out["recent_events"] = list(self.recent_events)[-10:]
        return out


# ---------------------------------------------------------------------------
# Live Upstox Fetching & Push Alerting
# ---------------------------------------------------------------------------
def load_token(root: Path) -> str:
    env_p = root / "upstox_refresh" / ".env"
    if not env_p.exists():
        raise FileNotFoundError(f"Upstox token file missing: {env_p}")
    for line in env_p.read_text().splitlines():
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            tok = line.split("=", 1)[1].strip().strip('"').strip("'")
            if tok:
                return tok
    raise RuntimeError(f"UPSTOX_ACCESS_TOKEN missing in {env_p}")


def api_get(path: str, token: str) -> Dict[str, Any]:
    url = path if path.startswith("http") else (API + path)
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"HTTP 429 on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def send_push_alert(title: str, body: str, webhook_url: Optional[str] = None) -> None:
    """Optional Telegram / Webhook push notification (never blocks or crashes)."""
    tg_tok = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if tg_tok and tg_chat:
        try:
            payload = json.dumps({"chat_id": tg_chat, "text": f"{title}\n{body}"}).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{tg_tok}/sendMessage",
                data=payload, headers={"Content-Type": "application/json"}, method="POST",
            )
            urllib.request.urlopen(req, timeout=10).read()
        except Exception:
            pass
    if webhook_url:
        try:
            payload = json.dumps({"text": f"{title}\n{body}"}).encode("utf-8")
            req = urllib.request.Request(
                webhook_url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
            )
            urllib.request.urlopen(req, timeout=10).read()
        except Exception:
            pass


def load_nse_master(root: Path) -> List[Dict[str, str]]:
    out_dir = root / "november_shadow_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    master = out_dir / "instruments_NSE.csv"
    stamp = out_dir / "instruments_stamp.txt"
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    if not master.exists() or (stamp.exists() and stamp.read_text().strip() != today_s):
        req = urllib.request.Request(
            INSTRUMENTS_URL, headers={"Accept": "application/gzip", "User-Agent": UA}
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            master.write_bytes(gzip.decompress(r.read()))
        stamp.write_text(today_s)
    with open(master, newline="") as f:
        return list(csv.DictReader(f))


def resolve_live_instruments(
    root: Path, master: Sequence[Dict[str, str]], today_s: str
) -> Dict[str, Any]:
    """Resolve active FUT keys, active OPT expiries, and heavyweight EQ keys."""
    futs: Dict[str, Tuple[str, str]] = {}
    exps: Dict[str, str] = {}
    eq_keys: Dict[str, Tuple[str, str]] = {}
    need_eq = {s for spec in INDEX_SPECS.values() for s in spec["heavyweights"]}

    for idx, spec in INDEX_SPECS.items():
        fcands = [
            r for r in master
            if r.get("name") == idx and r.get("instrument_type") == "FUTIDX" and (r.get("expiry") or "") >= today_s
        ]
        fcands.sort(key=lambda r: r["expiry"])
        if fcands:
            futs[idx] = (fcands[0]["instrument_key"], fcands[0].get("tradingsymbol") or idx)

        oexps = sorted({
            r["expiry"] for r in master
            if r.get("name") == idx and r.get("instrument_type") == "OPTIDX" and (r.get("expiry") or "") >= today_s
        })
        if oexps:
            if spec["prefer_monthly"]:
                in_m = [e for e in oexps if e[:7] == today_s[:7]]
                exps[idx] = in_m[-1] if in_m else [e for e in oexps if e[:7] == oexps[0][:7]][-1]
            else:
                exps[idx] = oexps[0]

    for r in master:
        if r.get("exchange") == "NSE_EQ" and r.get("instrument_type") == "EQUITY":
            ts = (r.get("tradingsymbol") or "").strip()
            if ts in need_eq and ts not in eq_keys:
                eq_keys[ts] = (r["instrument_key"], ts)

    return {"futs": futs, "expiries": exps, "eq_keys": eq_keys}


def _read_fresh_orderflow_state(root: Path, max_age_sec: float = 60.0) -> Dict[str, Any]:
    p = root / "data" / "orderflow_live" / "orderflow_state.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
        upd = datetime.fromisoformat(data["updated_at"])
        if (datetime.now(IST) - upd).total_seconds() <= max_age_sec:
            return data.get("instruments") or {}
    except Exception:
        pass
    return {}


def _calc_obi_l5(depth: Dict[str, Any]) -> float:
    bids = depth.get("buy") or []
    asks = depth.get("sell") or []
    wb = sum(DEPTH_WEIGHTS[i] * _f(bids[i].get("quantity")) for i in range(min(5, len(bids))))
    wa = sum(DEPTH_WEIGHTS[i] * _f(asks[i].get("quantity")) for i in range(min(5, len(asks))))
    return round((wb - wa) / (wb + wa), 4) if (wb + wa) > 0 else 0.0


# ---------------------------------------------------------------------------
# Auto-Refreshing Reversal Radar HTML Dashboard
# ---------------------------------------------------------------------------
REVERSAL_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Green/Red Reversal & OI Flip Radar — NIFTY & BANKNIFTY</title>
<style>
  body { background:#0b0f17; color:#e5e7eb; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; margin:16px; }
  h1 { font-size:18px; color:#93c5fd; margin:0 0 6px; }
  .meta { font-size:12px; color:#9ca3af; margin-bottom:14px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(520px, 1fr)); gap:16px; }
  .card { background:#111827; border:2px solid #1f2937; border-radius:8px; padding:14px; }
  .card.IMMINENT_FLIP, .card.CONFIRMED_FLIP { border-color:#ef4444; box-shadow:0 0 14px rgba(239,68,68,0.25); }
  .card.EARLY_WARNING { border-color:#f59e0b; }
  .hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
  .badge { padding:4px 8px; border-radius:4px; font-weight:700; font-size:12px; }
  .GREEN { background:#064e3b; color:#34d399; } .RED { background:#7f1d1d; color:#fca5a5; }
  .STABLE { background:#1f2937; color:#9ca3af; }
  .EARLY_WARNING { background:#78350f; color:#fbbf24; }
  .IMMINENT_FLIP, .CONFIRMED_FLIP { background:#991b1b; color:#fecaca; }
  .FAKE_CROSS_WARNING { background:#4c1d95; color:#ddd6fe; }
  .meter { height:12px; background:#1f2937; border-radius:6px; overflow:hidden; margin:4px 0 8px; }
  .fill-bear { height:100%; background:#ef4444; } .fill-bull { height:100%; background:#10b981; }
  .kpis { display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:12px; margin:8px 0; }
  .box { background:#0f172a; padding:6px 8px; border-radius:4px; }
  .action { padding:8px; border-radius:6px; background:#1e293b; font-weight:700; margin:8px 0; color:#fde68a; }
  ul { margin:4px 0 0 16px; padding:0; font-size:12px; }
</style></head>
<body>
<h1>Sudden Green ↔ Red Reversal & OI Interpretation Radar</h1>
<div class="meta" id="meta">Loading reversal_state.json...</div>
<div class="grid" id="grid"></div>
<script>
async function refresh() {
  try {
    const r = await fetch('reversal_state.json?_=' + Date.now());
    const d = await r.json();
    document.getElementById('meta').textContent =
      `Updated: ${d.updated_at} | Mode: ${d.mode} | Paper Alert Bridge Only (Rs 0) | Refresh 3s`;
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    for (const [idx, st] of Object.entries(d.indices || {})) {
      const card = document.createElement('div');
      card.className = 'card ' + (st.alert_level || 'STABLE');
      const reasons = (st.reasons || []).map(x => `<li>${x}</li>`).join('') || '<li>No active reversal warning</li>';
      const evs = (st.recent_events || []).slice(-4).reverse().map(e =>
        `<li>[${e.time}] <b>${e.flip_type}</b> (${e.score}/100 @ ${e.spot}) — ${e.action}</li>`).join('');
      card.innerHTML = `
        <div class="hdr">
          <div><b style="font-size:16px">${idx}</b> <span class="badge ${st.color}">${st.color} (${st.chg_vs_prev_pct>=0?'+':''}${st.chg_vs_prev_pct}%)</span>
               <span style="font-size:12px;color:#9ca3af">Spot ${st.spot_ltp} | PrevClose ${st.prev_close}</span></div>
          <span class="badge ${st.alert_level}">${st.flip_type !== 'NONE' ? st.flip_type : st.alert_level}</span>
        </div>
        <div style="font-size:12px">GREEN→RED Pressure: <b>${st.bear_flip_score}/100</b> (${(st.bear_pillars||[]).join(', ')||'none'})</div>
        <div class="meter"><div class="fill-bear" style="width:${st.bear_flip_score}%"></div></div>
        <div style="font-size:12px">RED→GREEN Pressure: <b>${st.bull_flip_score}/100</b> (${(st.bull_pillars||[]).join(', ')||'none'})</div>
        <div class="meter"><div class="fill-bull" style="width:${st.bull_flip_score}%"></div></div>
        <div class="action">ACTION: ${st.directives.summary_action}</div>
        <div class="kpis">
          <div class="box"><b>OI (15m):</b> ${st.oi_interpretation_15m}<br>dCE ${st.d_ce_oi_15m>=0?'+':''}${st.d_ce_oi_15m} | dPE ${st.d_pe_oi_15m>=0?'+':''}${st.d_pe_oi_15m} | PCR ${st.near_pcr} (${st.d_pcr_15m>=0?'+':''}${st.d_pcr_15m})</div>
          <div class="box"><b>Futures (15m):</b> ${st.fut_quadrant_15m}<br>Fut ${st.fut_ltp} vs VWAP ${st.fut_vwap} | Basis ${st.basis} (${st.d_basis_15m>=0?'+':''}${st.d_basis_15m})</div>
          <div class="box"><b>Order Flow:</b> dCVD ${st.d_cvd_15m>=0?'+':''}${st.d_cvd_15m} | OBI-L5 ${(st.fut_obi_l5*100).toFixed(1)}%<br>Walls: CE ${st.ce_wall} / PE ${st.pe_wall}</div>
          <div class="box"><b>Heavyweights:</b> Bull ${st.heavyweight_bull_pct}% / Bear ${st.heavyweight_bear_pct}%<br>${Object.entries(st.heavyweight_states||{}).map(([k,v])=>k+':'+v).join(' ')}</div>
        </div>
        <div style="font-size:12px"><b>Active Triggers:</b><ul>${reasons}</ul></div>
        ${evs ? `<div style="font-size:11px;margin-top:8px;color:#9ca3af"><b>Recent Alerts:</b><ul>${evs}</ul></div>` : ''}
      `;
      grid.appendChild(card);
    }
  } catch (e) {
    document.getElementById('meta').textContent = 'Waiting for reversal_state.json... (' + e + ')';
  }
}
refresh();
setInterval(refresh, 3000);
</script></body></html>
"""


def write_reversal_outputs(root: Path, mode: str, states: Dict[str, Dict[str, Any]]) -> Path:
    out_dir = root / "data" / "reversal_alerts"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_p = out_dir / "reversal_dashboard.html"
    if not html_p.exists():
        html_p.write_text(REVERSAL_HTML)
    st_p = out_dir / "reversal_state.json"
    tmp = st_p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({
        "updated_at": datetime.now(IST).isoformat(),
        "mode": mode, "paper_only": True, "indices": states,
    }, indent=2))
    os.replace(tmp, st_p)
    return st_p


def _start_dashboard_server(directory: Path, port: int) -> Optional[http.server.ThreadingHTTPServer]:
    if port <= 0:
        return None

    class _Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass

    try:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(_Quiet, directory=str(directory)))
    except OSError:
        return None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def print_status(states: Dict[str, Dict[str, Any]]) -> None:
    print(f"\n================ GREEN<->RED REVERSAL RADAR ({datetime.now(IST).strftime('%H:%M:%S IST')}) ================")
    for idx, st in states.items():
        print(
            f"[{idx:<9}] {st['color']:<5} ({st['chg_vs_prev_pct']:+.2f}%) Spot={st['spot_ltp']} "
            f"| G->R={st['bear_flip_score']:>3}/100 R->G={st['bull_flip_score']:>3}/100 "
            f"| {st['alert_level']} ({st['flip_type']})"
        )
        print(
            f"  OI(15m): {st['oi_interpretation_15m']} (dCE={st['d_ce_oi_15m']:+,.0f} dPE={st['d_pe_oi_15m']:+,.0f} dPCR={st['d_pcr_15m']:+.3f}) "
            f"| Fut={st['fut_quadrant_15m']} Basis={st['basis']}({st['d_basis_15m']:+.1f}) "
            f"| HW Bull={st['heavyweight_bull_pct']}% Bear={st['heavyweight_bear_pct']}%"
        )
        print(f"  DIRECTIVE: {st['directives']['summary_action']}")
        for r in st["reasons"][:4]:
            print(f"    -> {r}")


# ---------------------------------------------------------------------------
# Modes: live, replay, selftest
# ---------------------------------------------------------------------------
def run_live(
    root: Path, interval_s: float = 20.0, window_sec: int = 900,
    serve_port: int = 8766, webhook_url: Optional[str] = None,
    cooldown_sec: int = 180, max_cycles: int = 0,
) -> int:
    token = load_token(root)
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    master = load_nse_master(root)
    res = resolve_live_instruments(root, master, today_s)
    monitors = {idx: IndexReversalMonitor(idx, window_sec=window_sec) for idx in INDEX_SPECS}

    # Build single batched quote key map: Spots + Futures + Heavyweight equities
    key_map: Dict[str, str] = {}
    tsym_map: Dict[str, str] = {}
    for idx, spec in INDEX_SPECS.items():
        key_map[spec["spot_key"]] = f"SPOT:{idx}"
        if idx in res["futs"]:
            fk, ft = res["futs"][idx]
            key_map[fk] = f"FUT:{idx}"
            tsym_map[ft] = f"FUT:{idx}"
    for sym, (ek, et) in res["eq_keys"].items():
        key_map[ek] = f"EQ:{sym}"
        tsym_map[et] = f"EQ:{sym}"

    arch_dir = root / "data" / "reversal_alerts" / today_s
    arch_dir.mkdir(parents=True, exist_ok=True)
    snap_p = arch_dir / "snapshots.jsonl"
    st_p = write_reversal_outputs(root, "LIVE", {})
    srv = _start_dashboard_server(st_p.parent, serve_port)
    print(f"Reversal Radar started | Archive: {snap_p}")
    if srv:
        print(f"Live Dashboard: http://127.0.0.1:{serve_port}/reversal_dashboard.html")
    print(f"Strategy Action Bridge: {st_p}")

    # Native fallback CVD tracker if orderflow_footprint_engine.py isn't running
    prev_fut_vol: Dict[str, float] = {}
    prev_fut_px: Dict[str, float] = {}
    native_cvd: Dict[str, float] = {"BANKNIFTY": 0.0, "NIFTY": 0.0}

    cycles = 0
    with open(snap_p, "a", encoding="utf-8") as fh:
        while True:
            t0 = time.monotonic()
            now_dt = datetime.now(IST)
            now_iso, now_ep = now_dt.isoformat(), time.time()

            # 1. Single batched quote call for Spots + Futures + all Heavyweights
            joined = urllib.parse.quote(",".join(key_map.keys()), safe=",")
            q_data = (api_get(f"/v2/market-quote/quotes?instrument_key={joined}", token).get("data") or {})
            parsed: Dict[str, Dict[str, Any]] = {}
            for _rk, q in q_data.items():
                if not isinstance(q, dict):
                    continue
                ik = q.get("instrument_token") or q.get("instrument_key") or ""
                tag = key_map.get(ik) or tsym_map.get((q.get("symbol") or "").strip())
                if tag:
                    parsed[tag] = q

            of_live = _read_fresh_orderflow_state(root)
            states: Dict[str, Dict[str, Any]] = {}

            for idx, spec in INDEX_SPECS.items():
                sq = parsed.get(f"SPOT:{idx}") or {}
                fq = parsed.get(f"FUT:{idx}") or {}
                spot_ltp = _f(sq.get("last_price"))
                if spot_ltp <= 0:
                    continue
                ohlc = sq.get("ohlc") or {}
                prev_close = _f(ohlc.get("close"), spot_ltp)
                day_open = _f(ohlc.get("open"), prev_close)
                fut_ltp = _f(fq.get("last_price"), spot_ltp)
                fut_oi = _f(fq.get("oi"))
                fut_atp = _f(fq.get("average_price"), fut_ltp)
                fut_vol = _f(fq.get("volume"))
                fut_obi = _calc_obi_l5(fq.get("depth") or {})

                # Use rich orderflow_state.json if running, else native CVD fallback
                of_inst = of_live.get(f"{idx}_FUT")
                of_extras: Dict[str, Any] = {}
                if of_inst:
                    fut_cvd = float(of_inst.get("cvd") or 0.0)
                    fut_obi = float(of_inst.get("obi_l5") or fut_obi)
                    of_extras["dpoc"] = (of_inst.get("session_vp") or {}).get("poc")
                    last_fp = (of_inst.get("footprint_bars") or [{}])[-1]
                    of_extras["stacked_buy"] = bool(last_fp.get("stacked_buy"))
                    of_extras["stacked_sell"] = bool(last_fp.get("stacked_sell"))
                    rec_al = of_inst.get("recent_alerts") or []
                    of_extras["bullish_absorption"] = any(a.get("type") == "BULLISH_ABSORPTION" for a in rec_al[-2:])
                    of_extras["bearish_absorption"] = any(a.get("type") == "BEARISH_ABSORPTION" for a in rec_al[-2:])
                else:
                    if idx in prev_fut_vol and fut_vol > prev_fut_vol[idx]:
                        dv = fut_vol - prev_fut_vol[idx]
                        dp = fut_ltp - prev_fut_px[idx]
                        native_cvd[idx] += dv if dp > 0 else (-dv if dp < 0 else 0.0)
                    prev_fut_vol[idx] = fut_vol
                    prev_fut_px[idx] = fut_ltp
                    fut_cvd = native_cvd[idx]

                # 2. Fetch active option chain (1 call per index)
                exp = res["expiries"].get(idx)
                chain_rows = []
                if exp:
                    enc = urllib.parse.quote(spec["spot_key"], safe="")
                    chain_rows = (api_get(f"/v2/option/chain?instrument_key={enc}&expiry_date={exp}", token).get("data") or [])
                    time.sleep(0.25)
                cm = extract_near_atm_chain_metrics(chain_rows, spot_ltp, spec["step"])

                # 3. Heavyweight snapshot
                hw = {}
                for sym in spec["heavyweights"]:
                    eq = parsed.get(f"EQ:{sym}") or {}
                    if _f(eq.get("last_price")) > 0:
                        hw[sym] = {"ltp": _f(eq.get("last_price")), "atp": _f(eq.get("average_price"), _f(eq.get("last_price")))}

                obs = {
                    "index": idx, "timestamp_ist": now_iso, "epoch": now_ep,
                    "spot_ltp": spot_ltp, "prev_close": prev_close, "day_open": day_open,
                    "fut_ltp": fut_ltp, "fut_oi": fut_oi, "fut_atp": fut_atp,
                    "fut_obi_l5": fut_obi, "fut_cvd": fut_cvd,
                    "chain_metrics": cm, "heavyweights": hw, "orderflow_extras": of_extras,
                }
                fh.write(json.dumps(obs) + "\n")
                st = monitors[idx].evaluate(obs)
                states[idx] = st

                # Push high-priority notification with cooldown
                if st["alert_level"] in ("IMMINENT_FLIP", "CONFIRMED_FLIP", "FAKE_CROSS_WARNING"):
                    ckey = f"{idx}:{st['flip_type']}"
                    if now_ep - monitors[idx].last_alert_ts.get(ckey, 0.0) >= cooldown_sec:
                        monitors[idx].last_alert_ts[ckey] = now_ep
                        send_push_alert(
                            f"[{idx}] {st['flip_type']} ({st['active_score']}/100)",
                            f"Spot {st['spot_ltp']} ({st['chg_vs_prev_pct']:+.2f}%) | Action: {st['directives']['summary_action']}\n"
                            + "\n".join(f"- {r}" for r in st["reasons"][:4]),
                            webhook_url=webhook_url,
                        )

            fh.flush()
            write_reversal_outputs(root, "LIVE", states)
            print_status(states)
            cycles += 1
            if max_cycles > 0 and cycles >= max_cycles:
                break
            if datetime.now(IST).time() >= dtime(15, 32):
                print("Market closed (>= 15:32 IST) — stopping cleanly.")
                break
            el = time.monotonic() - t0
            if el < interval_s:
                time.sleep(interval_s - el)
    return 0


def run_replay(root: Path, jsonl_path: Path) -> int:
    if not jsonl_path.exists():
        print(f"Replay file not found: {jsonl_path}")
        return 2
    monitors = {idx: IndexReversalMonitor(idx) for idx in INDEX_SPECS}
    states: Dict[str, Dict[str, Any]] = {}
    cnt = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obs = json.loads(line)
            idx = obs["index"]
            states[idx] = monitors[idx].evaluate(obs)
            cnt += 1
    write_reversal_outputs(root, f"REPLAY:{jsonl_path.name}", states)
    print(f"Replayed {cnt} observations across {len(states)} indices.")
    print_status(states)
    return 0


def run_selftest() -> int:
    print("=== GREEN<->RED REVERSAL & OI FLIP DETECTOR SELF-TEST ===")
    # Scenario 1: Bank Nifty is STILL GREEN (+0.22%), yet Put Writers unwind,
    # Call Writers slam ATM, Futures Short Buildup + Basis drops, CVD & OBI flip
    # negative, Top-5 heavyweights turn bearish -> must fire IMMINENT_GREEN_TO_RED BEFORE red!
    m = IndexReversalMonitor("BANKNIFTY", window_sec=900)
    t0 = 1764130000.0
    obs_green_ok = {
        "index": "BANKNIFTY", "timestamp_ist": "2026-11-26T10:30:00+05:30", "epoch": t0,
        "spot_ltp": 61250.0, "prev_close": 61000.0, "day_open": 61100.0,
        "fut_ltp": 61310.0, "fut_oi": 2500000.0, "fut_atp": 61220.0,
        "fut_obi_l5": 0.30, "fut_cvd": 1200.0,
        "chain_metrics": {
            "valid": True, "atm": 61200, "strikes_used": 7,
            "ce_oi": 1000000.0, "pe_oi": 1300000.0, "near_pcr": 1.30,
            "ce_ltp_sum": 1500.0, "pe_ltp_sum": 1200.0, "iv_skew": 0.5,
            "ce_wall_strike": 61500, "pe_wall_strike": 61000,
        },
        "heavyweights": {
            "HDFCBANK": {"ltp": 815.0, "atp": 810.0}, "ICICIBANK": {"ltp": 1605.0, "atp": 1598.0},
            "SBIN": {"ltp": 1095.0, "atp": 1090.0}, "KOTAKBANK": {"ltp": 1820.0, "atp": 1815.0},
            "AXISBANK": {"ltp": 1350.0, "atp": 1345.0},
        },
    }
    st0 = m.evaluate(obs_green_ok)
    assert st0["color"] == "GREEN" and st0["alert_level"] == "STABLE", st0

    obs_pre_g2r = {
        "index": "BANKNIFTY", "timestamp_ist": "2026-11-26T10:45:00+05:30", "epoch": t0 + 900,
        "spot_ltp": 61120.0,  # STILL GREEN (+0.20% above prev_close 61000)!
        "prev_close": 61000.0, "day_open": 61100.0,
        "fut_ltp": 61150.0, "fut_oi": 2590000.0, "fut_atp": 61210.0,  # Short buildup + below VWAP + basis dropped -30 pts!
        "fut_obi_l5": -0.35, "fut_cvd": 400.0,  # dCVD = -800!
        "chain_metrics": {
            "valid": True, "atm": 61100, "strikes_used": 7,
            "ce_oi": 1120000.0, "pe_oi": 1180000.0, "near_pcr": 1.0536,  # CE +12%, PE -9.2%, PCR -0.246!
            "ce_ltp_sum": 1320.0, "pe_ltp_sum": 1390.0, "iv_skew": 1.4,
            "ce_wall_strike": 61200, "pe_wall_strike": 61000,
        },
        "heavyweights": {
            "HDFCBANK": {"ltp": 808.0, "atp": 811.0}, "ICICIBANK": {"ltp": 1592.0, "atp": 1599.0},
            "SBIN": {"ltp": 1086.0, "atp": 1091.0}, "KOTAKBANK": {"ltp": 1812.0, "atp": 1816.0},
            "AXISBANK": {"ltp": 1348.0, "atp": 1346.0},
        },
        "orderflow_extras": {"bearish_absorption": True, "dpoc": 61200.0},
    }
    st1 = m.evaluate(obs_pre_g2r)
    assert st1["color"] == "GREEN", "Must fire BEFORE spot actually turns RED!"
    assert st1["alert_level"] == "IMMINENT_FLIP" and st1["flip_type"] == "IMMINENT_GREEN_TO_RED", st1
    assert st1["directives"]["exit_ce_now"] is True and st1["directives"]["block_ce_entries"] is True
    print(f"  OK  Scenario 1 (Pre-flip G->R while still +0.20% GREEN): {st1['flip_type']} ({st1['active_score']}/100) -> {st1['directives']['summary_action']}")

    # Scenario 2: Spot actually crosses RED (< 61000) with full OI + Breadth -> CONFIRMED_GREEN_TO_RED
    obs_conf_g2r = dict(obs_pre_g2r, timestamp_ist="2026-11-26T10:50:00+05:30", epoch=t0 + 1200, spot_ltp=60960.0, fut_ltp=60980.0)
    st2 = m.evaluate(obs_conf_g2r)
    assert st2["color"] == "RED" and st2["flip_type"] == "CONFIRMED_GREEN_TO_RED", st2
    print(f"  OK  Scenario 2 (Confirmed G->R cross): {st2['flip_type']} ({st2['active_score']}/100)")

    # Scenario 3: Nifty RED -> GREEN short-covering squeeze while still RED (-0.12%)!
    mn = IndexReversalMonitor("NIFTY", window_sec=900)
    mn.evaluate({
        "index": "NIFTY", "timestamp_ist": "2026-11-26T11:00:00+05:30", "epoch": t0,
        "spot_ltp": 25380.0, "prev_close": 25500.0, "day_open": 25460.0,
        "fut_ltp": 25400.0, "fut_oi": 12000000.0, "fut_atp": 25440.0,
        "fut_obi_l5": -0.25, "fut_cvd": -900.0,
        "chain_metrics": {
            "valid": True, "atm": 25400, "strikes_used": 7,
            "ce_oi": 5000000.0, "pe_oi": 3800000.0, "near_pcr": 0.76,
            "ce_ltp_sum": 800.0, "pe_ltp_sum": 1100.0, "iv_skew": 1.6,
            "ce_wall_strike": 25500, "pe_wall_strike": 25300,
        },
        "heavyweights": {
            "HDFCBANK": {"ltp": 800.0, "atp": 805.0}, "RELIANCE": {"ltp": 1280.0, "atp": 1290.0},
            "ICICIBANK": {"ltp": 1580.0, "atp": 1590.0}, "INFY": {"ltp": 1850.0, "atp": 1860.0},
        },
    })
    st_r2g = mn.evaluate({
        "index": "NIFTY", "timestamp_ist": "2026-11-26T11:15:00+05:30", "epoch": t0 + 900,
        "spot_ltp": 25470.0,  # STILL RED (-0.12% below 25500)!
        "prev_close": 25500.0, "day_open": 25460.0,
        "fut_ltp": 25505.0, "fut_oi": 11600000.0, "fut_atp": 25455.0,  # Short covering + Basis +15 + above VWAP!
        "fut_obi_l5": 0.38, "fut_cvd": -100.0,  # dCVD +800!
        "chain_metrics": {
            "valid": True, "atm": 25500, "strikes_used": 7,
            "ce_oi": 4500000.0, "pe_oi": 4400000.0, "near_pcr": 0.9778,  # CE -10% covering, PE +15.8% writing!
            "ce_ltp_sum": 940.0, "pe_ltp_sum": 920.0, "iv_skew": 0.6,
            "ce_wall_strike": 25600, "pe_wall_strike": 25400,
        },
        "heavyweights": {
            "HDFCBANK": {"ltp": 809.0, "atp": 805.0}, "RELIANCE": {"ltp": 1296.0, "atp": 1290.0},
            "ICICIBANK": {"ltp": 1598.0, "atp": 1590.0}, "INFY": {"ltp": 1865.0, "atp": 1860.0},
        },
        "orderflow_extras": {"bullish_absorption": True, "dpoc": 25440.0},
    })
    assert st_r2g["flip_type"] in ("IMMINENT_RED_TO_GREEN", "CONFIRMED_RED_TO_GREEN") and st_r2g["directives"]["exit_pe_now"] is True, st_r2g
    print(f"  OK  Scenario 3 (Nifty R->G Short-Covering Squeeze): {st_r2g['flip_type']} ({st_r2g['active_score']}/100) -> {st_r2g['directives']['summary_action']}")

    # Scenario 4: Fake Green->Red cross WITHOUT OI/OrderFlow/Breadth support -> FAKE_CROSS_WARNING
    mf = IndexReversalMonitor("NIFTY", window_sec=900)
    mf.evaluate({
        "index": "NIFTY", "timestamp_ist": "2026-11-26T12:00:00+05:30", "epoch": t0,
        "spot_ltp": 25510.0, "prev_close": 25500.0, "day_open": 25505.0,
        "fut_ltp": 25540.0, "fut_oi": 12000000.0, "fut_atp": 25520.0,
        "fut_obi_l5": 0.15, "fut_cvd": 300.0,
        "chain_metrics": {"valid": True, "atm": 25500, "strikes_used": 7, "ce_oi": 4000000.0, "pe_oi": 4500000.0, "near_pcr": 1.125, "ce_ltp_sum": 900.0, "pe_ltp_sum": 850.0, "iv_skew": 0.5, "ce_wall_strike": 25600, "pe_wall_strike": 25400},
        "heavyweights": {"HDFCBANK": {"ltp": 810.0, "atp": 808.0}},
    })
    st_fake = mf.evaluate({
        "index": "NIFTY", "timestamp_ist": "2026-11-26T12:05:00+05:30", "epoch": t0 + 300,
        "spot_ltp": 25495.0, "prev_close": 25500.0, "day_open": 25505.0,  # tiny dip below prev_close!
        "fut_ltp": 25525.0, "fut_oi": 12000000.0, "fut_atp": 25520.0,  # STILL above VWAP, OI flat!
        "fut_obi_l5": 0.10, "fut_cvd": 320.0,
        "chain_metrics": {"valid": True, "atm": 25500, "strikes_used": 7, "ce_oi": 4010000.0, "pe_oi": 4510000.0, "near_pcr": 1.1247, "ce_ltp_sum": 895.0, "pe_ltp_sum": 855.0, "iv_skew": 0.5, "ce_wall_strike": 25600, "pe_wall_strike": 25400},
        "heavyweights": {"HDFCBANK": {"ltp": 810.0, "atp": 808.0}},
    })
    assert st_fake["alert_level"] == "FAKE_CROSS_WARNING", st_fake
    print(f"  OK  Scenario 4 (Fake wick below prev_close): {st_fake['flip_type']} -> {st_fake['directives']['summary_action']}")

    # Verify JSONL replay + HTML dashboard + JSON bridge
    with tempfile.TemporaryDirectory() as td:
        troot = Path(td)
        jf = troot / "rev.jsonl"
        jf.write_text(json.dumps(obs_green_ok) + "\n" + json.dumps(obs_pre_g2r) + "\n")
        assert run_replay(troot, jf) == 0
        assert (troot / "data" / "reversal_alerts" / "reversal_state.json").exists()
        assert (troot / "data" / "reversal_alerts" / "reversal_dashboard.html").exists()

    print("  OK  Replay, strategy action bridge, and Reversal Radar dashboard verified")
    print("REVERSAL FLIP DETECTOR SELF-TEST PASSED!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "live", "replay"), default="live")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--interval", type=float, default=20.0, help="Live poll interval in seconds (>= 10)")
    ap.add_argument("--window-sec", type=int, default=900, help="Rolling velocity lookback in seconds (default 900 = 15m)")
    ap.add_argument("--serve-port", type=int, default=8766, help="Localhost port for HTML radar (0 = disable)")
    ap.add_argument("--webhook-url", default=None, help="Optional webhook URL for push alerts")
    ap.add_argument("--cooldown-sec", type=int, default=180, help="Minimum seconds between duplicate push alerts")
    ap.add_argument("--max-cycles", type=int, default=0, help="Stop after N cycles (0 = run until 15:32 IST)")
    ap.add_argument("--file", dest="replay_file", help="JSONL file for --mode replay")
    a = ap.parse_args(argv)

    if a.mode == "selftest":
        return run_selftest()
    root = Path(a.root)
    if a.mode == "replay":
        if not a.replay_file:
            print("--file is required for --mode replay", file=sys.stderr)
            return 2
        return run_replay(root, Path(a.replay_file))
    try:
        return run_live(
            root, interval_s=max(a.interval, 10.0), window_sec=a.window_sec,
            serve_port=a.serve_port, webhook_url=a.webhook_url,
            cooldown_sec=a.cooldown_sec, max_cycles=a.max_cycles,
        )
    except RateLimited as e:
        print(f"RATE_LIMITED HARD STOP: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
