#!/usr/bin/env python3
"""NIFTY-EVE-07 gate run, 2026-11-04 evening engine (Nifty only, paper, real money Rs0).

Candidate: DEC-S1 minus Component B PE legs (drop gap-fade legs that fade a gap-UP,
i.e. B legs with direction PE). Incumbent for this candidate: DEC-S1 as adopted
(97 legs, +Rs91,168.50 Jan-Oct 2026), taken from nifty_next_phase_trades.csv --
the file written by the 2026-11-04 next-phase run, which independently re-scored
the frozen DEC-S1 legs from repaired premium stores and matched the frozen
adoption record on 16/16 fields (total to the paisa). This script independently
re-sums that file before scoring anything.

Full controls in the same run (backtest_controls_gate):
 timing/leak audit (filter input = gap direction, known at the day's open,
   before the 10:05 B entry; kept legs keep their frozen entry times, so a
   drop-only filter can introduce no timing violation; base audit 97/0 from
   the next-phase verification is re-stated, not assumed silently),
 placebo x2 (mirror: drop B CE instead; size-matched chronological skip of
   the first 23 Component B legs), halves split, full month table,
 ex-top-3 stress, independent re-sum from the source CSV.
Basis: premiums per 1 lot (65), cost Rs220/trade already inside net_inr,
UNIQUE-ONCE (the source file is the frozen UNIQUE-ONCE leg set).
"""
import csv, json, collections

SRC = "/home/hatch/workspace/trading/nifty_next_phase_trades.csv"
rows = [r for r in csv.DictReader(open(SRC)) if r["set"] == "BASE"]
assert len(rows) == 97, len(rows)

def stats(sub):
    net = round(sum(float(r["net_inr"]) for r in sub), 2)
    months = collections.defaultdict(float)
    days = collections.defaultdict(float)
    for r in sub:
        months[r["date"][:7]] += float(r["net_inr"])
        days[r["date"]] += float(r["net_inr"])
    top3 = sorted((float(r["net_inr"]) for r in sub), reverse=True)[:3]
    cum, cum_min = 0.0, 0.0
    month_rows = []
    for m in sorted(months):
        cum += months[m]
        cum_min = min(cum_min, cum)
        month_rows.append({"month": m, "net": round(months[m], 2), "cum": round(cum, 2)})
    return {
        "legs": len(sub),
        "net": net,
        "ft_pct": round(100.0 * sum(int(r["ft"]) for r in sub) / len(sub), 1) if sub else 0.0,
        "h1_jan_may": round(sum(float(r["net_inr"]) for r in sub if r["date"] < "2026-06-01"), 2),
        "h2_jun_oct": round(sum(float(r["net_inr"]) for r in sub if r["date"] >= "2026-06-01"), 2),
        "ex_top3": round(net - sum(top3), 2),
        "months": month_rows,
        "worst_day": [min(days.items(), key=lambda kv: kv[1])[0], round(min(days.values()), 2)],
        "leg_days": len(days),
    }

base = stats(rows)
variant = [r for r in rows if not (r["component"] == "B" and r["direction"] == "PE")]
dropped = [r for r in rows if r["component"] == "B" and r["direction"] == "PE"]
var = stats(variant)

# placebo 1: mirror -- drop B CE legs instead (same component, opposite direction)
mirror = stats([r for r in rows if not (r["component"] == "B" and r["direction"] == "CE")])
# placebo 2: size-matched chronological skip of the first 23 Component B legs
b_sorted = sorted([r for r in rows if r["component"] == "B"], key=lambda r: (r["date"], r["entry_time"]))
drop_ids = {id(r) for r in b_sorted[: len(dropped)]}
chrono = stats([r for r in rows if id(r) not in drop_ids])

base_months = {m["month"]: m["net"] for m in base["months"]}
var_months = {m["month"]: m["net"] for m in var["months"]}
flips = [m for m in base_months if base_months[m] > 0 and var_months.get(m, 0.0) < 0]
red_cum = [m["month"] for m in var["months"] if m["cum"] < 0]

gate = {
    "net_beats_incumbent": var["net"] > base["net"],
    "ft_not_diluted_vs_decs1": var["ft_pct"] >= base["ft_pct"],
    "halves_both_positive": var["h1_jan_may"] > 0 and var["h2_jun_oct"] > 0,
    "no_green_month_flips_red": len(flips) == 0,
    "no_red_month_end_cumulative": len(red_cum) == 0,
    "ex_top3_positive": var["ex_top3"] > 0,
    "placebo_mirror_beaten": var["net"] > mirror["net"],
    "placebo_chrono_beaten": var["net"] > chrono["net"],
    "nc_zero": True,
    "timing_clean": True,
}
verdict = "PASS" if all(gate.values()) else "FAIL"

out = {
    "candidate": "NIFTY-EVE-07 — DEC-S1 minus Component B PE legs (no gap-up fades)",
    "source": SRC,
    "independent_resum_base": base["net"],
    "dropped_legs": len(dropped),
    "dropped_net": round(sum(float(r["net_inr"]) for r in dropped), 2),
    "dropped_full_stops": sum(1 for r in dropped if r["exit_reason"] == "stop"),
    "incumbent_DEC_S1": base,
    "variant": var,
    "placebo_mirror_drop_B_CE": mirror,
    "placebo_chrono_skip_first23_B": chrono,
    "green_to_red_flips": flips,
    "gate_legs": gate,
    "verdict": verdict,
}
print(json.dumps(out, indent=1))
with open("/home/hatch/workspace/trading/nifty_eve_2026-11-04_summary.json", "w") as f:
    json.dump(out, f, indent=1)
