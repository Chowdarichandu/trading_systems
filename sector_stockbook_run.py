#!/usr/bin/env python3
"""SECTOR-ADDITIONS TEST — Stock Book (build_book machinery) on the
enlarged 37-name universe. Within-machinery comparison: BOTH the
25-name control and the 37-name enlarged run are built by
wide100_stockbook.run_build on the SAME root (data/wide100, which
holds all 37 names in the frozen layout) — the control is additionally
cross-checked against the existing sarvaritu-root sb25 run
(wide100_stockbook_sb25_results.json). Research only.
Basis: equity cash, per 100 shares PROVISIONAL, Rs40/trade."""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import wide100_stockbook as SB

WS = "/home/hatch/workspace/trading"
ROOT = f"{WS}/data/wide100"
FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]
ADD12 = ["ULTRACEMCO", "LT", "SBILIFE", "APOLLOHOSP", "ICICIBANK", "SBIN",
         "RELIANCE", "INFY", "M&M", "BHARTIARTL", "SUNPHARMA", "TITAN"]

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "control25":
        raise SystemExit(SB.run_build(ROOT, FROZEN25, "sector25w"))
    if which == "enlarged37":
        raise SystemExit(SB.run_build(ROOT, FROZEN25 + ADD12, "sector37"))
    raise SystemExit(2)
