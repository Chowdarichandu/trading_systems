#!/usr/bin/env python3
"""ROUND 3 WS4 (Cycles 47-73): adopted-book geometry micro-grid, frozen in
nifty_engine_frozen.md before scoring. lock {40,50,60} x TGT2 {160,175,190}
x BE arm {40,50,60} on the 44 adopted legs (monthly contracts)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r3_harness import run_r3, adopted_set

_, CH3R, _ = adopted_set()
cyc = 47
for lock in (40.0, 50.0, 60.0):
    for tgt2 in (160.0, 175.0, 190.0):
        for arm in (40.0, 50.0, 60.0):
            print(f"\n--- Cycle {cyc}: lock {lock:.0f} TGT2 {tgt2:.0f} arm {arm:.0f} ---")
            run_r3(f"run3r3_cycle{cyc}_lock{int(lock)}_tgt{int(tgt2)}_arm{int(arm)}",
                   CH3R, lock=lock, tgt2=tgt2, arm=arm)
            cyc += 1
print(f"\ngrid done: cycles 47..{cyc - 1}")
