#!/usr/bin/env python3
"""BREAKER GAP — the ROLL10 rolling-drawdown leg: overlay test.

FREEZE: scenario_proofing_2026-11-14.md, "BREAKER GAP — ROLL10
LEG: FREEZE" (written BEFORE this test ran). The leg: trailing
10-trading-day realised sum <= -Rs5,000 at a non-paused close ->
pause the next 3 trading days; evaluation order MTD -> ROLL10 ->
STREAK; pauses never stack/extend; streak resets on a ROLL10
trip; window spans months; armed from the 10th evaluated day.
Adoption criteria (ALL, BOTH books): (a) worst rolling-10 window
on the combined realised series >= -5,500 (Bank) / >= -7,000
(Nifty); (b) cost vs standing total <= 10%; (c) combined trips
<= 6 per book. One shot — no retuning here.

Local stored legs only; no API calls. Controls first: the
default (leg-off) simulate MUST reproduce Item 3 exactly, or
this run stops.
Writes scenario_breaker_gap_results.json and merges the verdict
into scenario_proofing_results.json (key breaker_gap_roll10_leg).
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import circuit_breaker as CB

OUT = {"freeze": dict(leg="ROLL10", floor=CB.ROLL10_FLOOR,
                      window=CB.ROLL10_WINDOW,
                      pause_days=CB.ROLL10_PAUSE_DAYS,
                      order="MTD -> ROLL10 -> STREAK",
                      criteria=dict(
                          a_bank_worst_window_min=-5500.0,
                          a_nifty_worst_window_min=-7000.0,
                          b_max_cost_frac=0.10,
                          c_max_trips=6))}


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


# ---------------- inputs (identical to scenario34) ----------------
bank_cal = cal_from_csv("oi_history/banknifty_daily_oi.csv")
nifty_cal = []
with open(TR / "volrix/nifty_daily_2019_2026.csv") as f:
    for r in csv.DictReader(f):
        d = r["date"]
        if "2026-01-01" <= d <= "2026-10-31":
            nifty_cal.append(d)
assert len(bank_cal) == 205 and len(nifty_cal) == 205

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

nov_cal = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
           "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
           "2026-11-13"]
nov_hyp = {}
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_hyp[r["date"]] = nov_hyp.get(r["date"], 0.0) \
                + float(r["net_inr"])

# ---------------- controls: leg OFF must reproduce Item 3 --------
ctl = {}
rec2_b, sum2_b = CB.simulate(bank_cal, stack_hyp)
assert sum2_b["total_realised"] == 127475.50, sum2_b
assert sum2_b["trips"] == [dict(date="2026-07-06", kind="STREAK",
                                mtd=-1937.0)], sum2_b["trips"]
assert sum2_b["paused_days"] == 3
assert sum2_b["suppressed_hypothetical"] == -124.0
assert all(r["trip"] != "ROLL10" for r in rec2_b)
ctl["bank_two_leg"] = sum2_b

rec2_n, sum2_n = CB.simulate(nifty_cal, tv1_hyp)
assert sum2_n["total_realised"] == 76432.75, sum2_n
assert sum2_n["trips"] == [dict(date="2026-02-06", kind="MTD",
                                mtd=-6940.0),
                           dict(date="2026-05-11", kind="MTD",
                                mtd=-6084.25)], sum2_n["trips"]
assert sum2_n["paused_days"] == 28
assert sum2_n["suppressed_hypothetical"] == 26617.50
ctl["nifty_two_leg"] = sum2_n

_, nov2 = CB.simulate(nov_cal, nov_hyp)
assert nov2["trips"] == [] and nov2["total_realised"] == -2680.0
ctl["stack_november_two_leg"] = nov2

legacy_hyp = {}
with open(TR / "november_paper_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr") and r.get("channel") == "PRIMARY":
            legacy_hyp[r["date"]] = legacy_hyp.get(r["date"], 0.0) \
                + float(r["net_inr"])
_, leg2 = CB.simulate(nov_cal, legacy_hyp)
assert leg2["trips"] and leg2["trips"][0]["date"] == "2026-11-04" \
    and leg2["trips"][0]["kind"] == "MTD"
ctl["legacy_november_control"] = leg2
OUT["controls_item3_reproduced"] = ctl
print("CONTROLS OK — leg-off simulate reproduces Item 3 exactly")

# ---------------- window machinery (Item 4, same semantics) ------
def window_stats(cal, nets_by_day, regime):
    series = [round(nets_by_day.get(d, 0.0), 2) for d in cal]
    W = 10
    rows = []
    for i in range(len(cal) - W + 1):
        vals = series[i:i + W]
        cum, peak, dd = 0.0, 0.0, 0.0
        for v in vals:
            cum += v
            peak = max(peak, cum)
            dd = min(dd, cum - peak)
        rows.append(dict(start=cal[i], end=cal[i + W - 1],
                         net=round(sum(vals), 2),
                         max_drawdown=round(dd, 2),
                         worst_day=round(min(vals), 2),
                         regime_days=sum(1 for d in cal[i:i + W]
                                         if regime.get(d, False))))
    worst = min(rows, key=lambda r: r["net"])
    conc = [r for r in rows if r["regime_days"] >= 5]
    worst_conc = min(conc, key=lambda r: r["net"]) if conc else None
    return dict(windows=len(rows), worst_window=worst,
                worst_regime_concentrated=worst_conc)


def brute_worst_window(cal, nets_by_day):
    """Independent second implementation (no shared helper):
    plain nested-loop slice sums over the calendar."""
    worst = None
    for i in range(len(cal) - 9):
        s = 0.0
        for d in cal[i:i + 10]:
            s += round(nets_by_day.get(d, 0.0), 2)
        s = round(s, 2)
        if worst is None or s < worst[0]:
            worst = (s, cal[i], cal[i + 9])
    return worst


def realised_series(records):
    return {r["date"]: r["realised_net"] for r in records}


def enrich_trips(records, summ):
    out = []
    for t in summ["trips"]:
        i = next(i for i, r in enumerate(records)
                 if r["date"] == t["date"] and r["trip"] == t["kind"])
        mine = []
        for r in records[i + 1:]:
            if r["paused"]:
                mine.append(r)
            else:
                break
        out.append(dict(
            trip_date=t["date"], kind=t["kind"], mtd_at_trip=t["mtd"],
            roll10_at_trip=t.get("roll10"),
            paused_days=[r["date"] for r in mine],
            suppressed_hypothetical=round(
                sum(r["hypothetical_net"] for r in mine), 2),
            suppressed_detail=[(r["date"], r["hypothetical_net"])
                               for r in mine
                               if r["hypothetical_net"] != 0]))
    return out


# ---------------- three-leg replays ------------------------------
BOOKS = [
    dict(key="bank", label="BANK TUNED STACK v2", cal=bank_cal,
         hyp=stack_hyp, regime=bank_regime, standing=127351.50,
         rec2=rec2_b, sum2=sum2_b, a_min=-5500.0),
    dict(key="nifty", label="NIFTY TUNED v1", cal=nifty_cal,
         hyp=tv1_hyp, regime=nifty_regime, standing=103050.25,
         rec2=rec2_n, sum2=sum2_n, a_min=-7000.0),
]

verdicts = {}
for B in BOOKS:
    rec3, sum3 = CB.simulate(B["cal"], B["hyp"],
                             roll10_floor=CB.ROLL10_FLOOR)
    rs3 = realised_series(rec3)
    rs2 = realised_series(B["rec2"])
    w0 = window_stats(B["cal"], B["hyp"], B["regime"])
    w2 = window_stats(B["cal"], rs2, B["regime"])
    w3 = window_stats(B["cal"], rs3, B["regime"])
    # independent re-sums
    tot3_check = round(sum(rs3.get(d, 0.0) for d in B["cal"]), 2)
    assert tot3_check == sum3["total_realised"], (tot3_check, sum3)
    bw = brute_worst_window(B["cal"], rs3)
    assert bw[0] == w3["worst_window"]["net"], (bw, w3["worst_window"])
    assert bw[1] == w3["worst_window"]["start"]
    cost = round(B["standing"] - sum3["total_realised"], 2)
    cost_cap = round(B["standing"] * 0.10, 2)
    kinds = defaultdict(int)
    for t in sum3["trips"]:
        kinds[t["kind"]] += 1
    crit = dict(
        a_worst_window_net=w3["worst_window"]["net"],
        a_required_min=B["a_min"],
        a_pass=w3["worst_window"]["net"] >= B["a_min"],
        b_cost=cost, b_cost_cap=cost_cap,
        b_cost_frac=round(cost / B["standing"], 4),
        b_pass=cost <= cost_cap,
        c_trips_total=len(sum3["trips"]),
        c_pass=len(sum3["trips"]) <= 6)
    crit["all_pass"] = crit["a_pass"] and crit["b_pass"] \
        and crit["c_pass"]
    verdicts[B["key"]] = crit["all_pass"]
    OUT[B["key"]] = dict(
        book=B["label"], standing_total=B["standing"],
        two_leg=dict(summary=B["sum2"],
                     worst_window=w2["worst_window"]),
        three_leg=dict(
            summary=sum3, trips_enriched=enrich_trips(rec3, sum3),
            trips_by_kind=dict(kinds),
            paused_days=sum3["paused_days"],
            total_realised=sum3["total_realised"],
            worst_window=w3["worst_window"],
            worst_regime_concentrated=w3["worst_regime_concentrated"],
            independent_resum=dict(total=tot3_check,
                                   worst_window_bruteforce=dict(
                                       net=bw[0], start=bw[1],
                                       end=bw[2]))),
        no_breaker_worst_window=w0["worst_window"],
        criteria=crit)
    print(f"{B['label']}: 3-leg realised "
          f"{sum3['total_realised']:+.2f} (standing "
          f"{B['standing']:+.2f}, 2-leg {B['sum2']['total_realised']:+.2f})"
          f" · trips {len(sum3['trips'])} {dict(kinds)}"
          f" · paused {sum3['paused_days']}d"
          f" · worst window {w3['worst_window']['net']:+.2f}"
          f" ({w3['worst_window']['start']}->{w3['worst_window']['end']})"
          f" · criteria a/b/c = {crit['a_pass']}/{crit['b_pass']}/"
          f"{crit['c_pass']}")

# ---------------- November under the combined brake --------------
_, nov3 = CB.simulate(nov_cal, nov_hyp, roll10_floor=CB.ROLL10_FLOOR)
assert round(sum(nov_hyp.get(d, 0.0) for d in nov_cal), 2) == -2680.0
OUT["november_stack_standalone_three_leg"] = nov3

cont_cal = bank_cal + nov_cal
cont_hyp = dict(stack_hyp)
cont_hyp.update(nov_hyp)
recC, sumC = CB.simulate(cont_cal, cont_hyp,
                         roll10_floor=CB.ROLL10_FLOOR)
nov_trips_C = [t for t in sumC["trips"] if t["date"] >= "2026-11-01"]
nov_rec_C = [r for r in recC if r["date"] >= "2026-11-01"]
OUT["november_stack_continuous_three_leg"] = dict(
    trips_in_november=nov_trips_C,
    november_realised=round(sum(r["realised_net"] for r in nov_rec_C), 2),
    november_paused_days=sum(1 for r in nov_rec_C if r["paused"]),
    full_series_trips=len(sumC["trips"]))
print(f"November standalone (3 legs): trips={nov3['trips']} "
      f"realised={nov3['total_realised']:+.2f}")
print(f"November continuous (3 legs): trips in Nov={nov_trips_C} "
      f"realised={OUT['november_stack_continuous_three_leg']['november_realised']:+.2f}")

OUT["verdict"] = "ADOPTED" if all(verdicts.values()) else "REJECTED"
OUT["verdict_per_book"] = verdicts
print("VERDICT:", OUT["verdict"])

(TR / "scenario_breaker_gap_results.json").write_text(
    json.dumps(OUT, indent=1))

sp = json.loads((TR / "scenario_proofing_results.json").read_text())
sp["breaker_gap_roll10_leg"] = dict(
    freeze=OUT["freeze"], verdict=OUT["verdict"],
    verdict_per_book=verdicts,
    bank=OUT["bank"], nifty=OUT["nifty"],
    november_stack_standalone_three_leg=
        OUT["november_stack_standalone_three_leg"],
    november_stack_continuous_three_leg=
        OUT["november_stack_continuous_three_leg"],
    controls="leg-off simulate reproduces Item 3 exactly "
             "(asserted in-script before any three-leg run)")
(TR / "scenario_proofing_results.json").write_text(
    json.dumps(sp, indent=1))
print("SCENARIO BREAKER GAP DONE")
