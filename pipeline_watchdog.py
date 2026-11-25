#!/usr/bin/env python3
"""PIPELINE HEALTH WATCHDOG (added 2026-11-25).

Read-only operational audit across all active November/forward ledgers,
state files, and the circuit breaker. Designed to run nightly (e.g. 20:45 IST)
and print actionable alerts when any pipeline silently breaks, goes NC,
lags behind peers, logs invalid negative stops, or trips a risk breaker.

Zero API calls, zero mutations. Exit code: 0 = healthy, 2 = alerts found.
Usage:
    python3 pipeline_watchdog.py [--root /path/to/repo] [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ACTIVE_LEDGERS = [
    ("TRIO Bank (B-FIX-1)", "november_repaired_bfix1_bank_log.csv"),
    ("Bank TUNED STACK v2", "november_shadow_stack_bank_log.csv"),
    ("Bank Legacy BNF-PAPER-V1", "november_paper_bank_log.csv"),
    ("Bank D1 Shadow", "november_shadow_d1_bank_log.csv"),
    ("Bank Skill V3 Shadow", "november_shadow_skill_bank_log.csv"),
    ("TRIO Nifty (N-FIX-1)", "november_repaired_nfix1_nifty_log.csv"),
    ("Nifty DEC-S1 Control", "november_shadow_decs1_nifty_log.csv"),
    ("Nifty TUNED v2 Shadow", "november_shadow_tunedv2_nifty_log.csv"),
    ("Nifty C3G7 Control", "november_paper_nifty_log.csv"),
    ("Nifty Skill V3 Shadow", "november_shadow_skill_nifty_log.csv"),
    ("TRIO Stocks (Stock Book)", "stocks_sarvaritu_paper_log.csv"),
    ("EKAM Intraday CAND-T5", "november_shadow_ekam_t5_stocks_log.csv"),
    ("EKAM Intraday S2", "november_shadow_ekam_s2_stocks_log.csv"),
    ("EKAM Daily Paper", "ekam_daily_paper_log.csv"),
    ("HOLD L35-H15 Shadow", "hold_shadow_log.csv"),
    ("BTST-IND Bank Shadow", "november_shadow_btstind_bank_log.csv"),
    ("R4-D1 Bank Shadow", "r4d1_shadow_log.csv"),
    ("OI-V3 Bank Shadow", "oi_v3_shadow_log.csv"),
    ("Premium-Tape Bank Shadow", "november_shadow_premiumtape_bank_log.csv"),
    ("Forward TARANG-C1", "forward_tarang_c1_log.csv"),
    ("Forward TARANG-C2", "forward_tarang_c2_log.csv"),
    ("Forward SAPTA-C1", "forward_sapta_c1_log.csv"),
    ("Forward SAPTA-C2", "forward_sapta_c2_log.csv"),
]


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def audit_repo(root: Path) -> Dict[str, Any]:
    alerts: List[Dict[str, str]] = []
    ledger_stats: List[Dict[str, Any]] = []
    max_dates: List[str] = []

    for label, fname in ACTIVE_LEDGERS:
        p = root / fname
        if not p.exists():
            alerts.append({"severity": "HIGH", "source": fname,
                           "msg": f"{label}: ledger file missing"})
            continue
        rows = _read_csv(p)
        dates = sorted({r.get("date", "") for r in rows if r.get("date")})
        last_date = dates[-1] if dates else None
        if last_date:
            max_dates.append(last_date)

        # Count recent NC / UNSCORED rows (since 2026-11-16)
        recent = [r for r in rows if r.get("date", "") >= "2026-11-16"]
        nc_recent = [
            r for r in recent
            if (r.get("status", "").upper() in ("NC", "UNSCORED")
                or "NC_" in r.get("decision", "").upper()
                or "NOT_COMPUTED" in (r.get("notes") or "").upper())
        ]
        # Check for negative stop prices in option ledgers
        neg_stops = []
        for r in rows:
            sv = r.get("stop", "")
            if sv not in ("", None):
                try:
                    if float(sv) <= 0.0:
                        neg_stops.append((r.get("date", ""), sv))
                except ValueError:
                    pass

        ledger_stats.append({
            "label": label,
            "file": fname,
            "rows": len(rows),
            "last_date": last_date,
            "recent_rows": len(recent),
            "recent_nc": len(nc_recent),
            "negative_stops": neg_stops,
        })

        if len(rows) == 0:
            alerts.append({"severity": "HIGH", "source": fname,
                           "msg": f"{label}: ledger is empty (header-only)"})
        if recent and len(nc_recent) == len(recent):
            reasons = sorted({r.get("reason") or r.get("status") or "NC" for r in nc_recent})
            alerts.append({
                "severity": "HIGH",
                "source": fname,
                "msg": f"{label}: 100% NC/UNSCORED since 2026-11-16 "
                       f"({len(nc_recent)}/{len(recent)} rows; reasons={reasons})",
            })
        elif nc_recent:
            alerts.append({
                "severity": "MEDIUM",
                "source": fname,
                "msg": f"{label}: {len(nc_recent)} NC/UNSCORED row(s) since 2026-11-16",
            })
        for d, sv in neg_stops:
            alerts.append({
                "severity": "HIGH",
                "source": fname,
                "msg": f"{label}: non-positive stop price ({sv}) logged on {d}",
            })

    # Detect ledgers lagging behind the newest trading day across peers
    ref_date = max(max_dates) if max_dates else None
    if ref_date:
        for st in ledger_stats:
            ld = st["last_date"]
            if ld and ld < ref_date and "D1 Shadow" not in st["label"]:
                alerts.append({
                    "severity": "MEDIUM",
                    "source": st["file"],
                    "msg": f"{st['label']}: last_date={ld} lags peer max={ref_date}",
                })

    # Check circuit breaker state consistency
    cb_path = root / "breaker_state_stack.json"
    if cb_path.exists():
        cb = json.loads(cb_path.read_text())
        trips = cb.get("trips") or []
        if trips and not cb.get("currently_paused"):
            last_trip = trips[-1]
            if last_trip.get("kind") in ("MTD", "HWMDD") and last_trip.get("date", "")[:7] == (cb.get("last_date") or "")[:7]:
                alerts.append({
                    "severity": "CRITICAL",
                    "source": "breaker_state_stack.json",
                    "msg": f"Breaker tripped ({last_trip['kind']} on {last_trip['date']}) "
                           f"but currently_paused=False! Re-run patched circuit_breaker_stack.py.",
                })
        if ref_date and (cb.get("last_date") or "") < ref_date:
            alerts.append({
                "severity": "MEDIUM",
                "source": "breaker_state_stack.json",
                "msg": f"Circuit breaker state stale: last_date={cb.get('last_date')} < {ref_date}",
            })

    # Check live producer state files for orphaned open positions / staleness
    trio_st = root / "trio_live_state.json"
    if trio_st.exists():
        ts = json.loads(trio_st.read_text())
        if ref_date and (ts.get("date") or "") < ref_date:
            open_cnt = sum(len(b.get("open") or {}) for b in (ts.get("books") or {}).values())
            alerts.append({
                "severity": "HIGH" if open_cnt else "MEDIUM",
                "source": "trio_live_state.json",
                "msg": f"TRIO live producer stale: last_run={ts.get('last_run')} "
                       f"(date={ts.get('date')} < {ref_date}, open_positions={open_cnt})",
            })

    return {
        "root": str(root),
        "peer_max_date": ref_date,
        "alert_count": len(alerts),
        "alerts": alerts,
        "ledgers": ledger_stats,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    rep = audit_repo(Path(a.root))
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"PIPELINE WATCHDOG — {rep['root']} (peer max date: {rep['peer_max_date']})")
        print(f"Total alerts: {rep['alert_count']}\n")
        for al in rep["alerts"]:
            print(f"  [{al['severity']:<8}] {al['source']}: {al['msg']}")
    return 2 if rep["alert_count"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
