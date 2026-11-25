#!/usr/bin/env python3
"""BTST-IND BANK VOTES-ONLY SHADOW SCORER — forward paper evidence
for the one non-failed row of the BTST-IND programme (2026-11-15):
Bank Nifty overnight holds decided by the EKAM 6-vote state alone.

WHAT THIS IS: a SCORE-ONLY paper shadow. It is a WATCH candidate,
NOT a pass, and it is armed nowhere. The backtest row it shadows
(btst_ind_2026-11-15.md, spec btst_ind_SPEC.md): 104 trades,
Jan-Oct 2026, +Rs98,630.50, WR 50.0%, halves +Rs39,016.00 /
+Rs59,614.50, random-entry placebo 97.8th percentile — BUT
ex-top-3 only +Rs9,290.50 (the row is TOP-HEAVY: its profit
concentrates in a few big gap nights) and the worst single night
was -Rs17,036.50 on 1 lot. Overnight gap risk is inherent and
unhedgeable; the ledger records the actual overnight move of
every trade so the forward evidence shows the gaps as they
happen. This scorer only collects forward evidence, one evening
at a time, from Mon 2026-11-16 to the Nov 30 verdicts (the
review bound).

FROZEN RULE (btst_ind_SPEC.md index arm, VOTES row, verbatim):
- Compute the EKAM 6-vote state on Bank Nifty 5-min spot bars at
  the 15:00 bar (causal): VWAP side (futures session VWAP) .
  EMA(9,21) . Supertrend(7,3) . MACD(12,26,9) . RSI(14) zone
  (long 50<=RSI<70, short 30<RSI<=50) . ADX(14)>=20 adds +1 to
  the leading side. LV/SV in 0..6.
- If LV >= 5: buy the near-ATM CE. If SV >= 5: buy the near-ATM
  PE. (Both >= 5 is arithmetically impossible: LV + SV <= 6.)
  Otherwise no trade.
- Contract: strike = 100-step nearest the spot close of the
  day's 15:10 bar (exact half rounds up), in-force expiry.
- ENTRY fill = close of the contract's premium bar stamped
  15:15 on the entry day. EXIT fill = close of the same
  contract's premium bar stamped 09:30 on the next trading day.
- Net = (exit - entry) x 30 - Rs220. 1 lot (30). BUYING ONLY.
- Missing entry or exit premium bar in the backtest was NC,
  counted, never substituted; the shadow keeps the same rule.

MACHINERY: the indicator / VWAP / premium machinery is
btst_ind_build.py's bank_ctx() copied verbatim (it was itself
copied frozen from ekam_intraday_bank_build.py), with three
documented sourcing extensions, none of which changes any
stored-day value:
  1. The build's timestamp filter (<= "2026-11-13" at midnight)
     silently dropped 2026-11-13's own bars, so its series ended
     Nov 12. This scorer filters by DATE, so Nov 13 is included
     and the Nov 2-13 seed window is complete. All indicators are
     causal: appending Nov 13 changes no earlier value.
  2. The OI expiry map ends 2026-11-11. Exactly as in the build,
     stored days not in the map get NO futures-VWAP vote (their
     stored LV/SV are the build's own). For FORWARD days
     (> 2026-11-13) the map simply does not extend, so the
     VWAP uses the in-force expiry's futures contract — the
     frozen 6-vote system requires the vote; without this the
     shadow would silently score a different, 5-vote rule.
  3. Expiry candidates for the trade contract extend the map's
     values with {2026-11-23, 2026-12-29} so days after the
     November expiry resolve to the December monthly; stored
     days resolve exactly as the build's expiry_fn resolved
     them.
Forward-day data: spot bars and futures bars are fetched via
the v3 route (r4d1_shadow_score.py's pattern: futures keys from
round2_history/futures_keys.json + round4_history/
futures_keys_fwd.json, refreshed from the Upstox instruments
master when an expiry is unknown) and cached
(btstind_spot_fwd.json / btstind_fut_fwd.json). Premium bars:
the build's prem_store verbatim (round5 C5 store, then
daily2leg/prem_bank.json, then the fetched-candle folders incl.
oi_buildup_data), then round 1's fetch machinery
(oi_buildup_score.fetch_bars) for forward days only. A day that
still cannot be sourced is UNSCORED with the reason named —
never estimated.

RUN SHAPE (one evening run per day, two logical steps):
  (a) SETTLE: any OPEN position entered on the previous trading
      day is settled at today's 09:30 premium bar close of the
      same contract (its entry-date ledger row is updated in
      place: exit fields, overnight premium move in points,
      overnight spot gap %, net). A missing 09:30 bar NCs the
      position with the reason named, exactly as the backtest
      counted it.
  (b) ENTER: today's 15:00 votes are evaluated; a triggered
      entry is recorded OPEN at today's 15:15 premium bar close.
Entries stop after 2026-11-30 (the review bound). An OPEN
position from Nov 30 still settles on the next available
trading day; that settlement is labelled past_bound_settlement
in the row's notes.

LEDGER: november_shadow_btstind_bank_log.csv — one row per
entry day (BACKFILL_COUNTERFACTUAL for the Nov 2-13 seeds,
SCORED forward), status TRADED (settled) / OPEN (awaiting
settlement) / NO_TRADE / NC + the reason named, idempotent per
date. The forward tally excludes the seeds.

DRY-RUN VERIFICATION (2026-11-15, --verify): the scorer's
machinery reproduces the build's Jan-Oct VOTES row EXACTLY —
104 trades, +Rs98,630.50, every trade's date/side/strike/
expiry/entry/exit/net identical to btst_ind_trades.csv — and
its November pass over Nov 2-13 (the build's own window ended
Oct 31, so November was never in btst_ind_trades.csv; the seeds
are the build's frozen machinery applied to November, the same
basis as the premium-tape shadow's November CF) gives 4 settled
trades, +Rs14,336.00 (Nov 2 CE 54900 +Rs7,409.00 . Nov 5 CE
57800 -Rs2,555.50 . Nov 9 CE 59600 +Rs15,924.50 . Nov 11 PE
60500 -Rs6,442.00), 5 NO_TRADE days, no open position.
--seed-backfill writes those rows only after the same
reproduction passes.

Paper only, real money Rs0. No live orders. Every
api.upstox.com call carries the browser User-Agent. On HTTP
429: HARD STOP for the run — the day is marked NC rate_limited,
no retry, no route switch.

Usage:
    python3 btstind_shadow_score.py [--date YYYY-MM-DD]
                        [--dry-run] [--verify] [--seed-backfill]
Default date = today (IST). --dry-run computes and prints but
writes NOTHING (forward fetches are not cached either).
--verify is a hard-wired no-write check (Jan-Oct reproduction +
November pass; bypasses the start/window guards, never writes,
makes no API calls). --seed-backfill writes ONLY the Nov 2-13
BACKFILL_COUNTERFACTUAL rows, and only if the reproduction
passes.
"""
import argparse, bisect, csv, gzip, io, json, math, sys
import importlib.util
import urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
LAST_STORED = "2026-11-13"  # last day of the build's stored stores
COST = 220.0
LOT = 30
STEP = 100
VOTE_STAMP, FILL_STAMP = "15:00", "15:15"
EXIT_STAMP = "09:30"
MIN_DAY_BARS = 70           # a real session has 75 5-min bars
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
MASTER_URL = ("https://assets.upstox.com/market-quote/instruments/"
              "exchange/complete.csv.gz")
