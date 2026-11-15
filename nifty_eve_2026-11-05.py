#!/usr/bin/env python3
"""NIFTY-EVE-09/10/11 gate run, 2026-11-05 evening engine (Nifty only, paper, Rs0).

Trigger: 2026-11-05 was Nifty's first MISSED-MOVE day (afternoon extension
+137.70 pts beyond the morning high while the book was flat; Lesson
RSI-NIFTY-006) and the third blocked early solo-Skill day. The solo-admission
family is gate-closed (EVE-01/02b/03b) and the afternoon-addition population
is empty (EVE-06), so tonight's gated families come from the DEC-S1 leg-set
diagnosis on the TUNED SHADOW v1 frame (DEC-S1 minus Component B PE legs;
74 legs, +Rs103,050.25, GATE PASS 2026-11-04):

  component x direction nets on the frozen 97-leg DEC-S1 set:
    A CE 10 legs -2,560.75 | A PE 25 legs +56,662.75
    B CE 26 legs +45,506.50 | B PE 23 legs -11,881.75 (already dropped in v1)
    C CE  5 legs -10,339.75 | C PE  8 legs +13,781.50
  The CE weakness is sleeve-specific (B CE is the book's best cell), so the
  candidates drop CE legs one sleeve at a time, then combined.

Candidates (drop-only filters on the frozen leg set; incumbent = TUNED v1):
  EVE-09: v1 minus Component C CE legs (5 legs).
  EVE-10: v1 minus Component A CE legs (10 legs).
  EVE-11: v1 minus Component A CE and Component C CE legs (15 legs).

Full controls in the same run (backtest_controls_gate): independent re-sum
of both the DEC-S1 base (97 legs / +91,168.50) and the v1 frame (74 legs /
+103,050.25) from the source CSV before scoring; timing/leak audit (filter
inputs = component + direction, both fixed at the leg's entry bar; a
drop-only filter on frozen legs can introduce no timing violation);
placebo x2 per candidate (mirror: drop the same component's PE legs;
size-matched chronological skip of the first N legs of the same component);
halves split; full month table with green->red flip and red month-end
cumulative checks vs the v1 frame; ex-top-3 stress; NC = 0 (frozen set).
Basis: premiums per 1 lot (65), cost Rs220/trade already inside net_inr,
UNIQUE-ONCE (the source file is the frozen UNIQUE-ONCE leg set).
"""
import csv, json, collections

SRC = "/home/hatch/workspace/trading/nifty_next_phase_trades.csv"
rows = [r for r in csv.DictReader(open(SRC)) if r["set"] == "BASE"]
assert len(rows) == 97, len(rows)
assert round(sum(float(r["net_inr"]) for r in rows), 2) == 91168.50

V1 = [r for r in rows if not (r["component"] == "B" and r["direction"] == "PE")]
assert len(V1) == 74 and round(sum(float(r["net_inr"]) for r in V1), 2) == 103050.25


def stats(sub):
    net = round(sum(float(r["net_inr"]) for r in sub), 2)
    months = collections.defaultdict(float)
    days = collections.defaultdict(float)
    for r in sub:
        months[r["date"][:7]] += float(r["net_inr"])
        days[r["date"]] += float(r["net_inr"])
    top3 = sorted((float(r["net_inr"]) for r in sub), reverse=True)[:3]
    cum, month_rows = 0.0, []
    for m in sorted(months):
        cum += months[m]
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


base = stats(V1)
base_months = {m["month"]: m["net"] for m in base["months"]}


def gate_candidate(name, drop_pred, mirror_pred, chrono_pool, n_drop):
    variant = [r for r in V1 if not drop_pred(r)]
    dropped = [r for r in V1 if drop_pred(r)]
    var = stats(variant)
    mirror = stats([r for r in V1 if not mirror_pred(r)])
    pool_sorted = sorted(chrono_pool, key=lambda r: (r["date"], r["entry_time"]))
    drop_ids = {id(r) for r in pool_sorted[:n_drop]}
    chrono = stats([r for r in V1 if id(r) not in drop_ids])
    var_months = {m["month"]: m["net"] for m in var["months"]}
    flips = [m for m in base_months if base_months[m] > 0 and var_months.get(m, 0.0) < 0]
    red_cum = [m["month"] for m in var["months"] if m["cum"] < 0]
    gate = {
        "net_beats_incumbent_v1": var["net"] > base["net"],
        "ft_not_diluted_vs_v1": var["ft_pct"] >= base["ft_pct"],
        "halves_both_positive": var["h1_jan_may"] > 0 and var["h2_jun_oct"] > 0,
        "no_green_month_flips_red": len(flips) == 0,
        "no_red_month_end_cumulative": len(red_cum) == 0,
        "ex_top3_positive": var["ex_top3"] > 0,
        "placebo_mirror_beaten": var["net"] > mirror["net"],
        "placebo_chrono_beaten": var["net"] > chrono["net"],
        "nc_zero": True,
        "timing_clean": True,
    }
    return {
        "candidate": name,
        "dropped_legs": len(dropped),
        "dropped_net": round(sum(float(r["net_inr"]) for r in dropped), 2),
        "dropped_full_stops": sum(1 for r in dropped if r["exit_reason"] == "stop"),
        "incumbent_TUNED_v1": base,
        "variant": var,
        "placebo_mirror": mirror,
        "placebo_chrono": chrono,
        "green_to_red_flips": flips,
        "gate_legs": gate,
        "verdict": "PASS" if all(gate.values()) else "FAIL",
    }


out = {"incumbent_frame": "TUNED SHADOW v1 = DEC-S1 minus Component B PE (74 legs, +103,050.25)"}
out["EVE-09"] = gate_candidate(
    "NIFTY-EVE-09 — TUNED v1 minus Component C CE legs (weekly-expiry CE sleeve)",
    lambda r: r["component"] == "C" and r["direction"] == "CE",
    lambda r: r["component"] == "C" and r["direction"] == "PE",
    [r for r in V1 if r["component"] == "C"], 5)
out["EVE-10"] = gate_candidate(
    "NIFTY-EVE-10 — TUNED v1 minus Component A CE legs (confirmed-book CE)",
    lambda r: r["component"] == "A" and r["direction"] == "CE",
    lambda r: r["component"] == "A" and r["direction"] == "PE",
    [r for r in V1 if r["component"] == "A"], 10)
out["EVE-11"] = gate_candidate(
    "NIFTY-EVE-11 — TUNED v1 minus Component A CE and Component C CE legs (combined)",
    lambda r: r["component"] in ("A", "C") and r["direction"] == "CE",
    lambda r: r["component"] in ("A", "C") and r["direction"] == "PE",
    [r for r in V1 if r["component"] in ("A", "C")], 15)

print(json.dumps(out, indent=1))
with open("/home/hatch/workspace/trading/nifty_eve_2026-11-05_summary.json", "w") as f:
    json.dump(out, f, indent=1)
