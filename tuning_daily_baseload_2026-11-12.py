#!/usr/bin/env python3
"""DAILY BASE-LOAD FALLBACK — tuning programme 2026-11-12 (owner
directive 2026-11-12 20:23 IST: "Tune it — something is missing").
Paper only, real Rs 0. December candidates / forward shadows only;
frozen November primaries untouched (read-only at most).

DIAGNOSIS (owner's terms): the index books wait for perfect signals
and sit IDLE (Nifty primary 1 trade in 8 November days; Bank stack
legs on a minority of days) while the market moves daily. The owner's
Nov-3 design mandated a daily base-load layer under the quality
layer; for the long-premium signal books that layer was never built
(only the premium-selling SHORT-FOLLOW exists). This programme builds
and gates it.

=====================================================================
FROZEN SPEC — BASE-LOAD FALLBACK v1 (fixed BEFORE any scoring)
=====================================================================
Trigger time T = 13:30, both indices.
Eligibility (per index, per trading day): the incumbent book
  BANK  = TUNED STACK v2 (eve19 leg set, +127,351.50 / 111 legs)
  NIFTY = TUNED v1 (DEC-S1 minus B PE, +103,050.25 / 74 legs)
has taken NO leg with entry_time <= 13:30 that day.
Signal: from the day's U1 sysmap (systems: (lA) v2, V5 v2, Skill V3,
Volrix (b); per (date, direction) earliest entry_time per system —
NIFTY: nifty_engine_r5_ws0.build_sysmap verbatim; BANK: the identical
builder mirrored to BANKNIFTY from the same source CSVs, minus the
NIFTY-only Volrix merge hardcode — no Bank analogue exists on record;
disclosed), take all signals with 13:30 <= entry_time <= 15:05. t* =
the earliest such time across both directions. If BOTH directions
hold a signal at exactly t* -> ambiguous, no leg (Family B tie-break).
Direction = the direction at t*.
Race rule: let u = the incumbent's first leg entry_time that day
(u > 13:30 by eligibility). If u exists and u <= t* -> no fallback
(the incumbent took the afternoon first / same bar — never duplicate).
If no u, or u > t*, the fallback fires at t*.
Contract: strike = atm100(spot OPEN at t*) (each index's house
atm100: BANK tuning_bank round-half-down; NIFTY R6 floor(x/100+.5));
expiry = monthly expiry in force; entry fill = premium bar open at t*.
Geometry: BANK — sim_g0 (stop -50 / target +90 / SQ = 15:10 bar open,
bars scanned to 15:05), lot 30. NIFTY — TUNED v1 geometry
(STANDING_GEOM via replay_r5: stop -50, arm +50, tgt1 +90 -> runner
lock +60 / tgt2 +175, SQ 15:20), lot 65. Cost Rs 220/trade.
At most ONE fallback leg per day; incumbent legs never altered.

GATE (pre-registered, per variant, vs its incumbent) — PASS requires:
  G1 combined total > incumbent total
  G2 no new red month: red-month set(combined) subset of incumbent's
  G3 combined ex-top-3 legs >= incumbent ex-top-3 legs
  G4 combined total > delay-6 placebo combined total AND
     > random-time placebo combined total (seed 20261112; unfillable
     placebo legs count at candidate net — disclosed house convention)
  G5 traded-day rate materially higher: combined traded days/month
     >= incumbent + 2.0
  Hygiene: fallback NC == 0; sysmap re-derivation (independent pandas
  implementation) reproduces the fallback leg set exactly; per-leg
  entry audit clean (entry premium == scoring-store bar open at t*;
  strike == atm100(spot open at t*)); truncation spot-proof passes;
  independent re-sum from emitted trades CSVs exact.
"""
import csv, json, math, random, sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path.home() / "workspace/trading"))
TR = Path.home() / "workspace/trading"
COST = 220.0
TRIGGER = "13:30"
LAST_ENTRY = "15:05"
SEED = 20261112

def mins(t): return int(t[:2]) * 60 + int(t[3:])

