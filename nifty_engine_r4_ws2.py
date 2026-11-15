#!/usr/bin/env python3
"""ROUND 4 WS2 — Volrix parameter grid, Cycles 74-91 (frozen in
nifty_engine_frozen.md Round-4 WS2 before scoring). Confirmation-toggle
on recorded pool legs; centre cell (-1.0%, 10, book) = Cycle 82 must
reproduce the adopted book +114,921.75 exactly."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r2_harness import pool_sets
from nifty_engine_score import nsrc
from nifty_engine_r4_harness import volrix_firings, run_r4, set_current, CURRENT

def build_cell(trigger, cooldown, exit_variant):
    F = set(volrix_firings(trigger, cooldown))
    B, _, _ = pool_sets()
    pool = []
    for l in B:
        l = dict(l)
        if l["direction"] == "CE":
            srcs = [s.strip() for s in l["sources"].split(";") if s.strip()]
            if l["date"] in F and "Volrix (b)" not in srcs:
                srcs.append("Volrix (b)")
            if l["date"] not in F and "Volrix (b)" in srcs:
                srcs.remove("Volrix (b)")
            l["sources"] = ";".join(srcs)
        pool.append(l)
    C3L = [l for l in pool if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
    EXP0 = [l for l in C3L if l["date"] != l["expiry"]]
    book = [l for l in EXP0 if not (nsrc(l) >= 2 and l["entry_time"] > "09:55")]
    if exit_variant == "plain":
        for l in book:
            if "Volrix (b)" in l["sources"]:
                l["plain"] = True
    return book

results = {}
cyc = 74
for trigger in (-0.75, -1.0, -1.25):
    for cooldown in (5, 10, 15):
        for xv in ("book", "plain"):
            legs = build_cell(trigger, cooldown, xv)
            name = f"run3r4_c{cyc}_volrix_t{trigger}_cd{cooldown}_{xv}"
            c, res = run_r4(name, legs)
            vk = sorted(r["date"] for r in res if "Volrix (b)" in r["sources"])
            results[cyc] = dict(trigger=trigger, cooldown=cooldown, exit=xv,
                                total=c["total"], n=c["n"], ft=c["ft_pct"],
                                per_week=c["per_week"], volrix_legs=vk,
                                banked=c["gate_vs_current"]["banked"],
                                flagged=c["gate_vs_current"]["flagged_freq_only"],
                                failed=[k for k, v in c["gate_vs_current"]["checks"].items() if not v])
            if cyc == 82:
                assert c["total"] == 114921.75, f"CENTRE CELL MISMATCH: {c['total']}"
                print("CENTRE CELL (Cycle 82) reproduces the adopted book exactly ✓")
            if c["gate_vs_current"]["banked"]:
                set_current(c, f"Round-4 Cycle {cyc} (Volrix t{trigger} cd{cooldown} {xv})")
                print(f"*** BANKED Cycle {cyc}: new current = {CURRENT['total']:+,.2f}")
            cyc += 1
Path("nifty_engine_r4_ws2_results.json").write_text(json.dumps(results, indent=1))
print("\nWS2 done. Current candidate:", CURRENT["label"], f"{CURRENT['total']:+,.2f}")
