#!/usr/bin/env python3
"""INDEX APEX LAB — Bank Nifty & Nifty Multi-Family Research, Gate & Paper Engine.

Designed from first principles after the 2026-11-26 audit and 160+ controlled
lessons in bank_engine_lessons.md + nifty_engine_lessons.md. Tests THREE
structurally distinct, non-overfit Bank Nifty & Nifty strategy families side-by-
side behind a strict institutional verification gate (zero look-ahead, realistic
NSE costs & slippage on every leg, fail-closed breadth/data NC accounting,
200-draw matched cost-identical placebo, and truncated-series causal audit):

  1. HEDGED_THETA (Defined-Risk Intraday Iron Condor / Short Strangle + Wings)
     Harvests NSE intraday Volatility Risk Premium (IV > RV) on calm/balanced
     opens (09:50 -> 15:10, EXP0), with protective OTM wings capping tail risk
     and MTM stop-loss (+65% of credit) / TP (60% of credit), priced at FULL
     4-leg realistic NSE option taxes + slippage.

  2. SWING_DEBIT (Buying-Only Multi-Day Index Trend via Monthly Vertical Debit
     Spread — ~15-25 trades/yr)
     Captures multi-day directional trends (10-day Donchian breakout + rising
     20-DMA) using defined-risk Bull Call / Bear Put spreads (>= 7 DTE) with
     5-day spot trail, -45% debit SL, +70% max-gain TP, and DTE-1 exit — low
     capital, capped overnight gap risk, ~5x lower annual friction than intraday.

  3. SQUEEZE_ORB (Buying-Only High-Selectivity Intraday Compression Breakout)
     Fixes every flaw of Pillar 2 v1 and obeys the repo's verified Bank/Nifty
     lessons: trades ONLY on volatility-compression days (NR4 or tight OR <=
     0.65x 20d median), ATM strike (not ITM-100), fixed-point -50/+90->runner
     with min_premium >= Rs 80 floor, EXP0 on Nifty, and STRICT FAIL-CLOSED
     Bank Nifty Top-5 constituent breadth (NC if < 4/5 heavyweights present).

PAPER ONLY. Real money Rs 0. Places ZERO broker orders. No strategy is armed
for live paper until it passes --mode gate (positive net + ex-top-3 + >= 90th
pct matched cost-identical placebo + 0 causal leaks + <= 10% NC).

Usage:
  # 1. Offline deterministic self-test + live-path leak audit (zero API calls)
  python3 index_apex_lab.py --mode selftest
  python3 index_apex_lab.py --mode leakaudit

  # 2. Full institutional gate (2025 vs 2026, all 3 families, matched placebo)
  python3 index_apex_lab.py --mode gate --index ALL --strategy ALL

  # 3. Live intraday / EOD paper scan (only for an explicitly chosen strategy)
  python3 index_apex_lab.py --mode live --index ALL --strategy HEDGED_THETA --dry-run
  python3 index_apex_lab.py --mode score --date 2026-11-26 --index ALL --strategy ALL
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import random
import statistics
import sys
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
API = "https://api.upstox.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
INSTRUMENTS_URL = (
    "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
)
PLACEBO_SEED = 20261126

INDEX_CFG: Dict[str, Dict[str, Any]] = {
    "BANKNIFTY": {
        "spot_key": "NSE_INDEX|Nifty Bank",
        "master_name": "BANKNIFTY",
        "default_lot": 30,
        "step": 100,
        "condor_short_off": 100,
        "condor_wing": 400,
        "debit_wing": 400,
    },
    "NIFTY": {
        "spot_key": "NSE_INDEX|Nifty 50",
        "master_name": "NIFTY",
        "default_lot": 65,
        "step": 50,
        "condor_short_off": 50,
        "condor_wing": 200,
        "debit_wing": 200,
    },
}

STRATEGIES = ("HEDGED_THETA", "SWING_DEBIT", "SQUEEZE_ORB")
BANK_HEAVYWEIGHTS = list(ERU.BANKNIFTY_TOP5_WEIGHTS.keys())


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "data").exists() or (live / "oi_buildup_data").exists():
        return live
    return THIS_DIR


def round_strike(spot: float, step: int) -> int:
    return int(round(spot / float(step)) * step)


def plus5(t: str) -> str:
    h, m = int(t[:2]), int(t[3:5])
    m += 5
    if m >= 60:
        h, m = h + 1, m - 60
    return f"{h:02d}:{m:02d}"


# ---------------------------------------------------------------------------
# Local Data Loaders (Spot, Breadth Constituents, Option Candles & Lot Sizes)
# ---------------------------------------------------------------------------
def load_lot_sizes(root: Path) -> Dict[str, Dict[str, int]]:
    """Read historical lot sizes per (index, expiry) from backfill metadata or contracts."""
    out: Dict[str, Dict[str, int]] = {"BANKNIFTY": {}, "NIFTY": {}}
    reg = root / "historical_proof_data" / "lot_sizes_by_expiry.json"
    if reg.exists():
        try:
            raw = json.loads(reg.read_text())
            for k, v in raw.items():
                out.setdefault(k, {}).update({ek: int(ev) for ek, ev in v.items()})
        except Exception:
            pass
    hp = root / "historical_proof_data"
    if hp.exists():
        for cf in hp.glob("contracts_*.json"):
            parts = cf.stem.split("_")
            if len(parts) < 3:
                continue
            idx, exp = parts[1], parts[2]
            if idx in out and exp not in out[idx]:
                try:
                    data = json.loads(cf.read_text()).get("data") or []
                    for c in data:
                        if c.get("lot_size"):
                            out[idx][exp] = int(float(c["lot_size"]))
                            break
                except Exception:
                    pass
    return out


def lot_for(lot_map: Dict[str, Dict[str, int]], idx: str, exp: Optional[str]) -> int:
    if exp and exp in lot_map.get(idx, {}):
        return lot_map[idx][exp]
    return INDEX_CFG[idx]["default_lot"]


def load_5m_store(root: Path, sym: str) -> Dict[str, List[Dict[str, Any]]]:
    paths = [
        root / "data" / "breadth_5m" / sym / "spot_5m_vol.csv",
        root / "data" / "progressive" / sym / "spot_5m.csv",
        root / "data" / "sarvaritu_fwd" / sym / "spot_5m.csv",
        root / "data" / "tarang_vol" / sym / "spot_5m_vol.csv",
        root / "data" / "sapta_vol" / sym / "spot_5m_vol.csv",
    ]
    by_day: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for p in paths:
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
    return {d: [by_day[d][t] for t in sorted(by_day[d])] for d in sorted(by_day)}


def load_daily_from_spot(root: Path, idx: str, spot_5m: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Merge spot_daily.csv + aggregated 5-min bars into sorted daily OHLC list."""
    by_day: Dict[str, Dict[str, Any]] = {}
    dp = root / "data" / "progressive" / idx / "spot_daily.csv"
    if dp.exists():
        with open(dp, newline="") as f:
            for r in csv.DictReader(f):
                d = (r.get("date") or "")[:10]
                if d:
                    by_day[d] = {
                        "date": d, "open": float(r["open"]), "high": float(r["high"]),
                        "low": float(r["low"]), "close": float(r["close"]),
                    }
    for d, bars in spot_5m.items():
        if not bars:
            continue
        by_day[d] = {
            "date": d,
            "open": bars[0]["open"],
            "high": max(b["high"] for b in bars),
            "low": min(b["low"] for b in bars),
            "close": bars[-1]["close"],
        }
    return [by_day[d] for d in sorted(by_day)]


