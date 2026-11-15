#!/usr/bin/env python3
"""PREMIUM-TAPE — BANK NIFTY · ROUND 2: THE RETEST TURN.
Spec: premium_tape_bank_r2_SPEC.md (frozen 2026-11-14 before scoring).
Local stores only — NO API calls. Research only: reads the Round-1
machinery and stores; writes premium_tape_bank_r2_results.json +
premium_tape_bank_r2_2026-11-14.md + premium_tape_bank_r2_trades.csv
only. The control is asserted BEFORE any turn statistic is computed.
"""
import csv, json, random, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
LOT, COST = 30, 220.0
SEED = 20261114

# ---- reuse Round-1 machinery EXACTLY (definitions only; the Round-1
# main/scoring block is not executed) ----
_src = (TR / "premium_tape_bank_build.py").read_text()
_defs = _src.split("# ---------------- run a window ----------------")[0]
_ns = {"__name__": "premium_tape_bank_r1_defs", "__file__": str(TR / "premium_tape_bank_build.py")}
exec(compile(_defs, "premium_tape_bank_build.py(defs)", "exec"), _ns)

TIMES = _ns["TIMES"]; TIDX = _ns["TIDX"]
GATE_DAYS = _ns["GATE_DAYS"]; NOV_DAYS = _ns["NOV_DAYS"]
get_day = _ns["get_day"]; day_triggers = _ns["day_triggers"]
pick = _ns["pick"]; make_trade = _ns["make_trade"]; score_exit = _ns["score_exit"]

EVENT_LO = TIDX["09:50"]; EVENT_HI = TIDX["14:20"]
WATCH_HI = TIDX["14:25"]

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

# ---------------- CONTROL: Round-1 P1-X2, identical machinery ----------------
def control_book(days):
    out = []
    for day in days:
        trig, late = pick(day_triggers(day), "P1")
        if trig is None:
            continue
        tr = make_trade(day, trig, "X2")
        if tr is not None:
            out.append(tr)
    return out

ctrl_gate = control_book(GATE_DAYS)
ctrl_full = stats(ctrl_gate)
ctrl_jj = win_stats(ctrl_gate, "2026-01-01", "2026-06-30")
ctrl_jo = win_stats(ctrl_gate, "2026-07-01", "2026-10-31")
ctrl_nov = stats(control_book(NOV_DAYS))
CONTROL_EXPECTED = dict(trades=174, total=1791.00,
                        jj_trades=110, jj_total=33046.00,
                        jo_trades=64, jo_total=-31255.00)
control_ok = (ctrl_full["trades"] == CONTROL_EXPECTED["trades"] and
              ctrl_full["total"] == CONTROL_EXPECTED["total"] and
              ctrl_jj["trades"] == CONTROL_EXPECTED["jj_trades"] and
              ctrl_jj["total"] == CONTROL_EXPECTED["jj_total"] and
              ctrl_jo["trades"] == CONTROL_EXPECTED["jo_trades"] and
              ctrl_jo["total"] == CONTROL_EXPECTED["jo_total"])
control = dict(book="P1-X2 (Round 1)", reproduced=control_ok,
               full=ctrl_full, jan_jun=ctrl_jj, jul_oct=ctrl_jo, nov=ctrl_nov,
               expected=CONTROL_EXPECTED)
if not control_ok:
    print("CONTROL MISMATCH — turn NOT scored.")
    print(json.dumps(control, indent=1))
    sys.exit(1)
print(f"control: PASS (P1-X2 {ctrl_full['trades']} trades, "
      f"{ctrl_full['total']:+.2f}; Jan-Jun {ctrl_jj['trades']}/"
      f"{ctrl_jj['total']:+.2f}; Jul-Oct {ctrl_jo['trades']}/"
      f"{ctrl_jo['total']:+.2f})")

# ---------------- P-RET: events, watches, retests ----------------
def contract_retest(s):
    """First break event of the contract-day and its watch outcome.
    Returns dict(status, event_i, retest_i, expiry_reason)."""
    C, L, VW = s["C"], s["L"], s["VWAP"]
    event_i = None
    for i in range(EVENT_LO, EVENT_HI + 1):
        if C[i] > s["or_high"] and C[i] > VW[i]:
            event_i = i
            break
    if event_i is None:
        return dict(status="no_event", event_i=None, retest_i=None,
                    expiry_reason=None)
    end = min(event_i + 12, WATCH_HI)
    for j in range(event_i + 1, end + 1):
        if L[j] <= VW[j] and C[j] > VW[j]:
            return dict(status="retest", event_i=event_i, retest_i=j,
                        expiry_reason=None)
        if C[j] <= VW[j]:
            return dict(status="expired", event_i=event_i, retest_i=None,
                        expiry_reason="close_below_vwap")
    return dict(status="expired", event_i=event_i, retest_i=None,
                expiry_reason="window_end")

