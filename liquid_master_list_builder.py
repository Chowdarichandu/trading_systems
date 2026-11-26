#!/usr/bin/env python3
"""LIQUID NSE MASTER-LIST BUILDER, FULL-UNIVERSE ACCURACY AUDITOR & LIVE OUTPERFORMER SCANNER.

Directly solves three core problems found in the 2026-11-25/26 audit:
  1. Trades ONLY ultra-liquid NSE index stocks (Nifty 50, Nifty Next 50,
     Nifty Bank, Nifty Midcap 100/150 from sapta_constituents/) — zero
     illiquid tickers.
  2. Eliminates the EKAM [:3]/[:5] alphabetical cap — scores EVERY SINGLE STOCK
     across all ~200 liquid names individually at fixed Rs 1,00,000 capital and
     FULL realistic NSE delivery costs + slippage, reporting true full-universe
     average win rate, median stock PnL, % stocks profitable, and expectancy.
  3. Builds an HONEST Walk-Forward Master List (zero cherry-picking bias!):
     selects durable outperformers strictly on 2025 data ONLY, freezes that
     Master List on 2025-12-31, and tests it BLIND on 2026 Out-of-Sample right
     beside the Full Liquid Universe Average so you know whether stock selection
     actually persists out-of-sample.
  4. Includes a Live Intraday Relative-Strength Scanner (--mode live-leaders)
     that polls all 200 liquid stocks in 4 batched Upstox calls (~2 seconds) and
     ranks TODAY'S real-time liquid outperformers (LONG) & underperformers (SHORT).

PAPER / RESEARCH ONLY. Real money Rs 0. Places ZERO broker orders.

Usage:
  # 1. Deterministic offline self-test (no API or local data required)
  python3 liquid_master_list_builder.py --mode selftest

  # 2. Backfill 2024-2026 daily candles for all ~200 liquid NSE stocks (~60s)
  python3 liquid_master_list_builder.py --mode backfill --universe nifty200

  # 3. Evaluate EVERY liquid stock + build Walk-Forward Master List (2025 -> 2026 OOS)
  python3 liquid_master_list_builder.py --mode evaluate --universe nifty200

  # 4. Live intraday scan: TODAY'S top liquid outperformers vs Nifty 50
  python3 liquid_master_list_builder.py --mode live-leaders --universe nifty200
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
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
import pillar1_value_ekam_swing as P1

IST = ZoneInfo("Asia/Kolkata")
API = "https://api.upstox.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
INSTRUMENTS_URL = (
    "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
)
NIFTY_KEY = "NSE_INDEX|Nifty 50"


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "data").exists() or (live / "upstox_refresh" / ".env").exists():
        return live
    return THIS_DIR


# ---------------------------------------------------------------------------
# 1. Ultra-Liquid NSE Universe Loader (from sapta_constituents/)
# ---------------------------------------------------------------------------
def load_liquid_universe(root: Path, universe: str = "nifty200") -> List[Dict[str, str]]:
    """Load deduplicated liquid NSE constituents with exact NSE Industry & Index tier."""
    sc = root / "sapta_constituents"
    if not sc.exists():
        sc = THIS_DIR / "sapta_constituents"

    files_map = {
        "nifty50": [("NIFTY50", "ind_nifty50list.csv")],
        "niftybank": [("NIFTYBANK", "ind_niftybanklist.csv")],
        "nifty100": [("NIFTY50", "ind_nifty50list.csv"), ("NIFTY100", "ind_nifty100list.csv")],
        "nifty200": [
            ("NIFTY50", "ind_nifty50list.csv"),
            ("NIFTY100", "ind_nifty100list.csv"),
            ("NIFTYBANK", "ind_niftybanklist.csv"),
            ("MIDCAP100", "ind_niftymidcap100list.csv"),
        ],
        "nifty250": [
            ("NIFTY50", "ind_nifty50list.csv"),
            ("NIFTY100", "ind_nifty100list.csv"),
            ("NIFTYBANK", "ind_niftybanklist.csv"),
            ("MIDCAP150", "ind_niftymidcap150list.csv"),
        ],
    }
    wanted = files_map.get(universe.lower(), files_map["nifty200"])
    seen: Dict[str, Dict[str, str]] = {}
    for bucket, fname in wanted:
        p = sc / fname
        if not p.exists():
            continue
        with open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                sym = (r.get("Symbol") or r.get("symbol") or "").strip()
                if not sym or sym.startswith("DUMMY"):
                    continue
                if sym not in seen:
                    # Distinguish Nifty Next 50 cleanly from Nifty 50 inside ind_nifty100list.csv
                    idx_label = "NIFTY_NEXT50" if bucket == "NIFTY100" else bucket
                    seen[sym] = {
                        "sym": sym,
                        "company": (r.get("Company Name") or sym).strip(),
                        "industry": (r.get("Industry") or "UNKNOWN").strip(),
                        "index_bucket": idx_label,
                    }
    return [seen[k] for k in sorted(seen.keys())]


# ---------------------------------------------------------------------------
# 2. Per-Stock Engines (NO Alphabetical Cap — Every Stock Tested Independently!)
#    A) EKAM Daily 2c S0 (Mean-Reversion Swing, fixed Rs1L, REAL NSE Delivery Cost)
#    B) RS_TREND_20D (20-day Breakout + Outperforming Nifty + 10-day Trail, fixed Rs1L)
# ---------------------------------------------------------------------------
def simulate_stock_ekam2c_s0(
    sym: str,
    dates: Sequence[str],
    o: Sequence[float],
    h: Sequence[float],
    l: Sequence[float],
    c: Sequence[float],
    capital_per_trade: float = 100_000.0,
) -> List[Dict[str, Any]]:
    """Exact EKAM-2c S0 state machine (no premature ATR stop) at fixed capital + REAL delivery cost."""
    ind = P1.compute_indicators(dates, o, h, l, c)
    n = ind["n"]
    trades: List[Dict[str, Any]] = []
    pos: Optional[Dict[str, Any]] = None
    i = 0
    while i < n:
        if pos is None:
            sigs = tuple(k for k in ("BB", "RSI") if ind["sig_in"][k][i])
            if sigs and i + 1 < n:
                ep = float(o[i + 1])
                qty = ERU.fixed_capital_qty(ep, capital_per_trade)
                if qty > 0:
                    pos = {
                        "e": i + 1, "E": ep, "qty": qty, "comps": sigs,
                        "sig_date": dates[i], "upgraded": False,
                    }
                    i += 1
                    continue
            i += 1
            continue

        e, E, qty, comps = pos["e"], pos["E"], pos["qty"], pos["comps"]
        converted_today = False
        if comps == ("BB",) and not pos["upgraded"] and ind["sig_in"]["RSI"][i]:
            pos["upgraded"] = True
            converted_today = True

        allow_tc = ("RSI" in comps) or (comps == ("BB",) and pos["upgraded"] and not converted_today)
        done: Optional[Tuple[int, float, str]] = None
        if allow_tc and (i - e) >= 60 and i > e:
            done = (i, float(o[i]), "TIME60")
        if done is None and allow_tc and i >= e:
            lvl = E * 1.10
            if h[i] >= lvl:
                done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP10")
        if done is None:
            fire = None
            if comps == ("BB",) and pos["upgraded"]:
                if ind["sig_out"]["RSI"][i]:
                    fire = "SIGNAL-RSI"
            elif "RSI" in comps:
                for k in comps:
                    if ind["sig_out"][k][i]:
                        fire = f"SIGNAL-{k}"
                        break
            else:
                if ind["sig_out"]["BB"][i]:
                    fire = "SIGNAL-BB"
            if fire is not None:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), fire)
                else:
                    done = (i, float(c[i]), "FORCED")

        if done is not None:
            xi, xp, why = done
            cost = ERU.equity_delivery_cost(E, xp, qty, slippage_bps_per_side=5.0)["total_cost_inr"]
            gross = (xp - E) * qty
            trades.append({
                "sym": sym, "strategy": "EKAM2C_S0",
                "entry_date": dates[e], "exit_date": dates[xi],
                "qty": qty, "entry": E, "exit": xp, "hold": xi - e,
                "exit_kind": why, "gross_inr": round(gross, 2),
                "cost_inr": cost, "net_inr": round(gross - cost, 2),
            })
            pos = None
            i = xi
            continue
        i += 1

    if pos is not None:
        e, E, qty = pos["e"], pos["E"], pos["qty"]
        xp = float(c[n - 1])
        cost = ERU.equity_delivery_cost(E, xp, qty, slippage_bps_per_side=5.0)["total_cost_inr"]
        gross = (xp - E) * qty
        trades.append({
            "sym": sym, "strategy": "EKAM2C_S0",
            "entry_date": dates[e], "exit_date": dates[n - 1],
            "qty": qty, "entry": E, "exit": xp, "hold": n - 1 - e,
            "exit_kind": "FORCED", "gross_inr": round(gross, 2),
            "cost_inr": cost, "net_inr": round(gross - cost, 2),
        })
    return trades


def simulate_stock_rs_trend(
    sym: str,
    dates: Sequence[str],
    o: Sequence[float],
    h: Sequence[float],
    l: Sequence[float],
    c: Sequence[float],
    nifty_by_date: Dict[str, float],
    capital_per_trade: float = 100_000.0,
) -> List[Dict[str, Any]]:
    """Relative-Strength Trend Outperformer Swing (LONG only, 20d breakout + RS > Nifty + 10d low trail)."""
    n = len(c)
    if n < 55:
        return []
    trades: List[Dict[str, Any]] = []
    pos: Optional[Dict[str, Any]] = None
    i = 50
    while i < n:
        if pos is None:
            # Causal signal at close[i]: 20-day high break + above 50-DMA + outperforming Nifty over 20d
            hi20 = max(h[i - 20 : i])
            sma50 = sum(c[i - 49 : i + 1]) / 50.0
            stk_ret20 = (c[i] / c[i - 20] - 1.0) if c[i - 20] > 0 else 0.0
            nf_now = nifty_by_date.get(dates[i])
            nf_20 = nifty_by_date.get(dates[i - 20])
            nf_ret20 = (nf_now / nf_20 - 1.0) if (nf_now and nf_20 and nf_20 > 0) else 0.0
            if c[i] > hi20 and c[i] > sma50 and (stk_ret20 - nf_ret20) >= 0.02 and i + 1 < n:
                ep = float(o[i + 1])
                qty = ERU.fixed_capital_qty(ep, capital_per_trade)
                if qty > 0:
                    pos = {"e": i + 1, "E": ep, "qty": qty}
                    i += 1
                    continue
            i += 1
            continue

        e, E, qty = pos["e"], pos["E"], pos["qty"]
        # Exit if close drops below trailing 10-day low (next-day open) or hard -12% stop
        done: Optional[Tuple[int, float, str]] = None
        hard_sl = E * 0.88
        if l[i] <= hard_sl:
            done = (i, float(o[i]) if o[i] <= hard_sl else hard_sl, "STOP_12PCT")
        else:
            lo10 = min(l[i - 10 : i])
            if c[i] < lo10:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "TRAIL_10D")
                else:
                    done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            cost = ERU.equity_delivery_cost(E, xp, qty, slippage_bps_per_side=5.0)["total_cost_inr"]
            gross = (xp - E) * qty
            trades.append({
                "sym": sym, "strategy": "RS_TREND_20D",
                "entry_date": dates[e], "exit_date": dates[xi],
                "qty": qty, "entry": E, "exit": xp, "hold": xi - e,
                "exit_kind": why, "gross_inr": round(gross, 2),
                "cost_inr": cost, "net_inr": round(gross - cost, 2),
            })
            pos = None
            i = xi
            continue
        i += 1

    if pos is not None:
        e, E, qty = pos["e"], pos["E"], pos["qty"]
        xp = float(c[n - 1])
        cost = ERU.equity_delivery_cost(E, xp, qty, slippage_bps_per_side=5.0)["total_cost_inr"]
        gross = (xp - E) * qty
        trades.append({
            "sym": sym, "strategy": "RS_TREND_20D",
            "entry_date": dates[e], "exit_date": dates[n - 1],
            "qty": qty, "entry": E, "exit": xp, "hold": n - 1 - e,
            "exit_kind": "FORCED", "gross_inr": round(gross, 2),
            "cost_inr": cost, "net_inr": round(gross - cost, 2),
        })
    return trades


def _stock_metrics(trades: Sequence[Dict[str, Any]], year: str) -> Dict[str, Any]:
    sel = [t for t in trades if t["entry_date"].startswith(year)]
    if not sel:
        return {"trades": 0, "net": 0.0, "gross": 0.0, "cost": 0.0, "wr": 0.0, "pf": 0.0, "worst": 0.0}
    nets = [t["net_inr"] for t in sel]
    wins = [x for x in nets if x > 0]
    losses = [-x for x in nets if x < 0]
    pf = (sum(wins) / sum(losses)) if losses else (99.0 if wins else 0.0)
    return {
        "trades": len(sel),
        "net": round(sum(nets), 2),
        "gross": round(sum(t["gross_inr"] for t in sel), 2),
        "cost": round(sum(t["cost_inr"] for t in sel), 2),
        "wr": round(100.0 * len(wins) / len(sel), 1),
        "pf": round(min(pf, 99.0), 2),
        "worst": round(min(nets), 2),
    }


def _aggregate_universe_stats(per_stock: Sequence[Dict[str, Any]], year_key: str) -> Dict[str, Any]:
    active = [s for s in per_stock if s[year_key]["trades"] > 0]
    if not active:
        return {"stocks_active": 0, "stocks_profitable": 0, "pct_stocks_profitable": 0.0,
                "total_trades": 0, "avg_wr_pct": 0.0, "total_net_inr": 0.0,
                "mean_net_per_stock": 0.0, "median_net_per_stock": 0.0, "avg_net_per_trade": 0.0}
    nets = [s[year_key]["net"] for s in active]
    tot_tr = sum(s[year_key]["trades"] for s in active)
    tot_net = round(sum(nets), 2)
    prof = sum(1 for x in nets if x > 0)
    wrs = [s[year_key]["wr"] for s in active]
    return {
        "stocks_active": len(active),
        "stocks_profitable": prof,
        "pct_stocks_profitable": round(100.0 * prof / len(active), 1),
        "total_trades": tot_tr,
        "avg_wr_pct": round(sum(wrs) / len(wrs), 1),
        "total_net_inr": tot_net,
        "mean_net_per_stock": round(tot_net / len(active), 2),
        "median_net_per_stock": round(statistics.median(nets), 2),
        "avg_net_per_trade": round(tot_net / tot_tr, 2) if tot_tr else 0.0,
    }


# ---------------------------------------------------------------------------
# 3. Walk-Forward Evaluation (2025 Train -> 2026 BLIND Out-of-Sample)
# ---------------------------------------------------------------------------
def run_evaluate(
    root: Path, universe_name: str, strategy: str = "BOTH", capital_per_trade: float = 100_000.0
) -> int:
    uni = load_liquid_universe(root, universe_name)
    ndates, _, _, _, ncloses = P1.load_daily_series(root, "NIFTY")
    nifty_by_date = dict(zip(ndates, ncloses))

    loaded = 0
    missing: List[str] = []
    strats = ("EKAM2C_S0", "RS_TREND_20D") if strategy == "BOTH" else (strategy,)
    results_by_strat: Dict[str, List[Dict[str, Any]]] = {s: [] for s in strats}

    for u in uni:
        sym = u["sym"]
        ds, o, h, l, c = P1.load_daily_series(root, sym)
        if len(ds) < 60:
            missing.append(sym)
            continue
        loaded += 1
        if "EKAM2C_S0" in strats:
            tr = simulate_stock_ekam2c_s0(sym, ds, o, h, l, c, capital_per_trade)
            m25, m26 = _stock_metrics(tr, "2025"), _stock_metrics(tr, "2026")
            results_by_strat["EKAM2C_S0"].append({**u, "y2025": m25, "y2026": m26})
        if "RS_TREND_20D" in strats:
            tr = simulate_stock_rs_trend(sym, ds, o, h, l, c, nifty_by_date, capital_per_trade)
            m25, m26 = _stock_metrics(tr, "2025"), _stock_metrics(tr, "2026")
            results_by_strat["RS_TREND_20D"].append({**u, "y2025": m25, "y2026": m26})

    if loaded == 0:
        print(f"NO LOCAL DAILY STORES FOUND for {universe_name} under {root}/data/.")
        print("Run: python3 liquid_master_list_builder.py --mode backfill --universe nifty200")
        return 2

    full_report: Dict[str, Any] = {
        "generated_at": datetime.now(IST).isoformat(),
        "universe": universe_name,
        "universe_size": len(uni),
        "symbols_loaded": loaded,
        "symbols_missing": len(missing),
        "strategies": {},
    }

    print(f"\n================ LIQUID UNIVERSE ACCURACY & WALK-FORWARD MASTER LIST ({universe_name}) ================")
    print(f"Loaded: {loaded}/{len(uni)} liquid NSE stocks | Capital/trade: Rs {capital_per_trade:,.0f} | REAL NSE Delivery Costs + 5bps/side")

    for st_name, rows in results_by_strat.items():
        # Full-universe honest averages (NO alphabetical cap!)
        all_25 = _aggregate_universe_stats(rows, "y2025")
        all_26 = _aggregate_universe_stats(rows, "y2026")

        # Walk-Forward Master List: selected STRICTLY on 2025 durability (ZERO 2026 peeking!)
        # Criteria on 2025: >=2 trades, net > 0, WR >= 50%, PF >= 1.25, worst trade >= -15% cap
        wf_cands = [
            r for r in rows
            if r["y2025"]["trades"] >= 2
            and r["y2025"]["net"] > 0
            and r["y2025"]["wr"] >= 50.0
            and r["y2025"]["pf"] >= 1.25
            and r["y2025"]["worst"] >= -0.15 * capital_per_trade
        ]
        # Rank by durability score (PF * WR * sqrt(trades)), capped at max 4 per industry & top 30 total
        wf_cands.sort(
            key=lambda r: -(min(r["y2025"]["pf"], 6.0) * (r["y2025"]["wr"] / 100.0) * math.sqrt(r["y2025"]["trades"]))
        )
        master_list: List[Dict[str, Any]] = []
        ind_cnt = Counter()
        for r in wf_cands:
            if len(master_list) >= 30:
                break
            if ind_cnt[r["industry"]] >= 4:
                continue
            master_list.append(r)
            ind_cnt[r["industry"]] += 1

        master_syms = {r["sym"] for r in master_list}
        ml_25 = _aggregate_universe_stats(master_list, "y2025")
        ml_26_oos = _aggregate_universe_stats(master_list, "y2026")

        print(f"\n--- STRATEGY: {st_name} ---")
        print(f"  FULL UNIVERSE 2025     : {all_25['stocks_profitable']}/{all_25['stocks_active']} stocks green ({all_25['pct_stocks_profitable']}%) | {all_25['total_trades']} tr | AvgWR {all_25['avg_wr_pct']}% | Mean/stock Rs {all_25['mean_net_per_stock']:+,.0f} | Median Rs {all_25['median_net_per_stock']:+,.0f} | Avg/tr Rs {all_25['avg_net_per_trade']:+,.0f}")
        print(f"  FULL UNIVERSE 2026     : {all_26['stocks_profitable']}/{all_26['stocks_active']} stocks green ({all_26['pct_stocks_profitable']}%) | {all_26['total_trades']} tr | AvgWR {all_26['avg_wr_pct']}% | Mean/stock Rs {all_26['mean_net_per_stock']:+,.0f} | Median Rs {all_26['median_net_per_stock']:+,.0f} | Avg/tr Rs {all_26['avg_net_per_trade']:+,.0f}")
        print(f"  2025 MASTER LIST (n={len(master_list):<2}) [IN-SAMPLE 2025] : {ml_25['stocks_profitable']}/{ml_25['stocks_active']} green ({ml_25['pct_stocks_profitable']}%) | {ml_25['total_trades']} tr | AvgWR {ml_25['avg_wr_pct']}% | Mean/stock Rs {ml_25['mean_net_per_stock']:+,.0f} | Avg/tr Rs {ml_25['avg_net_per_trade']:+,.0f}")
        print(f"  2025 MASTER LIST (n={len(master_list):<2}) [BLIND 2026 OOS] : {ml_26_oos['stocks_profitable']}/{ml_26_oos['stocks_active']} green ({ml_26_oos['pct_stocks_profitable']}%) | {ml_26_oos['total_trades']} tr | AvgWR {ml_26_oos['avg_wr_pct']}% | Mean/stock Rs {ml_26_oos['mean_net_per_stock']:+,.0f} | Avg/tr Rs {ml_26_oos['avg_net_per_trade']:+,.0f}")
        if master_list:
            print("  Top 10 Walk-Forward Master List (frozen end-2025 -> blind 2026 OOS):")
            for r in master_list[:10]:
                print(
                    f"    {r['sym']:<13} [{r['index_bucket']:<12} | {r['industry'][:16]:<16}] "
                    f"2025: {r['y2025']['trades']:>2}tr WR {r['y2025']['wr']:>5.1f}% Net Rs {r['y2025']['net']:>+8,.0f} | "
                    f"BLIND 2026: {r['y2026']['trades']:>2}tr WR {r['y2026']['wr']:>5.1f}% Net Rs {r['y2026']['net']:>+8,.0f}"
                )

        # Write full per-stock CSV scorecard
        csv_p = root / f"liquid_master_list_{st_name.lower()}_{universe_name}.csv"
        with open(csv_p, "w", newline="") as f:
            cols = [
                "sym", "company", "index_bucket", "industry", "in_wf_master_list",
                "tr_2025", "wr_2025", "pf_2025", "net_2025", "worst_2025",
                "tr_2026", "wr_2026", "pf_2026", "net_2026", "worst_2026",
            ]
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in sorted(rows, key=lambda x: -(x["y2025"]["net"] + x["y2026"]["net"])):
                w.writerow({
                    "sym": r["sym"], "company": r["company"],
                    "index_bucket": r["index_bucket"], "industry": r["industry"],
                    "in_wf_master_list": "YES" if r["sym"] in master_syms else "NO",
                    "tr_2025": r["y2025"]["trades"], "wr_2025": r["y2025"]["wr"],
                    "pf_2025": r["y2025"]["pf"], "net_2025": r["y2025"]["net"],
                    "worst_2025": r["y2025"]["worst"],
                    "tr_2026": r["y2026"]["trades"], "wr_2026": r["y2026"]["wr"],
                    "pf_2026": r["y2026"]["pf"], "net_2026": r["y2026"]["net"],
                    "worst_2026": r["y2026"]["worst"],
                })
        full_report["strategies"][st_name] = {
            "full_universe_2025": all_25, "full_universe_2026": all_26,
            "wf_master_list_size": len(master_list),
            "wf_master_2025_in_sample": ml_25,
            "wf_master_2026_blind_oos": ml_26_oos,
            "wf_master_symbols": [r["sym"] for r in master_list],
            "csv_path": str(csv_p),
        }

    rep_p = root / f"liquid_master_report_{universe_name}.json"
    rep_p.write_text(json.dumps(full_report, indent=2))
    print(f"\nSaved full JSON report -> {rep_p}")
    return 0


# ---------------------------------------------------------------------------
# 4. Backfill All Liquid NSE Stocks (Daily OHLCV 2024-2026) & Live Leaders Scan
# ---------------------------------------------------------------------------
def run_backfill(root: Path, universe_name: str, sleep_s: float = 0.25) -> int:
    uni = load_liquid_universe(root, universe_name)
    token = P1._load_token(root)
    ikeys = P1.load_instrument_keys(root)
    today_s = datetime.now(IST).strftime("%Y-%m-%d")

    st_n, _ = P1.refresh_daily_symbol(root, "NIFTY", NIFTY_KEY, today_s, token, lookback_days=760)
    print(f"[BACKFILL] NIFTY -> {st_n}", flush=True)
    time.sleep(sleep_s)

    done = missing_key = 0
    for idx, u in enumerate(uni, 1):
        sym = u["sym"]
        ik = ikeys.get(sym)
        if not ik:
            missing_key += 1
            continue
        st, added = P1.refresh_daily_symbol(root, sym, ik, today_s, token, lookback_days=760)
        done += 1
        if idx % 20 == 0 or idx == len(uni):
            print(f"[BACKFILL] {idx}/{len(uni)} ({sym}: {st}, +{added})", flush=True)
        if st != "UP_TO_DATE":
            time.sleep(sleep_s)
    print(f"Backfill complete: {done} synced, {missing_key} missing instrument keys.")
    return 0


def run_live_leaders(root: Path, universe_name: str, top_n: int = 15) -> int:
    """Scan ALL ~200 liquid NSE stocks in ~4 batched API calls and rank TODAY'S
    real-time Relative Strength outperformers (LONG) & underperformers (SHORT)."""
    uni = load_liquid_universe(root, universe_name)
    umeta = {u["sym"]: u for u in uni}
    token = P1._load_token(root)
    ikeys = P1.load_instrument_keys(root)

    # Fetch Nifty 50 % change first
    nf_q = P1._api_get(f"/v2/market-quote/quotes?instrument_key={urllib.parse.quote(NIFTY_KEY, safe='')}", token)
    nf_data = next(iter((nf_q.get("data") or {}).values()), {})
    nf_ltp = float(nf_data.get("last_price") or 0.0)
    nf_prev = float((nf_data.get("ohlc") or {}).get("close") or nf_ltp)
    nf_chg = ((nf_ltp - nf_prev) / nf_prev) * 100.0 if nf_prev > 0 else 0.0

    key_to_sym = {ikeys[u["sym"]]: u["sym"] for u in uni if u["sym"] in ikeys}
    tsym_to_sym = {u["sym"]: u["sym"] for u in uni}
    keys = list(key_to_sym.keys())

    scored: List[Dict[str, Any]] = []
    for start in range(0, len(keys), 50):
        batch = keys[start : start + 50]
        joined = urllib.parse.quote(",".join(batch), safe=",")
        payload = P1._api_get(f"/v2/market-quote/quotes?instrument_key={joined}", token)
        for _rk, q in (payload.get("data") or {}).items():
            if not isinstance(q, dict):
                continue
            ik = q.get("instrument_token") or q.get("instrument_key") or ""
            sym = key_to_sym.get(ik) or tsym_to_sym.get((q.get("symbol") or "").strip())
            if not sym:
                continue
            ltp = float(q.get("last_price") or 0.0)
            ohlc = q.get("ohlc") or {}
            prev_c = float(ohlc.get("close") or ltp)
            hi, lo = float(ohlc.get("high") or ltp), float(ohlc.get("low") or ltp)
            atp = float(q.get("average_price") or ltp)
            vol = float(q.get("volume") or 0.0)
            if ltp <= 0 or prev_c <= 0:
                continue
            chg_pct = ((ltp - prev_c) / prev_c) * 100.0
            rs_pct = chg_pct - nf_chg
            vs_vwap_pct = ((ltp - atp) / atp) * 100.0 if atp > 0 else 0.0
            pos_in_day = ((ltp - lo) / (hi - lo)) * 100.0 if hi > lo else 50.0
            turnover_cr = (ltp * vol) / 1e7
            if turnover_cr < 5.0:  # minimum Rs 5 Cr intraday liquidity guard!
                continue
            scored.append({
                "sym": sym, "bucket": umeta[sym]["index_bucket"],
                "industry": umeta[sym]["industry"],
                "ltp": round(ltp, 2), "chg_pct": round(chg_pct, 2),
                "rs_vs_nifty": round(rs_pct, 2), "vs_vwap_pct": round(vs_vwap_pct, 2),
                "day_pos_pct": round(pos_in_day, 1), "turnover_cr": round(turnover_cr, 1),
            })
        time.sleep(0.25)

    longs = sorted(
        [s for s in scored if s["vs_vwap_pct"] > 0 and s["day_pos_pct"] >= 65.0],
        key=lambda x: -x["rs_vs_nifty"],
    )[:top_n]
    shorts = sorted(
        [s for s in scored if s["vs_vwap_pct"] < 0 and s["day_pos_pct"] <= 35.0],
        key=lambda x: x["rs_vs_nifty"],
    )[:top_n]

    print(f"\n================ LIVE LIQUID OUTPERFORMERS ({datetime.now(IST).strftime('%H:%M:%S IST')}) ================")
    print(f"Universe: {universe_name} ({len(scored)} liquid stocks >= Rs 5 Cr turnover) | Nifty 50: {nf_ltp:.2f} ({nf_chg:+.2f}%)")
    print(f"\nTOP {len(longs)} LIQUID OUTPERFORMERS (LONG — Above VWAP, Near Day High, Beating Nifty):")
    for s in longs:
        print(f"  {s['sym']:<13} [{s['bucket']:<12}] LTP {s['ltp']:>8.2f} | Chg {s['chg_pct']:>+6.2f}% | RS {s['rs_vs_nifty']:>+6.2f}% | >VWAP {s['vs_vwap_pct']:>+5.2f}% | Vol Rs {s['turnover_cr']:>6.1f}Cr | {s['industry']}")
    print(f"\nTOP {len(shorts)} LIQUID UNDERPERFORMERS (SHORT — Below VWAP, Near Day Low, Lagging Nifty):")
    for s in shorts:
        print(f"  {s['sym']:<13} [{s['bucket']:<12}] LTP {s['ltp']:>8.2f} | Chg {s['chg_pct']:>+6.2f}% | RS {s['rs_vs_nifty']:>+6.2f}% | <VWAP {s['vs_vwap_pct']:>+5.2f}% | Vol Rs {s['turnover_cr']:>6.1f}Cr | {s['industry']}")
    out_p = root / "data" / "live_liquid_leaders.json"
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "updated_at": datetime.now(IST).isoformat(), "nifty_ltp": nf_ltp, "nifty_chg_pct": round(nf_chg, 2),
        "longs": longs, "shorts": shorts,
    }, indent=2))
    return 0


def run_selftest() -> int:
    print("=== LIQUID MASTER-LIST BUILDER SELF-TEST ===")
    uni = load_liquid_universe(THIS_DIR, "nifty200")
    assert len(uni) >= 180, f"Expected ~200 liquid NSE stocks, got {len(uni)}"
    syms = {u["sym"] for u in uni}
    assert {"HDFCBANK", "RELIANCE", "ICICIBANK", "SBIN", "INFY"}.issubset(syms)

    # Synthetic 2-year stock (2025 + 2026) with clean dips + RS breakout surge
    dates = [(ddate(2025, 1, 1) + timedelta(days=i)).isoformat() for i in range(520)]
    c = [1000.0 + i * 0.5 for i in range(520)]
    for dip_start in (60, 180, 390, 460):
        for k in range(6):
            c[dip_start + k] -= (k + 1) * 24.0
        c[dip_start + 6] = c[dip_start + 5] + 30.0
    for k in range(20):
        c[250 + k] += (k + 1) * 8.0  # strong 20d breakout outperforming Nifty!
    o = [c[0]] + [c[i - 1] for i in range(1, len(c))]
    h = [max(o[i], c[i]) * 1.005 for i in range(len(c))]
    l = [min(o[i], c[i]) * 0.995 for i in range(len(c))]
    nf = {d: 24000.0 + i * 2.0 for i, d in enumerate(dates)}

    tr_e = simulate_stock_ekam2c_s0("TESTSTK", dates, o, h, l, c)
    tr_r = simulate_stock_rs_trend("TESTSTK", dates, o, h, l, c, nf)
    assert len(tr_e) >= 2 and all(t["cost_inr"] > 100.0 for t in tr_e), tr_e
    assert len(tr_r) >= 1 and all(t["cost_inr"] > 100.0 for t in tr_r), tr_r
    print(f"  OK  Loaded {len(uni)} liquid NSE stocks from sapta_constituents/ (Nifty 50 + Next 50 + Bank + Midcap 100)")
    print(f"  OK  EKAM2C_S0 simulated {len(tr_e)} trades (realistic delivery costs); RS_TREND_20D simulated {len(tr_r)} trades")
    print("LIQUID MASTER-LIST BUILDER SELF-TEST PASSED!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "backfill", "evaluate", "live-leaders"), default="evaluate")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--universe", choices=("nifty50", "niftybank", "nifty100", "nifty200", "nifty250"), default="nifty200")
    ap.add_argument("--strategy", choices=("EKAM2C_S0", "RS_TREND_20D", "BOTH"), default="BOTH")
    ap.add_argument("--capital-per-trade", type=float, default=100_000.0)
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args(argv)

    if a.mode == "selftest":
        return run_selftest()
    root = Path(a.root)
    if a.mode == "backfill":
        return run_backfill(root, a.universe)
    if a.mode == "live-leaders":
        return run_live_leaders(root, a.universe, top_n=a.top)
    return run_evaluate(root, a.universe, strategy=a.strategy, capital_per_trade=a.capital_per_trade)


if __name__ == "__main__":
    sys.exit(main())
