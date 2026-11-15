#!/usr/bin/env python3
"""PREMIUM-TAPE — BANK NIFTY · ROUND 3: WIDEN THE RETEST.
Spec: premium_tape_bank_r3_SPEC.md (frozen 2026-11-14 before scoring).
Local stores only — NO API calls. Research only: reads the Round-1
machinery and stores; writes premium_tape_bank_r3_results.json +
premium_tape_bank_r3_2026-11-14.md + premium_tape_bank_r3_trades.csv
only. The CONTROL (Round-2 P-RET-X1) is asserted BEFORE any step
statistic is computed. X1 exits only.
"""
import csv, json, random, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
LOT, COST = 30, 220.0
SEED = 20261114

# ---- reuse Round-1 machinery EXACTLY (definitions only) ----
_src = (TR / "premium_tape_bank_build.py").read_text()
_defs = _src.split("# ---------------- run a window ----------------")[0]
_ns = {"__name__": "premium_tape_bank_r1_defs",
       "__file__": str(TR / "premium_tape_bank_build.py")}
exec(compile(_defs, "premium_tape_bank_build.py(defs)", "exec"), _ns)

TIMES = _ns["TIMES"]; TIDX = _ns["TIDX"]
GATE_DAYS = _ns["GATE_DAYS"]; NOV_DAYS = _ns["NOV_DAYS"]
get_day = _ns["get_day"]; score_exit = _ns["score_exit"]

EVENT_LO = TIDX["09:50"]; EVENT_HI = TIDX["14:20"]
WATCH_HI = TIDX["14:25"]
W60, W120 = 12, 24          # watch bars: 60 / 120 minutes

# ---------------- stats ----------------
def stats(trades):
    n = len(trades)
    wins = sum(1 for t in trades if t["net"] > 0)
    total = round(sum(t["net"] for t in trades), 2)
    tdays = len(set(t["date"] for t in trades))
    months = {}
    for t in trades:
        months[t["date"][:7]] = round(months.get(t["date"][:7], 0.0) + t["net"], 2)
    return dict(trades=n, wins=wins,
                wr=round(100.0 * wins / n, 1) if n else 0.0,
                total=total, trade_days=tdays,
                per_td=round(total / tdays, 2) if tdays else 0.0,
                months=dict(sorted(months.items())))

def win_stats(trades, lo, hi):
    return stats([t for t in trades if lo <= t["date"] <= hi])

# ---------------- generalized retest search ----------------
def find_retest(s, start_i, watch_bars):
    """First break event at/after start_i (and >= EVENT_LO, <= EVENT_HI)
    and its watch outcome under watch_bars. Mirrors Round-2 semantics."""
    C, L, VW = s["C"], s["L"], s["VWAP"]
    lo = max(start_i, EVENT_LO)
    event_i = None
    for i in range(lo, EVENT_HI + 1):
        if C[i] > s["or_high"] and C[i] > VW[i]:
            event_i = i
            break
    if event_i is None:
        return dict(status="no_event", event_i=None, retest_i=None,
                    expiry_reason=None)
    end = min(event_i + watch_bars, WATCH_HI)
    for j in range(event_i + 1, end + 1):
        if L[j] <= VW[j] and C[j] > VW[j]:
            return dict(status="retest", event_i=event_i, retest_i=j,
                        expiry_reason=None)
        if C[j] <= VW[j]:
            return dict(status="expired", event_i=event_i, retest_i=None,
                        expiry_reason="close_below_vwap")
    return dict(status="expired", event_i=event_i, retest_i=None,
                expiry_reason="window_end")

def make_x1_trade(day, cand, leg):
    s = get_day(day)[cand["side"]]
    r = score_exit(s, cand["retest_i"], "X1")
    if r is None:
        return None
    entry_px, exit_px, xt, reason = r
    return dict(step=cand["step"], leg=leg, date=day, side=cand["side"],
                strike=s["strike"], expiry=s["expiry"], src=s["src"],
                vwap_mode=s["vwap_mode"],
                event_time=TIMES[cand["event_i"]],
                retest_time=TIMES[cand["retest_i"]],
                entry_time=TIMES[cand["retest_i"] + 1],
                entry_px=entry_px, exit_time=xt, exit_px=exit_px,
                exit_reason=reason,
                net=round((exit_px - entry_px) * LOT - COST, 2))

