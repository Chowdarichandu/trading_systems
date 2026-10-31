#!/usr/bin/env python3
"""RUN 2 Cycle 1 (engine Cycle 12) — EXP0: skip legs whose trade date == expiry.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Controls in same run
(run_candidate: timing audit, +30-min placebo, halves, month table, ex-top-3,
independent re-sum)."""
import sys, json
from pathlib import Path
from datetime import date as ddate
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score, run_candidate

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)

full, nc0 = score(C3L, geom)
ftot = round(sum(r["net"] for r in full), 2)
print("full book check:", len(full), ftot, "NC", nc0, "expect 63 / 92437.75 / 0")
assert len(full) == 63 and ftot == 92437.75 and nc0 == 0

kept = [l for l in C3L if l["date"] != l["expiry"]]
dropped = [(l["date"], l["direction"], l["expiry"]) for l in C3L if l["date"] == l["expiry"]]
print("DTE0 legs dropped:", dropped)
c, res = run_candidate("run2_cycle12_exp0", kept, geom)
c["dropped_dte0_legs"] = dropped
c["full_book_total_check"] = ftot
print(json.dumps(c, indent=1, default=str))
Path.home().joinpath("workspace/trading/nifty_engine_run2_cycle12_summary.json").write_text(json.dumps(c, indent=1, default=str))
