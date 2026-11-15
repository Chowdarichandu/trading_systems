#!/usr/bin/env python3
"""STOCK OPTIONS FAR-EXPIRY — FETCH (SPEC stock_options_far_SPEC.md
s.2-s.4). Reuses stock_options_fetch.py machinery (token, pacing,
discovery, candle pulls, disk cache under stock_options_data/).
Discovery covers the entry month + three following months per name so
the >= 45-day expiry can be found. On HTTP 429: hard-stop the attempt
(exit 3). Token check failure: exit 2 before any data call.
Research only; places no orders."""
import csv, json, sys
from datetime import date, timedelta
from pathlib import Path

WS = Path(__file__).resolve().parent
sys.path.insert(0, str(WS))
import stock_options_fetch as F
import stock_options_common as C
from stock_options_far_common import choose_contract_far

def main():
    s, _ = F.get("/v2/user/profile")
    if s != 200:
        print(f"BLOCKED_TOKEN: profile check HTTP {s}; no data calls made.")
        return 2
    print("token OK")
    # purge pre-live-path None discoveries for not-yet-expired months
    stale = [k for k, v in F.EXPIRIES.items()
             if v is None and k.split("|")[1] >= "2026-11"]
    for k in stale:
        del F.EXPIRIES[k]
    if stale:
        F._save_exp()
        print(f"purged {len(stale)} stale future-month None expiries")
    rows = list(csv.DictReader(open(WS / "stock_options_far_trades.csv")))
    pend = [r for r in rows if r["status"] == "PENDING_FETCH"]
    print(f"trades pending fetch: {len(pend)}")
    try:
        months = {}
        for r in pend:
            ed = date.fromisoformat(r["entry_date"])
            ms = set()
            y, m = ed.year, ed.month
            for _ in range(4):
                ms.add((y, m))
                m += 1
                if m == 13:
                    y, m = y + 1, 1
            months.setdefault(r["sym"], set()).update(ms)
        for sym in sorted(months):
            for (y, m) in sorted(months[sym]):
                e = F.discover_expiry(sym, y, m)
                print(f"expiry {sym} {y}-{m:02d}: {e}")
        expiries = C.expiries_cached()
        plan_daily, plan_m5 = {}, set()
        nosel = 0
        dte_hist = {}
        for r in pend:
            sel, reason = choose_contract_far(r, expiries)
            if sel is None:
                nosel += 1
                continue
            dte_hist[sel["days_to_expiry"] >= 45] = \
                dte_hist.get(sel["days_to_expiry"] >= 45, 0) + 1
            frm = r["entry_date"]
            to = max(r["exit_date"], sel["expiry"])
            cur = plan_daily.get(sel["key"], (frm, to))
            plan_daily[sel["key"]] = (min(cur[0], frm), max(cur[1], to))
            if r["cash_exit_kind"] == "CAP":
                plan_m5.add((sel["key"], r["exit_date"]))
        print(f"selection: {len(pend) - nosel} ok, {nosel} no-contract; "
              f"dte>=45: {dte_hist.get(True, 0)}, "
              f"dte<45 (farthest fallback): {dte_hist.get(False, 0)}; "
              f"daily pulls {len(plan_daily)}, 5-min pulls {len(plan_m5)}")
        for key, (frm, to) in sorted(plan_daily.items()):
            F.fetch_daily(key, frm, to)
        for key, day in sorted(plan_m5):
            F.fetch_m5(key, day)
    except F.RateLimited:
        print("RATE_LIMITED: attempt hard-stopped; cache kept. "
              "Unfetched trades score as NC RATE_LIMITED for this attempt.")
        return 3
    print("fetch complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
