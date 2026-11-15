#!/usr/bin/env python3
"""ROUND 6 — ADMISSION-CAUSALITY AUDIT of the incumbent book (R6-11),
on the Nifty Round-5 WS0 model: every admission condition of every
component must be fully knowable at its recorded entry bar.

Mechanical per-row checks (recomputed from stored data, never from the
book's own claims):
  ALL        no weekend rows.
  F4         entry_time >= 10:00 (the premove completes at 10:00);
             premove recomputed bar-by-bar (last close < 10:00 vs the
             09:30 bar open, ctx-candles definition): 0.5% <= |pm| <
             1.0% and dir == sign(pm); below50(day) recomputed from
             NIFTY daily (prev close <= trailing-50 mean, prior bars
             only).
  INV-LONG   cond_inv1 date gate recomputed (prev close <= ma50);
             entry_time <= 11:00 (R2-07 cutoff).
  INV-ABOVE  g1 date gate recomputed (prev close > ma50);
             entry_time <= 10:30 (frozen cutoff).
  INV-R3     below50 date gate recomputed; entry_time <= 11:00.
  N4-V3      entry_time == 09:35 (signal = 09:25 bar close, known
             09:30); move recomputed (floor_lib.n4_move, validated):
             |move| >= 0.8 (R2-17 law), dir == sign(move), the
             one-sided cap (no LONG row with move >= +3.0, FLOOR-2);
             (stock, day) is a machinery reaction day.
  P2F        entry = R+1 trading day, |reaction_ret| >= 2.5,
             dir == sign(ret), entry_time == 09:15. (ret = R close /
             R-1 close - 1, complete at R's close — before entry.)
  P2F-R2     same at R+2.  R2-LOWBAND same at R+2, 2.0 <= |ret| < 2.5.
  GAP-FADE   gap recomputed (bar-0 open / prior close): <= -1.5%
             (LONG fade), dir LONG, regime label in {DOWN, FLAT}
             (labels are prior-day-only by construction), entry_time
             == the second bar's time (entry strictly after the print
             that defines the signal).
  GAP-FADE-INC  gap in (-1.5%, -1.25%], labels in {DOWN, FLAT},
             entry_time == 09:40 with bar index >= 1.

Code-level certifications (read, not re-run): find_v4_from /
find_skor_from build state bar-by-bar in order and return at bar i
using bars <= i; entries are at idx+1 (validation run_chain / build2,
with build2's own _AUDIT asserting entry/signal >= 10:00 for F4);
pool_pick's prospective tie-break is UNREACHABLE across heads — RANK
gives v4 setups 1..3 and skor setups 0, so the primary key always
decides a cross-head pick and no later bar's price can choose an
earlier entry; ADR map uses the prior 10 daily bars only; chain
rounds are sequential counts of completed same-day signals;
results_events takes R = the calendar reaction_date verbatim (no
return-based selection); FL.LABELS uses closes[i-1] and windows
ending at i (prior day only).
"""
import sys, json
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_floor_lib as FL
import stocks_engine_r2_lib as R
import stocks_engine_r6_lib as R6

books = R6.load_books()
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E = g["STOCKS_E"]
rc = g["reaction_candidates"]
LABELS = FL.LABELS

# ------------------------------------------------- NIFTY daily (merged,
# same merge as floor_lib._nifty_labels) -------------------------------
daily_n = []
with open(f"{FL.WS}/data/full_hist/NIFTY/spot_daily.csv") as f:
    import csv as _csv
    for r in _csv.DictReader(f):
        daily_n.append((r["date"][:10], float(r["close"])))
have = {d for d, _ in daily_n}
with open(f"{FL.WS}/data/sarvaritu_fwd/NIFTY/spot_daily.csv") as f:
    for r in _csv.DictReader(f):
        d = r["date"][:10]
        if d not in have:
            daily_n.append((d, float(r["close"])))
daily_n.sort()
NCLOSES = [c for _, c in daily_n]
NIDX = {d: i for i, (d, _) in enumerate(daily_n)}

def below50(day):
    i = NIDX.get(day)
    if i is None or i < 50:
        return None
    return NCLOSES[i - 1] <= sum(NCLOSES[i - 50:i]) / 50

def above50(day):
    b = below50(day)
    return None if b is None else (not b)

# ------------------------------------------------------- candidates ----
cand = {}   # (symbol, R) -> reaction_ret_pct
RDAYS = set()
for cal, lo, hi in ((f"{WS}/stock_event_calendar_2025.csv",
                     "2025-01-01", "2025-12-31"),
                    (f"{WS}/stock_event_calendar_jan_oct_2026.csv",
                     "2026-01-01", "2026-12-31")):
    for c in rc(cal, lo, hi):
        cand[(c["symbol"], c["R"])] = c["reaction_ret_pct"]
        RDAYS.add((c["symbol"], c["R"]))
print(f"reaction candidates: {len(cand)}")

DIDX = {sym: {d["date"]: i for i, d in enumerate(STOCKS_E[sym][1])}
        for sym in STOCKS_E}

viol = defaultdict(list)   # comp -> [(row, why)]

def flag(comp, t, why):
    viol[comp].append({"date": t["date"], "stock": t["stock"],
                       "dir": t["dir"], "entry_time": t["entry_time"],
                       "net": t["net"], "why": why})

def premove(sym, day):
    spot, daily = STOCKS_E[sym]
    bars = [b for b in spot.get(day, []) if b["time"] >= "09:30"]
    if not bars:
        return None
    pre = [b for b in bars if b["time"] < "10:00"]
    if not pre or not bars[0]["open"]:
        return None
    return pre[-1]["close"] / bars[0]["open"] - 1

