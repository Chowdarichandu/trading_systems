#!/usr/bin/env python3
"""ROUND 6 WS3 (G7 re-grid, Cycles 123-127) + WS4 (square-off axis,
Cycles 128-129) on the standing book left by WS1/WS2 (loaded from
nifty_engine_r6_standing.json). Freeze: nifty_engine_frozen.md ROUND 6.
Bankings update the standing baseline (supersession). Paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r6_harness import run_r6, set_current, BOOK_GEOM

TR = Path.home() / "workspace/trading"
standing = json.loads((TR / "nifty_engine_r6_standing.json").read_text())
legs, geom, label = standing["legs"], standing["geom"], standing["label"]
print(f"STANDING BOOK for WS3/WS4: {label} | legs {len(legs)} | geom {geom}")

c0, _ = run_r6("r6_ws34_baseline", legs, geom=geom, save=True, gate=False, quiet=True)
set_current(c0, label)
print(f"BASELINE SET: {c0['total']:+,.2f} | n {c0['n']} | FT {c0['ft_pct']}% | {c0['per_week']}/wk")

def bank_if(c, new_geom, new_label):
    global geom, label
    if c.get("gate_relative", {}).get("banked"):
        geom, label = new_geom, new_label
        set_current(c, label)
        print(f"  ^^ BANKED -> standing geometry is now: {label}")
    return c

# ---- Cycles 123-127: WS3 lock x TGT2 grid (centre 50/175 = standing) ----
for name, lock, tgt2 in [("r6_c123_lock40_t175", 40.0, 175.0),
                         ("r6_c124_lock60_t175", 60.0, 175.0),
                         ("r6_c125_lock40_t150", 40.0, 150.0),
                         ("r6_c126_lock50_t150", 50.0, 150.0),
                         ("r6_c127_lock60_t150", 60.0, 150.0)]:
    g = dict(geom, lock=lock, tgt2=tgt2)
    c, _ = run_r6(name, legs, geom=g)
    bank_if(c, g, f"{label} + lock{int(lock)}/TGT2-{int(tgt2)}")

# ---- Cycles 128-129: WS4 square-off axis on the standing book ----
for name, sq in [("r6_c128_sq1445", "14:45"), ("r6_c129_sq1520", "15:20")]:
    g = dict(geom, sq=sq)
    c, _ = run_r6(name, legs, geom=g)
    bank_if(c, g, f"{label} + sq {sq}")

standing.update(legs=legs, geom=geom, label=label)
Path(TR / "nifty_engine_r6_standing.json").write_text(json.dumps(standing, indent=1, default=str))
print("STANDING after WS3/WS4:", label, "| geom", geom)
