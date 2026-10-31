#!/usr/bin/env python3
"""Diagnosis pass (no candidate scoring): incumbent C3+G7 trade detail, plus the
full N1 pool under G7 broken down by confirmed/solo x representative system.
Nifty ONLY. Uses aggressive_score (frozen conventions)."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import base_legs, score_legs

B = base_legs("NIFTY")
def nsrc(l): return len([s for s in l["sources"].split(";") if s.strip()])
C3 = [l for l in B if nsrc(l) >= 2]
res, nc = score_legs(C3, stop=50, target=90, mode="runner_lock50")
print("== INCUMBENT C3+G7 TRADES ==")
for r in sorted(res, key=lambda x: x["date"]):
    print(r["date"], r["direction"], r["entry_time"], r["rep"], "| net", r["net"], "|", r["exit_reason"], "| ft", r["ft"])
bym = defaultdict(lambda: [0, 0.0, 0])
for r in res: bym[r["date"][:7]][0] += 1; bym[r["date"][:7]][1] += r["net"]; bym[r["date"][:7]][2] += r["ft"]
print("\nmonth: n, net, ft")
for m in sorted(bym): print(m, bym[m])
reasons = defaultdict(lambda: [0, 0.0])
for r in res: reasons[r["exit_reason"]][0] += 1; reasons[r["exit_reason"]][1] += r["net"]
print("\nexit reasons:", dict(reasons))
oct_res = [r for r in res if r["date"][5:7] == "10"]
print("\nOctober C3 legs:", [(r["date"], r["direction"], r["net"], r["exit_reason"]) for r in oct_res])

res_all, _ = score_legs(B, stop=50, target=90, mode="runner_lock50")
key2leg = {(l["date"], l["direction"]): l for l in B}
print("\n== FULL N1 POOL under G7, split confirmed/solo x rep ==")
split = defaultdict(lambda: [0, 0.0, 0])
for r in res_all:
    l = key2leg[(r["date"], r["direction"])]
    grp = ("CONF" if nsrc(l) >= 2 else "SOLO") + "|" + l["rep"]
    split[grp][0] += 1; split[grp][1] += round(r["net"], 2); split[grp][2] += r["ft"]
for k in sorted(split): print(k, split[k])
print("\n== SOLO legs under G7 by month ==")
sm = defaultdict(lambda: [0, 0.0])
for r in res_all:
    l = key2leg[(r["date"], r["direction"])]
    if nsrc(l) == 1: sm[r["date"][:7]][0] += 1; sm[r["date"][:7]][1] += round(r["net"], 2)
for m in sorted(sm): print(m, sm[m])
print("\nOctober solo legs under G7:", [(r["date"], r["direction"], key2leg[(r["date"], r["direction"])]["rep"], r["net"], r["exit_reason"]) for r in res_all if r["date"][5:7] == "10" and nsrc(key2leg[(r["date"], r["direction"])]) == 1])