for yr in (2025, 2026):
    for t in books[yr]:
        comp, day, sym = t["comp"], t["date"], t["stock"]
        if R._wk(day):
            flag(comp, t, "weekend row")
        spot, daily = STOCKS_E[sym]
        bars = spot.get(day, [])
        didx = DIDX[sym]
        i = didx.get(day)
        if comp == "F4":
            if t["entry_time"] < "10:00":
                flag(comp, t, f"entry {t['entry_time']} < 10:00 "
                              f"measurement completion")
            pm = premove(sym, day)
            if pm is None or not (0.00495 <= abs(pm) < 0.01005):
                flag(comp, t, f"premove {pm} outside [0.5%, 1.0%)")
            elif t["dir"] != ("LONG" if pm > 0 else "SHORT"):
                flag(comp, t, "dir != sign(premove)")
            if below50(day) is not True:
                flag(comp, t, "day not below50 (recomputed)")
        elif comp == "INV-LONG":
            if t["entry_time"] > "11:00":
                flag(comp, t, f"entry {t['entry_time']} past 11:00 "
                              f"cutoff")
            if below50(day) is not True:
                flag(comp, t, "cond_inv1 gate fails (recomputed: day "
                              "is above50)")
        elif comp == "INV-ABOVE":
            if t["entry_time"] > "10:30":
                flag(comp, t, f"entry {t['entry_time']} past 10:30 "
                              f"cutoff")
            if above50(day) is not True:
                flag(comp, t, "g1 gate fails (recomputed: day not "
                              "above50)")
        elif comp == "INV-R3":
            if t["entry_time"] > "11:00":
                flag(comp, t, f"entry {t['entry_time']} past bound")
            if below50(day) is not True:
                flag(comp, t, "below50 gate fails (recomputed)")
        elif comp == "N4-V3":
            if t["entry_time"] != "09:35":
                flag(comp, t, f"entry {t['entry_time']} != 09:35")
            mv = FL.n4_move(sym, day)
            if mv is None:
                flag(comp, t, "n4 move not computable")
            else:
                if abs(mv) < 0.795:
                    flag(comp, t, f"|move| {mv} < 0.8 threshold")
                if t["dir"] != ("LONG" if mv > 0 else "SHORT"):
                    flag(comp, t, "dir != sign(move)")
                if t["dir"] == "LONG" and mv >= 2.995:
                    flag(comp, t, f"LONG move {mv} >= +3.0 one-sided "
                                  f"cap (FLOOR-2) violated")
            if (sym, day) not in RDAYS:
                flag(comp, t, "not a machinery reaction day")
        elif comp in ("P2F", "P2F-R2", "R2-LOWBAND"):
            lag = 1 if comp == "P2F" else 2
            if t["entry_time"] != "09:15":
                flag(comp, t, f"entry {t['entry_time']} != 09:15")
            ok = False
            if i is not None and i - lag >= 0:
                Rday = daily[i - lag]["date"]
                ret = cand.get((sym, Rday))
                if ret is not None:
                    ok = True
                    if comp == "R2-LOWBAND":
                        if not (1.995 <= abs(ret) <= 2.494):
                            flag(comp, t, f"|ret| {ret} outside "
                                          f"[2.0, 2.5)")
                    elif abs(ret) < 2.495:
                        flag(comp, t, f"|ret| {ret} < 2.5 band")
                    if t["dir"] != ("LONG" if ret > 0 else "SHORT"):
                        flag(comp, t, "dir != sign(reaction_ret)")
            if not ok:
                flag(comp, t, f"no reaction candidate at R+{lag}")
        elif comp in ("GAP-FADE", "GAP-FADE-INC"):
            if not bars or i is None or i == 0:
                flag(comp, t, "no bars / no prior day")
                continue
            gap = (bars[0]["open"] / daily[i - 1]["close"] - 1) * 100
            if comp == "GAP-FADE":
                if gap > -1.495:
                    flag(comp, t, f"gap {gap:.2f} > -1.5% threshold")
                if len(bars) < 2 or t["entry_time"] != bars[1]["time"]:
                    flag(comp, t, "entry_time != second bar's time "
                                  "(entry not strictly after the "
                                  "signal print bar)")
            else:
                if not (-1.505 < gap <= -1.245):
                    flag(comp, t, f"gap {gap:.2f} outside "
                                  f"(-1.5%, -1.25%] increment band")
                idx = {b["time"]: k for k, b in enumerate(bars)}
                if t["entry_time"] != "09:40" or idx.get("09:40", 0) < 1:
                    flag(comp, t, "entry not the 09:40 bar / index < 1")
            if t["dir"] != "LONG":
                flag(comp, t, "dir != LONG")
            if LABELS.get(day) not in ("DOWN", "FLAT"):
                flag(comp, t, f"regime label {LABELS.get(day)} not in "
                              f"DOWN+FLAT")

total_rows = sum(len(books[yr]) for yr in (2025, 2026))
n_viol = sum(len(v) for v in viol.values())
viol_net = round(sum(x["net"] for v in viol.values() for x in v), 2)
print(f"\nAUDIT: {total_rows} rows checked; violations: {n_viol} "
      f"(net of violating rows: {viol_net})")
for comp in sorted(viol):
    print(f"  {comp}: {len(viol[comp])} violations")
    for x in viol[comp][:12]:
        print(f"    {x['date']} {x['stock']} {x['dir']} "
              f"{x['entry_time']} net {x['net']}: {x['why']}")

detail = {"rows_checked": total_rows, "violations": n_viol,
          "violating_net": viol_net,
          "by_comp": {c: v for c, v in viol.items()}}
json.dump(detail, open(f"{WS}/r6_causality_audit.json", "w"), indent=1)
print("detail -> r6_causality_audit.json")
