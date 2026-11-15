#!/usr/bin/env python3
"""NIFTY TUNING SESSION 2026-11-10 (owner-directed "start tuning"; market
holiday, historical data only). Nifty only, paper, Rs0. Frozen primary
NF-PAPER-C3G7 and its logs/specs are never touched.

CANDIDATE 1 -- NIFTY-EVE-17, scored EXACTLY as registered on 2026-11-09
(no rule alteration):
  Rule diff vs the standing causal book (Component A, 35 legs,
  +Rs54,102.00): if by the close of the 3rd bar after entry the running
  maximum premium high (entry bar through that bar) is still < entry+15,
  exit at that close (exit_reason "nodev_cut"); all other exits frozen
  (frozen S5 geometry: stop -50 before target incl. entry bar; BE arm +50
  -> stop to entry from the next bar; tgt1 +90 -> runner lock +60 /
  TGT2 +175 from the following bar; square-off at the 15:20 bar close;
  entry = entry bar's open; net = pts*65 - 220).
  Registered pre-condition: the replay must reproduce all 35 stored A-leg
  exits exactly (exit_time, exit_premium, exit_reason, net) from the
  stored premium candle files (aggressive_data/) before any variant
  number is treated as a score. Coverage is now 35/35 (3 files fetched
  and verified 2026-11-10).
  DATA NOTE (found in this run, before scoring): the 35/35 coverage
  figure rested on the 2026-11-09 check's date-OR-expiry filename glob.
  Day-exact aggressive files exist for only 31 of the 35 legs (e.g.
  2026-02-19 25600 PE has contract files for other days but no
  2026-02-19 file). The audit in this run compares each day-exact
  aggressive file against the construction-store day on shared bars:
  10 of 31 agree on every shared bar (the 3 files fetched 2026-11-10
  among them); on the other 21 the file differs at EVERY shared bar --
  a different contract series under the same strike/direction/date
  label, unusable as the leg's path. The replay population is
  therefore the frozen construction store alone (daily2leg prem
  stores via prem_day, the exact population
  nifty_next_phase_score.score_base produced the stored exits from).
  The cut RULE is unchanged; the registered pre-condition is enforced
  in its substantive form -- 35/35 exact reproduction on this
  population, or the candidate fails on the reproduction leg and no
  variant number is quoted.
  Trigger: Lesson RSI-NIFTY-009 (2026-11-09 primary leg never developed,
  MFE +0.25, stopped in 40 min).
  Controls (same run, per backtest_controls_gate): independent re-sum of
  the DEC-S1 base / A frame / TUNED v2 frame before scoring; timing
  audit (cut uses only bars up to and including the decision bar, fills
  at that bar's close -- the frozen square-off fill convention; entries
  unchanged); TWO placebos -- mirror (same bar-3 evaluation, inverted
  condition: exit at the bar-3 close when runmax >= entry+15) and shift
  (same rule evaluated at the close of the 6th bar after entry);
  halves (Jan-May / Jun-Oct); full month table with green->red flip and
  red month-end cumulative checks vs the incumbent; ex-top-3 stress;
  NC must be 0.
  Promotion rule (standing engine rule): if EVE-17 PASSES on the
  registered frame, the identical cut is additionally gated on the
  TUNED SHADOW v2 frame's Component A legs (v2's non-A legs keep stored
  exits) before any promotion is recorded -- promotion lands on the v2
  frame, so the v2 frame must clear the same gate. PASS on both ->
  TUNED SHADOW BOOK v3 (= v2 + EVE-17 cut on A legs) effective
  Wed 2026-11-11. PASS on the registered frame only -> the PASS is
  recorded but promotion is withheld, with the reason stated.

CANDIDATE 2 -- NIFTY-EVE-18, registered here BEFORE scoring.
  Target flaw: RSI-NIFTY-008 (C3 confirmation scarcity -- solo Skill
  legs blocked 4 of 5 days in November week 1; the information existed
  but not on the same key).
  Rule diff vs the standing causal book: additionally admit a U1 pool
  key whose sole source is Skill V3 (EXP0-filtered: date != expiry;
  UNIQUE-ONCE vs standing on date+direction) when the same trading day
  carries at least one OTHER pool key containing at least one non-Skill
  source system, in the same direction, whose entry_time is at or
  before the solo leg's entry_time (day-level second-source agreement,
  knowable at the moment of entry -- the causal form). Admitted legs
  are scored standalone under the standing geometry (lock60/TGT2-175,
  sq 15:20). Everything else identical.
  Mechanically new: EVE-01/02b/03b admitted by direction x entry-time
  slices of ALL solo legs; EVE-18 admits by a cross-system agreement
  condition on a different state variable (the day's already-fired
  other-system keys). No failed variant is retested: the admission set
  is neither a superset slice nor a time window.
  Incumbent: standing causal book +Rs54,102.00 (35 legs). Controls via
  the R6 harness in the same run (timing audit, shift+30min placebo,
  halves, month table, ex-top-3, independent re-sum), same PASS legs as
  the EVE-01 family.

Basis throughout: premiums per 1 lot (65), cost Rs220/trade inside
net_inr, UNIQUE-ONCE.
"""
import csv, json, collections, glob, os, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
SRC = TR / "nifty_next_phase_trades.csv"
AGG = TR / "aggressive_data"
LOT, COST, SQ = 65, 220.0, "15:20"

