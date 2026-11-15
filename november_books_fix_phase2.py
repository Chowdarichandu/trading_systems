#!/usr/bin/env python3
"""NOVEMBER BOOKS FIX — PHASE 2: REPAIR GATES (2026-11-14).

FREEZE (written in november_books_fix_2026-11-14.md BEFORE this ran):
  BANK  B-FIX-1 on TUNED STACK v2: stand down a leg iff side=PE and
        day gap% < 0 and entry premium in [500, 800].
        Target cell Jan-Oct: 17 legs, -Rs4,158.50.
  NIFTY N-FIX-1 on TUNED v1: stand down a leg iff side=CE and
        day gap% > 0. Target cell Jan-Oct: 8 legs, -Rs14,119.75.
GATE (both, frozen): (i) repaired total >= 90% of standing total;
  (ii) target cell post-repair contribution = Rs0 (loss cut 100%);
  (iii) placebo: 200 seeded (1000-1199) random stand-downs of the
        same leg-count from the same book — repaired total must
        exceed the 95th percentile (linear interpolation);
  (iv) repaired H1 (Jan-May) > 0 and H2 (Jun-Oct) > 0;
  (v) November counterfactual, day by day (reported, not pass/fail).
Basis: premiums per 1 lot (Bank 30 / Nifty 65), Rs220/trade inside
stored nets, buying only, paper, real money Rs0. November sets no
rule — Jan-Oct legs only are gated.
"""
import csv, json, random, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import november_books_fix_phase1 as P1  # reuses asserted leg assembly

TR = Path.home() / "workspace/trading"
legs = P1.all_legs

def gap_of(book_row):
    g = book_row["gap_pct"]
    return float(g) if g not in (None, "") else None

def percentile95(vals):
    s = sorted(vals)
    n = len(s)
    pos = 0.95 * (n - 1)
    lo = int(pos); frac = pos - lo
    return s[lo] + frac * (s[min(lo + 1, n - 1)] - s[lo])