LEDGER = TR / "november_shadow_btstind_bank_log.csv"
SPOT_FWD = TR / "btstind_spot_fwd.json"
FUT_FWD = TR / "btstind_fut_fwd.json"
FUT_KEYS_FWD = TR / "round4_history/futures_keys_fwd.json"
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
EXPECT_JANOCT_TRADES = 104
EXPECT_JANOCT_TOTAL = 98630.50
EXPECT_NOV_TRADES = 4
EXPECT_NOV_TOTAL = 14336.00

LEDGER_FIELDS = ["date", "row_type", "status", "reason",
                 "votes_long", "votes_short", "side", "strike",
                 "expiry", "entry_time", "entry_premium",
                 "exit_date", "exit_time", "exit_premium",
                 "overnight_move_pts", "spot_gap_pct", "net_inr",
                 "timing_violations", "notes"]

_spec = importlib.util.spec_from_file_location(
    "oi_buildup_score", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)


class RateLimited(Exception):
    pass


_token = None
for _line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if _line.startswith("UPSTOX_ACCESS_TOKEN="):
        _token = _line.split("=", 1)[1].strip()
assert _token


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {_token}",
        "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return None


# ======================================================================
# FORWARD-DAY SPOT (v3 route; r4d1/regime-rev pattern)
# ======================================================================
def _fetch_spot_day(day):
    """(state, bars): state 'ok' (bars = {time: (o,h,l,c)}),
    'empty' (successful response, zero candles — a non-trading
    day), 'fail' (no usable response). Raises RateLimited.
    Fix (2026-11-25): for day == today (IST), fall back to the v3
    intraday endpoint because the v3 historical range endpoint lags
    by one day for the newest session."""
    ikey = quote(obs.IDXKEY["BANKNIFTY"], safe="")
    today_s = datetime.now(IST).date().isoformat()
    body = get(f"{API}/v3/historical-candle/{ikey}"
               f"/minutes/5/{day}/{day}")
    cd = [c for c in (((body or {}).get("data") or {}).get("candles")
                      or []) if c[0][:10] == day]
    if not cd and day == today_s:
        body = get(f"{API}/v3/historical-candle/intraday/{ikey}/minutes/5")
        cd = [c for c in (((body or {}).get("data") or {}).get("candles")
                          or []) if c[0][:10] == day]
    if body is None:
        return "fail", None
    if not cd:
        return "empty", None
    return "ok", {c[0][11:16]: (float(c[1]), float(c[2]),
                                float(c[3]), float(c[4]))
                  for c in cd}


def _spot_fwd_cache():
    if SPOT_FWD.exists():
        return json.loads(SPOT_FWD.read_text())
    return {}


def spot_day_forward(day, dry):
    """Bars for a forward day (> LAST_STORED) from this scorer's
    cache or the v3 route. Returns (state, bars, source) with
    state 'ok' / 'empty' (non-trading) / 'fail'."""
    cache = _spot_fwd_cache()
    if day in cache:
        return "ok", {b[0]: tuple(b[1:]) for b in cache[day]}, \
            "fwd_cache"
    state, bars = _fetch_spot_day(day)  # may raise RateLimited
    if state != "ok":
        return state, None, None
    if len(bars) < MIN_DAY_BARS:
        return "fail", None, f"spot_fragment_{len(bars)}_bars"
    if not dry:
        cache[day] = [[t] + list(v) for t, v in sorted(bars.items())]
        SPOT_FWD.write_text(json.dumps(cache))
    return "ok", bars, "fetched_v3"


