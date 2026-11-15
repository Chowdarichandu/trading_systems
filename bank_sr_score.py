#!/usr/bin/env python3
"""BANK S/R-REJECTION layer on v21 — scorer + full gate (2026-11-04).

Definitions are PRE-REGISTERED in bank_sr_rejection_v21_2026-11-04.md
(header written before this scorer ran). Nothing here is tuned: textbook
values only (5-pt proximity, 50% wick, first test per (level, role),
next-bar-open entry, G0 -50/+90 exits, SQ 15:10, max 2 S/R legs/day,
combined-book day-loss cap -3000, UNIQUE-ONCE).

Conventions reused verbatim from the frozen machinery:
  - prem store daily2leg/prem_bank.json: prem[expiry|strike|TYPE][date]
    [time] = [open, high, low, close]; spot daily2leg/spot.json BANKNIFTY
    bars [time, open, high, low, close].
  - store_expiry_for / atm100 / prem_day / G0 loop copied from
    bank_aggressive_tune_score.py (sim_g0_arm with no arm).
  - day-cap semantics copied from the same file: a new leg is blocked
    when the day's realised net (book legs with exit_time <= decision
    time) is <= -3000.
Money: lot 30, cost Rs 220/trade, net = (exit-entry)*30 - 220.
"""
import csv, json, random
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
LOT, COST = 30, 220.0
SQ = "15:10"
PROX = 5.0          # spot points, proximity of a test
WICK = 0.5          # rejection wick fraction of bar range
MAX_SR_PER_DAY = 2
DAY_CAP = -3000.0
RANDOM_SEED = 20261104

