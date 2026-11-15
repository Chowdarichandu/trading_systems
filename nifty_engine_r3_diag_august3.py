#!/usr/bin/env python3
"""ROUND 3 WS1 diagnosis #3: the frozen-signature candidate set
(PE legs, prior-day spot return in (-0.50%, -0.25%)) — monthly vs weekly
carriage per leg, adopted geometry. Diagnostic only, pre-freeze."""
import sys, csv, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r3_harness import score_r3, adopted_set, candles_exact, replay_r3

TR = Path.home() / "workspace/trading"
rows = list(csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_daily.csv")))
daily = {r["date"]: float(r["close"]) for r in rows}
order = [r["date"] for r in rows]
prev = {order[i]: order[i - 1] for i in range(1, len(order))}
def pdret(d):
    p = prev.get(d)
    return (daily[d] / daily[p] - 1) * 100 if p else None

EXP0, CH3R, DIFF = adopted_set()
resA, _, _ = score_r3(CH3R, lock=50.0, tgt2=175.0, arm=50.0)
netA = {(r["date"], r["direction"]): r["net"] for r in resA}
wmap = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]

sig = []
for l in CH3R:
    pd = pdret(l["date"])
    if l["direction"] == "PE" and pd is not None and -0.50 < pd < -0.25:
        wexp = wmap[f"{l['date']}|{l['direction']}"]
        cs = candles_exact("NIFTY", l["strike"], l["direction"], l["date"], wexp)
        r = replay_r3(cs, l["entry_time"], lock=50.0, tgt2=175.0, arm=50.0) if cs else None
        sig.append((l["date"], round(pd, 3), netA[(l["date"], l["direction"])],
                    (r["net"] if r else None), (r["exit_reason"] if r else "NO CANDLES"), wexp))
print("signature legs (PE, prior-day return in (-0.50%, -0.25%)):")
tm = tw = 0.0
for d, pd, m, w, rsn, wexp in sig:
    print(f"  {d} pd={pd:+.3f} monthly={m:+,.2f} weekly(exp {wexp})={w if w is None else format(w, '+,.2f')} {rsn}")
    tm += m; tw += (w or 0.0)
print(f"  SUM monthly {tm:+,.2f} | weekly {tw:+,.2f} | weekly delta {tw - tm:+,.2f} | stand-aside delta {-tm:+,.2f}")