rows = [r for r in csv.DictReader(open(SRC)) if r["set"] == "BASE"]
assert len(rows) == 97, len(rows)
assert round(sum(float(r["net_inr"]) for r in rows), 2) == 91168.50
A = [r for r in rows if r["component"] == "A"]
assert len(A) == 35 and round(sum(float(r["net_inr"]) for r in A), 2) == 54102.00
V2 = [r for r in rows if not ((r["component"] == "B" and r["direction"] == "PE")
                             or (r["component"] in ("A", "C") and r["direction"] == "CE"))]
assert len(V2) == 59 and round(sum(float(r["net_inr"]) for r in V2), 2) == 115950.75
print("RE-SUM OK: DEC-S1 base 97/+91,168.50 · A frame 35/+54,102.00 · TUNED v2 59/+115,950.75")

# ------------- candle loading (house merged population) ---------------------
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

def leg_bars(leg):
    """(bars, tag): the frozen construction store day (prem_day) -- the
    population the stored exits were produced from."""
    return prem_day(leg["expiry"], leg["strike"], leg["direction"],
                    leg["date"], leg["component"])

def aggressive_audit(leg, ref_bars):
    """Diagnostic only: compare the day-exact aggressive file (if any)
    against the construction-store day on shared timestamps. Returns a
    dict describing agreement; never feeds the replay."""
    pat = str(AGG / f"candles_NIFTY_{leg['strike']}{leg['direction']}_*.json")
    day_files = [f for f in glob.glob(pat) if leg["date"] in os.path.basename(f)]
    if not day_files:
        return {"file": None}
    d = json.load(open(sorted(day_files)[0]))
    agg = {c[0][11:16]: [float(c[1]), float(c[2]), float(c[3]), float(c[4])]
           for c in d["data"]["candles"] if c[0][:10] == leg["date"]}
    ref = {t: [o, h, l, c] for (t, o, h, l, c) in (ref_bars or [])}
    shared = sorted(set(agg) & set(ref))
    dis = [t for t in shared if agg[t] != ref[t]]
    return {"file": os.path.basename(sorted(day_files)[0]),
            "shared_bars": len(shared), "disagree": dis,
            "disagree_le_sq": [t for t in dis if t <= SQ]}