# ======================================================================
# FUTURES KEYS + FORWARD FUTURES BARS (r4d1 pattern)
# ======================================================================
def _fut_universe():
    """{expiry: (key, route)} — round 2 keys extended by the
    forward keys file (instruments-master live contracts)."""
    uni = {}
    r2 = json.loads((TR / "round2_history/futures_keys.json")
                    .read_text())
    for e, v in r2.items():
        uni[e] = (v["key"], "expired" if v["route"] == "expired"
                  else "live")
    if FUT_KEYS_FWD.exists():
        for e, v in json.loads(FUT_KEYS_FWD.read_text()).items():
            uni.setdefault(e, (v["key"], "live"))
    return uni


def _refresh_fut_keys(uni, dry):
    req = urllib.request.Request(MASTER_URL,
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return uni
    rows = csv.DictReader(io.StringIO(
        gzip.decompress(raw).decode()))
    fwd = {}
    if FUT_KEYS_FWD.exists():
        fwd = json.loads(FUT_KEYS_FWD.read_text())
    for r in rows:
        if (r.get("instrument_type") == "FUTIDX"
                and r.get("name") == "BANKNIFTY" and r.get("expiry")):
            fwd[r["expiry"]] = dict(key=r["instrument_key"],
                                    symbol=r["tradingsymbol"],
                                    lot=r.get("lot_size"))
            uni.setdefault(r["expiry"], (r["instrument_key"], "live"))
    if not dry:
        FUT_KEYS_FWD.write_text(json.dumps(fwd, indent=1))
    return uni


def _fetch_fut_day(key, route, day, exp=None):
    """{time: (o,h,l,c,v)} or None. Raises RateLimited on 429.
    Fix (2026-11-25):
      1. Only switch a live contract to the v2 expired route when the
         CONTRACT EXPIRY (`exp`) < today (previously checked `day < today`,
         which broke catch-up fetches on unexpired contracts).
      2. For day == today on a live contract, fall back to the v3 intraday
         route because the v3 historical range route lags by one day."""
    today_s = datetime.now(IST).date().isoformat()
    if route == "live" and exp is not None and exp < today_s:
        route = "expired"
    enc = quote(key, safe="")
    if route == "expired":
        url = (f"{API}/v2/expired-instruments/historical-candle/"
               f"{enc}/5minute/{day}/{day}")
    else:
        url = (f"{API}/v3/historical-candle/{enc}/minutes/5/"
               f"{day}/{day}")
    body = get(url)
    cd = [c for c in (((body or {}).get("data") or {}).get("candles")
                      or []) if c[0][:10] == day]
    if not cd and route != "expired" and day == today_s:
        body = get(f"{API}/v3/historical-candle/intraday/{enc}/minutes/5")
        cd = [c for c in (((body or {}).get("data") or {}).get("candles")
                          or []) if c[0][:10] == day]
    if not cd:
        return None
    return {c[0][11:16]: (float(c[1]), float(c[2]), float(c[3]),
                          float(c[4]), float(c[5])) for c in cd}


# ======================================================================
# BANK CONTEXT — btst_ind_build.bank_ctx() copied verbatim, with the
# three documented sourcing extensions (module docstring). Indicator
# and vote functions are the build's own code, unchanged.
# ======================================================================
_fut7 = {}


def _fut7_file(exp):
    if exp not in _fut7:
        fn = TR / f"round5_history/FUT7_{exp}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (
                    float(r[2]), float(r[3]), float(r[4]),
                    float(r[5]), float(r[6]))
        _fut7[exp] = byd
    return _fut7[exp]


def _fut_fwd_cache():
    if FUT_FWD.exists():
        return json.loads(FUT_FWD.read_text())
    return {}


def fut_day_ext(exp, day, dry, allow_fetch):
    """The build's fut_day(exp, day) -> {time: (o,h,l,c,v)} or
    None, extended: FUT7 file first (the build's source), then
    this scorer's forward cache, then (forward days only) the
    r4d1-style futures fetch."""
    byd = _fut7_file(exp)
    if day in byd:
        return byd[day]
    if not allow_fetch:
        return None
    cache = _fut_fwd_cache()
    ck = f"{exp}|{day}"
    if ck in cache:
        return {r[0]: tuple(r[1:]) for r in cache[ck]}
    uni = _fut_universe()
    if exp not in uni:
        uni = _refresh_fut_keys(uni, dry)
    if exp not in uni:
        return None
    key, route = uni[exp]
    bars = _fetch_fut_day(key, route, day, exp=exp)  # may raise RateLimited
    if not bars or len(bars) < MIN_DAY_BARS:
        return None
    if not dry:
        cache[ck] = [[t] + list(v) for t, v in sorted(bars.items())]
        FUT_FWD.write_text(json.dumps(cache))
    return bars


def _ema_series(c, period):
    n = len(c); out = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(c[:period]) / period
    for i in range(period, n):
        out[i] = c[i] * k + out[i - 1] * (1 - k)
    return out


