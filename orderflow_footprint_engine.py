#!/usr/bin/env python3
"""LIVE ORDER FLOW, VOLUME PROFILE & FOOTPRINT ENGINE (Upstox Real Snapshots).

Builds genuine, real-time microstructure analytics on NSE Near-Month Index Futures
(BANKNIFTY FUT & NIFTY FUT — where real volume, OI, and 5-level order book depth
exist; spot indices have zero volume/depth) plus optional ATM CE/PE option tape.

HONEST FEED DISCLOSURE:
  Upstox retail feeds (REST /v2/market-quote/quotes and WebSocket v3 full mode)
  deliver ~1-2 aggregated snapshots/second with 5-level depth, NOT NSE TBT L3
  colocation tick-by-tick feeds. Therefore:
    - Volume Profile (dPOC / dVAH / dVAL / HVN / LVN + prior-day pPOC/pVAH/pVAL)
      is seeded immediately from 1-min intraday & prior-day Futures candles and
      updated live at exact traded price bins on every snapshot.
    - Order Flow Delta, CVD, 5-min Footprint Bid x Ask ladders, 3:1 diagonal &
      stacked imbalances, L2 Order Book Imbalance (OBI), OI flow, and Absorption
      Divergences are computed STRICTLY from LIVE incremental volume deltas
      classified via the causal Lee-Ready Quote Rule (against prior-tick best
      bid/ask) — NEVER fabricated from historical OHLCV bars.
    - Every live snapshot is appended to data/orderflow_snapshots/YYYY-MM-DD/
      snapshots.jsonl so you accumulate a real replayable Order Flow archive.

OUTPUTS (Paper / Analytics Only — Zero Broker Orders):
  1. Live ANSI terminal Footprint ladder + Volume Profile + Order Flow summary.
  2. Auto-refreshing standalone HTML visual dashboard:
       data/orderflow_live/orderflow_dashboard.html
  3. Machine-readable JSON bridge for strategy confirmation filters:
       data/orderflow_live/orderflow_state.json
  4. Raw live snapshot archive for offline replay & future backtesting:
       data/orderflow_snapshots/YYYY-MM-DD/snapshots.jsonl

Usage:
  # 1. Run deterministic offline self-test + replay check (zero API calls)
  python3 orderflow_footprint_engine.py --mode selftest

  # 2. Run live during market hours (09:15-15:30 IST) — futures only (1 call/1.5s)
  python3 orderflow_footprint_engine.py --mode live --interval 1.5

  # 3. Run live with Futures + ATM CE/PE option tape included (still 1 batch call!)
  python3 orderflow_footprint_engine.py --mode live --with-options --interval 1.5

  # 4. Replay any previously recorded live JSONL file offline
  python3 orderflow_footprint_engine.py --mode replay --file data/orderflow_snapshots/2026-11-26/snapshots.jsonl
"""
from __future__ import annotations

import argparse
import csv
import functools
import gzip
import http.server
import json
import math
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from datetime import date as ddate, datetime, time as dtime, timedelta
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

DEFAULT_TICK_BINS: Dict[str, float] = {
    "BANKNIFTY_FUT": 10.0,
    "NIFTY_FUT": 5.0,
    "BANKNIFTY_CE": 2.0,
    "BANKNIFTY_PE": 2.0,
    "NIFTY_CE": 1.0,
    "NIFTY_PE": 1.0,
}

DEPTH_WEIGHTS = (1.0, 0.70, 0.50, 0.35, 0.25)


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "upstox_refresh" / ".env").exists() or (live / "data").exists():
        return live
    return Path(__file__).resolve().parent


def bin_price(price: float, step: float) -> float:
    return round(round(price / step) * step, 2)


def slot_5m(ts_hhmm: str) -> str:
    h, m = int(ts_hhmm[:2]), int(ts_hhmm[3:5])
    return f"{h:02d}:{(m // 5) * 5:02d}"


# ---------------------------------------------------------------------------
# 1. Volume Profile Engine (POC, 70% VAH/VAL, HVN, LVN)
# ---------------------------------------------------------------------------
class VolumeProfile:
    """Real-time & backfilled Volume Profile with standard 70% Value Area."""

    def __init__(self, step: float):
        self.step = float(step)
        self.bins: Dict[float, float] = defaultdict(float)
        self.total_vol: float = 0.0

    def add_trade(self, price: float, volume: float) -> None:
        if volume <= 0 or price <= 0:
            return
        b = bin_price(price, self.step)
        self.bins[b] += float(volume)
        self.total_vol += float(volume)

    def add_ohlcv_bar(self, low: float, high: float, close: float, volume: float) -> None:
        """Distribute 1-min candle volume across [low, high] bins (higher weight near close)."""
        if volume <= 0 or high <= 0 or low <= 0:
            return
        b_lo = bin_price(low, self.step)
        b_hi = bin_price(high, self.step)
        n_steps = max(1, int(round((b_hi - b_lo) / self.step)) + 1)
        if n_steps == 1:
            self.add_trade(close, volume)
            return
        # Triangular weight peaking at close bin for realistic 1-min profile
        b_cl = bin_price(close, self.step)
        levels = [round(b_lo + k * self.step, 2) for k in range(n_steps)]
        weights = [
            1.0 + max(0.0, 1.0 - abs(lv - b_cl) / max(b_hi - b_lo, self.step))
            for lv in levels
        ]
        wsum = sum(weights)
        for lv, w in zip(levels, weights):
            dv = float(volume) * (w / wsum)
            self.bins[lv] += dv
            self.total_vol += dv

    def summary(self, value_area_pct: float = 0.70) -> Dict[str, Any]:
        if not self.bins or self.total_vol <= 0:
            return {
                "poc": None, "vah": None, "val": None, "total_vol": 0,
                "hvns": [], "lvns": [], "histogram": [],
            }
        levels = sorted(self.bins.keys())
        poc_idx = max(range(len(levels)), key=lambda i: self.bins[levels[i]])
        poc = levels[poc_idx]

        # Standard Market Profile 70% Value Area expansion (2 bins above vs 2 bins below)
        target = self.total_vol * value_area_pct
        included = {poc_idx}
        cum = self.bins[poc]
        lo_i = poc_idx - 1
        hi_i = poc_idx + 1
        while cum < target and (lo_i >= 0 or hi_i < len(levels)):
            up_vol = 0.0
            up_idxs = []
            for k in (hi_i, hi_i + 1):
                if k < len(levels):
                    up_vol += self.bins[levels[k]]
                    up_idxs.append(k)
            dn_vol = 0.0
            dn_idxs = []
            for k in (lo_i, lo_i - 1):
                if k >= 0:
                    dn_vol += self.bins[levels[k]]
                    dn_idxs.append(k)
            if up_idxs and (not dn_idxs or up_vol >= dn_vol):
                for k in up_idxs:
                    included.add(k)
                    cum += self.bins[levels[k]]
                hi_i += len(up_idxs)
            elif dn_idxs:
                for k in dn_idxs:
                    included.add(k)
                    cum += self.bins[levels[k]]
                lo_i -= len(dn_idxs)
            else:
                break

        val = levels[min(included)]
        vah = levels[max(included)]
        mean_v = self.total_vol / len(levels)
        hvns = [lv for lv in levels if self.bins[lv] >= 1.5 * mean_v]
        lvns = [
            lv for lv in levels
            if val <= lv <= vah and self.bins[lv] <= 0.35 * mean_v
        ]
        # Top histogram around POC (up to 40 bins for dashboard)
        hist = [
            {"price": lv, "vol": round(self.bins[lv], 1), "in_va": val <= lv <= vah}
            for lv in reversed(levels)
        ]
        return {
            "poc": poc,
            "vah": vah,
            "val": val,
            "total_vol": int(round(self.total_vol)),
            "hvns": hvns[:8],
            "lvns": lvns[:8],
            "histogram": hist[:45],
        }


