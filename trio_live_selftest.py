#!/usr/bin/env python3
"""TRIO LIVE PRODUCER — SELF-TEST (run before wiring; re-runnable).

Replays the live evaluation (trio_live_producer.py --replay-day)
as fresh subprocesses at causal checkpoints on the two November
forward days the evening scorers have already scored, and
compares against their ledgers:

- 2026-11-16 (evening): TUNED STACK no-trade day -> D1 0 legs
  Rs0; DEC-S1 no-trade day -> repaired 0 legs Rs0. Gaps:
  Bank +0.3138 (B-FIX-1 ledger), Nifty +0.246 (N-FIX-1 ledger).
- 2026-11-17 (evening): TUNED STACK no-trade day -> D1 0 legs
  Rs0; DEC-S1 one component-C CE 25400 (weekly expiry
  2026-11-17) entry 09:50 @ 38.80, exit 13:05 @ 38.80 be_stop,
  net -220.00; gap -0.0546% (not > 0) -> N-FIX-1 keeps it ->
  repaired 1 leg -220.00. Bank gap -0.0259.

Causality checkpoints on 2026-11-17: at 09:45 the C leg must
NOT exist yet (its entry bar 09:50 has not completed); at 10:00
it must be present and OPEN; at 13:10 it must be CLOSED
(be_stop bar 13:05 completed at 13:10) with net -220.00.

Exit 0 iff every check passes.
"""
import json, subprocess, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"


def replay(day, at):
    r = subprocess.run(
        [sys.executable, "trio_live_producer.py",
         "--replay-day", day, "--at", at],
        cwd=TR, capture_output=True, text=True, timeout=1200)
    for line in r.stdout.splitlines():
        if line.startswith("REPLAY_RESULT "):
            return json.loads(line[len("REPLAY_RESULT "):])
    raise SystemExit(f"replay {day} {at} produced no result:\n"
                     f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}")


CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def book(res, b):
    return res["books"][b]


# ---- 2026-11-16 full day ---------------------------------------------
r = replay("2026-11-16", "15:35")
b, n = book(r, "BANK_D1"), book(r, "NIFTY_REP")
check("Nov16 Bank gap", b["gap"] is not None
      and abs(b["gap"] - 0.3138) < 0.01, f"gap={b['gap']}")
check("Nov16 Bank legs", b["legs"] == [] and b["kept_legs"] == 0
      and b["kept_net"] == 0, f"legs={len(b['legs'])}")
check("Nov16 Nifty gap", n["gap"] is not None
      and abs(n["gap"] - 0.246) < 0.01, f"gap={n['gap']}")
check("Nov16 Nifty legs", n["legs"] == [] and n["kept_legs"] == 0
      and n["kept_net"] == 0, f"legs={len(n['legs'])}")

# ---- 2026-11-17 causality checkpoints --------------------------------
r = replay("2026-11-17", "09:45")
n = book(r, "NIFTY_REP")
check("Nov17 09:45 Nifty C leg absent",
      all(L["entry_time"] != "09:50" for L in n["legs"]),
      f"legs={[(L['family'], L['entry_time']) for L in n['legs']]}")
check("Nov17 09:45 Bank legs", book(r, "BANK_D1")["legs"] == [])

r = replay("2026-11-17", "10:00")
n = book(r, "NIFTY_REP")
c = [L for L in n["legs"] if L["family"] == "DEC-S1-C"]
check("Nov17 10:00 C leg present+open",
      len(c) == 1 and c[0]["status"] == "open"
      and c[0]["entry_price"] == 38.8
      and c[0]["decision"] == "KEPT",
      f"{c}")

r = replay("2026-11-17", "13:10")
n = book(r, "NIFTY_REP")
c = [L for L in n["legs"] if L["family"] == "DEC-S1-C"]
check("Nov17 13:10 C leg closed -220",
      len(c) == 1 and c[0]["status"] == "closed"
      and c[0]["exit_time"] == "13:05"
      and c[0]["exit_reason"] == "be_stop"
      and c[0]["net"] == -220.0,
      f"{c}")

# ---- 2026-11-17 full day ---------------------------------------------
r = replay("2026-11-17", "15:35")
b, n = book(r, "BANK_D1"), book(r, "NIFTY_REP")
check("Nov17 Bank gap", b["gap"] is not None
      and abs(b["gap"] - (-0.0259)) < 0.01, f"gap={b['gap']}")
check("Nov17 Bank legs", b["legs"] == [] and b["kept_legs"] == 0
      and b["kept_net"] == 0, f"legs={len(b['legs'])}")
check("Nov17 Nifty gap", n["gap"] is not None
      and abs(n["gap"] - (-0.0546)) < 0.01, f"gap={n['gap']}")
check("Nov17 Nifty kept", n["kept_legs"] == 1
      and n["kept_net"] == -220.0,
      f"kept={n['kept_legs']} net={n['kept_net']}")

ok = all(c for _n, c, _d in CHECKS)
print(f"\nSELFTEST: {'ALL PASS' if ok else 'FAILURES PRESENT'} "
      f"({sum(1 for _n, c, _d in CHECKS if c)}/{len(CHECKS)})")
sys.exit(0 if ok else 1)
