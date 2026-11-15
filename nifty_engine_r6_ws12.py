#!/usr/bin/env python3
"""ROUND 6 WS1 (confirmation-native grid, Cycles 113-118) + WS2 (solo-
system causal books, Cycles 119-122). Freeze: nifty_engine_frozen.md
ROUND 6. Standing baseline opens as the causal book; any banking updates
it (supersession) and is written to nifty_engine_r6_standing.json for
WS3/WS4. Paper only, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r6_harness import (run_r6, set_current, native_population,
                                     solo_book, BOOK_GEOM)
from nifty_engine_r5_ws0 import causal_legs

TR = Path.home() / "workspace/trading"
standing = {"legs": None, "geom": BOOK_GEOM, "label": None}

def bank_if(c, legs, label):
    if c.get("gate_relative", {}).get("banked"):
        set_current(c, label)
        standing.update(legs=legs, label=label)
        print(f"  ^^ BANKED -> standing baseline is now: {label}")
    return c

# ---- baseline: causal book (asserted) ----
c0, _ = run_r6("r6_baseline_causal", causal_legs(), save=True, gate=False, quiet=True)
assert (c0["total"], c0["n"], c0["ft_pct"], c0["per_week"]) == (50618.00, 35, 34.3, 0.86), c0["total"]
set_current(c0, "Causal book (Round-5 WS0 baseline)")
standing.update(legs=causal_legs(), label="Causal book (Round-5 WS0 baseline)")
print(f"BASELINE SET: causal book +50,618.00 | 35 tr | FT 34.3% | 0.86/wk")

# ---- Cycle 113: WS1 centre (validation — must reproduce the causal book) ----
legs, _ = native_population(2, "09:55", True)
c, _ = run_r6("r6_c113_centre", legs)
assert c["total"] == 50618.00 and c["n"] == 35, "centre must reproduce causal book"
print("  ^^ Cycle 113 = validation reproduction of the baseline (not a candidate)")

# ---- Cycles 114-118: WS1 grid, one axis at a time from the centre ----
cells = [
    ("r6_c114_sys3",      dict(systems_needed=3, window="09:55", solo=True),  "WS1 sys=3 (win 09:55, solo lA)"),
    ("r6_c115_w1030",     dict(systems_needed=2, window="10:30", solo=True),  "WS1 win<=10:30 (sys 2, solo lA)"),
    ("r6_c116_w1130",     dict(systems_needed=2, window="11:30", solo=True),  "WS1 win<=11:30 (sys 2, solo lA)"),
    ("r6_c117_wnone",     dict(systems_needed=2, window=None,    solo=True),  "WS1 no window (sys 2, solo lA)"),
    ("r6_c118_solonever", dict(systems_needed=2, window="09:55", solo=False), "WS1 solo=never (sys 2, win 09:55)"),
]
for name, kw, label in cells:
    legs, notes = native_population(**kw)
    c, _ = run_r6(name, legs)
    bank_if(c, legs, label)

# ---- Cycles 119-122: WS2 solo-system causal books ----
for name, system in [("r6_c119_solo_lA", "(lA) v2"), ("r6_c120_solo_v5", "V5 v2"),
                     ("r6_c121_solo_skill", "Skill V3"), ("r6_c122_solo_volrix", "Volrix (b)")]:
    legs, missing = solo_book(system)
    if missing: print(f"  !! {system}: keys with no sysmap time (excluded, named): {missing}")
    c, _ = run_r6(name, legs)
    bank_if(c, legs, f"WS2 solo book: {system}")

Path(TR / "nifty_engine_r6_standing.json").write_text(json.dumps(standing, indent=1, default=str))
print("STANDING after WS1/WS2:", standing["label"])