# ---------------------------------------------------------------------------
# 2. Footprint Bar (5-Min Bid x Ask Ladder + 3:1 Diagonal & Stacked Imbalances)
# ---------------------------------------------------------------------------
class FootprintBar:
    """Single 5-minute footprint bar built from live classified order flow."""

    def __init__(self, slot: str, step: float, first_price: float):
        self.slot = slot
        self.step = float(step)
        self.open = float(first_price)
        self.high = float(first_price)
        self.low = float(first_price)
        self.close = float(first_price)
        # price_bin -> [bid_vol (aggressive sells), ask_vol (aggressive buys)]
        self.levels: Dict[float, List[float]] = defaultdict(lambda: [0.0, 0.0])
        self.total_bid: float = 0.0
        self.total_ask: float = 0.0
        self.max_delta: float = 0.0
        self.min_delta: float = 0.0
        self.ticks: int = 0

    def update(self, price: float, bid_vol: float, ask_vol: float) -> None:
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = float(price)
        self.ticks += 1
        if bid_vol > 0 or ask_vol > 0:
            b = bin_price(price, self.step)
            self.levels[b][0] += float(bid_vol)
            self.levels[b][1] += float(ask_vol)
            self.total_bid += float(bid_vol)
            self.total_ask += float(ask_vol)
            delta = self.total_ask - self.total_bid
            self.max_delta = max(self.max_delta, delta)
            self.min_delta = min(self.min_delta, delta)

    def analyze(self, imb_ratio: float = 3.0, min_imb_vol: float = 30.0) -> Dict[str, Any]:
        tot = self.total_bid + self.total_ask
        delta = self.total_ask - self.total_bid
        delta_pct = round(100.0 * delta / tot, 1) if tot > 0 else 0.0
        sorted_lvls = sorted(self.levels.keys())

        poc = None
        if sorted_lvls:
            poc = max(sorted_lvls, key=lambda lv: self.levels[lv][0] + self.levels[lv][1])

        buy_imbs: List[float] = []
        sell_imbs: List[float] = []
        ladder: List[Dict[str, Any]] = []

        for lv in sorted(sorted_lvls, reverse=True):
            bv, av = self.levels[lv]
            below = round(lv - self.step, 2)
            above = round(lv + self.step, 2)
            # Diagonal buy imbalance: ask at P >= ratio * bid at (P - step)
            b_below = self.levels[below][0] if below in self.levels else 0.0
            a_above = self.levels[above][1] if above in self.levels else 0.0
            is_buy_imb = (av >= min_imb_vol) and (b_below == 0 or av >= imb_ratio * b_below) and (below in self.levels)
            is_sell_imb = (bv >= min_imb_vol) and (a_above == 0 or bv >= imb_ratio * a_above) and (above in self.levels)
            if is_buy_imb:
                buy_imbs.append(lv)
            if is_sell_imb:
                sell_imbs.append(lv)
            ladder.append({
                "price": lv,
                "bid": int(round(bv)),
                "ask": int(round(av)),
                "delta": int(round(av - bv)),
                "is_poc": lv == poc,
                "buy_imb": is_buy_imb,
                "sell_imb": is_sell_imb,
            })

        def _stacked(pts: Sequence[float]) -> List[List[float]]:
            s = sorted(pts)
            stacks: List[List[float]] = []
            cur: List[float] = []
            for p in s:
                if not cur or abs((p - cur[-1]) - self.step) < 1e-6:
                    cur.append(p)
                else:
                    if len(cur) >= 3:
                        stacks.append(cur)
                    cur = [p]
            if len(cur) >= 3:
                stacks.append(cur)
            return stacks

        # Unfinished auction check at bar extremes
        hi_bin = bin_price(self.high, self.step)
        lo_bin = bin_price(self.low, self.step)
        unfinished_high = bool(hi_bin in self.levels and self.levels[hi_bin][0] > 0 and self.levels[hi_bin][1] > 0)
        unfinished_low = bool(lo_bin in self.levels and self.levels[lo_bin][0] > 0 and self.levels[lo_bin][1] > 0)

        return {
            "slot": self.slot,
            "open": round(self.open, 2),
            "high": round(self.high, 2),
            "low": round(self.low, 2),
            "close": round(self.close, 2),
            "volume": int(round(tot)),
            "bid_vol": int(round(self.total_bid)),
            "ask_vol": int(round(self.total_ask)),
            "delta": int(round(delta)),
            "delta_pct": delta_pct,
            "max_delta": int(round(self.max_delta)),
            "min_delta": int(round(self.min_delta)),
            "bar_poc": poc,
            "buy_imbalances": sorted(buy_imbs),
            "sell_imbalances": sorted(sell_imbs),
            "stacked_buy": _stacked(buy_imbs),
            "stacked_sell": _stacked(sell_imbs),
            "unfinished_high": unfinished_high,
            "unfinished_low": unfinished_low,
            "ladder": ladder,
        }


