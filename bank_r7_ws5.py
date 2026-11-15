#!/usr/bin/env python3
"""ROUND 7 WS5 — SQUARE-OFF RE-GATE ON THE CAUSAL BOOK (Cycles 160-161).

The 15:20 square-off was banked in Round 3 on the pre-audit book. On
the causal v21 book, re-gate the two neighbours, one cell each:
C160 = 15:10, C161 = 15:25 (incumbent 15:20 = the v21 reference).
The square-off constant lives in bank_r5_core.SQ (final-row scoring in
build_base_rows and add-on replay) and is re-exported into
bank_r6_core (assemble6's add-on scoring); both are patched for the
duration of each cell and restored after. Everything else — legs,
admissions, geometry — is the frozen v21 construction.
CAUSALITY CERTIFICATE: the square-off time is a session parameter fixed
in advance; no entry, admission or feature changes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r6_core as c6
from bank_r7_core import judge7, v21_ref
from bank_r6_core import v20_inputs

ref = v21_ref()          # computed at the incumbent SQ = 15:20
pooled, ns1 = v20_inputs()
assert c5.SQ == "15:20" and c6.SQ == "15:20"
for cyc, sq in ((160, "15:10"), (161, "15:25")):
    c5.SQ = sq
    c6.SQ = sq
    try:
        judge7(f"C{cyc} SQUARE-OFF {sq}", ref, pooled, ns1)
    finally:
        c5.SQ = "15:20"
        c6.SQ = "15:20"
chk = judge7("POST-RESTORE CHECK (must equal v21 exactly)", ref, pooled, ns1)
assert chk["net"] == ref[0]["net"] and chk["n"] == ref[0]["n"]
print("restore verified: SQ back at 15:20, book reproduces v21 exactly.")
