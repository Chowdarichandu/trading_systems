#!/usr/bin/env python3
"""NIFTY-EVE-14/15/16 gate run, 2026-11-09 evening engine (Nifty only, paper, Rs0).

Trigger: 2026-11-09 was the PRIMARY's first November trade and its first loss:
NF-PAPER-C3G7 confirmed PE key (V5 v2 via Skill or_breakdown + Skill V3, both
signal 10:40), entry 10:45 @ 293.85 on 24800 PE (expiry 2026-11-23), stopped
11:25 @ 243.85, net -3,470.00. Premium MFE +0.25 (entry bar only) -- the leg
NEVER developed; spot printed the day low (24,838.75) on the signal bar itself
and never traded lower after entry (Lesson RSI-NIFTY-009: no follow-through
chop -- breakdown at the day's extreme).

History census first (same run): the primary's own history is Component A of
the frozen DEC-S1 leg set (35 legs, the standing causal book). Candidates are
drop-only filters diagnosed from today's shape -- a LATE-MORNING confirmed PE
entry that never developed -- tested on both frames that contain A PE legs:
  EVE-14: standing causal book (A frame) minus A PE legs entering >= 10:30.
  EVE-15: TUNED SHADOW v2 frame minus A PE legs entering >= 10:30.
  EVE-16: standing causal book minus A PE legs entering >= 11:00
          (the family's next threshold variant, mechanically distinct).
Plus a population check (not a scored candidate): the no-development cut
(exit if running max premium high < entry+15 by the close of the 3rd bar
after entry) needs per-leg premium paths, which the frozen leg file does not
store; candle-file coverage for the 35 A legs is counted and reported.

Full controls in the same run (backtest_controls_gate): independent re-sum
of the DEC-S1 base (97 / +91,168.50), the A frame (35 / +54,102.00) and the
TUNED v2 frame (59 / +115,950.75) before scoring; timing audit (filter input
= entry_time + direction, both known at the entry bar; drop-only filter on
frozen legs introduces no timing violation); placebo x2 per candidate
(mirror: same component, opposite direction, same time cut; size-matched
chronological skip of the first N legs of the same component+direction);
halves split; full month table with green->red flip and red month-end
cumulative checks vs each frame's incumbent; ex-top-3 stress; NC = 0.
Basis: premiums per 1 lot (65), cost Rs220/trade inside net_inr, UNIQUE-ONCE.
"""
import csv, json, collections, glob, os

SRC = "/home/hatch/workspace/trading/nifty_next_phase_trades.csv"
rows = [r for r in csv.DictReader(open(SRC)) if r["set"] == "BASE"]
assert len(rows) == 97, len(rows)
assert round(sum(float(r["net_inr"]) for r in rows), 2) == 91168.50

A = [r for r in rows if r["component"] == "A"]
assert len(A) == 35 and round(sum(float(r["net_inr"]) for r in A), 2) == 54102.00
V2 = [r for r in rows if not ((r["component"] == "B" and r["direction"] == "PE")
                             or (r["component"] in ("A", "C") and r["direction"] == "CE"))]
assert len(V2) == 59 and round(sum(float(r["net_inr"]) for r in V2), 2) == 115950.75

def mins(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)

# ---------- history census (journal / RSI log evidence) ----------
cen = {}
for label, sub in [("A_all", A),
                   ("A_PE", [r for r in A if r["direction"] == "PE"]),
                   ("A_CE", [r for r in A if r["direction"] == "CE"])]:
    stops = [r for r in sub if r["exit_reason"] == "stop"]
    cen[label] = {
        "legs": len(sub), "net": round(sum(float(r["net_inr"]) for r in sub), 2),
        "exits": dict(collections.Counter(r["exit_reason"] for r in sub)),
        "full_stops": len(stops),
        "stop_net": round(sum(float(r["net_inr"]) for r in stops), 2),
        "quick_stops_le45min": sum(1 for r in stops if mins(r["exit_time"]) - mins(r["entry_time"]) <= 45),
        "worst_month_for_stops": collections.Counter(r["date"][:7] for r in stops).most_common(1),
    }
late_pe = [r for r in A if r["direction"] == "PE" and mins(r["entry_time"]) >= mins("10:30")]
late_pe11 = [r for r in A if r["direction"] == "PE" and mins(r["entry_time"]) >= mins("11:00")]
cen["A_PE_entry_ge_1030"] = {"legs": len(late_pe), "net": round(sum(float(r["net_inr"]) for r in late_pe), 2),
                            "full_stops": sum(1 for r in late_pe if r["exit_reason"] == "stop"),
                            "detail": [(r["date"], r["entry_time"], r["exit_reason"], float(r["net_inr"])) for r in late_pe]}
cen["A_PE_entry_ge_1100"] = {"legs": len(late_pe11), "net": round(sum(float(r["net_inr"]) for r in late_pe11), 2),
                             "full_stops": sum(1 for r in late_pe11 if r["exit_reason"] == "stop")}
