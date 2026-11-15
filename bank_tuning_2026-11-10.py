#!/usr/bin/env python3
"""BANK TUNING SESSION 2026-11-10 (owner-directed "start tuning"; market
holiday — historical gate run only). Paper only, real money Rs 0.
Basis: Bank Nifty option premiums per 1 lot (30), Rs 220/trade, UNIQUE-ONCE.
The frozen primary BNF-PAPER-V1 and its logs/specs are never touched.

CANDIDATE 1 — BANK-EVE-16: SHADOW v22 + BANK-EVE-06(a) re-entry gated as
ONE combined book vs SHADOW v22 alone (incumbent: 90 legs, +Rs 91,450.50,
Jan-Oct 2026). Recomputed from the stored Phase-1/Phase-2 CSVs on an
independent code path (no phase-2 scorer code reused for the gate numbers).

CANDIDATE 2 — BANK-EVE-17: first-3-bars close-stop on OR-break legs
(rep 'Skill V3', non-NS1 families) on the v22 frame. Registered in
november_rsi_candidates.md BEFORE this run. During the first 3 bars from
entry the -50 stop is enforced on bar closes only (exit at the close);
intrabar stop disabled inside the window; frozen v21 geometry from bar 4.
Tie-break: on a window bar the close-stop check precedes the trigger check.
Placebos: P1 same window on non-OR non-NS1 legs only; P2 window close-stop
level shifted to entry-70 on OR legs.

Incumbent rebuild for candidate 2 follows bank_v22_phase1_score.py exactly
(assemble6 + replay_overlay copied verbatim; fc2 overlay on NS1 legs =
EVE-04; EVE-05 skip on the leg set) and is asserted leg-for-leg against
the frozen r6 CSV and bank_v22_phase1_trades.csv before any variant is
scored. The Jan-Oct spot universe of bank_r3_setups is restricted to
<= 2026-10-31 (the store now also carries November dirs; the frozen
window is Jan-Oct — same restriction the phase-2 scorer applies to its
spot store).
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
LOT, COST, SQ = 30, 220.0, "15:20"
OUT = {"session": "bank_tuning_2026-11-10"}

def mins(t):
    h, m = map(int, str(t).split(":")[:2]); return h * 60 + m

def battery(rows, label):
    """rows: list of dicts with date + net. Programme-standard battery."""
    total = round(sum(r["net"] for r in rows), 2)
    months = {}
    for m in range(1, 11):
        mm = f"2026-{m:02d}"
        months[mm] = round(sum(r["net"] for r in rows if r["date"][:7] == mm), 2)
    H1 = round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2)
    H2 = round(total - H1, 2)
    top3l = sorted((r["net"] for r in rows), reverse=True)[:3]
    days = defaultdict(float)
    for r in rows: days[r["date"]] += r["net"]
    dnets = [round(v, 2) for _, v in sorted(days.items())]
    top3d = sorted(dnets, reverse=True)[:3]
    return dict(label=label, n_legs=len(rows), n_days=len(days), total=total,
                per_month=round(total / 10, 2),
                per_leg=round(total / len(rows), 2) if rows else 0.0,
                months=months, H1=H1, H2=H2,
                ex_top3_legs=round(total - sum(top3l), 2),
                ex_top3_days=round(total - sum(top3d), 2),
                worst_day=round(min(dnets), 2) if dnets else 0.0)

def green_flips(inc_months, var_months):
    return [m for m in inc_months if inc_months[m] > 0 and var_months[m] < 0]

# =====================================================================
# CANDIDATE 1 — BANK-EVE-16 (pure-CSV independent gate)
# =====================================================================
base16 = [{"date": r["date"], "net": float(r["net_inr"]),
           "exit_reason": r["exit_reason"], "exit_time": r["exit_time"],
           "entry_time": r["entry_time"]}
          for r in csv.DictReader(open(TR / "bank_v22_phase1_trades.csv"))]
assert len(base16) == 90 and round(sum(r["net"] for r in base16), 2) == 91450.50
inc = list(csv.DictReader(open(TR / "bank_v22_phase2_increments.csv")))
A = [{"date": r["date"], "net": float(r["net_inr"])} for r in inc if r["set"] == "A_reentry"]
A_legrows = [r for r in inc if r["set"] == "A_reentry"]
A_shift = [{"date": r["date"], "net": float(r["net_inr"])} for r in inc if r["set"] == "A_shift60"]
assert len(A) == 16 and round(sum(r["net"] for r in A), 2) == 6119.00
assert len(A_shift) == 15 and round(sum(r["net"] for r in A_shift), 2) == 1083.00

comb16 = base16 + A
plac16 = base16 + A_shift
b_inc = battery(base16, "v22 incumbent")
b_comb = battery(comb16, "v22+EVE06a combined")
b_plac = battery(plac16, "v22+shift60 placebo")
b_A = battery(A, "EVE06a increment")

# cross-validation: phase-2 combined trade file, non-sleeve rows == base + A
p2 = [r for r in csv.DictReader(open(TR / "bank_v22_phase2_trades.csv"))
      if r["family"] != "EVE06_SLEEVE"]
p2_sum = round(sum(float(r["net_inr"]) for r in p2), 2)
xval = dict(p2_nonsleeve_rows=len(p2), p2_nonsleeve_net=p2_sum,
            matches_combined=(len(p2) == len(comb16) and abs(p2_sum - b_comb["total"]) < 0.005))

# bleed on the Jan-Oct trading-day calendar (phase-2 method)
spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
DAYS = sorted(d for d in spot_raw if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
SPOT = {d: {b[0]: b for b in spot_raw[d]} for d in DAYS}
def bleed(rows):
    s = {d: 0.0 for d in DAYS}
    for r in rows: s[r["date"]] += r["net"]
    cal = [s[d] for d in DAYS]
    w3 = min(round(cal[i] + cal[i + 1] + cal[i + 2], 2) for i in range(len(cal) - 2))
    eq = peak = dd = 0.0
    for v in cal:
        eq += v; peak = max(peak, eq); dd = min(dd, eq - peak)
    legdays = {d: v for d, v in s.items() if any(r["date"] == d for r in rows)}
    wd = min(legdays.items(), key=lambda kv: kv[1])
    return dict(worst_day=[wd[0], round(wd[1], 2)], worst_3day=w3,
                worst_drawdown=round(dd, 2), pos_days=sum(1 for v in legdays.values() if v > 0))
bleed_inc, bleed_comb = bleed(base16), bleed(comb16)

# timing audit recomputed from CSVs + spot store
base_by_day = defaultdict(list)
for r in base16: base_by_day[r["date"]].append(r)
viol16 = []
for r in A_legrows:
    d = r["date"]
    if r["trigger_time"] < "12:00": viol16.append(("trigger_before_1200", d))
    stops = [x for x in base_by_day[d] if x["exit_reason"] == "stop"]
    if not stops: viol16.append(("no_stopped_base_leg", d))
    elif min(x["exit_time"] for x in stops) > r["trigger_time"]:
        viol16.append(("trigger_before_stop_exit", d))
    ts = sorted(SPOT[d])
    i = ts.index(r["trigger_time"])
    nxt = ts[i + 1] if i + 1 < len(ts) else None
    if nxt != r["entry_time"]: viol16.append(("entry_not_next_bar", d))
    if r["exit_time"] < r["entry_time"]: viol16.append(("exit_before_entry", d))
    ep, xp = float(r["entry_premium"]), float(r["exit_premium"])
    if r["exit_reason"] == "stop" and abs(xp - (ep - 50.0)) > 1e-9: viol16.append(("stop_fill", d))
    if r["exit_reason"] == "target" and abs(xp - (ep + 90.0)) > 1e-9: viol16.append(("target_fill", d))

flips16 = green_flips(b_inc["months"], b_comb["months"])
gate16 = dict(
    G1_timing_0_violations=(len(viol16) == 0),
    G2_placebo_beaten=(b_comb["total"] > b_plac["total"]),
    G3_net_beats_incumbent=(b_comb["total"] > b_inc["total"]),
    G5_halves_both_nonneg=(b_comb["H1"] >= 0 and b_comb["H2"] >= 0),
    G6_ex_top3_legs_positive=(b_comb["ex_top3_legs"] > 0),
    G7_no_green_month_flips_red=(len(flips16) == 0))
verdict16 = "PASS" if all(gate16.values()) else "FAIL"
OUT["eve16"] = dict(incumbent=b_inc, combined=b_comb, placebo_book=b_plac,
                   increment=b_A, increment_ex_top3_legs=b_A["ex_top3_legs"],
                   cross_validation=xval, bleed_incumbent=bleed_inc,
                   bleed_combined=bleed_comb, timing_violations=viol16,
                   green_to_red_flips=flips16, gate=gate16, verdict=verdict16)
print(f"EVE-16: incumbent {b_inc['total']} -> combined {b_comb['total']} "
      f"(placebo book {b_plac['total']}); flips={flips16}; viol={len(viol16)}; verdict {verdict16}")

# =====================================================================
# CANDIDATE 2 — BANK-EVE-17 (replay on the rebuilt v22 frame)
# =====================================================================
import bank_r3_setups as s3
s3.SPOT = s3.SPOT[s3.SPOT["date"] <= "2026-10-31"].reset_index(drop=True)
s3.DAYS = sorted(s3.SPOT["date"].unique())
s3.DAY_BARS = {d: g.reset_index(drop=True) for d, g in s3.SPOT.groupby("date")}
s3.DAILY = {k: v for k, v in s3.DAILY.items() if k <= "2026-10-31"}

from aggressive_score import candles
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU

pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0 and len(rows21) == 99

# replay_overlay copied verbatim from flaw_cycle_run.py (mode='open'),
# identical to bank_v22_phase1_score.py
def replay_overlay(cs, entry_time, p, overlay=None, delay=0, sq=SQ):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if start >= len(cs) or cs[start][0] > sq: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0)
    runmax = None; lock_armed = False
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        runmax = h if runmax is None else max(runmax, h)
        eff_stop = entry + 0.0 if lock_armed else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if lock_armed else "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == sq: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if overlay in ("fc2", "fc3") and h >= entry + 30.0:
            lock_armed = True
        if overlay in ("fc1", "fc3") and j == 2 and t < sq and runmax < entry + 15.0:
            return mk(cl, "nodev_cut", t, 0)
        if t == sq:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

def replay_e17(cs, entry_time, p, window=3, level=50.0, sq=SQ):
    """Frozen geometry with the stop enforced on closes for the first
    `window` bars (stop level entry-`level`); close-stop precedes the
    trigger check on window bars (pre-registered conservative tie-break).
    overlay is always None for the populations this is applied to."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0]
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if cs[start][0] > sq: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    win_stop = entry - level
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0)
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        in_window = j < window
        if in_window and cl <= win_stop:
            return mk(cl, "closestop_win", t, 0)
        if not in_window and l <= stop0:
            return mk(stop0, "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == sq: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if t == sq:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

# --- verify incumbent replay vs frozen r6 CSV (phase-1 assertion) ---
frozen = {(r["date"], r["direction"], r["entry_time"]): r
          for r in csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv"))}
def leg_candles(r):
    leg = lbk[r["leg_key"]]
    return candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"]), leg

inc_replay, mism = {}, []
for r in rows21:
    cs, leg = leg_candles(r)
    res = replay_overlay(cs, leg["entry_time"], r["_params"], overlay=None)
    assert res is not None, r["leg_key"]
    inc_replay[r["leg_key"]] = res
    f = frozen[(r["date"], r["direction"], r["entry_time"])]
    if (abs(res["net"] - float(f["net_inr"])) > 0.005 or res["exit_time"] != f["exit_time"]
            or res["exit_reason"] != f["exit_reason"] or abs(res["entry"] - float(f["entry_premium"])) > 0.005):
        mism.append((r["date"], r["direction"], r["entry_time"]))
assert not mism, mism
print("EVE-17 incumbent replay vs frozen r6 CSV: 0 mismatches (99 legs)")

# --- build v22 book (step A fc2 on NS1 + step B EVE-05 skip) ---
def is_or_pe_early(r):
    return r["rep"] == "Skill V3" and r["direction"] == "PE" and mins(r["entry_time"]) < mins("10:30")
v22 = []
for r in rows21:
    if is_or_pe_early(r): continue
    if r["family"] == "NS1_second":
        cs, leg = leg_candles(r)
        res = replay_overlay(cs, leg["entry_time"], r["_params"], overlay="fc2")
        assert res is not None
        net, xt, xr, xp = res["net"], res["exit_time"], res["exit_reason"], res["exit"]
    else:
        s = inc_replay[r["leg_key"]]
        net, xt, xr, xp = s["net"], s["exit_time"], s["exit_reason"], s["exit"]
    v22.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                    rep=r["rep"], entry_time=r["entry_time"], entry=r["entry"],
                    exit_time=xt, exit_reason=xr, exit=xp, net=net, leg_key=r["leg_key"],
                    params=r["_params"]))