def _wilder_atr(h, l, c, period=7):
    n = len(c); tr = [None] * n; atr = [None] * n
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]),
                    abs(l[i] - c[i - 1]))
    if n > period:
        atr[period] = sum(tr[1:period + 1]) / period
        for i in range(period + 1, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def _supertrend(h, l, c, period=7, mult=3.0):
    n = len(c); atr = _wilder_atr(h, l, c, period)
    direc = [None] * n; fu = [None] * n; fl = [None] * n
    for i in range(n):
        if atr[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2.0
        bu = hl2 + mult * atr[i]; bl = hl2 - mult * atr[i]
        if fu[i - 1] is None:
            fu[i], fl[i] = bu, bl
            direc[i] = "up" if c[i] >= hl2 else "down"
            continue
        fu[i] = bu if (bu < fu[i - 1] or c[i - 1] > fu[i - 1]) \
            else fu[i - 1]
        fl[i] = bl if (bl > fl[i - 1] or c[i - 1] < fl[i - 1]) \
            else fl[i - 1]
        if direc[i - 1] == "up":
            direc[i] = "down" if c[i] < fl[i] else "up"
        else:
            direc[i] = "up" if c[i] > fu[i] else "down"
    return direc


def _rsi_wilder(c, period=14):
    n = len(c); out = [None] * n
    if n <= period:
        return out
    gains = [max(c[i] - c[i - 1], 0.0) for i in range(1, n)]
    losses = [max(c[i - 1] - c[i], 0.0) for i in range(1, n)]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period

    def _r(ag_, al_):
        return 100.0 if al_ == 0 else 100.0 - 100.0 / (1.0 + ag_ / al_)
    out[period] = _r(ag, al)
    for i in range(period + 1, n):
        ag = (ag * (period - 1) + gains[i - 1]) / period
        al = (al * (period - 1) + losses[i - 1]) / period
        out[i] = _r(ag, al)
    return out


def _macd_from(c, fast=12, slow=26, sig=9):
    ef, es = _ema_series(c, fast), _ema_series(c, slow)
    n = len(c); line = [None] * n
    for i in range(n):
        if ef[i] is not None and es[i] is not None:
            line[i] = ef[i] - es[i]
    start = next(i for i in range(n) if line[i] is not None)
    vals = [line[i] for i in range(start, n)]
    sigv = _ema_series(vals, sig)
    signal = [None] * n
    for j, i in enumerate(range(start, n)):
        signal[i] = sigv[j]
    return line, signal


def _adx_wilder(h, l, c, period=14):
    n = len(c)
    tr = [0.0] * n; pdm = [0.0] * n; ndm = [0.0] * n
    for i in range(1, n):
        up_move = h[i] - h[i - 1]; dn_move = l[i - 1] - l[i]
        pdm[i] = up_move if (up_move > dn_move and up_move > 0) else 0.0
        ndm[i] = dn_move if (dn_move > up_move and dn_move > 0) else 0.0
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]),
                    abs(l[i] - c[i - 1]))
    dx = [None] * n
    if n > period:
        str_ = sum(tr[1:period + 1]); sp = sum(pdm[1:period + 1])
        sn = sum(ndm[1:period + 1])
        for i in range(period, n):
            if i > period:
                str_ = str_ - str_ / period + tr[i]
                sp = sp - sp / period + pdm[i]
                sn = sn - sn / period + ndm[i]
            if str_ > 0:
                dip = 100.0 * sp / str_; din = 100.0 * sn / str_
                dx[i] = 0.0 if (dip + din) == 0 else \
                    100.0 * abs(dip - din) / (dip + din)
    out = [None] * n
    first = 2 * period - 1
    if n > first and all(dx[j] is not None
                         for j in range(period, first + 1)):
        out[first] = sum(dx[period:first + 1]) / period
        for i in range(first + 1, n):
            if dx[i] is not None and out[i - 1] is not None:
                out[i] = (out[i - 1] * (period - 1) + dx[i]) / period
    return out


def _compute_ind(O_, H_, L_, C_):
    ml, ms = _macd_from(list(C_))
    return dict(e9=_ema_series(list(C_), 9),
                e21=_ema_series(list(C_), 21),
                st=_supertrend(list(H_), list(L_), list(C_), 7, 3.0),
                ml=ml, ms=ms, rsi=_rsi_wilder(list(C_)),
                adx=_adx_wilder(list(H_), list(L_), list(C_)))


def _votes_at_bar(C, gi, ind, vwap_val):
    ld = sd = 0
    if vwap_val is not None:
        if C[gi] > vwap_val: ld += 1
        elif C[gi] < vwap_val: sd += 1
    e9, e21 = ind["e9"][gi], ind["e21"][gi]
    if e9 is not None and e21 is not None:
        if e9 > e21: ld += 1
        elif e9 < e21: sd += 1
    if ind["st"][gi] == "up": ld += 1
    elif ind["st"][gi] == "down": sd += 1
    ml, ms = ind["ml"][gi], ind["ms"][gi]
    if ml is not None and ms is not None:
        if ml > ms: ld += 1
        elif ml < ms: sd += 1
    r = ind["rsi"][gi]
    if r is not None:
        if 50 <= r < 70: ld += 1
        if 30 < r <= 50: sd += 1
    a = ind["adx"][gi]
    L_, S_ = ld, sd
    if a is not None and a >= 20:
        if ld > sd: L_ = ld + 1
        elif sd > ld: S_ = sd + 1
    return L_, S_


# ---- premium: the build's prem_store, verbatim ----------------------
_c5 = {}