def run_window(days):
    trades = {"X1": [], "X2": []}
    candidates = []          # every completed contract retest
    counts = dict(days=len(days), side_nc_CE=0, side_nc_PE=0,
                  both_nc_days=0, break_events=0, completed_retests=0,
                  expired_close_below_vwap=0, expired_window_end=0,
                  no_event_contract_days=0,
                  events_by_side={"CE": 0, "PE": 0},
                  retests_by_side={"CE": 0, "PE": 0})
    for day in days:
        sides = get_day(day)
        if sides["CE"] is None:
            counts["side_nc_CE"] += 1
        if sides["PE"] is None:
            counts["side_nc_PE"] += 1
        if sides["CE"] is None and sides["PE"] is None:
            counts["both_nc_days"] += 1
            continue
        day_cands = []
        for typ in ("CE", "PE"):
            s = sides[typ]
            if s is None:
                continue
            r = contract_retest(s)
            if r["status"] == "no_event":
                counts["no_event_contract_days"] += 1
                continue
            counts["break_events"] += 1
            counts["events_by_side"][typ] += 1
            if r["status"] == "expired":
                counts[f"expired_{r['expiry_reason']}"] += 1
                continue
            counts["completed_retests"] += 1
            counts["retests_by_side"][typ] += 1
            cand = dict(date=day, side=typ, strike=s["strike"],
                        expiry=s["expiry"], src=s["src"],
                        vwap_mode=s["vwap_mode"],
                        event_time=TIMES[r["event_i"]],
                        event_i=r["event_i"],
                        retest_time=TIMES[r["retest_i"]],
                        retest_i=r["retest_i"],
                        touch_depth=round(s["VWAP"][r["retest_i"]] -
                                          s["L"][r["retest_i"]], 4))
            candidates.append(cand)
            day_cands.append(cand)
        if not day_cands:
            continue
        day_cands.sort(key=lambda c: (c["retest_i"], -c["touch_depth"],
                                      0 if c["side"] == "CE" else 1))
        chosen = day_cands[0]
        s = sides[chosen["side"]]
        for x in ("X1", "X2"):
            r = score_exit(s, chosen["retest_i"], x)
            if r is None:
                continue
            entry_px, exit_px, xt, reason = r
            trades[x].append(dict(
                book="P-RET", exit=x, date=day, side=chosen["side"],
                strike=chosen["strike"], expiry=chosen["expiry"],
                src=chosen["src"], vwap_mode=chosen["vwap_mode"],
                event_time=chosen["event_time"],
                retest_time=chosen["retest_time"],
                entry_time=TIMES[chosen["retest_i"] + 1],
                entry_px=entry_px, exit_time=xt, exit_px=exit_px,
                exit_reason=reason,
                net=round((exit_px - entry_px) * LOT - COST, 2)))
    return trades, counts, candidates

gate_trades, gcnt, gate_cands = run_window(GATE_DAYS)
nov_trades, ncnt, nov_cands = run_window(NOV_DAYS)

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

def audit(candidates, trades_by_exit):
    bad = []
    checked = 0
    for cand in candidates:
        s = get_day(cand["date"])[cand["side"]]
        ei, ri = cand["event_i"], cand["retest_i"]
        vw_e = recompute_vwap(s, ei)
        vw_r = recompute_vwap(s, ri)
        or_high = max(s["H"][:7])
        ok = (abs(or_high - s["or_high"]) < 1e-9 and
              abs(vw_e[ei] - s["VWAP"][ei]) < 1e-9 and
              abs(vw_r[ri] - s["VWAP"][ri]) < 1e-9 and
              s["C"][ei] > or_high and s["C"][ei] > vw_e[ei])
        # event must be the FIRST eligible break
        for i in range(EVENT_LO, ei):
            vw_i = vw_r[i]
            if s["C"][i] > or_high and s["C"][i] > vw_i:
                ok = False
        # watch: no fail before the retest; hold exactly at ri
        for j in range(ei + 1, ri):
            if s["C"][j] <= vw_r[j]:
                ok = False
            if s["L"][j] <= vw_r[j] and s["C"][j] > vw_r[j]:
                ok = False     # an earlier hold would have completed first
        ok = ok and s["L"][ri] <= vw_r[ri] and s["C"][ri] > vw_r[ri]
        ok = ok and ri <= min(ei + 12, WATCH_HI) and ri > ei
        checked += 1
        if not ok:
            bad.append((cand["date"], cand["side"], ei, ri))
    trade_checked = 0
    for x, trs in trades_by_exit.items():
        for t in trs:
            s = get_day(t["date"])[t["side"]]
            ri = TIDX[t["retest_time"]]
            ok = (t["entry_time"] == TIMES[ri + 1] and
                  abs(t["entry_px"] - s["O"][ri + 1]) < 1e-9)
            trade_checked += 1
            if not ok:
                bad.append((t["date"], t["side"], "entry", x))
    return bad, checked, trade_checked