# ---------------------------------------------------------------------------
# 3. Full Instrument Order Flow Tracker (Snapshot -> Lee-Ready -> VP + FP + OBI)
# ---------------------------------------------------------------------------
class InstrumentOrderFlow:
    """Tracks live Order Flow, Volume Profile, Footprint, OBI & OI for 1 contract."""

    def __init__(self, label: str, instrument_key: str, tick_bin: float):
        self.label = label
        self.instrument_key = instrument_key
        self.tick_bin = float(tick_bin)
        self.prior_vp = VolumeProfile(tick_bin)
        self.session_vp = VolumeProfile(tick_bin)
        self.bars: Dict[str, FootprintBar] = {}
        self.bar_order: List[str] = []

        # Causal state from previous snapshot
        self.prev_ltp: Optional[float] = None
        self.prev_vol: Optional[float] = None
        self.prev_oi: Optional[float] = None
        self.prev_best_bid: Optional[float] = None
        self.prev_best_ask: Optional[float] = None
        self.prev_trade_sign: int = 0

        # Cumulative session live order flow metrics
        self.cvd: float = 0.0
        self.session_high: float = -1e18
        self.session_low: float = 1e18
        self.live_ticks: int = 0
        self.last_atp: Optional[float] = None
        self.last_obi_l1: float = 0.0
        self.last_obi_l5: float = 0.0
        self.last_tbq_tsq_ratio: float = 1.0
        self.last_spread: float = 0.0
        self.last_oi_regime: str = "NEUTRAL"
        self.last_update_ist: Optional[str] = None
        self.obi_hist: Deque[float] = deque(maxlen=20)
        self.cvd_hist: Deque[Tuple[str, float, float]] = deque(maxlen=60)
        self.alerts: Deque[Dict[str, Any]] = deque(maxlen=25)

    def seed_prior_profile(self, candles_1m: Sequence[Sequence[Any]]) -> None:
        for c in candles_1m:
            # Upstox candle: [ts, o, h, l, c, vol, oi]
            self.prior_vp.add_ohlcv_bar(float(c[3]), float(c[2]), float(c[4]), float(c[5] or 0))

    def seed_intraday_profile(self, candles_1m: Sequence[Sequence[Any]]) -> None:
        for c in candles_1m:
            h, l, cl, v = float(c[2]), float(c[3]), float(c[4]), float(c[5] or 0)
            self.session_vp.add_ohlcv_bar(l, h, cl, v)
            self.session_high = max(self.session_high, h)
            self.session_low = min(self.session_low, l)

    def ingest_snapshot(self, snap: Dict[str, Any]) -> Dict[str, Any]:
        """Process one live Upstox quote snapshot causally (Lee-Ready Quote Rule)."""
        ts = str(snap.get("timestamp_ist") or datetime.now(IST).isoformat())
        hhmm = ts[11:16] if len(ts) >= 16 else datetime.now(IST).strftime("%H:%M")
        ltp = float(snap.get("ltp") or 0.0)
        vol = float(snap.get("volume") or 0.0)
        oi = float(snap.get("oi") or 0.0)
        atp = float(snap.get("atp") or 0.0)
        tbq = float(snap.get("tbq") or 0.0)
        tsq = float(snap.get("tsq") or 0.0)
        bids = snap.get("bids") or []   # list of [price, qty]
        asks = snap.get("asks") or []

        if ltp <= 0:
            return {"status": "EMPTY_LTP"}

        best_bid = float(bids[0][0]) if bids and bids[0][0] else 0.0
        best_ask = float(asks[0][0]) if asks and asks[0][0] else 0.0
        self.last_spread = round(best_ask - best_bid, 2) if (best_ask > 0 and best_bid > 0) else 0.0
        self.last_atp = round(atp, 2) if atp > 0 else self.last_atp

        # Compute L1 and L5 distance-weighted Order Book Imbalance (OBI)
        b1q = float(bids[0][1]) if bids else 0.0
        a1q = float(asks[0][1]) if asks else 0.0
        self.last_obi_l1 = round((b1q - a1q) / (b1q + a1q), 4) if (b1q + a1q) > 0 else 0.0
        wb = sum(DEPTH_WEIGHTS[i] * float(bids[i][1]) for i in range(min(5, len(bids))))
        wa = sum(DEPTH_WEIGHTS[i] * float(asks[i][1]) for i in range(min(5, len(asks))))
        self.last_obi_l5 = round((wb - wa) / (wb + wa), 4) if (wb + wa) > 0 else 0.0
        self.obi_hist.append(self.last_obi_l5)
        self.last_tbq_tsq_ratio = round(tbq / tsq, 3) if tsq > 0 else 1.0

        # Incremental volume + causal Lee-Ready classification against PRIOR bid/ask
        bid_vol = 0.0
        ask_vol = 0.0
        dv = 0.0
        if self.prev_vol is not None and vol > self.prev_vol:
            dv = vol - self.prev_vol
            ref_bid = self.prev_best_bid if (self.prev_best_bid and self.prev_best_bid > 0) else best_bid
            ref_ask = self.prev_best_ask if (self.prev_best_ask and self.prev_best_ask > 0) else best_ask
            if ref_ask > 0 and ltp >= ref_ask:
                ask_vol = dv
                self.prev_trade_sign = 1
            elif ref_bid > 0 and ltp <= ref_bid:
                bid_vol = dv
                self.prev_trade_sign = -1
            elif self.prev_ltp is not None and ltp > self.prev_ltp:
                ask_vol = dv
                self.prev_trade_sign = 1
            elif self.prev_ltp is not None and ltp < self.prev_ltp:
                bid_vol = dv
                self.prev_trade_sign = -1
            elif self.prev_trade_sign == 1:
                ask_vol = dv
            elif self.prev_trade_sign == -1:
                bid_vol = dv
            else:
                bid_vol = dv * 0.5
                ask_vol = dv * 0.5

            self.cvd += (ask_vol - bid_vol)
            self.session_vp.add_trade(ltp, dv)

        # OI flow classification
        if self.prev_oi is not None and self.prev_ltp is not None and oi > 0:
            doi = oi - self.prev_oi
            dp = ltp - self.prev_ltp
            if abs(doi) > 0 and abs(dp) > 0:
                if dp > 0 and doi > 0:
                    self.last_oi_regime = "LONG_BUILDUP"
                elif dp < 0 and doi > 0:
                    self.last_oi_regime = "SHORT_BUILDUP"
                elif dp > 0 and doi < 0:
                    self.last_oi_regime = "SHORT_COVERING"
                else:
                    self.last_oi_regime = "LONG_UNWINDING"

        # Update 5-min Footprint bar
        s5 = slot_5m(hhmm)
        if s5 not in self.bars:
            self.bars[s5] = FootprintBar(s5, self.tick_bin, ltp)
            self.bar_order.append(s5)
        bar = self.bars[s5]
        bar.update(ltp, bid_vol, ask_vol)

        # Absorption / Divergence detection on new session extremes
        new_high = ltp > self.session_high and self.session_high > -1e17
        new_low = ltp < self.session_low and self.session_low < 1e17
        self.session_high = max(self.session_high, ltp)
        self.session_low = min(self.session_low, ltp)
        bar_delta = bar.total_ask - bar.total_bid
        bar_tot = bar.total_ask + bar.total_bid

        if new_high and bar_tot >= 150 and bar_delta < -0.20 * bar_tot:
            self.alerts.append({
                "time": hhmm, "type": "BEARISH_ABSORPTION",
                "msg": f"New high {ltp:.1f} on negative bar delta {int(bar_delta)} (passive sellers absorbing)",
            })
        elif new_low and bar_tot >= 150 and bar_delta > 0.20 * bar_tot:
            self.alerts.append({
                "time": hhmm, "type": "BULLISH_ABSORPTION",
                "msg": f"New low {ltp:.1f} on positive bar delta +{int(bar_delta)} (passive buyers absorbing)",
            })

        self.live_ticks += 1
        self.cvd_hist.append((hhmm, round(ltp, 2), round(self.cvd, 1)))
        self.prev_ltp = ltp
        self.prev_vol = vol
        self.prev_oi = oi if oi > 0 else self.prev_oi
        self.prev_best_bid = best_bid if best_bid > 0 else self.prev_best_bid
        self.prev_best_ask = best_ask if best_ask > 0 else self.prev_best_ask
        self.last_update_ist = ts
        return {"dv": dv, "bid_vol": bid_vol, "ask_vol": ask_vol, "slot": s5}

    def snapshot_state(self, max_bars: int = 8) -> Dict[str, Any]:
        sess_vp = self.session_vp.summary()
        prior_vp = self.prior_vp.summary()
        recent_slots = self.bar_order[-max_bars:]
        fp_bars = [self.bars[s].analyze() for s in recent_slots]

        # Auction state vs Developing & Prior Value Area
        auction = "UNKNOWN"
        if self.prev_ltp is not None and sess_vp["vah"] is not None:
            if self.prev_ltp > sess_vp["vah"]:
                auction = "ABOVE_VA"
            elif self.prev_ltp < sess_vp["val"]:
                auction = "BELOW_VA"
            else:
                auction = "INSIDE_VA"

        obi_avg = round(sum(self.obi_hist) / len(self.obi_hist), 4) if self.obi_hist else 0.0
        # Composite directional order-flow bias score in [-3, +3]
        bias_score = 0
        if self.cvd > 0:
            bias_score += 1
        elif self.cvd < 0:
            bias_score -= 1
        if obi_avg >= 0.15:
            bias_score += 1
        elif obi_avg <= -0.15:
            bias_score -= 1
        if self.prev_ltp and self.last_atp:
            bias_score += 1 if self.prev_ltp > self.last_atp else (-1 if self.prev_ltp < self.last_atp else 0)

        return {
            "label": self.label,
            "instrument_key": self.instrument_key,
            "tick_bin": self.tick_bin,
            "updated_at": self.last_update_ist,
            "ltp": round(self.prev_ltp, 2) if self.prev_ltp is not None else None,
            "vwap_atp": self.last_atp,
            "best_bid": self.prev_best_bid,
            "best_ask": self.prev_best_ask,
            "spread": self.last_spread,
            "live_ticks": self.live_ticks,
            "cvd": int(round(self.cvd)),
            "obi_l1": self.last_obi_l1,
            "obi_l5": self.last_obi_l5,
            "obi_l5_avg20": obi_avg,
            "tbq_tsq_ratio": self.last_tbq_tsq_ratio,
            "oi": int(round(self.prev_oi)) if self.prev_oi else 0,
            "oi_regime": self.last_oi_regime,
            "auction_state": auction,
            "orderflow_bias_score": bias_score,
            "session_vp": sess_vp,
            "prior_vp": {k: prior_vp[k] for k in ("poc", "vah", "val", "total_vol")},
            "footprint_bars": fp_bars,
            "recent_alerts": list(self.alerts)[-8:],
        }


