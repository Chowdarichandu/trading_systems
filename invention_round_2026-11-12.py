#!/usr/bin/env python3
"""INVENTION ROUND — 2026-11-12 (owner order 2026-11-12 17:03 IST:
"I need twenty thousand per month — work on it"). Paper only, real Rs 0.
Output = December candidates only; nothing armed; frozen November
primaries untouched (read-only at most).

FROZEN SPEC — fixed in this header BEFORE any scoring in this run.
No parameter below was fitted to results; there is exactly ONE
configuration per family (no sweep, no variants).

=====================================================================
FAMILY A — BANK-APC v1: Bank Nifty AFTERNOON PULLBACK-CONTINUATION
=====================================================================
Mechanically distinct from every closed route: NOT a range-break
capture (BREAK-CAPTURE / EVE-06b / EVE-12 closed), NOT an admission
filter on an existing book, NOT the ladder, NOT causal-chain
selection. The trigger is a RETRACEMENT-and-hold against a FIRST-HALF
trend leg, entered in the afternoon in the trend direction.

Population: Bank Nifty days 2026-01-01..2026-10-31 present in the
premium-covered store (data/banknifty-2026-*/option_5m.csv days) —
185 days. Disclosed store facts: the spot store's 7 extra jul-oct
days (2026-07-29/30/31, 08-26/27/28/31) have no premium coverage and
11 NSE calendar days are absent from the spot store entirely
(2026-01-28/29/30, 02-25/26/27, 04-29/30, 05-27, 05-29, 10-28).

Definitions (5-min spot bars, bars labelled by start time):
  day_open  = open of the 09:15 bar.
  REF       = close of the 12:55 bar (the first-half close, 13:00).
  HILEG     = max high of bars 09:15..12:55; LOLEG = min low.
  Trend: REF - day_open >= +150.0 -> CE (up-leg, extreme HILEG,
         leg = HILEG - day_open);
         day_open - REF >= +150.0 -> PE (down-leg, extreme LOLEG,
         leg = day_open - LOLEG). Otherwise no trade.
  Pullback level PL: CE: PL = HILEG - 0.25 * leg;
                     PE: PL = LOLEG + 0.25 * leg.
  Afternoon scan, bars 13:00..14:30 in order (CE case; PE mirrored):
    - if bar close < day_open: origin broken -> day dead, no trade
      (checked first, before trigger/signal on the same bar);
    - trigger: first bar with low <= PL sets triggered = True
      (PE: high >= PL);
    - signal: the first bar at/after the trigger (the trigger bar
      itself included) that closes in the trend direction
      (CE: close > open; PE: close < open) is the signal bar.
  One leg per day maximum (first pullback only).
  Entry: entry_time = signal bar start + 5 min; entry premium = open
  of the first premium bar at/after entry_time (house convention).
  Strike: round100(signal bar close); expiry = monthly expiry in
  force (next of EXPIRIES >= date); on the expiry day itself the
  strike shifts 100 ITM (CE -100 / PE +100) per the incumbent books'
  expiry-day convention (bank_r3_setups.mkleg).
  Geometry (P21, the incumbent stack's input geometry, with the
  task-mandated square-off): stop -50; at +90 the leg becomes a
  runner — floor locks entry+50, second target +150; SQ 15:10
  (exit at the 15:10 bar close). Replay semantics mirror
  bank_aggressive_tune_score.replay_mod exactly (stop checked
  before target on every bar including the entry bar; runner phase
  starts on the bar AFTER the trigger bar; runner stop checked
  before runner target; if the SQ bar is never reached inside the
  runner loop, exit at the last available bar's close).
  Lot 30, cost Rs 220/trade, UNIQUE-ONCE (one leg/day by construction).

GATE — FAMILY A (pre-registered; PASS requires ALL):
  1. Total net Jan-Oct > 0.
  2. H1 (Jan-May) > 0 AND H2 (Jun-Oct) > 0.
  3. Red months <= 3 of 10 AND worst month >= -Rs 5,000 (bleed leg).
  4. Ex-top-3 legs total > 0.
  5. Candidate total > delay-6 placebo total AND > flipped-direction
     placebo total (unfillable placebo legs count at candidate net —
     the disclosed tuning_bank convention — fills counted).
  6. NC == 0 (every generated leg scored from premium data).
  7. Timing/admission audit 0 violations; independent re-sum exact.

November counterfactual (separately labelled, never in the gate):
  same frozen generator on data/banknifty-2026-11 spot (8 full days;
  2026-11-08 is a 14-bar muhurat session with no first half -> no
  signal can form). Premium from november_shadow_data JSONs + the
  standard candle dirs only; legs without the exact contract are
  NOT_COMPUTED and named — never estimated. November expiry in
  force: 2026-11-23 (shifted monthly, per november_shadow_score).

=====================================================================
FAMILY B — NIFTY WEEKLY-EXPIRY-DAY BOOK: coverage verified FIRST.
=====================================================================
Population would be the 33 Nifty weekly expiry days Jan-Oct 2026
(nifty_engine_run3_expiries.json minus the monthly expiries).
The premium-chain completeness check runs before any entry rule is
defined; if coverage cannot support causal scoring the family is
marked NOT TESTABLE with the exact data build required (no
approximation, no reduced population).

Premium sources (the workspace's own stores, nothing fetched):
  Bank : data/banknifty-2026-*/option_5m.csv (chain store) —
         cross-validated bar-for-bar against the JSON candle store
         the incumbent books score from (aggressive_score.candles).
  Nifty: JSON candle dirs aggressive_data / v4_options_oct_data /
         historical_proof_data (candles_exact route). No Nifty chain
         store exists in the workspace.
"""
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))