# =====================================================================
# shared battery over unified results [{date, net}]
# =====================================================================
def battery(results, trading_days):
    total = round(sum(r["net"] for r in results), 2)
    bym = defaultdict(float); bym_n = defaultdict(int)
    for r in results:
        bym[r["date"][:7]] += r["net"]; bym_n[r["date"][:7]] += 1
    months = {}
    for m in sorted({d[:7] for d in trading_days}):
        months[m] = [round(bym.get(m, 0.0), 2), bym_n.get(m, 0)]
    h1 = round(sum(v[0] for k, v in months.items() if k <= "2026-05"), 2)
    h2 = round(sum(v[0] for k, v in months.items() if k >= "2026-06"), 2)
    top3 = sorted((r["net"] for r in results), reverse=True)[:3]
    ex_top3 = round(total - sum(top3), 2)
    byd = defaultdict(float)
    for r in results: byd[r["date"]] += r["net"]
    top3d = sorted(byd.values(), reverse=True)[:3]
    ex_top3_days = round(total - sum(top3d), 2)
    traded = len(byd)
    return dict(total=total, n=len(results), months=months, halves={"Jan-May": h1, "Jun-Oct": h2},
                red_months=[m for m, v in months.items() if v[0] < 0],
                top3=[round(x, 2) for x in top3], ex_top3_legs=ex_top3,
                ex_top3_days=ex_top3_days, traded_days=traded,
                traded_days_per_month=round(traded / 10.0, 2),
                trading_days=len(trading_days))

def gate_verdict(inc, comb, fb_batt, pl_delay_total, pl_rand_total):
    checks = {
        "G1_total_beats_incumbent": comb["total"] > inc["total"],
        "G2_no_new_red_month": set(comb["red_months"]) <= set(inc["red_months"]),
        "G3_ex_top3_not_worse": comb["ex_top3_legs"] >= inc["ex_top3_legs"],
        "G4a_beats_delay6_placebo": comb["total"] > pl_delay_total,
        "G4b_beats_random_placebo": comb["total"] > pl_rand_total,
        "G5_traded_rate_materially_higher":
            comb["traded_days_per_month"] >= inc["traded_days_per_month"] + 2.0,
    }
    return checks