# ---------------------------------------------------------------------------
# 4. Upstox Live Feed Client (Stdlib-Only Batch Quotes + 1m Profile Seed)
# ---------------------------------------------------------------------------
def load_token(root: Path) -> str:
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


def api_get(path: str, token: str) -> Dict[str, Any]:
    url = path if path.startswith("http") else (API + path)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"HTTP 429 on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


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


def resolve_near_futures(
    master_rows: Sequence[Dict[str, str]], today_s: str
) -> Dict[str, Tuple[str, str, str]]:
    """Return {label: (instrument_key, tradingsymbol, expiry)} for BANKNIFTY & NIFTY FUT."""
    out: Dict[str, Tuple[str, str, str]] = {}
    for uname, lbl in (("BANKNIFTY", "BANKNIFTY_FUT"), ("NIFTY", "NIFTY_FUT")):
        cands = [
            r for r in master_rows
            if r.get("name") == uname
            and r.get("instrument_type") == "FUTIDX"
            and (r.get("expiry") or "") >= today_s
        ]
        cands.sort(key=lambda r: r["expiry"])
        if cands:
            c0 = cands[0]
            out[lbl] = (c0["instrument_key"], c0.get("tradingsymbol") or lbl, c0["expiry"])
    return out


def resolve_atm_options(
    master_rows: Sequence[Dict[str, str]], today_s: str, fut_ltps: Dict[str, float]
) -> Dict[str, Tuple[str, str, str]]:
    """Resolve nearest ATM CE & PE for BANKNIFTY (monthly) and NIFTY (nearest expiry)."""
    out: Dict[str, Tuple[str, str, str]] = {}
    for uname, flbl, step, monthly in (
        ("BANKNIFTY", "BANKNIFTY_FUT", 100, True),
        ("NIFTY", "NIFTY_FUT", 50, False),
    ):
        px = fut_ltps.get(flbl)
        if not px:
            continue
        atm = int(round(px / float(step)) * step)
        exps = sorted({
            r["expiry"] for r in master_rows
            if r.get("name") == uname and r.get("instrument_type") == "OPTIDX"
            and (r.get("expiry") or "") >= today_s
        })
        if not exps:
            continue
        if monthly:
            in_m = [e for e in exps if e[:7] == today_s[:7]]
            exp = in_m[-1] if in_m else [e for e in exps if e[:7] == exps[0][:7]][-1]
        else:
            exp = exps[0]
        for typ in ("CE", "PE"):
            hit = next(
                (r for r in master_rows
                 if r.get("name") == uname and r.get("expiry") == exp
                 and r.get("instrument_type") == "OPTIDX"
                 and (r.get("tradingsymbol") or "").endswith(typ)
                 and abs(float(r.get("strike") or 0) - float(atm)) < 0.01),
                None,
            )
            if hit:
                out[f"{uname}_{typ}"] = (hit["instrument_key"], hit.get("tradingsymbol") or "", exp)
    return out