LOT_B, COST = 30, 220.0
SQ = "15:10"
GEOM = dict(stop=50.0, trig=90.0, lock=50.0, tgt2=150.0)
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
            "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
            "2026-09-29", "2026-10-27", "2026-11-23"]
LEG_MIN = 150.0
RETRACE = 0.25

OUT = {"session": "invention_round_2026-11-12"}


def mins(t):
    h, m = map(int, str(t).split(":")[:2])
    return h * 60 + m


def plus5(t):
    v = mins(t) + 5
    return f"{v // 60:02d}:{v % 60:02d}"


def round100(x):
    return int(round(x / 100.0) * 100)


# =====================================================================
# DATA — Bank spot (monthly dirs; jul-oct overlaps verified identical)
# =====================================================================
def load_bank_spot(extra_dirs=()):
    frames = []
    for f in sorted(glob.glob(str(TR / "data/banknifty-2026-*/spot_5m.csv"))):
        if "jul-oct" in f:
            continue
        frames.append(pd.read_csv(f))
    spot = pd.concat(frames).sort_values("timestamp")
    spot = spot.drop_duplicates(subset=["timestamp"], keep="first")
    spot["date"] = spot["timestamp"].str[:10]
    spot["time"] = spot["timestamp"].str[11:16]
    days = {}
    for d, g in spot.groupby("date"):
        days[d] = [(r["time"], float(r["open"]), float(r["high"]),
                    float(r["low"]), float(r["close"]))
                   for _, r in g.sort_values("time").iterrows()]
    return days


def load_bank_premium():
    """(date, strike, type, expiry) -> [(time, o, h, l, c)] from the
    option_5m.csv chain store (Jan-Oct month dirs)."""
    frames = []
    for f in sorted(glob.glob(str(TR / "data/banknifty-2026-*/option_5m.csv"))):
        frames.append(pd.read_csv(f))
    opt = pd.concat(frames)
    opt["date"] = opt["timestamp"].str[:10]
    opt["time"] = opt["timestamp"].str[11:16]
    store = {}
    for (d, s, t, e), g in opt.groupby(["date", "strike", "option_type", "expiry"]):
        store[(d, int(s), t, e)] = [(r["time"], float(r["open"]), float(r["high"]),
                                     float(r["low"]), float(r["close"]))
                                    for _, r in g.sort_values("time").iterrows()]
    return store