def first_pass(day, sides, watch_bars, step_name, cnt, audit_recs):
    """Control/A first pass: per-contract first event + watch; day
    candidates returned (all completed retests)."""
    day_cands = []
    for typ in ("CE", "PE"):
        s = sides[typ]
        if s is None:
            continue
        r = find_retest(s, EVENT_LO, watch_bars)
        if r["status"] == "no_event":
            cnt["no_event_contract_days"] += 1
            continue
        cnt["break_events"] += 1
        cnt["events_by_side"][typ] += 1
        if r["status"] == "expired":
            cnt[f"expired_{r['expiry_reason']}"] += 1
            continue
        cnt["completed_retests"] += 1
        cnt["retests_by_side"][typ] += 1
        cand = dict(step=step_name, pass_no=1, date=day, side=typ,
                    search_start=EVENT_LO, watch_bars=watch_bars,
                    event_i=r["event_i"], retest_i=r["retest_i"],
                    touch_depth=round(s["VWAP"][r["retest_i"]] -
                                      s["L"][r["retest_i"]], 4))
        audit_recs.append(cand)
        day_cands.append(cand)
    return day_cands

def second_pass(day, sides, watch_bars, step_name, exit_i, cnt, audit_recs):
    """Steps B/C: per-contract first NEW event strictly after the first
    trade's exit bar; day candidates returned."""
    day_cands = []
    for typ in ("CE", "PE"):
        s = sides[typ]
        if s is None:
            continue
        r = find_retest(s, exit_i + 1, watch_bars)
        if r["status"] == "no_event":
            continue
        cnt["second_events"] += 1
        if r["status"] == "expired":
            cnt[f"second_expired_{r['expiry_reason']}"] += 1
            continue
        cnt["second_completed_retests"] += 1
        cand = dict(step=step_name, pass_no=2, date=day, side=typ,
                    search_start=exit_i + 1, watch_bars=watch_bars,
                    first_exit_i=exit_i,
                    event_i=r["event_i"], retest_i=r["retest_i"],
                    touch_depth=round(s["VWAP"][r["retest_i"]] -
                                      s["L"][r["retest_i"]], 4))
        audit_recs.append(cand)
        day_cands.append(cand)
    return day_cands

def choose(day_cands):
    if not day_cands:
        return None
    return sorted(day_cands,
                  key=lambda c: (c["retest_i"], -c["touch_depth"],
                                 0 if c["side"] == "CE" else 1))[0]

def new_counts(ndays):
    return dict(days=ndays, side_nc_CE=0, side_nc_PE=0, both_nc_days=0,
                break_events=0, completed_retests=0,
                expired_close_below_vwap=0, expired_window_end=0,
                no_event_contract_days=0,
                events_by_side={"CE": 0, "PE": 0},
                retests_by_side={"CE": 0, "PE": 0},
                days_with_trade1=0, second_events=0,
                second_completed_retests=0,
                second_expired_close_below_vwap=0,
                second_expired_window_end=0, second_trades=0)

def run_config(days, watch_bars, two_trades, step_name):
    """Returns (trades, counts, audit_records)."""
    trades, audit_recs = [], []
    cnt = new_counts(len(days))
    for day in days:
        sides = get_day(day)
        if sides["CE"] is None:
            cnt["side_nc_CE"] += 1
        if sides["PE"] is None:
            cnt["side_nc_PE"] += 1
        if sides["CE"] is None and sides["PE"] is None:
            cnt["both_nc_days"] += 1
            continue
        c1 = choose(first_pass(day, sides, watch_bars, step_name, cnt,
                               audit_recs))
        if c1 is None:
            continue
        t1 = make_x1_trade(day, c1, leg=1)
        if t1 is None:
            continue
        trades.append(t1)
        cnt["days_with_trade1"] += 1
        if not two_trades:
            continue
        exit_i = TIDX[t1["exit_time"]]
        c2 = choose(second_pass(day, sides, watch_bars, step_name,
                                exit_i, cnt, audit_recs))
        if c2 is None:
            continue
        t2 = make_x1_trade(day, c2, leg=2)
        if t2 is None:
            continue
        trades.append(t2)
        cnt["second_trades"] += 1
    return trades, cnt, audit_recs

