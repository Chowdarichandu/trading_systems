#!/usr/bin/env python3
"""NIFTY NEXT PHASE (2026-11-04, Chandu's direction: tune DEC-S1 the way
Bank v21 was tuned to v22). DEC-S1 stays frozen as the December candidate;
the tuned book is a NEW candidate. Nothing armed.

STEP 0  Independent base verification: the 97 frozen DEC-S1 legs
        (nifty_engine_r11_decs1_legs.json) re-scored from the daily2leg
        premium stores (prem_nifty.json + prem_nifty_weekly.json) under
        the frozen S5 geometry, implemented here from the spec text
        (stop -50 before target incl. entry bar; BE arm +50 -> stop to
        entry; tgt1 +90 -> runner lock +60 / TGT2 +175; square-off at the
        15:20 bar close; entry = entry bar's open; net = pts*65 - 220).
        Compared field-by-field vs the frozen Cycle-168/adoption record.
STEP 1  EVE-06 frame check: confirmed (>=2-system) N1 pool keys with
        entry >= 12:00 not already in DEC-S1 (the afternoon-addition
        population on DEC-S1's own frame).
STEP 2  RE-ENTRY increment (Bank EVE-06a port, pre-registered by
        analogy): on a day whose earliest full-stop (-50) DEC-S1 leg has
        exited, if spot closes back through the morning-range extreme
        (09:15-11:55 bars) on that leg's side on a 5-min bar at/after
        12:00 and at/after the stop's exit bar -> re-enter same side at
        the next bar, strike ATM100 at the entry bar's spot open, expiry
        = the stopped leg's expiry (its component's contract convention),
        exits = frozen S5 geometry, max 1/day. Skipped if the day's
        realised DEC-S1 net (legs exited on/before the trigger bar) is
        already <= -3,000. Placebo: trigger scan shifted +60 min.
        Increment gate (the Bank phase-2 standard): total > 0 AND beats
        the shifted placebo AND both halves >= 0 AND timing clean AND
        NC = 0. Ex-top-3 of the increment reported as a flag either way.
STEP 3  Assembly (base + Step-1 passes [none exist besides the inert
        EVE-04 no-op] + re-entry if it passes) under the full gate.

Nifty only, premiums per 1 lot (65), cost Rs220/trade, UNIQUE-ONCE.
Paper only, real money Rs0. No frozen file, November book or log touched.
"""
import json, csv, math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_next_phase_backfill import source_bars, same as bars_same

TR = Path.home() / "workspace/trading"
DL = TR / "daily2leg"
LOT, COST, WEEKS = 65, 220.0, 40.6
SQ = "15:20"
DAY_CAP = -3000.0

# ---------------- data ----------------
PREM_M = json.load(open(DL / "prem_nifty.json"))
PREM_W = json.load(open(DL / "prem_nifty_weekly.json"))
SPOT_R = json.load(open(DL / "spot.json"))["NIFTY"]
SPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in bars}
        for d, bars in SPOT_R.items() if "2026-01-01" <= d <= "2026-10-31"}
STIMES = {d: [b[0] for b in bars] for d, bars in SPOT_R.items()
          if "2026-01-01" <= d <= "2026-10-31"}
DAYS = sorted(d for d in SPOT if len(SPOT_R[d]) >= 74)

BASE_LEGS = json.load(open(TR / "nifty_engine_r11_decs1_legs.json"))

def prem_day(exp, strike, typ, d, component):
    """Contract bars for the day from the component's designated store
    (C -> weekly, A/B -> monthly), falling back to the other store.
    Returns (bars list [(t,o,h,l,c)] sorted, store_name) or (None, None)."""
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

def merged_day(exp, strike, typ, d, component):
    """Store day (designated store first) overlaid add-only with the
    declared-source day (engine exact-tag / range caches). Returns
    (bars, tag) or (None, reason). A source bar disagreeing with a
    stored bar on any shared timestamp voids the day."""
    bars, tag = prem_day(exp, strike, typ, d, component)
    base = {}
    if bars:
        base = {t: [o, h, l, c] for (t, o, h, l, c) in bars}
    src, how = source_bars(strike, typ, d, exp)
    if src:
        for t, v in src.items():
            if t in base and not bars_same(base[t], v):
                return None, f"source_disagreement@{t}"
            base.setdefault(t, v)
        tag = f"{tag or 'none'}+{how}"
    if not base:
        return None, "no_candles_anywhere"
    bars = sorted((t, v[0], v[1], v[2], v[3]) for t, v in base.items())
    return bars, tag

