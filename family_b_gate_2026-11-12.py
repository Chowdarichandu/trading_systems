#!/usr/bin/env python3
"""FAMILY B GATE RUN — 2026-11-12 (invention_round_2026-11-12.md §3
follow-through: the 760-file weekly-expiry chain build landed —
nifty_weekly_expiry_chain/, 760/760, cross-validated 15/15 — so the
Nifty weekly-expiry-day book is testable for the first time).
Paper only, real Rs 0. December candidate only; nothing armed;
frozen November primaries untouched (read-only at most).

=====================================================================
FROZEN SPEC — FAMILY B: NIFTY-WEXP v1 (fixed BEFORE any scoring)
=====================================================================
Population: the 33 Nifty WEEKLY expiry days Jan-Oct 2026
(nifty_engine_run3_expiries.json minus the 10 monthly expiries —
R8.weekly_expiry_days()). One leg per day maximum.

Entry logic (the incumbent books' signal vocabulary, applied to the
single-day expiry population): the day's FIRST U1 system signal.
The sysmap (nifty_engine_r5_ws0.build_sysmap — the same causal
per-system signal store every incumbent Nifty book reads) holds, per
(date, direction), each system's earliest signal time for the four
U1 systems: (lA) v2, V5 v2, Skill V3, Volrix (b). On an expiry day,
take the earliest signal time across ALL systems and BOTH directions.
If that earliest time belongs to exactly one direction, enter that
direction at that time. If both directions share the exact earliest
time, the day is ambiguous -> no leg (frozen tie-break). Signals with
entry_time > 15:10 are inadmissible (the book cannot enter after its
own square-off) -> no leg, named exclusion. No confirmation keying
(no C3), no window restriction, no exclusion against any other book's
keys — the book is standalone.

Strike/contract: strike = atm100(spot OPEN at entry_time) — the
incumbent convention (R7.atm100 / R7.spot_open on the full_hist spot
store); contract = that strike, signal direction, expiring THAT day,
premium from nifty_weekly_expiry_chain/ ONLY.
Entry fill: first chain bar at/after entry_time, at its open (the
nifty_engine_score.replay house semantics).

Geometry: G7, frozen (nifty_engine_score.G7 + replay defaults):
stop -50; at +90 the leg becomes a runner — stop moves to entry+50,
second target +150; square-off 15:10 (runner legs also 15:10);
no break-even arm. Lot 65, cost Rs 220/trade.

WHY THIS IS NOT A RE-SCORE OF DEC-S1 COMPONENT C: Component C is a
RESIDUAL sleeve inside DEC-S1: it admits ONLY Skill V3 signals, only
inside 09:15-11:00, and only on (date, direction) keys that neither
the standing book (A) nor the fade book (B) already holds — 13 legs,
scored at DEC-S1's standing geometry (lock +60 / tgt2 +175 / SQ
15:20). Family B differs on every axis: signal set (all four U1
systems, not Skill-only), timing rule (the day's first signal at any
time, not a morning window), population treatment (all 33 weekly
expiry days standalone, no in-pair key exclusions), strike rule (own
atm100 at its own entry time — any strike in the fetched band), and
geometry (G7: lock +50 / tgt2 +150 / SQ 15:10).

GATE — the invention round's standing gate (pre-registered; PASS
requires ALL):
  1. Total net Jan-Oct > 0.
  2. H1 (Jan-May) > 0 AND H2 (Jun-Oct) > 0.
  3. Red months <= 3 of 10 AND worst month >= -Rs 5,000 (bleed leg).
  4. Ex-top-3 legs total > 0.
  5. Candidate total > delay-6 placebo total AND > flipped-direction
     placebo total (unfillable placebo legs count at candidate net —
     the disclosed house convention; fills counted).
  6. NC == 0 (every generated leg scored from chain premium data).
  7. Timing/admission audit 0 violations (incl. an independent
     re-derivation of the leg set from the raw source CSVs) and
     independent re-sum from the emitted trades CSV exact.

November counterfactual: the chain store covers Jan-Oct 2026 only
(0 November files) and november_shadow_data holds only prior books'
legs — November expiring-weekly premium candles exist in no store,
so the counterfactual is NOT_COMPUTED by construction (never
estimated). Verified in-run below.
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path.home() / "workspace/trading"))
TR = Path.home() / "workspace/trading"
CHAIN = TR / "nifty_weekly_expiry_chain"

import nifty_engine_r7_harness as R7
import nifty_engine_r8_harness as R8
import nifty_engine_r6_harness as R6
from nifty_engine_r4_harness import spot5m
from nifty_engine_score import replay as g7_replay, G7

COST, LOT = 220.0, 65
GEOM = dict(G7)  # stop 50, tgt1 90, lock 50, tgt2 150; replay sq default 15:10

# ---------------- chain store loader ----------------
def chain_candles(strike, direction, day):
    """Load one contract-day from the weekly-expiry chain store and
    return bars as [time 'HH:MM', o, h, l, c, v] ascending — the
    nifty_engine_score.replay input format. None if the file is
    absent or empty."""
    f = CHAIN / f"candles_NIFTY_{strike}{direction}_{day}_{day}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
        rows = d["data"]["candles"]
    except Exception:
        return None
    bars = []
    for r in rows:
        bars.append((r[0][11:16], float(r[1]), float(r[2]), float(r[3]),
                     float(r[4]), float(r[5])))
    bars.sort()
    out, seen = [], set()
    for b in bars:
        if b[0] in seen:
            continue
        seen.add(b[0])
        out.append(list(b))
    return out or None

# ---------------- leg generation (frozen rule) ----------------
def generate_legs():
    S = R6.sysmap()
    S5 = spot5m()
    days = R8.weekly_expiry_days()
    assert len(days) == 33, len(days)
    legs, excluded = [], []
    for d in days:
        cands = []  # (time, direction, system)
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((d, dirn), {}).items():
                if t:
                    cands.append((t, dirn, sysname))
        if not cands:
            excluded.append((d, "no-system-signal"))
            continue
        tmin = min(c[0] for c in cands)
        dirs_at_min = {c[1] for c in cands if c[0] == tmin}
        if len(dirs_at_min) > 1:
            excluded.append((d, f"tie-at-{tmin}-both-directions"))
            continue
        dirn = next(iter(dirs_at_min))
        if tmin > "15:10":
            excluded.append((d, f"first-signal-{tmin}-after-1510"))
            continue
        so = R7.spot_open(d, tmin)
        if so is None:
            excluded.append((d, "no-spot-bar-at-signal"))
            continue
        strike = R7.atm100(so)
        systems_at = sorted(c[2] for c in cands if c[0] == tmin and c[1] == dirn)
        legs.append(dict(date=d, index="NIFTY", direction=dirn,
                         entry_time=tmin, strike=strike, expiry=d,
                         lot=LOT, rep="FAMB-WEXP",
                         sources="; ".join(systems_at),
                         family="FAMILY-B", base_net=0.0, base_reason=""))
    return legs, excluded

# ---------------- scoring ----------------
def score_legs(legs, delay_bars=0, flip=False):
    res, nc, nc_legs = [], 0, []
    for l in legs:
        dirn = ("PE" if l["direction"] == "CE" else "CE") if flip else l["direction"]
        cs = chain_candles(l["strike"], dirn, l["date"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], dirn, "no-chain-file")); continue
        r = g7_replay(cs, l["entry_time"], delay_bars=delay_bars, **GEOM)
        if r is None:
            nc += 1; nc_legs.append((l["date"], dirn, "replay-none")); continue
        res.append({**r, "date": l["date"], "direction": dirn,
                    "entry_time": l["entry_time"], "strike": l["strike"],
                    "sources": l["sources"]})
    return res, nc, nc_legs

def placebo_total(candidate_res, placebo_res, placebo_nc):
    """House convention: unfillable placebo legs count at candidate net."""
    cand = {r["date"]: r["net"] for r in candidate_res}
    tot = sum(r["net"] for r in placebo_res)
    filled_dates = {r["date"] for r in placebo_res}
    unfilled = 0
    for d, net in cand.items():
        if d not in filled_dates:
            tot += net; unfilled += 1
    return round(tot, 2), len(placebo_res), unfilled

# ---------------- independent re-derivation (audit) ----------------
def rederive_legs():
    """Second implementation: rebuild the sysmap from the raw source
    CSVs (build_sysmap's own rules, incl. its October filters and the
    merge hardcode) and re-apply the frozen rule. Returns the leg
    triples (date, direction, entry_time, strike)."""
    import pandas as pd
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "NIFTY" or not et or pd.isna(et):
            return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]:
            S[k][sysname] = et
    o1 = pd.read_csv(TR / "index_options_o1_janoct_trades.csv", dtype=str)
    for r in o1.itertuples():
        if r.date >= "2026-10-01":
            continue
        if r.track == "(lA) v2":
            put(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.track == "V5-v2":
            put(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    sk = pd.read_csv(TR / "index_options_U1_skillV3_jansep_spot.csv", dtype=str)
    for r in sk.itertuples():
        put(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    vx = pd.read_csv(TR / "index_options_U1_volrixB_jansep_spot.csv", dtype=str)
    for r in vx.itertuples():
        put(r.entry_date, r.index, r.direction, "Volrix (b)", r.entry_time)
    po = pd.read_csv(TR / "index_options_premium_october_trades.csv", dtype=str)
    for r in po.itertuples():
        if r.premium_status != "COMPUTED":
            continue
        if r.version.startswith("(lA)"):
            put(r.date, r.index, r.direction, "(lA) v2", r.entry_time)
        elif r.version.startswith("V5"):
            put(r.date, r.index, r.direction, "V5 v2", r.entry_time)
    so30 = pd.read_csv(TR / "index_options_skill_tuned_oct30_trades.csv", dtype=str)
    for r in so30.itertuples():
        if r.variant == "V3" and r.premium_status == "COMPUTED":
            put(r.date, r.index, r.direction, "Skill V3", r.entry_time)
    put("2026-10-09", "NIFTY", "CE", "Volrix (b)", "09:20")

    spot = {}
    for r in csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_5m.csv")):
        spot.setdefault(r["timestamp"][:10], {})[r["timestamp"][11:16]] = float(r["open"])
    days = R8.weekly_expiry_days()
    out = []
    for d in days:
        cands = []
        for dirn in ("CE", "PE"):
            for sysname, t in S.get((d, dirn), {}).items():
                if t:
                    cands.append((t, dirn))
        if not cands:
            continue
        tmin = min(c[0] for c in cands)
        dirs = {c[1] for c in cands if c[0] == tmin}
        if len(dirs) > 1 or tmin > "15:10":
            continue
        dirn = next(iter(dirs))
        so = spot.get(d, {}).get(tmin)
        if so is None:
            continue
        out.append((d, dirn, tmin, R7.atm100(so)))
    return out

def main():
    legs, excluded = generate_legs()
    res, nc, nc_legs = score_legs(legs)
    total = round(sum(r["net"] for r in res), 2)

    # placebos
    dres, dnc, _ = score_legs(legs, delay_bars=6)
    delay_total, delay_filled, delay_unfilled = placebo_total(res, dres, dnc)
    fres, fnc, _ = score_legs(legs, flip=True)
    flip_total, flip_filled, flip_unfilled = placebo_total(res, fres, fnc)

    # month table (all 10 months; absent month = 0.00, 0 legs)
    months = {}
    for m in range(1, 11):
        key = f"2026-{m:02d}"
        mres = [r for r in res if r["date"][:7] == key]
        months[key] = [round(sum(r["net"] for r in mres), 2), len(mres)]
    h1 = round(sum(r["net"] for r in res if r["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"][:7] >= "2026-06"), 2)
    red_months = [m for m, (v, n) in months.items() if v < 0]
    worst = min(v for v, _ in months.values())
    top3 = sorted((r["net"] for r in res), reverse=True)[:3]
    ex_top3 = round(total - sum(top3), 2)
    byday = defaultdict(float)
    for r in res:
        byday[r["date"]] += r["net"]
    top3d = sorted(byday.values(), reverse=True)[:3]
    ex_top3_days = round(total - sum(top3d), 2)
    ft = sum(r["ft"] for r in res)

    # audits: timing (entry bar exists in chain file; scored entry == bar open)
    res_by_date = {r["date"]: r for r in res}
    audit_bad = 0
    for l in legs:
        r = res_by_date.get(l["date"])
        if r is None:
            continue  # unscored leg — counted in NC, gate leg 6
        cs = chain_candles(l["strike"], l["direction"], l["date"])
        bars = [b for b in cs if b[0] >= l["entry_time"]]
        if not bars or bars[0][1] != r["entry"]:
            audit_bad += 1
    # independent leg re-derivation
    rederived = rederive_legs()
    mine = [(l["date"], l["direction"], l["entry_time"], l["strike"]) for l in legs]
    rederive_ok = (sorted(map(str, rederived)) == sorted(map(str, mine)))

    # emit trades CSV + independent re-sum
    out_csv = TR / "family_b_gate_2026-11-12_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "entry_time", "strike", "expiry",
                    "sources", "entry", "exit", "exit_time", "exit_reason",
                    "ft", "net"])
        for r in res:
            w.writerow([r["date"], r["direction"], r["entry_time"], r["strike"],
                        r["date"], r["sources"], r["entry"], r["exit"],
                        r["exit_time"], r["exit_reason"], r["ft"], r["net"]])
    resum = round(sum(float(r["net"]) for r in csv.DictReader(open(out_csv))), 2)

    # November counterfactual availability check
    nov_chain = list(CHAIN.glob("*2026-11*"))
    nov_shadow_files = 0
    nsd = TR / "november_shadow_data"
    if nsd.exists():
        nov_shadow_files = len([p for p in nsd.rglob("*") if p.is_file()])

    gate = {
        "1_total_positive": total > 0,
        "2_halves_positive": h1 > 0 and h2 > 0,
        "3_bleed": len(red_months) <= 3 and worst >= -5000.0,
        "4_ex_top3_positive": ex_top3 > 0,
        "5_placebos_beaten": total > delay_total and total > flip_total,
        "6_nc_zero": nc == 0,
        "7_audits_clean": audit_bad == 0 and rederive_ok and resum == total,
    }
    verdict = "PASS" if all(gate.values()) else "FAIL"

    summary = dict(
        family="FAMILY B — NIFTY-WEXP v1 (weekly-expiry-day book)",
        verdict=verdict, gate=gate,
        n_legs=len(res), n_generated=len(legs), nc=nc, nc_legs=[str(x) for x in nc_legs],
        total=total, per_month=round(total / 10.0, 2),
        ft_pct=round(100.0 * ft / len(res), 1) if res else 0.0,
        halves={"Jan-May": h1, "Jun-Oct": h2}, month_table=months,
        red_months=red_months, worst_month=worst,
        top3=top3, ex_top3_legs=ex_top3, ex_top3_days=ex_top3_days,
        placebo_delay6=dict(total=delay_total, filled=delay_filled, unfilled=delay_unfilled),
        placebo_flipped=dict(total=flip_total, filled=flip_filled, unfilled=flip_unfilled),
        timing_audit=dict(checked=len(res), violations=audit_bad),
        rederive_match=rederive_ok, resum=resum,
        excluded_days=[list(x) for x in excluded],
        november_counterfactual="NOT_COMPUTED — chain store covers Jan-Oct 2026 only "
                                f"({len(nov_chain)} November files); expiring-weekly premium "
                                "candles for November exist in no store "
                                f"(november_shadow_data: {nov_shadow_files} files, prior books' legs only)",
        nifty_stacked_now=12347.90,
        nifty_stacked_if_pass=round(12347.90 + total / 10.0, 2),
    )
    (TR / "family_b_gate_2026-11-12_results.json").write_text(
        json.dumps(summary, indent=1, default=str))

    print(f"[FAMILY B] legs {len(res)}/{len(legs)} generated | NC {nc} | "
          f"TOTAL {total:+,.2f} | per-month {total/10:+,.2f} | FT {summary['ft_pct']}%")
    print(f"  halves H1 {h1:+,.2f} / H2 {h2:+,.2f} | red months {red_months} "
          f"| worst {worst:+,.2f}")
    print(f"  ex-top-3 legs {ex_top3:+,.2f} | ex-top-3 days {ex_top3_days:+,.2f}")
    print(f"  placebos: delay6 {delay_total:+,.2f} (filled {delay_filled}, "
          f"unfilled-at-candidate {delay_unfilled}) | flipped {flip_total:+,.2f} "
          f"(filled {flip_filled}, unfilled-at-candidate {flip_unfilled})")
    print(f"  months: " + " · ".join(f"{m[5:]} {v[0]:+,.2f}({v[1]})" for m, v in months.items()))
    print(f"  timing audit violations {audit_bad} | rederive match {rederive_ok} "
          f"| resum {resum:+,.2f} ok={resum == total}")
    print(f"  excluded days: {excluded}")
    print(f"  GATE: {gate}")
    print(f"  VERDICT: {verdict}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
