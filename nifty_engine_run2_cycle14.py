#!/usr/bin/env python3
"""RUN 2 Cycle 3 (engine Cycle 14) — WROOM5: skip legs whose directional room
to the prior-5-trading-day high (CE) / low (PE), measured from the last
pre-entry spot close, is in [0, 0.25%). Frozen in nifty_engine_frozen.md
before scoring (same 0.25% threshold as Cycle 13, not re-tuned).
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Controls in same run
(run_candidate: timing audit, +30-min placebo, halves, month table, ex-top-3,
independent re-sum)."""
import sys, json, csv
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score, run_candidate

TR = Path.home() / "workspace/trading"
spot = {}
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day, tm = r["timestamp"][:10], r["timestamp"][11:16]
        spot.setdefault(day, []).append((tm, float(r["open"]), float(r["high"]),
                                         float(r["low"]), float(r["close"])))
for d in spot: spot[d].sort()
days_sorted = sorted(spot)

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)

EXP0 = [l for l in C3L if l["date"] != l["expiry"]]
full, nc0 = score(EXP0, geom)
ftot = round(sum(r["net"] for r in full), 2)
print("EXP0 book check:", len(full), ftot, "NC", nc0, "expect 59 / 98001.0 / 0")
assert len(full) == 59 and ftot == 98001.0 and nc0 == 0
net_by_key = {(r["date"], r["direction"]): r["net"] for r in full}

def room5(l):
    day = l["date"]; bars = spot.get(day, [])
    pre = [b for b in bars if b[0] < l["entry_time"]]
    if not pre: return None
    ref = pre[-1][4]
    i = days_sorted.index(day)
    if i < 5: return None
    prev5 = days_sorted[i - 5:i]
    h5 = max(b[2] for d in prev5 for b in spot[d])
    l5 = min(b[3] for d in prev5 for b in spot[d])
    if l["direction"] == "CE": return (h5 - ref) / ref
    return (ref - l5) / ref

kept, dropped, noroom = [], [], []
for l in EXP0:
    rm = room5(l)
    if rm is None: noroom.append(l); kept.append(l); continue
    if 0 <= rm < 0.0025:
        dropped.append((l["date"], l["direction"], l["entry_time"], round(rm * 100, 3),
                        net_by_key.get((l["date"], l["direction"]))))
    else:
        kept.append(l)
print("legs with no prior-5-day/spot data (kept):", len(noroom))
print("WROOM5 legs dropped (date, dir, time, room%, EXP0 net):")
for d in dropped: print(" ", d)
print("dropped sum (EXP0 nets):", round(sum(d[4] for d in dropped if d[4] is not None), 2))

c, res = run_candidate("run2_cycle14_wroom5", kept, geom)
c["dropped_wroom5_legs"] = [list(d) for d in dropped]
c["exp0_book_total_check"] = ftot
c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
print(json.dumps(c, indent=1, default=str))
Path(TR / "nifty_engine_run2_cycle14_summary.json").write_text(json.dumps(c, indent=1, default=str))