def _prem_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = TR / f"round5_history/C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (
                    float(r[2]), float(r[3]), float(r[4]),
                    float(r[5]))
        _c5[ck] = byd
    return _c5[ck].get(day)


PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
_prem_cache = {}


def prem_store(exp, strike, typ, day):
    ck = (exp, strike, typ, day)
    if ck in _prem_cache:
        return _prem_cache[ck]
    res = _prem_c5(exp, strike, typ, day)
    if not res:
        cd = PREM_B.get(f"{exp}|{int(strike)}|{typ}", {}).get(day)
        if cd:
            res = {t: tuple(float(x) for x in v)
                   for t, v in cd.items()}
    if not res:
        for folder in ("btst_data", "november_shadow_data",
                       "nifty_weekly_expiry_chain", "oi_buildup_data"):
            fn = TR / folder / \
                f"candles_BANKNIFTY_{int(strike)}{typ}_{exp}_{day}.json"
            if fn.exists():
                body = json.loads(fn.read_text())
                rows = [c for c in ((body.get("data") or {})
                                    .get("candles") or [])
                        if c[0][:10] == day]
                if rows:
                    res = {c[0][11:16]: (float(c[1]), float(c[2]),
                                         float(c[3]), float(c[4]))
                           for c in rows}
                    break
    _prem_cache[ck] = res
    return res


def prem_bars_ext(exp, strike, typ, day, allow_fetch):
    """(bars_dict, source): the build's prem_store first; for
    forward days only, round 1's fetch machinery as fallback
    (caches into oi_buildup_data in the shared convention)."""
    res = prem_store(exp, strike, typ, day)
    if res:
        return res, "store"
    if not allow_fetch:
        return None, None
    try:
        bars = obs.fetch_bars("BANKNIFTY", exp, strike, typ, day)
    except Exception as e:
        if type(e).__name__ == "RateLimited" or \
                getattr(obs, "RateLimited", None) is type(e):
            raise RateLimited()
        bars = None
    if bars:
        return {b[0]: (b[1], b[2], b[3], b[4]) for b in bars}, \
            "fetched"
    return None, None


# ---- context ---------------------------------------------------------
def build_ctx(through_day, dry, allow_fetch):
    """The build's bank context over the spot series from
    2026-01-01 through `through_day`. Stored days come from the
    progressive store exactly as the build reads them; forward
    days (> LAST_STORED) are appended in date order from this
    scorer's cache / the v3 route. Chain integrity: the first
    forward weekday that cannot be sourced stops the append
    (a successful-but-empty response marks a non-trading day
    and is skipped); later days are NOT appended past a gap.
    Returns (ctx, appended_days, gap_day)."""
    spot = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
    add_rows = []
    appended, gap_day = [], None
    if through_day > LAST_STORED:
        d = datetime.strptime(LAST_STORED, "%Y-%m-%d").date() \
            + timedelta(days=1)
        end = datetime.strptime(through_day, "%Y-%m-%d").date()
        while d <= end:
            if d.weekday() < 5:  # Mon-Fri only; markets shut weekends
                day = d.isoformat()
                state, bars, _src = spot_day_forward(day, dry) \
                    if allow_fetch else ("fail", None, None)
                if state == "ok":
                    for t in sorted(bars):
                        o, h, l, c = bars[t]
                        add_rows.append({
                            "timestamp": f"{day} {t}:00+05:30",
                            "open": o, "high": h, "low": l,
                            "close": c})
                    appended.append(day)
                elif state == "empty":
                    pass  # non-trading day (holiday): skip, chain intact
                else:
                    gap_day = day
                    break
            d += timedelta(days=1)
    if add_rows:
        spot = pd.concat([spot, pd.DataFrame(add_rows)],
                         ignore_index=True)
    spot["timestamp"] = pd.to_datetime(
        spot["timestamp"]).dt.tz_localize(None)
    spot["date"] = spot["timestamp"].dt.strftime("%Y-%m-%d")
    spot = spot[(spot["date"] >= "2026-01-01")
                & (spot["date"] <= through_day)] \
        .sort_values("timestamp")
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    O = spot["open"].to_numpy(float); H = spot["high"].to_numpy(float)
    L = spot["low"].to_numpy(float);  C = spot["close"].to_numpy(float)
    DATES = spot["date"].tolist(); TIMES = spot["time"].tolist()
    day_idx = {}
    for i, d in enumerate(DATES):
        day_idx.setdefault(d, []).append(i)
    EXP = {}
    with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
        for r in csv.DictReader(f):
            EXP[r["date"]] = r["expiry"]
    all_exps = sorted(set(EXP.values())
                      | {"2026-11-23", "2026-12-29"})

    def expiry_fn(day):
        e = EXP.get(day)
        if e is not None and e > day:
            return e
        nxt = [x for x in all_exps if x > day]
        return nxt[0] if nxt else None

    def vwap_series(exp, day):
        fd = fut_day_ext(exp, day, dry, allow_fetch)
        if not fd:
            return None
        out, cum_pv, cum_v = {}, 0.0, 0.0
        for t in sorted(fd):
            o, h, l, c, v = fd[t]
            tp = (h + l + c) / 3.0
            cum_pv += tp * v; cum_v += v
            out[t] = cum_pv / cum_v if cum_v > 0 else None
        return out

    def day_vwap(exp, day):
        raw = vwap_series(exp, day)
        if raw is None:
            return None
        ftimes = sorted(raw)
        out = {}
        for gi in day_idx[day]:
            t = TIMES[gi]
            j = bisect.bisect_right(ftimes, t) - 1
            out[t] = raw[ftimes[j]] if j >= 0 else None
        return out

    IND = _compute_ind(O, H, L, C)
    VWAP_BY_DAY = {}
    vwap_missing_fwd = []
    for d in day_idx:
        if d in EXP:
            vw = day_vwap(EXP[d], d)
        elif d <= LAST_STORED:
            continue  # build treatment: unmapped stored day, no VWAP
        else:
            e = expiry_fn(d)
            vw = day_vwap(e, d) if e else None
            if vw is None:
                vwap_missing_fwd.append(d)
        if vw is not None:
            VWAP_BY_DAY[d] = vw
    LV = [0] * len(C); SV = [0] * len(C)
    for d, idxs in day_idx.items():
        vw = VWAP_BY_DAY.get(d)
        for gi in idxs:
            v = vw.get(TIMES[gi]) if vw else None
            LV[gi], SV[gi] = _votes_at_bar(C, gi, IND, v)
    return (dict(kind="BANK", step=STEP, lot=LOT,
                 days=sorted(day_idx), day_idx=day_idx, TIMES=TIMES,
                 DATES=DATES, C=C, O=O, H=H, L=L, LV=LV, SV=SV,
                 expiry_fn=expiry_fn,
                 vwap_missing_fwd=vwap_missing_fwd),
            appended, gap_day)