def fetch_batch_quotes(
    key_to_label: Dict[str, str],
    token: str,
    tsym_to_label: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Fetch full 5-level depth + volume + OI quotes for all instruments in 1 API call."""
    if not key_to_label:
        return []
    joined = urllib.parse.quote(",".join(key_to_label.keys()), safe=",")
    payload = api_get(f"/v2/market-quote/quotes?instrument_key={joined}", token)
    data = payload.get("data") or {}
    now_iso = datetime.now(IST).isoformat()
    snaps: List[Dict[str, Any]] = []
    for _resp_key, q in data.items():
        if not isinstance(q, dict):
            continue
        ikey = q.get("instrument_token") or q.get("instrument_key") or ""
        lbl = key_to_label.get(ikey)
        if not lbl and tsym_to_label:
            sym = (q.get("symbol") or "").strip()
            lbl = tsym_to_label.get(sym)
        if not lbl:
            continue
        depth = q.get("depth") or {}
        bids = [[float(x.get("price") or 0), float(x.get("quantity") or 0)] for x in (depth.get("buy") or [])[:5]]
        asks = [[float(x.get("price") or 0), float(x.get("quantity") or 0)] for x in (depth.get("sell") or [])[:5]]
        snaps.append({
            "timestamp_ist": now_iso,
            "label": lbl,
            "instrument_key": ikey,
            "ltp": float(q.get("last_price") or 0.0),
            "volume": float(q.get("volume") or 0.0),
            "oi": float(q.get("oi") or 0.0),
            "atp": float(q.get("average_price") or 0.0),
            "tbq": float(q.get("total_buy_quantity") or 0.0),
            "tsq": float(q.get("total_sell_quantity") or 0.0),
            "bids": bids,
            "asks": asks,
        })
    return snaps


# ---------------------------------------------------------------------------
# 5. Terminal Printer & Standalone Live Auto-Refreshing HTML Dashboard
# ---------------------------------------------------------------------------
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Live Order Flow, Volume Profile & Footprint</title>
<style>
  body { background:#0b0f17; color:#e5e7eb; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin:16px; }
  h1 { font-size:18px; margin:0 0 8px; color:#93c5fd; }
  .meta { font-size:12px; color:#9ca3af; margin-bottom:14px; }
  .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(560px, 1fr)); gap:16px; }
  .card { background:#111827; border:1px solid #1f2937; border-radius:8px; padding:14px; }
  .hdr { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1f2937; padding-bottom:8px; margin-bottom:10px; }
  .kpi { display:flex; flex-wrap:wrap; gap:10px; font-size:12px; margin-bottom:10px; }
  .pill { background:#1f2937; padding:4px 8px; border-radius:4px; }
  .pos { color:#34d399; } .neg { color:#f87171; } .warn { color:#fbbf24; }
  .cols { display:grid; grid-template-columns: 1.5fr 1fr; gap:12px; }
  table { width:100%; border-collapse:collapse; font-size:11px; }
  th, td { padding:3px 5px; border-bottom:1px solid #1f2937; text-align:right; }
  th { color:#9ca3af; font-weight:600; }
  .poc { background:#312e81 !important; font-weight:700; }
  .bimb { color:#34d399; font-weight:700; } .simb { color:#f87171; font-weight:700; }
  .bar { height:10px; background:#3b82f6; display:inline-block; border-radius:2px; }
  .bar-va { background:#60a5fa; } .bar-poc { background:#f59e0b; }
  .alert { font-size:11px; padding:4px 6px; margin-top:4px; border-radius:4px; background:#1e293b; }
</style></head>
<body>
<h1>NSE Index Futures — Live Order Flow, Volume Profile & Footprint</h1>
<div class="meta" id="meta">Loading orderflow_state.json...</div>
<div class="grid" id="grid"></div>
<script>
async function refresh() {
  try {
    const r = await fetch('orderflow_state.json?_=' + Date.now());
    const d = await r.json();
    document.getElementById('meta').textContent =
      `Updated: ${d.updated_at} | Mode: ${d.mode} | Paper Analytics Only (Rs 0) | Auto-refresh 2s`;
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    for (const [lbl, st] of Object.entries(d.instruments || {})) {
      const vp = st.session_vp || {};
      const pvp = st.prior_vp || {};
      const bars = (st.footprint_bars || []).slice(-3);
      const lastBar = bars[bars.length - 1];
      const maxVol = Math.max(1, ...(vp.histogram || []).map(x => x.vol));
      const cvdCls = st.cvd >= 0 ? 'pos' : 'neg';
      const obiCls = st.obi_l5 >= 0 ? 'pos' : 'neg';

      let fpHtml = '<div style="font-size:11px;color:#9ca3af">Waiting for live footprint ticks...</div>';
      if (lastBar && lastBar.ladder && lastBar.ladder.length) {
        fpHtml = `<div style="font-size:11px;margin-bottom:4px">Footprint <b>${lastBar.slot}</b> | O:${lastBar.open} H:${lastBar.high} L:${lastBar.low} C:${lastBar.close} | Δ:<span class="${lastBar.delta>=0?'pos':'neg'}">${lastBar.delta>=0?'+':''}${lastBar.delta} (${lastBar.delta_pct}%)</span></div>
        <table><tr><th>Price</th><th>Bid (Sell)</th><th>Ask (Buy)</th><th>Delta</th></tr>` +
        lastBar.ladder.slice(0, 18).map(row => `<tr class="${row.is_poc?'poc':''}">
          <td>${row.price.toFixed(1)}${row.is_poc?' *':''}</td>
          <td class="${row.sell_imb?'simb':''}">${row.bid}</td>
          <td class="${row.buy_imb?'bimb':''}">${row.ask}</td>
          <td class="${row.delta>=0?'pos':'neg'}">${row.delta>=0?'+':''}${row.delta}</td>
        </tr>`).join('') + '</table>';
      }

      let vpHtml = '<table><tr><th>Price</th><th style="text-align:left">Volume Profile</th><th>Vol</th></tr>' +
        (vp.histogram || []).slice(0, 18).map(h => {
          const w = Math.max(2, Math.round((h.vol / maxVol) * 110));
          const isPoc = h.price === vp.poc;
          const cls = isPoc ? 'bar bar-poc' : (h.in_va ? 'bar bar-va' : 'bar');
          return `<tr class="${isPoc?'poc':''}"><td>${h.price.toFixed(1)}</td>
            <td style="text-align:left"><span class="${cls}" style="width:${w}px"></span></td>
            <td>${Math.round(h.vol)}</td></tr>`;
        }).join('') + '</table>';

      const alertsHtml = (st.recent_alerts || []).slice(-4).map(a =>
        `<div class="alert"><span class="warn">[${a.time} ${a.type}]</span> ${a.msg}</div>`
      ).join('');

      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="hdr">
          <div><b>${lbl}</b> <span style="font-size:11px;color:#9ca3af">(${st.instrument_key})</span></div>
          <div style="font-size:15px"><b>${st.ltp ?? '—'}</b> <span style="font-size:11px;color:#9ca3af">VWAP ${st.vwap_atp ?? '—'}</span></div>
        </div>
        <div class="kpi">
          <div class="pill">CVD: <b class="${cvdCls}">${st.cvd>=0?'+':''}${st.cvd}</b></div>
          <div class="pill">OBI-L5: <b class="${obiCls}">${(st.obi_l5*100).toFixed(1)}%</b></div>
          <div class="pill">TBQ/TSQ: <b>${st.tbq_tsq_ratio}</b></div>
          <div class="pill">OI: <b>${st.oi_regime}</b></div>
          <div class="pill">Auction: <b>${st.auction_state}</b></div>
          <div class="pill">Bias: <b class="${st.orderflow_bias_score>0?'pos':(st.orderflow_bias_score<0?'neg':'')}">${st.orderflow_bias_score>=0?'+':''}${st.orderflow_bias_score}/3</b></div>
        </div>
        <div class="kpi">
          <div class="pill">dPOC: <b>${vp.poc ?? '—'}</b> | dVA: <b>${vp.val ?? '—'} – ${vp.vah ?? '—'}</b></div>
          <div class="pill">pPOC: <b>${pvp.poc ?? '—'}</b> | pVA: <b>${pvp.val ?? '—'} – ${pvp.vah ?? '—'}</b></div>
          <div class="pill">Spread: <b>${st.spread}</b> | Ticks: <b>${st.live_ticks}</b></div>
        </div>
        <div class="cols"><div>${fpHtml}</div><div>${vpHtml}</div></div>
        ${alertsHtml}`;
      grid.appendChild(card);
    }
  } catch (e) {
    document.getElementById('meta').textContent = 'Waiting for state file... (' + e + ')';
  }
}
refresh();
setInterval(refresh, 2000);
</script></body></html>
"""


def write_outputs(root: Path, mode: str, trackers: Dict[str, InstrumentOrderFlow]) -> Path:
    live_dir = root / "data" / "orderflow_live"
    live_dir.mkdir(parents=True, exist_ok=True)
    html_p = live_dir / "orderflow_dashboard.html"
    if not html_p.exists():
        html_p.write_text(DASHBOARD_HTML)
    state = {
        "updated_at": datetime.now(IST).isoformat(),
        "mode": mode,
        "paper_only": True,
        "instruments": {lbl: tr.snapshot_state() for lbl, tr in trackers.items()},
    }
    st_p = live_dir / "orderflow_state.json"
    tmp = st_p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=1))
    os.replace(tmp, st_p)
    return st_p