# ---------------- CONTROL: Round-2 P-RET-X1 (60-min, 1 trade/day) ----------------
ctrl_gate, ctrl_gcnt, ctrl_audit = run_config(GATE_DAYS, W60, False, "CONTROL")
ctrl_full = stats(ctrl_gate)
ctrl_jj = win_stats(ctrl_gate, "2026-01-01", "2026-06-30")
ctrl_jo = win_stats(ctrl_gate, "2026-07-01", "2026-10-31")
ctrl_nov_trades, ctrl_ncnt, ctrl_nov_audit = run_config(NOV_DAYS, W60, False,
                                                       "CONTROL")
ctrl_nov = stats(ctrl_nov_trades)
CONTROL_EXPECTED = dict(trades=46, total=12132.50, wr=47.8,
                        jj_trades=28, jj_total=5724.50,
                        jo_trades=18, jo_total=6408.00,
                        gate_events=199, gate_retests=49)
control_ok = (ctrl_full["trades"] == CONTROL_EXPECTED["trades"] and
              ctrl_full["total"] == CONTROL_EXPECTED["total"] and
              ctrl_full["wr"] == CONTROL_EXPECTED["wr"] and
              ctrl_jj["trades"] == CONTROL_EXPECTED["jj_trades"] and
              ctrl_jj["total"] == CONTROL_EXPECTED["jj_total"] and
              ctrl_jo["trades"] == CONTROL_EXPECTED["jo_trades"] and
              ctrl_jo["total"] == CONTROL_EXPECTED["jo_total"] and
              ctrl_gcnt["break_events"] == CONTROL_EXPECTED["gate_events"] and
              ctrl_gcnt["completed_retests"] == CONTROL_EXPECTED["gate_retests"])
control = dict(book="P-RET-X1 (Round 2)", reproduced=control_ok,
               full=ctrl_full, jan_jun=ctrl_jj, jul_oct=ctrl_jo,
               nov=ctrl_nov, counts=ctrl_gcnt, nov_counts=ctrl_ncnt,
               expected=CONTROL_EXPECTED)
if not control_ok:
    print("CONTROL MISMATCH — steps NOT scored.")
    print(json.dumps(control, indent=1))
    sys.exit(1)
print(f"control: PASS (P-RET-X1 {ctrl_full['trades']} trades, "
      f"{ctrl_full['total']:+.2f}, WR {ctrl_full['wr']}; Jan-Jun "
      f"{ctrl_jj['trades']}/{ctrl_jj['total']:+.2f}; Jul-Oct "
      f"{ctrl_jo['trades']}/{ctrl_jo['total']:+.2f}; events "
      f"{ctrl_gcnt['break_events']}, retests {ctrl_gcnt['completed_retests']})")

# ---------------- STEPS ----------------
CONFIGS = [("A", W120, False), ("B", W60, True), ("C", W120, True)]
step_data = {}
all_audit = list(ctrl_audit) + list(ctrl_nov_audit)
all_trades = {"CONTROL": ctrl_gate}
for name, wb, two in CONFIGS:
    gt, gc, ga = run_config(GATE_DAYS, wb, two, name)
    nt, nc, na = run_config(NOV_DAYS, wb, two, name)
    step_data[name] = dict(
        watch_bars=wb, two_trades=two,
        full=stats(gt), jan_jun=win_stats(gt, "2026-01-01", "2026-06-30"),
        jul_oct=win_stats(gt, "2026-07-01", "2026-10-31"),
        nov=stats(nt), counts=gc, nov_counts=nc)
    all_audit += ga + na
    all_trades[name] = gt
    print(f"step {name}: {step_data[name]['full']['trades']} trades, "
          f"{step_data[name]['full']['total']:+.2f}, "
          f"WR {step_data[name]['full']['wr']}")

