#!/usr/bin/env python3
"""RESUMABLE DATA BACKFILL — Bank Nifty & Nifty (2025–2026 Spot, Breadth & Options).

Closes the exact three index-option data holes identified by the live-machine
audit (2026-11-26):
  1. Bank Nifty & Nifty 2024–2026 daily + 2025–2026 5-min spot candles
     (ensuring full multi-year coverage in data/progressive/<IDX>/).
  2. All 5 Bank Nifty heavyweight constituent 5-min bars for 2025–2026
     (HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK -> data/breadth_5m/<SYM>/
     spot_5m_vol.csv) so breadth confirmation NEVER degrades to 1 stock.
  3. 2025 + 2026 expired & active index option 5-min candles (ATM + ±1..±5
     strikes for CE & PE — covering naked buying, debit spreads, and hedged
     iron condors) via Upstox's proven /v2/expired-instruments/ & /v3/ routes,
     mirrored into oi_buildup_data/ (and historical_proof_data/ for contract
     metadata including exact historical lot_size per expiry!).

Features:
  - Resumable JSON manifest checkpointing (backfill_index_manifest.json)
  - Strict HTTP 429 HARD STOP (exit code 3, no blind retries)
  - Browser User-Agent on every call; token read from upstox_refresh/.env
    (never printed or written anywhere)
  - Probes /v2/expired-instruments/expiries first and reports the EXACT date
    span Upstox currently serves so you know immediately how far back 2025
    expired option candles reach.
  - Read-only market data fetches. Paper only, real money Rs 0.

Usage:
  # 1. Check Upstox expired-expiry retention window (fast, 2 API calls)
  python3 backfill_index_2025_2026.py --probe-only

  # 2. Pull spot (2024-2026) + all 5 Bank Nifty breadth heavyweights (2025-2026)
  python3 backfill_index_2025_2026.py --stage spot --stage breadth

  # 3. Pull option candles (targeted: ATM + wings on sampled/signal days, or full)
  python3 backfill_index_2025_2026.py --stage options --from 2025-01-01 --to 2026-11-25
  python3 backfill_index_2025_2026.py --stage all --from 2025-01-01 --to 2026-11-25

  # 4. Offline self-test (no API calls)
  python3 backfill_index_2025_2026.py --selftest
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as ddate, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
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

INDEX_META: Dict[str, Dict[str, Any]] = {
    "BANKNIFTY": {
        "spot_key": "NSE_INDEX|Nifty Bank",
        "step": 100,
        "ce_offsets": (0, 100, 200, 400, 500, 600),
        "pe_offsets": (0, -100, -200, -400, -500, -600),
        "prefer_monthly": True,
    },
    "NIFTY": {
        "spot_key": "NSE_INDEX|Nifty 50",
        "step": 50,
        "ce_offsets": (0, 50, 100, 200, 250, 300),
        "pe_offsets": (0, -50, -100, -200, -250, -300),
        "prefer_monthly": False,
    },
}

BANK_HEAVYWEIGHTS = ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"]


class RateLimited(Exception):
    pass


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "upstox_refresh" / ".env").exists() or (live / "data").exists():
        return live
    return Path(__file__).resolve().parent


def load_token(root: Path) -> str:
    env_p = root / "upstox_refresh" / ".env"
    if not env_p.exists():
        raise FileNotFoundError(f"Token file missing: {env_p}")
    for line in env_p.read_text().splitlines():
        line = line.strip()
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            tok = line.split("=", 1)[1].strip().strip('"').strip("'")
            if tok:
                return tok
    raise RuntimeError(f"UPSTOX_ACCESS_TOKEN not found in {env_p}")


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
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(f"HTTP 429 rate limit on {path}")
        raise RuntimeError(f"HTTP {e.code} on {path}")


def write_csv_atomic(path: Path, header: Sequence[str], rows: Sequence[Sequence[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def month_chunks(start_s: str, end_s: str) -> List[Tuple[str, str, str]]:
    """Split [start_s, end_s] into calendar-month chunks (label, frm, to)."""
    s = ddate.fromisoformat(start_s)
    e = ddate.fromisoformat(end_s)
    out: List[Tuple[str, str, str]] = []
    y, m = s.year, s.month
    while True:
        frm = max(ddate(y, m, 1), s)
        nxt = ddate(y + (m == 12), (m % 12) + 1, 1)
        to = min(nxt - timedelta(days=1), e)
        if frm <= to:
            out.append((f"{y}-{m:02d}", frm.isoformat(), to.isoformat()))
        if to >= e:
            break
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def resolve_equity_keys(root: Path) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    uni = root / "universe_daily" / "universe.csv"
    if uni.exists():
        with open(uni, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("symbol") and r.get("instrument_key"):
                    keys[r["symbol"].strip()] = r["instrument_key"].strip()

    master = root / "november_shadow_data" / "instruments_NSE.csv"
    if not master.exists():
        master.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(
            INSTRUMENTS_URL,
            headers={"Accept": "application/gzip", "User-Agent": UA},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            master.write_bytes(gzip.decompress(r.read()))
    with open(master, newline="") as f:
        for r in csv.DictReader(f):
            if r.get("exchange") == "NSE_EQ" and r.get("instrument_type") == "EQUITY":
                s = (r.get("tradingsymbol") or "").strip()
                k = (r.get("instrument_key") or "").strip()
                if s and k and s not in keys:
                    keys[s] = k
    return keys


def _load_manifest(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    return {"spot_chunks": {}, "breadth_chunks": {}, "option_days": {}, "expiries": {}}


def _save_manifest(path: Path, man: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1))
    os.replace(tmp, path)


def _merge_5m_csv(path: Path, new_candles: Sequence[Sequence[Any]]) -> int:
    bars: Dict[str, List[Any]] = {}
    if path.exists():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                bars[r["timestamp"]] = [
                    r["timestamp"], r["open"], r["high"],
                    r["low"], r["close"], r.get("volume", "0"),
                ]
    for c in new_candles:
        ts = str(c[0]).replace("T", " ")[:19] + "+05:30"
        vol = c[5] if len(c) > 5 and c[5] is not None else 0
        bars[ts] = [ts, c[1], c[2], c[3], c[4], vol]
    write_csv_atomic(
        path,
        ["timestamp", "open", "high", "low", "close", "volume"],
        [bars[k] for k in sorted(bars)],
    )
    return len(bars)


def _merge_daily_csv(path: Path, new_candles: Sequence[Sequence[Any]]) -> int:
    rows: Dict[str, List[Any]] = {}
    if path.exists():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                rows[r["date"][:10]] = [r["date"][:10], r["open"], r["high"], r["low"], r["close"]]
    for c in new_candles:
        dt = str(c[0])[:10]
        rows[dt] = [dt, c[1], c[2], c[3], c[4]]
    write_csv_atomic(
        path, ["date", "open", "high", "low", "close"],
        [rows[k] for k in sorted(rows)],
    )
    return len(rows)


# ---------------------------------------------------------------------------
# Stage 0: Probe Upstox Expired-Instruments Retention
# ---------------------------------------------------------------------------
def probe_expiries(root: Path, token: str, man: Dict[str, Any]) -> Dict[str, List[str]]:
    res: Dict[str, List[str]] = {}
    for idx, meta in INDEX_META.items():
        enc = urllib.parse.quote(meta["spot_key"], safe="")
        body = api_get(f"/v2/expired-instruments/expiries?instrument_key={enc}", token)
        exps = sorted(body.get("data") or [])
        res[idx] = exps
        man["expiries"][idx] = exps
        e25 = [e for e in exps if e.startswith("2025-")]
        e26 = [e for e in exps if e.startswith("2026-")]
        print(
            f"[PROBE] {idx:<9}: {len(exps)} expired expiries available | "
            f"earliest={exps[0] if exps else 'NONE'} latest={exps[-1] if exps else 'NONE'} | "
            f"2025={len(e25)} 2026={len(e26)}",
            flush=True,
        )
        time.sleep(0.30)
    return res


# ---------------------------------------------------------------------------
# Stage 1: Spot 5-min & Daily Backfill (BANKNIFTY + NIFTY)
# ---------------------------------------------------------------------------
def backfill_spot(
    root: Path, token: str, man: Dict[str, Any], start_s: str, end_s: str, sleep_s: float
) -> None:
    chunks = month_chunks(start_s, end_s)
    daily_start = (ddate.fromisoformat(start_s) - timedelta(days=90)).isoformat()
    for idx, meta in INDEX_META.items():
        enc = urllib.parse.quote(meta["spot_key"], safe="")
        # Daily bars (for 20-DMA / NR4 / swing trend warmup)
        d_path = root / "data" / "progressive" / idx / "spot_daily.csv"
        d_body = api_get(f"/v3/historical-candle/{enc}/days/1/{end_s}/{daily_start}", token)
        d_cnt = _merge_daily_csv(d_path, (d_body.get("data") or {}).get("candles") or [])
        print(f"[SPOT-D] {idx}: {d_cnt} daily bars -> {d_path}", flush=True)
        time.sleep(sleep_s)

        # 5-min bars month by month (resumable)
        p5 = root / "data" / "progressive" / idx / "spot_5m.csv"
        done = set(man["spot_chunks"].get(idx) or [])
        for lbl, frm, to in chunks:
            if lbl in done:
                continue
            body = api_get(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}", token)
            cs = (body.get("data") or {}).get("candles") or []
            tot = _merge_5m_csv(p5, cs)
            done.add(lbl)
            man["spot_chunks"][idx] = sorted(done)
            _save_manifest(root / "backfill_index_manifest.json", man)
            print(f"[SPOT-5M] {idx} {lbl}: +{len(cs)} bars (total {tot})", flush=True)
            time.sleep(sleep_s)


# ---------------------------------------------------------------------------
# Stage 2: Bank Nifty Top-5 Constituent 5-min Breadth Backfill
# ---------------------------------------------------------------------------
def backfill_breadth(
    root: Path, token: str, man: Dict[str, Any], start_s: str, end_s: str, sleep_s: float
) -> None:
    eq_keys = resolve_equity_keys(root)
    chunks = month_chunks(start_s, end_s)
    for sym in BANK_HEAVYWEIGHTS:
        ik = eq_keys.get(sym)
        if not ik:
            print(f"[BREADTH] {sym}: instrument_key NOT FOUND — skipped", flush=True)
            continue
        enc = urllib.parse.quote(ik, safe="")
        p5 = root / "data" / "breadth_5m" / sym / "spot_5m_vol.csv"
        done = set(man["breadth_chunks"].get(sym) or [])
        for lbl, frm, to in chunks:
            if lbl in done:
                continue
            body = api_get(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}", token)
            cs = (body.get("data") or {}).get("candles") or []
            tot = _merge_5m_csv(p5, cs)
            done.add(lbl)
            man["breadth_chunks"][sym] = sorted(done)
            _save_manifest(root / "backfill_index_manifest.json", man)
            print(f"[BREADTH] {sym:<10} {lbl}: +{len(cs)} bars (total {tot})", flush=True)
            time.sleep(sleep_s)


# ---------------------------------------------------------------------------
# Stage 3: Expired & Active Index Option 5-min Candles + Lot Size Metadata
# ---------------------------------------------------------------------------
def _load_spot_open_by_day(root: Path, idx: str, start_s: str, end_s: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    p = root / "data" / "progressive" / idx / "spot_5m.csv"
    if not p.exists():
        return out
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            t = r["timestamp"][11:16]
            if start_s <= d <= end_s and t == "09:15":
                out[d] = float(r["open"])
    return out


def _ensure_contracts_file(
    root: Path, idx: str, expiry: str, token: str, is_expired: bool, sleep_s: float
) -> List[Dict[str, Any]]:
    hp = root / "historical_proof_data"
    hp.mkdir(parents=True, exist_ok=True)
    cf = hp / f"contracts_{idx}_{expiry}.json"
    if cf.exists():
        try:
            data = json.loads(cf.read_text()).get("data") or []
            if data:
                return data
        except Exception:
            pass
    enc = urllib.parse.quote(INDEX_META[idx]["spot_key"], safe="")
    route = (
        f"/v2/expired-instruments/option/contract?instrument_key={enc}&expiry_date={expiry}"
        if is_expired else
        f"/v2/option/contract?instrument_key={enc}&expiry_date={expiry}"
    )
    body = api_get(route, token)
    data = body.get("data") or []
    if data:
        cf.write_text(json.dumps(body))
    time.sleep(sleep_s)
    return data


def _select_expiry_for_day(
    day_s: str, monthly_exps: Sequence[str], all_exps: Sequence[str], prefer_monthly: bool
) -> Optional[str]:
    pool = monthly_exps if prefer_monthly else all_exps
    for e in pool:
        if e >= day_s:
            return e
    for e in all_exps:
        if e >= day_s:
            return e
    return None


def backfill_options(
    root: Path,
    token: str,
    man: Dict[str, Any],
    indices: Sequence[str],
    start_s: str,
    end_s: str,
    sleep_s: float,
    include_wings: bool = True,
    max_days: int = 0,
) -> None:
    today_s = datetime.now(IST).strftime("%Y-%m-%d")
    out_dir = root / "oi_buildup_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    exp_map = probe_expiries(root, token, man)

    # Also build lot-size registry per (index, expiry) so 2025 vs 2026 lot changes are exact!
    lot_reg_p = root / "historical_proof_data" / "lot_sizes_by_expiry.json"
    lot_reg: Dict[str, Dict[str, int]] = (
        json.loads(lot_reg_p.read_text()) if lot_reg_p.exists() else {}
    )

    for idx in indices:
        meta = INDEX_META[idx]
        step = meta["step"]
        spot_opens = _load_spot_open_by_day(root, idx, start_s, end_s)
        if not spot_opens:
            print(f"[OPTIONS] {idx}: no spot_5m.csv bars in [{start_s}, {end_s}] — run --stage spot first!", flush=True)
            continue

        all_exps = sorted(exp_map.get(idx) or [])
        # Identify monthly expiries (last expiry per YYYY-MM)
        by_ym: Dict[str, List[str]] = {}
        for e in all_exps:
            by_ym.setdefault(e[:7], []).append(e)
        monthly_exps = sorted(v[-1] for v in by_ym.values())

        # Group trading days by chosen monthly expiry, then fetch each unique
        # (expiry, strike, typ) in 14-day range chunks (~10x fewer API calls AND
        # guarantees full multi-day continuity for SWING_DEBIT holds!).
        exp_to_days: Dict[str, List[str]] = {}
        for d in sorted(spot_opens):
            exp = _select_expiry_for_day(d, monthly_exps, all_exps, prefer_monthly=True)
            if exp:
                exp_to_days.setdefault(exp, []).append(d)

        done_contracts = set(man.setdefault("option_contracts", {}).get(idx) or [])
        exps_todo = sorted(exp_to_days.keys())
        if max_days > 0:
            # Cap number of expiries (~months) when max_days is set
            exps_todo = exps_todo[:max(1, max_days // 20 or 1)]
        print(
            f"[OPTIONS] {idx}: {len(exps_todo)} monthly expiries covering "
            f"{sum(len(exp_to_days[e]) for e in exps_todo)}/{len(spot_opens)} spot days "
            f"(cached contracts={len(done_contracts)})",
            flush=True,
        )

        for exp in exps_todo:
            exp_days = sorted(exp_to_days[exp])
            is_exp = exp < today_s
            rows = _ensure_contracts_file(root, idx, exp, token, is_exp, sleep_s)
            cmap: Dict[Tuple[int, str], str] = {}
            for c in rows:
                sp = c.get("strike_price") or c.get("strike")
                typ = c.get("instrument_type")
                ik = c.get("instrument_key")
                if sp is not None and typ in ("CE", "PE") and ik:
                    cmap[(int(float(sp)), typ)] = ik
                if c.get("lot_size"):
                    lot_reg.setdefault(idx, {})[exp] = int(float(c["lot_size"]))
            lot_reg_p.write_text(json.dumps(lot_reg, indent=1))

            # Collect unique (strike, typ) needed across all days in this expiry
            needed: set[Tuple[int, str]] = set()
            for d in exp_days:
                atm = int(round(spot_opens[d] / float(step)) * step)
                if include_wings:
                    for off in meta["ce_offsets"]:
                        needed.add((atm + off, "CE"))
                    for off in meta["pe_offsets"]:
                        needed.add((atm + off, "PE"))
                else:
                    needed.add((atm, "CE"))
                    needed.add((atm, "PE"))

            d_start = ddate.fromisoformat(exp_days[0])
            d_end = ddate.fromisoformat(exp_days[-1])
            fetched_c = 0
            for strike, typ in sorted(needed):
                ckey = f"{exp}|{strike}{typ}"
                if ckey in done_contracts:
                    continue
                ik = cmap.get((strike, typ))
                if not ik:
                    continue
                enc = urllib.parse.quote(ik, safe="")
                by_day_candles: Dict[str, List[Any]] = {}
                cur = d_start
                while cur <= d_end:
                    chunk_to = min(cur + timedelta(days=13), d_end)
                    if is_exp:
                        url = (
                            f"/v2/expired-instruments/historical-candle/"
                            f"{enc}/5minute/{chunk_to.isoformat()}/{cur.isoformat()}"
                        )
                    else:
                        url = (
                            f"/v3/historical-candle/"
                            f"{enc}/minutes/5/{chunk_to.isoformat()}/{cur.isoformat()}"
                        )
                    try:
                        body = api_get(url, token)
                    except RuntimeError as err:
                        print(f"  [WARN] {idx} {exp} {strike}{typ} ({cur}..{chunk_to}): {err}", flush=True)
                        cur = chunk_to + timedelta(days=1)
                        time.sleep(sleep_s)
                        continue
                    for c in ((body.get("data") or {}).get("candles") or []):
                        cd = str(c[0])[:10]
                        by_day_candles.setdefault(cd, []).append(c)
                    time.sleep(sleep_s)
                    cur = chunk_to + timedelta(days=1)

                for cd, cs in by_day_candles.items():
                    fn = out_dir / f"candles_{idx}_{strike}{typ}_{exp}_{cd}.json"
                    if not fn.exists():
                        fn.write_text(json.dumps({"status": "success", "data": {"candles": cs}}))
                done_contracts.add(ckey)
                man["option_contracts"][idx] = sorted(done_contracts)
                _save_manifest(root / "backfill_index_manifest.json", man)
                fetched_c += 1

            print(
                f"[OPTIONS] {idx} exp {exp} ({exp_days[0]}..{exp_days[-1]}): "
                f"fetched {fetched_c} new contracts (total needed={len(needed)})",
                flush=True,
            )


def run_selftest() -> int:
    print("=== BACKFILL INDEX 2025-2026 SELF-TEST ===")
    ch = month_chunks("2025-01-01", "2025-03-15")
    assert ch == [
        ("2025-01", "2025-01-01", "2025-01-31"),
        ("2025-02", "2025-02-01", "2025-02-28"),
        ("2025-03", "2025-03-01", "2025-03-15"),
    ], ch
    exp = _select_expiry_for_day("2025-03-10", ["2025-02-27", "2025-03-27"], ["2025-03-13", "2025-03-27"], True)
    assert exp == "2025-03-27", exp
    print("  OK  month_chunks & monthly expiry selection verified")
    print("BACKFILL SELF-TEST PASSED!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(default_root()))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe-only", action="store_true")
    ap.add_argument(
        "--stage", action="append", choices=("spot", "breadth", "options", "all"),
        default=[], help="Stages to run (repeatable; default: all)",
    )
    ap.add_argument("--index", choices=("BANKNIFTY", "NIFTY", "ALL"), default="ALL")
    ap.add_argument("--from", dest="date_from", default="2025-01-01")
    ap.add_argument("--to", dest="date_to", default=datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--atm-only", action="store_true", help="Only fetch ATM strikes (skip condor/spread wings)")
    ap.add_argument("--max-days", type=int, default=0, help="Optional cap on option days per run (0 = all)")
    ap.add_argument("--sleep", type=float, default=0.30, help="Seconds between API calls")
    a = ap.parse_args(argv)

    if a.selftest:
        return run_selftest()

    root = Path(a.root)
    token = load_token(root)
    man_p = root / "backfill_index_manifest.json"
    man = _load_manifest(man_p)

    try:
        if a.probe_only:
            probe_expiries(root, token, man)
            _save_manifest(man_p, man)
            return 0

        stages = set(a.stage) if a.stage else {"all"}
        if "all" in stages:
            stages = {"spot", "breadth", "options"}
        indices = ["BANKNIFTY", "NIFTY"] if a.index == "ALL" else [a.index]

        if "spot" in stages:
            backfill_spot(root, token, man, a.date_from, a.date_to, a.sleep)
        if "breadth" in stages:
            backfill_breadth(root, token, man, a.date_from, a.date_to, a.sleep)
        if "options" in stages:
            backfill_options(
                root, token, man, indices, a.date_from, a.date_to, a.sleep,
                include_wings=not a.atm_only, max_days=a.max_days,
            )
    except RateLimited as e:
        _save_manifest(man_p, man)
        print(f"RATE_LIMITED HARD STOP (manifest saved, re-run later to resume): {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