# =====================================================================
# BANK
# =====================================================================
def build_sysmap_bank():
    """build_sysmap (nifty_engine_r5_ws0) mirrored to BANKNIFTY:
    same files, same October merge rules, no Volrix merge hardcode
    (that hardcode is a NIFTY 2026-10-09 entry; no Bank analogue)."""
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "BANKNIFTY" or not et: return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    for r in csv.DictReader(open(TR / "index_options_o1_janoct_trades.csv")):
        if r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2": put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["track"] == "V5-v2": put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_skillV3_jansep_spot.csv")):
        put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_volrixB_jansep_spot.csv")):
        put(r["entry_date"], r["index"], r["direction"], "Volrix (b)", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_premium_october_trades.csv")):
        if r["premium_status"] != "COMPUTED": continue
        if r["version"].startswith("(lA)"): put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["version"].startswith("V5"): put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_skill_tuned_oct30_trades.csv")):
        if r["variant"] == "V3" and r["premium_status"] == "COMPUTED":
            put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    return S

def rederive_sysmap_bank_pandas():
    """Independent second implementation (pandas) of the same rules —
    the Family B audit pattern."""
    import pandas as pd
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "BANKNIFTY" or not et or (isinstance(et, float) and pd.isna(et)): return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    o1 = pd.read_csv(TR / "index_options_o1_janoct_trades.csv", dtype=str)
    for r in o1.itertuples():
        if r.date >= "2026-10-01": continue
        if r.track == "(lA) v2": put(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.track == "V5-v2": put(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    sk = pd.read_csv(TR / "index_options_U1_skillV3_jansep_spot.csv", dtype=str)
    for r in sk.itertuples(): put(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    vx = pd.read_csv(TR / "index_options_U1_volrixB_jansep_spot.csv", dtype=str)
    for r in vx.itertuples(): put(r.entry_date, r.index, r.direction, "Volrix (b)", r.entry_time)
    po = pd.read_csv(TR / "index_options_premium_october_trades.csv", dtype=str)
    for r in po.itertuples():
        if r.premium_status != "COMPUTED": continue
        if r.version.startswith("(lA)"): put(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.version.startswith("V5"): put(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    so30 = pd.read_csv(TR / "index_options_skill_tuned_oct30_trades.csv", dtype=str)
    for r in so30.itertuples():
        if r.variant == "V3" and r.premium_status == "COMPUTED":
            put(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    return S

# --- Bank stores (daily2leg machinery, as tuning_bank_2026-11-12) ----
_spot_raw = json.load(open(TR / "daily2leg/spot.json"))["BANKNIFTY"]
_prem_bank = json.load(open(TR / "daily2leg/prem_bank.json"))
BANK_DAYS = sorted(d for d in _spot_raw if "2026-01-01" <= d <= "2026-10-31"
                   and len(_spot_raw[d]) >= 74)
BSPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in _spot_raw[d]} for d in BANK_DAYS}
_chain_days = defaultdict(set)
for k, v in _prem_bank.items():
    for d in v: _chain_days[k.split("|")[0]].add(d)
BANK_MONTHLY = sorted(e for e, ds in _chain_days.items() if len(ds) >= 10)

def bank_expiry_for(d):
    for e in BANK_MONTHLY:
        if d <= e: return e
    present = {k.split("|")[0] for k, v in _prem_bank.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None

def bank_atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def bank_prem_day(exp, strike, typ, d):
    cd = _prem_bank.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None: return None
    return {t: tuple(float(x) for x in v) for t, v in cd.items()}

_opt5m_cache = {}
def bank_prem_day_opt5m(exp, strike, typ, d):
    """Backup source: data/banknifty-2026-MM/option_5m.csv (full chain)."""
    import pandas as pd
    m = d[:7]
    if m not in _opt5m_cache:
        f = TR / f"data/banknifty-{m}/option_5m.csv"
        if not f.exists(): _opt5m_cache[m] = None
        else:
            df = pd.read_csv(f, dtype={"strike": int, "option_type": str, "expiry": str})
            df["date"] = df["timestamp"].str[:10]; df["time"] = df["timestamp"].str[11:16]
            _opt5m_cache[m] = df
    df = _opt5m_cache[m]
    if df is None: return None
    sel = df[(df["date"] == d) & (df["strike"] == int(strike)) &
             (df["option_type"] == typ) & (df["expiry"] == exp)]
    if sel.empty: return None
    return {r.time: (float(r.open), float(r.high), float(r.low), float(r.close))
            for r in sel.itertuples()}

def sim_g0(pd, entry_time, entry_prem, lot=30):
    stop_lvl, tgt_lvl = entry_prem - 50.0, entry_prem + 90.0
    for t in sorted(pd):
        if t < entry_time or t > "15:05": continue
        o, h, l, c = pd[t]
        if l <= stop_lvl: return t, stop_lvl, "stop"
        if h >= tgt_lvl: return t, tgt_lvl, "target"
    if "15:10" in pd: return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def bank_fallback_legset(S, inc_by_day):
    """Frozen rule -> candidate fallback legs (unscored) + exclusions."""
    legs, excluded = [], []
    for d in BANK_DAYS:
        inc_times = sorted(inc_by_day.get(d, []))
        if inc_times and inc_times[0] <= TRIGGER:
            continue  # incumbent took a leg by 13:30 — not eligible
        u = inc_times[0] if inc_times else None
        cands = []
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((d, dirn), {}).items():
                if t and TRIGGER <= t <= LAST_ENTRY:
                    cands.append((t, dirn, sysname))
        if not cands:
            excluded.append((d, "no-u1-signal-after-1330")); continue
        tstar = min(c[0] for c in cands)
        dirs_at = {c[1] for c in cands if c[0] == tstar}
        if len(dirs_at) > 1:
            excluded.append((d, f"tie-at-{tstar}")); continue
        if u is not None and u <= tstar:
            excluded.append((d, f"incumbent-first-{u}")); continue
        dirn = next(iter(dirs_at))
        if tstar not in BSPOT.get(d, {}):
            excluded.append((d, "no-spot-bar-at-tstar")); continue
        strike = bank_atm100(BSPOT[d][tstar][0])
        legs.append(dict(date=d, direction=dirn, entry_time=tstar,
                         strike=strike, expiry=bank_expiry_for(d),
                         systems=sorted(c[2] for c in cands if c[0] == tstar
                                        and c[1] == dirn),
                         flat_day=(u is None)))
    return legs, excluded

def bank_score_leg(leg, entry_time=None, same_contract=True):
    et = entry_time or leg["entry_time"]
    pd = bank_prem_day(leg["expiry"], leg["strike"], leg["direction"], leg["date"])
    src = "prem_bank"
    if pd is None:
        pd = bank_prem_day_opt5m(leg["expiry"], leg["strike"], leg["direction"], leg["date"])
        src = "option_5m"
    if pd is None or et not in pd:
        return None, src
    ep = pd[et][0]
    xt, xp, reason = sim_g0(pd, et, ep)
    return dict(date=leg["date"], direction=leg["direction"], entry_time=et,
                strike=leg["strike"], expiry=leg["expiry"], entry=ep,
                exit_time=xt, exit=xp, exit_reason=reason,
                net=round((xp - ep) * 30 - COST, 2), src=src), src

def stage_bank():
    S = build_sysmap_bank()
    # incumbent: eve19 anchor CSV
    inc_rows = list(csv.DictReader(open(TR / "bank_positive_tuning_2026-11-10_eve19_trades.csv")))
    assert len(inc_rows) == 111, len(inc_rows)
    inc_total = round(sum(float(r["net_inr"]) for r in inc_rows), 2)
    assert inc_total == 127351.50, inc_total
    inc_res = [dict(date=r["date"], net=float(r["net_inr"])) for r in inc_rows]
    inc_by_day = defaultdict(list)
    for r in inc_rows: inc_by_day[r["date"]].append(r["entry_time"])
    inc_batt = battery(inc_res, BANK_DAYS)

    legs, excluded = bank_fallback_legset(S, inc_by_day)
    # independent re-derivation of the leg set
    S2 = rederive_sysmap_bank_pandas()
    legs2, _ = bank_fallback_legset(S2, inc_by_day)
    rederive_ok = ([(l["date"], l["direction"], l["entry_time"], l["strike"]) for l in legs]
                   == [(l["date"], l["direction"], l["entry_time"], l["strike"]) for l in legs2])

    # score candidate + audits
    fb_res, nc, audit_bad, trunc_bad = [], [], 0, 0
    for leg in legs:
        r, src = bank_score_leg(leg)
        if r is None:
            nc.append((leg["date"], leg["direction"], leg["strike"], src)); continue
        # entry audit: entry premium == store bar open; strike == atm100(spot open)
        pd = bank_prem_day(leg["expiry"], leg["strike"], leg["direction"], leg["date"]) \
            or bank_prem_day_opt5m(leg["expiry"], leg["strike"], leg["direction"], leg["date"])
        if pd[leg["entry_time"]][0] != r["entry"] or \
           bank_atm100(BSPOT[leg["date"]][leg["entry_time"]][0]) != leg["strike"]:
            audit_bad += 1
        # truncation spot-proof: selection from signals in [13:30, t*] only
        sub = []
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((leg["date"], dirn), {}).items():
                if t and TRIGGER <= t <= leg["entry_time"]:
                    sub.append((t, dirn))
        if not sub or min(s[0] for s in sub) != leg["entry_time"] or \
           {s[1] for s in sub if s[0] == leg["entry_time"]} != {leg["direction"]}:
            trunc_bad += 1
        fb_res.append({**r, "systems": "; ".join(leg["systems"]),
                       "flat_day": leg["flat_day"]})
    fb_batt = battery(fb_res, BANK_DAYS)
    comb_batt = battery(inc_res + fb_res, BANK_DAYS)

    # placebos (delay-6 same contract; random-time same day/direction)
    rng = random.Random(SEED)
    fb_by_date = {r["date"]: r for r in fb_res}
    leg_by_date = {l["date"]: l for l in legs}
    delay_res, rand_res = [], []
    delay_unfilled = rand_unfilled = 0
    for d, r in fb_by_date.items():
        leg = leg_by_date[d]
        times = sorted(BSPOT[d])
        i = times.index(leg["entry_time"])
        # delay-6
        if i + 6 < len(times) and times[i + 6] <= "15:05":
            dr, _ = bank_score_leg(leg, entry_time=times[i + 6])
            if dr is not None: delay_res.append(dr)
            else: delay_unfilled += 1; delay_res.append(dict(date=d, net=r["net"]))
        else:
            delay_unfilled += 1; delay_res.append(dict(date=d, net=r["net"]))
        # random-time (same day, same direction, atm at drawn time)
        window = [t for t in times if "13:30" <= t <= "14:55"]
        rt = rng.choice(window)
        rleg = dict(leg, entry_time=rt,
                    strike=bank_atm100(BSPOT[d][rt][0]))
        rr, _ = bank_score_leg(rleg, entry_time=rt)
        if rr is not None: rand_res.append(rr)
        else: rand_unfilled += 1; rand_res.append(dict(date=d, net=r["net"]))
    delay_batt = battery(inc_res + delay_res, BANK_DAYS)
    rand_batt = battery(inc_res + rand_res, BANK_DAYS)

    checks = gate_verdict(inc_batt, comb_batt, fb_batt,
                          delay_batt["total"], rand_batt["total"])
    hygiene = dict(nc=len(nc), rederive_ok=rederive_ok,
                   audit_violations=audit_bad, truncation_violations=trunc_bad)
    verdict = "PASS" if all(checks.values()) and hygiene["nc"] == 0 \
        and rederive_ok and audit_bad == 0 and trunc_bad == 0 else "FAIL"

    # emit fallback trades CSV + independent re-sum
    out_csv = TR / "tuning_daily_baseload_2026-11-12_bank_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "entry_time", "strike", "expiry",
                    "systems", "flat_day", "prem_source", "entry", "exit",
                    "exit_time", "exit_reason", "net"])
        for r in fb_res:
            w.writerow([r["date"], r["direction"], r["entry_time"], r["strike"],
                        r["expiry"], r["systems"], r["flat_day"], r["src"],
                        r["entry"], r["exit"], r["exit_time"], r["exit_reason"],
                        r["net"]])
    resum = round(sum(float(r["net"]) for r in csv.DictReader(open(out_csv))), 2)
    hygiene["resum_ok"] = (resum == fb_batt["total"])
    if not hygiene["resum_ok"]: verdict = "FAIL"

    census = dict(sysmap_signals_total=sum(len(m) for m in S.values()),
                  sysmap_signals_ge_1330=sum(1 for m in S.values()
                                             for t in m.values() if t >= "13:30"),
                  sysmap_signals_in_window=sum(1 for m in S.values()
                                               for t in m.values()
                                               if "13:30" <= t <= "15:05"),
                  eligible_days=sum(1 for d in BANK_DAYS
                                    if not inc_by_day.get(d)
                                    or min(inc_by_day[d]) > "13:30"))
    out = dict(index="BANKNIFTY", variant="STACK v2 + BASE-LOAD FALLBACK v1",
               verdict=verdict, gate=checks, hygiene=hygiene, census=census,
               incumbent=inc_batt, fallback=fb_batt, combined=comb_batt,
               placebo_delay6_total=delay_batt["total"],
               placebo_random_total=rand_batt["total"],
               placebo_unfilled=dict(delay=delay_unfilled, random=rand_unfilled),
               fallback_legs_generated=len(legs),
               fallback_flat_day_legs=sum(1 for l in legs if l["flat_day"]),
               fallback_race_day_legs=sum(1 for l in legs if not l["flat_day"]),
               excluded_days=[list(x) for x in excluded],
               nc_legs=[list(map(str, x)) for x in nc])
    (TR / "tuning_daily_baseload_2026-11-12_bank_results.json").write_text(
        json.dumps(out, indent=1, default=str))
    print(f"[BANK] incumbent {inc_batt['total']:+,.2f}/{inc_batt['n']} legs, "
          f"traded {inc_batt['traded_days']}d ({inc_batt['traded_days_per_month']}/mo)")
    print(f"[BANK] fallback legs {len(fb_res)} scored / {len(legs)} generated, "
          f"NC {len(nc)} | fallback net {fb_batt['total']:+,.2f}")
    print(f"[BANK] combined {comb_batt['total']:+,.2f} | traded "
          f"{comb_batt['traded_days']}d ({comb_batt['traded_days_per_month']}/mo) | "
          f"red months {comb_batt['red_months']} | ex-top3 {comb_batt['ex_top3_legs']:+,.2f} "
          f"vs inc {inc_batt['ex_top3_legs']:+,.2f}")
    print(f"[BANK] placebos: delay6 {delay_batt['total']:+,.2f} | random "
          f"{rand_batt['total']:+,.2f} (unfilled d{delay_unfilled}/r{rand_unfilled})")
    print(f"[BANK] months combined: " + " · ".join(
        f"{m[5:]} {v[0]:+,.2f}" for m, v in comb_batt["months"].items()))
    print(f"[BANK] hygiene: {hygiene}")
    print(f"[BANK] GATE: {checks}")
    print(f"[BANK] VERDICT: {verdict}")
    return out

# =====================================================================
# NIFTY
# =====================================================================
def stage_nifty():
    import nifty_engine_r7_harness as R7
    import nifty_engine_r8_harness as R8
    import nifty_engine_r6_harness as R6
    from nifty_engine_r2_harness import candles_exact, audit_exact
    from nifty_engine_r4_harness import spot5m
    from nifty_engine_r5_harness import replay_r5

    GEOM = dict(R7.STANDING_GEOM)  # lock 60, tgt2 175, arm 50, sq 15:20
    # --- incumbent TUNED v1 (assembly identical to tuning_nifty_2026-11-12)
    A = R7.standing_legs()
    B, _f = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                with_trend=False, exclude_keys=R7.keys_of(A))
    C, _e = R8.expiry_sleeve_legs(R7.keys_of(A) | R7.keys_of(B))
    DECS1 = A + B + C
    dump = json.loads((TR / "nifty_engine_r11_decs1_legs.json").read_text())
    tagmap = {(d["date"], d["direction"], d["entry_time"], int(d["strike"]),
               d["expiry"]): d["component"] for d in dump}
    def comp(l): return tagmap[(l["date"], l["direction"], l["entry_time"],
                                int(l["strike"]), l["expiry"])]
    V1 = [l for l in DECS1 if not (comp(l) == "B" and l["direction"] == "PE")]
    assert len(V1) == 74, len(V1)
    res_v1, nc_v1, _ = R6.score_r6(V1, geom=GEOM)
    assert nc_v1 == 0 and round(sum(r["net"] for r in res_v1), 2) == 103050.25
    print("anchor: TUNED v1 +103,050.25 / 74 reproduced")

    S5 = spot5m()
    NDAYS = sorted(d for d in S5 if "2026-01-01" <= d <= "2026-10-31")
    inc_res = [dict(date=r["date"], net=r["net"]) for r in res_v1]
    inc_by_day = defaultdict(list)
    for l in V1: inc_by_day[l["date"]].append(l["entry_time"])
    inc_batt = battery(inc_res, NDAYS)

    MONTHLY_EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
                   "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
                   "2026-09-29", "2026-10-27"]
    def expiry_for(d):
        for e in MONTHLY_EXP:
            if d <= e: return e
        return None
    for l in DECS1:  # sanity: A/B legs follow the monthly rule; C legs
        if comp(l) == "C":  # are the weekly-expiry sleeve (expiry == date)
            assert l["expiry"] == l["date"], (l["date"], l["expiry"])
        else:
            assert l["expiry"] == expiry_for(l["date"]), (l["date"], l["expiry"])

    prem_nifty = json.load(open(TR / "daily2leg/prem_nifty.json"))
    def nifty_bars(strike, dirn, day, exp):
        cs = candles_exact("NIFTY", strike, dirn, day, exp)
        if cs: return [list(b) for b in cs], "dirs"
        cd = prem_nifty.get(f"{exp}|{int(strike)}|{dirn}", {}).get(day)
        if cd is None: return None, "none"
        bars = [[t] + [float(x) for x in v] + [0.0]
                for t, v in sorted(cd.items())]
        return bars, "prem_nifty"
    # loader cross-validation: my loader + replay_r5 must reproduce
    # score_r6 nets on every incumbent leg before it scores anything new
    xv_bad = 0
    for l, r in zip(sorted(V1, key=lambda x: (x["date"], x["entry_time"])), res_v1):
        pass
    res_by_key = {(r["date"], r["entry_time"], int(r["strike"])): r for r in res_v1}
    for l in V1:
        bars, _src = nifty_bars(l["strike"], l["direction"], l["date"], l["expiry"])
        rr = replay_r5(bars, l["entry_time"], **GEOM) if bars else None
        ref = res_by_key.get((l["date"], l["entry_time"], int(l["strike"])))
        if rr is None or ref is None or abs(rr["net"] - ref["net"]) > 0.005:
            xv_bad += 1
    assert xv_bad == 0, f"loader cross-validation mismatches: {xv_bad}"

    S = R6.sysmap()
    def spot_open(d, t):
        for b in S5.get(d, []):
            if b[0] == t: return b[1]
        return None
    # --- fallback legset (frozen rule, v1 frame)
    legs, excluded = [], []
    for d in NDAYS:
        inc_times = sorted(inc_by_day.get(d, []))
        if inc_times and inc_times[0] <= TRIGGER: continue
        u = inc_times[0] if inc_times else None
        cands = []
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((d, dirn), {}).items():
                if t and TRIGGER <= t <= LAST_ENTRY:
                    cands.append((t, dirn, sysname))
        if not cands:
            excluded.append((d, "no-u1-signal-after-1330")); continue
        tstar = min(c[0] for c in cands)
        if len({c[1] for c in cands if c[0] == tstar}) > 1:
            excluded.append((d, f"tie-at-{tstar}")); continue
        if u is not None and u <= tstar:
            excluded.append((d, f"incumbent-first-{u}")); continue
        dirn = next(c[1] for c in cands if c[0] == tstar)
        so = spot_open(d, tstar)
        if so is None:
            excluded.append((d, "no-spot-bar-at-tstar")); continue
        legs.append(dict(date=d, direction=dirn, entry_time=tstar,
                         strike=R6.atm100(so), expiry=expiry_for(d),
                         systems=sorted(c[2] for c in cands if c[0] == tstar
                                        and c[1] == dirn),
                         flat_day=(u is None)))
    # independent sysmap re-derivation (pandas, Family B pattern) -> legset
    import pandas as pd
    S2 = defaultdict(dict)
    def put2(date, idx, dirn, sysname, et):
        if idx != "NIFTY" or not et or (isinstance(et, float) and pd.isna(et)): return
        k = (date, dirn)
        if sysname not in S2[k] or et < S2[k][sysname]: S2[k][sysname] = et
    o1 = pd.read_csv(TR / "index_options_o1_janoct_trades.csv", dtype=str)
    for r in o1.itertuples():
        if r.date >= "2026-10-01": continue
        if r.track == "(lA) v2": put2(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.track == "V5-v2": put2(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    sk = pd.read_csv(TR / "index_options_U1_skillV3_jansep_spot.csv", dtype=str)
    for r in sk.itertuples(): put2(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    vx = pd.read_csv(TR / "index_options_U1_volrixB_jansep_spot.csv", dtype=str)
    for r in vx.itertuples(): put2(r.entry_date, r.index, r.direction, "Volrix (b)", r.entry_time)
    po = pd.read_csv(TR / "index_options_premium_october_trades.csv", dtype=str)
    for r in po.itertuples():
        if r.premium_status != "COMPUTED": continue
        if r.version.startswith("(lA)"): put2(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.version.startswith("V5"): put2(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    so30 = pd.read_csv(TR / "index_options_skill_tuned_oct30_trades.csv", dtype=str)
    for r in so30.itertuples():
        if r.variant == "V3" and r.premium_status == "COMPUTED":
            put2(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    put2("2026-10-09", "NIFTY", "CE", "Volrix (b)", "09:20")
    legs2 = []
    for d in NDAYS:
        inc_times = sorted(inc_by_day.get(d, []))
        if inc_times and inc_times[0] <= TRIGGER: continue
        u = inc_times[0] if inc_times else None
        cands = []
        for dirn in ("CE", "PE"):
            for sysname, t in S2.get((d, dirn), {}).items():
                if t and TRIGGER <= t <= LAST_ENTRY: cands.append((t, dirn))
        if not cands: continue
        tstar = min(c[0] for c in cands)
        if len({c[1] for c in cands if c[0] == tstar}) > 1: continue
        if u is not None and u <= tstar: continue
        dirn = next(c[1] for c in cands if c[0] == tstar)
        so = spot_open(d, tstar)
        if so is None: continue
        legs2.append((d, dirn, tstar, R6.atm100(so)))
    rederive_ok = (sorted(map(str, legs2)) ==
                   sorted(map(str, [(l["date"], l["direction"], l["entry_time"],
                                     l["strike"]) for l in legs])))

    # --- score + audits
    fb_res, nc, audit_bad, trunc_bad = [], [], 0, 0
    for leg in legs:
        bars, src = nifty_bars(leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        r = replay_r5(bars, leg["entry_time"], **GEOM) if bars else None
        if r is None:
            nc.append((leg["date"], leg["direction"], leg["strike"], src)); continue
        if bars[[b[0] for b in bars].index(leg["entry_time"])][1] != r["entry"] or \
           R6.atm100(spot_open(leg["date"], leg["entry_time"])) != leg["strike"]:
            audit_bad += 1
        sub = []
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((leg["date"], dirn), {}).items():
                if t and TRIGGER <= t <= leg["entry_time"]: sub.append((t, dirn))
        if not sub or min(s[0] for s in sub) != leg["entry_time"] or \
           {s[1] for s in sub if s[0] == leg["entry_time"]} != {leg["direction"]}:
            trunc_bad += 1
        fb_res.append({**r, "date": leg["date"], "direction": leg["direction"],
                       "entry_time": leg["entry_time"], "strike": leg["strike"],
                       "expiry": leg["expiry"], "systems": "; ".join(leg["systems"]),
                       "flat_day": leg["flat_day"], "src": src})
    fb_batt = battery(fb_res, NDAYS)
    comb_batt = battery(inc_res + fb_res, NDAYS)

    # placebos (delay-6 same contract; random-time same day/direction)
    rng = random.Random(SEED)
    delay_res, rand_res = [], []
    delay_unfilled = rand_unfilled = 0
    for leg, r in zip(legs, fb_res):
        bars, _ = nifty_bars(leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        dr = replay_r5(bars, leg["entry_time"], delay_bars=6, **GEOM) if bars else None
        if dr is not None: delay_res.append(dict(date=leg["date"], net=dr["net"]))
        else: delay_unfilled += 1; delay_res.append(dict(date=leg["date"], net=r["net"]))
        times = [b[0] for b in S5[leg["date"]] if "13:30" <= b[0] <= "14:55"]
        rt = rng.choice(times)
        rbars, _ = nifty_bars(R6.atm100(spot_open(leg["date"], rt)),
                              leg["direction"], leg["date"], leg["expiry"])
        rr = replay_r5(rbars, rt, **GEOM) if rbars else None
        if rr is not None: rand_res.append(dict(date=leg["date"], net=rr["net"]))
        else: rand_unfilled += 1; rand_res.append(dict(date=leg["date"], net=r["net"]))
    delay_batt = battery(inc_res + delay_res, NDAYS)
    rand_batt = battery(inc_res + rand_res, NDAYS)

    checks = gate_verdict(inc_batt, comb_batt, fb_batt,
                          delay_batt["total"], rand_batt["total"])
    hygiene = dict(nc=len(nc), rederive_ok=rederive_ok,
                   audit_violations=audit_bad, truncation_violations=trunc_bad,
                   loader_cross_validation="74/74 v1 legs reproduced")
    verdict = "PASS" if all(checks.values()) and hygiene["nc"] == 0 \
        and rederive_ok and audit_bad == 0 and trunc_bad == 0 else "FAIL"

    out_csv = TR / "tuning_daily_baseload_2026-11-12_nifty_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "entry_time", "strike", "expiry",
                    "systems", "flat_day", "prem_source", "entry", "exit",
                    "exit_time", "exit_reason", "net"])
        for r in fb_res:
            w.writerow([r["date"], r["direction"], r["entry_time"], r["strike"],
                        r["expiry"], r["systems"], r["flat_day"], r["src"],
                        r["entry"], r["exit"], r["exit_time"], r["exit_reason"],
                        r["net"]])
    resum = round(sum(float(r["net"]) for r in csv.DictReader(open(out_csv))), 2)
    hygiene["resum_ok"] = (resum == fb_batt["total"])
    if not hygiene["resum_ok"]: verdict = "FAIL"

    # signal census (the vacuity evidence)
    census = dict(sysmap_signals_total=sum(len(m) for m in S.values()),
                  sysmap_signals_ge_1330=sum(1 for m in S.values()
                                             for t in m.values() if t >= "13:30"),
                  sysmap_signals_in_window=sum(1 for m in S.values()
                                               for t in m.values()
                                               if "13:30" <= t <= "15:05"))
    out = dict(index="NIFTY", variant="TUNED v1 + BASE-LOAD FALLBACK v1",
               verdict=verdict, gate=checks, hygiene=hygiene, census=census,
               incumbent=inc_batt, fallback=fb_batt, combined=comb_batt,
               placebo_delay6_total=delay_batt["total"],
               placebo_random_total=rand_batt["total"],
               placebo_unfilled=dict(delay=delay_unfilled, random=rand_unfilled),
               fallback_legs_generated=len(legs),
               fallback_flat_day_legs=sum(1 for l in legs if l["flat_day"]),
               fallback_race_day_legs=sum(1 for l in legs if not l["flat_day"]),
               excluded_days=[list(x) for x in excluded],
               nc_legs=[list(map(str, x)) for x in nc])
    (TR / "tuning_daily_baseload_2026-11-12_nifty_results.json").write_text(
        json.dumps(out, indent=1, default=str))
    print(f"[NIFTY] incumbent {inc_batt['total']:+,.2f}/{inc_batt['n']} legs, "
          f"traded {inc_batt['traded_days']}d ({inc_batt['traded_days_per_month']}/mo)")
    print(f"[NIFTY] census: {census}")
    print(f"[NIFTY] fallback legs {len(fb_res)} scored / {len(legs)} generated, "
          f"NC {len(nc)} | fallback net {fb_batt['total']:+,.2f}")
    print(f"[NIFTY] combined {comb_batt['total']:+,.2f} | traded "
          f"{comb_batt['traded_days']}d | red {comb_batt['red_months']}")
    print(f"[NIFTY] hygiene: {hygiene}")
    print(f"[NIFTY] GATE: {checks}")
    print(f"[NIFTY] VERDICT: {verdict}")
    return out

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "bank"
    if which == "bank":
        stage_bank()
    elif which == "nifty":
        stage_nifty()
