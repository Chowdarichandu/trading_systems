#!/usr/bin/env python3
"""PILLAR 1 (OPTION A) — Quality Value x EKAM Daily 2c Swing Engine.

Combines the locked fundamental Value Screener v2 universe (Tier A + clean
Tier B from investing_value_analysis_2026-11-14.csv) with the EKAM Daily 2c
daily swing engine (BB lower-band return + RSI-14 oversold turn + RSI-upgrade
rule), upgraded with the structural fixes from AUDIT_AND_FIXES_2026-11-25.md:

  1. Fixed-capital equal-rupee sizing (default Rs 1,00,000/trade) via
     execution_risk_utils.fixed_capital_qty — eliminates 32x price distortion.
  2. Realistic NSE delivery transaction costs + 5 bps/side slippage via
     execution_risk_utils.equity_delivery_cost (~0.20% STT + DP + GST + slip).
  3. Portfolio-level risk caps: max concurrent positions (default 8) and
     sector concentration cap (default max 3 per sector), with quality/oversold
     tie-breaking (zero alphabetical bias).
  4. Nifty 50 200-DMA macro regime scaler: 100% sizing when Nifty >= 200-DMA,
     50% sizing (defensive) when Nifty < 200-DMA (or 0% with --strict-regime).
  5. Gap-aware 3.0x Daily ATR(14) catastrophe stop below entry.
  6. Same-day Upstox v3 intraday synthesis fallback when Upstox's daily candle
     endpoint lags by 1 day (solves ekam_daily_feed_diagnosis_2026-11-18.md).

PAPER ONLY. Real money Rs 0. Places ZERO broker orders.

Usage:
  # Run offline deterministic self-test (no API / local stores required)
  python3 pillar1_value_ekam_swing.py --mode selftest

  # Run full historical backtest on live machine local daily stores
  python3 pillar1_value_ekam_swing.py --mode backtest --universe tier_ab
  python3 pillar1_value_ekam_swing.py --mode backtest --universe ekam25

  # Run daily EOD paper scan (after 15:35 IST) with live Upstox refresh
  python3 pillar1_value_ekam_swing.py --mode live --universe tier_ab
  python3 pillar1_value_ekam_swing.py --mode live --no-refresh --dry-run
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
NIFTY_INDEX_KEY = "NSE_INDEX|Nifty 50"

EKAM25_NAMES = (
    "ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR "
    "HINDZINC INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY "
    "OIL PFC RECLTD TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO"
).split()

BAD_TIER_B_FLAGS = (
    "no 3Y profit growth",
    "insurer",
    "holding-company",
    "thin free float",
    "promoter/sponsor holding declining",
    "cyclical earnings",
    "small cap",
)

# Explicit sector map for Tier A, Clean Tier B, and EKAM-25 names (prevents
# loading 8 financial stocks simultaneously when banks pull back together).
SECTOR_MAP: Dict[str, str] = {
    # Private & PSU Banks
    "HDFCBANK": "BANK", "ICICIBANK": "BANK", "SBIN": "BANK", "AXISBANK": "BANK",
    "KOTAKBANK": "BANK", "INDIANB": "BANK", "CANBK": "BANK", "BANKINDIA": "BANK",
    "CUB": "BANK", "J&KBANK": "BANK", "PNB": "BANK", "UNIONBANK": "BANK",
    "BANKBARODA": "BANK", "FEDERALBNK": "BANK", "KARURVYSYA": "BANK",
    "SOUTHBANK": "BANK", "TMB": "BANK", "CSBBANK": "BANK", "IDBI": "BANK",
    "UCOBANK": "BANK", "CENTRALBK": "BANK", "MAHABANK": "BANK",
    # NBFC / Housing Finance / Infra Finance
    "PFC": "NBFC_FIN", "RECLTD": "NBFC_FIN", "M&MFIN": "NBFC_FIN",
    "HUDCO": "NBFC_FIN", "LICHSGFIN": "NBFC_FIN", "PNBHOUSING": "NBFC_FIN",
    "CANFINHOME": "NBFC_FIN", "SHRIRAMFIN": "NBFC_FIN", "MUTHOOTFIN": "NBFC_FIN",
    "IRFC": "NBFC_FIN", "HDBFS": "NBFC_FIN", "JMFINANCIL": "NBFC_FIN",
    "AAVAS": "NBFC_FIN", "AADHARHFC": "NBFC_FIN", "CHOLAHLDNG": "NBFC_FIN",
    # Energy / Utilities / Power
    "GAIL": "ENERGY_UTIL", "PETRONET": "ENERGY_UTIL", "ONGC": "ENERGY_UTIL",
    "IOC": "ENERGY_UTIL", "BPCL": "ENERGY_UTIL", "OIL": "ENERGY_UTIL",
    "NTPC": "ENERGY_UTIL", "NHPC": "ENERGY_UTIL", "PTC": "ENERGY_UTIL",
    # Metals / Mining
    "HINDALCO": "METALS", "HINDCOPPER": "METALS", "HINDZINC": "METALS",
    "NATIONALUM": "METALS", "TATASTEEL": "METALS", "VEDL": "METALS",
    "SAIL": "METALS",
    # Pharma / Healthcare
    "GLENMARK": "PHARMA", "NATCOPHARM": "PHARMA", "FDC": "PHARMA",
    # Auto / Tyres / Industrials / Defence
    "APOLLOTYRE": "AUTO_IND", "TVSMOTOR": "AUTO_IND", "BDL": "AUTO_IND",
    "ASTRAL": "AUTO_IND", "TIMETECHNO": "AUTO_IND", "LGBBROSLTD": "AUTO_IND",
    "TCI": "AUTO_IND",
    # IT / Tech / Distribution
    "WIPRO": "TECH", "ZENSARTECH": "TECH", "REDINGTON": "TECH",
    "SAGILITY": "TECH",
    # Consumer / FMCG / Realty / Telecom
    "GODREJCP": "CONSUMER", "HINDUNILVR": "CONSUMER", "ITC": "CONSUMER",
    "UNITDSPR": "CONSUMER", "KALYANKJIL": "CONSUMER", "AWL": "CONSUMER",
    "IRCTC": "CONSUMER", "OBEROIRLTY": "REALTY", "INDUSTOWER": "TELECOM",
}

PAPER_LOG_FIELDS = [
    "trade_key", "universe", "sym", "tier", "sector", "comps",
    "signal_date", "entry_date", "exit_date", "qty", "entry_price",
    "exit_price", "stop_price", "hold_days", "exit_kind", "upgraded",
    "regime_mult", "gross_inr", "cost_inr", "net_inr", "notes",
]


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "data").exists():
        return live
    return THIS_DIR


def sector_of(sym: str) -> str:
    return SECTOR_MAP.get(sym.upper(), "OTHER")


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(str(x).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Universe Loader
# ---------------------------------------------------------------------------
def load_universe(root: Path, universe: str) -> List[Dict[str, Any]]:
    """Return ordered list of universe dicts: {sym, tier, sector, mcap_cr}."""
    val_csv = root / "investing_value_analysis_2026-11-14.csv"
    if not val_csv.exists():
        val_csv = THIS_DIR / "investing_value_analysis_2026-11-14.csv"
    val_rows: Dict[str, Dict[str, Any]] = {}
    if val_csv.exists():
        with open(val_csv, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                val_rows[r["Ticker"].strip()] = {
                    "sym": r["Ticker"].strip(),
                    "tier": r["Tier"].strip(),
                    "reason": r.get("Reason", ""),
                    "sector": sector_of(r["Ticker"].strip()),
                    "mcap_cr": _safe_float(r.get("MarketCap_Cr"), 0.0),
                }

    u = universe.lower()
    if u == "ekam25":
        return [
            {
                "sym": s,
                "tier": val_rows.get(s, {}).get("tier", "EKAM25"),
                "sector": sector_of(s),
                "mcap_cr": val_rows.get(s, {}).get("mcap_cr", 10000.0),
            }
            for s in EKAM25_NAMES
        ]

    out: List[Dict[str, Any]] = []
    for sym, info in val_rows.items():
        if info["tier"] == "A":
            out.append(info)
        elif u in ("tier_ab", "value_all") and info["tier"] == "B":
            if u == "value_all" or not any(
                bad in info["reason"] for bad in BAD_TIER_B_FLAGS
            ):
                out.append(info)
    out.sort(key=lambda x: (0 if x["tier"] == "A" else 1, -x["mcap_cr"], x["sym"]))
    return out


# ---------------------------------------------------------------------------
# Daily Store Loader + Upstox v3 Live Refresh (with same-day intraday synth)
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
            raise RateLimited(f"HTTP 429 rate limit on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def load_instrument_keys(root: Path) -> Dict[str, str]:
    """Resolve NSE_EQ symbol -> Upstox instrument_key from local caches or NSE.csv.gz."""
    keys: Dict[str, str] = {}
    uni = root / "universe_daily" / "universe.csv"
    if uni.exists():
        with open(uni, newline="") as f:
            for r in csv.DictReader(f):
                s = (r.get("symbol") or "").strip()
                k = (r.get("instrument_key") or "").strip()
                if s and k:
                    keys[s] = k

    master = root / "november_shadow_data" / "instruments_NSE.csv"
    if not master.exists():
        cache_dir = root / "data" / "pillar1_daily"
        cache_dir.mkdir(parents=True, exist_ok=True)
        master = cache_dir / "instruments_NSE.csv"
        stamp = cache_dir / "instruments_stamp.txt"
        today_s = datetime.now(IST).strftime("%Y-%m-%d")
        if not master.exists() or (stamp.exists() and stamp.read_text().strip() != today_s):
            try:
                req = urllib.request.Request(
                    INSTRUMENTS_URL,
                    headers={"Accept": "application/gzip", "User-Agent": UA},
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    master.write_bytes(gzip.decompress(r.read()))
                stamp.write_text(today_s)
            except Exception:
                pass
    if master.exists():
        with open(master, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("exchange") == "NSE_EQ" and r.get("instrument_type") == "EQUITY":
                    tsym = (r.get("tradingsymbol") or "").strip()
                    ikey = (r.get("instrument_key") or "").strip()
                    if tsym and ikey and tsym not in keys:
                        keys[tsym] = ikey
    return keys


def _read_daily_csv(path: Path) -> Dict[str, Tuple[float, float, float, float, str]]:
    out: Dict[str, Tuple[float, float, float, float, str]] = {}
    if not path.exists():
        return out
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            dt = (r.get("date") or r.get("timestamp") or "")[:10]
            if not dt:
                continue
            src = r.get("source") or "official"
            out[dt] = (
                float(r["open"]), float(r["high"]),
                float(r["low"]), float(r["close"]), src,
            )
    return out


def _agg_5m_to_daily(path: Path) -> Dict[str, Tuple[float, float, float, float, str]]:
    by_day: Dict[str, List[Tuple[str, float, float, float, float]]] = defaultdict(list)
    if not path.exists():
        return {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ts = r.get("timestamp") or ""
            if len(ts) < 16:
                continue
            by_day[ts[:10]].append(
                (ts[11:16], float(r["open"]), float(r["high"]),
                 float(r["low"]), float(r["close"]))
            )
    out: Dict[str, Tuple[float, float, float, float, str]] = {}
    for dt, bars in by_day.items():
        bars.sort(key=lambda x: x[0])
        out[dt] = (
            bars[0][1],
            max(b[2] for b in bars),
            min(b[3] for b in bars),
            bars[-1][4],
            "agg_5m",
        )
    return out


def load_daily_series(
    root: Path, sym: str
) -> Tuple[List[str], List[float], List[float], List[float], List[float]]:
    """Merge local daily stores for `sym`, preferring official bars over intraday_synth."""
    merged: Dict[str, Tuple[float, float, float, float, str]] = {}
    stores = (
        root / "data" / "full_hist" / sym / "spot_daily.csv",
        root / "data" / "sarvaritu_fwd" / sym / "spot_daily.csv",
        root / "data" / "progressive_ext" / sym / "spot_daily.csv",
        root / "data" / "progressive" / sym / "spot_daily.csv",
        root / "data" / "wide_nse_fwd" / sym / "spot_daily.csv",
        root / "data" / "pillar1_daily" / f"{sym}.csv",
    )
    for p in stores:
        for dt, rec in _read_daily_csv(p).items():
            prev = merged.get(dt)
            if prev is None or (prev[4] == "intraday_synth" and rec[4] != "intraday_synth"):
                merged[dt] = rec

    # Also merge ekam_daily_fwd_cache.json if present
    fwd_cache = root / "ekam_daily_fwd_cache.json"
    if fwd_cache.exists():
        try:
            fc = json.loads(fwd_cache.read_text()).get(sym) or {}
            for dt, ohlc in fc.items():
                if dt not in merged and len(ohlc) >= 4:
                    merged[dt] = (
                        float(ohlc[0]), float(ohlc[1]),
                        float(ohlc[2]), float(ohlc[3]), "fwd_cache",
                    )
        except Exception:
            pass

    # Fallback: aggregate 5-min bars if no daily store existed
    if not merged:
        for p5 in (
            root / "data" / "progressive" / sym / "spot_5m.csv",
            root / "data" / "sarvaritu_fwd" / sym / "spot_5m.csv",
        ):
            for dt, rec in _agg_5m_to_daily(p5).items():
                merged.setdefault(dt, rec)

    dates = sorted(merged)
    o = [merged[d][0] for d in dates]
    h = [merged[d][1] for d in dates]
    l = [merged[d][2] for d in dates]
    c = [merged[d][3] for d in dates]
    return dates, o, h, l, c


def refresh_daily_symbol(
    root: Path,
    sym: str,
    instrument_key: str,
    target_date: str,
    token: str,
    lookback_days: int = 420,
) -> Tuple[str, int]:
    """Fetch missing daily candles via Upstox v3 + same-day intraday 5m synthesis."""
    p = root / "data" / "pillar1_daily" / f"{sym}.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_daily_csv(p)
    # Also check longest local store so we don't re-fetch 420 days unnecessarily
    dates_loc, o_loc, h_loc, l_loc, c_loc = load_daily_series(root, sym)
    for d, oo, hh, ll, cc in zip(dates_loc, o_loc, h_loc, l_loc, c_loc):
        existing.setdefault(d, (oo, hh, ll, cc, "official"))

    non_synth = [d for d, rec in existing.items() if rec[4] != "intraday_synth"]
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    if non_synth and max(non_synth) >= target_date:
        return "UP_TO_DATE", len(existing)

    if non_synth:
        frm = (ddate.fromisoformat(max(non_synth)) - timedelta(days=3)).isoformat()
    else:
        frm = (ddate.fromisoformat(target_date) - timedelta(days=lookback_days)).isoformat()

    enc = urllib.parse.quote(instrument_key, safe="")
    payload = _api_get(f"/v3/historical-candle/{enc}/days/1/{target_date}/{frm}", token)
    candles = (payload.get("data") or {}).get("candles") or []
    added = 0
    for row in candles:
        dt = str(row[0])[:10]
        if dt <= target_date:
            existing[dt] = (
                float(row[1]), float(row[2]),
                float(row[3]), float(row[4]), "official",
            )
            added += 1

    # FIX for Upstox 1-day daily-candle lag: synthesize today from v3 intraday 5m
    status = "OFFICIAL"
    if target_date == today_s and (
        target_date not in existing or existing[target_date][4] == "intraday_synth"
    ):
        time.sleep(0.25)
        ip = _api_get(f"/v3/historical-candle/intraday/{enc}/minutes/5", token)
        ic = [
            r for r in ((ip.get("data") or {}).get("candles") or [])
            if str(r[0])[:10] == target_date
        ]
        if ic:
            ic.sort(key=lambda r: str(r[0]))
            existing[target_date] = (
                float(ic[0][1]),
                max(float(r[2]) for r in ic),
                min(float(r[3]) for r in ic),
                float(ic[-1][4]),
                "intraday_synth",
            )
            status = "INTRADAY_SYNTH"
            added += 1
        elif target_date not in existing:
            status = "MISSING_TODAY"

    # Atomic write to data/pillar1_daily/{sym}.csv
    tmp = p.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "source"])
        for d in sorted(existing):
            oo, hh, ll, cc, src = existing[d]
            w.writerow([d, f"{oo:.4f}", f"{hh:.4f}", f"{ll:.4f}", f"{cc:.4f}", src])
    os.replace(tmp, p)
    return status, added


# ---------------------------------------------------------------------------
# Causal Daily Indicators (pure Python / stdlib — zero external dependency)
# ---------------------------------------------------------------------------
def compute_indicators(
    dates: Sequence[str],
    o: Sequence[float],
    h: Sequence[float],
    l: Sequence[float],
    c: Sequence[float],
) -> Dict[str, Any]:
    n = len(c)
    mid: List[Optional[float]] = [None] * n
    lower: List[Optional[float]] = [None] * n
    upper: List[Optional[float]] = [None] * n
    pctb: List[Optional[float]] = [None] * n
    for i in range(19, n):
        win = c[i - 19 : i + 1]
        m = sum(win) / 20.0
        var = max(sum((x - m) ** 2 for x in win) / 20.0, 0.0)
        sd = math.sqrt(var)
        mid[i] = m
        lower[i] = m - 2.0 * sd
        upper[i] = m + 2.0 * sd
        rng = upper[i] - lower[i]
        pctb[i] = (c[i] - lower[i]) / rng if rng > 0 else 0.5

    # Wilder RSI(14)
    rsi: List[Optional[float]] = [None] * n
    if n > 14:
        gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
        losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
        ag = sum(gains[:14]) / 14.0
        al = sum(losses[:14]) / 14.0
        rsi[14] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
        for i in range(14, len(gains)):
            ag = (ag * 13.0 + gains[i]) / 14.0
            al = (al * 13.0 + losses[i]) / 14.0
            rsi[i + 1] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)

    # Wilder ATR(14)
    atr: List[Optional[float]] = [None] * n
    if n > 14:
        tr = [h[0] - l[0]]
        for i in range(1, n):
            tr.append(
                max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
            )
        val = sum(tr[:14]) / 14.0
        atr[13] = val
        for i in range(14, n):
            val = (val * 13.0 + tr[i]) / 14.0
            atr[i] = val

    # EKAM-2c entry & close signals (verbatim ekam_build.py)
    sig_bb_in = [False] * n
    sig_rsi_in = [False] * n
    sig_bb_out = [False] * n
    sig_rsi_out = [False] * n
    for i in range(n):
        if mid[i] is not None and c[i] >= mid[i]:
            sig_bb_out[i] = True
        if rsi[i] is not None and rsi[i] >= 70.0:
            sig_rsi_out[i] = True
        if i >= 1:
            if (
                lower[i - 1] is not None
                and lower[i] is not None
                and c[i - 1] < lower[i - 1]
                and c[i] >= lower[i]
            ):
                sig_bb_in[i] = True
            if (
                rsi[i - 1] is not None
                and rsi[i] is not None
                and rsi[i - 1] <= 30.0
                and rsi[i] > 30.0
            ):
                sig_rsi_in[i] = True

    return {
        "dates": list(dates),
        "idx": {d: i for i, d in enumerate(dates)},
        "o": list(o), "h": list(h), "l": list(l), "c": list(c), "n": n,
        "mid": mid, "lower": lower, "upper": upper, "pctb": pctb,
        "rsi": rsi, "atr": atr,
        "sig_in": {"BB": sig_bb_in, "RSI": sig_rsi_in},
        "sig_out": {"BB": sig_bb_out, "RSI": sig_rsi_out},
    }


def compute_nifty_regime(
    dates: Sequence[str], closes: Sequence[float], sma_window: int = 200
) -> Dict[str, Dict[str, Any]]:
    """Map date -> {close, sma200, above_200dma} strictly causally."""
    out: Dict[str, Dict[str, Any]] = {}
    n = len(closes)
    for i in range(n):
        if i + 1 >= sma_window:
            s200 = sum(closes[i + 1 - sma_window : i + 1]) / float(sma_window)
            out[dates[i]] = {
                "close": closes[i],
                "sma200": round(s200, 2),
                "above_200dma": closes[i] >= s200,
            }
        else:
            out[dates[i]] = {
                "close": closes[i],
                "sma200": None,
                "above_200dma": True,  # neutral default until 200 bars exist
            }
    return out


# ---------------------------------------------------------------------------
# Chronological Portfolio Backtest Engine (Pillar 1 vs Legacy Ablation)
# ---------------------------------------------------------------------------
def simulate_portfolio(
    series_map: Dict[str, Dict[str, Any]],
    meta_map: Dict[str, Dict[str, Any]],
    nifty_regime: Dict[str, Dict[str, Any]],
    *,
    capital_per_trade: float = 100_000.0,
    fixed_shares: Optional[int] = None,
    max_positions: int = 8,
    max_per_sector: int = 3,
    atr_stop_mult: float = 3.0,
    use_regime: bool = True,
    strict_regime: bool = False,
    realistic_costs: bool = True,
    slippage_bps_per_side: float = 5.0,
    flat_cost_inr: float = 40.0,
) -> Dict[str, Any]:
    """Chronological day-by-day simulation of EKAM Daily 2c with portfolio risk caps."""
    all_dates = sorted({d for s in series_map.values() for d in s["dates"]})
    # Open positions: sym -> pos dict
    positions: Dict[str, Dict[str, Any]] = {}
    # Pending next-open actions scheduled on prior close
    pending_exits: Dict[str, str] = {}            # sym -> exit_kind
    pending_entries: List[Dict[str, Any]] = []    # ranked list of candidate dicts
    closed_trades: List[Dict[str, Any]] = []
    skipped_counts = Counter()

    def _close_pos(sym: str, pos: Dict[str, Any], exit_date: str, exit_px: float,
                   exit_kind: str, hold_days: int) -> None:
        qty = pos["qty"]
        entry_px = pos["entry_px"]
        gross = (exit_px - entry_px) * qty
        if realistic_costs:
            cost_d = ERU.equity_delivery_cost(
                entry_px, exit_px, qty,
                slippage_bps_per_side=slippage_bps_per_side,
            )
            cost_inr = cost_d["total_cost_inr"]
        else:
            cost_inr = flat_cost_inr
        net = round(gross - cost_inr, 2)
        closed_trades.append({
            "sym": sym,
            "tier": meta_map[sym]["tier"],
            "sector": meta_map[sym]["sector"],
            "comps": "+".join(pos["comps"]),
            "signal_date": pos["signal_date"],
            "entry_date": pos["entry_date"],
            "exit_date": exit_date,
            "qty": qty,
            "deployed_inr": round(entry_px * qty, 2),
            "entry_price": round(entry_px, 4),
            "exit_price": round(exit_px, 4),
            "stop_price": round(pos["stop_px"], 4) if pos["stop_px"] is not None else None,
            "hold_days": hold_days,
            "exit_kind": exit_kind,
            "upgraded": pos["upgraded"],
            "regime_mult": pos["regime_mult"],
            "gross_inr": round(gross, 2),
            "cost_inr": round(cost_inr, 2),
            "net_inr": net,
            "forced": exit_kind == "FORCED",
        })

    for day in all_dates:
        # 1. Execute pending next-open EXITS scheduled on previous close
        for sym in list(pending_exits.keys()):
            if sym not in positions:
                pending_exits.pop(sym, None)
                continue
            sd = series_map[sym]
            idx = sd["idx"].get(day)
            if idx is None:
                continue
            why = pending_exits.pop(sym)
            pos = positions.pop(sym)
            hold = idx - pos["entry_idx"]
            _close_pos(sym, pos, day, sd["o"][idx], why, hold)

        # 2. Execute pending next-open ENTRIES scheduled on previous close
        if pending_entries:
            sec_counts = Counter(meta_map[s]["sector"] for s in positions)
            next_pending: List[Dict[str, Any]] = []
            for cand in pending_entries:
                sym = cand["sym"]
                if sym in positions:
                    continue
                sd = series_map[sym]
                idx = sd["idx"].get(day)
                if idx is None:
                    continue
                if len(positions) >= max_positions:
                    skipped_counts["max_positions"] += 1
                    continue
                sec = meta_map[sym]["sector"]
                if sec_counts[sec] >= max_per_sector:
                    skipped_counts["sector_cap"] += 1
                    continue
                entry_px = sd["o"][idx]
                if entry_px <= 0:
                    continue
                rmult = cand["regime_mult"]
                if rmult <= 0.0:
                    skipped_counts["regime_blocked"] += 1
                    continue
                if fixed_shares is not None:
                    qty = fixed_shares
                else:
                    qty = ERU.fixed_capital_qty(entry_px, capital_per_trade * rmult)
                if qty <= 0:
                    continue
                stop_px = None
                if atr_stop_mult > 0 and cand["sig_atr"] is not None:
                    stop_px = max(entry_px - atr_stop_mult * cand["sig_atr"], 0.05)
                positions[sym] = {
                    "entry_idx": idx,
                    "entry_date": day,
                    "entry_px": entry_px,
                    "qty": qty,
                    "comps": cand["comps"],
                    "signal_date": cand["signal_date"],
                    "upgraded": False,
                    "up_idx": None,
                    "stop_px": stop_px,
                    "regime_mult": rmult,
                }
                sec_counts[sec] += 1
            pending_entries = next_pending

        # 3. Evaluate intraday / close rules on all open positions
        for sym in list(positions.keys()):
            sd = series_map[sym]
            idx = sd["idx"].get(day)
            if idx is None:
                continue
            pos = positions[sym]
            e = pos["entry_idx"]
            E = pos["entry_px"]
            comps = pos["comps"]
            o_i, h_i, l_i, c_i = sd["o"][idx], sd["h"][idx], sd["l"][idx], sd["c"][idx]
            hold = idx - e

            # EKAM-2c RSI upgrade on pure-BB position
            converted_today = False
            if comps == ("BB",) and not pos["upgraded"] and sd["sig_in"]["RSI"][idx]:
                pos["upgraded"] = True
                pos["up_idx"] = idx
                converted_today = True

            # Intraday exits (TIME60 -> ATR catastrophe stop -> CAP +10%)
            use_rsi_stack = ("RSI" in comps) or (comps == ("BB",) and pos["upgraded"])
            allow_time_cap = (
                ("RSI" in comps)
                or (comps == ("BB",) and pos["upgraded"] and not converted_today)
            )

            done_now: Optional[Tuple[float, str]] = None
            if allow_time_cap and hold >= 60 and idx > e:
                done_now = (o_i, "TIME")

            if done_now is None and pos["stop_px"] is not None and idx >= e:
                stp = pos["stop_px"]
                if o_i <= stp:
                    done_now = (o_i, "STOP_GAP")
                elif l_i <= stp:
                    done_now = (stp, "STOP_ATR")

            if done_now is None and allow_time_cap and idx >= e:
                lvl = E * 1.10
                if h_i >= lvl:
                    done_now = (o_i if o_i >= lvl else lvl, "CAP")

            if done_now is not None:
                positions.pop(sym)
                _close_pos(sym, pos, day, done_now[0], done_now[1], hold)
                continue

            # Close signal exits -> scheduled for NEXT trading day's open
            fire: Optional[str] = None
            if comps == ("BB",) and pos["upgraded"]:
                if sd["sig_out"]["RSI"][idx]:
                    fire = "SIGNAL-RSI"
            elif "RSI" in comps:
                for k in comps:
                    if sd["sig_out"][k][idx]:
                        fire = f"SIGNAL-{k}"
                        break
            else:
                if sd["sig_out"]["BB"][idx]:
                    fire = "SIGNAL-BB"

            if fire is not None:
                pending_exits[sym] = fire

        # 4. Scan for new close-confirmed entries -> scheduled for NEXT open
        reg = nifty_regime.get(day)
        above_200 = reg["above_200dma"] if reg else True
        if not use_regime or above_200:
            rmult = 1.0
        else:
            rmult = 0.0 if strict_regime else 0.5

        day_cands: List[Dict[str, Any]] = []
        for sym, sd in series_map.items():
            if sym in positions:
                continue
            idx = sd["idx"].get(day)
            if idx is None:
                continue
            sigs = tuple(k for k in ("BB", "RSI") if sd["sig_in"][k][idx])
            if not sigs:
                continue
            r_val = sd["rsi"][idx] if sd["rsi"][idx] is not None else 50.0
            pb_val = sd["pctb"][idx] if sd["pctb"][idx] is not None else 0.5
            # Quality + oversold depth rank (NO alphabetical selection bias!)
            tier_rank = 0 if meta_map[sym]["tier"] == "A" else 1
            oversold_score = (35.0 - r_val) + (1.0 - pb_val) * 20.0
            day_cands.append({
                "sym": sym,
                "comps": sigs,
                "signal_date": day,
                "sig_atr": sd["atr"][idx],
                "regime_mult": rmult,
                "sort_key": (tier_rank, -oversold_score, -meta_map[sym]["mcap_cr"]),
            })
        day_cands.sort(key=lambda x: x["sort_key"])
        pending_entries = day_cands

    # Mark remaining open positions at final close (forced for backtest accounting)
    open_final = []
    for sym, pos in positions.items():
        sd = series_map[sym]
        last_i = sd["n"] - 1
        last_d = sd["dates"][last_i]
        last_c = sd["c"][last_i]
        open_final.append({
            "sym": sym,
            "entry_date": pos["entry_date"],
            "entry_price": round(pos["entry_px"], 4),
            "last_date": last_d,
            "last_close": round(last_c, 4),
            "qty": pos["qty"],
            "unrealized_gross_inr": round((last_c - pos["entry_px"]) * pos["qty"], 2),
        })
        _close_pos(sym, pos, last_d, last_c, "FORCED", last_i - pos["entry_idx"])

    return {
        "trades": closed_trades,
        "open_at_end": open_final,
        "skipped": dict(skipped_counts),
        "stats_2025": summarize_trades(closed_trades, year=2025),
        "stats_2026": summarize_trades(closed_trades, year=2026),
        "stats_all": summarize_trades(closed_trades, year=None),
    }


def summarize_trades(
    trades: Sequence[Dict[str, Any]], year: Optional[int] = None
) -> Dict[str, Any]:
    sel = [
        t for t in trades
        if year is None or t["entry_date"][:4] == str(year)
    ]
    if not sel:
        return {
            "trades": 0, "win_rate_pct": None, "gross_inr": 0.0,
            "cost_inr": 0.0, "net_inr": 0.0, "avg_net_inr": 0.0,
            "avg_hold_days": None, "worst_trade_inr": 0.0,
            "max_dd_inr": 0.0, "peak_concurrent": 0,
            "avg_deployed_inr": 0.0, "exit_breakdown": {}, "sector_net": {},
        }
    nets = [t["net_inr"] for t in sel]
    gross = round(sum(t["gross_inr"] for t in sel), 2)
    costs = round(sum(t["cost_inr"] for t in sel), 2)
    total = round(sum(nets), 2)
    wins = sum(1 for x in nets if x > 0)
    curve = sorted(sel, key=lambda t: (t["exit_date"], t["entry_date"], t["sym"]))
    eq = peak = mdd = 0.0
    for t in curve:
        eq += t["net_inr"]
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    days = sorted({t["entry_date"] for t in sel} | {t["exit_date"] for t in sel})
    peak_conc = 0
    for d0 in days:
        c0 = sum(1 for t in sel if t["entry_date"] <= d0 <= t["exit_date"])
        peak_conc = max(peak_conc, c0)
    sec_net: Dict[str, float] = defaultdict(float)
    for t in sel:
        sec_net[t["sector"]] = round(sec_net[t["sector"]] + t["net_inr"], 2)
    return {
        "trades": len(sel),
        "win_rate_pct": round(100.0 * wins / len(sel), 2),
        "gross_inr": gross,
        "cost_inr": costs,
        "net_inr": total,
        "avg_net_inr": round(total / len(sel), 2),
        "avg_hold_days": round(sum(t["hold_days"] for t in sel) / len(sel), 1),
        "worst_trade_inr": round(min(nets), 2),
        "max_dd_inr": round(mdd, 2),
        "peak_concurrent": peak_conc,
        "avg_deployed_inr": round(
            sum(t["deployed_inr"] for t in sel) / len(sel), 2
        ),
        "exit_breakdown": dict(Counter(t["exit_kind"] for t in sel)),
        "sector_net": dict(sorted(sec_net.items(), key=lambda kv: -kv[1])),
    }


# ---------------------------------------------------------------------------
# Live Paper Scanner & Daily Action Card (for tomorrow 15:35+ IST)
# ---------------------------------------------------------------------------
def _append_paper_log(path: Path, rows: List[Dict[str, Any]]) -> int:
    seen = set()
    existing: List[Dict[str, Any]] = []
    if path.exists():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                seen.add(r["trade_key"])
                existing.append(r)
    added = 0
    for r in rows:
        if r["trade_key"] in seen:
            continue
        seen.add(r["trade_key"])
        existing.append(r)
        added += 1
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PAPER_LOG_FIELDS)
        w.writeheader()
        for r in existing:
            w.writerow({k: r.get(k, "") for k in PAPER_LOG_FIELDS})
    os.replace(tmp, path)
    return added


def run_live_scan(
    root: Path,
    universe_name: str,
    target_date: str,
    *,
    do_refresh: bool = True,
    dry_run: bool = False,
    capital_per_trade: float = 100_000.0,
    max_positions: int = 8,
    max_per_sector: int = 3,
    atr_stop_mult: float = 3.0,
    strict_regime: bool = False,
) -> Dict[str, Any]:
    """Run Pillar 1 EOD scan for `target_date`, updating paper state & action card."""
    uni = load_universe(root, universe_name)
    meta_map = {u["sym"]: u for u in uni}

    refresh_stats = Counter()
    if do_refresh:
        token = _load_token(root)
        ikeys = load_instrument_keys(root)
        # Refresh Nifty 50 first for regime filter
        st_n, _ = refresh_daily_symbol(root, "NIFTY", NIFTY_INDEX_KEY, target_date, token)
        refresh_stats[f"NIFTY:{st_n}"] += 1
        time.sleep(0.25)
        for u in uni:
            sym = u["sym"]
            ik = ikeys.get(sym)
            if not ik:
                refresh_stats["NO_KEY"] += 1
                continue
            st, _ = refresh_daily_symbol(root, sym, ik, target_date, token)
            refresh_stats[st] += 1
            if st != "UP_TO_DATE":
                time.sleep(0.25)

    # Load Nifty regime
    ndates, _, _, _, ncloses = load_daily_series(root, "NIFTY")
    nifty_reg = compute_nifty_regime(ndates, ncloses)
    reg_today = nifty_reg.get(target_date)
    if reg_today is None and ndates:
        reg_today = nifty_reg[ndates[-1]]
    above_200 = reg_today["above_200dma"] if reg_today else True
    rmult = 1.0 if above_200 else (0.0 if strict_regime else 0.5)

    # Load stock series + indicators
    series_map: Dict[str, Dict[str, Any]] = {}
    missing_today: List[str] = []
    for u in uni:
        sym = u["sym"]
        ds, o, h, l, c = load_daily_series(root, sym)
        if len(ds) < 25:
            missing_today.append(sym)
            continue
        series_map[sym] = compute_indicators(ds, o, h, l, c)
        if target_date not in series_map[sym]["idx"]:
            missing_today.append(sym)

    # Load paper state
    state_p = root / "pillar1_state.json"
    log_p = root / "pillar1_paper_log.csv"
    if state_p.exists():
        state = json.loads(state_p.read_text())
    else:
        state = {
            "universe": universe_name,
            "last_date": None,
            "positions": {},
            "pending_buys": [],
            "pending_sells": [],
        }

    closed_today: List[Dict[str, Any]] = []
    # 1. Process pending fills scheduled for today's open (only if target_date > last_date)
    already_processed = state.get("last_date") == target_date
    if not already_processed:
        for ps in list(state.get("pending_sells") or []):
            sym = ps["sym"]
            pos = state["positions"].get(sym)
            sd = series_map.get(sym)
            if not pos or not sd or target_date not in sd["idx"]:
                continue
            i = sd["idx"][target_date]
            xp = sd["o"][i]
            cost = ERU.equity_delivery_cost(pos["entry_price"], xp, pos["qty"])
            gross = (xp - pos["entry_price"]) * pos["qty"]
            closed_today.append({
                "trade_key": f"P1|{pos['entry_date']}|{sym}|{target_date}",
                "universe": universe_name, "sym": sym,
                "tier": meta_map.get(sym, {}).get("tier", ""),
                "sector": sector_of(sym), "comps": pos["comps"],
                "signal_date": pos["signal_date"],
                "entry_date": pos["entry_date"], "exit_date": target_date,
                "qty": pos["qty"], "entry_price": f"{pos['entry_price']:.2f}",
                "exit_price": f"{xp:.2f}",
                "stop_price": f"{pos['stop_price']:.2f}" if pos.get("stop_price") else "",
                "hold_days": pos.get("hold_days", 0) + 1,
                "exit_kind": ps["reason"], "upgraded": str(pos.get("upgraded", False)),
                "regime_mult": pos.get("regime_mult", 1.0),
                "gross_inr": f"{gross:.2f}", "cost_inr": f"{cost['total_cost_inr']:.2f}",
                "net_inr": f"{gross - cost['total_cost_inr']:.2f}",
                "notes": "paper only, real money Rs0",
            })
            state["positions"].pop(sym, None)
        state["pending_sells"] = []

        sec_counts = Counter(sector_of(s) for s in state["positions"])
        for pb in list(state.get("pending_buys") or []):
            sym = pb["sym"]
            if sym in state["positions"] or len(state["positions"]) >= max_positions:
                continue
            if sec_counts[sector_of(sym)] >= max_per_sector:
                continue
            sd = series_map.get(sym)
            if not sd or target_date not in sd["idx"]:
                continue
            i = sd["idx"][target_date]
            ep = sd["o"][i]
            qty = ERU.fixed_capital_qty(ep, capital_per_trade * pb["regime_mult"])
            if qty <= 0:
                continue
            stop_px = (
                max(ep - atr_stop_mult * pb["sig_atr"], 0.05)
                if (atr_stop_mult > 0 and pb.get("sig_atr"))
                else None
            )
            state["positions"][sym] = {
                "entry_date": target_date, "signal_date": pb["signal_date"],
                "entry_price": round(ep, 4), "qty": qty,
                "comps": pb["comps"], "upgraded": False,
                "stop_price": round(stop_px, 4) if stop_px else None,
                "hold_days": 0, "regime_mult": pb["regime_mult"],
            }
            sec_counts[sector_of(sym)] += 1
        state["pending_buys"] = []

    # 2. Evaluate open positions on today's bar + generate tomorrow's SELL list
    tomorrow_sells: List[Dict[str, Any]] = []
    open_summary: List[Dict[str, Any]] = []
    for sym in list(state["positions"].keys()):
        pos = state["positions"][sym]
        sd = series_map.get(sym)
        if not sd or target_date not in sd["idx"]:
            continue
        i = sd["idx"][target_date]
        if not already_processed and pos["entry_date"] != target_date:
            pos["hold_days"] = pos.get("hold_days", 0) + 1
        o_i, h_i, l_i, c_i = sd["o"][i], sd["h"][i], sd["l"][i], sd["c"][i]
        converted_today = False
        if pos["comps"] == "BB" and not pos.get("upgraded") and sd["sig_in"]["RSI"][i]:
            pos["upgraded"] = True
            converted_today = True
        allow_tc = ("RSI" in pos["comps"]) or (pos.get("upgraded") and not converted_today)

        exit_now = None
        if allow_tc and pos["hold_days"] >= 60:
            exit_now = (o_i, "TIME")
        elif pos.get("stop_price") and o_i <= pos["stop_price"]:
            exit_now = (o_i, "STOP_GAP")
        elif pos.get("stop_price") and l_i <= pos["stop_price"]:
            exit_now = (pos["stop_price"], "STOP_ATR")
        elif allow_tc and h_i >= pos["entry_price"] * 1.10:
            lvl = pos["entry_price"] * 1.10
            exit_now = (o_i if o_i >= lvl else lvl, "CAP")

        if exit_now is not None and not already_processed:
            xp, why = exit_now
            cost = ERU.equity_delivery_cost(pos["entry_price"], xp, pos["qty"])
            gross = (xp - pos["entry_price"]) * pos["qty"]
            closed_today.append({
                "trade_key": f"P1|{pos['entry_date']}|{sym}|{target_date}",
                "universe": universe_name, "sym": sym,
                "tier": meta_map.get(sym, {}).get("tier", ""),
                "sector": sector_of(sym), "comps": pos["comps"],
                "signal_date": pos["signal_date"],
                "entry_date": pos["entry_date"], "exit_date": target_date,
                "qty": pos["qty"], "entry_price": f"{pos['entry_price']:.2f}",
                "exit_price": f"{xp:.2f}",
                "stop_price": f"{pos['stop_price']:.2f}" if pos.get("stop_price") else "",
                "hold_days": pos["hold_days"], "exit_kind": why,
                "upgraded": str(pos.get("upgraded", False)),
                "regime_mult": pos.get("regime_mult", 1.0),
                "gross_inr": f"{gross:.2f}", "cost_inr": f"{cost['total_cost_inr']:.2f}",
                "net_inr": f"{gross - cost['total_cost_inr']:.2f}",
                "notes": "paper only, real money Rs0",
            })
            state["positions"].pop(sym, None)
            continue

        # Close-confirmed sell signal for tomorrow 09:15 open
        sell_why = None
        if pos["comps"] == "BB" and pos.get("upgraded"):
            if sd["sig_out"]["RSI"][i]:
                sell_why = "SIGNAL-RSI"
        elif "RSI" in pos["comps"]:
            for k in pos["comps"].split("+"):
                if sd["sig_out"][k][i]:
                    sell_why = f"SIGNAL-{k}"
                    break
        else:
            if sd["sig_out"]["BB"][i]:
                sell_why = "SIGNAL-BB"
        if sell_why:
            tomorrow_sells.append({
                "sym": sym, "reason": sell_why, "close": round(c_i, 2),
                "qty": pos["qty"],
            })
        open_summary.append({
            "sym": sym, "entry_date": pos["entry_date"],
            "entry_price": pos["entry_price"], "close": round(c_i, 2),
            "qty": pos["qty"], "stop_price": pos.get("stop_price"),
            "hold_days": pos["hold_days"], "upgraded": pos.get("upgraded", False),
            "unrealized_inr": round((c_i - pos["entry_price"]) * pos["qty"], 2),
        })

    # 3. Scan for new BUY signals + NEAR watchlist on today's close
    tomorrow_buys: List[Dict[str, Any]] = []
    near_watch: List[Dict[str, Any]] = []
    for sym, sd in series_map.items():
        if sym in state["positions"]:
            continue
        i = sd["idx"].get(target_date)
        if i is None:
            continue
        sigs = [k for k in ("BB", "RSI") if sd["sig_in"][k][i]]
        r_val = sd["rsi"][i]
        pb_val = sd["pctb"][i]
        c_i = sd["c"][i]
        atr_i = sd["atr"][i]
        if sigs:
            est_qty = ERU.fixed_capital_qty(c_i, capital_per_trade * rmult) if rmult > 0 else 0
            est_stop = round(max(c_i - atr_stop_mult * atr_i, 0.05), 2) if (atr_stop_mult > 0 and atr_i) else None
            tomorrow_buys.append({
                "sym": sym, "tier": meta_map[sym]["tier"], "sector": sector_of(sym),
                "comps": "+".join(sigs), "signal_date": target_date,
                "close": round(c_i, 2),
                "rsi": round(r_val, 1) if r_val is not None else None,
                "pctb": round(pb_val, 2) if pb_val is not None else None,
                "sig_atr": round(atr_i, 4) if atr_i is not None else None,
                "regime_mult": rmult, "est_qty": est_qty, "est_stop": est_stop,
                "blocked_by": None,
                "sort_key": (
                    0 if meta_map[sym]["tier"] == "A" else 1,
                    -((35.0 - (r_val or 50.0)) + (1.0 - (pb_val or 0.5)) * 20.0),
                    -meta_map[sym]["mcap_cr"],
                ),
            })
        elif (pb_val is not None and pb_val <= 0.15) or (r_val is not None and r_val <= 35.0):
            near_watch.append({
                "sym": sym, "tier": meta_map[sym]["tier"], "sector": sector_of(sym),
                "close": round(c_i, 2),
                "rsi": round(r_val, 1) if r_val is not None else None,
                "pctb": round(pb_val, 2) if pb_val is not None else None,
            })

    # Rank deterministically by quality + oversold depth BEFORE applying caps
    tomorrow_buys.sort(key=lambda x: x["sort_key"])
    planned_total = len(state["positions"])
    planned_sec = Counter(sector_of(s) for s in state["positions"])
    for b in tomorrow_buys:
        b.pop("sort_key", None)
        if rmult <= 0:
            b["blocked_by"] = "regime_off"
        elif planned_total >= max_positions:
            b["blocked_by"] = "max_positions"
        elif planned_sec[b["sector"]] >= max_per_sector:
            b["blocked_by"] = "sector_cap"
        else:
            planned_total += 1
            planned_sec[b["sector"]] += 1
    near_watch.sort(key=lambda x: (x["rsi"] if x["rsi"] is not None else 99.0))

    actionable_buys = [b for b in tomorrow_buys if not b["blocked_by"]]
    state["pending_buys"] = actionable_buys
    state["pending_sells"] = tomorrow_sells
    state["last_date"] = target_date
    state["universe"] = universe_name

    if not dry_run:
        if closed_today:
            _append_paper_log(log_p, closed_today)
        tmp = state_p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=2))
        os.replace(tmp, state_p)

    return {
        "date": target_date,
        "universe": universe_name,
        "universe_size": len(uni),
        "scored_symbols": len(series_map) - len([s for s in missing_today if s in series_map]),
        "missing_today": missing_today[:10],
        "missing_today_count": len(missing_today),
        "refresh_stats": dict(refresh_stats),
        "nifty_regime": {
            **(reg_today or {}),
            "sizing_mult": rmult,
            "label": "RISK-ON (100%)" if rmult == 1.0 else ("DEFENSIVE (50%)" if rmult > 0 else "PAUSED (0%)"),
        },
        "closed_today": closed_today,
        "open_positions": open_summary,
        "tomorrow_buys": tomorrow_buys,
        "tomorrow_sells": tomorrow_sells,
        "near_watchlist": near_watch[:10],
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# Deterministic Offline Self-Test (verifies every rule with zero API calls)
# ---------------------------------------------------------------------------
def run_selftest() -> int:
    print("=== PILLAR 1 (OPTION A) DETERMINISTIC SELF-TEST ===")
    # Generate 260 trading days of synthetic data covering:
    #   - SYM_BB: dips below lower BB then bounces (pure BB entry -> mid exit)
    #   - SYM_UPG: dips below lower BB, then RSI crosses up > 30 (BB->RSI upgrade -> CAP +10%)
    #   - SYM_CRASH: dips below lower BB then gaps/crashes > 3x ATR (STOP_ATR / STOP_GAP)
    #   - SYM_BANK1..4: all BANK sector firing same day -> verifies sector cap = 3!
    #   - Nifty 50: first 210 days bullish (> 200-DMA), last 50 days bearish (< 200-DMA)
    n = 260
    start = ddate(2025, 1, 1)
    dates = [(start + timedelta(days=i)).isoformat() for i in range(n)]

    def _mk_series(closes: List[float], spread: float = 0.012) -> Dict[str, Any]:
        o = [closes[0]] + [closes[i - 1] for i in range(1, len(closes))]
        h = [max(o[i], closes[i]) * (1.0 + spread) for i in range(len(closes))]
        l = [min(o[i], closes[i]) * (1.0 - spread) for i in range(len(closes))]
        return compute_indicators(dates, o, h, l, closes)

    # Nifty: rising from 22000 to 25000, then dropping below 200-DMA at day 220
    nifty_c = [22000.0 + i * 15.0 for i in range(215)] + [21500.0 - (i - 215) * 40.0 for i in range(215, n)]
    nifty_reg = compute_nifty_regime(dates, nifty_c)
    assert nifty_reg[dates[205]]["above_200dma"] is True
    assert nifty_reg[dates[235]]["above_200dma"] is False

    # 1. Deep BB dip -> triggers EKAM-2c RSI upgrade -> hits CAP +10%
    c_upg = [1000.0] * n
    for i in range(50, 56):
        c_upg[i] = 1000.0 - (i - 49) * 28.0
    c_upg[56] = 865.0
    for i in range(57, 72):
        c_upg[i] = 865.0 + (i - 56) * 14.0

    # 1b. Mild BB dip (RSI stays > 30) -> pure BB entry -> SIGNAL-BB mid exit
    c_bb_pure = [1000.0 + ((i % 2) * 2.0 - 1.0) for i in range(n)]
    c_bb_pure[54] = 970.0  # brief 1-day dip below tight lower BB (RSI stays > 30)
    c_bb_pure[55] = 985.0  # closes back inside lower BB -> pure BB entry!
    for i in range(56, 65):
        c_bb_pure[i] = 985.0 + (i - 55) * 4.0  # mean reverts cleanly above 20-SMA

    # 2. Catastrophe crash stock (fires BB on day 90 then crashes -25% on day 95)
    c_crash = [500.0] * n
    for i in range(84, 90):
        c_crash[i] = 500.0 - (i - 83) * 15.0
    c_crash[90] = 430.0  # bounce back into BB -> entry day 91
    c_crash[91] = 432.0
    for i in range(92, 105):
        c_crash[i] = 310.0  # sudden gap crash -> must trigger STOP_GAP/STOP_ATR!

    # 3. Four BANK stocks firing simultaneously on day 235 (when Nifty < 200-DMA!)
    c_bank = [200.0] * n
    for i in range(228, 234):
        c_bank[i] = 200.0 - (i - 227) * 7.0
    c_bank[234] = 165.0  # BB entry on day 234 (Nifty < 200-DMA -> 50% size!)
    for i in range(235, 250):
        c_bank[i] = 165.0 + (i - 234) * 3.5

    series_map = {
        "SYM_UPG": _mk_series(c_upg),
        "SYM_BB_PURE": _mk_series(c_bb_pure),
        "SYM_CRASH": _mk_series(c_crash),
        "BANK_1": _mk_series(c_bank),
        "BANK_2": _mk_series(c_bank),
        "BANK_3": _mk_series(c_bank),
        "BANK_4": _mk_series(c_bank),
    }
    meta_map = {
        "SYM_UPG": {"sym": "SYM_UPG", "tier": "A", "sector": "TECH", "mcap_cr": 55000.0},
        "SYM_BB_PURE": {"sym": "SYM_BB_PURE", "tier": "A", "sector": "CONSUMER", "mcap_cr": 50000.0},
        "SYM_CRASH": {"sym": "SYM_CRASH", "tier": "A", "sector": "PHARMA", "mcap_cr": 40000.0},
        "BANK_1": {"sym": "BANK_1", "tier": "A", "sector": "BANK", "mcap_cr": 90000.0},
        "BANK_2": {"sym": "BANK_2", "tier": "A", "sector": "BANK", "mcap_cr": 80000.0},
        "BANK_3": {"sym": "BANK_3", "tier": "A", "sector": "BANK", "mcap_cr": 70000.0},
        "BANK_4": {"sym": "BANK_4", "tier": "B", "sector": "BANK", "mcap_cr": 60000.0},
    }

    res = simulate_portfolio(
        series_map, meta_map, nifty_reg,
        capital_per_trade=100_000.0, max_positions=8, max_per_sector=3,
        atr_stop_mult=3.0, use_regime=True, realistic_costs=True,
    )
    trades = res["trades"]
    upg_tr = [t for t in trades if t["sym"] == "SYM_UPG"]
    bb_tr = [t for t in trades if t["sym"] == "SYM_BB_PURE"]
    crash_tr = [t for t in trades if t["sym"] == "SYM_CRASH"]
    bank_tr = [t for t in trades if t["sym"].startswith("BANK_")]

    assert upg_tr and upg_tr[0]["upgraded"] is True and upg_tr[0]["exit_kind"] == "CAP" and upg_tr[0]["net_inr"] > 0, upg_tr
    assert bb_tr and bb_tr[0]["upgraded"] is False and bb_tr[0]["exit_kind"] == "SIGNAL-BB" and bb_tr[0]["net_inr"] > 0, bb_tr
    assert crash_tr and crash_tr[0]["exit_kind"] in ("STOP_ATR", "STOP_GAP"), crash_tr
    assert len(bank_tr) == 3, f"Sector cap=3 should block 4th bank, got {len(bank_tr)}"
    assert res["skipped"].get("sector_cap", 0) >= 1
    assert all(t["regime_mult"] == 0.5 for t in bank_tr), f"Expected 0.5x regime mult: {bank_tr}"
    assert all(t["deployed_inr"] <= 52_000.0 for t in bank_tr), f"Expected ~50k deployed: {bank_tr}"
    assert all(t["cost_inr"] > 100.0 for t in trades), "Realistic delivery costs must apply"

    # Also verify live scan + idempotent state persistence in a temp folder
    with tempfile.TemporaryDirectory() as td:
        troot = Path(td)
        (troot / "data" / "pillar1_daily").mkdir(parents=True)
        with open(troot / "investing_value_analysis_2026-11-14.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Company", "Ticker", "Screener_Section", "Tier", "Reason", "MarketCap_Cr"])
            w.writerow(["HDFC Bank", "HDFCBANK", "Main", "A", "Clean", "1256430"])
        with open(troot / "data" / "pillar1_daily" / "NIFTY.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close", "source"])
            for d, cc in zip(dates, nifty_c):
                w.writerow([d, cc, cc * 1.005, cc * 0.995, cc, "official"])
        with open(troot / "data" / "pillar1_daily" / "HDFCBANK.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close", "source"])
            for d, cc in zip(dates, c_upg):
                w.writerow([d, cc, cc * 1.01, cc * 0.99, cc, "official"])
        scan = run_live_scan(troot, "tier_a", dates[56], do_refresh=False, dry_run=False)
        assert len(scan["tomorrow_buys"]) == 1 and scan["tomorrow_buys"][0]["sym"] == "HDFCBANK", scan
        assert (troot / "pillar1_state.json").exists()

    print(f"  OK  EKAM-2c BB->RSI upgrade -> CAP +10%: net=Rs {upg_tr[0]['net_inr']:+.2f} (cost=Rs {upg_tr[0]['cost_inr']:.2f})")
    print(f"  OK  Pure BB mean-reversion -> SIGNAL-BB: net=Rs {bb_tr[0]['net_inr']:+.2f} (cost=Rs {bb_tr[0]['cost_inr']:.2f})")
    print(f"  OK  3x ATR catastrophe stop triggered: {crash_tr[0]['exit_kind']} @ Rs {crash_tr[0]['exit_price']}")
    print(f"  OK  Sector cap (max 3 BANK) blocked 4th bank (skipped={res['skipped']})")
    print(f"  OK  Nifty < 200-DMA automatically scaled deployment to 50% (Rs {bank_tr[0]['deployed_inr']:.0f})")
    print(f"  OK  Live scanner & state persistence verified cleanly")
    print("PILLAR 1 SELF-TEST PASSED!")
    return 0


# ---------------------------------------------------------------------------
# Backtest Runner + Pretty Printer
# ---------------------------------------------------------------------------
def run_backtest(
    root: Path,
    universe_name: str,
    *,
    capital_per_trade: float = 100_000.0,
    max_positions: int = 8,
    max_per_sector: int = 3,
    atr_stop_mult: float = 3.0,
    strict_regime: bool = False,
) -> int:
    uni = load_universe(root, universe_name)
    meta_map = {u["sym"]: u for u in uni}
    series_map: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []
    for u in uni:
        ds, o, h, l, c = load_daily_series(root, u["sym"])
        if len(ds) >= 40:
            series_map[u["sym"]] = compute_indicators(ds, o, h, l, c)
        else:
            missing.append(u["sym"])

    if not series_map:
        print(f"NO LOCAL DAILY DATA FOUND under {root}/data/ for universe={universe_name}.")
        print("Run this on your live machine (~/workspace/trading) or run --mode live to refresh via Upstox.")
        return 2

    ndates, _, _, _, ncloses = load_daily_series(root, "NIFTY")
    nifty_reg = compute_nifty_regime(ndates, ncloses) if ndates else {}

    legacy = simulate_portfolio(
        series_map, meta_map, nifty_reg,
        fixed_shares=100, max_positions=999, max_per_sector=999,
        atr_stop_mult=0.0, use_regime=False, realistic_costs=False,
        flat_cost_inr=40.0,
    )
    legacy_real_cost = simulate_portfolio(
        series_map, meta_map, nifty_reg,
        fixed_shares=100, max_positions=999, max_per_sector=999,
        atr_stop_mult=0.0, use_regime=False, realistic_costs=True,
    )
    apex = simulate_portfolio(
        series_map, meta_map, nifty_reg,
        capital_per_trade=capital_per_trade,
        max_positions=max_positions,
        max_per_sector=max_per_sector,
        atr_stop_mult=atr_stop_mult,
        use_regime=True,
        strict_regime=strict_regime,
        realistic_costs=True,
    )

    rep = {
        "generated_at": datetime.now(IST).isoformat(),
        "root": str(root),
        "universe": universe_name,
        "symbols_loaded": len(series_map),
        "symbols_missing_history": missing,
        "nifty_bars": len(ndates),
        "legacy_100sh_rs40": {
            "2025": legacy["stats_2025"], "2026": legacy["stats_2026"], "all": legacy["stats_all"],
        },
        "legacy_100sh_real_cost": {
            "2025": legacy_real_cost["stats_2025"], "2026": legacy_real_cost["stats_2026"],
            "all": legacy_real_cost["stats_all"],
        },
        "apex_pillar1": {
            "config": {
                "capital_per_trade": capital_per_trade, "max_positions": max_positions,
                "max_per_sector": max_per_sector, "atr_stop_mult": atr_stop_mult,
                "strict_regime": strict_regime,
            },
            "2025": apex["stats_2025"], "2026": apex["stats_2026"], "all": apex["stats_all"],
            "skipped": apex["skipped"], "open_at_end": apex["open_at_end"],
        },
    }
    (root / f"pillar1_backtest_{universe_name}.json").write_text(json.dumps(rep, indent=2))
    with open(root / f"pillar1_backtest_{universe_name}_trades.csv", "w", newline="") as f:
        cols = [
            "sym", "tier", "sector", "comps", "signal_date", "entry_date",
            "exit_date", "qty", "deployed_inr", "entry_price", "exit_price",
            "stop_price", "hold_days", "exit_kind", "upgraded", "regime_mult",
            "gross_inr", "cost_inr", "net_inr",
        ]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in apex["trades"]:
            w.writerow({k: t.get(k, "") for k in cols})

    print(f"\nPILLAR 1 BACKTEST — universe={universe_name} ({len(series_map)}/{len(uni)} symbols loaded, Nifty bars={len(ndates)})")
    for label, blk in (
        ("LEGACY (100 sh, Rs40 flat, S0)", rep["legacy_100sh_rs40"]),
        ("LEGACY (100 sh, REAL NSE cost)", rep["legacy_100sh_real_cost"]),
        ("APEX PILLAR 1 (Rs1L, REAL cost, 3xATR, 200DMA, caps)", rep["apex_pillar1"]),
    ):
        print(f"\n  {label}:")
        for yr in ("2025", "2026", "all"):
            s = blk[yr]
            print(
                f"    {yr:<4}: {s['trades']:>3} tr | WR {str(s['win_rate_pct']):>5}% | "
                f"Gross Rs {s['gross_inr']:>+10,.0f} | Cost Rs {s['cost_inr']:>8,.0f} | "
                f"Net Rs {s['net_inr']:>+10,.0f} | MaxDD Rs {s['max_dd_inr']:>+9,.0f} | "
                f"PeakConc {s['peak_concurrent']}"
            )
    if missing:
        print(f"\n  Missing daily stores ({len(missing)}): {missing[:15]}")
    print(f"  Saved report -> {root / f'pillar1_backtest_{universe_name}.json'}")
    return 0


def _print_action_card(rep: Dict[str, Any]) -> None:
    reg = rep["nifty_regime"]
    print(f"\n================ PILLAR 1 DAILY ACTION CARD ({rep['date']}) ================")
    print(f"Universe: {rep['universe']} ({rep['scored_symbols']}/{rep['universe_size']} scored) | "
          f"Nifty Regime: {reg.get('label')} (close={reg.get('close')}, 200-DMA={reg.get('sma200')})")
    if rep["refresh_stats"]:
        print(f"Feed refresh: {rep['refresh_stats']}")
    if rep["closed_today"]:
        print(f"\nClosed Today ({len(rep['closed_today'])}):")
        for t in rep["closed_today"]:
            print(f"  CLOSE {t['sym']:<12} {t['exit_kind']:<10} qty={t['qty']} "
                  f"{t['entry_price']} -> {t['exit_price']} | Net Rs {t['net_inr']}")
    print(f"\nOpen Paper Positions ({len(rep['open_positions'])}):")
    if not rep["open_positions"]:
        print("  (none)")
    for p in rep["open_positions"]:
        print(f"  HOLD  {p['sym']:<12} qty={p['qty']:<4} entry={p['entry_price']:<8.2f} "
              f"close={p['close']:<8.2f} stop={str(p['stop_price']):<8} "
              f"day={p['hold_days']:<2} upg={p['upgraded']} uPnL=Rs {p['unrealized_inr']:+,.0f}")
    print(f"\nACTION FOR TOMORROW 09:15 OPEN — SELLS ({len(rep['tomorrow_sells'])}):")
    for s in rep["tomorrow_sells"]:
        print(f"  SELL  {s['sym']:<12} qty={s['qty']:<4} reason={s['reason']} (last close {s['close']})")
    print(f"\nACTION FOR TOMORROW 09:15 OPEN — BUYS ({len(rep['tomorrow_buys'])}):")
    if not rep["tomorrow_buys"]:
        print("  (no EKAM-2c entry signals fired today)")
    for b in rep["tomorrow_buys"]:
        tag = f"BLOCKED({b['blocked_by']})" if b["blocked_by"] else "ACTIONABLE"
        print(f"  BUY   {b['sym']:<12} [{b['tier']}|{b['sector']}] {b['comps']:<6} "
              f"close={b['close']:<8.2f} est_qty={b['est_qty']:<4} est_stop={b['est_stop']} -> {tag}")
    print(f"\nNEAR WATCHLIST ({len(rep['near_watchlist'])} approaching BB/RSI):")
    for w in rep["near_watchlist"]:
        print(f"  NEAR  {w['sym']:<12} [{w['tier']}|{w['sector']}] close={w['close']:<8.2f} "
              f"RSI={w['rsi']} %B={w['pctb']}")
    print("=============================================================================\n")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("selftest", "backtest", "live"), default="live")
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--universe", choices=("tier_a", "tier_ab", "value_all", "ekam25"), default="tier_ab")
    ap.add_argument("--date", default=datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--capital-per-trade", type=float, default=100_000.0)
    ap.add_argument("--max-positions", type=int, default=8)
    ap.add_argument("--max-per-sector", type=int, default=3)
    ap.add_argument("--atr-stop", type=float, default=3.0)
    ap.add_argument("--strict-regime", action="store_true")
    ap.add_argument("--no-refresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.mode == "selftest":
        return run_selftest()
    root = Path(a.root)
    if a.mode == "backtest":
        return run_backtest(
            root, a.universe,
            capital_per_trade=a.capital_per_trade,
            max_positions=a.max_positions,
            max_per_sector=a.max_per_sector,
            atr_stop_mult=a.atr_stop,
            strict_regime=a.strict_regime,
        )
    try:
        rep = run_live_scan(
            root, a.universe, a.date,
            do_refresh=not a.no_refresh,
            dry_run=a.dry_run,
            capital_per_trade=a.capital_per_trade,
            max_positions=a.max_positions,
            max_per_sector=a.max_per_sector,
            atr_stop_mult=a.atr_stop,
            strict_regime=a.strict_regime,
        )
    except RateLimited as e:
        print(f"HARD STOP (HTTP 429): {e}", file=sys.stderr)
        return 3
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        _print_action_card(rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