# ---------------- timing audit (independent recomputation) ----------------
def recompute_vwap(s, upto):
    H, L, C, V = s["H"], s["L"], s["C"], s["V"]
    has_vol = s["vwap_mode"] == "volume"
    cum_pv = cum_v = cum_tp = 0.0
    vw = []
    for i in range(upto + 1):
        tp = (H[i] + L[i] + C[i]) / 3.0
        cum_tp += tp
        if has_vol:
            cum_pv += tp * V[i]; cum_v += V[i]
            vw.append(cum_pv / cum_v if cum_v > 0 else tp)
        else:
            vw.append(cum_tp / (i + 1))
    return vw

bad = []
checked = 0
for cand in all_audit:
    s = get_day(cand["date"])[cand["side"]]
    ei, ri = cand["event_i"], cand["retest_i"]
    start = max(cand["search_start"], EVENT_LO)
    vw_r = recompute_vwap(s, ri)
    or_high = max(s["H"][:7])
    ok = (abs(or_high - s["or_high"]) < 1e-9 and
          abs(vw_r[ei] - s["VWAP"][ei]) < 1e-9 and
          abs(vw_r[ri] - s["VWAP"][ri]) < 1e-9 and
          s["C"][ei] > or_high and s["C"][ei] > vw_r[ei] and
          EVENT_LO <= ei <= EVENT_HI and
          ri <= min(ei + cand["watch_bars"], WATCH_HI) and ri > ei and
          s["L"][ri] <= vw_r[ri] and s["C"][ri] > vw_r[ri])
    for i in range(start, ei):            # event = first break in range
        if s["C"][i] > or_high and s["C"][i] > vw_r[i]:
            ok = False
    for j in range(ei + 1, ri):           # no fail / no earlier hold
        if s["C"][j] <= vw_r[j]:
            ok = False
        if s["L"][j] <= vw_r[j] and s["C"][j] > vw_r[j]:
            ok = False
    if cand["pass_no"] == 2:
        ok = ok and ei > cand["first_exit_i"]
    checked += 1
    if not ok:
        bad.append((cand["step"], cand["date"], cand["side"], ei, ri))
trade_checked = 0
for name, trs in all_trades.items():
    for t in trs:
        s = get_day(t["date"])[t["side"]]
        ri = TIDX[t["retest_time"]]
        ok = (t["entry_time"] == TIMES[ri + 1] and
              abs(t["entry_px"] - s["O"][ri + 1]) < 1e-9)
        trade_checked += 1
        if not ok:
            bad.append((name, t["date"], t["side"], "entry"))
if bad:
    print("TIMING AUDIT FAILED:", bad[:5])
    sys.exit(1)
timing_audit = (f"PASS ({checked} completed retests re-verified from "
                f"truncated series across control + steps A/B/C, gate + "
                f"November; {trade_checked} gate trade entries re-checked)")
print(timing_audit)

# ---------------- placebo per step row (X1, fresh seed per row) ----------------
scoreable_days = []
for d in GATE_DAYS:
    sides = get_day(d)
    ok = [typ for typ in ("CE", "PE") if sides[typ] is not None]
    if ok:
        scoreable_days.append((d, ok))
entry_idxs = [i for i, t in enumerate(TIMES) if "09:20" <= t <= "15:15"]

def placebo(n_trades):
    rng = random.Random(SEED)
    totals, drops = [], 0
    for _ in range(1000):
        tot = 0.0
        for _rt in range(n_trades):
            got = None
            for _a in range(51):
                d, oks = rng.choice(scoreable_days)
                typ = rng.choice(oks)
                ei = rng.choice(entry_idxs)
                r = score_exit(get_day(d)[typ], ei - 1, "X1")
                if r is not None:
                    got = (r[1] - r[0]) * LOT - COST
                    break
            if got is None:
                drops += 1
            else:
                tot += got
        totals.append(round(tot, 2))
    totals.sort()
    return totals, drops

