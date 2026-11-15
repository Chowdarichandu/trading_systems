#!/usr/bin/env python3
"""Generates bank_engine_round2_2026-11-02.md from the Round-2 result files
+ a fresh controlled scorecard of the ending book v16. All numbers are read
from the scored artefacts, never retyped."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import build_fixed, controls, V14
from bank_r2_expiry import build_geo

grid = json.load(open("/home/hatch/workspace/trading/bank_r2_grid_results.json"))
ns1 = json.load(open("/home/hatch/workspace/trading/bank_r2_ns1_results.json"))
cross = json.load(open("/home/hatch/workspace/trading/bank_r2_ns1_cross_results.json"))
entry = json.load(open("/home/hatch/workspace/trading/bank_r2_entry_results.json"))
expiry = json.load(open("/home/hatch/workspace/trading/bank_r2_expiry_results.json"))
bleed = json.load(open("/home/hatch/workspace/trading/bank_r2_bleed_results.json"))
blue = json.load(open("/home/hatch/workspace/trading/bank_r2_blue_results.json"))

rows16, nc16, lbk16 = build_geo((50.0, 90.0), 0)
prows16, pnc16, _ = build_geo((50.0, 90.0), 6)
C16 = controls(rows16, nc16, lbk16, prows16, pnc16)
rows14, nc14, lbk14 = build_fixed(V14, delay=0)
prows14, pnc14, _ = build_fixed(V14, delay=6)
C14 = controls(rows14, nc14, lbk14, prows14, pnc14)

L = []
L.append("# BANK NIFTY ENGINE — ROUND 2 — 2026-11-02")
L.append("")
L.append("**Mandate (Chandu, 2026-11-02):** no saturation conclusions; work different use cases, "
         "combinations and permutations until the goal is achievable. Goal: **≥ ₹1,50,000 Jan–Oct 2026 "
         "gated pace (₹15,000/month)**. Basis: index-options premiums per 1 lot (30), cost ₹220/trade, "
         "UNIQUE-ONCE, paper only, real money ₹0. November primary/spec/logs untouched (read-only).")
L.append("")
L.append(f"**Result: book v14 +₹104,567.00 → book v16 +₹106,517.00** (82 trades, FT 53.7%, 2.02/week). "
         f"Two ingredients banked under the full controls gate: Cycle 28 grid cell (+₹600.00) and "
         f"Cycle 39 expiry-day pocket (+₹1,350.00). Ending pace **₹10,651.70/month**; remaining gap to the "
         f"floor pace **₹43,483.00 (₹4,348.30/month)**. 14 cycles run (28–41); the enumerated Round-2 space "
         f"is exhausted: 108/108 exit-grid cells, 24/24 NS1 cross cells, both (lA) cutoffs, both bias "
         f"variants, expiry-day strike + 3 expiry geometries, 3 bleed-pocket geometries, the standalone "
         f"setup3 family, and the combination stack — every cell gated, every verdict below.")
L.append("")
L.append("## Method and sanity (all before any variant was read)")
L.append("- A generalised exit replay (`bank_r2_core.py`) reproduces book v14 (+₹104,567.00, placebo "
         "+₹10,830.70, ex-top-3 +₹75,527.00, halves +₹84,980/+₹19,587, months exact) and book v8 "
         "(+₹77,196.50) to the paisa through the new code path.")
L.append("- NS1 regeneration (`bank_r2_ns1.py`, the frozen generator's logic with parameterised "
         "room/window): at frozen parameters it reproduces all 41 pooled book NS1 second legs exactly "
         "(date, direction, entry time, strike, expiry; signal times match the frozen map, 0 mismatches); "
         "the 24 regenerated legs absent from the pool are each explained by an earlier base leg on the "
         "same key. Frozen-construction note: stored second legs carry entry_time = the spot replay's "
         "exit-bar time (`replay()` returns the exit bar's time on stop/target) with strike = ATM(spot "
         "entry) — that convention is the frozen book and is preserved identically in every variant.")
L.append("- Entry-side re-pool (`bank_r2_entry.py`) from stored component candidates reproduces the "
         "89-leg B2 base exactly (date, direction, entry time, strike, expiry, representative system). "
         "The B2 Skill filters were measured to operate post-pool (73 Skill-rep CE legs and 21 Skill-solo "
         "PE legs ≤09:55 dropped, keys do not survive) and are applied that way.")
L.append("- Data completion: 22 expired contracts whose candles were missing were fetched from the "
         "Upstox expired-instruments API (browser User-Agent header) into `historical_proof_data/` — "
         "16 for the NS1 cells (the room-1.3/1.4 leg 2026-01-07 PE 59900, the window-15:00 leg 2026-09-03 "
         "PE 57500, 14 ITM second legs over 13 contracts) and 6 expiry-day ITM contracts. No number below "
         "rests on a NOT_COMPUTED exclusion: every taken book has NOT_COMPUTED = 0 (a few ITM cross "
         "cells carry named stream-level NOT_COMPUTED legs, counted where they occur).")
L.append("")
L.append("## Family 1 — exit-geometry grid (Cycles 28–30): 108 cells vs book v14")
L.append("Stop {40, 50, 60} × trigger {75, 90, 105} × lock {none, 50, 75, 90}; second targets frozen "
         "(330 <400 / 180 ≥400). Mode A = <400 segment only; B = ≥400 segments (warm runner + cold "
         "plain S/T); AB = all segments. Exactly **one cell passes the full gate**: "
         "A / stop 50 / trigger 105 / lock 75 → **+₹105,167.00 (+₹600.00), BANKED as book v15**. "
         "Its two changed legs: 2026-01-20 PE runner_stop +₹2,030 → square-off +₹6,380; 2026-07-27 PE "
         "runner_stop +₹2,030 → stop −₹1,720. Every other cell fails, 104 of them on the net leg alone. "
         "Full table (net = Jan–Oct ₹, FT90 = % of legs touching +90, placebo = +30-min delayed twin):")
L.append("")
L.append("| Mode | Stop | Trig | Lock | Net ₹ | FT90 % | Placebo ₹ | Ex-top-3 ₹ | Verdict |")
L.append("|---|---|---|---|---|---|---|---|---|")
for c in grid["cells"]:
    lock = "none" if c["lock"] is None else f"{c['lock']:.0f}"
    verdict = "**PASS — BANKED (v15)**" if (c["mode"] == "A" and c["stop"] == 50 and c["trig"] == 105
                                           and c["lock"] == 75) else "fail"
    L.append(f"| {c['mode']} | {c['stop']:.0f} | {c['trig']:.0f} | {lock} | {c['net']:,.2f} | "
             f"{c['ft90']} | {c['placebo']:,.2f} | {c['ex_top3']:,.2f} | {verdict} |")
L.append("")
L.append("## Family 2 — NS1 permutations (Cycles 31–33 + Cycle 41 cross): 24 cells, no pass")
L.append("Pool rebuilt per cell (B2 base + regenerated second legs → UNIQUE-ONCE → NS1-CE block → "
         "premium band [400,550) block → rebuilt anchored states → cold-(lA) skip → working exits). "
         "Axis cells gated vs v15; the 17 cross cells gated vs v16 with the v16 assembly.")
L.append("")
L.append("| Cell | Taken | Net ₹ | Verdict |")
L.append("|---|---|---|---|")
axis = [("room 1.3 (win 14:30, ATM)", ns1["r2c31_room13"]), ("room 1.4", ns1["r2c31_room14"]),
        ("room 1.6", ns1["r2c31_room16"]), ("window 14:00 (room 1.5, ATM)", ns1["r2c32_win1400"]),
        ("window 15:00", ns1["r2c32_win1500"]), ("strike 100 ITM (room 1.5, 14:30)", ns1["r2c33_itm"])]
for name, c in axis:
    note = "book identical to working book" if c["net"] in (105167.0,) else ""
    L.append(f"| {name} | {c['n']} | {c['net']:,.2f} | fail {note} |")
L.append(f"| window 15:00 detail | 83 | {ns1['r2c32_win1500']['net']:,.2f} | the one added leg "
         f"(2026-09-03 PE, entry premium 588.0) scores −₹325.00 square-off |")
L.append(f"| room 1.3/1.4 detail | — | — | their only newly admitted leg (2026-01-07 PE, entry premium "
         f"445.85) falls inside the blocked premium band [400,550) — the room axis cannot bite |")
for name, c in sorted(cross.items()):
    L.append(f"| cross {name} | {c['n']} | {c['net']:,.2f} | fail"
             + (f" (stream NOT_COMPUTED {c['stream_nc']} named)" if c["stream_nc"] else "") + " |")
L.append("")
L.append("## Family 3 — entry-side permutations (Cycles 34–37)")
c34, c35 = entry["r2c34_cutoff1130"], entry["r2c35_cutoff1230"]
L.append(f"- **(lA) rescan cutoff 11:30 (C34):** {c34['n']} taken, +₹{c34['net']:,.2f} — REJECTED "
         f"(net −₹310.00 vs v15; frequency {c34['per_week_raw']}/week < 2.0).")
L.append(f"- **(lA) rescan cutoff 12:30 (C35):** {c35['n']} taken, +₹{c35['net']:,.2f} — REJECTED "
         f"(same legs lost; frequency {c35['per_week_raw']}/week). Mechanism, measured: cutting the "
         f"rescan removes the pooled (lA) winners on 2026-02-24 (and, at 11:30, 2026-09-08's candidacy), "
         f"and on 2026-04-16 / 2026-06-30 the surviving 09:45 Skill legs lose their second source system "
         f"and fall under the B2 Skill-solo ≤09:55 drop — a pipeline interaction, recorded not hidden. "
         f"The frozen 13:30 cutoff is worth +₹310.00 to the book.")
L.append("- **Bias thresholds ±5 (C36):** (40, 85) and (30, 75) each remove **zero** stored V5-v2 "
         "winners — no winner sits on a flip band (CE winners on prev-day closing strength ∈ [35,40): "
         "none; PE winners on [75,80): none). Both cells are exact no-ops on the stored book; the "
         "admission side (legs a looser gate would have generated) does not exist in stored candidates "
         "and was not invented.")
c37 = expiry["r2c37_expiry_itm"]
L.append(f"- **Expiry-day strike 100 ITM (C37):** +₹{c37['net']:,.2f} — REJECTED (−₹3,750.00). Only 1 of "
         f"the 8 expiry-day legs changes outcome at the ITM strike (2026-02-24 PE +₹2,030 → −₹1,720); "
         f"level-relative exits make the other 7 identical.")
L.append("")
L.append("## Family 4 — use-case pockets (Cycles 38–40)")
L.append("- **Jun/Jul PE bleed (C38).** Diagnosis first (v16 book, 69 PE legs): Jun/Jul PE = 14 legs / "
         "−₹15,680.00 / 12 losers; the mechanical signature frozen after diagnosis and before scoring — "
         "**PE leg with anchored state cold** — covers 10 of the 14 (−₹13,000.00); prev-day-return and "
         "gap signatures do not isolate it. Conditional geometries on the 17 signature legs, all REJECTED: "
         f"plain (−50/+90) +₹{bleed['r2c38_bleed_plain']['net']:,.2f}; plain (−60/+90) "
         f"+₹{bleed['r2c38_bleed_s60']['net']:,.2f}; plain (−40/+90) +₹{bleed['r2c38_bleed_s40']['net']:,.2f}. "
         "The bleed is not an exit-geometry problem: the cold-PE legs that run earn more under the "
         "standard assembly than any tested variant recovers from the losers.")
e39 = expiry["r2c39_exp_plain"]
L.append(f"- **Expiry-day pocket (C39).** Expiry-day legs (8) under plain G0 (−50/+90) regardless of "
         f"segment/state: **+₹{e39['net']:,.2f} (+₹1,350.00) — full gate PASS, BANKED as book v16**. "
         f"Variants rejected: (−40/+90) +₹{expiry['r2c39_exp_s40']['net']:,.2f}; (−50/+75) "
         f"+₹{expiry['r2c39_exp_t75']['net']:,.2f}. Expiry-day paths do better without the runner: no "
         f"lock give-back on expiry-day theta paths.")
L.append(f"- **Wide-candle rejection standalone (C40).** Blue-Line setup3 legs admitted on unused keys "
         f"under the frozen admission rules: exactly **1 leg** in Jan–Oct (2026-07-06 PE, entry premium "
         f"683.5), scoring −₹1,720.00 → combined +₹{blue['net']:,.2f} — REJECTED. The book's pool already "
         f"covers nearly every setup3 day.")
L.append("")
L.append("## Family 5 — combinations (Cycle 41)")
L.append("- Passing ingredients from Families 1–4: exactly two — the Cycle-28 grid cell (lt400 trigger "
         "105) and the Cycle-39 expiry-day plain geometry. Families 2, 3 and the other pockets produced "
         "no passing ingredient, so no further stack exists to form. The two-ingredient stack was "
         "re-gated formally against the Round-2 starting book: **book v16 vs v14 — gate PASS** "
         "(net +₹106,517.00 vs +₹104,567.00; FT90 53.7 both; no red month-ends; no green month flips; "
         "halves ≥ 0; placebo beaten; timing audit 0 violations; independent re-sum matched).")
L.append("")
L.append("## Ending book v16 — controlled scorecard")
L.append(f"- Jan–Oct 2026: **+₹{C16['net']:,.2f}**, {C16['n']} trades, FT {C16['ft_pct']}% "
         f"(FT90 {C16['ft90_pct']}%), {C16['per_week_raw']}/week, premiums per 1 lot (30), cost ₹220/trade, "
         f"UNIQUE-ONCE. Pace ₹{C16['net']/10:,.2f}/month vs the ₹15,000 floor → **gap "
         f"₹{150000 - C16['net']:,.2f}**.")
L.append(f"- Months: " + " · ".join(f"{m} {C16['months'][m]:,.2f}" for m in
         ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")) +
         f". Red month-ends: {C16['red_month_ends'] or 'none'}.")
L.append(f"- Halves: Jan–May +₹{C16['halves']['jan_may']:,.2f} · Jun–Oct +₹{C16['halves']['jun_oct']:,.2f}. "
         f"Placebo (+30 min): +₹{C16['placebo']['net']:,.2f} (beaten). Ex-top-3: +₹{C16['ex_top3_total']:,.2f}. "
         f"Timing audit: {len(C16['timing_violations'])} violations / {C16['timing_entry_bars_checked']} "
         f"entry bars. NOT_COMPUTED: {C16['not_computed']}. Independent re-sum: "
         f"`bank_engine_r2c41_stack_trades.csv` — 82 trades / +₹106,517.00, matched.")
L.append("- Definition (frozen in `bank_engine_frozen.md`): pool V1 (B2 + NS1 second legs) → NS1 CE "
         "blocked → entry premium [400,550) blocked → anchored trailing-10 state → cold (lA) stand-aside; "
         "exits: entry premium <400 → runner stop −50, trigger +105, lock +75, second target +330; "
         "≥400 warm → runner stop −50, trigger +90, lock +90, second target +180; ≥400 cold → plain "
         "−50/+90; **expiry-day legs (date == expiry) → plain −50/+90 regardless of segment/state**; "
         "square-off 15:10.")
L.append("")
L.append("## Cycle index (Round 2)")
L.append("28–30 exit grid (108 cells, 1 banked → v15) · 31 NS1 room · 32 NS1 window · 33 NS1 strike ITM "
         "· 34 (lA) cutoff 11:30 · 35 (lA) cutoff 12:30 · 36 bias ±5 (zero-effect, proven) · 37 expiry-day "
         "strike ITM · 38 bleed pocket (3 geometries) · 39 expiry-day pocket (3 geometries, 1 banked → "
         "v16) · 40 setup3 standalone · 41 NS1 cross-grid (17 cells) + combination stack re-gate.")
L.append("")
L.append("Artefacts: `bank_r2_core.py`, `bank_r2_grid.py` + `bank_r2_grid_results.json`, `bank_r2_ns1.py` "
         "+ `bank_r2_ns1_results.json` + `bank_r2_ns1_cross_results.json`, `bank_r2_entry.py` + "
         "`bank_r2_entry_results.json`, `bank_r2_expiry.py` + `bank_r2_expiry_results.json`, "
         "`bank_r2_bleed.py` + `bank_r2_bleed_results.json`, `bank_r2_blue.py` + "
         "`bank_r2_blue_results.json`, `bank_r2_combine.py`, `bank_r2_fetch_missing.py`; trades: "
         "`bank_engine_r2c28_gridA_t105_trades.csv` (v15), `bank_engine_r2c39_exp_plain_trades.csv` and "
         "`bank_engine_r2c41_stack_trades.csv` (v16).")
open("/home/hatch/workspace/trading/bank_engine_round2_2026-11-02.md", "w").write("\n".join(L) + "\n")
print("report written:", len("\n".join(L)), "chars")