v22_total = round(sum(r["net"] for r in v22), 2)
p1 = {(r["date"], r["direction"], r["entry_time"]): r
      for r in csv.DictReader(open(TR / "bank_v22_phase1_trades.csv"))}
p1_match = (len(v22) == len(p1) == 90 and v22_total == 91450.50 and all(
    abs(r["net"] - float(p1[(r["date"], r["direction"], r["entry_time"])]["net_inr"])) < 0.005
    and r["exit_time"] == p1[(r["date"], r["direction"], r["entry_time"])]["exit_time"]
    for r in v22))
assert p1_match, (len(v22), v22_total)
print(f"EVE-17 v22 rebuild: 90 legs, +{v22_total} — leg-for-leg match with phase-1 file: {p1_match}")

# --- prem-store cross-check on in-scope legs (phase-1 method) ---
prem = json.load(open(TR / "daily2leg/prem_bank.json"))
def store_bars(expiry, strike, typ, date):
    d = prem.get(f"{expiry}|{int(strike)}|{typ}", {}).get(date, {})
    return [(t, v[0], v[1], v[2], v[3], 0.0) for t, v in sorted(d.items())]
def in_scope(r): return r["rep"] == "Skill V3" and r["family"] != "NS1_second"
scope = [r for r in v22 if in_scope(r)]
xchk_bad = []
for r in scope:
    leg = lbk[r["leg_key"]]
    cs2 = store_bars(leg["expiry"], leg["strike"], leg["direction"], leg["date"])
    a = replay_overlay(cs2, leg["entry_time"], r["params"], overlay=None) if cs2 else None
    if a is None or abs(a["net"] - r["net"]) > 0.005 or a["exit_time"] != r["exit_time"]:
        xchk_bad.append((r["date"], r["direction"], r["entry_time"]))