def nearest_step(x, step):
    return int(step * math.floor(x / step + 0.5))


# ======================================================================
# ENTRY EVALUATION + SETTLEMENT (the build's VOTES branch, split
# across the overnight boundary exactly as the rule states)
# ======================================================================
def _blank_row(D, row_type):
    row = {k: "" for k in LEDGER_FIELDS}
    row["date"] = D
    row["row_type"] = row_type
    return row


def evaluate_entry(ctx, D, allow_fetch, row_type="SCORED"):
    """Today's step (b): the 15:00 votes and, if triggered, the
    OPEN position at the 15:15 premium bar close."""
    row = _blank_row(D, row_type)
    idxs = ctx["day_idx"].get(D)
    if idxs is None:
        row.update(status="NC", reason="not_a_trading_day")
        return row
    vgi = next((gi for gi in idxs
                if ctx["TIMES"][gi] == VOTE_STAMP), None)
    if vgi is None:
        row.update(status="NC", reason="no_1500_bar")
        return row
    lv, sv = int(ctx["LV"][vgi]), int(ctx["SV"][vgi])
    row.update(votes_long=str(lv), votes_short=str(sv))
    if D in ctx["vwap_missing_fwd"]:
        row.update(status="NC", reason="futures_unserved",
                   notes="futures VWAP unavailable; votes not "
                         "faithful to the frozen 6-vote rule")
        return row
    side = 1 if lv >= 5 else (-1 if sv >= 5 else 0)
    if side == 0:
        row.update(status="NO_TRADE", reason="votes_below_5")
        return row
    ref = next((float(ctx["C"][gi]) for gi in idxs
                if ctx["TIMES"][gi] == "15:10"), None)
    if ref is None:
        row.update(status="NC", reason="no_1510_bar")
        return row
    strike = nearest_step(ref, STEP)
    typ = "CE" if side == 1 else "PE"
    exp = ctx["expiry_fn"](D)
    row.update(side=typ, strike=str(strike), expiry=exp or "")
    if exp is None:
        row.update(status="NC", reason="no_expiry")
        return row
    prem, psrc = prem_bars_ext(exp, strike, typ, D, allow_fetch)
    if not prem or FILL_STAMP not in prem:
        row.update(status="NC", reason="no_entry_bar",
                   notes=f"premium={psrc}")
        return row
    entry = float(prem[FILL_STAMP][3])
    # TIMING ASSERTION (the build's): the fill stamp is strictly
    # after the vote stamp.
    viol = 0 if FILL_STAMP > VOTE_STAMP else 1
    row["timing_violations"] = str(viol)
    assert viol == 0, "timing violation on scored entry"
    row.update(status="OPEN", reason="entered",
               entry_time=FILL_STAMP, entry_premium=f"{entry:.2f}",
               notes=f"premium={psrc}")
    return row