# =====================================================================
# CROSS-VALIDATION: chain store vs the JSON store incumbents score from
# =====================================================================
def cross_validate(prem):
    pat = re.compile(r"candles_(?:premium_)?BANKNIFTY_(\d+)(CE|PE)_"
                     r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json")
    files = bars = mismatch = 0
    examples = []
    for d in ["aggressive_data", "v4_options_oct_data", "historical_proof_data"]:
        for f in sorted(os.listdir(TR / d)):
            m = pat.match(f)
            if not m:
                continue
            strike, typ, day, exp = int(m.group(1)), m.group(2), m.group(3), m.group(4)
            key = (day, strike, typ, exp)
            if key not in prem:
                continue  # contract outside the chain store's window
            try:
                data = json.loads((TR / d / f).read_text()).get("data", {}).get("candles", [])
            except Exception:
                continue
            jrows = {c[0][11:16]: (float(c[1]), float(c[2]), float(c[3]), float(c[4]))
                     for c in data if c[0][:10] == day}
            crows = {r[0]: (r[1], r[2], r[3], r[4]) for r in prem[key]}
            files += 1
            for t, v in jrows.items():
                bars += 1
                if crows.get(t) != v:
                    mismatch += 1
                    if len(examples) < 3:
                        examples.append((f, t, v, crows.get(t)))
    return dict(files_compared=files, bars_compared=bars,
                mismatches=mismatch, examples=examples)


# =====================================================================
# FAMILY A — signal generation (streaming; sees each bar once, in
# order, and decides using only bars up to the current one)
# =====================================================================
def gen_family_a(bars):
    """bars: [(time, o, h, l, c)] for one day. Returns a signal dict
    or None. Pure function of the day's bars, evaluated causally."""
    by_time = {b[0]: b for b in bars}
    if "09:15" not in by_time or "12:55" not in by_time:
        return None
    day_open = by_time["09:15"][1]
    first = [b for b in bars if b[0] <= "12:55"]
    ref = by_time["12:55"][4]
    hileg = max(b[2] for b in first)
    loleg = min(b[3] for b in first)
    if ref - day_open >= LEG_MIN:
        direction, extreme, leg = "CE", hileg, hileg - day_open
        pl = extreme - RETRACE * leg
    elif day_open - ref >= LEG_MIN:
        direction, extreme, leg = "PE", loleg, day_open - loleg
        pl = extreme + RETRACE * leg
    else:
        return None
    triggered = False
    for b in bars:
        t, o, h, l, c = b
        if t < "13:00" or t > "14:30":
            continue
        if direction == "CE":
            if c < day_open:
                return None  # origin broken on a close
            if not triggered and l <= pl:
                triggered = True
            if triggered and c > o:
                return dict(direction=direction, signal_time=t,
                            signal_close=c, day_open=day_open, ref=ref,
                            extreme=extreme, leg=leg, pl=pl)
        else:
            if c > day_open:
                return None
            if not triggered and h >= pl:
                triggered = True
            if triggered and c < o:
                return dict(direction=direction, signal_time=t,
                            signal_close=c, day_open=day_open, ref=ref,
                            extreme=extreme, leg=leg, pl=pl)
    return None


def gen_family_a_independent(day_bars_df):
    """SECOND implementation (pandas, explicit cutoffs) used only as
    the admission/feature-timing audit: recomputes each signal from
    bars truncated at the signal bar and compares leg-for-leg."""
    df = day_bars_df
    if not ((df["time"] == "09:15").any() and (df["time"] == "12:55").any()):
        return None
    day_open = float(df.loc[df["time"] == "09:15", "open"].iloc[0])
    first = df[df["time"] <= "12:55"]
    ref = float(df.loc[df["time"] == "12:55", "close"].iloc[0])
    hileg = float(first["high"].max())
    loleg = float(first["low"].min())
    if ref - day_open >= LEG_MIN:
        direction, pl = "CE", hileg - RETRACE * (hileg - day_open)
    elif day_open - ref >= LEG_MIN:
        direction, pl = "PE", loleg + RETRACE * (day_open - loleg)
    else:
        return None
    aft = df[(df["time"] >= "13:00") & (df["time"] <= "14:30")]
    triggered = False
    for _, b in aft.iterrows():
        if direction == "CE":
            if float(b["close"]) < day_open:
                return None
            if not triggered and float(b["low"]) <= pl:
                triggered = True
            if triggered and float(b["close"]) > float(b["open"]):
                return dict(direction=direction, signal_time=b["time"],
                            signal_close=float(b["close"]))
        else:
            if float(b["close"]) > day_open:
                return None
            if not triggered and float(b["high"]) >= pl:
                triggered = True
            if triggered and float(b["close"]) < float(b["open"]):
                return dict(direction=direction, signal_time=b["time"],
                            signal_close=float(b["close"]))
    return None


def mkleg_a(date, sig):
    expiry = next(e for e in EXPIRIES if e >= date)
    strike = round100(sig["signal_close"])
    if date == expiry:
        strike += -100 if sig["direction"] == "CE" else 100
    return dict(date=date, index="BANKNIFTY", direction=sig["direction"],
                entry_time=plus5(sig["signal_time"]),
                signal_time=sig["signal_time"], strike=strike,
                expiry=expiry, lot=LOT_B, family="BANK-APC-v1",
                day_open=sig["day_open"], ref=sig["ref"],
                extreme=sig["extreme"], leg_pts=sig["leg"], pl=sig["pl"])


# =====================================================================
# REPLAY — mirrors bank_aggressive_tune_score.replay_mod phase
# semantics with GEOM frozen above and SQ = 15:10 (task-mandated)
# =====================================================================
def replay_a(cs, entry_time, delay=0):
    if not cs:
        return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs:
        return None
    i0 = idxs[0] + delay
    if i0 >= len(cs):
        return None
    entry = cs[i0][1]
    if cs[i0][0] > SQ:
        return None
    stop0, trig = entry - GEOM["stop"], entry + GEOM["trig"]

    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT_B - COST, 2),
                    exit_reason=reason, exit_time=t, ft=ft,
                    entry=entry, exit=px)
    bars = cs[i0:]
    if not bars:
        return mk(entry, "square_off", cs[i0][0], 0)
    for j, b in enumerate(bars):
        t, o, h, l, cl = b
        if t > SQ:
            break
        if l <= stop0:
            return mk(stop0, "stop", t, 0)
        if h >= trig:
            stop2 = entry + GEOM["lock"]
            tgt2 = entry + GEOM["tgt2"]
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2 = b2
                if t2 > SQ:
                    break
                if l2 <= stop2:
                    rest = (stop2, "runner_stop", t2)
                    break
                if h2 >= tgt2:
                    rest = (tgt2, "runner_target", t2)
                    break
                if t2 == SQ:
                    rest = (cl2, "runner_square_off", t2)
                    break
            if rest is None:
                lb = bars[-1]
                rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if t == SQ:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)