print(f"EVE-17 prem-store cross-check on in-scope legs: {len(scope) - len(xchk_bad)}/{len(scope)} match; NC={xchk_bad}")

# --- score variant + placebos ---
def apply_variant(rows, scope_fn, **kw):
    out, changed = [], []
    for r in rows:
        nr = dict(r)
        if scope_fn(r):
            cs, leg = leg_candles(r)
            res = replay_e17(cs, leg["entry_time"], r["params"], **kw)
            assert res is not None, r["leg_key"]
            nr.update(net=res["net"], exit_time=res["exit_time"],
                      exit_reason=res["exit_reason"], exit=res["exit"])
            if abs(res["net"] - r["net"]) > 0.005:
                changed.append(dict(date=r["date"], direction=r["direction"],
                                    entry_time=r["entry_time"], family=r["family"],
                                    old_reason=r["exit_reason"], new_reason=res["exit_reason"],
                                    old_exit_time=r["exit_time"], new_exit_time=res["exit_time"],
                                    old_net=r["net"], new_net=res["net"],
                                    delta=round(res["net"] - r["net"], 2)))
        out.append(nr)
    return out, changed

var17, ch17 = apply_variant(v22, in_scope, window=3, level=50.0)
p1_rows, chp1 = apply_variant(v22, lambda r: (not in_scope(r)) and r["family"] != "NS1_second",
                              window=3, level=50.0)
