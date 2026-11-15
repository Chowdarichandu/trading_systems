#!/usr/bin/env python3
"""DAY TRADER SKILL (Skill V3) STANDALONE TUNING — 2026-11-05.

Chandu's direction: tune Skill V3 as a standalone book. Tuning data =
Jan-Oct 2026 ONLY (203 trading days, 2026-01-01..2026-10-28, the stored
progressive spot window = the U1 window). Nov 2-4 2026 are forward
evidence and are NEVER touched here.

Signal: frozen Skill V3 (skill_v3_jansep.py definition, copied verbatim
for signal detection): OR = bars < 09:30; first 5-min close beyond OR in
09:30-11:30 = signal (CE above ORH / PE below ORL); CE bearish block
REMOVED (V3); a 09:30 PE is taken only if its close < PDL (prev trading
day's daily low), else the day ends. Entry = next 5-min bar; entry
premium = that bar's premium open. One signal max per day, so
UNIQUE-ONCE per (date, index, direction) holds by construction.
Spot-exit drops of the spot scorer (risk==0 / no-exit-bar) are NOT
applied: the premium book takes every fired signal (diff vs the stored
spot CSV is measured and reported).

Premiums: daily2leg/prem_bank.json (BANKNIFTY) / prem_nifty.json
(NIFTY), monthly series only. Store format prem[expiry|strike|TYPE]
[date][time] = [O,H,L,C]. Expiry = store_expiry_for (monthly chain,
>=10 chain days) exactly as bank_sr_score.py. Strike = atm100 of the
entry bar's spot open (progressive spot), bank_sr atm100 convention.

Baseline geometries replicate aggressive_score.replay EXACTLY (the code
that scored the Nov 2-4 standalone record): Bank mode=plain
(-50/+90, stop before target incl. entry bar, SQ at the 15:10 bar
close); Nifty mode=runner_lock50 = G7 (-50; +90 -> lock +50; +150;
SQ 15:10 close). Entry bar must be present in the premium day or the
leg is NOT_COMPUTED (counted, never estimated).

Registered families (pre-declared 2026-11-05, tested in order, no
parameter changes after seeing results):
  F1 trailing (close-based): hard stop -50; arm at +40 (close pnl);
     exit at close when close pnl <= peak_close_pnl - 25; cap +150
     (exit at close); SQ 15:10 close.
  F2 premium ladder (close-based): stages +30->lock+5, +58->lock+30,
     +82->lock+58, +100->exit at close; hard stop -50 until first lock;
     SQ 15:10 close.
  F3 tighter stop: -35/+90 Bank (plain); -35 + G7 runner shape Nifty.
  F4 entry window: drop legs with entry_time > 11:30 (incumbent exits).
  F5 direction split: CE-only / PE-only (incumbent exits) — anatomy;
     a direction book is a candidate only if it passes the full gate.

Gate (every run, same run): timing/feature audit, flipped-direction
placebo, +30-min shifted placebo, random-entry placebo (matched
count/month, seed 20261105), halves (H1 <= 2026-06-30, H2 >=
2026-07-01; pass needs both >= -2000), month table (pass needs <= 3
negative months), ex-top-3 (pass needs > 0), independent re-sum from
the written CSV. PASS = net > baseline net AND every gate leg passes.

Money: Bank lot 30 / Nifty lot 65, cost Rs 220/trade,
net = (exit-entry)*lot - 220. Paper only, real money Rs 0.
"""
import csv, json, random, sys
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import skill_v3_jansep as SK  # frozen signal machinery (load_index)

LOT = {"BANKNIFTY": 30, "NIFTY": 65}
COST = 220.0
SQ = "15:10"
RANDOM_SEED = 20261105
WINDOW = ("2026-01-01", "2026-10-31")

# ---------------- premium stores ----------------
STORES = {}
for idx, fn in (("BANKNIFTY", "prem_bank.json"), ("NIFTY", "prem_nifty.json")):
    STORES[idx] = json.load(open(TR / "daily2leg" / fn))


