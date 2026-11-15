#!/usr/bin/env python3
"""NIFTY + BANK NIFTY LONG HOLDS — build (2026-11-15).
Spec: nifty_longhold_SPEC.md (frozen before scoring, Bank arm added by the
2026-11-15 10:45 extension, still before scoring).
Monthly trend (50/200-DMA) -> buy monthly-expiry ATM on the trend side at the
next month's first-day open; HOLD-1M exits at expiry close; HOLD-2M rolls once
(trend recomputed at the first expiry) and exits at the second expiry close.
Premiums: Upstox expired-instruments route, browser UA. HTTP 429 = hard stop,
progress saved, remaining fetches NC (house rule). Resumable via disk cache.
"""
import csv, json, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OUT = TR / "nifty_longhold_data"
CH = OUT / "candles"
CH.mkdir(parents=True, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token


class RateLimited(Exception):
    pass


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        raise


# ---------------- spot + trend -------------------------------------------
def load_spot(fn):
    rows = list(csv.DictReader(open(fn)))
    return [(r["date"], float(r["close"])) for r in rows]


SPOTS = {
    "NIFTY": load_spot(TR / "volrix/nifty_daily_2019_2026.csv"),
    "BANKNIFTY": load_spot(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv"),
}


def trend_at(series, i):
    closes = [c for _, c in series]

    def dma(j, w):
        if j + 1 < w or j < 0:
            return None
        return sum(closes[j - w + 1:j + 1]) / w

    d50, d200, c = dma(i, 50), dma(i, 200), closes[i]
    if d50 is None:
        return "NA"
    if d200 is not None:
        return ("UP" if (c > d50 and d50 > d200)
                else "DOWN" if (c < d50 and d50 < d200) else "FLAT")
    p = dma(i - 20, 50)
    if p is None:
        return "NA"
    return ("UP" if (c > d50 and d50 > p)
            else "DOWN" if (c < d50 and d50 < p) else "FLAT")


def month_ends(series):
    me = {}
    for i, (d, _) in enumerate(series):
        me[d[:7]] = i
    return me


def first_day_of_month(series, ym):
    for i, (d, _) in enumerate(series):
        if d[:7] == ym:
            return i
    return None


def next_trading_day(series, i):
    return i + 1 if i + 1 < len(series) else None


# ---------------- monthly expiries ----------------------------------------
EXPIRY_2025 = ["2025-01-30", "2025-02-27", "2025-03-27", "2025-04-24",
               "2025-05-29", "2025-06-26", "2025-07-31", "2025-08-28",
               "2025-09-30", "2025-10-28", "2025-11-25", "2025-12-30"]
EXPIRY_2026 = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
               "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
               "2026-09-29", "2026-10-27", "2026-11-23"]
MONTHLY = EXPIRY_2025 + EXPIRY_2026  # index by month order from 2025-01


def expiry_for_month(ym):
    """Monthly expiry date (nominal) for calendar month ym (2025-01..2026-11)."""
    y, m = int(ym[:4]), int(ym[5:7])
    k = (y - 2025) * 12 + (m - 1)
    return MONTHLY[k] if 0 <= k < len(MONTHLY) else None


# ---------------- contract keys (cached, verified) -------------------------
IDXKEY = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}
_keymaps = {}


def key_map(idx, exp):
    ck = (idx, exp)
    if ck in _keymaps:
        return _keymaps[ck]
    fn = OUT / f"keys_{idx}_{exp}.json"
    if fn.exists():
        raw = json.loads(fn.read_text())
        m = {(int(s), t): v for (s, t), v in
             ((tuple(k.split("|")), v) for k, v in raw.items())}
        _keymaps[ck] = (exp, m)
        return _keymaps[ck]
    # probe exp, stepping back up to 4 days for holiday shifts
    from datetime import date, timedelta
    d0 = date.fromisoformat(exp)
    for back in range(0, 5):
        cand = (d0 - timedelta(days=back)).isoformat()
        body = get(f"{API}/v2/expired-instruments/option/contract"
                   f"?instrument_key={quote(IDXKEY[idx], safe='')}"
                   f"&expiry_date={cand}")
        data = body.get("data") or []
        if data:
            m = {(int(float(c["strike_price"])), c["instrument_type"]):
                 c["instrument_key"] for c in data}
            fn.write_text(json.dumps(
                {f"{s}|{t}": v for (s, t), v in m.items()}))
            _keymaps[ck] = (cand, m)
            return _keymaps[ck]
        time.sleep(0.25)
    _keymaps[ck] = (exp, {})
    return _keymaps[ck]