p2_rows, chp2 = apply_variant(v22, in_scope, window=3, level=70.0)

b_v22 = battery(v22, "v22 incumbent (rebuilt)")
b_var = battery(var17, "EVE-17 variant")
b_p1 = battery(p1_rows, "EVE-17 placebo P1 (non-OR non-NS1 window)")
b_p2 = battery(p2_rows, "EVE-17 placebo P2 (level -70)")

# flaw metric: in-scope legs frozen-stopped within <=10 min
def hold(r): return mins(r["exit_time"]) - mins(r["entry_time"])
qs_inc = [r for r in scope if r["exit_reason"] == "stop" and hold(r) <= 10]
qs_var = [next(x for x in var17 if x["leg_key"] == r["leg_key"]) for r in qs_inc]
flaw = dict(scope_legs=len(scope),
            quick_stops_incumbent=len(qs_inc),
            quick_stop_cohort=[dict(date=r["date"], direction=r["direction"],
                                    entry_time=r["entry_time"], exit_time=r["exit_time"],
                                    net=r["net"]) for r in qs_inc],
            cohort_net_incumbent=round(sum(r["net"] for r in qs_inc), 2),
            cohort_net_variant=round(sum(r["net"] for r in qs_var), 2),
            variant_closestop_exits=sum(1 for r in var17 if r["exit_reason"] == "closestop_win"),
            changed_legs=ch17)