def print_terminal_snapshot(trackers: Dict[str, InstrumentOrderFlow]) -> None:
    print(f"\n================ LIVE ORDER FLOW / VP / FOOTPRINT ({datetime.now(IST).strftime('%H:%M:%S IST')}) ================")
    for lbl, tr in trackers.items():
        st = tr.snapshot_state(max_bars=2)
        vp, pvp = st["session_vp"], st["prior_vp"]
        print(
            f"[{lbl:<14}] LTP={st['ltp']} VWAP={st['vwap_atp']} | CVD={st['cvd']:+} "
            f"OBI5={st['obi_l5']*100:+.1f}% TBQ/TSQ={st['tbq_tsq_ratio']:.2f} "
            f"OI={st['oi_regime']} Bias={st['orderflow_bias_score']:+d}/3"
        )
        print(
            f"  VP: dPOC={vp['poc']} dVA=[{vp['val']}..{vp['vah']}] ({st['auction_state']}) | "
            f"pPOC={pvp['poc']} pVA=[{pvp['val']}..{pvp['vah']}]"
        )
        if st["footprint_bars"]:
            fb = st["footprint_bars"][-1]
            print(
                f"  FP {fb['slot']}: O={fb['open']} H={fb['high']} L={fb['low']} C={fb['close']} "
                f"Vol={fb['volume']} Delta={fb['delta']:+} ({fb['delta_pct']:+.1f}%) "
                f"BuyImb={fb['buy_imbalances'][:3]} SellImb={fb['sell_imbalances'][:3]} "
                f"StackedBuy={fb['stacked_buy']} StackedSell={fb['stacked_sell']}"
            )
            for row in fb["ladder"][:8]:
                tag = " [POC]" if row["is_poc"] else ""
                bi = "*" if row["buy_imb"] else " "
                si = "*" if row["sell_imb"] else " "
                print(f"    {row['price']:>8.1f} | {si}{row['bid']:>6} x {row['ask']:<6}{bi} | Δ {row['delta']:>+6}{tag}")
        for al in st["recent_alerts"][-2:]:
            print(f"  ALERT [{al['time']} {al['type']}]: {al['msg']}")


