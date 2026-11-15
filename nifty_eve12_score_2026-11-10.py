#!/usr/bin/env python3
"""NIFTY-EVE-12 — afternoon spot-range-break sleeve. Scored 2026-11-10,
exactly as registered (november_rsi_candidates.md, 2026-11-05):
"while the book is flat, the first fresh day-range break after 12:30 is
taken ATM100 on the break side with DEC-S1 geometry, max 1/day, segment
day-cap governs." Population: nifty_eve12_population_2026-11-10.md.

Frozen conventions (all copied verbatim from the house machinery):
- S5 exit geometry + prem_day store convention: nifty_tuning_2026-11-10.py
  (itself verbatim from nifty_next_phase_score.py); SQ bar = "15:20"
  (the DEC-S1 construction's square-off bar — all 44 stored DEC-S1
  square-off exits carry exit_time 15:20).
- Basis: premiums per 1 lot (65), cost Rs 220/trade, UNIQUE-ONCE.
- Gate form: house gate (nifty_tuning_2026-11-10 gate_eval) adapted to an
  increment sleeve per the BANK-EVE-06(a) precedent.

Registered-rule readings, stated once (registry text governs; these are
the mechanical readings of its words):
- Day range = running day high/low from ALL prior bars of the day
  (09:15 onward, bar highs/lows). Break = first bar with start >= 12:30
  whose CLOSE is strictly beyond that running range. Entry = next bar
  open (signal exists only at the break bar's close).
- ATM100 = strike nearest the break bar's spot close on the 100 grid,
  halves round up (floor(x/100 + 0.5) * 100). Uses ONLY the break bar's
  close — information available at the signal moment.
- Expiry in force = nearest monthly >= date (A/B-leg convention),
  validated in-run against every A/B leg's stored expiry.
- "While the book is flat" (layering): evaluated at the break bar — no
  frame leg with entry_time <= break_time < exit_time. Only the day's
  FIRST afternoon break is the trigger; if the book is busy then, no
  EVE-12 leg that day (a scan-reading sensitivity is reported, not gated).
- "Segment day-cap governs": causal realised form (EVE-08/EVE-13 form) —
  skip if the frame's realised day P&L from legs exited at/before the
  break bar is <= -Rs 3,000 at the break.
Paper only, real money Rs 0. Frozen logs/specs unmodified.
"""
import csv, json, collections, math
from pathlib import Path

TR = Path.home() / "workspace/trading"
LOT, COST, SQ = 65, 220.0, "15:20"
DAY_CAP = -3000.0

# ---------------- stores ----------------
SPOT = json.load(open(TR / "daily2leg" / "spot.json"))["NIFTY"]
PREM_M = json.load(open(TR / "daily2leg" / "prem_nifty.json"))
PREM_W = json.load(open(TR / "daily2leg" / "prem_nifty_weekly.json"))

def prem_day(exp, strike, typ, d, component):
    """Verbatim convention of nifty_next_phase_score.prem_day: designated
    store first (C -> weekly, A/B -> monthly), fallback to the other."""
    key = f"{exp}|{int(strike)}|{typ}"
    order = (("weekly", PREM_W), ("monthly", PREM_M)) if component == "C" \
        else (("monthly", PREM_M), ("weekly", PREM_W))
    for name, store in order:
        cd = store.get(key, {}).get(d)
        if cd:
            bars = sorted((t, float(v[0]), float(v[1]), float(v[2]),
                           float(v[3])) for t, v in cd.items())
            return bars, name
    return None, None

def prem_day_monthly(exp, strike, typ, d):
    """EVE-12 legs: monthly construction store only (population report)."""
    cd = PREM_M.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if not cd:
        return None
    return sorted((t, float(v[0]), float(v[1]), float(v[2]), float(v[3]))
                  for t, v in cd.items())