def atm100(x):
    return int(math.floor(x / 100.0 + 0.5)) * 100

def add_min(t, m):
    h, mm = int(t[:2]), int(t[3:]) + m
    return f"{h + mm // 60:02d}:{mm % 60:02d}"

# ---------------- frozen S5 geometry (independent implementation) ----
def replay(bars, entry_time, lock=60.0, tgt2=175.0, arm=50.0, sq=SQ,
           delay_bars=0):
    """bars: [(t,o,h,l,c)] sorted. Mirrors the frozen S5 sequencing:
    bars from the first bar >= entry_time (+ delay_bars for the placebo);
    entry = that bar's open; on every bar up to and including the sq bar,
    stop is checked before target; BE arm applies from the next bar after
    the arming bar; tgt1 converts to a runner from the following bar;
    terminal exit at the sq bar's close. Fills at the level for
    stop/lock/target exits, at the close for square-offs."""
    if not bars:
        return None
    idxs = [i for i, b in enumerate(bars) if b[0] >= entry_time]
    if not idxs:
        return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(bars):
        return None
    bs = bars[i0:]
    if bs[0][0] > sq:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0

    def out(pts, reason, t, ft, px):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round(pts * LOT - COST, 2))

    cur_stop = stop
    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > sq:
            break
        if l <= cur_stop:
            return out(cur_stop - entry,
                       "be_stop" if cur_stop == entry else "stop", t, 0,
                       cur_stop)
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for (t2, o2, h2, l2, cl2) in bs[i + 1:]:
                if t2 > sq:
                    break
                if l2 <= stop2:
                    return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2:
                    return out(target2 - entry, "runner_target", t2, 1,
                               target2)
                if t2 == sq:
                    return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bs[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == sq:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bs[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

# ---------------- STEP 0: base re-score ----------------
def score_base(delay_bars=0):
    res, nc = [], []
    for l in BASE_LEGS:
        bars, src = prem_day(l["expiry"], l["strike"], l["direction"],
                             l["date"], l["component"])
        if bars is None:
            nc.append({**l, "why": "no_contract_in_stores"})
            continue
        r = replay(bars, l["entry_time"], delay_bars=delay_bars)
        if r is None:
            nc.append({**l, "why": "replay_none"})
            continue
        res.append({**l, **r, "store": src,
                    "entry_bar_exact": (l["entry_time"]
                                        in {b[0] for b in bars}
                                        and SQ in {b[0] for b in bars})
                    if delay_bars == 0 else None})
    return res, nc

def stats(res):
    total = round(sum(r["net"] for r in res), 2)
    months = {}
    for m in sorted({r["date"][:7] for r in res}):
        months[m] = round(sum(r["net"] for r in res
                              if r["date"][:7] == m), 2)
    h1 = round(sum(r["net"] for r in res if r["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"][:7] >= "2026-06"), 2)
    top3 = sorted((r["net"] for r in res), reverse=True)[:3]
    return dict(n=len(res), total=total, months=months, halves=(h1, h2),
                ft=sum(r["ft"] for r in res),
                ft_pct=round(100.0 * sum(r["ft"] for r in res) / len(res), 1)
                if res else 0.0,
                per_week=round(len(res) / WEEKS, 2),
                ex_top3=round(total - sum(top3), 2), top3=top3)

def day_stats(res):
    byd = defaultdict(float)
    for r in res:
        byd[r["date"]] += r["net"]
    days = sorted(byd)
    nets = [round(byd[d], 2) for d in days]
    worst = min(zip(nets, days))
    w3 = min((round(nets[i] + nets[i + 1] + nets[i + 2], 2), days[i])
             for i in range(len(nets) - 2))
    cum, peak, dd = 0.0, 0.0, 0.0
    for v in nets:
        cum = round(cum + v, 2)
        peak = max(peak, cum)
        dd = min(dd, round(cum - peak, 2))
    return dict(leg_days=len(days), worst_day=(worst[1], worst[0]),
                worst_3day=(w3[1], w3[0]), worst_dd=dd,
                pos_days=sum(1 for v in nets if v > 0),
                pos_pct=round(100.0 * sum(1 for v in nets if v > 0)
                              / len(nets), 1) if nets else 0.0,
                by_day={d: round(byd[d], 2) for d in days})

base_res, base_nc = score_base()
BS = stats(base_res)
BD = day_stats(base_res)
base_pl, _ = score_base(delay_bars=6)
base_pl_total = round(sum(r["net"] for r in base_pl), 2)
comp = {c: stats([r for r in base_res if r["component"] == c])
        for c in "ABC"}

FROZEN = dict(total=91168.50,
              months={"2026-01": 19211.25, "2026-02": 5038.75,
                      "2026-03": -11846.50, "2026-04": 28416.00,
                      "2026-05": 4574.00, "2026-06": -1331.00,
                      "2026-07": 5839.00, "2026-08": 841.25,
                      "2026-09": 20265.25, "2026-10": 20160.50},
              halves=(45393.50, 45775.00), placebo=52867.25,
              ex_top3=57703.50, ft_pct=34.0, per_week=2.39,
              A=(35, 54102.00), B=(49, 33624.75), C=(13, 3441.75),
              worst_day=("2026-07-14", -5295.50), worst_3day=-10630.00,
              worst_dd=-17360.00)
verify = {
    "total": BS["total"] == FROZEN["total"],
    "n": BS["n"] == 97, "nc": len(base_nc) == 0,
    "months": BS["months"] == FROZEN["months"],
    "halves": BS["halves"] == FROZEN["halves"],
    "placebo": base_pl_total == FROZEN["placebo"],
    "ex_top3": BS["ex_top3"] == FROZEN["ex_top3"],
    "ft_pct": BS["ft_pct"] == FROZEN["ft_pct"],
    "per_week": BS["per_week"] == FROZEN["per_week"],
    "A": (comp["A"]["n"], comp["A"]["total"]) == FROZEN["A"],
    "B": (comp["B"]["n"], comp["B"]["total"]) == FROZEN["B"],
    "C": (comp["C"]["n"], comp["C"]["total"]) == FROZEN["C"],
    "worst_day": BD["worst_day"] == FROZEN["worst_day"],
    "worst_3day": BD["worst_3day"][1] == FROZEN["worst_3day"],
    "worst_dd": BD["worst_dd"] == FROZEN["worst_dd"],
    "entry_bars_exact": all(r["entry_bar_exact"] for r in base_res),
}
print("STEP 0 base verification:")
for k, v in verify.items():
    print(f"  {'MATCH' if v else 'MISMATCH'} {k}")
print(f"  base: n {BS['n']} total {BS['total']:+,.2f} placebo "
      f"{base_pl_total:+,.2f} NC {len(base_nc)}")
if base_nc:
    print("  NC legs:", base_nc)

base_by_day = defaultdict(list)
for r in base_res:
    base_by_day[r["date"]].append(r)

# ---------------- STEP 1: EVE-06 frame check ----------------
pool = list(csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv")))
decs1_keys = {(l["date"], l["direction"]) for l in BASE_LEGS}
conf_aft = [p for p in pool
            if len([s for s in p["source_systems"].split(";")
                    if s.strip()]) >= 2
            and p["entry_time"] >= "12:00"]
conf_aft_new = [p for p in conf_aft
                if (p["date"], p["direction"]) not in decs1_keys]
print(f"STEP 1 EVE-06 frame check: confirmed pool keys entry>=12:00: "
      f"{len(conf_aft)}; not in DEC-S1: {len(conf_aft_new)}")

# ---------------- STEP 2: re-entry increment ----------------
def realised_before(d, trig):
    return round(sum(r["net"] for r in base_by_day.get(d, [])
                     if r["exit_time"] <= trig), 2)

def find_reentry(d, shift_min=0):
    stops = [r for r in base_by_day.get(d, [])
             if r["exit_reason"] == "stop"]
    if not stops:
        return None
    leg0 = sorted(stops, key=lambda r: (r["exit_time"], r["entry_time"]))[0]
    side = leg0["direction"]
    b, ts = SPOT[d], STIMES[d]
    mh = max(b[t][1] for t in ts if t <= "11:55")
    ml = min(b[t][2] for t in ts if t <= "11:55")
    start = add_min(max("12:00", leg0["exit_time"]), shift_min)
    for t in ts:
        if t < start:
            continue
        c = b[t][3]
        if (side == "CE" and c > mh) or (side == "PE" and c < ml):
            return dict(side=side, trig=t, leg0=leg0,
                        extreme=mh if side == "CE" else ml)
    return None

def build_reentry(d, f):
    ts = STIMES[d]
    i = ts.index(f["trig"])
    et = ts[i + 1] if i + 1 < len(ts) else None
    if et is None or et > SQ:
        return None, "trigger_no_time"
    leg0 = f["leg0"]
    strike = atm100(SPOT[d][et][0])
    bars, src = merged_day(leg0["expiry"], strike, f["side"], d,
                           leg0["component"])
    if bars is None:
        return None, f"{src} {leg0['expiry']}|{strike}|{f['side']}"
    times = {b[0] for b in bars}
    if et not in times:
        return None, f"no_entry_bar {leg0['expiry']}|{strike}|{f['side']}@{et}"
    if SQ not in times:
        return None, f"no_sq_bar {leg0['expiry']}|{strike}|{f['side']}"
    r = replay(bars, et)
    if r is None:
        return None, "replay_none"
    return dict(date=d, component="RE", direction=f["side"],
                expiry=leg0["expiry"], strike=strike, entry_time=et,
                trigger_time=f["trig"], anchor_component=leg0["component"],
                anchor_exit_time=leg0["exit_time"],
                anchor_entry_time=leg0["entry_time"], store=src, **r), "ok"

re_legs, re_blocked, re_nc = [], [], []
pl_legs, pl_nc = [], []
stop_days = sorted({r["date"] for r in base_res
                    if r["exit_reason"] == "stop"})
for d in stop_days:
    for shift, out, ncout in ((0, re_legs, re_nc), (60, pl_legs, pl_nc)):
        f = find_reentry(d, shift)
        if not f:
            continue
        if realised_before(d, f["trig"]) <= DAY_CAP:
            if shift == 0:
                re_blocked.append(dict(date=d, trigger=f["trig"],
                                       realised=realised_before(
                                           d, f["trig"])))
            continue
        leg, st = build_reentry(d, f)
        if leg:
            out.append(leg)
        else:
            ncout.append(dict(date=d, why=st, trigger=f["trig"]))

RS = stats(re_legs) if re_legs else dict(n=0, total=0.0, months={},
                                         halves=(0.0, 0.0), ft=0,
                                         ft_pct=0.0, per_week=0.0,
                                         ex_top3=0.0, top3=[])
pl_total = round(sum(r["net"] for r in pl_legs), 2)
whips = [r for r in re_legs if r["exit_reason"] == "stop"]
be_days = sorted({r["date"] for r in base_res
                  if r["exit_reason"] == "be_stop"})
rs_days = sorted({r["date"] for r in base_res
                  if r["exit_reason"] == "runner_stop"})
re_gate = dict(total_pos=RS["total"] > 0, beats_placebo=RS["total"] > pl_total,
               halves_nonneg=RS["halves"][0] >= 0 and RS["halves"][1] >= 0,
               nc_zero=len(re_nc) == 0)
re_pass = all(re_gate.values())
print(f"STEP 2 re-entry: stop days {len(stop_days)}; legs {RS['n']} "
      f"total {RS['total']:+,.2f}; placebo {pl_total:+,.2f} "
      f"({len(pl_legs)} legs); blocked {len(re_blocked)}; NC {len(re_nc)}; "
      f"double-stops {len(whips)}; gate {re_gate} -> "
      f"{'PASS' if re_pass else 'FAIL'}")

# ---------------- STEP 3: assembly + full gate ----------------
asm_res = base_res + (re_legs if re_pass else [])
AS = stats(asm_res)
AD = day_stats(asm_res)
asm_pl_legs = list(base_pl)
if re_pass:
    for r in re_legs:
        bars, _ = prem_day(r["expiry"], r["strike"], r["direction"],
                           r["date"], r["anchor_component"])
        rr = replay(bars, r["entry_time"], delay_bars=6) if bars else None
        if rr:
            asm_pl_legs.append({**r, **rr})
asm_pl_total = round(sum(r["net"] for r in asm_pl_legs), 2)
flips = [m for m in FROZEN["months"]
         if BS["months"].get(m, 0.0) > 0 and AS["months"].get(m, 0.0) < 0]
audit_bad = []
for r in re_legs:
    if r["trigger_time"] < "12:00" or r["trigger_time"] < r["anchor_exit_time"]:
        audit_bad.append(("trigger_order", r["date"]))
    if r["entry_time"] <= r["trigger_time"]:
        audit_bad.append(("entry_not_after_trigger", r["date"]))
    if r["exit_time"] < r["entry_time"]:
        audit_bad.append(("exit_before_entry", r["date"]))
for r in base_res:
    if r["exit_time"] < r["entry_time"]:
        audit_bad.append(("base_exit_before_entry", r["date"]))
print(f"STEP 3 assembled: n {AS['n']} total {AS['total']:+,.2f} "
      f"({AS['total'] / 10:+,.2f}/mo); placebo {asm_pl_total:+,.2f}; "
      f"flips {flips}; audit violations {len(audit_bad)}")

# ---------------- outputs ----------------
rows = []
for r in base_res:
    rows.append(dict(set="BASE", date=r["date"], component=r["component"],
                     direction=r["direction"], expiry=r["expiry"],
                     strike=r["strike"], entry_time=r["entry_time"],
                     entry_premium=r["entry"], exit_time=r["exit_time"],
                     exit_premium=r["exit"], exit_reason=r["exit_reason"],
                     ft=r["ft"], net_inr=r["net"], trigger_time="",
                     anchor="", store=r["store"]))
for r in re_legs:
    rows.append(dict(set="REENTRY", date=r["date"], component="RE",
                     direction=r["direction"], expiry=r["expiry"],
                     strike=r["strike"], entry_time=r["entry_time"],
                     entry_premium=r["entry"], exit_time=r["exit_time"],
                     exit_premium=r["exit"], exit_reason=r["exit_reason"],
                     ft=r["ft"], net_inr=r["net"],
                     trigger_time=r["trigger_time"],
                     anchor=f"{r['anchor_component']}@{r['anchor_entry_time']}"
                            f" stop {r['anchor_exit_time']}",
                     store=r["store"]))
rows.sort(key=lambda x: (x["date"], x["entry_time"], x["set"]))
with open(TR / "nifty_next_phase_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# independent re-sum: read ONLY the written CSV
back = list(csv.DictReader(open(TR / "nifty_next_phase_trades.csv")))
rs_base = round(sum(float(x["net_inr"]) for x in back
                    if x["set"] == "BASE"), 2)
rs_re = round(sum(float(x["net_inr"]) for x in back
                  if x["set"] == "REENTRY"), 2)
rs_asm = round(sum(float(x["net_inr"]) for x in back
                   if x["set"] == "BASE" or (re_pass
                                             and x["set"] == "REENTRY")), 2)
resum_ok = (rs_base == BS["total"] and rs_re == RS["total"]
            and rs_asm == AS["total"])
print(f"RE-SUM from CSV: base {rs_base:+,.2f} reentry {rs_re:+,.2f} "
      f"assembled {rs_asm:+,.2f} -> {'EXACT' if resum_ok else 'MISMATCH'}")

out = dict(
    step0_verify=verify, base=BS, base_days=BD, base_placebo=base_pl_total,
    base_nc=base_nc, components={c: comp[c] for c in "ABC"},
    step1_eve06_frame=dict(confirmed_afternoon_keys=len(conf_aft),
                           not_in_decs1=len(conf_aft_new),
                           keys=[(p["date"], p["direction"], p["entry_time"])
                                 for p in conf_aft]),
    step2=dict(stop_days=len(stop_days), legs=re_legs, stats=RS,
               placebo_total=pl_total, placebo_legs=len(pl_legs),
               blocked=re_blocked, nc=re_nc, placebo_nc=pl_nc,
               double_stops=len(whips), gate=re_gate, passed=re_pass,
               be_stop_days=len(be_days), runner_stop_days=len(rs_days)),
    step3=dict(assembled=AS, days=AD, placebo_total=asm_pl_total,
               flips=flips, audit_violations=audit_bad,
               pace_per_month=round(AS["total"] / 10, 2),
               gap_to_bracket=round(150000.0 - AS["total"], 2)),
    resum=dict(base=rs_base, reentry=rs_re, assembled=rs_asm, ok=resum_ok))
(TR / "nifty_next_phase_results.json").write_text(
    json.dumps(out, indent=1, default=str))
print("wrote nifty_next_phase_trades.csv + nifty_next_phase_results.json")
