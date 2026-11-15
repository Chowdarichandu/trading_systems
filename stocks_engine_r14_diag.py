#!/usr/bin/env python3
"""ROUND 14 — pre-registration diagnostic (NOT a gate score).

GAP-FADE family (GAP-FADE + GAP-FADE-INC, book cell T125/S050):
first-passage excursion diagnosis on the sleeve's own banked
population, SAT-10/11/12 discipline, to choose the ONE adjacent
neighbour the round may freeze:
  - stop axis: of the trades the S050 stop kills, how many reach
    the +1.25% target before the -0.65% level (rescue), how many
    go deeper first, how many do neither before the 15:10
    square-off — rough swing of S065.
  - target axis: of the trades the T125 target banks, how many
    reach +1.50% before the -0.50% stop (reach), how many fall
    to the stop first, how many do neither — rough swing of T150.
Pick rule (stated before the diagnostic runs): the axis with
the larger combined (both-years) rough swing is frozen; a tie
goes to the stop axis. The gate, not this estimate, decides
(Lesson 31: an estimate can be sign-wrong; it only chooses
which ONE cell is worth an exact score).
Semantics: the sleeve's own `replay` (scan from the bar after
the entry bar, stop before target inside a bar, square-off at
the 15:10 close). All fade trades are LONG.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r6_builders as B

g = B.machinery()
STOCKS_E = g["STOCKS_E"]
DF = {"DOWN", "FLAT"}
COST = 40.0

fade = B.gap_rows("fade", 1.5, 1, 1.25, 0.5, only_dir="LONG",
                  cells=DF)
inc = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                 cells=DF, band=(1.25, 1.5),
                 comp_name="GAP-FADE-INC", entry_time="09:40")
sa = {yr: round(sum(t["net"] for t in fade[yr]), 2)
      for yr in (2025, 2026)}
si = {yr: round(sum(t["net"] for t in inc[yr]), 2)
      for yr in (2025, 2026)}
assert sa == {2025: 21470.27, 2026: 1492.21}, sa
assert si == {2025: 2305.22, 2026: 4763.03}, si
print(f"anchor OK: fade {sa}, inc {si} == book comp sums")

rows = []
for yr in (2025, 2026):
    rows += [(yr, t) for t in fade[yr]] + [(yr, t) for t in inc[yr]]

def scan(bars, ei, entry):
    """Replay at T125/S050 (LONG); return (reason, exit_idx,
    exit_price). Mirrors v2_build.replay: scan from ei+1, stop
    before target, square-off at the 15:10 close."""
    tgt = entry * 1.0125
    stp = entry * 0.995
    last = None
    for j in range(ei + 1, len(bars)):
        c = bars[j]
        if c["time"] > "15:10":
            break
        last = j
        if c["low"] <= stp:
            return "stop", j, stp
        if c["high"] >= tgt:
            return "target", j, tgt
        if c["time"] == "15:10":
            return "square", j, c["close"]
    if last is not None:
        return "square", last, bars[last]["close"]
    return None, None, None

def passage(bars, j0, entry, up_lvl, dn_lvl, inclusive_bar):
    """First passage from bar j0 (inclusive_bar: scan j0 itself,
    else from j0+1) to up_lvl (high) vs dn_lvl (low), stop-first
    inside a bar, square-off at 15:10 close. Returns
    (kind, price)."""
    start = j0 if inclusive_bar else j0 + 1
    last = None
    for j in range(start, len(bars)):
        c = bars[j]
        if c["time"] > "15:10":
            break
        last = j
        if c["low"] <= dn_lvl:
            return "down", dn_lvl
        if c["high"] >= up_lvl:
            return "up", up_lvl
        if c["time"] == "15:10":
            return "square", c["close"]
    if last is not None:
        return "square", bars[last]["close"]
    return "none", entry

res = {yr: {"stop_n": 0, "rescue": 0.0, "deeper": 0.0,
            "s_neither": 0.0, "tgt_n": 0, "reach": 0.0,
            "fallback": 0.0, "t_neither": 0.0}
       for yr in (2025, 2026)}
for yr, t in rows:
    spot, _daily = STOCKS_E[t["stock"]]
    bars = spot.get(t["date"], [])
    idx = {b["time"]: k for k, b in enumerate(bars)}
    ei = idx[t["entry_time"]]
    entry = float(bars[ei]["open"])
    reason, xi, xp = scan(bars, ei, entry)
    gross = 100.0 * (xp - entry)
    assert round(gross - COST, 2) == round(float(t["net"]), 2), t
    r = res[yr]
    if reason == "stop":
        r["stop_n"] += 1
        kind, pp = passage(bars, xi, entry, entry * 1.0125,
                           entry * 0.9935, inclusive_bar=False)
        r[{"up": "rescue", "down": "deeper"}.get(
            kind, "s_neither")] += 100.0 * (pp - entry) - gross
    elif reason == "target":
        r["tgt_n"] += 1
        kind, pp = passage(bars, xi, entry, entry * 1.015,
                           entry * 0.995, inclusive_bar=True)
        r[{"up": "reach", "down": "fallback"}.get(
            kind, "t_neither")] += 100.0 * (pp - entry) - gross

for yr in (2025, 2026):
    r = res[yr]
    r["stop_swing"] = round(r["rescue"] + r["deeper"]
                            + r["s_neither"], 2)
    r["tgt_swing"] = round(r["reach"] + r["fallback"]
                           + r["t_neither"], 2)
    print(yr, {k: (round(v, 2) if isinstance(v, float) else v)
               for k, v in r.items()})
cs = round(sum(res[yr]["stop_swing"] for yr in (2025, 2026)), 2)
ct = round(sum(res[yr]["tgt_swing"] for yr in (2025, 2026)), 2)
print(f"combined rough swings: S065 stop axis {cs}; "
      f"T150 target axis {ct}")
pick = "T125/S065 (stop step)" if cs >= ct else "T150/S050 (target step)"
print(f"PICK under the frozen rule: GAP-FADE family neighbour = {pick}")