# ---------------- frozen S5 replay (verbatim from nifty_tuning) --------
def replay(bars, entry_time):
    if not bars:
        return None
    idxs = [i for i, b in enumerate(bars) if b[0] >= entry_time]
    if not idxs:
        return None
    i0 = idxs[0]
    if i0 >= len(bars):
        return None
    bs = bars[i0:]
    if bs[0][0] > SQ:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0

    def out(pts, reason, t, ft, px):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round(pts * LOT - COST, 2))

    cur_stop = stop
    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > SQ:
            break
        if l <= cur_stop:
            return out(cur_stop - entry,
                       "be_stop" if cur_stop == entry else "stop", t, 0,
                       cur_stop)
        if h >= target:
            stop2, target2 = entry + 60.0, entry + 175.0
            for (t2, o2, h2, l2, cl2) in bs[i + 1:]:
                if t2 > SQ:
                    break
                if l2 <= stop2:
                    return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2:
                    return out(target2 - entry, "runner_target", t2, 1,
                               target2)
                if t2 == SQ:
                    return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bs[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= 50.0:
            cur_stop = max(cur_stop, entry)
        if t == SQ:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bs[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

# ---------------- stats (house form) ----------------
def stats(sub):
    if not sub:
        return {"legs": 0, "net": 0.0, "ft_pct": 0.0, "h1_jan_may": 0.0,
                "h2_jun_oct": 0.0, "ex_top3": 0.0, "months": [],
                "worst_day": None}
    net = round(sum(float(r["net_inr"]) for r in sub), 2)
    months = collections.defaultdict(float); days = collections.defaultdict(float)
    for r in sub:
        months[r["date"][:7]] += float(r["net_inr"]); days[r["date"]] += float(r["net_inr"])
    top3 = sorted((float(r["net_inr"]) for r in sub), reverse=True)[:3]
    cum, mrows = 0.0, []
    for m in sorted(months):
        cum += months[m]; mrows.append({"month": m, "net": round(months[m], 2), "cum": round(cum, 2)})
    wd = min(days.items(), key=lambda kv: kv[1])
    return {"legs": len(sub), "net": net,
            "ft_pct": round(100.0 * sum(int(r["ft"]) for r in sub) / len(sub), 1),
            "h1_jan_may": round(sum(float(r["net_inr"]) for r in sub if r["date"] < "2026-06-01"), 2),
            "h2_jun_oct": round(sum(float(r["net_inr"]) for r in sub if r["date"] >= "2026-06-01"), 2),
            "ex_top3": round(net - sum(top3), 2), "months": mrows,
            "worst_day": [wd[0], round(wd[1], 2)]}

# ================= LEG 0 — reproduction =================
rows = [r for r in csv.DictReader(open(TR / "nifty_next_phase_trades.csv"))
        if r["set"] == "BASE"]
assert len(rows) == 97, len(rows)
assert round(sum(float(r["net_inr"]) for r in rows), 2) == 91168.50
V2 = [r for r in rows if not ((r["component"] == "B" and r["direction"] == "PE")
                             or (r["component"] in ("A", "C") and r["direction"] == "CE"))]
assert len(V2) == 59 and round(sum(float(r["net_inr"]) for r in V2), 2) == 115950.75
print("LEG 0a RE-SUM OK: DEC-S1 97/+91,168.50 - TUNED v2 59/+115,950.75")

repro_bad = []
for leg in rows:
    bars, _tag = prem_day(leg["expiry"], leg["strike"], leg["direction"],
                          leg["date"], leg["component"])
    res = replay(bars, leg["entry_time"]) if bars else None
    if res is None:
        repro_bad.append((leg["date"], leg["component"], "no-replay")); continue
    if not (abs(res["entry"] - float(leg["entry_premium"])) < 1e-9
            and abs(res["exit"] - float(leg["exit_premium"])) < 1e-9
            and res["exit_time"] == leg["exit_time"]
            and res["exit_reason"] == leg["exit_reason"]
            and abs(res["net"] - float(leg["net_inr"])) < 1e-9
            and res["ft"] == int(leg["ft"])):
        repro_bad.append((leg["date"], leg["component"], leg["direction"],
                          res, {k: leg[k] for k in ("entry_premium", "exit_premium",
                                                    "exit_time", "exit_reason", "net_inr")}))
assert not repro_bad, f"LEG 0b REPRODUCTION FAILED on {len(repro_bad)} legs: {repro_bad[:3]}"
print("LEG 0b REPLAY OK: all 97 DEC-S1 legs reproduce entry/exit/reason/net exactly")

# expiry calendar: monthly expiries attested by A/B legs + Nov monthly
legsfile = json.load(open(TR / "nifty_engine_r11_decs1_legs.json"))
AB = [l for l in legsfile if l["component"] in ("A", "B")]
MONTHLY = sorted({l["expiry"] for l in AB} | {"2026-11-23"})
def expiry_in_force(d):
    for e in MONTHLY:
        if e >= d:
            return e
    return None
cal_bad = [(l["date"], l["expiry"], expiry_in_force(l["date"])) for l in AB
           if expiry_in_force(l["date"]) != l["expiry"]]
assert not cal_bad, f"expiry calendar mismatch: {cal_bad[:3]}"
print(f"LEG 0c EXPIRY CALENDAR OK: nearest-monthly>={ '{date}' } reproduces all {len(AB)} A/B leg expiries; monthly set {MONTHLY}")

# ================= EVE-12 break detection =================
def detect_break(day_bars):
    """First bar start >= 12:30 whose close is strictly beyond the running
    day range (bar highs/lows of all prior bars). Returns dict or None."""
    run_hi, run_lo = None, None
    for i, (t, o, h, l, c) in enumerate(day_bars):
        if t >= "12:30":
            if run_hi is not None and c > run_hi:
                return {"idx": i, "time": t, "direction": "CE",
                        "ref": run_hi, "close": c}
            if run_lo is not None and c < run_lo:
                return {"idx": i, "time": t, "direction": "PE",
                        "ref": run_lo, "close": c}
        run_hi = h if run_hi is None else max(run_hi, h)
        run_lo = l if run_lo is None else min(run_lo, l)
    return None

def all_breaks(day_bars):
    """Every afternoon close-break of the (evolving) running range —
    used only for the scan-reading sensitivity."""
    out, run_hi, run_lo = [], None, None
    for i, (t, o, h, l, c) in enumerate(day_bars):
        if t >= "12:30":
            if run_hi is not None and c > run_hi:
                out.append({"idx": i, "time": t, "direction": "CE", "ref": run_hi, "close": c})
            elif run_lo is not None and c < run_lo:
                out.append({"idx": i, "time": t, "direction": "PE", "ref": run_lo, "close": c})
        run_hi = h if run_hi is None else max(run_hi, h)
        run_lo = l if run_lo is None else min(run_lo, l)
    return out

def atm100(close):
    return int(math.floor(close / 100.0 + 0.5) * 100)

def score_leg(date, brk, day_bars, direction=None, entry_idx_off=1):
    """Score one EVE-12-form leg. direction/entry_idx_off overridable for
    placebos (flip: opposite direction; shift: entry 6 bars later than the
    real entry bar). Returns (row, nc_reason)."""
    spot_idx = brk["idx"] + entry_idx_off
    if spot_idx >= len(day_bars):
        return None, "no entry bar after break"
    entry_time = day_bars[spot_idx][0]
    if entry_time > SQ:
        return None, "entry bar after square-off bar"
    typ = direction or brk["direction"]
    strike = atm100(brk["close"])
    exp = expiry_in_force(date)
    bars = prem_day_monthly(exp, strike, typ, date)
    if not bars:
        return None, f"premium series absent {exp}|{strike}|{typ}"
    if entry_time not in {b[0] for b in bars}:
        return None, f"entry bar {entry_time} absent from premium day"
    res = replay(bars, entry_time)
    if res is None:
        return None, "replay returned None"
    row = {"date": date, "break_time": brk["time"],
           "break_dir": brk["direction"], "ref_level": brk["ref"],
           "break_close": brk["close"], "direction": typ,
           "strike": strike, "expiry": exp, "entry_time": entry_time,
           "entry_premium": res["entry"], "exit_time": res["exit_time"],
           "exit_premium": res["exit"], "exit_reason": res["exit_reason"],
           "ft": res["ft"], "net_inr": res["net"],
           "prem_last_bar": bars[-1][0]}
    return row, None

DATES = sorted(d for d in SPOT if "2026-01-01" <= d <= "2026-10-31")
assert len(DATES) == 205, len(DATES)

standalone, nc_legs, no_break_days = [], [], 0
breaks = {}
for d in DATES:
    day = [(b[0], float(b[1]), float(b[2]), float(b[3]), float(b[4]))
           for b in SPOT[d]]
    brk = detect_break(day)
    if brk is None:
        no_break_days += 1
        continue
    breaks[d] = (brk, day)
    row, nc = score_leg(d, brk, day)
    if row is None:
        nc_legs.append({"date": d, "break_time": brk["time"], "reason": nc})
    else:
        row["set"] = "STANDALONE"
        standalone.append(row)
print(f"STANDALONE: {len(standalone)} legs scored, {len(nc_legs)} NC, "
      f"{no_break_days} no-break days of {len(DATES)}")

# ================= layering filters =================
def frame_filter(frame_rows, brk, date):
    """(eligible, why) — flatness at break + realised day cap."""
    ft = brk["time"]
    busy = [r for r in frame_rows if r["date"] == date
            and r["entry_time"] <= ft < r["exit_time"]]
    if busy:
        return False, "book busy at break"
    realised = sum(float(r["net_inr"]) for r in frame_rows
                   if r["date"] == date and r["exit_time"] <= ft)
    if realised <= DAY_CAP:
        return False, f"day-cap: realised {realised:.2f} <= -3000"
    return True, ""

def layered(frame_rows, label):
    kept, dropped = [], []
    for d, (brk, day) in sorted(breaks.items()):
        ok, why = frame_filter(frame_rows, brk, d)
        if not ok:
            dropped.append({"date": d, "break_time": brk["time"], "why": why})
            continue
        row, nc = score_leg(d, brk, day)
        if row is None:
            nc_legs.append({"date": d, "break_time": brk["time"],
                            "reason": f"{label}: {nc}"})
            continue
        row = dict(row); row["set"] = label
        kept.append(row)
    return kept, dropped

v2_inc, v2_dropped = layered(V2, "V2_LAYER")
s1_inc, s1_dropped = layered(rows, "DECS1_LAYER")

# placebos on the v2-eligible day set (same breaks, same filter outcome)
elig_dates = {r["date"] for r in v2_inc} | {x["date"] for x in v2_dropped
                                            if False}
elig_dates = sorted({d for d, (brk, day) in breaks.items()
                     if frame_filter(V2, brk, d)[0]})
shift_inc, flip_inc = [], []
for d in elig_dates:
    brk, day = breaks[d]
    r, _ = score_leg(d, brk, day, entry_idx_off=1 + 6)
    if r: r = dict(r); r["set"] = "PLACEBO_SHIFT"; shift_inc.append(r)
    opp = "PE" if brk["direction"] == "CE" else "CE"
    r, _ = score_leg(d, brk, day, direction=opp)
    if r: r = dict(r); r["set"] = "PLACEBO_FLIP"; flip_inc.append(r)

# scan-reading sensitivity on the v2 frame (first break WHILE flat)
scan_inc = []
for d in DATES:
    day = [(b[0], float(b[1]), float(b[2]), float(b[3]), float(b[4]))
           for b in SPOT[d]]
    for brk in all_breaks(day):
        ok, _ = frame_filter(V2, brk, d)
        if not ok:
            continue
        row, nc = score_leg(d, brk, day)
        if row:
            row = dict(row); row["set"] = "SENSITIVITY_SCAN"
            scan_inc.append(row)
        break  # first break-while-flat only

# ================= timing audit =================
timing_viol = 0
for r in standalone + v2_inc + s1_inc:
    if not (r["entry_time"] > r["break_time"]):
        timing_viol += 1
    # strike must derive only from the break bar's close
    if atm100(r["break_close"]) != r["strike"]:
        timing_viol += 1
print(f"TIMING AUDIT: {timing_viol} violations over "
      f"{len(standalone) + len(v2_inc) + len(s1_inc)} scored legs")

# ================= gate (TUNED v2 frame = decision frame) =================
def gate(frame_rows, inc_rows, label):
    layered_rows = [dict(r) for r in frame_rows] + \
                   [dict(r, component="E12") for r in inc_rows]
    base, var = stats(frame_rows), stats(layered_rows)
    incr, shf, flp = stats(inc_rows), stats(shift_inc), stats(flip_inc)
    base_months = {m["month"]: m["net"] for m in base["months"]}
    var_months = {m["month"]: m["net"] for m in var["months"]}
    flips = [m for m in base_months if base_months[m] > 0
             and var_months.get(m, 0.0) < 0]
    red_cum = [m["month"] for m in var["months"] if m["cum"] < 0]
    g = {"reproduction_exact": True,
         "increment_net_positive": incr["net"] > 0,
         "layered_net_beats_incumbent": var["net"] > base["net"],
         "layered_ft_not_diluted": var["ft_pct"] >= base["ft_pct"],
         "increment_halves_both_positive": incr["h1_jan_may"] > 0 and incr["h2_jun_oct"] > 0,
         "layered_halves_both_positive": var["h1_jan_may"] > 0 and var["h2_jun_oct"] > 0,
         "no_green_month_flips_red": len(flips) == 0,
         "no_red_month_end_cumulative": len(red_cum) == 0,
         "layered_ex_top3_positive": var["ex_top3"] > 0,
         "placebo_shift_beaten": incr["net"] > shf["net"],
         "placebo_flip_beaten": incr["net"] > flp["net"],
         "nc_zero": len(nc_legs) == 0,
         "timing_clean": timing_viol == 0}
    return {"frame": label, "incumbent": base, "layered": var,
            "increment": incr, "placebo_shift_increment": shf,
            "placebo_flip_increment": flp, "green_to_red_flips": flips,
            "gate_legs": g,
            "verdict": "PASS" if all(g.values()) else "FAIL"}

gate_v2 = gate(V2, v2_inc, "TUNED v2 (DEC-S1 minus B PE / A CE / C CE)")
gate_s1 = gate(rows, s1_inc, "DEC-S1 (frozen)")

# ================= November appendix (counterfactual, not gated) =========
nov_spot = [d for d in SPOT if d >= "2026-11-01"]
nov_contracts = [k for k in PREM_M if any(dd >= "2026-11-01" for dd in PREM_M[k])]
nov_appendix = {
    "window": "2026-11-02..2026-11-09",
    "status": "NOT_COMPUTED",
    "reason": ("daily2leg/spot.json NIFTY ends 2026-10-30 (no November spot "
               "days), and prem_nifty.json holds November days for only "
               f"{len(nov_contracts)} contracts (sleeve-specific patches "
               "for DEC-S1's own strikes) — no afternoon ATM100-at-break "
               "population exists for November. Never estimated."),
    "nov_spot_days_in_store": len(nov_spot)}

# ================= outputs =================
all_rows = standalone + v2_inc + s1_inc + shift_inc + flip_inc + scan_inc
cols = ["set", "date", "break_time", "break_dir", "ref_level", "break_close",
        "direction", "strike", "expiry", "entry_time", "entry_premium",
        "exit_time", "exit_premium", "exit_reason", "ft", "net_inr",
        "prem_last_bar"]
with open(TR / "nifty_eve12_trades_2026-11-10.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in all_rows:
        w.writerow({c: r.get(c, "") for c in cols})

summary = {
    "candidate": "NIFTY-EVE-12 — afternoon spot-range-break sleeve",
    "registered_rule": "while flat, first fresh day-range break after 12:30, "
                       "ATM100 on break side, DEC-S1 (S5) geometry, max 1/day, "
                       "segment day-cap governs",
    "basis": "premiums per 1 lot (65), Rs 220/trade, UNIQUE-ONCE, paper only",
    "leg0_reproduction": {"decs1": "97 legs / +91,168.50 re-summed exact; "
                                   "replay reproduces all 97 exits exactly",
                          "tuned_v2": "59 legs / +115,950.75 re-summed exact",
                          "expiry_calendar": f"validated on {len(AB)} A/B legs"},
    "standalone": stats(standalone),
    "no_break_days": no_break_days,
    "nc_legs": nc_legs,
    "v2_filter_dropped": v2_dropped,
    "decs1_filter_dropped": s1_dropped,
    "increment_ex_top3_v2": stats(v2_inc)["ex_top3"],
    "increment_worst_day_v2": stats(v2_inc)["worst_day"],
    "scan_sensitivity_increment": stats(scan_inc),
    "gate_tuned_v2": gate_v2,
    "gate_decs1_secondary": gate_s1,
    "november_appendix": nov_appendix,
    "exit_reason_mix_standalone": dict(collections.Counter(
        r["exit_reason"] for r in standalone)),
    "exit_reason_mix_v2_increment": dict(collections.Counter(
        r["exit_reason"] for r in v2_inc)),
}
json.dump(summary, open(TR / "nifty_eve12_score_2026-11-10_summary.json", "w"),
          indent=1)
print(json.dumps({"standalone": summary["standalone"],
                  "v2_increment": gate_v2["increment"],
                  "v2_layered": gate_v2["layered"],
                  "v2_verdict": gate_v2["verdict"],
                  "v2_gate_legs": gate_v2["gate_legs"],
                  "s1_increment": gate_s1["increment"],
                  "s1_verdict": gate_s1["verdict"]}, indent=1))