# timing / fill audit on changed legs: exit price must be a real bar close
# (close-stop) or a frozen level; exits >= entries everywhere
viol17 = []
for r in var17:
    if r["exit_time"] < r["entry_time"]: viol17.append(("exit_before_entry", r["date"]))
for c in ch17:
    r = next(x for x in v22 if x["date"] == c["date"] and x["entry_time"] == c["entry_time"]
             and x["direction"] == c["direction"])
    cs, leg = leg_candles(r)
    bars = {b[0]: b for b in cs}
    nv = next(x for x in var17 if x["leg_key"] == r["leg_key"])
    if nv["exit_reason"] == "closestop_win":
        if abs(nv["exit"] - bars[nv["exit_time"]][4]) > 1e-9:
            viol17.append(("closestop_fill_not_close", c["date"]))
    lvls = {r["entry"] - 50.0, r["entry"] + r["params"]["trig"]}
    if r["params"]["lock"] is not None: lvls.add(r["entry"] + r["params"]["lock"])
    if r["params"]["tgt2"] is not None: lvls.add(r["entry"] + r["params"]["tgt2"])
    closes = {b[4] for b in cs}
    if nv["exit"] not in lvls and nv["exit"] not in closes and nv["exit_reason"] != "closestop_win":
        viol17.append(("exit_price_unexplained", c["date"]))

flips17 = green_flips(b_v22["months"], b_var["months"])
gate17 = dict(
    G1_timing_fill_audit_clean=(len(viol17) == 0 and len(xchk_bad) == 0),
    G2_placebos_beaten=(b_var["total"] > b_p1["total"] and b_var["total"] > b_p2["total"]),
    G3_net_beats_incumbent=(b_var["total"] > b_v22["total"]),
    G5_halves_both_nonneg=(b_var["H1"] >= 0 and b_var["H2"] >= 0),
    G6_ex_top3_legs_positive=(b_var["ex_top3_legs"] > 0),
    G7_no_green_month_flips_red=(len(flips17) == 0),
    G8_flaw_cohort_improves=(flaw["cohort_net_variant"] > flaw["cohort_net_incumbent"]))
if len(ch17) == 0:
    verdict17 = "NO-OP"
elif all(gate17.values()):
    verdict17 = "PASS"
else:
    verdict17 = "FAIL"
OUT["eve17"] = dict(incumbent_rebuilt=b_v22, variant=b_var, placebo_p1=b_p1,
                    placebo_p2=b_p2, flaw=flaw, placebo_p1_changed=chp1,
                    placebo_p2_changed=chp2, timing_violations=viol17,
                    crosscheck_nc=xchk_bad, green_to_red_flips=flips17,
                    gate=gate17, verdict=verdict17)

# independent re-sum: write variant trades, re-read, re-sum
with open(TR / "bank_tuning_2026-11-10_eve17_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                "exit_time", "exit_premium", "exit_reason", "net_inr"])
    for r in sorted(var17, key=lambda x: (x["date"], x["entry_time"])):
        w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                    r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["net"]])
rs = [float(r["net_inr"]) for r in csv.DictReader(open(TR / "bank_tuning_2026-11-10_eve17_trades.csv"))]
OUT["eve17"]["independent_resum"] = dict(
    n=len(rs), net=round(sum(rs), 2),
    matches=(len(rs) == len(var17) and abs(round(sum(rs), 2) - b_var["total"]) < 0.005))
print(f"EVE-17: incumbent {b_v22['total']} -> variant {b_var['total']} "
      f"(P1 {b_p1['total']}, P2 {b_p2['total']}); changed={len(ch17)}; verdict {verdict17}")
print("EVE-17 changed legs:", json.dumps(ch17))

OUT["eve16_verdict"] = verdict16
OUT["eve17_verdict"] = verdict17
json.dump(OUT, open(TR / "bank_tuning_2026-11-10_summary.json", "w"), indent=1, default=str)
print("WROTE bank_tuning_2026-11-10_summary.json + bank_tuning_2026-11-10_eve17_trades.csv")