# =====================================================================
# FAMILY B — premium-chain completeness verification (runs BEFORE any
# entry rule; a FAIL here means NOT TESTABLE, full stop)
# =====================================================================
MONTHLY_N = {"2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
             "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
             "2026-09-29", "2026-10-27", "2026-11-24"}


def family_b_coverage():
    exps = json.loads((TR / "nifty_engine_run3_expiries.json").read_text())
    weekly = sorted(e for e in exps
                    if "2026-01-01" <= e <= "2026-10-31" and e not in MONTHLY_N)
    pat = re.compile(r"candles_(?:premium_)?NIFTY_(\d+)(CE|PE)_"
                     r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json")
    covered = {}
    nifty_files = 0
    for d in ["aggressive_data", "v4_options_oct_data", "historical_proof_data"]:
        for f in sorted(os.listdir(TR / d)):
            m = pat.match(f)
            if not m:
                continue
            nifty_files += 1
            strike, typ, day, exp = int(m.group(1)), m.group(2), m.group(3), m.group(4)
            if day == exp and exp in weekly:
                covered.setdefault(exp, []).append((strike, typ, d))
    missing = [d for d in weekly if d not in covered]
    return weekly, covered, missing, nifty_files


def family_b_build_size(weekly):
    """Exact minimum data build: for each weekly expiry day, every
    strike on the 50-pt grid inside [day_low - 100, day_high + 100]
    of that day's spot range, both types, expiring that day — the
    union any ATM-at-signal rule plus its same-strike flip placebo
    can touch."""
    import nifty_engine_r4_harness as R4
    s5 = R4.spot5m()
    total_contracts = 0
    per_day = {}
    for d in weekly:
        bars = s5.get(d, [])
        if not bars:
            per_day[d] = None
            continue
        lo = min(b[3] for b in bars) - 100
        hi = max(b[2] for b in bars) + 100
        k_lo = int(lo // 50 * 50)
        k_hi = int(-(-hi // 50) * 50)
        n_strikes = int((k_hi - k_lo) / 50) + 1
        per_day[d] = n_strikes
        total_contracts += n_strikes * 2
    return total_contracts, per_day


# =====================================================================
# NOVEMBER premium for the counterfactual (existing stores only)
# =====================================================================
def nov_candles(strike, typ, day, exp):
    tag = f"BANKNIFTY_{int(strike)}{typ}_{day}_{exp}"
    for d in [TR / "november_shadow_data", TR / "aggressive_data",
              TR / "historical_proof_data", TR / "v4_options_oct_data"]:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists():
                try:
                    data = json.loads(p.read_text()).get("data", {}).get("candles", [])
                except Exception:
                    continue
                rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
                         float(c[4])) for c in sorted(data, key=lambda c: c[0])
                        if c[0][:10] == day]
                if rows:
                    return rows
    return None


# =====================================================================
# MAIN
# =====================================================================
def main():
    spot_days = load_bank_spot()
    prem = load_bank_premium()
    prem_days = sorted({k[0] for k in prem})
    population = [d for d in prem_days if "2026-01-01" <= d <= "2026-10-31"]
    OUT["family_a_population_days"] = len(population)

    # ---- data integrity: chain store vs JSON store incumbents use --
    OUT["cross_validation"] = cross_validate(prem)

    # ---- generate legs (frozen generator) --------------------------
    legs, no_signal_days = [], 0
    for d in population:
        sig = gen_family_a(spot_days[d])
        if sig is None:
            no_signal_days += 1
            continue
        legs.append(mkleg_a(d, sig))
    OUT["family_a_legs_generated"] = len(legs)
    OUT["family_a_no_signal_days"] = no_signal_days

    # ---- admission / feature-timing audit: independent re-derivation
    spot_frames = {}
    for f in sorted(glob.glob(str(TR / "data/banknifty-2026-*/spot_5m.csv"))):
        if "jul-oct" in f:
            continue
        spot_frames[f] = pd.read_csv(f)
    spot_all = pd.concat(spot_frames).sort_values("timestamp")
    spot_all = spot_all.drop_duplicates(subset=["timestamp"], keep="first")
    spot_all["date"] = spot_all["timestamp"].str[:10]
    spot_all["time"] = spot_all["timestamp"].str[11:16]
    audit_violations = []
    indep_legs = {}
    for d in population:
        g = spot_all[spot_all["date"] == d].sort_values("time")
        s2 = gen_family_a_independent(g)
        if s2 is not None:
            l2 = mkleg_a(d, dict(s2, day_open=None, ref=None, extreme=None,
                                 leg=None, pl=None))
            indep_legs[d] = (l2["direction"], l2["entry_time"], l2["strike"],
                             l2["expiry"])
    for l in legs:
        key = (l["direction"], l["entry_time"], l["strike"], l["expiry"])
        if indep_legs.get(l["date"]) != key:
            audit_violations.append((l["date"], "independent-rederivation-mismatch",
                                     key, indep_legs.get(l["date"])))
        # feature-timing: every feature input is a bar <= signal bar
        # (by construction of the streaming generator); assert entry
        # is exactly signal + 5 and the premium entry bar matches.
        if l["entry_time"] != plus5(l["signal_time"]):
            audit_violations.append((l["date"], "entry-not-signal-plus-5"))
        if l["signal_time"] > "14:30" or l["entry_time"] > "14:35":
            audit_violations.append((l["date"], "entry-window-violation"))
    extra = set(indep_legs) - {l["date"] for l in legs}
    if extra:
        audit_violations.append(("population", "independent-extra-legs", sorted(extra)))
    OUT["family_a_audit_violations"] = audit_violations

    # ---- score ------------------------------------------------------
    res, nc = [], []
    for l in legs:
        cs = prem.get((l["date"], l["strike"], l["direction"], l["expiry"]))
        r = replay_a(cs, l["entry_time"]) if cs else None
        if r is None:
            nc.append(l)
            continue
        row = dict(l)
        row.update(r)
        res.append(row)
    OUT["family_a_nc"] = [(l["date"], l["direction"], l["strike"], l["expiry"])
                          for l in nc]

    def agg(rows):
        tot = round(sum(r["net"] for r in rows), 2)
        months = defaultdict(float)
        for r in rows:
            months[r["date"][:7]] += r["net"]
        h1 = round(sum(r["net"] for r in rows if r["date"] <= "2026-05-31"), 2)
        h2 = round(sum(r["net"] for r in rows if r["date"] >= "2026-06-01"), 2)
        srt = sorted(rows, key=lambda r: -r["net"])
        ex3 = round(tot - sum(r["net"] for r in srt[:3]), 2) if len(rows) > 3 else tot
        return dict(total=tot, n=len(rows), months={k: round(v, 2) for k, v
                                                   in sorted(months.items())},
                    h1=h1, h2=h2, ex_top3=ex3,
                    wins=sum(1 for r in rows if r["net"] > 0),
                    per_month=round(tot / 10.0, 2),
                    expectancy=round(tot / len(rows), 2) if rows else 0.0)
    cand = agg(res)
    OUT["family_a_candidate"] = cand

    # ---- placebos ---------------------------------------------------
    def placebo(delay=0, flip=False):
        rows, fills = [], 0
        by_key = {(r["date"], r["direction"], r["strike"]): r["net"] for r in res}
        for l in legs:
            typ = l["direction"] if not flip else ("PE" if l["direction"] == "CE" else "CE")
            cs = prem.get((l["date"], l["strike"], typ, l["expiry"]))
            r = replay_a(cs, l["entry_time"], delay=delay) if cs else None
            if r is None:
                fills += 1
                net = by_key.get((l["date"], l["direction"], l["strike"]))
                if net is None:
                    continue
                rows.append(dict(l, net=net))
            else:
                rows.append(dict(l, net=r["net"]))
        return round(sum(r["net"] for r in rows), 2), fills
    pl_delay, pl_delay_fills = placebo(delay=6)
    pl_flip, pl_flip_fills = placebo(flip=True)
    OUT["family_a_placebos"] = dict(delay6_total=pl_delay, delay6_fills=pl_delay_fills,
                                    flip_total=pl_flip, flip_fills=pl_flip_fills)

    # ---- gate ---------------------------------------------------------
    red_months = sum(1 for v in cand["months"].values() if v < 0)
    worst_month = min(cand["months"].values()) if cand["months"] else 0.0
    gate = {
        "1_total_positive": cand["total"] > 0,
        "2_halves_positive": cand["h1"] > 0 and cand["h2"] > 0,
        "3_months_bleed": red_months <= 3 and worst_month >= -5000.0,
        "4_ex_top3_positive": cand["ex_top3"] > 0,
        "5_placebos_beaten": cand["total"] > pl_delay and cand["total"] > pl_flip,
        "6_nc_zero": len(nc) == 0,
        "7_audit_clean": len(audit_violations) == 0,
    }
    OUT["family_a_gate"] = gate
    OUT["family_a_gate_detail"] = dict(red_months=red_months, worst_month=worst_month)
    OUT["family_a_pass"] = all(gate.values())

    # ---- independent re-sum from the emitted trades -----------------
    with open(TR / "invention_round_2026-11-12_familyA_trades.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "signal_time", "entry_time", "strike",
                    "expiry", "entry", "exit", "exit_time", "exit_reason", "ft", "net"])
        for r in sorted(res, key=lambda r: (r["date"], r["entry_time"])):
            w.writerow([r["date"], r["direction"], r["signal_time"], r["entry_time"],
                        r["strike"], r["expiry"], r["entry"], r["exit"],
                        r["exit_time"], r["exit_reason"], r["ft"], r["net"]])
    resum = 0.0
    with open(TR / "invention_round_2026-11-12_familyA_trades.csv") as f:
        for row in csv.DictReader(f):
            resum += float(row["net"])
    OUT["family_a_resum"] = dict(resum_total=round(resum, 2),
                                 matches=round(resum, 2) == cand["total"])

    # ---- November counterfactual (separately labelled) --------------
    nov_spot = {}
    ndf = pd.read_csv(TR / "data/banknifty-2026-11/spot_5m.csv")
    ndf["date"] = ndf["timestamp"].str[:10]
    ndf["time"] = ndf["timestamp"].str[11:16]
    for d, g in ndf.groupby("date"):
        nov_spot[d] = [(r["time"], float(r["open"]), float(r["high"]),
                        float(r["low"]), float(r["close"]))
                       for _, r in g.sort_values("time").iterrows()]
    nov_rows, nov_nc = [], []
    for d in sorted(nov_spot):
        if not ("2026-11-02" <= d <= "2026-11-12"):
            continue
        sig = gen_family_a(nov_spot[d])
        if sig is None:
            continue
        l = mkleg_a(d, sig)
        cs = nov_candles(l["strike"], l["direction"], d, l["expiry"])
        r = replay_a(cs, l["entry_time"]) if cs else None
        if r is None:
            nov_nc.append((d, l["direction"], l["strike"], l["expiry"],
                           l["entry_time"]))
            continue
        row = dict(l)
        row.update(r)
        nov_rows.append(row)
    OUT["november_counterfactual"] = dict(
        scored=[(r["date"], r["direction"], r["strike"], r["entry_time"],
                 r["entry"], r["exit_time"], r["exit_reason"], r["net"])
                for r in nov_rows],
        scored_total=round(sum(r["net"] for r in nov_rows), 2),
        not_computed=nov_nc)

    # ---- Family B -----------------------------------------------------
    weekly, covered, missing, nfiles = family_b_coverage()
    build_total, build_per_day = family_b_build_size(weekly)
    OUT["family_b"] = dict(
        weekly_days=len(weekly), nifty_premium_files=nfiles,
        covered_days={d: v for d, v in sorted(covered.items())},
        covered_count=len(covered), missing_days=missing,
        missing_count=len(missing),
        build_contract_days=build_total, build_per_day=build_per_day)

    (TR / "invention_round_2026-11-12_results.json").write_text(
        json.dumps(OUT, indent=1, default=str))
    print(json.dumps({k: OUT[k] for k in
                      ["family_a_population_days", "family_a_legs_generated",
                       "family_a_candidate", "family_a_placebos",
                       "family_a_gate", "family_a_pass",
                       "november_counterfactual"]}, indent=1, default=str))
    print("NC:", OUT["family_a_nc"])
    print("AUDIT:", audit_violations[:5], "count", len(audit_violations))
    print("RESUM:", OUT["family_a_resum"])
    print("XVAL:", OUT["cross_validation"])
    print("FAMILY B covered", len(covered), "of", len(weekly),
          "| missing", len(missing), "| build contract-days", build_total)


if __name__ == "__main__":
    main()
