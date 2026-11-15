#!/usr/bin/env python3
"""BREAKER GAP — the HWM-DD peak-anchored leg: overlay test.

FREEZE: scenario_proofing_2026-11-14.md, "BREAKER GAP — HWM-DD
LEG: FREEZE" (written BEFORE this test ran). The leg: within a
calendar month, HWM = highest realised MTD at any prior close
(floored at the month-start 0 baseline); at a non-paused close,
HWM - MTD >= Rs5,000 trips -> pause the rest of the month (the
MTD leg's pause shape and streak treatment). Evaluation order
MTD -> HWM-DD -> STREAK. Adoption criteria (ALL, BOTH books):
(a) worst rolling-10 window on the three-leg realised series
>= -5,500 (Bank) / >= -7,000 (Nifty); (b) MARGINAL cost
(two-leg - three-leg) <= 10% of the standing total (governs;
combined cost reported alongside); (c) HWM-DD trips <= 4 per
book. One shot — no retuning here; if it fails, brake work
stops and the Item 4 burn bounds stand.

Local stored legs only; no API calls. Controls first: leg OFF
must reproduce Item 3 exactly, ROLL10-on/HWM-DD-off must
reproduce the rejected ROLL10 run exactly, and two synthetic
series must prove the leg's semantics (bleed-from-peak trips;
never-positive month reduces to the MTD leg) — or this run
stops.
Writes scenario_breaker_hwm_results.json and merges the verdict
into scenario_proofing_results.json (key breaker_gap_hwmdd_leg).
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import circuit_breaker as CB

OUT = {"freeze": dict(leg="HWM-DD", drop=CB.HWMDD_DROP,
                      baseline="HWM floored at month-start 0",
                      action="pause rest of calendar month",
                      order="MTD -> HWM-DD -> STREAK",
                      criteria=dict(
                          a_bank_worst_window_min=-5500.0,
                          a_nifty_worst_window_min=-7000.0,
                          b_governing="marginal (two-leg minus "
                                      "three-leg)",
                          b_max_cost_frac_of_standing=0.10,
                          c_max_hwmdd_trips=4))}


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


# ---------------- inputs (identical to scenario34 / gap) --------
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

# ---------------- control 1: leg OFF reproduces Item 3 ---------
ctl = {}
rec2_b, sum2_b = CB.simulate(bank_cal, stack_hyp)
assert sum2_b["total_realised"] == 127475.50, sum2_b
assert sum2_b["trips"] == [dict(date="2026-07-06", kind="STREAK",
                                mtd=-1937.0)], sum2_b["trips"]
assert sum2_b["paused_days"] == 3
assert sum2_b["suppressed_hypothetical"] == -124.0
assert all(r["trip"] != "HWMDD" for r in rec2_b)
assert not sum2_b["hwmdd_enabled"]
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
print("CONTROL 1 OK — leg-off simulate reproduces Item 3 exactly")

# ------------- control 2: ROLL10 on, HWM-DD off reproduces
# ------------- the rejected ROLL10 run exactly ------------------
_, gap_b = CB.simulate(bank_cal, stack_hyp,
                       roll10_floor=CB.ROLL10_FLOOR)
assert gap_b["total_realised"] == 124995.50, gap_b
assert [(t["date"], t["kind"]) for t in gap_b["trips"]] == [
    ("2026-06-22", "ROLL10"), ("2026-07-06", "STREAK")], gap_b["trips"]
_, gap_n = CB.simulate(nifty_cal, tv1_hyp,
                       roll10_floor=CB.ROLL10_FLOOR)
assert gap_n["total_realised"] == 59693.25, gap_n
assert [(t["date"], t["kind"]) for t in gap_n["trips"]] == [
    ("2026-02-06", "MTD"), ("2026-03-27", "ROLL10"),
    ("2026-04-06", "ROLL10"), ("2026-05-11", "MTD")], gap_n["trips"]
ctl["roll10_run_reproduced"] = dict(bank=gap_b, nifty=gap_n)
print("CONTROL 2 OK — ROLL10-on/HWM-DD-off reproduces the "
      "rejected ROLL10 run exactly")

# ------------- control 3: synthetic semantics of the leg --------
# (i) bleed from a peak: MTD never <= -5,000, no 3-day losing
# streak (losses interleaved), so the two-leg brake never trips;
# HWM-DD must trip when the peak-to-current drop reaches 5,000.
syn_days = [f"2026-01-{d:02d}" for d in range(1, 9)]
syn_hyp = dict(zip(syn_days, [8000.0, -1500.0, 100.0, -1500.0,
                              100.0, -1500.0, -1400.0, 500.0]))
_, syn2 = CB.simulate(syn_days, syn_hyp)
assert syn2["trips"] == [], syn2["trips"]
syn_rec3, syn3 = CB.simulate(syn_days, syn_hyp,
                             hwmdd_drop=CB.HWMDD_DROP)
assert len(syn3["trips"]) == 1, syn3["trips"]
_t = syn3["trips"][0]
assert _t["kind"] == "HWMDD" and _t["date"] == "2026-01-07" \
    and _t["hwm"] == 8000.0 and _t["mtd"] == 2300.0 \
    and _t["drop"] == 5700.0, _t
assert syn_rec3[-1]["paused"] and \
    syn_rec3[-1]["pause_kind"] == "HWMDD" \
    and syn_rec3[-1]["realised_net"] == 0.0
# (ii) a month that never rises above 0: HWM stays 0, so the leg
# reduces to the MTD leg — identical realised series and trips,
# and the trip that fires carries the MTD label (checked first).
neg_days = [f"2026-02-{d:02d}" for d in range(1, 6)]
neg_hyp = dict(zip(neg_days, [-2000.0, -2000.0, -2000.0,
                              900.0, 900.0]))
neg_r2, neg_s2 = CB.simulate(neg_days, neg_hyp)
neg_r3, neg_s3 = CB.simulate(neg_days, neg_hyp,
                             hwmdd_drop=CB.HWMDD_DROP)
assert [r["realised_net"] for r in neg_r2] == \
    [r["realised_net"] for r in neg_r3]
assert neg_s3["trips"] == neg_s2["trips"] and \
    len(neg_s3["trips"]) == 1 and \
    neg_s3["trips"][0]["kind"] == "MTD", neg_s3["trips"]
assert all(r.get("hwm", 0.0) == 0.0 for r in neg_r3)
ctl["synthetic_semantics"] = dict(
    bleed_from_peak_two_leg_trips=syn2["trips"],
    bleed_from_peak_hwmdd_trip=_t,
    never_positive_month="HWM-DD run identical to two-leg run; "
                         "single trip labelled MTD")
OUT["controls"] = ctl
print("CONTROL 3 OK — synthetic semantics: bleed-from-peak "
      "trips HWM-DD only; never-positive month reduces to MTD")

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
            hwm_at_trip=t.get("hwm"),
            drop_at_trip=t.get("drop"),
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
                             hwmdd_drop=CB.HWMDD_DROP)
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
    combined_cost = round(B["standing"] - sum3["total_realised"], 2)
    marginal_cost = round(B["sum2"]["total_realised"]
                          - sum3["total_realised"], 2)
    cost_cap = round(B["standing"] * 0.10, 2)
    kinds = defaultdict(int)
    for t in sum3["trips"]:
        kinds[t["kind"]] += 1
    hwm_trips = [t for t in sum3["trips"] if t["kind"] == "HWMDD"]
    crit = dict(
        a_worst_window_net=w3["worst_window"]["net"],
        a_required_min=B["a_min"],
        a_pass=w3["worst_window"]["net"] >= B["a_min"],
        b_governing="marginal",
        b_marginal_cost=marginal_cost,
        b_combined_cost=combined_cost,
        b_cost_cap=cost_cap,
        b_marginal_frac_of_standing=round(
            marginal_cost / B["standing"], 4),
        b_combined_frac_of_standing=round(
            combined_cost / B["standing"], 4),
        b_pass=marginal_cost <= cost_cap,
        c_hwmdd_trips=len(hwm_trips),
        c_pass=len(hwm_trips) <= 4)
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
          f" · marginal cost {marginal_cost:+.2f} / combined "
          f"{combined_cost:+.2f}"
          f" · criteria a/b/c = {crit['a_pass']}/{crit['b_pass']}/"
          f"{crit['c_pass']}")

# ---------------- November under the combined brake --------------
recN3, nov3 = CB.simulate(nov_cal, nov_hyp,
                          hwmdd_drop=CB.HWMDD_DROP)
assert round(sum(nov_hyp.get(d, 0.0) for d in nov_cal), 2) == -2680.0
nov_path = [dict(date=r["date"], net=r["hypothetical_net"],
                 mtd=r["mtd_realised"], hwm=r.get("hwm"),
                 hwm_dd=r.get("hwm_dd"), trip=r["trip"],
                 paused=r["paused"]) for r in recN3]
OUT["november_stack_standalone_three_leg"] = dict(
    summary=nov3, day_path=nov_path)

cont_cal = bank_cal + nov_cal
cont_hyp = dict(stack_hyp)
cont_hyp.update(nov_hyp)
recC, sumC = CB.simulate(cont_cal, cont_hyp,
                         hwmdd_drop=CB.HWMDD_DROP)
nov_trips_C = [t for t in sumC["trips"] if t["date"] >= "2026-11-01"]
nov_rec_C = [r for r in recC if r["date"] >= "2026-11-01"]
OUT["november_stack_continuous_three_leg"] = dict(
    trips_in_november=nov_trips_C,
    november_realised=round(sum(r["realised_net"] for r in nov_rec_C), 2),
    november_paused_days=sum(1 for r in nov_rec_C if r["paused"]),
    full_series_trips=len(sumC["trips"]))
print(f"November standalone (3 legs): trips={nov3['trips']} "
      f"paused={nov3['paused_days']} "
      f"realised={nov3['total_realised']:+.2f}")
print(f"November continuous (3 legs): trips in Nov={nov_trips_C} "
      f"paused={OUT['november_stack_continuous_three_leg']['november_paused_days']} "
      f"realised={OUT['november_stack_continuous_three_leg']['november_realised']:+.2f}")

OUT["verdict"] = "ADOPTED" if all(verdicts.values()) else "REJECTED"
OUT["verdict_per_book"] = verdicts
print("VERDICT:", OUT["verdict"])

(TR / "scenario_breaker_hwm_results.json").write_text(
    json.dumps(OUT, indent=1))

sp = json.loads((TR / "scenario_proofing_results.json").read_text())
sp["breaker_gap_hwmdd_leg"] = dict(
    freeze=OUT["freeze"], verdict=OUT["verdict"],
    verdict_per_book=verdicts,
    bank=OUT["bank"], nifty=OUT["nifty"],
    november_stack_standalone_three_leg=
        OUT["november_stack_standalone_three_leg"],
    november_stack_continuous_three_leg=
        OUT["november_stack_continuous_three_leg"],
    controls="leg-off simulate reproduces Item 3 exactly; "
             "ROLL10-on/HWM-DD-off reproduces the rejected ROLL10 "
             "run exactly; synthetic series prove the leg's "
             "semantics (asserted in-script before any scored run)")
(TR / "scenario_proofing_results.json").write_text(
    json.dumps(sp, indent=1))
print("SCENARIO BREAKER HWM-DD DONE")