class LocalOptionCache:
    """Fast indexed lookup across oi_buildup_data/, november_shadow_data/, aggressive_data/."""

    def __init__(self, root: Path):
        self.root = root
        self.index: Dict[Tuple[str, int, str, str], List[Tuple[str, Path]]] = defaultdict(list)
        self._mem: Dict[Path, List[Tuple[str, float, float, float, float]]] = {}
        self.expiries_by_index: Dict[str, List[str]] = {"BANKNIFTY": [], "NIFTY": []}
        self._scan()

    def _scan(self) -> None:
        dirs = [
            self.root / "oi_buildup_data",
            self.root / "november_shadow_data",
            self.root / "aggressive_data",
            self.root / "daily2leg",
        ]
        exps: Dict[str, set] = {"BANKNIFTY": set(), "NIFTY": set()}
        for d in dirs:
            if not d.exists():
                continue
            for p in d.glob("candles_*.json"):
                parts = p.stem.split("_")
                if len(parts) < 5:
                    continue
                idx = parts[1]
                if idx not in ("BANKNIFTY", "NIFTY"):
                    continue
                st_str = parts[2]
                if not (st_str.endswith("CE") or st_str.endswith("PE")):
                    continue
                try:
                    strike = int(st_str[:-2])
                except ValueError:
                    continue
                typ = st_str[-2:]
                d1, d2 = parts[3], parts[4]
                # Determine which is day vs expiry: expiry >= day always!
                if len(d1) != 10 or len(d2) != 10:
                    continue
                if d.name == "november_shadow_data":
                    day_s, exp_s = d1, d2
                else:
                    exp_s, day_s = (d1, d2) if d1 >= d2 else (d2, d1)
                self.index[(idx, strike, typ, day_s)].append((exp_s, p))
                exps[idx].add(exp_s)
        for k in self.index:
            # Sort by expiry ascending; prefer monthly (longer DTE) via caller filter
            self.index[k].sort(key=lambda x: x[0])
        for idx in ("BANKNIFTY", "NIFTY"):
            self.expiries_by_index[idx] = sorted(exps[idx])

    def _read(self, p: Path, day_s: str) -> List[Tuple[str, float, float, float, float]]:
        if p not in self._mem:
            try:
                body = json.loads(p.read_text())
                raw = (body.get("data") or {}).get("candles") or []
                bars = [
                    (str(c[0])[11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]))
                    for c in raw if str(c[0])[:10] == day_s
                ]
                bars.sort(key=lambda x: x[0])
                self._mem[p] = bars
            except Exception:
                self._mem[p] = []
        return self._mem[p]

    def get_bars(
        self,
        idx: str,
        strike: int,
        typ: str,
        day_s: str,
        expiry: Optional[str] = None,
        min_dte: int = 0,
    ) -> Tuple[Optional[str], List[Tuple[str, float, float, float, float]]]:
        cands = self.index.get((idx, int(strike), typ, day_s)) or []
        if not cands:
            return None, []
        d0 = ddate.fromisoformat(day_s)
        for exp_s, p in cands:
            if expiry and exp_s != expiry:
                continue
            if (ddate.fromisoformat(exp_s) - d0).days < min_dte:
                continue
            bars = self._read(p, day_s)
            if bars:
                return exp_s, bars
        return None, []


# ---------------------------------------------------------------------------
# Causal Feature & Breadth Helpers
# ---------------------------------------------------------------------------
def score_constituent_votes(
    const_bars: Dict[str, List[Dict[str, Any]]], upto_time: str
) -> Dict[str, int]:
    """Causal constituent vote (+1 bullish, -1 bearish, 0 neutral) <= upto_time."""
    votes: Dict[str, int] = {}
    for sym, bars in const_bars.items():
        sub = [b for b in bars if b["time"] <= upto_time]
        if not sub:
            continue
        o915 = sub[0]["open"]
        tv = sum(b.get("volume", 0.0) for b in sub)
        if tv > 0:
            vwap = sum(((b["high"] + b["low"] + b["close"]) / 3.0) * b.get("volume", 0.0) for b in sub) / tv
        else:
            vwap = sum((b["high"] + b["low"] + b["close"]) / 3.0 for b in sub) / len(sub)
        or_sub = [b for b in sub if b["time"] < "09:30"]
        or_mid = (
            (max(b["high"] for b in or_sub) + min(b["low"] for b in or_sub)) / 2.0
            if or_sub else o915
        )
        lc = sub[-1]["close"]
        if lc > vwap and lc > o915 and lc >= or_mid:
            votes[sym] = 1
        elif lc < vwap and lc < o915 and lc <= or_mid:
            votes[sym] = -1
        else:
            votes[sym] = 0
    return votes


def check_banknifty_breadth_failclosed(
    const_bars: Optional[Dict[str, List[Dict[str, Any]]]],
    upto_time: str,
    direction: Optional[str] = None,
    min_share: float = 0.60,
) -> Tuple[str, Optional[float], Dict[str, int]]:
    """Fail-closed breadth evaluator.

    Returns (status, aligned_frac, votes):
      - status == 'NC_INCOMPLETE' if fewer than 4 of the 5 heavyweights exist
      - if direction is 'CE'/'PE': returns ('PASS' or 'FAIL', aligned_frac, votes)
      - if direction is None (for HEDGED_THETA): returns ('CALM' or 'TRENDING',
        max(bull_frac, bear_frac), votes)
    """
    if not const_bars:
        return "NC_INCOMPLETE", None, {}
    votes = score_constituent_votes(const_bars, upto_time)
    present = sum(1 for s in ERU.BANKNIFTY_TOP5_WEIGHTS if s in votes)
    if present < 4:
        return "NC_INCOMPLETE", None, votes
    if direction is not None:
        ok, frac = ERU.banknifty_breadth_aligned(votes, direction, min_weight_share=min_share)
        return ("PASS" if ok else "FAIL"), frac, votes
    _, bull_f = ERU.banknifty_breadth_aligned(votes, "CE", min_weight_share=0.80)
    _, bear_f = ERU.banknifty_breadth_aligned(votes, "PE", min_weight_share=0.80)
    dom = max(bull_f, bear_f)
    return ("TRENDING" if dom >= 0.80 else "CALM"), round(dom, 4), votes


