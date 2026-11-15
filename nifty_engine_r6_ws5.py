#!/usr/bin/env python3
"""ROUND 6 WS5 (Cycle 130) — combination of the round's two bankings
(C124 lock60/TGT2-175 + C129 square-off 15:20), re-gated whole-book
against the ROUND-OPENING baseline (the causal book at book geometry).
The bankings were applied sequentially under supersession (each gated
at its step); this cycle is the formal combined re-gate the freeze
pre-registered. Paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r6_harness import run_r6, set_current, BOOK_GEOM
from nifty_engine_r5_ws0 import causal_legs

TR = Path.home() / "workspace/trading"
standing = json.loads((TR / "nifty_engine_r6_standing.json").read_text())
legs, geom, label = standing["legs"], standing["geom"], standing["label"]

c0, _ = run_r6("r6_ws5_roundopen", causal_legs(), geom=BOOK_GEOM, save=False, gate=False, quiet=True)
assert c0["total"] == 50618.00
set_current(c0, "ROUND-OPENING baseline: causal book at book geometry (lock50/TGT2-175, sq 15:10)")
print(f"ROUND-OPEN baseline: {c0['total']:+,.2f} | FT {c0['ft_pct']}% | {c0['per_week']}/wk")

c, res = run_r6("r6_c130_combination", legs, geom=geom)
print("COMBINATION (C124+C129) vs round-open:", "BANKED (already standing)" if c["gate_relative"]["banked"] else "FAIL")
print(json.dumps({m: v for m, v in c["month_table"].items()}, indent=0))
Path(TR / "nifty_engine_r6_final_book.json").write_text(json.dumps(
    {"label": label, "geom": geom, "legs": legs,
     "summary": {k: c[k] for k in ("total", "n", "ft_pct", "per_week", "halves",
                                   "ex_top3", "placebo_shift30_total", "month_table",
                                   "red_month_ends")}}, indent=1, default=str))