prem_store = json.load(open(TR / "daily2leg/prem_bank.json"))
spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
DAYS = sorted(d for d in spot_raw
              if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
ALLDAYS = sorted(spot_raw)
SPOT = {d: {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
            for b in spot_raw[d]} for d in ALLDAYS}
TIMES = {d: [b[0] for b in spot_raw[d]] for d in ALLDAYS}

_chain_days = defaultdict(set)
for k, v in prem_store.items():
    for d in v:
        _chain_days[k.split("|")[0]].add(d)
MONTHLY = sorted(e for e, ds in _chain_days.items() if len(ds) >= 10)


def store_expiry_for(d):
    for e in MONTHLY:
        if d <= e:
            return e
    present = {k.split("|")[0] for k, v in prem_store.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None


def atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100


def prem_day(exp, strike, typ, d):
    cd = prem_store.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None:
        return None
    return {t: tuple(float(x) for x in v) for t, v in cd.items()}


def sim_g0(pd, entry_time):
    """Plain G0: stop -50 / target +90, stop before target, entry bar
    included, fills at the level, square-off at the 15:10 bar open.
    Returns (exit_time, exit_premium, reason, entry_premium) or None."""
    if pd is None or entry_time not in pd:
        return None
    entry = pd[entry_time][0]
    for t in sorted(pd):
        if t < entry_time or t > "15:05":
            continue
        o, h, l, c = pd[t]
        if l <= entry - 50.0:
            return t, entry - 50.0, "stop", entry
        if h >= entry + 90.0:
            return t, entry + 90.0, "target", entry
    if SQ in pd:
        return SQ, pd[SQ][0], "square_off", entry
    last = max(t for t in pd if t <= "15:05")
    if last < entry_time:
        return None
    return last, pd[last][3], "path_end", entry


def score_leg(date, direction, entry_time, strike=None, expiry=None):
    """Score one option leg under G0. Returns (row, None) or (None, why)."""
    et_spot = SPOT[date].get(entry_time)
    if et_spot is None:
        return None, f"spot bar {entry_time} absent {date}"
    exp = expiry or store_expiry_for(date)
    stk = strike if strike is not None else atm100(et_spot[0])
    pd = prem_day(exp, stk, direction, date)
    if pd is None:
        return None, f"no contract {exp}|{stk}|{direction} on {date}"
    out = sim_g0(pd, entry_time)
    if out is None:
        return None, f"entry bar {entry_time} absent for {exp}|{stk}|{direction} {date}"
    xt, xp, reason, entry = out
    return dict(date=date, direction=direction, expiry=exp, strike=stk,
                entry_time=entry_time, entry_premium=entry, exit_time=xt,
                exit_premium=xp, exit_reason=reason,
                net=round((xp - entry) * LOT - COST, 2)), None


# ================= pattern detection — implementation 1 =================
SRC_PRIORITY = {"PDH": 0, "PDC": 1, "PDL": 2, "ORH": 3, "ORL": 4,
                "SWH": 5, "SWL": 6}


def build_levels(date):
    """All (value, role) levels for the day with the bar index from which
    each is usable. Returns list of dicts."""
    bars = [SPOT[date][t] for t in TIMES[date]]
    times = TIMES[date]
    prev = ALLDAYS[ALLDAYS.index(date) - 1] if ALLDAYS.index(date) > 0 else None
    levels = {}  # (value, role) -> dict(source, usable_idx)

    def add(value, role, source, usable_idx):
        key = (round(value, 2), role)
        cur = levels.get(key)
        if cur is None or usable_idx < cur["usable_idx"] or (
                usable_idx == cur["usable_idx"]
                and SRC_PRIORITY[source] < SRC_PRIORITY[cur["source"]]):
            levels[key] = dict(value=round(value, 2), role=role,
                               source=source, usable_idx=usable_idx)

    if prev is not None:
        pb = [SPOT[prev][t] for t in TIMES[prev]]
        pdh = max(b[1] for b in pb); pdl = min(b[2] for b in pb)
        pdc = pb[-1][3]
        for src, val in (("PDH", pdh), ("PDL", pdl), ("PDC", pdc)):
            add(val, "resistance", src, 0)
            add(val, "support", src, 0)
    or_idx = [i for i, t in enumerate(times) if "09:15" <= t <= "09:40"]
    use_idx = next(i for i, t in enumerate(times) if t >= "09:45")
    orh = max(bars[i][1] for i in or_idx); orl = min(bars[i][2] for i in or_idx)
    for src, val in (("ORH", orh), ("ORL", orl)):
        add(val, "resistance", src, use_idx)
        add(val, "support", src, use_idx)
    n = len(bars)
    for t in range(2, n - 2):
        if all(bars[t][1] > bars[j][1] for j in (t - 2, t - 1, t + 1, t + 2)):
            add(bars[t][1], "resistance", "SWH", t + 3)
        if all(bars[t][2] < bars[j][2] for j in (t - 2, t - 1, t + 1, t + 2)):
            add(bars[t][2], "support", "SWL", t + 3)
    # a level whose usable index falls past the last bar can never be
    # tested today; it is dropped from the materialised list.
    return [dict(v, usable_time=times[v["usable_idx"]])
            for v in levels.values() if v["usable_idx"] < len(times)]


def is_test_reject(bar, value, role):
    """(tested, rejected) for one bar against one (level, role)."""
    o, h, l, c = bar
    rng = h - l
    if role == "resistance":
        if not (h >= value - PROX and l < value):
            return False, False
        if rng <= 0:
            return True, False
        rej = (h - max(o, c) >= WICK * rng and c <= (h + l) / 2.0
               and c < value)
        return True, rej
    else:
        if not (l <= value + PROX and h > value):
            return False, False
        if rng <= 0:
            return True, False
        rej = (min(o, c) - l >= WICK * rng and c >= (h + l) / 2.0
               and c > value)
        return True, rej


def detect_v1(date):
    """Implementation 1: bar loop, levels sorted by (source priority,
    value) inside each bar. Returns (events, n_first_tests)."""
    times = TIMES[date]
    bars = [SPOT[date][t] for t in times]
    levels = build_levels(date)
    tested = set()
    events = []
    n_tests = 0
    for i, t in enumerate(times):
        cands = [lv for lv in levels
                 if lv["usable_idx"] <= i
                 and (lv["value"], lv["role"]) not in tested]
        cands.sort(key=lambda lv: (SRC_PRIORITY[lv["source"]], lv["value"]))
        for lv in cands:
            tested_now, rej = is_test_reject(bars[i], lv["value"], lv["role"])
            if not tested_now:
                continue
            tested.add((lv["value"], lv["role"]))
            n_tests += 1
            if not rej:
                continue
            if i + 1 >= len(times):
                continue
            et = times[i + 1]
            if et > "15:05":
                continue
            events.append(dict(
                date=date, pattern_idx=i, pattern_time=t,
                level_value=lv["value"], level_role=lv["role"],
                level_source=lv["source"], level_usable_time=lv["usable_time"],
                direction="PE" if lv["role"] == "resistance" else "CE",
                entry_time=et))
    return events, n_tests


def detect_v2(date):
    """Implementation 2 (independent structure): first compute, for every
    (level, role), the first test bar and whether it rejected — scanning
    levels outermost — then turn rejections into events."""
    times = TIMES[date]
    bars = [SPOT[date][t] for t in times]
    levels = build_levels(date)
    events = []
    n_tests = 0
    for lv in levels:
        first = None
        for i in range(lv["usable_idx"], len(times)):
            tested_now, rej = is_test_reject(bars[i], lv["value"], lv["role"])
            if tested_now:
                first = (i, rej)
                break
        if first is None:
            continue
        n_tests += 1
        i, rej = first
        if not rej or i + 1 >= len(times):
            continue
        et = times[i + 1]
        if et > "15:05":
            continue
        events.append(dict(
            date=date, pattern_idx=i, pattern_time=times[i],
            level_value=lv["value"], level_role=lv["role"],
            level_source=lv["source"], level_usable_time=lv["usable_time"],
            direction="PE" if lv["role"] == "resistance" else "CE",
            entry_time=et))
    events.sort(key=lambda e: (e["pattern_idx"],
                               SRC_PRIORITY[e["level_source"]],
                               e["level_value"]))
    return events, n_tests


# ---- detection + cross-check ------------------------------------------------
ALL_EVENTS = {}
TOTAL_TESTS = 0
for d in DAYS:
    e1, n1 = detect_v1(d)
    e2, n2 = detect_v2(d)
    key1 = [(e["pattern_time"], e["direction"], e["level_value"],
             e["level_role"], e["entry_time"]) for e in e1]
    key2 = [(e["pattern_time"], e["direction"], e["level_value"],
             e["level_role"], e["entry_time"]) for e in e2]
    assert key1 == key2, (d, key1, key2)
    assert n1 == n2, (d, n1, n2)
    ALL_EVENTS[d] = e1
    TOTAL_TESTS += n1
print(f"pattern detection cross-check v1==v2: PASS "
      f"({sum(len(v) for v in ALL_EVENTS.values())} rejection events, "
      f"{TOTAL_TESTS} first tests, {len(DAYS)} days)")

# ---- timing audit on raw events ----------------------------------------------
audit_fail = []
for d, evs in ALL_EVENTS.items():
    times = TIMES[d]
    for e in evs:
        if times.index(e["entry_time"]) != e["pattern_idx"] + 1:
            audit_fail.append((d, "entry not next bar", e))
        if e["level_usable_time"] > e["pattern_time"]:
            audit_fail.append((d, "level usable after pattern", e))
        if e["pattern_time"] < e["level_usable_time"]:
            audit_fail.append((d, "pattern before usable", e))
assert not audit_fail, audit_fail[:3]
print("timing audit (level usable <= pattern bar; entry = pattern+1): PASS")


def day_events_sorted(d):
    return sorted(ALL_EVENTS[d],
                  key=lambda e: (e["pattern_idx"],
                                 SRC_PRIORITY[e["level_source"]],
                                 e["level_value"]))


def dedup_events(evs):
    """UNIQUE-ONCE within the S/R set: same (direction, entry_time) =
    same trade. Returns (kept, dropped)."""
    seen, kept, dropped = set(), [], []
    for e in evs:
        k = (e["direction"], e["entry_time"])
        if k in seen:
            dropped.append(e)
        else:
            seen.add(k)
            kept.append(e)
    return kept, dropped


# ================= (A) standalone ============================================
A_legs, A_nc, A_overcap, A_deduped = [], [], [], []
for d in DAYS:
    kept, dropped = dedup_events(day_events_sorted(d))
    A_deduped += [dict(e, date=e["date"]) for e in dropped]
    slots = 0
    for e in kept:
        if slots >= MAX_SR_PER_DAY:
            A_overcap.append(e)
            continue
        slots += 1  # NC consumes a slot (pre-registered)
        row, why = score_leg(d, e["direction"], e["entry_time"])
        if row is None:
            A_nc.append(dict(date=d, pattern_time=e["pattern_time"],
                             direction=e["direction"],
                             entry_time=e["entry_time"],
                             level_source=e["level_source"],
                             level_value=e["level_value"], why=why))
        else:
            A_legs.append({**row, "book": "A_standalone",
                           "pattern_time": e["pattern_time"],
                           "level_source": e["level_source"],
                           "level_value": e["level_value"],
                           "level_role": e["level_role"]})

# ================= (B) added book =============================================
v21 = list(csv.DictReader(open(TR / "bank_engine_r6_v21_trades.csv")))
V21_TOTAL = round(sum(float(r["net_inr"]) for r in v21), 2)
assert V21_TOTAL == 83650.50, V21_TOTAL
v21_keys = {(r["date"], r["direction"], r["entry_time"]) for r in v21}
v21_by_day = defaultdict(list)
for r in v21:
    v21_by_day[r["date"]].append(r)

B_incr, B_nc, B_overcap, B_deduped, B_blocked = [], [], [], [], []
for d in DAYS:
    evs, dropped = dedup_events(day_events_sorted(d))
    B_deduped += dropped
    admitted = []
    slots = 0
    for e in evs:
        if (d, e["direction"], e["entry_time"]) in v21_keys or \
                any(a["direction"] == e["direction"]
                    and a["entry_time"] == e["entry_time"] for a in admitted):
            B_deduped.append(e)
            continue
        realised = round(
            sum(float(r["net_inr"]) for r in v21_by_day[d]
                if r["exit_time"] <= e["pattern_time"])
            + sum(a["net"] for a in admitted
                  if a["exit_time"] <= e["pattern_time"]), 2)
        if realised <= DAY_CAP:
            B_blocked.append(dict(date=d, pattern_time=e["pattern_time"],
                                  direction=e["direction"],
                                  entry_time=e["entry_time"],
                                  realised_at_pattern=realised))
            continue
        if slots >= MAX_SR_PER_DAY:
            B_overcap.append(e)
            continue
        slots += 1
        row, why = score_leg(d, e["direction"], e["entry_time"])
        if row is None:
            B_nc.append(dict(date=d, pattern_time=e["pattern_time"],
                             direction=e["direction"],
                             entry_time=e["entry_time"],
                             level_source=e["level_source"],
                             level_value=e["level_value"], why=why))
        else:
            row = {**row, "book": "B_increment",
                   "pattern_time": e["pattern_time"],
                   "level_source": e["level_source"],
                   "level_value": e["level_value"],
                   "level_role": e["level_role"]}
            admitted.append(row)
            B_incr.append(row)

combined_rows = [dict(date=r["date"], direction=r["direction"],
                      family=r["family"], rep=r["rep"],
                      entry_time=r["entry_time"],
                      entry_premium=float(r["entry_premium"]),
                      exit_time=r["exit_time"],
                      exit_premium=float(r["exit_premium"]),
                      exit_reason=r["exit_reason"],
                      net=float(r["net_inr"]), book="v21")
                 for r in v21] + B_incr


# ================= aggregates / gate helpers ==================================
def aggregates(rows):
    if not rows:
        return dict(legs=0, total=0.0)
    total = round(sum(r["net"] for r in rows), 2)
    months = {}
    for m in sorted({r["date"][:7] for r in rows}):
        months[m] = round(sum(r["net"] for r in rows
                              if r["date"][:7] == m), 2)
    h1 = round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2)
    srt = sorted((r["net"] for r in rows), reverse=True)
    byday = defaultdict(float)
    for r in rows:
        byday[r["date"]] += r["net"]
    daynets = [round(byday[d], 2) for d in sorted(byday)]
    cum, peak, dd = 0.0, 0.0, 0.0
    for v in daynets:
        cum += v
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return dict(
        legs=len(rows), total=total,
        mean_per_leg=round(total / len(rows), 2),
        win_rate_pct=round(100.0 * sum(1 for r in rows if r["net"] > 0)
                           / len(rows), 1),
        ft_rate_pct=round(100.0 * sum(1 for r in rows
                                      if r["exit_reason"] == "target")
                          / len(rows), 1),
        months=months,
        halves=dict(H1_Jan_May=h1, H2_Jun_Oct=round(total - h1, 2)),
        ex_top3_legs=round(total - sum(srt[:3]), 2),
        days=len(daynets),
        worst_day=round(min(daynets), 2),
        bleed_days_le_3000=sum(1 for v in daynets if v <= -3000.0),
        negative_months=[m for m, v in months.items() if v < 0],
        worst_drawdown=round(dd, 2))


def placebo_flipped(legs):
    rows, nc = [], []
    for r in legs:
        flip = "PE" if r["direction"] == "CE" else "CE"
        row, why = score_leg(r["date"], flip, r["entry_time"],
                             strike=r["strike"], expiry=r["expiry"])
        if row is None:
            nc.append((r["date"], why))
        else:
            rows.append(row)
    return rows, nc


def placebo_shifted(legs):
    rows, nc, notime = [], [], []
    for r in legs:
        times = TIMES[r["date"]]
        i = times.index(r["entry_time"])
        if i + 6 >= len(times) or times[i + 6] > "15:05":
            notime.append((r["date"], "shifted entry past 15:05"))
            continue
        row, why = score_leg(r["date"], r["direction"], times[i + 6],
                             strike=r["strike"], expiry=r["expiry"])
        if row is None:
            nc.append((r["date"], why))
        else:
            rows.append(row)
    return rows, nc, notime


def placebo_random(legs):
    """Matched on count/month; single stream seeded RANDOM_SEED."""
    rng = random.Random(RANDOM_SEED)
    by_month = defaultdict(int)
    for r in legs:
        by_month[r["date"][:7]] += 1
    rows, failed = [], 0
    entry_choices = [t for t in TIMES[DAYS[0]] if "09:20" <= t <= "15:05"]
    for m, n in sorted(by_month.items()):
        mdays = [d for d in DAYS if d[:7] == m]
        for _ in range(n):
            got = None
            for _try in range(200):
                d = rng.choice(mdays)
                et = rng.choice(entry_choices)
                if et not in SPOT[d]:
                    continue
                direction = rng.choice(["CE", "PE"])
                row, why = score_leg(d, direction, et)
                if row is not None:
                    got = row
                    break
            if got is None:
                failed += 1
            else:
                rows.append(got)
    return rows, failed


def gate_pack(legs):
    fl, fl_nc = placebo_flipped(legs)
    sh, sh_nc, sh_nt = placebo_shifted(legs)
    ra, ra_failed = placebo_random(legs)
    return dict(
        base=aggregates(legs),
        flipped=dict(total=round(sum(r["net"] for r in fl), 2),
                     legs=len(fl), nc=fl_nc),
        shifted30=dict(total=round(sum(r["net"] for r in sh), 2),
                       legs=len(sh), nc=sh_nc, no_time=sh_nt),
        random=dict(total=round(sum(r["net"] for r in ra), 2),
                    legs=len(ra), failed_draws=ra_failed,
                    seed=RANDOM_SEED))


gate_A = gate_pack(A_legs)
gate_B = gate_pack(B_incr)
combined_agg = aggregates(combined_rows)

# ---- per-leg timing/premium audit on scored books ----------------------------
for r in A_legs + B_incr:
    pd = prem_day(r["expiry"], r["strike"], r["direction"], r["date"])
    assert pd[r["entry_time"]][0] == r["entry_premium"], r
    assert r["entry_time"] <= r["exit_time"] <= SQ, r
print("premium/timing audit on scored legs: PASS "
      "(entry premium == store open; exits within [entry, 15:10])")

# ---- write CSVs ---------------------------------------------------------------
def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


SR_FIELDS = ["date", "direction", "family", "rep", "pattern_time",
             "level_source", "level_role", "level_value", "expiry",
             "strike", "entry_time", "entry_premium", "exit_time",
             "exit_premium", "exit_reason", "net", "book"]
A_out = [dict(r, family="SR_REJ", rep=r["level_source"]) for r in A_legs]
B_out = [dict(r, family="SR_REJ", rep=r["level_source"]) for r in B_incr]
write_csv(TR / "bank_sr_standalone_trades.csv", A_out, SR_FIELDS)
COMB_FIELDS = ["date", "direction", "family", "rep", "entry_time",
               "entry_premium", "exit_time", "exit_premium",
               "exit_reason", "net", "book"]
write_csv(TR / "bank_sr_combined_trades.csv", combined_rows, COMB_FIELDS)

# ---- independent re-sum from written files ------------------------------------
chk = list(csv.DictReader(open(TR / "bank_sr_combined_trades.csv")))
resum_total = round(sum(float(r["net"]) for r in chk), 2)
resum_v21 = round(sum(float(r["net"]) for r in chk if r["book"] == "v21"), 2)
resum_incr = round(sum(float(r["net"]) for r in chk
                       if r["book"] == "B_increment"), 2)
assert resum_v21 == 83650.50, resum_v21
assert abs(resum_total - (83650.50 + resum_incr)) < 0.005, (resum_total, resum_incr)
assert resum_incr == gate_B["base"]["total"], (resum_incr, gate_B["base"]["total"])
print(f"independent re-sum: PASS (combined {resum_total} = v21 83650.50 "
      f"+ increment {resum_incr})")

# ---- verdict ------------------------------------------------------------------
inc = gate_B["base"]
verdict_pass = (
    inc["total"] > 0
    and inc["halves"]["H1_Jan_May"] >= -2000.0
    and inc["halves"]["H2_Jun_Oct"] >= -2000.0
    and inc["ex_top3_legs"] > 0
    and inc["total"] > gate_B["flipped"]["total"]
    and inc["total"] > gate_B["shifted30"]["total"]
    and inc["total"] > gate_B["random"]["total"])
verdict = "ADDED as separate candidate 'v21 + S/R'" if verdict_pass else "REJECTED"

anatomy = {}
for coll, name in ((A_legs, "A"), (B_incr, "B")):
    by_src = defaultdict(lambda: [0, 0.0])
    for r in coll:
        by_src[r["level_source"]][0] += 1
        by_src[r["level_source"]][1] = round(
            by_src[r["level_source"]][1] + r["net"], 2)
    anatomy[name] = {k: dict(legs=v[0], total=v[1])
                     for k, v in sorted(by_src.items())}

out = dict(
    build="Bank v21 + S/R rejection layer",
    date="2026-11-04",
    window="2026-01-01..2026-10-30 (205 trading days)",
    detection=dict(
        rejection_events=int(sum(len(v) for v in ALL_EVENTS.values())),
        first_tests=TOTAL_TESTS,
        cross_check_v1_v2="PASS",
        events_by_source={s: sum(1 for v in ALL_EVENTS.values()
                                 for e in v if e["level_source"] == s)
                          for s in sorted(SRC_PRIORITY)}),
    A_standalone=dict(gate=gate_A,
                      nc=A_nc, n_nc=len(A_nc),
                      over_cap_events=len(A_overcap),
                      deduped_within_sr=len(A_deduped)),
    B_added_book=dict(increment_gate=gate_B,
                      combined=combined_agg,
                      v21_total=83650.50,
                      combined_total=resum_total,
                      increment_total=resum_incr,
                      nc=B_nc, n_nc=len(B_nc),
                      over_cap_events=len(B_overcap),
                      deduped_vs_v21_or_sr=len(B_deduped),
                      cap_blocked=B_blocked,
                      n_cap_blocked=len(B_blocked)),
    anatomy=anatomy,
    timing_audit="PASS (level usable_time <= pattern bar for every event; "
                 "entry = next bar; entry premium == store open; exits "
                 "within [entry, 15:10]; detection v2 reproduces v1 "
                 "event-for-event)",
    independent_resum=dict(passed=True, combined=resum_total,
                           v21=resum_v21, increment=resum_incr),
    verdict=verdict,
    verdict_checks=dict(
        increment_positive=inc["total"] > 0,
        halves_ok=(inc["halves"]["H1_Jan_May"] >= -2000.0
                   and inc["halves"]["H2_Jun_Oct"] >= -2000.0),
        ex_top3_positive=inc["ex_top3_legs"] > 0,
        beats_flipped=inc["total"] > gate_B["flipped"]["total"],
        beats_shifted=inc["total"] > gate_B["shifted30"]["total"],
        beats_random=inc["total"] > gate_B["random"]["total"]),
)
(TR / "bank_sr_results.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in
                  ("detection", "verdict", "verdict_checks")}, indent=1))
print("A base:", json.dumps(gate_A["base"], indent=1))
print("A placebos:", gate_A["flipped"]["total"], gate_A["shifted30"]["total"],
      gate_A["random"]["total"], "| A NC:", len(A_nc))
print("B increment:", json.dumps(gate_B["base"], indent=1))
print("B placebos:", gate_B["flipped"]["total"],
      gate_B["shifted30"]["total"], gate_B["random"]["total"],
      "| B NC:", len(B_nc), "blocked:", len(B_blocked),
      "deduped:", len(B_deduped))
print("combined:", resum_total, "vs v21 83650.50")
print("anatomy:", json.dumps(anatomy, indent=1))
