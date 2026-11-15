#!/usr/bin/env python3
"""ROUND 3 census (BANKNIFTY ONLY): for the NS3 / NS5a / NS5b add-on families,
classify every source leg: key status vs the book-v4 pool (the original
Cycles 8-10 census) and vs the taken book v16, entry premium from the candle
cache, premium-band status, and NOT_COMPUTED legs (no cached candles) with
their fetch targets. Read-only; writes bank_r3_census.json."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import EXPIRIES
from bank_engine_cycle import _entry_premium
from bank_engine_repro import build_v1_legs
from bank_engine_cycle import FILTERS
from bank_r2_expiry import build_geo

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"
FAMS = [("NS3", "index_options_newsetup_ns3_trades_jan_oct_2026.csv", "NS3_gapclass"),
        ("NS5a", "index_options_newsetup_ns5a_trades_jan_oct_2026.csv", "NS5A_skillrescan"),
        ("NS5b", "index_options_newsetup_ns5b_trades_jan_oct_2026.csv", "NS5B_ce_mirror_rescan")]

def v3_pool_keys():
    legs, _, _ = build_v1_legs()
    legs = FILTERS["drop_ns1_ce"](legs)
    legs = FILTERS["drop_prem_400_550"](legs)
    return {(l["date"], l["direction"]) for l in legs}

def v16_keys():
    rows, nc, lbk = build_geo((50.0, 90.0), 0)
    assert abs(sum(r["net"] for r in rows) - 106517.00) < 0.005 and len(rows) == 82
    return {(r["date"], r["direction"]) for r in rows}

def main():
    v4k, v16k = v3_pool_keys(), v16_keys()
    out = {}
    fetch_targets = {}
    for fam, fname, famname in FAMS:
        recs = []
        for r in csv.DictReader(open(TR / fname)):
            if r["index"] != SYM: continue
            strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
            exp = next(e for e in EXPIRIES if e >= r["date"])
            leg = dict(date=r["date"], index=SYM, direction=r["direction"],
                       entry_time=r["entry_time"], strike=strike, expiry=exp, lot=30,
                       rep=fam.upper() + "_" + r["leg"], sources=fam.upper(), family=famname)
            ep = _entry_premium(leg)
            key = (r["date"], r["direction"])
            rec = dict(date=r["date"], direction=r["direction"], entry_time=r["entry_time"],
                       signal_time=r["signal_time"], strike=strike, expiry=exp,
                       subleg=r["leg"], entry_premium=ep,
                       key_used_v4=key in v4k, key_used_v16=key in v16k,
                       band=(ep is not None and 400.0 <= ep < 550.0))
            recs.append(rec)
            if ep is None and key not in v16k:
                fetch_targets[(r["date"], r["direction"], strike, exp)] = True
        out[fam] = recs
        nc16 = [r for r in recs if r["entry_premium"] is None and not r["key_used_v16"]]
        nc4 = [r for r in recs if r["entry_premium"] is None and not r["key_used_v4"]]
        print(f"{fam}: total={len(recs)} NC_vs_v16keys={len(nc16)} NC_vs_v4keys={len(nc4)}")
    (TR / "bank_r3_census.json").write_text(json.dumps(
        dict(families=out, fetch_targets=sorted(fetch_targets.keys())), indent=1))
    print(f"fetch targets (unique contracts): {len(fetch_targets)}")
    for t in sorted(fetch_targets.keys()): print("  ", t)

if __name__ == "__main__":
    main()
