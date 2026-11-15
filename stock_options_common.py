#!/usr/bin/env python3
"""STOCK OPTIONS — shared local helpers (no network): underlying keys,
contract normalisation, SPEC s.2 contract selection, local spot stores,
premium-cache readers. Used by stock_options_fetch.py (network) and
stock_options_build.py (scoring)."""
import csv, json, os
from datetime import date
from pathlib import Path

WS = Path(os.path.dirname(os.path.abspath(__file__)))
DATA = WS / "stock_options_data"
NAMES = ("ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER "
         "HINDUNILVR HINDZINC INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM "
         "NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL TVSMOTOR UNITDSPR "
         "VEDL WIPRO").split()

def eq_keys():
    out = {}
    with open(WS / "november_shadow_data/instruments_NSE.csv") as f:
        for r in csv.DictReader(f):
            if r["instrument_type"] == "EQUITY" and r["tradingsymbol"] in NAMES:
                out[r["tradingsymbol"]] = r["instrument_key"]
    return out

def norm_contracts(raw):
    """Expired-contract payload -> list of dicts with strike/type/key/lot."""
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

def contracts_cached(sym, expiry):
    fn = DATA / f"contracts_{sym}_{expiry}.json"
    if fn.exists():
        return norm_contracts(json.loads(fn.read_text()))
    return None

def expiries_cached():
    fn = DATA / "expiries.json"
    return json.loads(fn.read_text()) if fn.exists() else {}

# ---------------- local spot stores ----------------
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

_m5 = {}
def spot_m5(sym, day):
    if (sym, day) not in _m5:
        out = {}
        path = WS / f"data/sarvaritu_fwd/{sym}/spot_5m.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                ts = r["timestamp"]
                if ts[:10] == day:
                    out[ts[11:16]] = dict(open=float(r["open"]),
                                          high=float(r["high"]),
                                          low=float(r["low"]),
                                          close=float(r["close"]))
        _m5[(sym, day)] = out
    return _m5[(sym, day)]

# ---------------- premium cache readers ----------------
def daily_candles_cached(exp_key):
    fn = DATA / f"daily_{exp_key.replace('|', '_')}.json"
    if fn.exists():
        return json.loads(fn.read_text()).get("candles", {})
    return None

def m5_candles_cached(exp_key, day):
    fn = DATA / f"m5_{exp_key.replace('|', '_')}_{day}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    return None

# ---------------- SPEC s.2 selection ----------------
def choose_contract(row, expiries):
    """Returns dict(expiry, strike, type, key, lot) or (None, reason).
    expiries: dict 'SYM|YYYY-MM' -> expiry date str (discovered)."""
    sym = row["sym"]
    ed = date.fromisoformat(row["entry_date"])
    typ = "CE" if row["dir"] == "LONG" else "PE"
    months = []
    y, m = ed.year, ed.month
    for k in range(3):
        months.append(f"{sym}|{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    cand_expiries = []
    for mk in months:
        e = expiries.get(mk)
        if e:
            cand_expiries.append(e)
    cand_expiries = sorted(set(cand_expiries))
    if not cand_expiries:
        return None, "NO_OPTIONS"
    chosen_exp = None
    for e in cand_expiries:
        if (date.fromisoformat(e) - ed).days >= 5:
            chosen_exp = e
            break
    if chosen_exp is None:
        return None, "NO_CONTRACT"
    contracts = contracts_cached(sym, chosen_exp)
    if not contracts:
        return None, "NO_CONTRACT"
    pool = [c for c in contracts if c["type"] == typ]
    if not pool:
        return None, "NO_CONTRACT"
    if row["source"] in ("EKAM2C", "HOLD"):
        ref = spot_daily(sym).get(row["entry_date"], {}).get("close")
        if ref is None:
            return None, "NO_SPOT_REF"
    else:
        ref = float(row["cash_entry"])
    pool.sort(key=lambda c: (abs(c["strike"] - ref), c["strike"]))
    c = pool[0]
    if c["lot"] is None:
        return None, "NO_LOTSIZE"
    return dict(expiry=chosen_exp, strike=c["strike"], type=typ,
                key=c["key"], lot=c["lot"]), None