bad, cand_checked, trade_checked = audit(
    gate_cands + nov_cands, {"gate_X1": gate_trades["X1"],
                             "gate_X2": gate_trades["X2"],
                             "nov_X1": nov_trades["X1"],
                             "nov_X2": nov_trades["X2"]})
if bad:
    print("TIMING AUDIT FAILED:", bad[:5])
    sys.exit(1)
timing_audit = (f"PASS ({cand_checked} completed retests re-verified from "
                f"truncated series; {trade_checked} trade entries re-checked)")
print(timing_audit)

# ---------------- results ----------------
results = {}
for x in ("X1", "X2"):
    results[f"P-RET-{x}"] = dict(
        full=stats(gate_trades[x]),
        jan_jun=win_stats(gate_trades[x], "2026-01-01", "2026-06-30"),
        jul_oct=win_stats(gate_trades[x], "2026-07-01", "2026-10-31"),
        nov=stats(nov_trades[x]))
best_book = max(("P-RET-X1", "P-RET-X2"),
                key=lambda b: results[b]["full"]["total"])
best_exit = best_book.split("-")[-1]
best_trades = gate_trades[best_exit]

# ---------------- placebo on the best exit row ----------------
scoreable_days = []
for d in GATE_DAYS:
    sides = get_day(d)
    ok = [typ for typ in ("CE", "PE") if sides[typ] is not None]
    if ok:
        scoreable_days.append((d, ok))
rng = random.Random(SEED)
entry_idxs = [i for i, t in enumerate(TIMES) if "09:20" <= t <= "15:15"]
p_totals, p_drops = [], 0
for _ in range(1000):
    tot = 0.0
    for _rt in best_trades:
        got = None
        for _a in range(51):
            d, oks = rng.choice(scoreable_days)
            typ = rng.choice(oks)
            ei = rng.choice(entry_idxs)
            r = score_exit(get_day(d)[typ], ei - 1, best_exit)
            if r is not None:
                got = (r[1] - r[0]) * LOT - COST
                break
        if got is None:
            p_drops += 1
        else:
            tot += got
    p_totals.append(round(tot, 2))
p_totals.sort()
real = results[best_book]["full"]["total"]
pct = round(100.0 * sum(1 for v in p_totals if v < real) / len(p_totals), 1)
placebo = dict(book=best_book, iterations=1000, percentile=pct,
               drops=p_drops, p50=p_totals[500], p95=p_totals[949],
               max=p_totals[-1])
print("placebo:", placebo)

out = dict(spec="premium_tape_bank_r2_SPEC.md",
           basis="paper, buying only, 1 lot (30), Rs220/trade",
           gate_days=len(GATE_DAYS), control=control,
           counts=gcnt, nov_counts=ncnt, timing_audit=timing_audit,
           books=results, best_book=best_book, placebo=placebo,
           candidates_gate=gate_cands, candidates_nov=nov_cands,
           trades={x: gate_trades[x] for x in ("X1", "X2")},
           nov_trades={x: nov_trades[x] for x in ("X1", "X2")})
json.dump(out, open(TR / "premium_tape_bank_r2_results.json", "w"), indent=1)
with open(TR / "premium_tape_bank_r2_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["book", "exit", "date", "side", "strike", "expiry", "src",
                "vwap_mode", "event_time", "retest_time", "entry_time",
                "entry_px", "exit_time", "exit_px", "exit_reason", "net"])
    for x in ("X1", "X2"):
        for t in gate_trades[x]:
            w.writerow([t["book"], t["exit"], t["date"], t["side"],
                        t["strike"], t["expiry"], t["src"], t["vwap_mode"],
                        t["event_time"], t["retest_time"], t["entry_time"],
                        t["entry_px"], t["exit_time"], t["exit_px"],
                        t["exit_reason"], t["net"]])

# ---------------- markdown report ----------------
def row(label, s):
    return (f"| {label} | {s['trades']} | {s['total']:+,.2f} | "
            f"{s['wr']:.1f}% | {s['per_td']:+,.2f} |")

lines = []
lines.append("# PREMIUM-TAPE — BANK NIFTY · ROUND 2: THE RETEST TURN · RESULTS · 2026-11-14")
lines.append("")
lines.append("Spec frozen before scoring: `premium_tape_bank_r2_SPEC.md`. "
             "Build: `premium_tape_bank_r2_build.py`. Numbers: "
             "`premium_tape_bank_r2_results.json`, trades: "
             "`premium_tape_bank_r2_trades.csv`. Research only — no book, "
             "ledger or job changed. Paper only, real money Rs0. Buying "
             "only, 1 lot (30), Rs220/trade. Signals come off each "
             "selected contract's OWN premium candles (CE and PE of the "
             "strike nearest spot at 09:15, fixed for the day), identical "
             "data and contract selection to Round 1.")