# ---------------------------------------------------------------------------
# 6. Modes: live, replay, selftest
# ---------------------------------------------------------------------------
def _start_local_dashboard_server(directory: Path, port: int) -> Optional[http.server.ThreadingHTTPServer]:
    if port <= 0:
        return None

    class _QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass

    q_handler = functools.partial(_QuietHandler, directory=str(directory))
    try:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), q_handler)
    except OSError as e:
        print(f"[WARN] Dashboard HTTP server could not bind 127.0.0.1:{port} ({e}); continuing without HTTP server.")
        return None
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def run_live(
    root: Path,
    interval_s: float = 1.5,
    with_options: bool = False,
    max_polls: int = 0,
    serve_port: int = 8765,
) -> int:
    token = load_token(root)
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    master = load_nse_master(root)
    futs = resolve_near_futures(master, today_s)
    if not futs:
        print("ERROR: Could not resolve BANKNIFTY/NIFTY near-month futures from NSE master.")
        return 2

    instruments: Dict[str, Tuple[str, str, str]] = dict(futs)
    key_to_label = {v[0]: lbl for lbl, v in instruments.items()}
    tsym_to_label = {v[1]: lbl for lbl, v in instruments.items()}

    # Optional: fetch initial futures LTP to resolve live ATM CE/PE option keys
    if with_options:
        seed_q = fetch_batch_quotes(key_to_label, token, tsym_to_label)
        fut_ltps = {s["label"]: s["ltp"] for s in seed_q if s["ltp"] > 0}
        opts = resolve_atm_options(master, today_s, fut_ltps)
        instruments.update(opts)
        key_to_label = {v[0]: lbl for lbl, v in instruments.items()}
        tsym_to_label = {v[1]: lbl for lbl, v in instruments.items()}

    trackers: Dict[str, InstrumentOrderFlow] = {}
    for lbl, (ikey, tsym, exp) in instruments.items():
        tr = InstrumentOrderFlow(lbl, ikey, DEFAULT_TICK_BINS.get(lbl, 5.0))
        # Seed prior-day & today's 1-min Volume Profile so VP is ready immediately!
        enc = urllib.parse.quote(ikey, safe="")
        try:
            prev_to = (ddate.fromisoformat(today_s) - timedelta(days=1)).isoformat()
            prev_frm = (ddate.fromisoformat(today_s) - timedelta(days=7)).isoformat()
            hp = api_get(f"/v3/historical-candle/{enc}/minutes/1/{prev_to}/{prev_frm}", token)
            h_rows = (hp.get("data") or {}).get("candles") or []
            if h_rows:
                last_prev_day = max(str(c[0])[:10] for c in h_rows)
                tr.seed_prior_profile([c for c in h_rows if str(c[0])[:10] == last_prev_day])
            time.sleep(0.25)
            ip = api_get(f"/v3/historical-candle/intraday/{enc}/minutes/1", token)
            i_rows = [c for c in ((ip.get("data") or {}).get("candles") or []) if str(c[0])[:10] == today_s]
            if i_rows:
                tr.seed_intraday_profile(i_rows)
            time.sleep(0.25)
        except RateLimited:
            raise
        except Exception as e:
            print(f"[WARN] Profile backfill skipped for {lbl}: {e}")
        trackers[lbl] = tr
        print(f"[INIT] {lbl:<14} -> {tsym} ({ikey}, exp {exp}, bin={tr.tick_bin})")

    snap_dir = root / "data" / "orderflow_snapshots" / today_s
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap_file = snap_dir / "snapshots.jsonl"
    st_p = write_outputs(root, "LIVE", trackers)
    srv = _start_local_dashboard_server(st_p.parent, serve_port)
    print(f"\nLive archive   : {snap_file}")
    if srv:
        print(f"Live dashboard : http://127.0.0.1:{serve_port}/orderflow_dashboard.html")
    else:
        print(f"Live dashboard : {st_p.parent / 'orderflow_dashboard.html'}")
    print(f"Strategy JSON  : {st_p}\n")

    polls = 0
    with open(snap_file, "a", encoding="utf-8") as fh:
        while True:
            t0 = time.monotonic()
            snaps = fetch_batch_quotes(key_to_label, token, tsym_to_label)
            for s in snaps:
                fh.write(json.dumps(s) + "\n")
                trackers[s["label"]].ingest_snapshot(s)
            fh.flush()
            write_outputs(root, "LIVE", trackers)
            polls += 1
            if polls == 1 or polls % 5 == 0:
                print_terminal_snapshot(trackers)
            if max_polls > 0 and polls >= max_polls:
                break
            now_t = datetime.now(IST).time()
            if now_t >= dtime(15, 32):
                print("Market closed (>= 15:32 IST) — stopping cleanly.")
                break
            elapsed = time.monotonic() - t0
            if elapsed < interval_s:
                time.sleep(interval_s - elapsed)
    return 0


def run_replay(root: Path, jsonl_path: Path) -> int:
    if not jsonl_path.exists():
        print(f"Replay file not found: {jsonl_path}")
        return 2
    trackers: Dict[str, InstrumentOrderFlow] = {}
    cnt = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            s = json.loads(line)
            lbl = s["label"]
            if lbl not in trackers:
                trackers[lbl] = InstrumentOrderFlow(
                    lbl, s.get("instrument_key", lbl), DEFAULT_TICK_BINS.get(lbl, 5.0)
                )
            trackers[lbl].ingest_snapshot(s)
            cnt += 1
    write_outputs(root, f"REPLAY:{jsonl_path.name}", trackers)
    print(f"Replayed {cnt} snapshots across {len(trackers)} instruments.")
    print_terminal_snapshot(trackers)
    return 0


