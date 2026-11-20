#!/usr/bin/env python3
"""BTST-STOCK-OPTIONS (LIQUID-ONLY) — shared local helpers (no network).
Spec: btst_so_SPEC.md (frozen 2026-11-17). Signals, calendars, contract
selection and bar logic used identically by btst_so_fetch.py (network) and
btst_so_build.py (scoring). Research only."""
import csv, json, os
from datetime import date, timedelta
from pathlib import Path

WS = Path(os.path.dirname(os.path.abspath(__file__)))
DATA = WS / "btst_so_data"
PROG = WS / "stock_options_data"
NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER "
         "HINDUNILVR HINDZINC INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM "
         "NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL TVSMOTOR UNITDSPR "
         "VEDL WIPRO").split()
MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13)
          if (y, m) <= (2026, 10)]
OPT_COST = 220.0
CASH_COST = 40.0

# ---------------- spot stores (programme store basis) ----------------
_daily = {}
def spot_daily(sym):
    if sym not in _daily:
        rows = {}
        with open(WS / f"data/sarvaritu_fwd/{sym}/spot_daily.csv") as f:
            for r in csv.DictReader(f):
                rows[r["date"]] = dict(open=float(r["open"]),
                                       high=float(r["high"]),
                                       low=float(r["low"]),
                                       close=float(r["close"]))
        _daily[sym] = rows
    return _daily[sym]

def sessions(sym):
    return sorted(spot_daily(sym))

_m5 = {}
def spot_m5(sym):
    """{day: {hh:mm -> close}} for the whole store, loaded once per name."""
    if sym not in _m5:
        out = {}
        with open(WS / f"data/sarvaritu_fwd/{sym}/spot_5m.csv") as f:
            for r in csv.DictReader(f):
                ts = r["timestamp"]
                out.setdefault(ts[:10], {})[ts[11:16]] = float(r["close"])
        _m5[sym] = out
    return _m5[sym]

# ---------------- signals ----------------
def signals():
    """EKAM2c published entries, Jan-Oct of 2025/2026. t = signal_date,
    exit session = entry_date. Asserts the published cash totals."""
    out = []
    with open(WS / "ekam2c_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["book"] != "EKAM2c":
                continue
            ed = r["entry_date"]
            if ed[:4] in ("2025", "2026") and "01" <= ed[5:7] <= "10":
                out.append(dict(sym=r["sym"], t=r["signal_date"],
                                exit_session=ed, year=int(ed[:4]),
                                comps=r["comps"]))
    for yr, want_n, want_net in ((2025, 74, 42954.60),
                                 (2026, 102, 141328.40)):
        sel = [s for s in out if s["year"] == yr]
        assert len(sel) == want_n, (yr, len(sel))
    return out

def placebo_day(sym, t, shift=5):
    """The `shift`-th store session strictly after t, or None."""
    ss = sessions(sym)
    try:
        i = ss.index(t)
    except ValueError:
        return None
    return ss[i + shift] if i + shift < len(ss) else None

def next_session(sym, day):
    ss = sessions(sym)
    try:
        i = ss.index(day)
    except ValueError:
        return None
    return ss[i + 1] if i + 1 < len(ss) else None

# ---------------- programme caches (read) ----------------
def expiries():
    fn = PROG / "expiries.json"
    return json.loads(fn.read_text()) if fn.exists() else {}

def contracts(sym, expiry):
    fn = PROG / f"contracts_{sym}_{expiry}.json"
    if not fn.exists():
        return None
    raw = json.loads(fn.read_text())
    out = []
    for c in raw or []:
        if not isinstance(c, dict):
            continue
        strike = c.get("strike_price") or c.get("strike") or c.get("strikePrice")
        typ = (c.get("option_type") or c.get("instrument_type")
               or c.get("optionType") or "").upper()
        key = c.get("expired_instrument_key") or c.get("instrument_key")
        lot = c.get("lot_size") or c.get("lotSize")
        if strike is not None and key and typ in ("CE", "PE"):
            out.append(dict(strike=float(strike), type=typ, key=key,
                            lot=(float(lot) if lot else None)))
    return out

# ---------------- contract selection (SPEC s.3) ----------------
def choose_contract(sym, t):
    """Nearest expiry >= 7 days after t; CE strike nearest day-t spot close.
    Returns dict(expiry, strike, key, lot) or (None, reason). Local only."""
    exps = expiries()
    td = date.fromisoformat(t)
    cands = []
    y, m = td.year, td.month
    for _ in range(3):
        e = exps.get(f"{sym}|{y:04d}-{m:02d}")
        if e:
            cands.append(e)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    chosen = None
    for e in sorted(set(cands)):
        if (date.fromisoformat(e) - td).days >= 7:
            chosen = e
            break
    if chosen is None:
        return None, "NO_EXPIRY"
    pool_all = contracts(sym, chosen)
    if not pool_all:
        return None, "NO_CONTRACT_LIST"
    ref = spot_daily(sym).get(t, {}).get("close")
    if ref is None:
        return None, "NO_SPOT_REF"
    pool = [c for c in pool_all if c["type"] == "CE"]
    if not pool:
        return None, "NO_CONTRACT_LIST"
    pool.sort(key=lambda c: (abs(c["strike"] - ref), c["strike"]))
    c = pool[0]
    if c["lot"] is None:
        return None, "NO_LOTSIZE"
    return dict(expiry=chosen, strike=c["strike"], key=c["key"],
                lot=c["lot"]), None

# ---------------- option bar caches ----------------
def m5_bars(key, day):
    """[[hh:mm, o, h, l, c], ...] ascending, or None if not cached anywhere."""
    fn = DATA / f"m5_{key.replace('|', '_')}_{day}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    fn2 = PROG / f"m5_{key.replace('|', '_')}_{day}.json"
    if fn2.exists():
        return json.loads(fn2.read_text())
    return None

def screen_daily(key):
    fn = DATA / f"screen_daily_{key.replace('|', '_')}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    return None

ENTRY_WINDOW = [f"{h:02d}:{m:02d}" for h, m in
                [(15, 0), (15, 5), (15, 10), (15, 15), (15, 20), (15, 25)]]
EXIT_WINDOW = ["09:15", "09:20", "09:25", "09:30", "09:35", "09:40"]

def entry_fill(bars):
    """(price, bar_time) = close of LAST bar starting 15:00-15:25."""
    if not bars:
        return None, None
    by = {b[0]: b for b in bars}
    for t in reversed(ENTRY_WINDOW):
        if t in by:
            return float(by[t][4]), t
    return None, None

def exit_fill(bars):
    """(price, bar_time, late) = close of FIRST bar starting 09:15-09:40;
    else first bar of the day flagged late; else (None, None, False)."""
    if not bars:
        return None, None, False
    by = {b[0]: b for b in bars}
    for t in EXIT_WINDOW:
        if t in by:
            return float(by[t][4]), t, False
    first = sorted(by)[0]
    return float(by[first][4]), first, True