def settle_row(ctx, row, exit_day, allow_fetch, past_bound=False,
               late=False):
    """Step (a): settle an OPEN row at the exit day's 09:30
    premium bar close of the same contract. Updates the row in
    place and returns it."""
    exp, strike, typ = row["expiry"], int(row["strike"]), row["side"]
    prem, psrc = prem_bars_ext(exp, strike, typ, exit_day,
                               allow_fetch)
    if not prem or EXIT_STAMP not in prem:
        row.update(status="NC", reason="no_exit_bar",
                   exit_date=exit_day,
                   notes=(row["notes"] +
                          f"; settle@{exit_day}: premium={psrc}")
                          .strip("; "))
        return row
    xp = float(prem[EXIT_STAMP][3])
    entry = float(row["entry_premium"])
    net = round((xp - entry) * LOT - COST, 2)
    # overnight spot gap: entry day's last close -> exit day's
    # 09:15 open, from the same spot series.
    gap_pct = ""
    ei = ctx["day_idx"].get(row["date"])
    xi = ctx["day_idx"].get(exit_day)
    if ei and xi:
        last_close = float(ctx["C"][ei[-1]])
        open_915 = next((float(ctx["O"][gi]) for gi in xi
                         if ctx["TIMES"][gi] == "09:15"), None)
        if open_915 is not None and last_close:
            gap_pct = f"{(open_915 - last_close) / last_close * 100:.3f}"
    viol = 0 if (exit_day > row["date"]
                 and row["entry_time"] == FILL_STAMP) else 1
    row["timing_violations"] = str(viol)
    assert viol == 0, "timing violation on settlement"
    notes = row["notes"] + f"; settled@{exit_day} premium={psrc}"
    if late:
        notes += "; settled_late"
    if past_bound:
        notes += "; past_bound_settlement"
    row.update(status="TRADED", reason="scored",
               exit_date=exit_day, exit_time=EXIT_STAMP,
               exit_premium=f"{xp:.2f}",
               overnight_move_pts=f"{xp - entry:.2f}",
               spot_gap_pct=gap_pct, net_inr=f"{net:.2f}",
               notes=notes)
    return row


def next_series_day(ctx, D):
    days = ctx["days"]
    i = days.index(D) if D in days else None
    if i is None or i + 1 >= len(days):
        return None
    return days[i + 1]


# ======================================================================
# LEDGER
# ======================================================================
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def write_rows(new_rows):
    rows = ledger_rows()
    dates = {r["date"] for r in new_rows}
    rows = [r for r in rows if r["date"] not in dates]
    rows.extend(new_rows)
    rows.sort(key=lambda r: (r["date"], r["row_type"]))
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)


# ======================================================================
# VERIFY + SEED (no API calls; stored stores only)
# ======================================================================
def _historical_ctx():
    ctx, _app, _gap = build_ctx(LAST_STORED, dry=True,
                                allow_fetch=False)
    return ctx


def _score_window(ctx, days, row_type):
    """Evaluate + settle-in-window for a list of entry days,
    stored sourcing only (the build's own basis)."""
    out = []
    for D in days:
        row = evaluate_entry(ctx, D, allow_fetch=False,
                             row_type=row_type)
        if row["status"] == "OPEN":
            nd = next_series_day(ctx, D)
            if nd is not None:
                row = settle_row(ctx, row, nd, allow_fetch=False)
        out.append(row)
    return out


