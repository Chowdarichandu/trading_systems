#!/usr/bin/env python3
"""UNIFIED RUNNER FOR TOMORROW — Apex Pillar 1 (Option A) + Pillar 2 (Option B).

Single command entry point to run preflight checks, full historical backtests,
intraday live scans, or post-market EOD scoring cleanly on your live machine.

PAPER ONLY. Real money Rs 0. Places ZERO broker orders.

Usage:
  # 1. Before market open (08:45 IST): verify syntax, self-tests, token & watchdog
  python3 run_apex_tomorrow.py --preflight

  # 2. One-time historical backtest on your live machine's local data stores
  python3 run_apex_tomorrow.py --backtest

  # 3. During market hours (09:30-11:35 IST every 5 min): Pillar 2 live scan
  python3 run_apex_tomorrow.py --intraday

  # 4. After market close (15:40 IST): Pillar 1 + Pillar 2 EOD + breaker + watchdog
  python3 run_apex_tomorrow.py --eod
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

THIS_DIR = Path(__file__).resolve().parent
IST = ZoneInfo("Asia/Kolkata")


def _default_root() -> Path:
    live = Path.home() / "workspace" / "trading"
    if (live / "data").exists():
        return live
    return THIS_DIR


def _run(cmd: list[str], label: str) -> int:
    print(f"\n>>> [{label}] {' '.join(cmd)}")
    r = subprocess.run(cmd)
    print(f"<<< [{label}] exit={r.returncode}")
    return r.returncode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--preflight", action="store_true", help="Run self-tests, token check & watchdog")
    g.add_argument("--backtest", action="store_true", help="Backtest Pillar 1 + Pillar 2 on local stores")
    g.add_argument("--index-gate", action="store_true", help="Run Index Apex Lab (HEDGED_THETA / SWING_DEBIT / SQUEEZE_ORB) full gate + placebo")
    g.add_argument("--intraday", action="store_true", help="Run Pillar 2 live scan (09:30-11:35 IST)")
    g.add_argument("--eod", action="store_true", help="Run Pillar 1 + Pillar 2 EOD + breaker + watchdog")
    ap.add_argument("--root", default=str(_default_root()))
    ap.add_argument("--date", default=datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--structure", choices=("naked", "debit_spread"), default="naked")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    py = sys.executable
    root = Path(a.root)
    p1 = str(THIS_DIR / "pillar1_value_ekam_swing.py")
    p2 = str(THIS_DIR / "pillar2_index_options_apex.py")
    lab = str(THIS_DIR / "index_apex_lab.py")
    bf = str(THIS_DIR / "backfill_index_2025_2026.py")
    of = str(THIS_DIR / "orderflow_footprint_engine.py")
    wd = str(THIS_DIR / "pipeline_watchdog.py")
    cb = str(THIS_DIR / "circuit_breaker_stack.py")

    if a.preflight:
        rc1 = _run([py, p1, "--mode", "selftest"], "Pillar 1 self-test")
        rc2 = _run([py, p2, "--mode", "selftest"], "Pillar 2 self-test")
        rc3 = _run([py, lab, "--mode", "selftest"], "Index Apex Lab self-test + leak audit")
        rc4 = _run([py, bf, "--selftest"], "Index Backfill self-test")
        rc5 = _run([py, of, "--mode", "selftest"], "Order Flow / VP / Footprint self-test")
        env_p = root / "upstox_refresh" / ".env"
        tok_ok = env_p.exists() and "UPSTOX_ACCESS_TOKEN=" in env_p.read_text()
        print(f"\n>>> [Upstox token check] {env_p} -> {'OK' if tok_ok else 'MISSING (expected on live machine ~/workspace/trading)'}")
        _run([py, wd, "--root", str(root)], "Pipeline watchdog")
        return 0 if (rc1 == 0 and rc2 == 0 and rc3 == 0 and rc4 == 0 and rc5 == 0) else 1

    if a.index_gate:
        rc_lk = _run([py, lab, "--mode", "leakaudit"], "Index Apex Lab leak audit")
        rc_gt = _run([py, lab, "--mode", "gate", "--root", str(root), "--index", "ALL", "--strategy", "ALL"], "Index Apex Lab full gate")
        return 0 if (rc_lk == 0 and rc_gt == 0) else 1

    if a.backtest:
        rc1 = _run([py, p1, "--mode", "backtest", "--root", str(root), "--universe", "tier_ab"], "Pillar 1 backtest (tier_ab)")
        rc1b = _run([py, p1, "--mode", "backtest", "--root", str(root), "--universe", "ekam25"], "Pillar 1 backtest (ekam25)")
        rc2 = _run([py, p2, "--mode", "backtest", "--root", str(root), "--index", "ALL", "--structure", a.structure], "Pillar 2 backtest")
        return 0 if (rc1 == 0 and rc1b == 0 and rc2 == 0) else 1

    if a.intraday:
        cmd = [py, p2, "--mode", "live", "--root", str(root), "--index", "ALL",
               "--date", a.date, "--structure", a.structure]
        if a.dry_run:
            cmd.append("--dry-run")
        return _run(cmd, "Pillar 2 intraday live scan")

    if a.eod:
        c1 = [py, p1, "--mode", "live", "--root", str(root), "--universe", "tier_ab", "--date", a.date]
        c2 = [py, p2, "--mode", "score", "--root", str(root), "--index", "ALL",
              "--date", a.date, "--structure", a.structure]
        if a.dry_run:
            c1.append("--dry-run")
            c2.append("--dry-run")
        rc1 = _run(c1, "Pillar 1 EOD scan")
        rc2 = _run(c2, "Pillar 2 EOD scorer")
        if (root / "november_shadow_stack_bank_log.csv").exists() and not a.dry_run:
            _run([py, cb], "Refresh circuit_breaker_stack.py")
        _run([py, wd, "--root", str(root)], "Nightly pipeline watchdog")
        return 0 if (rc1 == 0 and rc2 == 0) else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