placebos = {}
for name, _wb, _two in CONFIGS:
    real = step_data[name]["full"]["total"]
    n = step_data[name]["full"]["trades"]
    totals, drops = placebo(n)
    pct = round(100.0 * sum(1 for v in totals if v < real) / len(totals), 1)
    placebos[name] = dict(iterations=1000, percentile=pct, drops=drops,
                          p50=totals[500], p95=totals[949], max=totals[-1])
    print(f"placebo step {name}: {pct}th pct (n={n})")

# ---------------- desired-result bar ----------------
bar = {}
for name, _wb, _two in CONFIGS:
    d = step_data[name]
    ok = (d["jan_jun"]["total"] > 0 and d["jul_oct"]["total"] > 0 and
          placebos[name]["percentile"] >= 95.0 and
          d["full"]["total"] > CONTROL_EXPECTED["total"])
    bar[name] = dict(both_windows_positive=bool(d["jan_jun"]["total"] > 0
                                               and d["jul_oct"]["total"] > 0),
                     placebo_pct=placebos[name]["percentile"],
                     above_control=bool(d["full"]["total"] >
                                        CONTROL_EXPECTED["total"]),
                     clears_bar=bool(ok))
    print(f"bar step {name}: clears={ok}")

# ---------------- outputs ----------------
out = dict(spec="premium_tape_bank_r3_SPEC.md",
           basis="paper, buying only, 1 lot (30), Rs220/trade, X1 exits only",
           gate_days=len(GATE_DAYS), control=control, steps=step_data,
           placebos=placebos, desired_result_bar=bar,
           timing_audit=timing_audit,
           trades={k: v for k, v in all_trades.items()})
json.dump(out, open(TR / "premium_tape_bank_r3_results.json", "w"), indent=1)
with open(TR / "premium_tape_bank_r3_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["step", "leg", "date", "side", "strike", "expiry", "src",
                "vwap_mode", "event_time", "retest_time", "entry_time",
                "entry_px", "exit_time", "exit_px", "exit_reason", "net"])
    for name in ("CONTROL", "A", "B", "C"):
        for t in all_trades[name]:
            w.writerow([name, t["leg"], t["date"], t["side"], t["strike"],
                        t["expiry"], t["src"], t["vwap_mode"],
                        t["event_time"], t["retest_time"], t["entry_time"],
                        t["entry_px"], t["exit_time"], t["exit_px"],
                        t["exit_reason"], t["net"]])

# ---------------- markdown report ----------------
def row(label, s):
    return (f"| {label} | {s['trades']} | {s['total']:+,.2f} | "
            f"{s['wr']:.1f}% | {s['per_td']:+,.2f} |")

STEP_DESC = {
    "A": "Step A — window widened to 120 min (24 watch bars), 1 trade/day",
    "B": "Step B — 60-min window, second trade allowed after the first closes (max 2/day)",
    "C": "Step C — A+B combined: 120-min window + second trade (max 2/day)",
}
lines = []
lines.append("# PREMIUM-TAPE — BANK NIFTY · ROUND 3: WIDEN THE RETEST · RESULTS · 2026-11-14")
lines.append("")
lines.append("Spec frozen before scoring: `premium_tape_bank_r3_SPEC.md`. "
             "Build: `premium_tape_bank_r3_build.py`. Numbers: "
             "`premium_tape_bank_r3_results.json`, trades: "
             "`premium_tape_bank_r3_trades.csv`. Research only — no book, "
             "ledger or job changed. Paper only, real money Rs0. Buying "
             "only, 1 lot (30), Rs220/trade, X1 exits only (stop −50 / "
             "target +90, square-off 15:20). Signals come off each "
             "selected contract's OWN premium candles, identical data "
             "and contract selection to Rounds 1–2.")
