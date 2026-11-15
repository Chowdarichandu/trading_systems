#!/usr/bin/env python3
"""SCENARIO-PROOFING ITEMS 3 + 4 — circuit-breaker replays and the
worst-window stress test. Local stored legs only; no API calls.

ITEM 3: replay circuit_breaker.simulate (the shared implementation)
  - over TUNED STACK v2's frozen Jan-Oct legs (day nets over the
    205-day calendar; no-leg days = 0) — when would it have tripped,
    what would it have saved / cost;
  - over November's actual stack sequence (cross-check of
    circuit_breaker_stack.py: must show 0 trips, MTD -2,680);
  - control: the same rule over the legacy BNF-PAPER-V1 November
    sequence must reproduce the known 2026-11-05 firing (streak of
    Nov 2/3/4 + MTD -5,160) — the semantics check.

ITEM 4: worst rolling 10-trading-day windows, per book, on day nets
(1 lot, costs inside the stored nets):
  - Bank TUNED STACK v2 and Nifty TUNED v1, Jan-Oct;
  - overall worst window and worst regime-concentrated window
    (>= 5 regime-like days per the frozen Phase C classification);
  - per window: net, max drawdown of the within-window cumulative
    curve, worst day;
  - then the same windows machinery on the breaker-applied series
    (legs on paused days suppressed by the Item 3 simulation) —
    the bounded outcome for the December Rs1,00,000 decision.
Writes scenario34_results.json.
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import circuit_breaker as CB

OUT = {}


def cal_from_csv(fn, datecol="date"):
    with open(TR / fn) as f:
        return [r[datecol] for r in csv.DictReader(f)
                if "2026-01-01" <= r[datecol] <= "2026-10-31"]


def regime_flags(fn):
    out = {}
    with open(TR / fn) as f:
        for r in csv.DictReader(f):
            out[r["date"]] = (r["regime_like"] == "True")
    return out


def day_nets(legs):
    d = defaultdict(float)
    for day, net in legs:
        d[day] += net
    return {k: round(v, 2) for k, v in d.items()}


# ---------------- inputs ----------------
bank_cal = cal_from_csv("oi_history/banknifty_daily_oi.csv")
nifty_cal = []
with open(TR / "volrix/nifty_daily_2019_2026.csv") as f:
    for r in csv.DictReader(f):
        d = r["date"]
        if "2026-01-01" <= d <= "2026-10-31":
            nifty_cal.append(d)
assert len(bank_cal) == 205, len(bank_cal)
assert len(nifty_cal) == 205, len(nifty_cal)

stack_legs = []
with open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv") as f:
    for r in csv.DictReader(f):
        stack_legs.append((r["date"], float(r["x1_net"])))
assert round(sum(n for _, n in stack_legs), 2) == 127351.50
stack_hyp = day_nets(stack_legs)

tv1 = json.loads((TR / "nifty_900_tradeday_2026-11-13_results.json")
                 .read_text())["books"]["TUNED_v1"]["legs_detail"]
tv1_legs = [(l["date"], float(l["net"])) for l in tv1]
assert round(sum(n for _, n in tv1_legs), 2) == 103050.25
tv1_hyp = day_nets(tv1_legs)

bank_regime = regime_flags("november_regime_days_bank.csv")
nifty_regime = regime_flags("november_regime_days_nifty.csv")

# ---------------- ITEM 3 replays ----------------
rec, summ = CB.simulate(bank_cal, stack_hyp)
OUT["item3_stack_janoct"] = dict(
    summary=summ,
    trip_detail=[dict(trip=t,
                      suppressed_next=[r for r in rec
                                       if r["paused"] and
                                       r["hypothetical_net"] != 0][:0])
                 for t in summ["trips"]],
    trips_enriched=[])
# enrich trips: the paused days that follow each trip and what was
# suppressed in them
for t in summ["trips"]:
    i = next(i for i, r in enumerate(rec) if r["date"] == t["date"]
             and r["trip"] == t["kind"])
    paused = [r for r in rec[i + 1:] if r["paused"]]
    # paused days belong to this trip until a non-paused day appears
    mine = []
    for r in rec[i + 1:]:
        if r["paused"]:
            mine.append(r)
        else:
            break
    OUT["item3_stack_janoct"]["trips_enriched"].append(dict(
        trip_date=t["date"], kind=t["kind"], mtd_at_trip=t["mtd"],
        paused_days=[r["date"] for r in mine],
        suppressed_hypothetical=round(
            sum(r["hypothetical_net"] for r in mine), 2),
        suppressed_legs_detail=[(r["date"], r["hypothetical_net"])
                                for r in mine
                                if r["hypothetical_net"] != 0]))

# November actual (stack) — cross-check vs circuit_breaker_stack.py
nov_cal = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
           "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
           "2026-11-13"]
nov_hyp = {}
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_hyp[r["date"]] = nov_hyp.get(r["date"], 0.0) \
                + float(r["net_inr"])
_, nov_summ = CB.simulate(nov_cal, nov_hyp)
OUT["item3_stack_november"] = nov_summ
assert nov_summ["trips"] == [] and nov_summ["total_realised"] == -2680.0

# Legacy November — semantics control (must fire after Nov 4)
legacy_hyp = {}
with open(TR / "november_paper_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr") and r.get("channel") == "PRIMARY":
            legacy_hyp[r["date"]] = legacy_hyp.get(r["date"], 0.0) \
                + float(r["net_inr"])
lrec, lsumm = CB.simulate(nov_cal, legacy_hyp)
OUT["item3_legacy_november_control"] = dict(
    day_nets={d: legacy_hyp.get(d, 0.0) for d in nov_cal},
    summary=lsumm)

# Nifty TUNED v1 Jan-Oct breaker simulation (feeds Item 4)
nrec, nsumm = CB.simulate(nifty_cal, tv1_hyp)
OUT["item3_nifty_tunedv1_janoct"] = nsumm

# ---------------- ITEM 4 windows ----------------
def window_stats(cal, nets_by_day, regime, label):
    series = [round(nets_by_day.get(d, 0.0), 2) for d in cal]
    W = 10
    rows = []
    for i in range(len(cal) - W + 1):
        win_days = cal[i:i + W]
        vals = series[i:i + W]
        cum, peak, dd = 0.0, 0.0, 0.0
        for v in vals:
            cum += v
            peak = max(peak, cum)
            dd = min(dd, cum - peak)
        rows.append(dict(start=win_days[0], end=win_days[-1],
                         net=round(sum(vals), 2),
                         max_drawdown=round(dd, 2),
                         worst_day=round(min(vals), 2),
                         regime_days=sum(1 for d in win_days
                                         if regime.get(d, False))))
    worst = min(rows, key=lambda r: r["net"])
    conc = [r for r in rows if r["regime_days"] >= 5]
    worst_conc = min(conc, key=lambda r: r["net"]) if conc else None
    worst_dd = min(rows, key=lambda r: r["max_drawdown"])
    return dict(book=label, windows=len(rows),
                worst_window=worst,
                worst_regime_concentrated=worst_conc,
                worst_drawdown_window=worst_dd,
                regime_concentrated_windows=len(conc))


def realised_series(records):
    return {r["date"]: r["realised_net"] for r in records}


OUT["item4"] = {
    "bank_no_breaker": window_stats(bank_cal, stack_hyp, bank_regime,
                                    "BANK TUNED STACK v2"),
    "bank_with_breaker": window_stats(bank_cal, realised_series(rec),
                                      bank_regime,
                                      "BANK TUNED STACK v2 + breaker"),
    "nifty_no_breaker": window_stats(nifty_cal, tv1_hyp, nifty_regime,
                                     "NIFTY TUNED v1"),
    "nifty_with_breaker": window_stats(nifty_cal, realised_series(nrec),
                                       nifty_regime,
                                       "NIFTY TUNED v1 + breaker"),
}
# original worst windows re-evaluated under the breaker series
for book, cal, hyp, rseries, regime in (
        ("bank", bank_cal, stack_hyp, realised_series(rec), bank_regime),
        ("nifty", nifty_cal, tv1_hyp, realised_series(nrec), nifty_regime)):
    key = f"{book}_no_breaker"
    w = OUT["item4"][key]["worst_window"]
    i = cal.index(w["start"])
    vals = [round(rseries.get(d, 0.0), 2) for d in cal[i:i + 10]]
    cum, peak, dd = 0.0, 0.0, 0.0
    for v in vals:
        cum += v
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    OUT["item4"][f"{book}_orig_worst_under_breaker"] = dict(
        start=w["start"], end=w["end"], net=round(sum(vals), 2),
        max_drawdown=round(dd, 2), worst_day=round(min(vals), 2))

(TR / "scenario34_results.json").write_text(json.dumps(OUT, indent=1))
print(json.dumps(OUT, indent=1))
print("SCENARIO34 DONE")