def run_selftest() -> int:
    print("=== ORDER FLOW, VOLUME PROFILE & FOOTPRINT SELF-TEST ===")
    tr = InstrumentOrderFlow("BANKNIFTY_FUT", "NSE_FO|TEST", tick_bin=10.0)
    # 1. Seed prior-day profile & verify 70% Value Area
    prior_1m = [
        ["2026-11-25T09:15:00+05:30", 61000, 61030, 60990, 61010, 5000, 100000],
        ["2026-11-25T09:16:00+05:30", 61010, 61020, 61000, 61010, 15000, 100500],
        ["2026-11-25T09:17:00+05:30", 61010, 61060, 61010, 61050, 4000, 101000],
    ]
    tr.seed_prior_profile(prior_1m)
    pvp = tr.prior_vp.summary()
    assert pvp["poc"] == 61010.0 and pvp["val"] <= pvp["poc"] <= pvp["vah"], pvp
    print(f"  OK  Volume Profile 70% VA: pPOC={pvp['poc']} pVA=[{pvp['val']}..{pvp['vah']}]")

    # 2. Stream synthetic live snapshots with aggressive buyer sweeps across 3 stacked levels
    snaps = [
        # Initial seed tick (vol=1000)
        {"timestamp_ist": "2026-11-26T09:30:01+05:30", "label": "BANKNIFTY_FUT", "instrument_key": "NSE_FO|TEST",
         "ltp": 61100.0, "volume": 1000, "oi": 200000, "atp": 61095.0, "tbq": 12000, "tsq": 8000,
         "bids": [[61098.0, 500], [61090.0, 400]], "asks": [[61100.0, 300], [61110.0, 250]]},
        # Small sell at bid 61090 (+50 bid vol)
        {"timestamp_ist": "2026-11-26T09:30:05+05:30", "label": "BANKNIFTY_FUT", "instrument_key": "NSE_FO|TEST",
         "ltp": 61090.0, "volume": 1050, "oi": 200020, "atp": 61095.0, "tbq": 12000, "tsq": 8000,
         "bids": [[61090.0, 500], [61080.0, 400]], "asks": [[61100.0, 300], [61110.0, 250]]},
        # Aggressive buy lifting ask at 61100 (+300 ask vol -> 6:1 buy imbalance vs 50 bid at 61090!)
        {"timestamp_ist": "2026-11-26T09:30:10+05:30", "label": "BANKNIFTY_FUT", "instrument_key": "NSE_FO|TEST",
         "ltp": 61100.0, "volume": 1350, "oi": 200250, "atp": 61097.0, "tbq": 14000, "tsq": 7000,
         "bids": [[61098.0, 600], [61090.0, 400]], "asks": [[61110.0, 250], [61120.0, 200]]},
        # Aggressive buy lifting ask at 61110 (+350 ask vol -> stacked buy #2!)
        {"timestamp_ist": "2026-11-26T09:30:15+05:30", "label": "BANKNIFTY_FUT", "instrument_key": "NSE_FO|TEST",
         "ltp": 61110.0, "volume": 1700, "oi": 200500, "atp": 61100.0, "tbq": 16000, "tsq": 6000,
         "bids": [[61108.0, 700], [61100.0, 500]], "asks": [[61120.0, 200], [61130.0, 200]]},
        # Aggressive buy lifting ask at 61120 (+400 ask vol -> stacked buy #3!)
        {"timestamp_ist": "2026-11-26T09:30:20+05:30", "label": "BANKNIFTY_FUT", "instrument_key": "NSE_FO|TEST",
         "ltp": 61120.0, "volume": 2100, "oi": 200900, "atp": 61105.0, "tbq": 18000, "tsq": 5500,
         "bids": [[61118.0, 800], [61110.0, 600]], "asks": [[61130.0, 150], [61140.0, 150]]},
    ]
    for s in snaps:
        tr.ingest_snapshot(s)

    st = tr.snapshot_state()
    fb = st["footprint_bars"][-1]
    assert st["cvd"] == 1000, f"Expected CVD +1000 (1050 ask - 50 bid), got {st['cvd']}"
    assert st["oi_regime"] == "LONG_BUILDUP", st["oi_regime"]
    assert st["obi_l5"] > 0.50 and st["orderflow_bias_score"] == 3, st
    assert len(fb["stacked_buy"]) == 1 and fb["stacked_buy"][0] == [61100.0, 61110.0, 61120.0], fb

    # 3. Verify JSONL replay + HTML dashboard + JSON bridge generation in temp dir
    with tempfile.TemporaryDirectory() as td:
        troot = Path(td)
        jf = troot / "test.jsonl"
        jf.write_text("\n".join(json.dumps(s) for s in snaps) + "\n")
        assert run_replay(troot, jf) == 0
        assert (troot / "data" / "orderflow_live" / "orderflow_dashboard.html").exists()
        assert (troot / "data" / "orderflow_live" / "orderflow_state.json").exists()

    print(f"  OK  Lee-Ready CVD=+1000, OI={st['oi_regime']}, OBI-L5={st['obi_l5']*100:+.1f}%, Bias=+3/3")
    print(f"  OK  Footprint 3:1 Stacked Buy Imbalance detected: {fb['stacked_buy']}")
    print("  OK  JSONL archive replay, HTML dashboard, and strategy bridge verified")
    print("ORDER FLOW / VP / FOOTPRINT SELF-TEST PASSED!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "live", "replay"), default="live")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--interval", type=float, default=1.5, help="Live poll interval in seconds (>= 1.0)")
    ap.add_argument("--with-options", action="store_true", help="Also track ATM CE/PE option tape")
    ap.add_argument("--serve-port", type=int, default=8765, help="Localhost port for HTML dashboard (0 = disable)")
    ap.add_argument("--max-polls", type=int, default=0, help="Stop after N polls (0 = run until 15:32 IST)")
    ap.add_argument("--file", dest="replay_file", help="JSONL snapshot file for --mode replay")
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
            root,
            interval_s=max(a.interval, 1.0),
            with_options=a.with_options,
            max_polls=a.max_polls,
            serve_port=a.serve_port,
        )
    except RateLimited as e:
        print(f"RATE_LIMITED HARD STOP: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