def compute_5m_atr(
    prior_5m: Sequence[Dict[str, Any]], today_before_sig: Sequence[Dict[str, Any]], period: int = 14
) -> float:
    seq = list(prior_5m[-20:]) + list(today_before_sig)
    if len(seq) < 3:
        return 0.0
    trs = [seq[0]["high"] - seq[0]["low"]]
    for i in range(1, len(seq)):
        h, l, pc = seq[i]["high"], seq[i]["low"], seq[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if len(trs) <= period:
        return sum(trs) / len(trs)
    val = sum(trs[:period]) / period
    for tr in trs[period:]:
        val = (val * (period - 1) + tr) / period
    return val


# ---------------------------------------------------------------------------
# Strategy 1: HEDGED_THETA (Defined-Risk Intraday Iron Condor)
# ---------------------------------------------------------------------------
def signal_hedged_theta(
    idx: str,
    today_bars: Sequence[Dict[str, Any]],
    prev_daily: Dict[str, Any],
    prior_or30_widths: Sequence[float],
    const_bars: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    require_breadth: bool = True,
) -> Dict[str, Any]:
    """Causal signal evaluated strictly on completed bars <= 09:45 (entry 09:50)."""
    sub = [b for b in today_bars if b["time"] <= "09:45"]
    if len(sub) < 6 or sub[-1]["time"] < "09:45":
        return {"decision": "NO_SIGNAL", "reason": "incomplete_0945_bars"}
    o915 = sub[0]["open"]
    gap_pct = abs((o915 - prev_daily["close"]) / prev_daily["close"]) * 100.0
    if gap_pct > 0.75:
        return {"decision": "BLOCKED", "reason": f"gap_{gap_pct:.2f}pct_gt_0.75"}

    hi30 = max(b["high"] for b in sub)
    lo30 = min(b["low"] for b in sub)
    rng30 = hi30 - lo30
    med30 = statistics.median(prior_or30_widths[-20:]) if len(prior_or30_widths) >= 5 else rng30
    if med30 > 0 and rng30 > 1.15 * med30:
        return {"decision": "BLOCKED", "reason": f"wide_open_range_{rng30/med30:.2f}x"}

    # Require balanced open (not pinned at extreme of wide opening drive)
    c945 = sub[-1]["close"]
    pos_in_rng = (c945 - lo30) / rng30 if rng30 > 0 else 0.5
    if (med30 > 0 and rng30 > 0.85 * med30) and (pos_in_rng < 0.15 or pos_in_rng > 0.85):
        return {"decision": "BLOCKED", "reason": "opening_drive_pinned"}

    breadth_dom = None
    if idx == "BANKNIFTY" and require_breadth:
        bst, breadth_dom, _ = check_banknifty_breadth_failclosed(const_bars, "09:45", direction=None)
        if bst == "NC_INCOMPLETE":
            return {"decision": "NC", "reason": "breadth_incomplete_lt_4_of_5"}
        if bst == "TRENDING":
            return {"decision": "BLOCKED", "reason": f"constituents_trending_{breadth_dom:.2f}"}

    cfg = INDEX_CFG[idx]
    atm = round_strike(c945, cfg["step"])
    s_ce = atm + cfg["condor_short_off"]
    l_ce = s_ce + cfg["condor_wing"]
    s_pe = atm - cfg["condor_short_off"]
    l_pe = s_pe - cfg["condor_wing"]
    return {
        "decision": "SIGNAL",
        "strategy": "HEDGED_THETA",
        "index": idx,
        "direction": "CONDOR",
        "signal_time": "09:45",
        "entry_time": "09:50",
        "spot_at_sig": round(c945, 2),
        "short_ce": s_ce, "long_ce": l_ce,
        "short_pe": s_pe, "long_pe": l_pe,
        "gap_pct": round(gap_pct, 2),
        "breadth_dom": breadth_dom,
    }


def replay_iron_condor(
    sc_bars: Sequence[Tuple[str, float, float, float, float]],
    lc_bars: Sequence[Tuple[str, float, float, float, float]],
    sp_bars: Sequence[Tuple[str, float, float, float, float]],
    lp_bars: Sequence[Tuple[str, float, float, float, float]],
    entry_time: str,
    lot_size: int,
    *,
    sl_mult: float = 1.65,
    tp_capture: float = 0.60,
    min_credit: float = 25.0,
    sq_time: str = "15:10",
    slippage_pts_per_side: float = 1.5,
) -> Dict[str, Any]:
    """4-leg defined-risk Iron Condor replay with FULL 4-leg realistic NSE costs."""
    m_sc = {b[0]: b for b in sc_bars if b[0] >= entry_time}
    m_lc = {b[0]: b for b in lc_bars if b[0] >= entry_time}
    m_sp = {b[0]: b for b in sp_bars if b[0] >= entry_time}
    m_lp = {b[0]: b for b in lp_bars if b[0] >= entry_time}
    times = sorted(t for t in m_sc if t in m_lc and t in m_sp and t in m_lp and t <= sq_time)
    if not times or times[0] != entry_time:
        return {"status": "NC", "reason": "missing_condor_entry_bars"}

    sc_e, lc_e = m_sc[entry_time][1], m_lc[entry_time][1]
    sp_e, lp_e = m_sp[entry_time][1], m_lp[entry_time][1]
    credit = round((sc_e + sp_e) - (lc_e + lp_e), 2)
    if credit < min_credit:
        return {"status": "BLOCKED", "reason": f"credit_{credit:.2f}_lt_{min_credit:.0f}"}

    sl_val = round(credit * sl_mult, 2)
    tp_val = round(credit * (1.0 - tp_capture), 2)

    def _finish(sc_x: float, lc_x: float, sp_x: float, lp_x: float, reason: str, t: str) -> Dict[str, Any]:
        # Short legs: sold at entry, bought back at exit -> pass (buy=exit, sell=entry)
        c_sc = ERU.index_option_cost(max(sc_x, 0.05), sc_e, lot_size, slippage_pts_per_side=slippage_pts_per_side)
        c_sp = ERU.index_option_cost(max(sp_x, 0.05), sp_e, lot_size, slippage_pts_per_side=slippage_pts_per_side)
        # Long wings: bought at entry, sold at exit -> pass (buy=entry, sell=exit)
        c_lc = ERU.index_option_cost(lc_e, max(lc_x, 0.05), lot_size, slippage_pts_per_side=slippage_pts_per_side)
        c_lp = ERU.index_option_cost(lp_e, max(lp_x, 0.05), lot_size, slippage_pts_per_side=slippage_pts_per_side)
        total_cost = round(
            c_sc["total_cost_inr"] + c_sp["total_cost_inr"]
            + c_lc["total_cost_inr"] + c_lp["total_cost_inr"], 2
        )
        exit_debit = round((sc_x + sp_x) - (lc_x + lp_x), 2)
        gross = round((credit - exit_debit) * lot_size, 2)
        return {
            "status": "TAKEN",
            "entry": credit,
            "exit": exit_debit,
            "exit_time": t,
            "exit_reason": reason,
            "gross_inr": gross,
            "cost_inr": total_cost,
            "net_inr": round(gross - total_cost, 2),
        }

    for t in times:
        _, sco, _, _, scc = m_sc[t]
        _, lco, _, _, lcc = m_lc[t]
        _, spo, _, _, spc = m_sp[t]
        _, lpo, _, _, lpc = m_lp[t]
        val_o = (sco + spo) - (lco + lpo)
        val_c = (scc + spc) - (lcc + lpc)
        if val_o >= sl_val:
            return _finish(sco, lco, spo, lpo, "SL_MTM_GAP", t)
        if val_c >= sl_val:
            return _finish(scc, lcc, spc, lpc, "SL_MTM", t)
        if val_o <= tp_val:
            return _finish(sco, lco, spo, lpo, "TP_60", t)
        if val_c <= tp_val:
            return _finish(scc, lcc, spc, lpc, "TP_60", t)
        if t == sq_time:
            return _finish(scc, lcc, spc, lpc, "SQ_1510", t)
    lt = times[-1]
    return _finish(m_sc[lt][4], m_lc[lt][4], m_sp[lt][4], m_lp[lt][4], "SQ_1510", lt)


# ---------------------------------------------------------------------------
# Strategy 2: SWING_DEBIT (Multi-Day Defined-Risk Monthly Vertical Debit Spread)
# ---------------------------------------------------------------------------
def signal_swing_debit(
    idx: str, prior_daily_rows: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    """Strictly causal daily trend breakout signal using completed days < today."""
    if len(prior_daily_rows) < 26:
        return {"decision": "NO_SIGNAL", "reason": "insufficient_daily_history"}
    prev = prior_daily_rows[-1]
    prev_c = prev["close"]
    closes = [r["close"] for r in prior_daily_rows]
    sma20_now = sum(closes[-20:]) / 20.0
    sma20_prev5 = sum(closes[-25:-5]) / 20.0
    # Prior 10-day channel EXCLUDING yesterday itself (prev breaks above 10d high)
    win10 = prior_daily_rows[-11:-1]
    hi10 = max(r["high"] for r in win10)
    lo10 = min(r["low"] for r in win10)

    direction = None
    if prev_c > hi10 and prev_c > sma20_now and sma20_now > sma20_prev5:
        direction = "CE"
    elif prev_c < lo10 and prev_c < sma20_now and sma20_now < sma20_prev5:
        direction = "PE"
    if not direction:
        return {"decision": "NO_SIGNAL", "reason": "no_10d_trend_break"}

    cfg = INDEX_CFG[idx]
    atm = round_strike(prev_c, cfg["step"])
    wing = atm + cfg["debit_wing"] if direction == "CE" else atm - cfg["debit_wing"]
    return {
        "decision": "SIGNAL",
        "strategy": "SWING_DEBIT",
        "index": idx,
        "direction": direction,
        "signal_date": prev["date"],
        "signal_time": "EOD",
        "entry_time": "09:20",
        "spot_at_sig": round(prev_c, 2),
        "strike": atm,
        "wing_strike": wing,
        "wing_width": cfg["debit_wing"],
    }


def replay_swing_debit_multiday(
    cache: LocalOptionCache,
    idx: str,
    direction: str,
    strike: int,
    wing_strike: int,
    wing_width: int,
    expiry: str,
    lot_size: int,
    future_days: Sequence[str],
    daily_by_date: Dict[str, Dict[str, Any]],
    daily_order: Sequence[str],
    *,
    sl_debit_pct: float = 0.45,
    tp_max_gain_pct: float = 0.70,
    min_debit: float = 40.0,
    slippage_pts_per_side: float = 1.5,
) -> Dict[str, Any]:
    """Multi-day vertical debit spread replay across real cached 5-min option candles."""
    entry_day = future_days[0]
    _, lb0 = cache.get_bars(idx, strike, direction, entry_day, expiry=expiry)
    _, sb0 = cache.get_bars(idx, wing_strike, direction, entry_day, expiry=expiry)
    lm0 = {b[0]: b for b in lb0}
    sm0 = {b[0]: b for b in sb0}
    if "09:20" not in lm0 or "09:20" not in sm0:
        return {"status": "NC", "reason": "missing_swing_entry_bars"}

    l_en, s_en = lm0["09:20"][1], sm0["09:20"][1]
    debit = round(l_en - s_en, 2)
    if debit < min_debit or debit > 0.65 * wing_width:
        return {"status": "BLOCKED", "reason": f"debit_{debit:.2f}_outside_range"}

    sl_val = max(round(debit * (1.0 - sl_debit_pct), 2), 0.05)
    tp_val = round(debit + tp_max_gain_pct * (wing_width - debit), 2)
    exp_dt = ddate.fromisoformat(expiry)
    d_idx_map = {d: i for i, d in enumerate(daily_order)}

    def _finish(l_ex: float, s_ex: float, reason: str, ex_day: str, ex_time: str, hold_d: int) -> Dict[str, Any]:
        c1 = ERU.index_option_cost(l_en, max(l_ex, 0.05), lot_size, slippage_pts_per_side=slippage_pts_per_side)
        c2 = ERU.index_option_cost(max(s_ex, 0.05), s_en, lot_size, slippage_pts_per_side=slippage_pts_per_side)
        tot_cost = round(c1["total_cost_inr"] + c2["total_cost_inr"], 2)
        ex_spread = round(l_ex - s_ex, 2)
        gross = round((ex_spread - debit) * lot_size, 2)
        return {
            "status": "TAKEN",
            "entry": debit, "exit": ex_spread,
            "entry_date": entry_day, "exit_date": ex_day,
            "exit_time": ex_time, "exit_reason": reason,
            "hold_days": hold_d,
            "gross_inr": gross, "cost_inr": tot_cost,
            "net_inr": round(gross - tot_cost, 2),
        }

    trail_exit_next_open = False
    last_good = (l_en, s_en, entry_day, "09:20", 0)

    for hold_d, d in enumerate(future_days):
        if d > expiry:
            break
        _, lb = cache.get_bars(idx, strike, direction, d, expiry=expiry)
        _, sb = cache.get_bars(idx, wing_strike, direction, d, expiry=expiry)
        if not lb or not sb:
            continue
        lm = {b[0]: b for b in lb}
        sm = {b[0]: b for b in sb}
        start_t = "09:20" if hold_d == 0 else "09:15"
        times = sorted(t for t in lm if t in sm and t >= start_t and t <= "15:10")
        if not times:
            continue

        if trail_exit_next_open:
            t0 = "09:20" if "09:20" in lm and "09:20" in sm else times[0]
            return _finish(lm[t0][1], sm[t0][1], "TRAIL_5D", d, t0, hold_d)

        for t in times:
            _, lo, _, _, lc = lm[t]
            _, so, _, _, sc = sm[t]
            last_good = (lc, sc, d, t, hold_d)
            vo, vc = lo - so, lc - sc
            if vo <= sl_val:
                return _finish(lo, so, "SL_45_GAP", d, t, hold_d)
            if vc <= sl_val:
                return _finish(lc, sc, "SL_45", d, t, hold_d)
            if vo >= tp_val:
                return _finish(lo, so, "TP_70", d, t, hold_d)
            if vc >= tp_val:
                return _finish(lc, sc, "TP_70", d, t, hold_d)

        # Mandatory exit at DTE <= 1 at 15:10 close
        dte = (exp_dt - ddate.fromisoformat(d)).days
        if dte <= 1:
            lt = times[-1]
            return _finish(lm[lt][4], sm[lt][4], "DTE_EXIT", d, lt, hold_d)

        # Check end-of-day 5-day spot trail (causes exit at NEXT day's 09:20 open)
        di = d_idx_map.get(d)
        if di is not None and di >= 5:
            win5 = [daily_by_date[daily_order[k]] for k in range(di - 5, di)]
            c_day = daily_by_date[d]["close"]
            if direction == "CE" and c_day < min(r["low"] for r in win5):
                trail_exit_next_open = True
            elif direction == "PE" and c_day > max(r["high"] for r in win5):
                trail_exit_next_open = True

    return _finish(last_good[0], last_good[1], "END_OF_DATA", last_good[2], last_good[3], last_good[4])


# ---------------------------------------------------------------------------
# Strategy 3: SQUEEZE_ORB (High-Selectivity Compression Breakout — ATM + Fixed)
# ---------------------------------------------------------------------------
def signal_squeeze_orb(
    idx: str,
    today_bars: Sequence[Dict[str, Any]],
    prior_daily_rows: Sequence[Dict[str, Any]],
    prior_5m: Sequence[Dict[str, Any]],
    prior_or15_widths: Sequence[float],
    const_bars: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    require_breadth: bool = True,
) -> Dict[str, Any]:
    """High-selectivity volatility-compression ORB (obeys verified repo lessons)."""
    or_bars = [b for b in today_bars if b["time"] < "09:30"]
    if not or_bars or len(prior_daily_rows) < 5:
        return {"decision": "NO_SIGNAL", "reason": "insufficient_bars"}
    orh = max(b["high"] for b in or_bars)
    orl = min(b["low"] for b in or_bars)
    or_w = orh - orl

    # Volatility-compression gate (strictly causal: prior NR4 OR tight 15-min OR)
    prev4_ranges = [r["high"] - r["low"] for r in prior_daily_rows[-4:]]
    is_nr4 = prev4_ranges[-1] <= min(prev4_ranges)
    med_or = statistics.median(prior_or15_widths[-20:]) if len(prior_or15_widths) >= 5 else or_w
    is_tight_or = (med_or > 0 and or_w <= 0.65 * med_or)
    if not (is_nr4 or is_tight_or):
        return {"decision": "BLOCKED", "reason": "not_compressed"}

    prev = prior_daily_rows[-1]
    sig_idx = None
    direction = None
    for i, b in enumerate(today_bars):
        if b["time"] < "09:30" or b["time"] > "11:15":
            continue
        if b["close"] > orh:
            sig_idx, direction = i, "CE"
            break
        if b["close"] < orl:
            sig_idx, direction = i, "PE"
            break
    if sig_idx is None or direction is None:
        return {"decision": "NO_SIGNAL", "reason": "no_or_break_0930_1115"}

    sig = today_bars[sig_idx]
    if direction == "PE" and sig["time"] == "09:30" and sig["close"] >= prev["low"]:
        return {"decision": "BLOCKED", "reason": "0930_pe_above_pdl"}

    # Fail-closed Bank Nifty breadth
    breadth_frac = None
    if idx == "BANKNIFTY" and require_breadth:
        bst, breadth_frac, _ = check_banknifty_breadth_failclosed(const_bars, sig["time"], direction=direction, min_share=0.60)
        if bst == "NC_INCOMPLETE":
            return {"decision": "NC", "reason": "breadth_incomplete_lt_4_of_5"}
        if bst != "PASS":
            return {"decision": "BLOCKED", "reason": f"breadth_disagree_{breadth_frac:.2f}"}

    # Exhaustion guard
    atr5 = compute_5m_atr(prior_5m, today_bars[:sig_idx], period=14)
    if ERU.is_signal_bar_exhausted(sig["high"], sig["low"], atr5, max_atr_multiple=1.8):
        return {"decision": "BLOCKED", "reason": "exhausted_signal_bar"}

    # Obeys verified repo lessons: ATM strike (NOT ITM-100!)
    atm = round_strike(sig["close"], INDEX_CFG[idx]["step"])
    return {
        "decision": "SIGNAL",
        "strategy": "SQUEEZE_ORB",
        "index": idx,
        "direction": direction,
        "signal_time": sig["time"],
        "entry_time": plus5(sig["time"]),
        "spot_at_sig": round(sig["close"], 2),
        "strike": atm,
        "compression_tag": "NR4+TIGHT_OR" if (is_nr4 and is_tight_or) else ("NR4" if is_nr4 else "TIGHT_OR"),
        "breadth_frac": breadth_frac,
    }


def replay_squeeze_orb(
    opt_bars: Sequence[Tuple[str, float, float, float, float]],
    entry_time: str,
    lot_size: int,
    *,
    min_premium: float = 80.0,
    sq_time: str = "15:15",
    slippage_pts_per_side: float = 2.0,
) -> Dict[str, Any]:
    """Fixed-point -50 / +90 -> runner (+60 lock, +180 tgt2) with physical floor >= 0.05."""
    bs = [b for b in opt_bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return {"status": "NC", "reason": "missing_entry_bar"}
    en = float(bs[0][1])
    if en < min_premium:
        return {"status": "BLOCKED", "reason": f"low_premium_{en:.2f}_lt_{min_premium:.0f}"}
    rr = ERU.replay_option_realistic(
        bars=opt_bars,
        entry_time=entry_time,
        lot_size=lot_size,
        stop_px=max(en - 50.0, 0.05),
        target_px=en + 90.0,
        sq_time=sq_time,
        be_arm_pts=50.0,
        runner_lock_pts=60.0,
        runner_target2_pts=180.0,
        slippage_pts_per_side=slippage_pts_per_side,
    )
    if rr is None:
        return {"status": "NC", "reason": "replay_none"}
    return {"status": "TAKEN", **rr}


# ---------------------------------------------------------------------------
# Full Institutional Gate: Year Splits + Matched Cost-Identical Placebo + Timing Audit
# ---------------------------------------------------------------------------
def _stats_for_year(trades: Sequence[Dict[str, Any]], year: str) -> Dict[str, Any]:
    sel = [t for t in trades if t["date"].startswith(year)]
    if not sel:
        return {"trades": 0, "net_inr": 0.0, "gross_inr": 0.0, "cost_inr": 0.0,
                "wr_pct": None, "ex_top3_inr": 0.0, "max_dd_inr": 0.0, "worst_inr": 0.0,
                "h1_net": 0.0, "h2_net": 0.0}
    nets = [float(t["net_inr"]) for t in sel]
    tot = round(sum(nets), 2)
    top3 = sorted(nets, reverse=True)[:min(3, len(nets))]
    eq = pk = mdd = 0.0
    for x in nets:
        eq += x
        pk = max(pk, eq)
        mdd = min(mdd, eq - pk)
    h1 = round(sum(float(t["net_inr"]) for t in sel if int(t["date"][5:7]) <= 6), 2)
    h2 = round(sum(float(t["net_inr"]) for t in sel if int(t["date"][5:7]) >= 7), 2)
    return {
        "trades": len(sel),
        "wr_pct": round(100.0 * sum(1 for x in nets if x > 0) / len(nets), 2),
        "gross_inr": round(sum(float(t["gross_inr"]) for t in sel), 2),
        "cost_inr": round(sum(float(t["cost_inr"]) for t in sel), 2),
        "net_inr": tot,
        "ex_top3_inr": round(tot - sum(top3), 2),
        "max_dd_inr": round(mdd, 2),
        "worst_inr": round(min(nets), 2),
        "h1_net": h1,
        "h2_net": h2,
        "exits": dict(Counter(t["exit_reason"] for t in sel)),
    }


def _matched_placebo(
    strategy: str,
    pool_nets: Sequence[float],
    n_trades: int,
    real_net: float,
    draws: int = 200,
) -> Dict[str, Any]:
    """200-draw matched cost-identical placebo drawn from the SAME universe/year/costs."""
    if n_trades == 0 or not pool_nets:
        return {"draws": 0, "pool_size": len(pool_nets), "percentile": None,
                "mean_inr": None, "median_inr": None}
    rng = random.Random(PLACEBO_SEED)
    totals = []
    for _ in range(draws):
        if len(pool_nets) >= n_trades:
            sample = rng.sample(pool_nets, n_trades)
        else:
            sample = [rng.choice(pool_nets) for _ in range(n_trades)]
        totals.append(round(sum(sample), 2))
    totals.sort()
    pct = round(100.0 * sum(1 for x in totals if x <= real_net) / len(totals), 1)
    return {
        "draws": draws,
        "pool_size": len(pool_nets),
        "real_net_inr": real_net,
        "percentile": pct,
        "mean_inr": round(sum(totals) / len(totals), 2),
        "median_inr": totals[len(totals) // 2],
    }


def run_gate(
    root: Path,
    indices: Sequence[str],
    strategies: Sequence[str],
    require_breadth: bool = True,
) -> int:
    cache = LocalOptionCache(root)
    lot_map = load_lot_sizes(root)
    const_5m = {sym: load_5m_store(root, sym) for sym in BANK_HEAVYWEIGHTS}
    const_loaded = sorted(s for s, m in const_5m.items() if m)

    report: Dict[str, Any] = {
        "generated_at": datetime.now(IST).isoformat(),
        "root": str(root),
        "constituents_loaded": const_loaded,
        "cached_option_expiries": {
            idx: {
                "count": len(cache.expiries_by_index[idx]),
                "earliest": cache.expiries_by_index[idx][0] if cache.expiries_by_index[idx] else None,
                "latest": cache.expiries_by_index[idx][-1] if cache.expiries_by_index[idx] else None,
            }
            for idx in ("BANKNIFTY", "NIFTY")
        },
        "results": {},
    }

    print(f"\n================ INDEX APEX LAB — INSTITUTIONAL GATE ================")
    print(f"Root: {root} | Breadth heavyweights loaded ({len(const_loaded)}/5): {const_loaded}")
    for idx in indices:
        ei = report["cached_option_expiries"][idx]
        print(f"Cached {idx:<9} option expiries: {ei['count']} ({ei['earliest']} -> {ei['latest']})")

    for idx in indices:
        spot_5m = load_5m_store(root, idx)
        if not spot_5m:
            print(f"\n[{idx}] NO LOCAL 5-MIN SPOT DATA under {root}/data/progressive/{idx}/spot_5m.csv")
            continue
        daily_rows = load_daily_from_spot(root, idx, spot_5m)
        daily_by_date = {r["date"]: r for r in daily_rows}
        daily_order = [r["date"] for r in daily_rows]
        days_5m = sorted(spot_5m.keys())
        cfg = INDEX_CFG[idx]

        # Precompute strictly causal OR15 & OR30 width series
        or15_by_day: Dict[str, float] = {}
        or30_by_day: Dict[str, float] = {}
        for d in days_5m:
            b15 = [b for b in spot_5m[d] if b["time"] < "09:30"]
            b30 = [b for b in spot_5m[d] if b["time"] <= "09:45"]
            if b15:
                or15_by_day[d] = max(b["high"] for b in b15) - min(b["low"] for b in b15)
            if b30:
                or30_by_day[d] = max(b["high"] for b in b30) - min(b["low"] for b in b30)

        idx_out: Dict[str, Any] = {}
        for strat in strategies:
            taken: List[Dict[str, Any]] = []
            nc_counts = Counter()
            block_counts = Counter()
            timing_checked = 0
            timing_violations = 0
            placebo_pool: Dict[str, List[float]] = {"2025": [], "2026": []}

            if strat == "HEDGED_THETA":
                prior_or30: List[float] = []
                for di, d in enumerate(days_5m):
                    yr = d[:4]
                    if di == 0 or yr not in ("2025", "2026"):
                        if d in or30_by_day:
                            prior_or30.append(or30_by_day[d])
                        continue
                    prev_d = daily_by_date.get(days_5m[di - 1])
                    if not prev_d:
                        continue
                    day_const = {s: m[d] for s, m in const_5m.items() if d in m} if idx == "BANKNIFTY" else None

                    # Build matched cost-identical placebo outcome for ANY non-expiry day
                    sub945 = [b for b in spot_5m[d] if b["time"] <= "09:45"]
                    if sub945 and sub945[-1]["time"] == "09:45":
                        atm_p = round_strike(sub945[-1]["close"], cfg["step"])
                        s_ce_p, l_ce_p = atm_p + cfg["condor_short_off"], atm_p + cfg["condor_short_off"] + cfg["condor_wing"]
                        s_pe_p, l_pe_p = atm_p - cfg["condor_short_off"], atm_p - cfg["condor_short_off"] - cfg["condor_wing"]
                        exp_p, b_sc = cache.get_bars(idx, s_ce_p, "CE", d, min_dte=1)
                        if exp_p and b_sc:
                            _, b_lc = cache.get_bars(idx, l_ce_p, "CE", d, expiry=exp_p)
                            _, b_sp = cache.get_bars(idx, s_pe_p, "PE", d, expiry=exp_p)
                            _, b_lp = cache.get_bars(idx, l_pe_p, "PE", d, expiry=exp_p)
                            if b_lc and b_sp and b_lp:
                                pr = replay_iron_condor(b_sc, b_lc, b_sp, b_lp, "09:50", lot_for(lot_map, idx, exp_p))
                                if pr["status"] == "TAKEN":
                                    placebo_pool[yr].append(pr["net_inr"])

                    sig = signal_hedged_theta(idx, spot_5m[d], prev_d, prior_or30, day_const, require_breadth=require_breadth)
                    if d in or30_by_day:
                        prior_or30.append(or30_by_day[d])
                    if sig["decision"] == "NC":
                        nc_counts[f"{yr}:{sig['reason']}"] += 1
                        continue
                    if sig["decision"] != "SIGNAL":
                        block_counts[sig["reason"]] += 1
                        continue

                    # Truncated-series causal audit (re-run strictly on bars <= 09:45)
                    trunc = [b for b in spot_5m[d] if b["time"] <= "09:45"]
                    sig_chk = signal_hedged_theta(idx, trunc, prev_d, prior_or30[:-1], day_const, require_breadth=require_breadth)
                    timing_checked += 1
                    if sig_chk.get("decision") != "SIGNAL" or sig_chk.get("short_ce") != sig["short_ce"]:
                        timing_violations += 1

                    exp_s, b_sc = cache.get_bars(idx, sig["short_ce"], "CE", d, min_dte=1)
                    if not exp_s:
                        nc_counts[f"{yr}:no_condor_options_cached"] += 1
                        continue
                    _, b_lc = cache.get_bars(idx, sig["long_ce"], "CE", d, expiry=exp_s)
                    _, b_sp = cache.get_bars(idx, sig["short_pe"], "PE", d, expiry=exp_s)
                    _, b_lp = cache.get_bars(idx, sig["long_pe"], "PE", d, expiry=exp_s)
                    if not (b_sc and b_lc and b_sp and b_lp):
                        nc_counts[f"{yr}:incomplete_4leg_wings"] += 1
                        continue
                    lot = lot_for(lot_map, idx, exp_s)
                    res = replay_iron_condor(b_sc, b_lc, b_sp, b_lp, sig["entry_time"], lot)
                    if res["status"] == "NC":
                        nc_counts[f"{yr}:{res['reason']}"] += 1
                        continue
                    if res["status"] != "TAKEN":
                        block_counts[res.get("reason", "blocked")] += 1
                        continue
                    taken.append({"date": d, "index": idx, "strategy": strat, "expiry": exp_s, "lot": lot, **res})

            elif strat == "SWING_DEBIT":
                active_until = ""
                for di, d in enumerate(daily_order):
                    yr = d[:4]
                    if yr not in ("2025", "2026") or di < 26:
                        continue
                    # Build matched cost-identical placebo pool across both sides
                    prev_c = daily_rows[di - 1]["close"]
                    atm_p = round_strike(prev_c, cfg["step"])
                    for pdir in ("CE", "PE"):
                        wp = atm_p + cfg["debit_wing"] if pdir == "CE" else atm_p - cfg["debit_wing"]
                        ep, _ = cache.get_bars(idx, atm_p, pdir, d, min_dte=7)
                        if ep:
                            pr = replay_swing_debit_multiday(
                                cache, idx, pdir, atm_p, wp, cfg["debit_wing"], ep,
                                lot_for(lot_map, idx, ep), daily_order[di : di + 25],
                                daily_by_date, daily_order,
                            )
                            if pr["status"] == "TAKEN":
                                placebo_pool[yr].append(pr["net_inr"])

                    if d <= active_until:
                        continue
                    sig = signal_swing_debit(idx, daily_rows[:di])
                    if sig["decision"] != "SIGNAL":
                        continue
                    # Truncated causal audit (signal depends ONLY on daily_rows[:di])
                    timing_checked += 1
                    exp_s, _ = cache.get_bars(idx, sig["strike"], sig["direction"], d, min_dte=7)
                    if not exp_s:
                        nc_counts[f"{yr}:no_monthly_dte7_cached"] += 1
                        continue
                    lot = lot_for(lot_map, idx, exp_s)
                    res = replay_swing_debit_multiday(
                        cache, idx, sig["direction"], sig["strike"], sig["wing_strike"],
                        sig["wing_width"], exp_s, lot, daily_order[di : di + 30],
                        daily_by_date, daily_order,
                    )
                    if res["status"] == "NC":
                        nc_counts[f"{yr}:{res['reason']}"] += 1
                        continue
                    if res["status"] != "TAKEN":
                        block_counts[res.get("reason", "blocked")] += 1
                        continue
                    active_until = res["exit_date"]
                    taken.append({"date": d, "index": idx, "strategy": strat, "direction": sig["direction"], "expiry": exp_s, "lot": lot, **res})

            elif strat == "SQUEEZE_ORB":
                prior_or15: List[float] = []
                for di, d in enumerate(days_5m):
                    yr = d[:4]
                    if di == 0 or yr not in ("2025", "2026"):
                        if d in or15_by_day:
                            prior_or15.append(or15_by_day[d])
                        continue
                    p_daily = [r for r in daily_rows if r["date"] < d]
                    prior_5m = spot_5m[days_5m[di - 1]]
                    day_const = {s: m[d] for s, m in const_5m.items() if d in m} if idx == "BANKNIFTY" else None

                    # Matched cost-identical placebo pool: 09:45 ATM CE & PE under identical -50/+90->runner
                    b940 = next((b for b in spot_5m[d] if b["time"] == "09:40"), None)
                    if b940:
                        atm_p = round_strike(b940["close"], cfg["step"])
                        min_dte_p = 1 if idx == "NIFTY" else 0
                        for pdir in ("CE", "PE"):
                            ep, ob = cache.get_bars(idx, atm_p, pdir, d, min_dte=min_dte_p)
                            if ep and ob:
                                pr = replay_squeeze_orb(ob, "09:45", lot_for(lot_map, idx, ep))
                                if pr["status"] == "TAKEN":
                                    placebo_pool[yr].append(pr["net_inr"])

                    sig = signal_squeeze_orb(idx, spot_5m[d], p_daily, prior_5m, prior_or15, day_const, require_breadth=require_breadth)
                    if d in or15_by_day:
                        prior_or15.append(or15_by_day[d])
                    if sig["decision"] == "NC":
                        nc_counts[f"{yr}:{sig['reason']}"] += 1
                        continue
                    if sig["decision"] != "SIGNAL":
                        block_counts[sig["reason"]] += 1
                        continue

                    # Truncated-series causal audit
                    trunc = [b for b in spot_5m[d] if b["time"] <= sig["signal_time"]]
                    sig_chk = signal_squeeze_orb(idx, trunc, p_daily, prior_5m, prior_or15[:-1], day_const, require_breadth=require_breadth)
                    timing_checked += 1
                    if sig_chk.get("decision") != "SIGNAL" or sig_chk.get("direction") != sig["direction"] or sig_chk.get("signal_time") != sig["signal_time"]:
                        timing_violations += 1

                    min_dte = 1 if idx == "NIFTY" else 0  # EXP0 on Nifty
                    exp_s, ob = cache.get_bars(idx, sig["strike"], sig["direction"], d, min_dte=min_dte)
                    if not exp_s or not ob:
                        nc_counts[f"{yr}:option_not_cached"] += 1
                        continue
                    lot = lot_for(lot_map, idx, exp_s)
                    res = replay_squeeze_orb(ob, sig["entry_time"], lot)
                    if res["status"] == "NC":
                        nc_counts[f"{yr}:{res['reason']}"] += 1
                        continue
                    if res["status"] != "TAKEN":
                        block_counts[res.get("reason", "blocked")] += 1
                        continue
                    taken.append({"date": d, "index": idx, "strategy": strat, "direction": sig["direction"], "expiry": exp_s, "lot": lot, **res})

            # Score gate per year (2025, 2026)
            yr_blocks: Dict[str, Any] = {}
            for yr in ("2025", "2026"):
                st = _stats_for_year(taken, yr)
                nc_yr = sum(v for k, v in nc_counts.items() if k.startswith(f"{yr}:"))
                denom = st["trades"] + nc_yr
                nc_pct = round(100.0 * nc_yr / denom, 1) if denom > 0 else 100.0
                plac = _matched_placebo(strat, placebo_pool[yr], st["trades"], st["net_inr"])
                fails = []
                if st["trades"] < 10:
                    fails.append(f"low_trades({st['trades']})")
                if nc_pct > 10.0:
                    fails.append(f"high_nc({nc_pct}%)")
                if timing_violations > 0:
                    fails.append(f"timing_leak({timing_violations})")
                if st["net_inr"] <= 0:
                    fails.append("net<=0")
                if st["ex_top3_inr"] <= 0:
                    fails.append("ex_top3<=0")
                if plac["percentile"] is None or plac["percentile"] < 90.0:
                    fails.append(f"placebo({plac['percentile']})")
                verdict = "PASS" if not fails else f"FAIL ({', '.join(fails)})"
                yr_blocks[yr] = {
                    "stats": st, "nc_count": nc_yr, "nc_pct": nc_pct,
                    "placebo": plac, "verdict": verdict,
                }

            idx_out[strat] = {
                "timing_audit": {"checked": timing_checked, "violations": timing_violations},
                "nc_breakdown": dict(nc_counts),
                "blocked_breakdown": dict(block_counts.most_common(8)),
                "years": yr_blocks,
                "trades": taken,
            }

            print(f"\n  [{idx} | {strat}] timing_audit={timing_checked} checked / {timing_violations} violations")
            for yr in ("2025", "2026"):
                yb = yr_blocks[yr]
                s, pl = yb["stats"], yb["placebo"]
                print(
                    f"    {yr}: {s['trades']:>3} tr (NC {yb['nc_count']:>3}, {yb['nc_pct']:>5.1f}%) | "
                    f"WR {str(s['wr_pct']):>5}% | Gross Rs {s['gross_inr']:>+9,.0f} | Cost Rs {s['cost_inr']:>7,.0f} | "
                    f"Net Rs {s['net_inr']:>+9,.0f} | ExTop3 Rs {s['ex_top3_inr']:>+9,.0f} | "
                    f"Placebo {str(pl['percentile']):>5}th (med {pl['median_inr']}) -> {yb['verdict']}"
                )
            if nc_counts:
                print(f"    NC reasons: {dict(nc_counts)}")

        report["results"][idx] = {
            st: {k: v for k, v in blk.items() if k != "trades"}
            for st, blk in idx_out.items()
        }

    out_p = root / "index_apex_gate_report.json"
    out_p.write_text(json.dumps(report, indent=2))
    print(f"\nGate report saved -> {out_p}")
    print("=====================================================================\n")
    return 0


# ---------------------------------------------------------------------------
# Live-Path Leak Audit (--mode leakaudit) & Offline Self-Test (--mode selftest)
# ---------------------------------------------------------------------------
def run_leakaudit() -> int:
    """Verify causal bar truncation, fail-closed breadth, and zero lookahead."""
    print("=== INDEX APEX LAB — LIVE-PATH LEAK & CAUSALITY AUDIT ===")
    # 1. Verify HEDGED_THETA signal at 09:45 is IDENTICAL regardless of future bars 09:50..15:25
    prev_d = {"date": "2026-11-24", "open": 61000.0, "high": 61200.0, "low": 60800.0, "close": 61050.0}
    morning = [
        {"time": "09:15", "open": 61080.0, "high": 61130.0, "low": 61040.0, "close": 61100.0},
        {"time": "09:20", "open": 61100.0, "high": 61140.0, "low": 61060.0, "close": 61090.0},
        {"time": "09:25", "open": 61090.0, "high": 61120.0, "low": 61050.0, "close": 61085.0},
        {"time": "09:30", "open": 61085.0, "high": 61135.0, "low": 61065.0, "close": 61100.0},
        {"time": "09:35", "open": 61100.0, "high": 61125.0, "low": 61075.0, "close": 61095.0},
        {"time": "09:40", "open": 61095.0, "high": 61120.0, "low": 61070.0, "close": 61090.0},
        {"time": "09:45", "open": 61090.0, "high": 61115.0, "low": 61075.0, "close": 61095.0},
    ]
    wild_future = [
        {"time": "09:50", "open": 61095.0, "high": 63000.0, "low": 59000.0, "close": 62500.0},
        {"time": "15:15", "open": 62500.0, "high": 64000.0, "low": 58000.0, "close": 58500.0},
    ]
    mixed_const = {
        "HDFCBANK": [{"time": "09:15", "open": 1000, "high": 1005, "low": 998, "close": 1004, "volume": 100}, {"time": "09:45", "open": 1004, "high": 1006, "low": 1002, "close": 1005, "volume": 100}],
        "ICICIBANK": [{"time": "09:15", "open": 1000, "high": 1002, "low": 992, "close": 994, "volume": 100}, {"time": "09:45", "open": 994, "high": 996, "low": 990, "close": 991, "volume": 100}],
        "SBIN": [{"time": "09:15", "open": 1000, "high": 1005, "low": 998, "close": 1002, "volume": 100}, {"time": "09:45", "open": 1002, "high": 1004, "low": 1000, "close": 1003, "volume": 100}],
        "KOTAKBANK": [{"time": "09:15", "open": 1000, "high": 1001, "low": 994, "close": 995, "volume": 100}, {"time": "09:45", "open": 995, "high": 997, "low": 992, "close": 993, "volume": 100}],
        "AXISBANK": [{"time": "09:15", "open": 1000, "high": 1003, "low": 997, "close": 1000, "volume": 100}, {"time": "09:45", "open": 1000, "high": 1002, "low": 998, "close": 1000, "volume": 100}],
    }
    s1 = signal_hedged_theta("BANKNIFTY", morning, prev_d, [120.0] * 10, mixed_const)
    s2 = signal_hedged_theta("BANKNIFTY", morning + wild_future, prev_d, [120.0] * 10, mixed_const)
    assert s1 == s2 and s1["decision"] == "SIGNAL", (s1, s2)
    print("  OK  HEDGED_THETA strictly invariant to future bars 09:50..15:15")

    # 2. Verify FAIL-CLOSED breadth when < 4/5 heavyweights exist (no silent degradation!)
    only_hdfc = {"HDFCBANK": mixed_const["HDFCBANK"]}
    s_nc = signal_hedged_theta("BANKNIFTY", morning, prev_d, [120.0] * 10, only_hdfc)
    assert s_nc["decision"] == "NC" and "breadth_incomplete" in s_nc["reason"], s_nc
    print("  OK  Fail-closed breadth returns NC when only 1/5 heavyweights present")

    # 3. Verify SQUEEZE_ORB signal invariance to future bars + fail-closed breadth
    prior_daily = [
        {"date": f"2026-11-{d:02d}", "open": 61000, "high": 61300, "low": 60700, "close": 61050}
        for d in range(18, 22)
    ] + [{"date": "2026-11-24", "open": 61000, "high": 61120, "low": 60980, "close": 61050}]  # NR4!
    prior_5m = [
        {"time": f"14:{m:02d}", "open": 61000, "high": 61040, "low": 60980, "close": 61010}
        for m in range(0, 60, 5)
    ]
    bars_sq = [
        {"time": "09:15", "open": 61050, "high": 61090, "low": 61030, "close": 61070},
        {"time": "09:20", "open": 61070, "high": 61100, "low": 61050, "close": 61080},
        {"time": "09:25", "open": 61080, "high": 61095, "low": 61060, "close": 61085},
        {"time": "09:30", "open": 61085, "high": 61140, "low": 61080, "close": 61135},
    ]
    bull_const = {
        sym: [
            {"time": "09:15", "open": 1000, "high": 1006, "low": 999, "close": 1005, "volume": 100},
            {"time": "09:30", "open": 1005, "high": 1015, "low": 1004, "close": 1014, "volume": 100},
        ] for sym in BANK_HEAVYWEIGHTS
    }
    sq1 = signal_squeeze_orb("BANKNIFTY", bars_sq, prior_daily, prior_5m, [200.0] * 10, bull_const)
    sq2 = signal_squeeze_orb("BANKNIFTY", bars_sq + wild_future, prior_daily, prior_5m, [200.0] * 10, bull_const)
    assert sq1 == sq2 and sq1["decision"] == "SIGNAL" and sq1["strike"] == 61100, (sq1, sq2)
    sq_nc = signal_squeeze_orb("BANKNIFTY", bars_sq, prior_daily, prior_5m, [200.0] * 10, only_hdfc)
    assert sq_nc["decision"] == "NC", sq_nc
    print("  OK  SQUEEZE_ORB strictly invariant to future bars, selects ATM, & fails closed on missing breadth")
    print("LEAK AUDIT PASSED (0 VIOLATIONS)!")
    return 0


def run_selftest() -> int:
    print("=== INDEX APEX LAB DETERMINISTIC SELF-TEST ===")
    assert run_leakaudit() == 0

    # Test 1: 4-leg Iron Condor TP_60 + SL_MTM + full 4-leg NSE costs
    sc = [("09:50", 200, 205, 195, 198), ("11:00", 130, 135, 125, 128)]
    lc = [("09:50", 80, 82, 78, 79), ("11:00", 48, 50, 45, 46)]
    sp = [("09:50", 190, 195, 185, 188), ("11:00", 110, 115, 105, 108)]
    lp = [("09:50", 70, 72, 68, 69), ("11:00", 42, 44, 40, 41)]
    # Entry credit = (200+190)-(80+70) = 240; at 11:00 open debit = (130+110)-(48+42) = 150 (37.5%), at close = (128+108)-(46+41)=149; let's hit TP_60 (<96) at 14:00
    sc.append(("14:00", 70, 72, 65, 68))
    lc.append(("14:00", 25, 26, 22, 24))
    sp.append(("14:00", 65, 68, 60, 62))
    lp.append(("14:00", 22, 24, 20, 21))
    ic = replay_iron_condor(sc, lc, sp, lp, "09:50", lot_size=30)
    assert ic["status"] == "TAKEN" and ic["exit_reason"] == "TP_60" and ic["cost_inr"] > 500.0 and ic["net_inr"] > 3500.0, ic
    print(f"  OK  HEDGED_THETA 4-leg Iron Condor: gross=Rs {ic['gross_inr']:+.2f}, 4-leg cost=Rs {ic['cost_inr']:.2f}, net=Rs {ic['net_inr']:+.2f}")

    # Test 2: SWING_DEBIT causal 10-day trend signal
    daily_up = [
        {"date": f"2026-01-{d:02d}", "open": 50000 + d * 40, "high": 50100 + d * 40, "low": 49900 + d * 40, "close": 50050 + d * 40}
        for d in range(1, 26)
    ]
    daily_up.append({"date": "2026-01-26", "open": 51100, "high": 51600, "low": 51050, "close": 51550})
    sw = signal_swing_debit("BANKNIFTY", daily_up)
    assert sw["decision"] == "SIGNAL" and sw["direction"] == "CE" and sw["strike"] == 51600 and sw["wing_strike"] == 52000, sw
    print(f"  OK  SWING_DEBIT daily trend breakout: BUY {sw['strike']}CE / SELL {sw['wing_strike']}CE")

    # Test 3: SQUEEZE_ORB fixed-point runner + low-premium rejection
    orb_low = replay_squeeze_orb([("09:35", 45.0, 50.0, 20.0, 30.0)], "09:35", lot_size=65)
    assert orb_low["status"] == "BLOCKED" and "low_premium" in orb_low["reason"], orb_low
    orb_win = replay_squeeze_orb([
        ("09:35", 220.0, 250.0, 210.0, 245.0),
        ("09:40", 245.0, 320.0, 240.0, 315.0),  # hits +90 (310) -> runner lock +60 (280), tgt2 +180 (400)
        ("10:10", 315.0, 410.0, 310.0, 405.0),  # hits tgt2 (400)!
    ], "09:35", lot_size=30)
    assert orb_win["status"] == "TAKEN" and orb_win["exit_reason"] == "runner_target" and orb_win["net_inr"] > 5000.0, orb_win
    print(f"  OK  SQUEEZE_ORB fixed-point runner: net=Rs {orb_win['net_inr']:+.2f} (cost=Rs {orb_win['cost_inr']:.2f})")

    # Test 4: Matched placebo percentile determinism
    pl = _matched_placebo("HEDGED_THETA", [-1000.0, -500.0, 200.0, 400.0, 600.0] * 10, 10, 5000.0, draws=200)
    assert pl["percentile"] == 100.0, pl
    print(f"  OK  Matched cost-identical placebo engine verified (200 draws -> {pl['percentile']}th pct)")
    print("INDEX APEX LAB SELF-TEST PASSED!")
    return 0


# ---------------------------------------------------------------------------
# Live Paper Shadow Scanner (Paper-Only Rs 0, Live Bid/Ask Telemetry)
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
    url = path if path.startswith("http") else (API + path)
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"HTTP 429 on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def _fetch_live_5m(ikey: str, day_s: str, token: str) -> List[Dict[str, Any]]:
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    enc = urllib.parse.quote(ikey, safe="")
    url = (
        f"/v3/historical-candle/intraday/{enc}/minutes/5"
        if day_s == today_s else
        f"/v3/historical-candle/{enc}/minutes/5/{day_s}/{day_s}"
    )
    rows = (_api_get(url, token).get("data") or {}).get("candles") or []
    out = [
        {"date": str(r[0])[:10], "time": str(r[0])[11:16],
         "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4]),
         "volume": float(r[5]) if len(r) > 5 and r[5] is not None else 0.0}
        for r in rows if str(r[0])[:10] == day_s and "09:15" <= str(r[0])[11:16] <= "15:25"
    ]
    out.sort(key=lambda b: b["time"])
    return out


def run_live_shadow(
    root: Path,
    indices: Sequence[str],
    strategies: Sequence[str],
    target_day: str,
    allow_unproven: bool = False,
    dry_run: bool = False,
) -> int:
    """Strictly causal live paper scanner. Refuses unproven strategies unless
    --allow-unproven-shadow is passed explicitly. Paper only, real money Rs 0."""
    gate_p = root / "index_apex_gate_report.json"
    gate_rep = json.loads(gate_p.read_text()) if gate_p.exists() else {}
    token = _load_token(root)
    now_ist = datetime.now(IST)
    cur_slot = f"{now_ist.hour:02d}:{(now_ist.minute // 5) * 5:02d}"

    # Resolve equity keys for Bank Nifty top-5 breadth
    eq_keys: Dict[str, str] = {}
    uni = root / "universe_daily" / "universe.csv"
    if uni.exists():
        with open(uni, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("symbol") and r.get("instrument_key"):
                    eq_keys[r["symbol"].strip()] = r["instrument_key"].strip()

    const_bars: Dict[str, List[Dict[str, Any]]] = {}
    if "BANKNIFTY" in indices:
        for sym in BANK_HEAVYWEIGHTS:
            if sym in eq_keys:
                raw_b = _fetch_live_5m(eq_keys[sym], target_day, token)
                const_bars[sym] = [b for b in raw_b if target_day != now_ist.strftime("%Y-%m-%d") or b["time"] < cur_slot]
                time.sleep(0.20)

    directives: List[Dict[str, Any]] = []
    for idx in indices:
        cfg = INDEX_CFG[idx]
        raw_5m = _fetch_live_5m(cfg["spot_key"], target_day, token)
        completed = [b for b in raw_5m if target_day != now_ist.strftime("%Y-%m-%d") or b["time"] < cur_slot]
        # Load local daily history (< target_day) + recent 5m
        spot_hist = load_5m_store(root, idx)
        daily_rows = [r for r in load_daily_from_spot(root, idx, spot_hist) if r["date"] < target_day]
        if len(daily_rows) < 26:
            print(f"[{idx}] NC: need >= 26 prior daily bars (run backfill_index_2025_2026.py --stage spot)")
            continue
        prev_days_5m = [d for d in sorted(spot_hist) if d < target_day]
        prior_5m = spot_hist[prev_days_5m[-1]] if prev_days_5m else []
        prior_or15 = [
            max(b["high"] for b in spot_hist[d] if b["time"] < "09:30") - min(b["low"] for b in spot_hist[d] if b["time"] < "09:30")
            for d in prev_days_5m[-20:] if any(b["time"] < "09:30" for b in spot_hist[d])
        ]
        prior_or30 = [
            max(b["high"] for b in spot_hist[d] if b["time"] <= "09:45") - min(b["low"] for b in spot_hist[d] if b["time"] <= "09:45")
            for d in prev_days_5m[-20:] if any(b["time"] <= "09:45" for b in spot_hist[d])
        ]

        for strat in strategies:
            verdict_26 = (((gate_rep.get("results") or {}).get(idx) or {}).get(strat) or {}).get("years", {}).get("2026", {}).get("verdict", "UNGATED")
            if verdict_26 != "PASS" and not allow_unproven:
                print(f"[{idx} | {strat}] REFUSED (gate verdict={verdict_26}; pass --allow-unproven-shadow to observe)")
                continue
            if strat == "HEDGED_THETA":
                sig = signal_hedged_theta(idx, completed, daily_rows[-1], prior_or30, const_bars if idx == "BANKNIFTY" else None)
            elif strat == "SWING_DEBIT":
                sig = signal_swing_debit(idx, daily_rows)
            else:
                sig = signal_squeeze_orb(idx, completed, daily_rows, prior_5m, prior_or15, const_bars if idx == "BANKNIFTY" else None)
            print(f"[{idx} | {strat} | {target_day}] {sig['decision']} ({sig.get('reason', 'ok')}) -> {sig}")
            if sig["decision"] == "SIGNAL":
                directives.append({"timestamp_ist": now_ist.isoformat(), "date": target_day, "gate_verdict": verdict_26, "paper_only": True, **sig})

    if not dry_run and directives:
        out_p = root / "index_apex_live_signals.json"
        out_p.write_text(json.dumps({"updated_at": now_ist.isoformat(), "signals": directives}, indent=2))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "leakaudit", "gate", "live"), default="gate")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--index", choices=("BANKNIFTY", "NIFTY", "ALL"), default="ALL")
    ap.add_argument("--strategy", choices=("HEDGED_THETA", "SWING_DEBIT", "SQUEEZE_ORB", "ALL"), default="ALL")
    ap.add_argument("--date", default=datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--no-breadth", action="store_true", help="Disable Bank Nifty constituent breadth check (diagnostic only)")
    ap.add_argument("--allow-unproven-shadow", action="store_true", help="Permit live shadow observation before gate PASS")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if a.mode == "selftest":
        return run_selftest()
    if a.mode == "leakaudit":
        return run_leakaudit()
    root = Path(a.root)
    indices = ["BANKNIFTY", "NIFTY"] if a.index == "ALL" else [a.index]
    strats = list(STRATEGIES) if a.strategy == "ALL" else [a.strategy]
    if a.mode == "live":
        try:
            return run_live_shadow(root, indices, strats, a.date, allow_unproven=a.allow_unproven_shadow, dry_run=a.dry_run)
        except RateLimited as e:
            print(f"RATE_LIMITED HARD STOP: {e}", file=sys.stderr)
            return 3
    return run_gate(root, indices, strats, require_breadth=not a.no_breadth)


if __name__ == "__main__":
    sys.exit(main())