def _janoct_check(ctx):
    ref = {}
    with open(TR / "btst_ind_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["arm"] == "bank" and r["row"] == "VOTES":
                ref[r["date"]] = r
    days = [d for d in ctx["days"] if "2026-01-01" <= d <= "2026-10-31"]
    rows = _score_window(ctx, days, "VERIFY")
    mine = {r["date"]: r for r in rows if r["status"] == "TRADED"}
    mism = []
    for D, r in ref.items():
        m = mine.get(D)
        if m is None:
            mism.append(f"{D}: missing")
            continue
        if not (m["side"] == r["side"]
                and int(m["strike"]) == int(float(r["strike"]))
                and m["expiry"] == r["expiry"]
                and abs(float(m["entry_premium"])
                        - float(r["entry"])) < 1e-9
                and abs(float(m["exit_premium"])
                        - float(r["exit"])) < 1e-9
                and m["exit_date"] == r["next_day"]
                and abs(float(m["net_inr"]) - float(r["net"])) < 1e-9):
            mism.append(f"{D}: differs")
    extra = [D for D in mine if D not in ref]
    total = round(sum(float(r["net_inr"]) for r in mine.values()), 2)
    ok = (len(mine) == EXPECT_JANOCT_TRADES
          and total == EXPECT_JANOCT_TOTAL
          and not mism and not extra)
    return ok, mine, total, mism, extra


def verify_and_seed(seed):
    try:
        ctx = _historical_ctx()
    except RateLimited:
        print("BTST-IND BANK VOTES SHADOW VERIFY: rate limited — "
              "nothing written.")
        return 3
    ok, mine, total, mism, extra = _janoct_check(ctx)
    print(f"BTST-IND BANK VOTES SHADOW VERIFY (Jan-Oct 2026): "
          f"trades={len(mine)} total={total:+.2f} vs build "
          f"{EXPECT_JANOCT_TRADES} trades / "
          f"{EXPECT_JANOCT_TOTAL:+.2f} — "
          f"{'PASS — exact reproduction' if ok else 'FAIL'}"
          + (f" (mismatches={mism[:5]} extra={extra[:5]})"
             if not ok else ""))
    nov = _score_window(ctx, NOV_DAYS, "BACKFILL_COUNTERFACTUAL")
    ntr = [r for r in nov if r["status"] == "TRADED"]
    ntot = round(sum(float(r["net_inr"]) for r in ntr), 2)
    for r in nov:
        print(f"  {r['date']}: {r['status']} {r['reason']} "
              f"votes={r['votes_long'] or '-'}/{r['votes_short'] or '-'} "
              f"{r['side'] or ''} {r['strike'] or ''} "
              f"net={r['net_inr'] or '-'}")
    nov_ok = (len(ntr) == EXPECT_NOV_TRADES
              and ntot == EXPECT_NOV_TOTAL)
    print(f"BTST-IND BANK VOTES SHADOW NOVEMBER (Nov 2-13): "
          f"settled={len(ntr)} total={ntot:+.2f} vs expected "
          f"{EXPECT_NOV_TRADES} / {EXPECT_NOV_TOTAL:+.2f} — "
          f"{'PASS' if nov_ok else 'FAIL'}")
    if not (ok and nov_ok):
        print("Nothing written.")
        return 1
    if seed:
        write_rows(nov)
        print(f"Seeded {len(nov)} BACKFILL_COUNTERFACTUAL rows "
              f"into {LEDGER.name} ({len(ntr)} settled trades, "
              f"{ntot:+.2f}; forward tally excludes them).")
    else:
        print("(--verify: nothing written.)")
    return 0


# ======================================================================
# FORWARD RUN
# ======================================================================
def score_run(T, dry):
    written = []
    try:
        ctx, _app, gap_day = build_ctx(T, dry, allow_fetch=True)
    except RateLimited:
        row = _blank_row(T, "SCORED")
        row.update(status="NC", reason="rate_limited")
        if T <= WINDOW_END:
            written.append(row)
            if not dry:
                write_rows(written)
            return row, written
        return row, written
    in_series = T in ctx["day_idx"]
    # (a) settle OPEN positions at today's 09:30 bar
    if in_series:
        for r in ledger_rows():
            if r["status"] != "OPEN":
                continue
            if not (r["date"] < T):
                continue
            expected = next_series_day(ctx, r["date"])
            late = expected is not None and expected != T
            try:
                r2 = settle_row(ctx, r, T, allow_fetch=True,
                                past_bound=(T > WINDOW_END),
                                late=late)
            except RateLimited:
                r2 = r
                r2["notes"] = (r2["notes"] +
                               "; settle rate_limited, still open")
            written.append(r2)
    # (b) today's entry (entries stop after the review bound)
    day_row = None
    if T <= WINDOW_END:
        if not in_series:
            day_row = _blank_row(T, "SCORED")
            day_row.update(
                status="NC",
                reason=(f"spot_gap_{gap_day}" if gap_day
                        else "not_a_trading_day"))
        else:
            try:
                day_row = evaluate_entry(ctx, T, allow_fetch=True)
            except RateLimited:
                day_row = _blank_row(T, "SCORED")
                day_row.update(status="NC", reason="rate_limited")
        written.append(day_row)
    if not dry and written:
        write_rows(written)
    return day_row, written


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check (Jan-Oct "
                         "exact + November pass); never writes, "
                         "no API calls")
    ap.add_argument("--seed-backfill", action="store_true",
                    help="write ONLY the Nov 2-13 "
                         "BACKFILL_COUNTERFACTUAL rows, and only "
                         "if the reproduction passes")
    a = ap.parse_args(argv)

    if a.verify or a.seed_backfill:
        return verify_and_seed(a.seed_backfill)

    T = a.date or datetime.now(IST).date().isoformat()
    if T < START:
        print(f"BTST-IND BANK VOTES SHADOW: {T} is before the "
              f"shadow start {START} — nothing scored.")
        return 0
    if T > WINDOW_END:
        opens = [r for r in ledger_rows() if r["status"] == "OPEN"]
        if not opens:
            print(f"BTST-IND BANK VOTES SHADOW: {T} is past the "
                  f"review bound {WINDOW_END} (the Nov 30 "
                  f"verdicts) and no position is open — scoring "
                  f"closed; the review is due.")
            return 0
        # fall through: settlement-only run for the Nov 30 position
    day_row, written = score_run(T, a.dry_run)
    settled_now = [r for r in written if r["status"] == "TRADED"]
    for r in settled_now:
        print(f"BTST-IND BANK VOTES SHADOW settle {r['date']}: "
              f"{r['side']} {r['strike']} entry "
              f"{r['entry_premium']} -> exit {r['exit_date']} "
              f"{EXIT_STAMP} {r['exit_premium']} "
              f"(overnight {r['overnight_move_pts']} pts, spot gap "
              f"{r['spot_gap_pct'] or '-'}%) net={r['net_inr']}")
    if day_row is not None:
        print(f"BTST-IND BANK VOTES SHADOW {T}: "
              f"status={day_row['status']} reason={day_row['reason']} "
              f"votes={day_row['votes_long'] or '-'}/"
              f"{day_row['votes_short'] or '-'} "
              f"side={day_row['side'] or '-'} "
              f"strike={day_row['strike'] or '-'} "
              f"entry={day_row['entry_premium'] or '-'}"
              f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    elif T > WINDOW_END:
        print(f"BTST-IND BANK VOTES SHADOW {T}: past the review "
              f"bound — settlement-only run, no new entries.")
    if not a.dry_run:
        after = ledger_rows()
        fwd = [r for r in after if r["row_type"] == "SCORED"
               and r["status"] == "TRADED"]
        fnet = round(sum(float(r["net_inr"]) for r in fwd), 2)
        opn = [r for r in after if r["status"] == "OPEN"]
        bf = [r for r in after
              if r["row_type"] == "BACKFILL_COUNTERFACTUAL"
              and r["status"] == "TRADED"]
        print(f"BTST-IND BANK VOTES SHADOW tally: forward "
              f"settled={len(fwd)} shadow_net={fnet:+.2f} "
              f"open={len(opn)} (backfill {len(bf)} settled "
              f"trades, pre-shadow history, excluded) "
              f"(paper, real money Rs0)")
    if day_row is not None and day_row["reason"] == "rate_limited":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