lines.append("")
lines.append("## Control — Round-1 P1-X2 reproduced exactly")
lines.append("")
lines.append(f"**PASS** — {ctrl_full['trades']} trades, "
             f"{ctrl_full['total']:+,.2f} full Jan–Oct "
             f"(Jan–Jun {ctrl_jj['trades']} trades / {ctrl_jj['total']:+,.2f}; "
             f"Jul–Oct {ctrl_jo['trades']} trades / {ctrl_jo['total']:+,.2f}; "
             f"November {ctrl_nov['trades']} trades / {ctrl_nov['total']:+,.2f}). "
             "The turn below was scored only after this reproduction.")
lines.append("")
lines.append("## Coverage / NC")
lines.append("")
lines.append(f"- Gate days: {gcnt['days']}. Side NC: CE {gcnt['side_nc_CE']} days, "
             f"PE {gcnt['side_nc_PE']} days; both-sides-NC days {gcnt['both_nc_days']}.")
lines.append(f"- November days: {ncnt['days']}. Side NC: CE {ncnt['side_nc_CE']} days, "
             f"PE {ncnt['side_nc_PE']} days; both-sides-NC days {ncnt['both_nc_days']}.")
lines.append("")
lines.append("## Selectivity — break events vs completed retests (contract-days)")
lines.append("")
lines.append("| Window | Break events | Completed retests | Expired: close below VWAP | Expired: window end | No-event contract-days |")
lines.append("|---|---|---|---|---|---|")
lines.append(f"| Gate Jan–Oct | {gcnt['break_events']} | {gcnt['completed_retests']} | "
             f"{gcnt['expired_close_below_vwap']} | {gcnt['expired_window_end']} | "
             f"{gcnt['no_event_contract_days']} |")
lines.append(f"| November CF | {ncnt['break_events']} | {ncnt['completed_retests']} | "
             f"{ncnt['expired_close_below_vwap']} | {ncnt['expired_window_end']} | "
             f"{ncnt['no_event_contract_days']} |")
lines.append("")
lines.append(f"Gate events by side: CE {gcnt['events_by_side']['CE']}, "
             f"PE {gcnt['events_by_side']['PE']}; completed retests by side: "
             f"CE {gcnt['retests_by_side']['CE']}, PE {gcnt['retests_by_side']['PE']}.")
lines.append("")
lines.append("## Results — P-RET")
lines.append("")
lines.append("| Window — exit | Trades | Net Rs | WR | Rs/trade-day |")
lines.append("|---|---|---|---|---|")
for x in ("X1", "X2"):
    r = results[f"P-RET-{x}"]
    lines.append(row(f"Full Jan–Oct — {x}", r["full"]))
    lines.append(row(f"Jan–Jun — {x}", r["jan_jun"]))
    lines.append(row(f"Jul–Oct — {x}", r["jul_oct"]))
lines.append("")
lines.append("## November CF (descriptive, Nov 2–13)")
lines.append("")
lines.append("| Exit | Trades | Net Rs | WR | Rs/trade-day |")
lines.append("|---|---|---|---|---|")
for x in ("X1", "X2"):
    s = results[f"P-RET-{x}"]["nov"]
    lines.append(f"| {x} | {s['trades']} | {s['total']:+,.2f} | "
                 f"{s['wr']:.1f}% | {s['per_td']:+,.2f} |")
lines.append("")
lines.append("## Timing audit")
lines.append("")
lines.append(f"**{timing_audit}** — premium opening-range high and premium VWAP "
             "recomputed from each contract-day series truncated at the event "
             "and retest bars by an independent code path; the first-break, "
             "watch and hold conditions re-asserted; every scored trade's "
             "entry is exactly the bar after its retest bar at that bar's "
             "stored open.")
lines.append("")
lines.append("## Placebo (best full-year exit row)")
lines.append("")
lines.append(f"Best row: **{best_book}** ({real:+,.2f}). Random-entry placebo "
             f"(1,000 iterations, same trade count, random scoreable day/side/"
             f"entry bar, same exit): real total at the **{pct:.1f}th "
             f"percentile** (placebo median {p_totals[500]:+,.2f}, "
             f"p95 {p_totals[949]:+,.2f}, max {p_totals[-1]:+,.2f}; "
             f"drops {p_drops}).")
lines.append("")
(TR / "premium_tape_bank_r2_2026-11-14.md").write_text("\n".join(lines))

print(json.dumps({bk: results[bk]["full"] for bk in results}, indent=1))
print("counts:", json.dumps(gcnt))
print("nov:", json.dumps({bk: results[bk]["nov"] for bk in results}, indent=1))
print("best:", best_book)