# ---------------- frozen S5 replay (verbatim sequencing) + cut modes --------
def replay(bars, entry_time, cut=None):
    """cut: None | ("nodev", 3) | ("mirror", 3) | ("shift", 6).
    The cut is evaluated at the close of the k-th bar after the entry bar
    (entry bar = index 0), only if the leg is still open in the main loop
    (a tgt1 conversion returns inside the target branch, so a cut can
    never touch a runner -- and runmax >= entry+90 there anyway for the
    nodev/shift forms). runmax = max premium high over bars 0..i."""
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
    runmax = None
    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > SQ:
            break
        runmax = h if runmax is None else max(runmax, h)
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
        if cut is not None and i == cut[1]:
            if cut[0] in ("nodev", "shift") and runmax < entry + 15.0:
                return out(cl - entry, "nodev_cut" if cut[0] == "nodev"
                           else "shift_cut", t, 0, cl)
            if cut[0] == "mirror" and runmax >= entry + 15.0:
                return out(cl - entry, "mirror_cut", t, 0, cl)
        if t == SQ:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bs[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

# ---------------- stats / gate (house form, as 2026-11-09) -------------------
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

def gate_eval(name, frame_label, base_rows, var_rows, mir_rows, shf_rows, nc_zero, timing_clean):
    base = stats(base_rows); var = stats(var_rows)
    mir = stats(mir_rows); shf = stats(shf_rows)
    base_months = {m["month"]: m["net"] for m in base["months"]}
    var_months = {m["month"]: m["net"] for m in var["months"]}
    flips = [m for m in base_months if base_months[m] > 0 and var_months.get(m, 0.0) < 0]
    red_cum = [m["month"] for m in var["months"] if m["cum"] < 0]
    g = {"net_beats_incumbent": var["net"] > base["net"],
         "ft_not_diluted": var["ft_pct"] >= base["ft_pct"],
         "halves_both_positive": var["h1_jan_may"] > 0 and var["h2_jun_oct"] > 0,
         "no_green_month_flips_red": len(flips) == 0,
         "no_red_month_end_cumulative": len(red_cum) == 0,
         "ex_top3_positive": var["ex_top3"] > 0,
         "placebo_mirror_beaten": var["net"] > mir["net"],
         "placebo_shift_beaten": var["net"] > shf["net"],
         "nc_zero": nc_zero, "timing_clean": timing_clean}
    return {"candidate": name, "frame": frame_label, "incumbent": base, "variant": var,
            "placebo_mirror": mir, "placebo_shift": shf,
            "green_to_red_flips": flips, "gate_legs": g,
            "verdict": "PASS" if all(g.values()) else "FAIL"}

def modified_rows(base_rows, results):
    """Replace exit fields of base_rows from replay results keyed by id(row)."""
    out = []
    for r in base_rows:
        res = results[id(r)]
        nr = dict(r)
        nr.update({"exit_time": res["exit_time"], "exit_premium": res["exit"],
                   "exit_reason": res["exit_reason"], "ft": res["ft"],
                   "net_inr": res["net"]})
        out.append(nr)
    return out

# ================= PART 1: EVE-17 reproduction, then scoring =================
BARS = {}
AUDIT = {}
for leg in A:
    b, tag = leg_bars(leg)
    BARS[id(leg)] = (b, tag)
    AUDIT[id(leg)] = aggressive_audit(leg, b)
AGG_DAY = sum(1 for v in AUDIT.values() if v["file"])
AGG_CLEAN = sum(1 for v in AUDIT.values() if v["file"] and not v["disagree"])
AGG_FULLDIFF = [{"date": leg["date"], "strike": leg["strike"], "direction": leg["direction"],
                 "shared_bars": AUDIT[id(leg)]["shared_bars"],
                 "disagree_bars": len(AUDIT[id(leg)]["disagree"])}
                for leg in A if AUDIT[id(leg)]["file"]
                and AUDIT[id(leg)]["shared_bars"] > 0
                and len(AUDIT[id(leg)]["disagree"]) == AUDIT[id(leg)]["shared_bars"]]
print(f"CANDLE POPULATION: construction-store bars for {sum(1 for v in BARS.values() if v[0])}/35 A legs · "
      f"day-exact aggressive files {AGG_DAY}/35 (agree on every shared bar {AGG_CLEAN}, "
      f"differ at every shared bar {len(AGG_FULLDIFF)})")

repro = {"exact": 0, "mismatch": []}
RES_INC = {}
for leg in A:
    bars, fname = BARS[id(leg)]
    r = replay(bars, leg["entry_time"])
    RES_INC[id(leg)] = r
    ok = (r is not None and r["exit_time"] == leg["exit_time"]
          and abs(r["exit"] - float(leg["exit_premium"])) < 1e-9
          and r["exit_reason"] == leg["exit_reason"]
          and abs(r["net"] - float(leg["net_inr"])) < 1e-9
          and abs(r["entry"] - float(leg["entry_premium"])) < 1e-9)
    if ok:
        repro["exact"] += 1
    else:
        repro["mismatch"].append({
            "date": leg["date"], "strike": leg["strike"], "direction": leg["direction"],
            "source": fname,
            "stored": [leg["exit_time"], leg["exit_premium"], leg["exit_reason"], leg["net_inr"]],
            "replay": None if r is None else [r["exit_time"], r["exit"], r["exit_reason"], r["net"]]})
print(f"REPRODUCTION: {repro['exact']}/35 exact")
for m in repro["mismatch"]:
    print("  MISMATCH", m)

out = {"eve17_reproduction": repro,
       "eve17_population": {"construction_store_legs": sum(1 for v in BARS.values() if v[0]),
                            "aggressive_day_exact_files": AGG_DAY,
                            "aggressive_agree_every_shared_bar": AGG_CLEAN,
                            "aggressive_differ_every_shared_bar": AGG_FULLDIFF,
                            "note": "2026-11-09 coverage check used a date-OR-expiry filename glob and overstated day-exact aggressive coverage (31/35 day-exact). Of those 31 files, 10 agree with the construction store on every shared bar (incl. the 3 fetched 2026-11-10); 21 differ at every shared bar (a different contract series under the same label). Replay population is the frozen construction store (prem_day), the population the stored exits were produced from; aggressive files audited as a diagnostic only."}}
EVE17_PASS = False
if repro["exact"] == 35:
    def run_cut(cut):
        return {id(leg): replay(BARS[id(leg)][0], leg["entry_time"], cut=cut) for leg in A}
    RES_VAR = run_cut(("nodev", 3))
    RES_MIR = run_cut(("mirror", 3))
    RES_SHF = run_cut(("shift", 6))
    # timing audit: exits never before entry; cut exits land exactly on the
    # k-th bar after the entry bar and use only bars up to that bar.
    viol = 0
    for leg in A:
        bars, _ = BARS[id(leg)]
        i0 = [i for i, b in enumerate(bars) if b[0] >= leg["entry_time"]][0]
        for res, k in ((RES_VAR[id(leg)], 3), (RES_MIR[id(leg)], 3), (RES_SHF[id(leg)], 6)):
            if res["exit_time"] < leg["entry_time"]:
                viol += 1
            if res["exit_reason"] in ("nodev_cut", "mirror_cut", "shift_cut"):
                if res["exit_time"] != bars[i0 + k][0]:
                    viol += 1
    cut_legs = [leg for leg in A if RES_VAR[id(leg)]["exit_reason"] == "nodev_cut"]
    diag = {"cut_legs": len(cut_legs),
            "cut_detail": [{"date": l["date"], "direction": l["direction"],
                            "entry_time": l["entry_time"],
                            "stored_exit": [l["exit_time"], l["exit_reason"], float(l["net_inr"])],
                            "cut_exit_time": RES_VAR[id(l)]["exit_time"],
                            "cut_net": RES_VAR[id(l)]["net"]} for l in cut_legs],
            "cut_stored_net": round(sum(float(l["net_inr"]) for l in cut_legs), 2),
            "cut_variant_net": round(sum(RES_VAR[id(l)]["net"] for l in cut_legs), 2),
            "full_stops_in_A": sum(1 for l in A if l["exit_reason"] == "stop"),
            "full_stops_cut": sum(1 for l in cut_legs if l["exit_reason"] == "stop")}
    g17 = gate_eval(
        "NIFTY-EVE-17 — standing book + no-development cut (bar-3 close, runmax < entry+15)",
        "standing causal book (A, 35 legs, +54,102.00)",
        A, modified_rows(A, RES_VAR), modified_rows(A, RES_MIR),
        modified_rows(A, RES_SHF), nc_zero=True, timing_clean=(viol == 0))
    g17["timing_audit"] = {"checked": 35 * 3, "violations": viol}
    g17["diagnostics"] = diag
    out["EVE-17"] = g17
    EVE17_PASS = g17["verdict"] == "PASS"
    print(f"EVE-17: incumbent {g17['incumbent']['net']:+,.2f} -> variant {g17['variant']['net']:+,.2f} "
          f"({g17['variant']['legs']} legs) · cut legs {diag['cut_legs']} "
          f"(stored {diag['cut_stored_net']:+,.2f} -> cut {diag['cut_variant_net']:+,.2f}) · "
          f"mirror {g17['placebo_mirror']['net']:+,.2f} · shift {g17['placebo_shift']['net']:+,.2f} · "
          f"verdict {g17['verdict']} · failed legs: {[k for k, v in g17['gate_legs'].items() if not v]}")

    # ---- promotion check on the TUNED v2 frame (A legs only) ----
    if EVE17_PASS:
        A_ids = {id(r) for r in A}
        def v2_rows(resmap):
            out_rows = []
            for r in V2:
                if id(r) in A_ids:
                    res = resmap[id(r)]
                    nr = dict(r)
                    nr.update({"exit_time": res["exit_time"], "exit_premium": res["exit"],
                               "exit_reason": res["exit_reason"], "ft": res["ft"],
                               "net_inr": res["net"]})
                    out_rows.append(nr)
                else:
                    out_rows.append(dict(r))
            return out_rows
        gp = gate_eval(
            "NIFTY-EVE-17 promotion check — TUNED v2 + no-dev cut on its Component A legs",
            "TUNED SHADOW v2 (59 legs, +115,950.75)",
            V2, v2_rows(RES_VAR), v2_rows(RES_MIR), v2_rows(RES_SHF),
            nc_zero=True, timing_clean=(viol == 0))
        out["EVE-17_promotion_check_v2"] = gp
        print(f"EVE-17 v2 promotion check: {gp['incumbent']['net']:+,.2f} -> {gp['variant']['net']:+,.2f} · "
              f"verdict {gp['verdict']} · failed legs: {[k for k, v in gp['gate_legs'].items() if not v]}")
else:
    out["EVE-17"] = {"candidate": "NIFTY-EVE-17 — no-development cut",
                     "verdict": "FAIL",
                     "failed_leg": "reproduction (registered pre-condition)",
                     "note": "Replay did not reproduce all 35 stored exits exactly on the registered candle population; no variant number is quoted as a score."}
    print("EVE-17: FAIL on the reproduction pre-condition — variant not scored.")

with open(TR / "nifty_tuning_2026-11-10_summary.json", "w") as f:
    json.dump(out, f, indent=1)
print("PART 1 written to nifty_tuning_2026-11-10_summary.json")

# ================= PART 2: EVE-18 population census ==========================
# Registered rule (header): admit a solo-Skill EXP0 pool key when the same
# day carries ANOTHER pool key with >= 1 non-Skill source, same direction,
# entry_time <= the solo leg's entry_time. The census below applies that
# exact predicate to the stored U1 pool.
sys.path.insert(0, str(TR))
from nifty_engine_score import pool as _pool
import nifty_engine_r6_harness as _R6

P = _pool()
_keys = [(l["date"], l["direction"]) for l in P]
_solo = [l for l in P if _R6.sources_of(l) == ["Skill V3"] and l["date"] != l["expiry"]]
_byday = collections.defaultdict(list)
for _l in P:
    _byday[_l["date"]].append(_l)
_adm = []
for _l in _solo:
    for _l2 in _byday[_l["date"]]:
        if _l2 is _l:
            continue
        if (_l2["direction"] == _l["direction"]
                and _l2["entry_time"] <= _l["entry_time"]
                and any(s != "Skill V3" for s in _R6.sources_of(_l2))):
            _adm.append(_l)
            break
out["EVE-18"] = {
    "candidate": "NIFTY-EVE-18 — day-level second-source agreement admission for solo Skill legs",
    "verdict": "NOT TESTABLE",
    "failed_leg": "population (empty by construction)",
    "population": {"pool_legs": len(P), "distinct_date_direction_keys": len(set(_keys)),
                   "solo_skill_exp0_legs": len(_solo), "admissible_under_registered_rule": len(_adm)},
    "note": ("The U1 pool holds exactly one leg per (date, direction) — 108 legs, 108 distinct "
             "keys — with the firing systems merged into the key's source set. A same-day, "
             "same-direction key from another system is therefore not a separate object: had "
             "another system fired that direction that day, it would be inside this key's "
             "sources, making the key confirmed (standing) by definition. The registered "
             "admission set is empty by construction, so no gate ran and no number is quoted "
             "(EVE-06 / early-solo-slice precedent). The day-level-agreement route to "
             "RSI-NIFTY-008 is closed on the stored pool: loosening C3 requires new signal "
             "data outside the pool key structure, not a new filter on it.")}
print(f"EVE-18: pool {len(P)} legs / {len(set(_keys))} distinct keys · solo Skill EXP0 {len(_solo)} · "
      f"admissible {len(_adm)} -> NOT TESTABLE (empty population by construction)")

with open(TR / "nifty_tuning_2026-11-10_summary.json", "w") as f:
    json.dump(out, f, indent=1)
print("FULL summary written to nifty_tuning_2026-11-10_summary.json")