def gate(book_name, standing_total, is_cell, nov_legs, nov_gap, label):
    book = [l for l in legs if l["book"] == book_name]
    assert round(sum(l["net"] for l in book), 2) == standing_total
    cell = [l for l in book if is_cell(l)]
    kept = [l for l in book if not is_cell(l)]
    rep_total = round(sum(l["net"] for l in kept), 2)
    cell_net = round(sum(l["net"] for l in cell), 2)
    k = len(cell)
    # halves of repaired book
    h1 = round(sum(l["net"] for l in kept if l["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(l["net"] for l in kept if l["date"][:7] >= "2026-06"), 2)
    # placebo: 200 seeded random stand-downs of k legs
    nets = [l["net"] for l in book]
    totals = []
    for seed in range(1000, 1200):
        rng = random.Random(seed)
        idx = rng.sample(range(len(nets)), k)
        totals.append(round(standing_total - sum(nets[i] for i in idx), 2))
    p95 = percentile95(totals)
    beats = sum(1 for t in totals if rep_total > t)
    g = dict(label=label, book=book_name, standing_total=standing_total,
             cell_legs=k, cell_net=cell_net,
             cell_detail=[dict(date=l["date"], side=l["side"],
                               family=l["family"], rep=l["rep"],
                               entry_time=l["entry_time"],
                               entry_premium=l["entry_premium"],
                               gap_pct=l["gap_pct"], net=l["net"])
                          for l in cell],
             repaired_total=rep_total,
             leg_i_pass=rep_total >= round(0.9 * standing_total, 2),
             leg_i_floor=round(0.9 * standing_total, 2),
             leg_ii_cell_after=0.0, leg_ii_pass=True,
             placebo_p95=round(p95, 2), placebo_beaten=beats,
             leg_iii_pass=rep_total > p95,
             halves=dict(H1=h1, H2=h2), leg_iv_pass=(h1 > 0 and h2 > 0))
    g["verdict"] = ("PASS" if (g["leg_i_pass"] and g["leg_ii_pass"]
                              and g["leg_iii_pass"] and g["leg_iv_pass"])
                   else "FAIL")
    # November counterfactual
    nov_days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
                "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
                "2026-11-13"]
    actual_day = defaultdict(float)
    rep_day = defaultdict(float)
    stood = []
    for l in nov_legs:
        actual_day[l["date"]] += l["net"]
        if nov_gap(l) is not None and is_cell(l, nov=True):
            stood.append(l)
        else:
            rep_day[l["date"]] += l["net"]
    def counts(dm):
        gg = sum(1 for d in nov_days if dm.get(d, 0.0) > 0)
        rr = sum(1 for d in nov_days if dm.get(d, 0.0) < 0)
        return gg, rr, 9 - gg - rr
    g["november"] = dict(
        actual_total=round(sum(actual_day.values()), 2),
        actual_counts=counts(actual_day),
        repaired_total=round(sum(rep_day.values()), 2),
        repaired_counts=counts(rep_day),
        stood_down=[dict(date=l["date"], side=l["side"], net=l["net"],
                         entry_premium=l.get("entry_premium"),
                         gap_pct=l.get("gap_pct")) for l in stood],
        days={d: dict(actual=actual_day.get(d, 0.0),
                      repaired=rep_day.get(d, 0.0)) for d in nov_days})
    print(f"\n===== {label} on {book_name}")
    print(f"  standing total {standing_total:+,.2f} ({len(book)} legs)")
    print(f"  target cell: {k} legs, {cell_net:+,.2f}")
    for c in g["cell_detail"]:
        print(f"    {c['date']} {c['side']} {c['family']}/{c['rep']} "
              f"entry {c['entry_time']} prem {c['entry_premium']} "
              f"gap {c['gap_pct']:+.3f}% net {c['net']:+,.2f}")
    print(f"  repaired total {rep_total:+,.2f}")
    print(f"  (i) >= {g['leg_i_floor']:,.2f}: {'PASS' if g['leg_i_pass'] else 'FAIL'}")
    print(f"  (ii) cell after repair Rs0 (loss cut 100%): PASS (by construction of the stand-down)")
    print(f"  (iii) placebo p95 {p95:+,.2f}; repaired beats {beats}/200 draws: "
          f"{'PASS' if g['leg_iii_pass'] else 'FAIL'}")
    print(f"  (iv) halves H1 {h1:+,.2f} / H2 {h2:+,.2f}: "
          f"{'PASS' if g['leg_iv_pass'] else 'FAIL'}")
    print(f"  VERDICT: {g['verdict']}")
    print(f"  (v) November: actual {g['november']['actual_total']:+,.2f} "
          f"{g['november']['actual_counts']} -> repaired "
          f"{g['november']['repaired_total']:+,.2f} "
          f"{g['november']['repaired_counts']}; stood down: "
          f"{g['november']['stood_down']}")
    return g

# ---------------- BANK B-FIX-1 ----------------------------------------------
def bank_cell(l, nov=False):
    g = float(l["gap_pct"]) if l["gap_pct"] not in (None, "") else None
    if g is None: return False
    return (l["side"] == "PE" and g < 0
            and 500.0 <= float(l["entry_premium"]) <= 800.0)

bank_nov = []
for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv")):
    if r["net_inr"]:
        bank_nov.append(dict(date=r["date"], side=r["direction"],
                             entry_premium=float(r["entry_premium"]),
                             net=float(r["net_inr"])))
bank_gap = {r["date"]: float(r["gap_pct"]) for r in
            csv.DictReader(open(TR / "november_regime_days_bank.csv"))
            if r["date"] >= "2026-11-01" and r["gap_pct"]}
for l in bank_nov: l["gap_pct"] = bank_gap[l["date"]]

gb = gate("BANK_STACK", 127351.50, bank_cell, bank_nov,
          lambda l: l["gap_pct"], "B-FIX-1")

# ---------------- NIFTY N-FIX-1 ----------------------------------------------
def nifty_cell(l, nov=False):
    g = float(l["gap_pct"]) if l["gap_pct"] not in (None, "") else None
    if g is None: return False
    return l["side"] == "CE" and g > 0

# TUNED v1 November legs: DEC-S1 shadow log minus component-B PE rows
nov_gap_nifty = {"2026-11-03": 0.6034}  # computed from stored spot bars
nifty_nov = []
for r in csv.DictReader(open(TR / "november_shadow_decs1_nifty_log.csv")):
    if not r["net_inr"]: continue
    comp = r["system_source"].replace("DEC-S1 ", "").strip()
    if comp == "B" and r["direction"] == "PE": continue  # not a v1 leg
    nifty_nov.append(dict(date=r["date"], side=r["direction"],
                          entry_premium=float(r["entry_premium"]),
                          net=float(r["net_inr"]),
                          gap_pct=nov_gap_nifty.get(r["date"])))
assert len(nifty_nov) == 1 and nifty_nov[0]["net"] == 3036.50

gn = gate("NIFTY_TUNED_V1", 103050.25, nifty_cell, nifty_nov,
          lambda l: l["gap_pct"], "N-FIX-1")

out = {"bank": gb, "nifty": gn}
json.dump(out, open(TR / "november_books_fix_phase2_partial.json", "w"),
          indent=1, default=str)
print("\nPHASE 2 DONE")
