#!/usr/bin/env python3
"""Cycle 10 — SA2D per-direction 2-loss stand-aside, skip next 1.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Controls in same run."""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score, run_candidate

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)

# Score the full best book first; the SA2D filter is causal (uses only prior
# same-direction kept legs' realised nets, each known before the next entry).
full, nc0 = score(C3L, geom)
full_sorted = sorted(full, key=lambda x: (x["date"], x["entry_time"]))
leg_by_key = {(l["date"], l["direction"]): l for l in C3L}
streak = defaultdict(int); skipnext = defaultdict(bool)
kept_keys, skipped = [], []
for r in full_sorted:
    d = r["direction"]
    if skipnext[d]:
        skipped.append((r["date"], d, r["net"])); skipnext[d] = False; streak[d] = 0; continue
    kept_keys.append((r["date"], d))
    if r["net"] < 0:
        streak[d] += 1
        if streak[d] >= 2: skipnext[d] = True
    else:
        streak[d] = 0
kept_legs = [leg_by_key[k] for k in kept_keys]
c, res = run_candidate("cycle10_sa2d", kept_legs, geom)
c["skipped_legs"] = skipped
c["full_book_total_check"] = round(sum(r["net"] for r in full), 2)
print(json.dumps(c, indent=1, default=str))
Path.home().joinpath("workspace/trading/nifty_engine_cycle10_summary.json").write_text(json.dumps(c, indent=1, default=str))
