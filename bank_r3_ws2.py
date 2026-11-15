#!/usr/bin/env python3
"""ROUND 3 WORKSTREAM 2 driver (Cycles 45-52): generate the mechanised
setup families (bank_r3_setups), fetch any missing premium contracts via
the expired-instruments route, then judge each family as add-ons on book
v16 under the full controls gate. Definitions frozen in
bank_engine_frozen.md (ROUND 3 appendix + amendment)."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r3_setups import generate
from bank_r3_core import admit, judge, BASE_KEYS

TR = Path.home() / "workspace/trading"
ORDER = [("S3A", "Cycle 45 S3-A OR>=400 R1 on v16"),
         ("S3B", "Cycle 46 S3-B OR 350-580 R1 on v16"),
         ("S3C", "Cycle 47 S3-C OR 400-650 R1 on v16"),
         ("S3D", "Cycle 48 S3-D wick rejection on v16"),
         ("S3E", "Cycle 49 S3-E close-below-PDC on v16"),
         ("S4", "Cycle 50 S4 reclaim (spec reading) on v16"),
         ("S4B", "Cycle 51 S4B reclaim (v4 as-coded) on v16"),
         ("S1RB", "Cycle 52 S1 retest-hold on derived Red bands on v16")]

def main():
    gen = generate()
    targets = set()
    for name, legs in gen.items():
        _, _, _, nc = admit(legs, BASE_KEYS)
        for l in nc:
            targets.add((l["date"], l["direction"], l["strike"], l["expiry"]))
    print(f"generated: { {k: len(v) for k, v in gen.items()} }")
    print(f"missing contracts to fetch: {len(targets)}")
    if targets:
        tf = TR / "bank_r3_ws2_fetch_targets.json"
        tf.write_text(json.dumps(sorted(targets)))
        r = subprocess.run([sys.executable, str(TR / "bank_r3_fetch.py"), str(tf)],
                           capture_output=True, text=True)
        print(r.stdout[-1500:]); print(r.stderr[-500:])
        import aggressive_score
        aggressive_score._cache.clear()  # misses were memoised pre-fetch
    results = {}
    for name, label in ORDER:
        results[name] = judge(label, gen[name])
    (TR / "bank_r3_ws2_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r3_ws2_results.json")

if __name__ == "__main__":
    main()
