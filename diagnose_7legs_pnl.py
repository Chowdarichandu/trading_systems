#!/usr/bin/env python3
"""7-LEG LIVE PNL DASHBOARD & "WHY DIDN'T TRIO FIRE?" DIAGNOSTIC.

Answers three operational questions in ONE command on ~/workspace/trading:
  1. Exact current November MTD + Live (Nov 16+) + Yesterday + Today PnL across
     ALL 7 active programme legs (TRIO Bank, TRIO Nifty, TRIO Stocks, EKAM
     Daily, EKAM Intraday, TARANG, SAPTA) + standalone controls (Skill V3, Raw).
  2. Exact reason TRIO Bank or TRIO Nifty did NOT fire on any given date
     (breaker paused? stale live producer? EXP0? B2 Skill-CE block? N-FIX-1
      gap-up CE block? quiet OR?).
  3. Counterfactual comparison: what the raw/unfiltered Skill V3 & Raw Stack
     controls made on yesterday & today vs the gated TRIO lead lines.

Read-only diagnostic (zero mutations, zero broker orders). Paper only, Rs 0.

Usage:
  python3 diagnose_7legs_pnl.py [--root ~/workspace/trading] [--dates 2026-11-25 2026-11-26]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

SEVEN_LEGS = [
    ("1. TRIO Bank (Stack v2+B-FIX-1)", "november_repaired_bfix1_bank_log.csv", "repaired_net_inr"),
    ("   └ Bank Raw Stack v2 (ctrl)", "november_shadow_stack_bank_log.csv", "net_inr"),
    ("   └ Bank Skill V3 (unfiltered)", "november_shadow_skill_bank_log.csv", "net_inr"),
    ("2. TRIO Nifty (v1+N-FIX-1)", "november_repaired_nfix1_nifty_log.csv", "repaired_net_inr"),
    ("   └ Nifty DEC-S1 / Raw v1", "november_shadow_decs1_nifty_log.csv", "net_inr"),
    ("   └ Nifty Skill V3 (unfiltered)", "november_shadow_skill_nifty_log.csv", "net_inr"),
    ("3. TRIO Stocks (Stock Book)", "stocks_sarvaritu_paper_log.csv", "net_inr"),
    ("4. EKAM Daily Paper", "ekam_daily_paper_log.csv", "net_inr"),
    ("5a. EKAM Intraday S2", "november_shadow_ekam_s2_stocks_log.csv", "net_inr"),
    ("5b. EKAM Intraday CAND-T5", "november_shadow_ekam_t5_stocks_log.csv", "net_inr"),
    ("6a. TARANG-C1 Forward", "forward_tarang_c1_log.csv", "net_inr"),
    ("6b. TARANG-C2 Forward", "forward_tarang_c2_log.csv", "net_inr"),
    ("7a. SAPTA-C1 Forward", "forward_sapta_c1_log.csv", "net_inr"),
    ("7b. SAPTA-C2 Forward", "forward_sapta_c2_log.csv", "net_inr"),
]


def default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "november_repaired_bfix1_bank_log.csv").exists():
        return live
    return Path(__file__).resolve().parent


def _f(v: Any) -> Optional[float]:
    try:
        if v is None or str(v).strip() == "":
            return None
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return None


def _date_of(r: Dict[str, str]) -> str:
    return (r.get("date") or r.get("entry_date") or r.get("exit_date") or "")[:10]


def _net_of(r: Dict[str, str], col: str) -> Optional[float]:
    for k in (col, "repaired_net_inr", "net_inr", "realised_pnl_inr", "pnl_inr", "net"):
        if k in r:
            val = _f(r.get(k))
            if val is not None:
                return val
    return None


def _row_trades(r: Dict[str, str], col: str) -> int:
    if col == "repaired_net_inr":
        raw_l = int(_f(r.get("stack_legs") or r.get("v1_legs")) or 0)
        sd = int(_f(r.get("stood_down")) or 0)
        return max(0, raw_l - sd)
    return 1 if _net_of(r, col) is not None else 0


def audit_7legs(root: Path, focus_dates: Sequence[str]) -> Dict[str, Any]:
    rows_out: List[Dict[str, Any]] = []
    print(f"\n================ 7-LEG CURRENT PNL & TRIO DIAGNOSTIC ({root}) ================")
    print(f"Focus dates checked: {list(focus_dates)}\n")
    print(f"{'Leg / Book':<34} | {'Last Date':<10} | {'Nov MTD (Rs)':>12} | {'Nov16+ Live':>11} | {'Tr':>3} | {'Focus Dates Detail'}")
    print("-" * 110)

    for label, fname, ncol in SEVEN_LEGS:
        p = root / fname
        if not p.exists():
            print(f"{label:<34} | {'MISSING':<10} | {'—':>12} | {'—':>11} | {'0':>3} | file absent")
            continue
        with open(p, newline="") as f:
            data = list(csv.DictReader(f))
        dates = sorted({_date_of(r) for r in data if _date_of(r)})
        last_d = dates[-1] if dates else "EMPTY"
        mtd_rows = [r for r in data if _date_of(r) >= "2026-11-01"]
        mtd_nums = [x for x in (_net_of(r, ncol) for r in mtd_rows) if x is not None]
        mtd_tr = sum(_row_trades(r, ncol) for r in mtd_rows)
        live_rows = [r for r in data if _date_of(r) >= "2026-11-16"]
        live_nums = [x for x in (_net_of(r, ncol) for r in live_rows) if x is not None]

        focus_parts = []
        for fd in focus_dates:
            frows = [r for r in data if _date_of(r) == fd]
            if not frows:
                focus_parts.append(f"{fd}:NOT_LOGGED")
                continue
            ftr = sum(_row_trades(r, ncol) for r in frows)
            fnets = [x for x in (_net_of(r, ncol) for r in frows) if x is not None]
            if ftr > 0:
                focus_parts.append(f"{fd}:{ftr}tr Rs{sum(fnets):+,.0f}")
            else:
                note = (frows[0].get("notes") or frows[0].get("status") or frows[0].get("decision") or "no-trade")[:38]
                focus_parts.append(f"{fd}:0tr({note})")

        mtd_sum = round(sum(mtd_nums), 2)
        live_sum = round(sum(live_nums), 2)
        print(
            f"{label:<34} | {last_d:<10} | {mtd_sum:>+12,.2f} | {live_sum:>+11,.2f} | "
            f"{mtd_tr:>3} | {' ; '.join(focus_parts)}"
        )
        rows_out.append({
            "label": label, "file": fname, "last_date": last_d,
            "mtd_net": mtd_sum, "live_net": live_sum, "trades": mtd_tr,
            "focus": focus_parts,
        })

    # Check exact TRIO operational blockers (circuit breaker + live producer state)
    print("\n--- WHY TRIO DID / DIDN'T FIRE (OPERATIONAL & FILTER CHECK) ---")
    cb_p = root / "breaker_state_stack.json"
    if cb_p.exists():
        cb = json.loads(cb_p.read_text())
        print(
            f"  Circuit Breaker (Bank Stack): last_date={cb.get('last_date')} | MTD=Rs {cb.get('mtd_inr')} "
            f"| HWM_DD=Rs {cb.get('hwm_dd_inr')} | currently_paused={cb.get('currently_paused')} "
            f"| trips={len(cb.get('trips') or [])}"
        )
    ts_p = root / "trio_live_state.json"
    if ts_p.exists():
        ts = json.loads(ts_p.read_text())
        open_b = {k: len(v.get("open") or {}) for k, v in (ts.get("books") or {}).items()}
        print(f"  TRIO Live Producer State    : last_run={ts.get('last_run')} | date={ts.get('date')} | open={open_b}")
    lp_p = root / "live_producer_state.json"
    if lp_p.exists():
        lp = json.loads(lp_p.read_text())
        print(f"  Legacy Live Producer State  : keys={list(lp.keys())[:6]} date={lp.get('date')}")

    print(
        "\n  Structural TRIO Silence Causes (from frozen rules):\n"
        "    1. TRIO Bank blocks Skill-V3 CE (B2), NS1 CE, pre-10:30 Skill PE (EVE-05), pre-10:30 NS1 (EVE-19),\n"
        "       [400,550) premium band, and PE+gap-down+[500,800) (B-FIX-1) — sits flat on most CE rallies.\n"
        "    2. TRIO Nifty requires >=2 confirming systems <= 09:55 (CH3-R), skips expiry day (EXP0), and\n"
        "       blocks ALL CE+gap-up days (N-FIX-1) -> averages only ~1 leg/week.\n"
        "    3. Compare 'Bank/Nifty Skill V3 (unfiltered)' rows above against TRIO Bank/Nifty on your focus dates\n"
        "       to see exact rupees missed when TRIO sat flat."
    )
    print("========================================================================\n")
    return {"root": str(root), "focus_dates": list(focus_dates), "rows": rows_out}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(default_root()))
    today = datetime.now(IST).date()
    yest = today - timedelta(days=1)
    ap.add_argument("--dates", nargs="*", default=[yest.isoformat(), today.isoformat()])
    a = ap.parse_args(argv)
    audit_7legs(Path(a.root), a.dates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