# ---------------- candles (cached) ------------------------------------------
def day_bars(idx, exp, strike, typ, day):
    """(first_open, last_close) of the contract's 5-min bars on `day`, or None."""
    fn = CH / f"{idx}_{exp}_{strike}{typ}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
    else:
        _, km = key_map(idx, exp)
        key = km.get((strike, typ))
        if not key:
            return None
        body = get(f"{API}/v2/expired-instruments/historical-candle/"
                   f"{quote(key, safe='')}/5minute/{day}/{day}")
        fn.write_text(json.dumps(body))
        time.sleep(0.25)
    candles = (body.get("data") or {}).get("candles") or []
    if not candles:
        return None
    candles = sorted(candles, key=lambda b: b[0])
    return float(candles[0][1]), float(candles[-1][4])


# ---------------- build positions -------------------------------------------
STEP = {"NIFTY": 50, "BANKNIFTY": 100}
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
COST = 220.0


def atm(ref_close, step):
    return int(round(ref_close / step)) * step


def build_index(idx):
    series = SPOTS[idx]
    dates = [d for d, _ in series]
    date_idx = {d: i for i, d in enumerate(dates)}
    me = month_ends(series)
    step, lot = STEP[idx], LOT[idx]
    positions = []  # one per signal month (non-FLAT), Dec-2024..Oct-2026
    sig_months = [ym for ym in sorted(me) if "2024-12" <= ym <= "2026-10"]
    for ym in sig_months:
        si = me[ym]
        state = trend_at(series, si)
        if state not in ("UP", "DOWN"):
            continue
        side = "CE" if state == "UP" else "PE"
        entry_ym = ym_next(ym)
        ei = first_day_of_month(series, entry_ym)
        exp1_nominal = expiry_for_month(entry_ym)
        pos = dict(index=idx, signal_month=ym, signal_date=dates[si],
                   trend=state, side=side, entry_month=entry_ym,
                   entry_date=dates[ei] if ei is not None else None,
                   strike1=atm(series[si][1], step), expiry1_nominal=exp1_nominal)
        positions.append(pos)
    return series, dates, date_idx, positions