def store_expiry_for(store, d):
    cd = defaultdict(set)
    for k, v in store.items():
        for dd in v:
            cd[k.split("|")[0]].add(dd)
    monthly = sorted(e for e, s in cd.items() if len(s) >= 10)
    for e in monthly:
        if d <= e:
            return e
    present = {k.split("|")[0] for k, v in store.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None


EXPIRY_CACHE = {}


def expiry_for(idx, d):
    if (idx, d) not in EXPIRY_CACHE:
        EXPIRY_CACHE[(idx, d)] = store_expiry_for(STORES[idx], d)
    return EXPIRY_CACHE[(idx, d)]


def atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100


def prem_day(idx, exp, strike, typ, d):
    cd = STORES[idx].get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None:
        return None
    return sorted((t, float(v[0]), float(v[1]), float(v[2]), float(v[3]))
                  for t, v in cd.items())


# ---------------- Skill V3 signal enumeration ----------------
def enumerate_skill(idx):
    """Every fired Skill V3 signal in the window (no spot-exit drops).
    Returns (legs, diag). Leg: date, direction, signal_time, entry_time,
    entry_spot (entry bar open, progressive spot)."""
    bars_by_date, prev = SK.load_index(idx)
    legs, diag = [], defaultdict(int)
    for date in sorted(bars_by_date):
        if not (WINDOW[0] <= date <= WINDOW[1]):
            continue
        day = bars_by_date[date]
        or_bars = [b for b in day if b["time"] < "09:30"]
        if not or_bars:
            diag["no_or_bars"] += 1
            continue
        orh = max(b["high"] for b in or_bars)
        orl = min(b["low"] for b in or_bars)
        if date not in prev:
            diag["no_prev_day"] += 1
            continue
        pdl = prev[date][2]
        sig = sig_dir = None
        for b in day:
            if "09:30" <= b["time"] <= "11:30":
                if b["close"] > orh:
                    sig, sig_dir = b, "CE"
                    break
                if b["close"] < orl:
                    sig, sig_dir = b, "PE"
                    break
        if sig is None:
            diag["no_signal"] += 1
            continue
        if sig_dir == "PE" and sig["time"] == "09:30" and not (sig["close"] < pdl):
            diag["blocked_0930_pe"] += 1
            continue
        pos = next(i for i, b in enumerate(day) if b["time"] == sig["time"])
        if pos + 1 >= len(day):
            diag["no_entry_bar"] += 1
            continue
        ebar = day[pos + 1]
        legs.append(dict(index=idx, date=date, direction=sig_dir,
                         signal_time=sig["time"], entry_time=ebar["time"],
                         entry_spot=ebar["open"],
                         orh=orh, orl=orl, pdl=pdl, sig_close=sig["close"]))
    return legs, dict(diag)


# ---------------- geometry sims ----------------
def _entry_idx(bars, entry_time):
    """Index of the entry bar; None unless the exact entry bar exists."""
    for i, b in enumerate(bars):
        if b[0] == entry_time:
            return i
        if b[0] > entry_time:
            return None
    return None


def replay_bar(bars, entry_time, lot, stop_pts=50.0, target_pts=90.0,
               mode="plain"):
    """aggressive_score.replay mechanics, verbatim, on (t,o,h,l,c) bars.
    mode plain | runner_lock50. Returns dict or None."""
    if not bars:
        return None
    i0 = _entry_idx(bars, entry_time)
    if i0 is None:
        return None
    bars = bars[i0:]
    if bars[0][0] > SQ:
        return None
    entry = bars[0][1]
    stop, target = entry - stop_pts, entry + target_pts

    def sqx(b):
        return dict(net=round((b[4] - entry) * lot - COST, 2),
                    exit_reason="square_off", exit_time=b[0], ft=0,
                    entry=entry, exit=b[4])
    for i, b in enumerate(bars):
        t, o, h, l, cl = b
        if t > SQ:
            break
        if l <= stop:
            return dict(net=round((stop - entry) * lot - COST, 2),
                        exit_reason="stop", exit_time=t, ft=0,
                        entry=entry, exit=stop)
        if h >= target:
            if mode == "plain":
                return dict(net=round((target - entry) * lot - COST, 2),
                            exit_reason="target", exit_time=t, ft=1,
                            entry=entry, exit=target)
            stop2 = entry + 50.0
            target2 = entry + 150.0
            rest = None
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2 = b2
                if t2 > SQ:
                    break
                if l2 <= stop2:
                    rest = (stop2, "runner_lock", t2)
                    break
                if h2 >= target2:
                    rest = (target2, "runner_target", t2)
                    break
                if t2 == SQ:
                    rest = (cl2, "square_off", t2)
                    break
            if rest is None:
                lb = bars[-1]
                rest = (lb[4], "square_off", lb[0])
            return dict(net=round((rest[0] - entry) * lot - COST, 2),
                        exit_reason=rest[1], exit_time=rest[2], ft=1,
                        entry=entry, exit=rest[0])
        if t == SQ:
            return sqx(b)
    lb = bars[-1]
    return sqx(lb)


def sim_trail_f1(bars, entry_time, lot):
    """F1 close-based trailing. Bars from entry bar through 15:10."""
    i0 = _entry_idx(bars, entry_time)
    if i0 is None:
        return None
    path = [b for b in bars[i0:] if b[0] <= SQ]
    if not path:
        return None
    entry = path[0][1]
    peak = None
    armed = False
    for t, o, h, l, cl in path:
        pnl = cl - entry
        if pnl >= 150.0:
            return dict(net=round(pnl * lot - COST, 2),
                        exit_reason="target_cap", exit_time=t, ft=1,
                        entry=entry, exit=cl)
        if not armed and pnl <= -50.0:
            return dict(net=round(pnl * lot - COST, 2),
                        exit_reason="stop", exit_time=t, ft=0,
                        entry=entry, exit=cl)
        if peak is None or pnl > peak:
            peak = pnl
        if peak >= 40.0:
            armed = True
        if armed and pnl <= peak - 25.0:
            return dict(net=round(pnl * lot - COST, 2),
                        exit_reason="trail_exit", exit_time=t, ft=0,
                        entry=entry, exit=cl)
    t, o, h, l, cl = path[-1]
    return dict(net=round((cl - entry) * lot - COST, 2),
                exit_reason="square_off", exit_time=t, ft=0,
                entry=entry, exit=cl)


F2_STAGES = [(30.0, 5.0), (58.0, 30.0), (82.0, 58.0)]  # (arm pnl, lock pnl)


def sim_ladder_f2(bars, entry_time, lot):
    """F2 close-based premium ladder."""
    i0 = _entry_idx(bars, entry_time)
    if i0 is None:
        return None
    path = [b for b in bars[i0:] if b[0] <= SQ]
    if not path:
        return None
    entry = path[0][1]
    stop_lvl = -50.0
    locked = False
    for t, o, h, l, cl in path:
        pnl = cl - entry
        if pnl >= 100.0:
            return dict(net=round(pnl * lot - COST, 2),
                        exit_reason="ladder_exit", exit_time=t, ft=1,
                        entry=entry, exit=cl)
        for thr, lock in F2_STAGES:
            if pnl >= thr and lock > stop_lvl:
                stop_lvl = lock
                locked = True
        if pnl <= stop_lvl:
            return dict(net=round(pnl * lot - COST, 2),
                        exit_reason="lock_stop" if locked else "stop",
                        exit_time=t, ft=0, entry=entry, exit=cl)
    t, o, h, l, cl = path[-1]
    return dict(net=round((cl - entry) * lot - COST, 2),
                exit_reason="square_off", exit_time=t, ft=0,
                entry=entry, exit=cl)


def incumbent_sim(idx):
    if idx == "BANKNIFTY":
        return lambda bars, et, lot: replay_bar(bars, et, lot, 50.0, 90.0, "plain")
    return lambda bars, et, lot: replay_bar(bars, et, lot, 50.0, 90.0, "runner_lock50")


def f3_sim(idx):
    if idx == "BANKNIFTY":
        return lambda bars, et, lot: replay_bar(bars, et, lot, 35.0, 90.0, "plain")
    return lambda bars, et, lot: replay_bar(bars, et, lot, 35.0, 90.0, "runner_lock50")


# ---------------- scoring ----------------
def score_leg(idx, date, direction, entry_time, strike, sim):
    exp = expiry_for(idx, date)
    if exp is None:
        return None, "no_expiry"
    bars = prem_day(idx, exp, strike, direction, date)
    if bars is None:
        return None, f"no_contract {exp}|{strike}|{direction}"
    if _entry_idx(bars, entry_time) is None:
        return None, f"entry_bar_absent {entry_time}"
    r = sim(bars, entry_time, LOT[idx])
    if r is None:
        return None, "sim_none"
    return dict(date=date, index=idx, direction=direction, expiry=exp,
                strike=strike, entry_time=entry_time,
                entry_premium=r["entry"], exit_time=r["exit_time"],
                exit_premium=r["exit"], exit_reason=r["exit_reason"],
                ft=r["ft"], net=r["net"]), None


def score_book(idx, legs, sim, leg_filter=None):
    rows, ncs = [], []
    for lg in legs:
        if leg_filter and not leg_filter(lg):
            continue
        strike = atm100(lg["entry_spot"])
        r, why = score_leg(idx, lg["date"], lg["direction"],
                           lg["entry_time"], strike, sim)
        if r is None:
            ncs.append(dict(date=lg["date"], direction=lg["direction"],
                            entry_time=lg["entry_time"], why=why))
        else:
            r["signal_time"] = lg["signal_time"]
            rows.append(r)
    rows.sort(key=lambda x: (x["date"], x["entry_time"]))
    return rows, ncs


def add_min(t, m):
    h, mm = int(t[:2]), int(t[3:]) + m
    return f"{h + mm // 60:02d}:{mm % 60:02d}"


# ---------------- placebos ----------------
def placebo_flipped(idx, legs, sim):
    rows, ncs = [], []
    for lg in legs:
        strike = atm100(lg["entry_spot"])
        opp = "PE" if lg["direction"] == "CE" else "CE"
        r, why = score_leg(idx, lg["date"], opp, lg["entry_time"], strike, sim)
        if r is None:
            ncs.append(why)
        else:
            rows.append(r)
    return rows, ncs


def placebo_shifted(idx, legs, sim):
    rows, ncs = [], []
    for lg in legs:
        strike = atm100(lg["entry_spot"])
        et2 = add_min(lg["entry_time"], 30)
        if et2 > SQ:
            ncs.append("shift_beyond_sq")
            continue
        r, why = score_leg(idx, lg["date"], lg["direction"], et2, strike, sim)
        if r is None:
            ncs.append(why)
        else:
            rows.append(r)
    return rows, ncs


def placebo_random(idx, sim, month_counts, spot_days):
    """month_counts: {YYYY-MM: n legs}.spot_days: {date: {time: open}}."""
    rng = random.Random(RANDOM_SEED)
    rows, ncs = [], []
    grid = [f"{h:02d}:{m:02d}" for h in range(9, 15) for m in range(0, 60, 5)
            if "09:35" <= f"{h:02d}:{m:02d}" <= "14:35"]
    for month in sorted(month_counts):
        days = [d for d in sorted(spot_days) if d.startswith(month)]
        for _ in range(month_counts[month]):
            d = rng.choice(days)
            times = [t for t in grid if t in spot_days[d]]
            if not times:
                ncs.append("random_no_times")
                continue
            et = rng.choice(times)
            direction = rng.choice(["CE", "PE"])
            strike = atm100(spot_days[d][et])
            r, why = score_leg(idx, d, direction, et, strike, sim)
            if r is None:
                ncs.append(why)
            else:
                rows.append(r)
    return rows, ncs


# ---------------- stats + gate ----------------
def stats(rows):
    n = len(rows)
    net = round(sum(r["net"] for r in rows), 2)
    wins = sum(1 for r in rows if r["net"] > 0)
    ft = sum(r["ft"] for r in rows)
    bym = defaultdict(float)
    bym_n = defaultdict(int)
    for r in rows:
        bym[r["date"][:7]] += r["net"]
        bym_n[r["date"][:7]] += 1
    h1 = round(sum(r["net"] for r in rows if r["date"] <= "2026-06-30"), 2)
    h2 = round(sum(r["net"] for r in rows if r["date"] >= "2026-07-01"), 2)
    top3 = sorted((r["net"] for r in rows), reverse=True)[:3]
    ex_top3 = round(net - sum(top3), 2)
    cum, peak, dd = 0.0, 0.0, 0.0
    for r in rows:
        cum += r["net"]
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return dict(n=n, net=net,
                win_rate=round(100.0 * wins / n, 1) if n else 0.0,
                ft_rate=round(100.0 * ft / n, 1) if n else 0.0,
                months={m: dict(net=round(bym[m], 2), n=bym_n[m])
                        for m in sorted(bym)},
                neg_months=sum(1 for m in bym if bym[m] < 0),
                h1=h1, h2=h2, ex_top3=ex_top3,
                worst_drawdown=round(dd, 2),
                avg_per_leg=round(net / n, 2) if n else 0.0,
                pace_per_month=round(net / 10.0, 2))


def gate(rows, ncs, placebos, audit_ok, resum_ok, baseline_net=None):
    s = stats(rows)
    legs = dict(
        timing_audit="PASS" if audit_ok else "FAIL",
        resum="PASS" if resum_ok else "FAIL",
        halves="PASS" if (s["h1"] >= -2000 and s["h2"] >= -2000) else "FAIL",
        months="PASS" if s["neg_months"] <= 3 else "FAIL",
        ex_top3="PASS" if s["ex_top3"] > 0 else "FAIL",
        placebo_flipped="PASS" if s["net"] > placebos["flipped"]["net"] else "FAIL",
        placebo_shifted="PASS" if s["net"] > placebos["shifted"]["net"] else "FAIL",
        placebo_random="PASS" if s["net"] > placebos["random"]["net"] else "FAIL",
    )
    if baseline_net is not None:
        legs["beats_baseline"] = "PASS" if s["net"] > baseline_net else "FAIL"
    allpass = all(v == "PASS" for v in legs.values())
    return dict(stats=s, nc=len(ncs), gate=legs, gate_pass=allpass)


def write_csv(path, rows):
    cols = ["date", "index", "direction", "expiry", "strike", "signal_time",
            "entry_time", "entry_premium", "exit_time", "exit_premium",
            "exit_reason", "ft", "net"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def resum_csv(path):
    tot = Decimal("0")
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            tot += Decimal(str(r["net"]))
    return float(tot)


# ---------------- validation + audit ----------------
def validate_enumeration(idx, legs):
    """Compare against the stored Jan-Sep spot CSV and the U1 Jan-Oct
    merged keys. Returns a report dict (no scoring decisions depend on
    it; discrepancies are disclosed)."""
    rep = {}
    stored = []
    with open(TR / "index_options_U1_skillV3_jansep_spot.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["index"] == idx:
                stored.append(r)
    mine_js = {(l["date"], l["direction"], l["signal_time"], l["entry_time"])
               for l in legs if l["date"] <= "2026-09-30"}
    stored_js = {(r["date"], r["direction"], r["signal_time"], r["entry_time"])
                 for r in stored}
    rep["jansep_stored_legs"] = len(stored_js)
    rep["jansep_mine_legs"] = len(mine_js)
    rep["jansep_stored_missing_from_mine"] = sorted(stored_js - mine_js)
    rep["jansep_extra_in_mine"] = sorted(mine_js - stored_js)
    u1_keys = set()
    with open(TR / "index_options_U1_janoct_trades.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["index"] == idx and "Skill V3" in r["source_systems"]:
                u1_keys.add((r["date"], r["direction"]))
    mine_keys = {(l["date"], l["direction"]) for l in legs}
    rep["u1_skill_keys"] = len(u1_keys)
    rep["u1_skill_keys_missing_from_mine"] = sorted(u1_keys - mine_keys)
    rep["my_keys_not_in_u1"] = len(mine_keys - u1_keys)
    return rep


def audit_signals(idx, legs):
    """Causality audit on the signal set itself: OR uses only bars
    < 09:30; the signal is the FIRST close beyond OR in the window;
    PDL is the previous trading day's low; entry is the bar right
    after the signal bar; UNIQUE-ONCE keys; window discipline."""
    bars_by_date, prev = SK.load_index(idx)
    problems = []
    seen = set()
    for lg in legs:
        key = (lg["date"], lg["direction"])
        if key in seen:
            problems.append(f"dup key {key}")
        seen.add(key)
        if not ("2026-01-01" <= lg["date"] <= "2026-10-28"):
            problems.append(f"date outside window {lg['date']}")
        day = bars_by_date[lg["date"]]
        or_bars = [b for b in day if b["time"] < "09:30"]
        orh = max(b["high"] for b in or_bars)
        orl = min(b["low"] for b in or_bars)
        if abs(orh - lg["orh"]) > 1e-9 or abs(orl - lg["orl"]) > 1e-9:
            problems.append(f"OR mismatch {lg['date']}")
        if abs(prev[lg["date"]][2] - lg["pdl"]) > 1e-9:
            problems.append(f"PDL mismatch {lg['date']}")
        first = None
        for b in day:
            if "09:30" <= b["time"] <= "11:30" and (
                    b["close"] > orh or b["close"] < orl):
                first = b
                break
        if first is None or first["time"] != lg["signal_time"]:
            problems.append(f"signal not first break {lg['date']}")
        times = [b["time"] for b in day]
        si = times.index(lg["signal_time"])
        if si + 1 >= len(times) or times[si + 1] != lg["entry_time"]:
            problems.append(f"entry not next bar {lg['date']}")
    return problems


def audit_rows(idx, rows):
    """Scoring audit: entry premium == premium bar open at entry_time;
    exit_time within [entry_time, 15:10]."""
    problems = []
    for r in rows:
        bars = prem_day(idx, r["expiry"], r["strike"], r["direction"], r["date"])
        if bars is None:
            problems.append(f"row contract vanished {r['date']}")
            continue
        bd = {t: (o, h, l, c) for t, o, h, l, c in bars}
        if r["entry_time"] not in bd or abs(bd[r["entry_time"]][0]
                                           - r["entry_premium"]) > 1e-9:
            problems.append(f"entry premium mismatch {r['date']} {r['entry_time']}")
        if not (r["entry_time"] <= r["exit_time"] <= SQ):
            problems.append(f"exit window violation {r['date']} {r['exit_time']}")
    return problems


# ---------------- variant runner ----------------
def run_variant(idx, name, legs_attempted, sim, spot_days,
                baseline_net=None, audit_problems_pre=None):
    rows, ncs = score_book(idx, legs_attempted, sim)
    month_counts = defaultdict(int)
    for lg in legs_attempted:
        month_counts[lg["date"][:7]] += 1
    pb = {}
    for pname, fn in (("flipped", placebo_flipped),
                      ("shifted", placebo_shifted)):
        prows, pncs = fn(idx, legs_attempted, sim)
        pb[pname] = dict(net=round(sum(r["net"] for r in prows), 2),
                         n=len(prows), nc=len(pncs))
    prows, pncs = placebo_random(idx, sim, dict(month_counts), spot_days)
    pb["random"] = dict(net=round(sum(r["net"] for r in prows), 2),
                        n=len(prows), nc=len(pncs))
    tag = "bank" if idx == "BANKNIFTY" else "nifty"
    path = TR / f"skill_tuning_{tag}_{name}_trades.csv"
    write_csv(path, rows)
    resum = resum_csv(path)
    resum_ok = abs(resum - round(sum(r["net"] for r in rows), 2)) < 0.01
    problems = list(audit_problems_pre or []) + audit_rows(idx, rows)
    g = gate(rows, ncs, pb, audit_ok=not problems, resum_ok=resum_ok,
             baseline_net=baseline_net)
    g["placebos"] = pb
    g["nc_detail"] = ncs
    g["audit_problems"] = problems[:10]
    g["csv"] = path.name
    return rows, g


def main():
    results = {}
    for idx in ("BANKNIFTY", "NIFTY"):
        print(f"\n===== {idx} =====", flush=True)
        legs, diag = enumerate_skill(idx)
        print(f"signal days (legs): {len(legs)}  diag={diag}", flush=True)
        val = validate_enumeration(idx, legs)
        print(f"validation: jansep stored={val['jansep_stored_legs']} "
              f"mine={val['jansep_mine_legs']} "
              f"stored_missing={len(val['jansep_stored_missing_from_mine'])} "
              f"extra={len(val['jansep_extra_in_mine'])}; "
              f"u1 keys={val['u1_skill_keys']} "
              f"missing={len(val['u1_skill_keys_missing_from_mine'])}",
              flush=True)
        sig_problems = audit_signals(idx, legs)
        print(f"signal audit problems: {len(sig_problems)}", flush=True)
        # spot opens per day for the random placebo
        bars_by_date, _ = SK.load_index(idx)
        spot_days = {d: {b["time"]: b["open"] for b in day}
                     for d, day in bars_by_date.items()
                     if WINDOW[0] <= d <= WINDOW[1]}
        inc = incumbent_sim(idx)
        out = dict(legs_total=len(legs), diag=diag, validation=val,
                   signal_audit_problems=sig_problems, variants={})
        rows, g = run_variant(idx, "baseline", legs, inc, spot_days,
                              audit_problems_pre=sig_problems)
        base_net = g["stats"]["net"]
        out["variants"]["baseline"] = g
        print(f"baseline: {g['stats']} nc={g['nc']} gate={g['gate']} "
              f"placebos={ {k: v['net'] for k, v in g['placebos'].items()} }",
              flush=True)
        fam = {}
        fam["F1"] = (legs, sim_trail_f1)
        fam["F2"] = (legs, sim_ladder_f2)
        fam["F3"] = (legs, f3_sim(idx))
        fam["F4"] = ([l for l in legs if l["entry_time"] <= "11:30"], inc)
        fam["F5CE"] = ([l for l in legs if l["direction"] == "CE"], inc)
        fam["F5PE"] = ([l for l in legs if l["direction"] == "PE"], inc)
        passed = []
        for name in ("F1", "F2", "F3", "F4", "F5CE", "F5PE"):
            lgs, sim = fam[name]
            rows, g = run_variant(idx, name, lgs, sim, spot_days,
                                  baseline_net=base_net,
                                  audit_problems_pre=sig_problems)
            out["variants"][name] = g
            print(f"{name}: net={g['stats']['net']} n={g['stats']['n']} "
                  f"nc={g['nc']} gate={g['gate']} "
                  f"placebos={ {k: v['net'] for k, v in g['placebos'].items()} } "
                  f"PASS={g['gate_pass']}", flush=True)
            if g["gate_pass"]:
                passed.append(name)
        out["passed_families"] = passed
        if len(passed) >= 2:
            # combination: best passing exit family (F1/F2/F3 by net),
            # + F4 window if it passed, + direction restriction only if
            # exactly one direction book passed.
            exit_pass = [p for p in passed if p in ("F1", "F2", "F3")]
            sim = inc
            combo_desc = ["incumbent exits"]
            if exit_pass:
                best_exit = max(exit_pass,
                                key=lambda p: out["variants"][p]["stats"]["net"])
                sim = {"F1": sim_trail_f1, "F2": sim_ladder_f2,
                       "F3": f3_sim(idx)}[best_exit]
                combo_desc = [f"{best_exit} exits"]
            lgs = legs
            if "F4" in passed:
                lgs = [l for l in lgs if l["entry_time"] <= "11:30"]
                combo_desc.append("F4 window")
            dir_pass = [p for p in passed if p in ("F5CE", "F5PE")]
            if len(dir_pass) == 1:
                d = "CE" if dir_pass[0] == "F5CE" else "PE"
                lgs = [l for l in lgs if l["direction"] == d]
                combo_desc.append(f"{dir_pass[0]} only")
            rows, g = run_variant(idx, "COMBO", lgs, sim, spot_days,
                                  baseline_net=base_net,
                                  audit_problems_pre=sig_problems)
            g["combo_components"] = combo_desc
            out["variants"]["COMBO"] = g
            print(f"COMBO ({' + '.join(combo_desc)}): net={g['stats']['net']} "
                  f"n={g['stats']['n']} nc={g['nc']} gate={g['gate']} "
                  f"PASS={g['gate_pass']}", flush=True)
        results[idx] = out
    with open(TR / "skill_tuning_results.json", "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("\nwrote skill_tuning_results.json", flush=True)


if __name__ == "__main__":
    main()
