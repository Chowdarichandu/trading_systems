#!/usr/bin/env python3
"""ROUND 3 WORKSTREAM 1 (Cycles 42-44): the NS3 / NS5a / NS5b add-on families,
premium-scored for the first time on the FULL post-fetch census (the missing
candles were fetched in bank_r3_fetch.py; definitions frozen in
bank_engine_frozen.md ROUND 3 appendix). Each family is judged as add-ons on
book v16 under the full controls gate (bank_r3_core.judge)."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import EXPIRIES
from bank_r3_core import judge

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"
FAMS = [("NS3", "index_options_newsetup_ns3_trades_jan_oct_2026.csv", "NS3_gapclass", "Cycle 42 NS3 on v16"),
        ("NS5a", "index_options_newsetup_ns5a_trades_jan_oct_2026.csv", "NS5A_skillrescan", "Cycle 43 NS5a on v16"),
        ("NS5b", "index_options_newsetup_ns5b_trades_jan_oct_2026.csv", "NS5B_ce_mirror_rescan", "Cycle 44 NS5b on v16")]

def build(fname, famname, prefix):
    legs = []
    for r in csv.DictReader(open(TR / fname)):
        if r["index"] != SYM: continue
        legs.append(dict(date=r["date"], index=SYM, direction=r["direction"],
                         entry_time=r["entry_time"], signal_time=r["signal_time"],
                         strike=int(round(float(r["entry_spot"]) / 100.0) * 100),
                         expiry=next(e for e in EXPIRIES if e >= r["date"]), lot=30,
                         rep=prefix + "_" + r["leg"], sources=prefix, family=famname))
    return legs

def main():
    results = {}
    for prefix, fname, famname, label in FAMS:
        legs = build(fname, famname, prefix)
        results[prefix] = judge(label, legs)
    (TR / "bank_r3_ws1_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r3_ws1_results.json")

if __name__ == "__main__":
    main()
