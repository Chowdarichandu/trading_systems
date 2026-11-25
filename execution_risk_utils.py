#!/usr/bin/env python3
"""EXECUTION, COST, SIZING & ACCURACY UTILITIES (added 2026-11-25).

Self-contained, zero-dependency helpers designed to close the largest
accounting, execution-realism, and entry-quality gaps found in the
2026-11-25 audit of trading_systems-main:

  1. Realistic NSE transaction costs + slippage (intraday cash, delivery
     swing, and index option buying — replacing flat Rs40 / Rs220 models).
  2. Fixed-capital equity position sizing (replacing flat 100-share sizing,
     which created 32x capital imbalances between Rs80 and Rs2,600 stocks).
  3. Gap-aware, physical-floor option replay (preventing negative stop
     prices like -11.20 and idealized fills through opening gaps).
  4. Volatility- & structure-aware accuracy filters:
       - Signal-candle exhaustion check (skip/retrace over-extended bars)
       - Bank Nifty heavyweight constituent breadth confirmation
       - Percentage/ATR-scaled option stop sizing

Paper/research utility only — places no orders, makes no API calls.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. Realistic NSE Transaction Costs & Slippage (Upstox discount-broker rates)
# ---------------------------------------------------------------------------
def equity_intraday_cost(
    entry_price: float,
    exit_price: float,
    qty: int,
    side: int = 1,
    slippage_bps_per_side: float = 5.0,
    brokerage_per_order: float = 20.0,
) -> Dict[str, float]:
    """Realistic round-trip cost for NSE equity intraday cash trades.

    Includes:
      - Brokerage: min(brokerage_per_order, 0.05% of leg value) per leg
      - STT: 0.025% on sell-side turnover
      - NSE transaction + IPFT: ~0.00307% on total turnover
      - SEBI turnover fee: 0.0001% on total turnover
      - Stamp duty: 0.003% on buy-side turnover
      - GST: 18% on (brokerage + exchange txn + SEBI)
      - Market-order / bid-ask slippage: `slippage_bps_per_side` per leg
    """
    buy_px, sell_px = (entry_price, exit_price) if side == 1 else (exit_price, entry_price)
    buy_val = buy_px * qty
    sell_val = sell_px * qty
    turnover = buy_val + sell_val

    brok = min(brokerage_per_order, 0.0005 * buy_val) + min(brokerage_per_order, 0.0005 * sell_val)
    stt = 0.00025 * sell_val
    exch = 0.0000307 * turnover
    sebi = 0.000001 * turnover
    stamp = 0.00003 * buy_val
    gst = 0.18 * (brok + exch + sebi)
    statutory = brok + stt + exch + sebi + stamp + gst
    slippage = turnover * (slippage_bps_per_side / 10000.0)
    return {
        "statutory_inr": round(statutory, 2),
        "slippage_inr": round(slippage, 2),
        "total_cost_inr": round(statutory + slippage, 2),
    }


def equity_delivery_cost(
    entry_price: float,
    exit_price: float,
    qty: int,
    slippage_bps_per_side: float = 5.0,
    brokerage_per_order: float = 20.0,
    dp_charge_inr: float = 18.50,
) -> Dict[str, float]:
    """Realistic round-trip cost for NSE equity delivery swing trades (LONG).

    Delivery STT is 0.10% on BOTH buy and sell sides (0.20% round-trip),
    plus 0.015% buy-side stamp duty and CDSL/NSDL DP sell charge.
    """
    buy_val = entry_price * qty
    sell_val = exit_price * qty
    turnover = buy_val + sell_val

    brok = min(brokerage_per_order, 0.001 * buy_val) + min(brokerage_per_order, 0.001 * sell_val)
    stt = 0.001 * turnover
    exch = 0.0000307 * turnover
    sebi = 0.000001 * turnover
    stamp = 0.00015 * buy_val
    gst = 0.18 * (brok + exch + sebi + dp_charge_inr)
    statutory = brok + stt + exch + sebi + stamp + dp_charge_inr + gst
    slippage = turnover * (slippage_bps_per_side / 10000.0)
    return {
        "statutory_inr": round(statutory, 2),
        "slippage_inr": round(slippage, 2),
        "total_cost_inr": round(statutory + slippage, 2),
    }


def index_option_cost(
    entry_premium: float,
    exit_premium: float,
    lot_size: int,
    lots: int = 1,
    slippage_pts_per_side: float = 2.0,
    brokerage_per_order: float = 20.0,
    stt_sell_rate: float = 0.001,
) -> Dict[str, float]:
    """Realistic round-trip cost for NSE index option buying (1+ lots).

    Note: `stt_sell_rate` defaults to 0.10% (post-Oct 2024 NSE option sell STT);
    pass 0.0015 if modelling the 0.15% STT slab.
    """
    qty = lot_size * lots
    buy_val = entry_premium * qty
    sell_val = exit_premium * qty
    turnover = buy_val + sell_val

    brok = 2.0 * brokerage_per_order
    stt = stt_sell_rate * sell_val
    exch = 0.0003503 * turnover  # NSE options txn + IPFT (~0.035%)
    sebi = 0.000001 * turnover
    stamp = 0.00003 * buy_val
    gst = 0.18 * (brok + exch + sebi)
    statutory = brok + stt + exch + sebi + stamp + gst
    slippage = 2.0 * slippage_pts_per_side * qty
    return {
        "statutory_inr": round(statutory, 2),
        "slippage_inr": round(slippage, 2),
        "total_cost_inr": round(statutory + slippage, 2),
    }


# ---------------------------------------------------------------------------
# 2. Fixed-Capital Equity Position Sizing
# ---------------------------------------------------------------------------
def fixed_capital_qty(
    entry_price: float,
    capital_per_trade_inr: float = 100_000.0,
    min_qty: int = 1,
) -> int:
    """Return integer share count deploying ~`capital_per_trade_inr`.

    Prevents high-priced tickers (e.g. GLENMARK Rs2,600, APARINDS Rs12,000)
    from dominating backtest rupees over low-priced names (NHPC Rs80).
    """
    if entry_price <= 0:
        return 0
    qty = int(math.floor(capital_per_trade_inr / entry_price))
    return max(qty, min_qty) if qty > 0 else 0


# ---------------------------------------------------------------------------
# 3. Volatility-Normalized Option Stops & Gap-Aware Replay
# ---------------------------------------------------------------------------
def normalized_option_levels(
    entry_premium: float,
    stop_pct: float = 0.15,
    target_pct: float = 0.30,
    min_premium_inr: float = 80.0,
    tick_floor: float = 0.05,
) -> Optional[Tuple[float, float]]:
    """Compute percentage-scaled (stop, target) option levels with a physical floor.

    Returns None if `entry_premium < min_premium_inr` (filtering out low-premium
    expiry lottery tickets where fixed point stops break down).
    """
    if entry_premium < min_premium_inr:
        return None
    stop_px = max(round(entry_premium * (1.0 - stop_pct), 2), tick_floor)
    target_px = round(entry_premium * (1.0 + target_pct), 2)
    return stop_px, target_px


def replay_option_realistic(
    bars: Sequence[Tuple[str, float, float, float, float]],
    entry_time: str,
    lot_size: int,
    stop_px: float,
    target_px: float,
    sq_time: str = "15:10",
    be_arm_pts: Optional[float] = None,
    runner_lock_pts: Optional[float] = None,
    runner_target2_pts: Optional[float] = None,
    slippage_pts_per_side: float = 2.0,
) -> Optional[Dict[str, object]]:
    """Gap-aware option replay with physical stop floor and realistic NSE costs.

    `bars`: sequence of (HH:MM, open, high, low, close).
    - Checks gap-through open fills (`o <= active_stop`) BEFORE intra-bar low.
    - Never allows a stop price below Rs 0.05.
    """
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return None
    entry = float(bs[0][1])
    cur_stop = max(float(stop_px), 0.05)

    def _finish(px: float, reason: str, t: str, ft: int) -> Dict[str, object]:
        px = max(float(px), 0.05)
        costs = index_option_cost(
            entry, px, lot_size=lot_size, slippage_pts_per_side=slippage_pts_per_side
        )
        gross = (px - entry) * lot_size
        return {
            "entry": entry,
            "exit": px,
            "exit_time": t,
            "exit_reason": reason,
            "ft": ft,
            "gross_inr": round(gross, 2),
            "cost_inr": costs["total_cost_inr"],
            "net_inr": round(gross - costs["total_cost_inr"], 2),
        }

    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > sq_time:
            break
        if o <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "gap_stop"
            return _finish(o, rsn, t, 0)
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return _finish(cur_stop, rsn, t, 0)
        if h >= target_px:
            if runner_lock_pts is None or runner_target2_pts is None:
                return _finish(target_px, "target", t, 1)
            stop2 = max(entry + runner_lock_pts, 0.05)
            target2 = entry + runner_target2_pts
            for t2, o2, h2, l2, cl2 in bs[i + 1 :]:
                if t2 > sq_time:
                    break
                if o2 <= stop2:
                    return _finish(o2, "runner_gap_stop", t2, 1)
                if l2 <= stop2:
                    return _finish(stop2, "runner_stop", t2, 1)
                if h2 >= target2:
                    return _finish(target2, "runner_target", t2, 1)
                if t2 == sq_time:
                    return _finish(cl2, "runner_square_off", t2, 1)
            lb = bs[-1]
            return _finish(lb[4], "runner_square_off", lb[0], 1)
        if be_arm_pts is not None and (h - entry) >= be_arm_pts:
            cur_stop = max(cur_stop, entry)
        if t == sq_time:
            return _finish(cl, "square_off", t, 0)
    lb = bs[-1]
    return _finish(lb[4], "square_off", lb[0], 0)


# ---------------------------------------------------------------------------
# 4. Accuracy Filters: Exhaustion & Bank Nifty Constituent Breadth
# ---------------------------------------------------------------------------
def is_signal_bar_exhausted(
    bar_high: float,
    bar_low: float,
    atr_5m: float,
    max_atr_multiple: float = 1.8,
) -> bool:
    """True when a breakout signal candle already consumed > `max_atr_multiple`
    of 5-min ATR (primary cause of entry-bar option stop-outs)."""
    if atr_5m <= 0:
        return False
    return (bar_high - bar_low) > (max_atr_multiple * atr_5m)


# Approximate top Bank Nifty weights (~75% of index combined)
BANKNIFTY_TOP5_WEIGHTS: Dict[str, float] = {
    "HDFCBANK": 0.28,
    "ICICIBANK": 0.24,
    "SBIN": 0.11,
    "KOTAKBANK": 0.09,
    "AXISBANK": 0.09,
}


def banknifty_breadth_aligned(
    constituent_signals: Dict[str, int],
    direction: str,
    min_weight_share: float = 0.60,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[bool, float]:
    """Check whether heavyweight Bank Nifty constituents agree with `direction`.

    `constituent_signals`: {symbol: +1 (bullish vs VWAP/OR), -1 (bearish), 0}.
    `direction`: "CE" (+1) or "PE" (-1).
    Returns (is_aligned, aligned_weight_fraction).
    """
    wmap = weights or BANKNIFTY_TOP5_WEIGHTS
    want = 1 if direction.upper() == "CE" else -1
    avail_w = sum(w for sym, w in wmap.items() if sym in constituent_signals)
    if avail_w <= 0:
        return False, 0.0
    aligned_w = sum(
        w for sym, w in wmap.items() if constituent_signals.get(sym) == want
    )
    frac = aligned_w / avail_w
    return frac >= min_weight_share, round(frac, 4)


if __name__ == "__main__":
    print("Self-check execution_risk_utils:")
    print("  GLENMARK 100sh intraday @2500:", equity_intraday_cost(2500, 2525, 100))
    print("  Fixed-cap Rs1L qty @2500:", fixed_capital_qty(2500, 100_000))
    print("  Bank Nifty 1-lot option @750->840:", index_option_cost(750, 840, 30))
    print("  Expiry opt @38.80 norm levels:", normalized_option_levels(38.80))
    print("  Breadth test (3/5 bull CE):",
          banknifty_breadth_aligned(
              {"HDFCBANK": 1, "ICICIBANK": 1, "SBIN": 1, "KOTAKBANK": -1, "AXISBANK": 0},
              "CE",
          ))