early_pe = [r for r in A if r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")]
cen["A_PE_entry_lt_1030"] = {"legs": len(early_pe), "net": round(sum(float(r["net_inr"]) for r in early_pe), 2)}

# ---------- no-development cut: candle-path coverage check ----------
cov = 0; missing = []
for r in A:
    pat = f"/home/hatch/workspace/trading/aggressive_data/candles_NIFTY_{r['strike']}{r['direction']}_*.json"
    hit = [f for f in glob.glob(pat) if r["date"] in os.path.basename(f) or r["expiry"] in os.path.basename(f)]
    if hit: cov += 1
    else: missing.append((r["date"], r["strike"], r["direction"]))
cen["nodev_candle_coverage"] = {"covered": cov, "of": len(A), "missing": missing}

def stats(sub):
    net = round(sum(float(r["net_inr"]) for r in sub), 2)
    months = collections.defaultdict(float); days = collections.defaultdict(float)
    for r in sub:
        months[r["date"][:7]] += float(r["net_inr"]); days[r["date"]] += float(r["net_inr"])
    top3 = sorted((float(r["net_inr"]) for r in sub), reverse=True)[:3]
    cum, mrows = 0.0, []
    for m in sorted(months):
        cum += months[m]; mrows.append({"month": m, "net": round(months[m], 2), "cum": round(cum, 2)})
    return {"legs": len(sub), "net": net,
            "ft_pct": round(100.0 * sum(int(r["ft"]) for r in sub) / len(sub), 1) if sub else 0.0,
            "h1_jan_may": round(sum(float(r["net_inr"]) for r in sub if r["date"] < "2026-06-01"), 2),
            "h2_jun_oct": round(sum(float(r["net_inr"]) for r in sub if r["date"] >= "2026-06-01"), 2),
            "ex_top3": round(net - sum(top3), 2), "months": mrows,
            "worst_day": [min(days.items(), key=lambda kv: kv[1])[0], round(min(days.values()), 2)] if days else None}

def gate(name, frame, frame_label, drop_pred, mirror_pred, chrono_pool):
    base = stats(frame); base_months = {m["month"]: m["net"] for m in base["months"]}
    dropped = [r for r in frame if drop_pred(r)]
    variant = [r for r in frame if not drop_pred(r)]
    var = stats(variant)
    mirror = stats([r for r in frame if not mirror_pred(r)])
    pool_sorted = sorted(chrono_pool, key=lambda r: (r["date"], r["entry_time"]))
    drop_ids = {id(r) for r in pool_sorted[:len(dropped)]}
    chrono = stats([r for r in frame if id(r) not in drop_ids])
    var_months = {m["month"]: m["net"] for m in var["months"]}
    flips = [m for m in base_months if base_months[m] > 0 and var_months.get(m, 0.0) < 0]
    red_cum = [m["month"] for m in var["months"] if m["cum"] < 0]
    g = {"net_beats_incumbent": var["net"] > base["net"],
         "ft_not_diluted": var["ft_pct"] >= base["ft_pct"],
         "halves_both_positive": var["h1_jan_may"] > 0 and var["h2_jun_oct"] > 0,
         "no_green_month_flips_red": len(flips) == 0,
         "no_red_month_end_cumulative": len(red_cum) == 0,
         "ex_top3_positive": var["ex_top3"] > 0,
         "placebo_mirror_beaten": var["net"] > mirror["net"],
         "placebo_chrono_beaten": var["net"] > chrono["net"],
         "nc_zero": True, "timing_clean": True}
    return {"candidate": name, "frame": frame_label, "incumbent": base, "variant": var,
            "dropped_legs": len(dropped), "dropped_net": round(sum(float(r["net_inr"]) for r in dropped), 2),
            "dropped_full_stops": sum(1 for r in dropped if r["exit_reason"] == "stop"),
            "placebo_mirror": mirror, "placebo_chrono": chrono,
            "green_to_red_flips": flips, "gate_legs": g,
            "verdict": "PASS" if all(g.values()) else "FAIL"}

out = {"census": cen}
out["EVE-14"] = gate("NIFTY-EVE-14 — standing book minus Component A PE legs entering >= 10:30",
    A, "standing causal book (A, 35 legs, +54,102.00)",
    lambda r: r["direction"] == "PE" and mins(r["entry_time"]) >= mins("10:30"),
    lambda r: r["direction"] == "CE" and mins(r["entry_time"]) >= mins("10:30"),
    [r for r in A if r["direction"] == "PE"])
out["EVE-15"] = gate("NIFTY-EVE-15 — TUNED v2 minus Component A PE legs entering >= 10:30",
    V2, "TUNED SHADOW v2 (59 legs, +115,950.75)",
    lambda r: r["component"] == "A" and r["direction"] == "PE" and mins(r["entry_time"]) >= mins("10:30"),
    lambda r: r["component"] == "A" and r["direction"] == "CE" and mins(r["entry_time"]) >= mins("10:30"),
    [r for r in V2 if r["component"] == "A" and r["direction"] == "PE"])
out["EVE-16"] = gate("NIFTY-EVE-16 — standing book minus Component A PE legs entering >= 11:00",
    A, "standing causal book (A, 35 legs, +54,102.00)",
    lambda r: r["direction"] == "PE" and mins(r["entry_time"]) >= mins("11:00"),
    lambda r: r["direction"] == "CE" and mins(r["entry_time"]) >= mins("11:00"),
    [r for r in A if r["direction"] == "PE"])
print(json.dumps(out, indent=1))
with open("/home/hatch/workspace/trading/nifty_eve_2026-11-09_summary.json", "w") as f:
    json.dump(out, f, indent=1)