def ym_next(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    m += 1
    if m == 13:
        y, m = y + 1, 1
    return f"{y:04d}-{m:02d}"


def score_index(idx):
    series, dates, date_idx, positions = build_index(idx)
    step, lot = STEP[idx], LOT[idx]
    trades = []
    nc = []
    for pos in positions:
        # --- leg 1 ---
        try:
            exp1_actual, km1 = key_map(idx, pos["expiry1_nominal"])
        except RateLimited:
            raise
        if not km1:
            nc.append({**pos, "hold": "1M+2M", "reason": "no_contracts_for_expiry"})
            continue
        pos["expiry1"] = exp1_actual
        b_in = day_bars(idx, exp1_actual, pos["strike1"], pos["side"],
                        pos["entry_date"])
        b_out = day_bars(idx, exp1_actual, pos["strike1"], pos["side"],
                         exp1_actual)
        if b_in is None or b_out is None:
            nc.append({**pos, "hold": "1M+2M", "reason": "no_candles_leg1"})
            continue
        e1, x1 = b_in[0], b_out[1]
        net1 = (x1 - e1) * lot - COST
        base = {**pos, "entry_premium1": e1, "exit_premium1": x1,
                "exit_date1": exp1_actual}
        trades.append({**base, "hold": "1M", "legs": 1, "net": round(net1, 2),
                       "exit_date": exp1_actual})
        # --- leg 2 (roll) ---
        xi = date_idx.get(exp1_actual)
        if xi is None:
            nc.append({**base, "hold": "2M", "reason": "expiry_not_in_spot_store"})
            continue
        roll_state = trend_at(series, xi)
        if roll_state == "FLAT":
            trades.append({**base, "hold": "2M", "legs": 1,
                           "net": round(net1, 2), "exit_date": exp1_actual,
                           "roll": "FLAT_stop"})
            continue
        # SPEC §2: FLAT stops the position; OTHERWISE it rolls on the SAME
        # side as leg 1 (the recompute is a FLAT check, not a direction check).
        entry2_i = next_trading_day(series, xi)
        exp2_nominal = expiry_for_month(ym_next(pos["entry_month"]))
        if entry2_i is None or exp2_nominal is None:
            nc.append({**base, "hold": "2M", "reason": "no_second_leg_calendar"})
            continue
        exp2_actual, km2 = key_map(idx, exp2_nominal)
        if not km2:
            nc.append({**base, "hold": "2M", "reason": "no_contracts_second_expiry"})
            continue
        strike2 = atm(series[xi][1], step)
        entry2_date = dates[entry2_i]
        b2_in = day_bars(idx, exp2_actual, strike2, pos["side"], entry2_date)
        b2_out = day_bars(idx, exp2_actual, strike2, pos["side"], exp2_actual)
        if b2_in is None or b2_out is None:
            nc.append({**base, "hold": "2M", "reason": "no_candles_leg2"})
            continue
        e2, x2 = b2_in[0], b2_out[1]
        net2 = net1 + (x2 - e2) * lot - COST
        trades.append({**base, "hold": "2M", "legs": 2, "net": round(net2, 2),
                       "exit_date": exp2_actual, "roll": "rolled",
                       "strike2": strike2, "entry_date2": entry2_date,
                       "entry_premium2": e2, "exit_premium2": x2,
                       "expiry2": exp2_actual})
    return trades, nc


def summarise(trades):
    out = {}
    for hold in ("1M", "2M"):
        by_year = {}
        for t in [x for x in trades if x["hold"] == hold]:
            by_year.setdefault(t["entry_date"][:4], []).append(t)
        out[hold] = {}
        for yr, ts in sorted(by_year.items()):
            ts_sorted = sorted(ts, key=lambda x: x["exit_date"])
            cum, peak, dd = 0.0, 0.0, 0.0
            for t in ts_sorted:
                cum += t["net"]
                peak = max(peak, cum)
                dd = min(dd, cum - peak)
            nets = [t["net"] for t in ts]
            halves = {}
            for lab, pred in (("H1_JanJun", lambda t: t["entry_date"][5:7] <= "06"),
                              ("H2_JulDec", lambda t: t["entry_date"][5:7] > "06")):
                hs = [t["net"] for t in ts if pred(t)]
                halves[lab] = dict(positions=len(hs), net=round(sum(hs), 2))
            out[hold][yr] = dict(
                positions=len(ts), net=round(sum(nets), 2),
                wr=round(100 * sum(1 for v in nets if v > 0) / len(nets), 1),
                best=round(max(nets), 2), worst=round(min(nets), 2),
                worst_drawdown=round(dd, 2), halves=halves)
    return out


def main():
    all_trades, all_nc, summary = [], [], {}
    try:
        for idx in ("NIFTY", "BANKNIFTY"):
            trades, nc = score_index(idx)
            all_trades += trades
            all_nc += nc
            summary[idx] = summarise(trades)
            print(idx, "trades:", len(trades), "nc:", len(nc), flush=True)
    except RateLimited:
        (OUT / "rate_limited.json").write_text(json.dumps(
            {"stopped": True, "note": "429 hard stop; rerun resumes from cache"}))
        print("RATE_LIMIT_STOP", flush=True)
        sys.exit(3)
    with open(TR / "nifty_longhold_trades.csv", "w", newline="") as f:
        cols = ["index", "hold", "signal_month", "signal_date", "trend", "side",
                "entry_month", "entry_date", "strike1", "expiry1",
                "entry_premium1", "exit_premium1", "exit_date1", "legs",
                "roll", "strike2", "entry_date2", "entry_premium2",
                "exit_premium2", "expiry2", "exit_date", "net"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for t in all_trades:
            w.writerow(t)
    sig = json.loads((OUT / "signals.json").read_text())
    result = dict(summary=summary,
                  annex={k: v["annex"] for k, v in sig.items()},
                  nc=all_nc, nc_count=len(all_nc),
                  trades_count=len(all_trades))
    (TR / "nifty_longhold_results.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(summary, indent=1))
    print("NC:", len(all_nc))
    for n in all_nc:
        print(" NC", n["index"], n.get("signal_month"), n.get("hold"),
              n.get("reason"))


if __name__ == "__main__":
    main()