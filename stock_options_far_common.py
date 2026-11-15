#!/usr/bin/env python3
"""STOCK OPTIONS FAR-EXPIRY — contract selection (SPEC
stock_options_far_SPEC.md s.2). The ONLY change vs the first run: expiry
is the first listed monthly expiry >= 45 calendar days after entry; if
none reaches 45 days, the farthest available expiry is taken and its
days-to-expiry recorded. Strike/lot/NC conventions identical to
stock_options_common.choose_contract."""
import sys, os
from datetime import date

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import stock_options_common as C

MIN_DAYS = 45

def candidate_expiries(row, expiries):
    sym = row["sym"]
    ed = date.fromisoformat(row["entry_date"])
    out = set()
    y, m = ed.year, ed.month
    for _ in range(4):  # entry month + three following months
        e = expiries.get(f"{sym}|{y:04d}-{m:02d}")
        if e:
            out.add(e)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return sorted(out)

def choose_contract_far(row, expiries):
    """Returns dict(expiry, strike, type, key, lot, days_to_expiry)
    or (None, reason)."""
    sym = row["sym"]
    ed = date.fromisoformat(row["entry_date"])
    typ = "CE" if row["dir"] == "LONG" else "PE"
    cands = candidate_expiries(row, expiries)
    if not cands:
        return None, "NO_OPTIONS"
    chosen = None
    for e in cands:
        if (date.fromisoformat(e) - ed).days >= MIN_DAYS:
            chosen = e
            break
    if chosen is None:
        chosen = cands[-1]  # farthest available; days recorded on row
    dte = (date.fromisoformat(chosen) - ed).days
    contracts = C.contracts_cached(sym, chosen)
    if not contracts:
        return None, "NO_CONTRACT"
    pool = [c for c in contracts if c["type"] == typ]
    if not pool:
        return None, "NO_CONTRACT"
    ref = C.spot_daily(sym).get(row["entry_date"], {}).get("close")
    if ref is None:
        return None, "NO_SPOT_REF"
    pool.sort(key=lambda c: (abs(c["strike"] - ref), c["strike"]))
    c = pool[0]
    if c["lot"] is None:
        return None, "NO_LOTSIZE"
    return dict(expiry=chosen, strike=c["strike"], type=typ,
                key=c["key"], lot=c["lot"], days_to_expiry=dte), None