lines.append("")
lines.append("## Control — Round-2 P-RET-X1 reproduced exactly")
lines.append("")
lines.append(f"**PASS** — {ctrl_full['trades']} trades, "
             f"{ctrl_full['total']:+,.2f} full Jan–Oct, WR {ctrl_full['wr']:.1f}% "
             f"(Jan–Jun {ctrl_jj['trades']} trades / {ctrl_jj['total']:+,.2f}; "
             f"Jul–Oct {ctrl_jo['trades']} trades / {ctrl_jo['total']:+,.2f}; "
             f"gate events {ctrl_gcnt['break_events']}, completed retests "
             f"{ctrl_gcnt['completed_retests']}; November {ctrl_nov['trades']} "
             f"trades / {ctrl_nov['total']:+,.2f}). Steps were scored only "
             "after this reproduction.")
lines.append("")
lines.append("## Coverage / NC")
lines.append("")
gc0 = ctrl_gcnt
lines.append(f"- Gate days: {gc0['days']}. Side NC: CE {gc0['side_nc_CE']} days, "
             f"PE {gc0['side_nc_PE']} days; both-sides-NC days {gc0['both_nc_days']} "
             "(identical for control and all steps — same selection).")
lines.append(f"- November days: {ctrl_ncnt['days']}. Side NC: CE "
             f"{ctrl_ncnt['side_nc_CE']} days, PE {ctrl_ncnt['side_nc_PE']} days; "
             f"both-sides-NC days {ctrl_ncnt['both_nc_days']}.")
lines.append("")
lines.append("## Selectivity — break events vs completed retests (contract-days)")
lines.append("")
lines.append("| Config | Window | Break events | Completed retests | Expired: close below VWAP | Expired: window end | No-event contract-days |")
lines.append("|---|---|---|---|---|---|---|")
lines.append(f"| Control (60m, 1/day) | Gate | {ctrl_gcnt['break_events']} | "
             f"{ctrl_gcnt['completed_retests']} | {ctrl_gcnt['expired_close_below_vwap']} | "
             f"{ctrl_gcnt['expired_window_end']} | {ctrl_gcnt['no_event_contract_days']} |")
for name, _wb, _two in CONFIGS:
    c = step_data[name]["counts"]
    lines.append(f"| {name} | Gate | {c['break_events']} | {c['completed_retests']} | "
                 f"{c['expired_close_below_vwap']} | {c['expired_window_end']} | "
                 f"{c['no_event_contract_days']} |")
lines.append(f"| Control (60m, 1/day) | November | {ctrl_ncnt['break_events']} | "
             f"{ctrl_ncnt['completed_retests']} | {ctrl_ncnt['expired_close_below_vwap']} | "
             f"{ctrl_ncnt['expired_window_end']} | {ctrl_ncnt['no_event_contract_days']} |")
for name, _wb, _two in CONFIGS:
    c = step_data[name]["nov_counts"]
    lines.append(f"| {name} | November | {c['break_events']} | {c['completed_retests']} | "
                 f"{c['expired_close_below_vwap']} | {c['expired_window_end']} | "
                 f"{c['no_event_contract_days']} |")
lines.append("")
lines.append("Second pass (Steps B/C, gate):")
lines.append("")
lines.append("| Config | Days with trade 1 | Second events | Completed second retests | Second expired: close below VWAP | Second expired: window end | Second trades taken |")
lines.append("|---|---|---|---|---|---|---|")
for name in ("B", "C"):
    c = step_data[name]["counts"]
    lines.append(f"| {name} | {c['days_with_trade1']} | {c['second_events']} | "
                 f"{c['second_completed_retests']} | "
                 f"{c['second_expired_close_below_vwap']} | "
                 f"{c['second_expired_window_end']} | {c['second_trades']} |")
