#!/usr/bin/env python3
"""BTST PROGRAMME (2026-11-13) — shared loaders + frozen constants.
Frozen spec lives in btst_programme_2026-11-13.md. Paper only, real ₹0.
"""
import json
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"

MONTHLY_EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
                    "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
                    "2026-09-29", "2026-10-27", "2026-11-23", "2026-12-29"]

WATCHLIST25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK", "HINDALCO",
               "HINDCOPPER", "HINDUNILVR", "HINDZINC", "INDUSTOWER", "IRCTC",
               "ITC", "KALYANKJIL", "NATIONALUM", "NHPC", "NTPC", "OBEROIRLTY",
               "OIL", "PFC", "RECLTD", "TATASTEEL", "TVSMOTOR", "UNITDSPR",
               "VEDL", "WIPRO"]

# 5-min bar start times 09:15..15:25
ALL_BARS = []
_h, _m = 9, 15
while (_h, _m) <= (15, 25):
    ALL_BARS.append(f"{_h:02d}:{_m:02d}")
    _m += 5
    if _m == 60:
        _h += 1; _m = 0
EXIT_BARS = [b for b in ALL_BARS if "09:15" <= b <= "10:25"]  # last close = 10:30


def btst_expiry(day):
    """Monthly expiry in force for an overnight hold entered on `day`:
    the first monthly expiry STRICTLY after day (on expiry day itself the
    expiring contract cannot be held overnight -> next monthly)."""
    for e in MONTHLY_EXPIRIES:
        if e > day:
            return e
    return None


def atm_strike(level):
    """Nearest 100 to level; an exact 50 remainder rounds DOWN (frozen)."""
    k = int(level // 100)
    return k * 100 if (level - k * 100) < 50 else (k + 1) * 100


def load_bank_spot():
    """day -> list of [hm, o, h, l, c] sorted by hm. Jan-Oct from
    daily2leg/spot.json; November from data/banknifty-2026-11/spot_5m.csv."""
    spot = {}
    raw = json.loads((TR / "daily2leg/spot.json").read_text())["BANKNIFTY"]
    for d, bars in raw.items():
        spot[d] = sorted(([b[0], float(b[1]), float(b[2]), float(b[3]), float(b[4])] for b in bars),
                         key=lambda b: b[0])
    nov = pd.read_csv(TR / "data/banknifty-2026-11/spot_5m.csv")
    nov["d"] = nov["timestamp"].str[:10]; nov["hm"] = nov["timestamp"].str[11:16]
    for d, g in nov.groupby("d"):
        spot[d] = sorted(([r.hm, float(r.open), float(r.high), float(r.low), float(r.close)]
                          for r in g.itertuples()), key=lambda b: b[0])
    return spot


def trading_days(spot):
    """Full-session trading days only (>=70 bars). Excludes mock/special
    sessions (e.g. 2026-11-08, a 14-bar Sunday session in the Nov store)."""
    return sorted(d for d, bars in spot.items() if len(bars) >= 70)


def spot_bar(spot, day, hm):
    for b in spot.get(day, []):
        if b[0] == hm:
            return b
    return None


class PremStore:
    """Merged Bank Nifty premium bars. Priority on overlap: fetched (btst_data)
    > option_5m.csv chain store > prem_bank.json (SHORT-FOLLOW store).
    bars() returns {hm: (o,h,l,c)} possibly partial — callers check keys."""

    def __init__(self):
        import glob, re
        self.opt = {}
        files = sorted(glob.glob(str(TR / "data/banknifty-2026-*/option_5m.csv")))
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        df["d"] = df["timestamp"].str[:10]; df["hm"] = df["timestamp"].str[11:16]
        for (exp, strike, side, d), g in df.groupby(["expiry", "strike", "option_type", "d"]):
            self.opt[(exp, int(strike), side, d)] = {
                r.hm: (float(r.open), float(r.high), float(r.low), float(r.close))
                for r in g.itertuples()}
        self.prem = json.loads((TR / "daily2leg/prem_bank.json").read_text())
        self.fetched = {}
        fd = TR / "btst_data"
        pat = re.compile(r"candles_BANKNIFTY_(\d+)(CE|PE)_(2026-\d\d-\d\d)_(2026-\d\d-\d\d)\.json$")
        if fd.exists():
            for f in fd.glob("candles_BANKNIFTY_*.json"):
                m = pat.match(f.name)
                if not m:
                    continue
                strike, side, exp, day = int(m.group(1)), m.group(2), m.group(3), m.group(4)
                try:
                    body = json.loads(f.read_text())
                except Exception:
                    continue
                candles = ((body.get("data") or {}).get("candles")) or []
                bars = {}
                for c in candles:
                    if c[0][:10] == day:
                        bars[c[0][11:16]] = (float(c[1]), float(c[2]), float(c[3]), float(c[4]))
                if bars:
                    self.fetched[(exp, strike, side, day)] = bars

    def bars(self, exp, strike, side, day):
        out = {}
        pk = f"{exp}|{strike}|{side}"
        if pk in self.prem and day in self.prem[pk]:
            for hm, v in self.prem[pk][day].items():
                out[hm] = (float(v[0]), float(v[1]), float(v[2]), float(v[3]))
        k = (exp, strike, side, day)
        if k in self.opt:
            out.update(self.opt[k])
        if k in self.fetched:
            out.update(self.fetched[k])
        return out

    def has_entry_bar(self, exp, strike, side, day):
        return "15:15" in self.bars(exp, strike, side, day)

    def has_exit_bars(self, exp, strike, side, day):
        b = self.bars(exp, strike, side, day)
        return all(hm in b for hm in EXIT_BARS)


def load_stock_bars(sym):
    """sarvaritu_fwd 5m store -> day -> list of [hm,o,h,l,c] sorted."""
    df = pd.read_csv(TR / f"data/sarvaritu_fwd/{sym}/spot_5m.csv")
    df["d"] = df["timestamp"].str[:10]; df["hm"] = df["timestamp"].str[11:16]
    out = {}
    for d, g in df.groupby("d"):
        out[d] = sorted(([r.hm, float(r.open), float(r.high), float(r.low), float(r.close)]
                         for r in g.itertuples()), key=lambda b: b[0])
    return out


def day_ohlc(bars):
    o = bars[0][1]; h = max(b[2] for b in bars); l = min(b[3] for b in bars); c = bars[-1][4]
    return o, h, l, c