lines.append("")
lines.append("## Results — X1 exits")
lines.append("")
lines.append("| Window | Trades | Net Rs | WR | Rs/trade-day |")
lines.append("|---|---|---|---|---|")
lines.append(row("Control — Full Jan–Oct", ctrl_full))
lines.append(row("Control — Jan–Jun", ctrl_jj))
lines.append(row("Control — Jul–Oct", ctrl_jo))
for name, _wb, _two in CONFIGS:
    d = step_data[name]
    lines.append(row(f"{name} — Full Jan–Oct", d["full"]))
    lines.append(row(f"{name} — Jan–Jun", d["jan_jun"]))
    lines.append(row(f"{name} — Jul–Oct", d["jul_oct"]))
lines.append("")
for name, _wb, _two in CONFIGS:
    lines.append(f"- **{name}**: {STEP_DESC[name]}.")
lines.append("")
lines.append("## November CF (descriptive, Nov 2–13)")
lines.append("")
lines.append("| Config | Trades | Net Rs | WR | Rs/trade-day |")
lines.append("|---|---|---|---|---|")
s = ctrl_nov
lines.append(f"| Control | {s['trades']} | {s['total']:+,.2f} | {s['wr']:.1f}% | {s['per_td']:+,.2f} |")
for name, _wb, _two in CONFIGS:
    s = step_data[name]["nov"]
    lines.append(f"| {name} | {s['trades']} | {s['total']:+,.2f} | {s['wr']:.1f}% | {s['per_td']:+,.2f} |")
lines.append("")
lines.append("## Timing audit")
lines.append("")
lines.append(f"**{timing_audit}** — premium opening-range high and premium "
             "VWAP recomputed from each contract-day series truncated at "
             "the event and retest bars by an independent code path; each "
             "event asserted as the first eligible break inside its search "
             "range; no fail and no earlier hold inside any watch; the "
             "watch-length bound and 14:25 cap asserted; second-pass "
             "events asserted strictly after the day's first-trade exit "
             "bar; every scored trade's entry is exactly the bar after "
             "its retest bar at that bar's stored open.")
lines.append("")
lines.append("## Placebo (random entry, X1, 1,000 draws × each row's trade count)")
lines.append("")
lines.append("| Config | Real total Rs | Percentile | Placebo median | Placebo p95 | Placebo max | Drops |")
lines.append("|---|---|---|---|---|---|---|")
for name, _wb, _two in CONFIGS:
    p = placebos[name]
    lines.append(f"| {name} | {step_data[name]['full']['total']:+,.2f} | "
                 f"{p['percentile']:.1f}th | {p['p50']:+,.2f} | "
                 f"{p['p95']:+,.2f} | {p['max']:+,.2f} | {p['drops']} |")
lines.append("")
lines.append("## Desired-result bar")
lines.append("")
lines.append("A step IS the channel only if ALL of: Jan–Jun net > 0 AND "
             "Jul–Oct net > 0 AND placebo percentile >= 95th AND full-year "
             "net above the control's +Rs12,132.50.")
lines.append("")
lines.append("| Config | Both windows positive | Placebo >= 95th | Above control | Clears the bar |")
lines.append("|---|---|---|---|---|")
for name, _wb, _two in CONFIGS:
    b = bar[name]
    lines.append(f"| {name} | {'YES' if b['both_windows_positive'] else 'no'} | "
                 f"{'YES' if b['placebo_pct'] >= 95.0 else 'no'} "
                 f"({b['placebo_pct']:.1f}th) | "
                 f"{'YES' if b['above_control'] else 'no'} | "
                 f"**{'YES' if b['clears_bar'] else 'NO'}** |")
lines.append("")
any_clear = [n for n, _w, _t in CONFIGS if bar[n]["clears_bar"]]
if any_clear:
    lines.append(f"**Step(s) clearing the bar: {', '.join(any_clear)}.**")
else:
    lines.append("**No step clears the bar — the Round-2 control "
                 "(P-RET-X1, 60-minute watch, one trade/day) stands.**")
lines.append("")
(TR / "premium_tape_bank_r3_2026-11-14.md").write_text("\n".join(lines))

print(json.dumps({n: step_data[n]["full"] for n, _w, _t in CONFIGS}, indent=1))
print("bar:", json.dumps(bar))
print("DONE")
