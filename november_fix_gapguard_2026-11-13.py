#!/usr/bin/env python3
"""
NOVEMBER FIX PART 1 — GAP-REGIME GUARD, gated (owner order 2026-11-13 05:58 IST).
Evidence base: november_failure_audit_2026-11-13.md (money-cause #1).

FROZEN SPEC (registered before scoring, 2026-11-13):
- Incumbents: Bank = TUNED STACK v2 leg stream (bank_positive_tuning_2026-11-10_eve19_trades.csv,
  anchor +127,351.50 / 111 legs). Nifty = TUNED v1 = DEC-S1 stream (nifty_next_phase_trades.csv)
  minus (component B & direction PE) legs, anchor +103,050.25 / 74 legs.
- Gap (audit-exact): sessions = days with >=70 bars in the stored 5-min spot series;
  gap_t = (open_t - close_{t-1}) / close_{t-1} * 100, prior session = previous stored session.
- Threshold: thr_t = 85th percentile (numpy linear) of |gap| over the PRIOR 60 stored sessions,
  strictly prior (causal). 2025 sessions in the store provide the warm-up; every 2026 day has 60 priors.
- Variants (day-level overlay, decision complete at 09:15 from the open print):
  G-1: |gap_t| >= thr_t  -> skip that day's PE legs (CE legs run).
  G-2: |gap_t| >= thr_t  -> skip ALL legs that day.
  G-3: gap_t >= +thr_t (large gap-UP, adverse to PE) -> skip that day's PE legs.
- Scoring convention (house precedent: TUNED v1/v2, BV-1/BV-2): drop-only filter on the frozen
  assembled leg stream; kept legs keep their recorded net_inr (1 lot, costs already inside).
- GATE (project standard, EVE-07..20 / repair programme): candidate FAILS if
  total <= incumbent, any month flips green->red, H1 < incumbent H1, H2 < incumbent H2,
  ex-top-3 legs <= incumbent, ex-top-3 days <= incumbent, or a placebo is not beaten.
  Placebos: (a) random-day skip, same removed-leg-class on the same NUMBER of fired days,
  1000 seeds -> candidate must exceed the 95th percentile; (b) shuffled-gap: gap series permuted
  across sessions, thresholds+triggers recomputed, 200 perms -> candidate must exceed p95;
  (c) mirror: G-1 -> skip CE (not PE) on guard days; G-3 -> skip PE on gap_t <= -thr_t days;
  candidate must exceed the mirror total (G-2 has no mirror; random-day binds).
- November lens (reported, cannot promote): Nov 2-12 incumbent legs with guard states.
Paper only, real money Rs 0.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

TR = Path.home() / "workspace/trading"
RNG = np.random.default_rng(20261113)
OUT = {}

# ---------------------------------------------------------------- spot sessions / gaps
def load5m_sessions(path):
    s = pd.read_csv(path)
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s["date"] = s["timestamp"].dt.normalize()
    s = s.sort_values("timestamp")
    out = {}
    for d, g in s.groupby("date"):
        if len(g) >= 70:
            out[d] = (float(g.iloc[0]["open"]), float(g.iloc[-1]["close"]))
    return out

def json_sessions(dates_wanted=None):
    d = json.load(open(TR / "oi_history/spot_nov_bars.json"))
    res = {}
    for sym, days in d.items():
        o = {}
        for dt, bars in days.items():
            if len(bars) >= 70:
                o[pd.Timestamp(dt)] = (float(bars[0][1]), float(bars[-1][4]))
        res[sym] = o
    return res

def build_gap_series(session_map):
    dates = sorted(session_map)
    rows = []
    prev_close = None
    for d in dates:
        o, c = session_map[d]
        gap = (o - prev_close) / prev_close * 100 if prev_close else np.nan
        rows.append(dict(date=d, open=o, close=c, gap=gap))
        prev_close = c
    df = pd.DataFrame(rows)
    # rolling causal threshold: 85th pctile of |gap| over prior 60 sessions (strictly prior)
    ag = df["gap"].abs()
    thr = []
    for i in range(len(df)):
        prior = ag.iloc[max(0, i - 60):i].dropna()
        thr.append(float(np.percentile(prior, 85)) if len(prior) >= 60 else np.nan)
    df["thr"] = thr
    return df

bank_sess = load5m_sessions(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
bank_sess.update(load5m_sessions(TR / "data/banknifty-2026-11/spot_5m.csv"))
nif_sess = load5m_sessions(TR / "data/progressive/NIFTY/spot_5m.csv")
nov_json = json_sessions()
nif_sess.update(nov_json["NIFTY"])   # Nov 2,3,4,5,6,9,11 full sessions (Nov 12 absent -> handled below)

bank_gaps = build_gap_series(bank_sess)
nif_gaps = build_gap_series(nif_sess)

# Nifty 2026-11-12 has no stored bars anywhere; the DEC-S1 shadow log (scorer-computed from the
# day's open/prior close) records gap -0.16%. Insert it as a flagged row so the November table is
# complete; it touches no leg (DEC-S1 Nov 12 = no-trade; TUNED v1 has no Nov 12 leg) and no threshold
# used by any November leg day (all v1/stack November legs are <= Nov 12, and Nov 12's own row is last).
assert pd.Timestamp("2026-11-12") not in set(nif_gaps.date)
nif_gaps = pd.concat([nif_gaps, pd.DataFrame([dict(date=pd.Timestamp("2026-11-12"), open=np.nan,
                    close=np.nan, gap=-0.16, thr=np.nan)])]).sort_values("date").reset_index(drop=True)
# recompute Nov-12 threshold causally from the series as it now stands (prior 60 sessions incl. Nov 11)
ag = nif_gaps["gap"].abs()
i12 = nif_gaps.index[nif_gaps.date == pd.Timestamp("2026-11-12")][0]
prior = ag.iloc[max(0, i12 - 60):i12].dropna()
nif_gaps.loc[i12, "thr"] = float(np.percentile(prior, 85))

# ---------------------------------------------------------------- validation vs the audit
def med_abs_gap(df, lo, hi):
    x = df[(df.date >= lo) & (df.date <= hi)]["gap"].abs()
    return round(float(x.median()), 3)

val = {}
val["bank_janoct_med_abs_gap"] = med_abs_gap(bank_gaps, "2026-01-01", "2026-10-31")   # audit: 0.303
val["nif_janoct_med_abs_gap"] = med_abs_gap(nif_gaps, "2026-01-01", "2026-10-31")     # audit: 0.262
for name, df in (("bank", bank_gaps), ("nif", nif_gaps)):
    nov = df[(df.date >= "2026-11-01") & (df.date <= "2026-11-12")]
    val[f"{name}_nov"] = {str(r.date)[:10]: (round(float(r.gap), 2) if pd.notna(r.gap) else None)
                          for r in nov.itertuples()}
    jo = df[(df.date >= "2026-01-01") & (df.date <= "2026-10-31")]["gap"].abs()
    val[f"{name}_nov_med_abs_gap"] = round(float(nov["gap"].abs().median()), 3)
    val[f"{name}_nov_med_pctile_in_janoct"] = round(float((jo <= nov["gap"].abs().median()).mean() * 100), 1)
OUT["validation"] = val
# audit anchors: bank Nov 2 +1.05, Nov 5 +2.13, Nov 11 +1.31 ; nifty Nov 5 +1.74, Nov 4 -0.29, Nov 6 +0.01, Nov 9 +0.36
print("VALIDATION:", json.dumps(val, indent=1))

# ---------------------------------------------------------------- leg streams (incumbents)
stack = pd.read_csv(TR / "bank_positive_tuning_2026-11-10_eve19_trades.csv")
stack["date"] = pd.to_datetime(stack["date"])
stack["net"] = stack["net_inr"]
assert len(stack) == 111 and abs(stack.net.sum() - 127351.50) < 0.01, (len(stack), stack.net.sum())

dec = pd.read_csv(TR / "nifty_next_phase_trades.csv")
dec["date"] = pd.to_datetime(dec["date"])
dec["net"] = dec["net_inr"]
assert len(dec) == 97 and abs(dec.net.sum() - 91168.50) < 0.01
v1 = dec[~((dec.component == "B") & (dec.direction == "PE"))].copy()
assert len(v1) == 74 and abs(v1.net.sum() - 103050.25) < 0.01, (len(v1), v1.net.sum())

def book_stats(df):
    df = df.copy()
    df["m"] = df["date"].dt.strftime("%Y-%m")
    months = {m: round(float(g.net.sum()), 2) for m, g in df.groupby("m")}
    months = {m: months.get(m, 0.0) for m in
              ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10"]}
    h1 = round(float(df[df.date <= "2026-06-30"].net.sum()), 2)
    h2 = round(float(df[df.date >= "2026-07-01"].net.sum()), 2)
    top3_legs = df.nlargest(3, "net").net.sum()
    day = df.groupby("date").net.sum()
    top3_days = day.nlargest(3).sum()
    return dict(total=round(float(df.net.sum()), 2), legs=int(len(df)), months=months, H1=h1, H2=h2,
                extop3_legs=round(float(df.net.sum() - top3_legs), 2),
                extop3_days=round(float(df.net.sum() - top3_days), 2),
                traded_days=int(df.date.nunique()))

# ---------------------------------------------------------------- guard machinery
def guard_states(gaps):
    """date -> dict(gap, thr, g1_fire, g2_fire, g3_fire) for sessions with a causal threshold."""
    st = {}
    for r in gaps.itertuples():
        if pd.isna(r.thr) or pd.isna(r.gap):
            continue
        st[r.date] = dict(gap=float(r.gap), thr=float(r.thr),
                          G1=bool(abs(r.gap) >= r.thr), G2=bool(abs(r.gap) >= r.thr),
                          G3=bool(r.gap >= r.thr))
    return st

def apply_variant(legs, states, variant):
    """Returns (kept_df, removed_df). Drop-only on the frozen stream."""
    keep_idx, rem_idx = [], []
    for i, r in legs.iterrows():
        s = states.get(r.date)
        fire = bool(s and s[{"G1": "G1", "G2": "G2", "G3": "G3"}[variant]])
        drop = False
        if fire:
            if variant in ("G1", "G3") and r.direction == "PE":
                drop = True
            elif variant == "G2":
                drop = True
        (rem_idx if drop else keep_idx).append(i)
    return legs.loc[keep_idx].copy(), legs.loc[rem_idx].copy()

def gate_eval(inc, cand, placebos):
    legs = {}
    legs["total_gt_incumbent"] = cand["total"] > inc["total"]
    flips = [m for m in inc["months"] if inc["months"][m] > 0 and cand["months"][m] < 0]
    legs["no_month_flip"] = len(flips) == 0
    legs["H1_ge"] = cand["H1"] >= inc["H1"]
    legs["H2_ge"] = cand["H2"] >= inc["H2"]
    legs["extop3_legs_gt"] = cand["extop3_legs"] > inc["extop3_legs"]
    legs["extop3_days_gt"] = cand["extop3_days"] > inc["extop3_days"]
    for name, p in placebos.items():
        legs[f"placebo_{name}"] = p
    return legs, flips

def random_day_placebo(legs, fired_days, drop_dirs, n_seeds=1000):
    """Skip legs of drop_dirs ('PE' or 'ALL') on the same number of randomly chosen traded days."""
    traded_days = sorted(legs.date.unique())
    k = len(fired_days)
    if k == 0:
        return None
    totals = []
    day_arr = np.array(traded_days, dtype=object)
    for _ in range(n_seeds):
        chosen = set(RNG.choice(day_arr, size=k, replace=False).tolist())
        if drop_dirs == "ALL":
            kept = legs[~legs.date.isin(chosen)]
        else:
            kept = legs[~((legs.date.isin(chosen)) & (legs.direction == drop_dirs))]
        totals.append(float(kept.net.sum()))
    t = np.array(totals)
    return dict(p50=float(np.percentile(t, 50)), p95=float(np.percentile(t, 95)),
                max=float(t.max()), mean=float(t.mean()))

def shuffled_gap_placebo(legs, gaps, variant, n_seeds=200):
    """Permute gap values across sessions (dates fixed), recompute causal thresholds+triggers,
    apply to the real leg stream. Destroys gap<->day alignment at matched trigger machinery."""
    g = gaps.copy()
    vals = g["gap"].to_numpy(dtype=float)
    totals = []
    for _ in range(n_seeds):
        gg = g.copy()
        gg["gap"] = RNG.permutation(vals)
        ag = gg["gap"].abs()
        thr = []
        for i in range(len(gg)):
            prior = ag.iloc[max(0, i - 60):i].dropna()
            thr.append(float(np.percentile(prior, 85)) if len(prior) >= 60 else np.nan)
        gg["thr"] = thr
        st = guard_states(gg)
        kept, _ = apply_variant(legs, st, variant)
        totals.append(float(kept.net.sum()))
    t = np.array(totals)
    return dict(p50=float(np.percentile(t, 50)), p95=float(np.percentile(t, 95)),
                max=float(t.max()), mean=float(t.mean()))

def mirror_total(legs, states, variant):
    if variant == "G1":
        rem = legs[[bool(states.get(r.date) and states[r.date]["G1"]) and r.direction == "CE"
                    for r in legs.itertuples()]]
    elif variant == "G3":
        rem = legs[[bool(states.get(r.date) and states[r.date]["thr"] and
                         states[r.date]["gap"] <= -states[r.date]["thr"]) and r.direction == "PE"
                    for r in legs.itertuples()]]
    else:
        return None
    return round(float(legs.net.sum() - rem.net.sum()), 2), int(len(rem)), round(float(rem.net.sum()), 2)

# ---------------------------------------------------------------- identity check vs closed filters
def identity_check(stack_legs, v1_legs, removed_map):
    """removed_map: {(book, variant): removed_df}. Compare against closed-filter removed sets
    ON THE SAME streams: BV-1 (Skill V3 PE legs entering >=10:15), BV-2 (all Skill V3 PE legs)
    for Bank; EVE-07 removed set (B PE) lives on the DEC-S1 stream, disjoint from v1 by construction."""
    out = {}
    bv1 = stack_legs[(stack_legs.rep == "Skill V3") & (stack_legs.direction == "PE") &
                     (stack_legs.entry_time >= "10:15")]
    bv2 = stack_legs[(stack_legs.rep == "Skill V3") & (stack_legs.direction == "PE")]
    def key(df):
        return set(zip(df.date.astype(str), df.direction, df.entry_time, df.entry_premium))
    out["bv1_on_stack"] = dict(legs=int(len(bv1)), net=round(float(bv1.net.sum()), 2))
    out["bv2_on_stack"] = dict(legs=int(len(bv2)), net=round(float(bv2.net.sum()), 2))
    for (book, variant), rem in removed_map.items():
        if book != "bank":
            continue
        rk = key(rem)
        for nm, ref in (("bv1", bv1), ("bv2", bv2)):
            fk = key(ref)
            out[f"bank_{variant}_vs_{nm}"] = dict(identical=bool(rk == fk),
                                                 overlap=int(len(rk & fk)),
                                                 guard_removed=int(len(rk)), filter_removed=int(len(fk)))
    # Nifty: v1 stream contains zero B-PE legs by construction -> EVE-07's removed set cannot recur
    out["nifty_v1_contains_B_PE"] = int((((v1.component == "B") & (v1.direction == "PE"))).sum())
    return out

# ---------------------------------------------------------------- run one index
def run_index(name, legs, gaps, nov_legs=None):
    states = guard_states(gaps)
    inc = book_stats(legs)
    res = dict(incumbent=inc, variants={})
    removed_map = {}
    for variant in ("G1", "G2", "G3"):
        kept, rem = apply_variant(legs, states, variant)
        removed_map[(name, variant)] = rem
        cand = book_stats(kept) if len(kept) else dict(total=0.0, legs=0, months={m: 0.0 for m in inc["months"]},
                                                       H1=0.0, H2=0.0, extop3_legs=0.0, extop3_days=0.0, traded_days=0)
        # independent re-sum: candidate total must equal incumbent total - removed sum, exactly
        assert abs(cand["total"] - round(float(inc["total"] - rem.net.sum()), 2)) < 0.011, (name, variant)
        fired_days = sorted(rem.date.unique())
        drop_dirs = "ALL" if variant == "G2" else "PE"
        rnd = random_day_placebo(legs, fired_days, drop_dirs)
        shf = shuffled_gap_placebo(legs, gaps, variant)
        mir = mirror_total(legs, states, variant)
        plac = {}
        if rnd is not None:
            plac["random_day_p95"] = cand["total"] > rnd["p95"]
        if shf is not None:
            plac["shuffled_gap_p95"] = cand["total"] > shf["p95"]
        if mir is not None:
            plac["mirror"] = cand["total"] > mir[0]
        glegs, flips = gate_eval(inc, cand, plac)
        fam = rem["family"].value_counts().to_dict() if "family" in rem else rem["component"].value_counts().to_dict()
        res["variants"][variant] = dict(
            candidate=cand, gate_legs=glegs, gate_pass=bool(all(glegs.values())), month_flips=flips,
            removed=dict(legs=int(len(rem)), net=round(float(rem.net.sum()), 2),
                         days=[str(d)[:10] for d in fired_days], by_family={str(k): int(v) for k, v in fam.items()},
                         detail=[f"{r.date.date()} {r.direction} {getattr(r, 'family', getattr(r, 'component', ''))} {r.entry_time} {r.net:+.2f}"
                                 for r in rem.itertuples()]),
            placebos=dict(random_day=rnd, shuffled_gap=shf,
                          mirror=(dict(total=mir[0], removed_legs=mir[1], removed_net=mir[2]) if mir else None)))
        # kept/removed CSV dumps
        kept.assign(variant=variant, book=name).to_csv(TR / f"november_fix_gapguard_2026-11-13_{name}_{variant}_kept.csv", index=False)
        rem.assign(variant=variant, book=name).to_csv(TR / f"november_fix_gapguard_2026-11-13_{name}_{variant}_removed.csv", index=False)
    if nov_legs is not None:
        nov = {}
        for variant in ("G1", "G2", "G3"):
            kept, rem = apply_variant(nov_legs, states, variant)
            nov[variant] = dict(incumbent_total=round(float(nov_legs.net.sum()), 2),
                                candidate_total=round(float(kept.net.sum()), 2),
                                delta=round(float(kept.net.sum() - nov_legs.net.sum()), 2),
                                removed=[f"{r.date.date()} {r.direction} {r.net:+.2f}" for r in rem.itertuples()])
        res["november_lens"] = nov
        res["november_guard_table"] = {str(r.date)[:10]: dict(gap=round(float(r.gap), 3) if pd.notna(r.gap) else None,
                                       thr=round(float(r.thr), 3) if pd.notna(r.thr) else None,
                                       G1=bool(abs(r.gap) >= r.thr) if pd.notna(r.thr) else None,
                                       G3=bool(r.gap >= r.thr) if pd.notna(r.thr) else None)
                                       for r in gaps[(gaps.date >= "2026-11-02") & (gaps.date <= "2026-11-12")].itertuples()}
    return res, removed_map

# November incumbent legs
nov_stack = pd.read_csv(TR / "november_shadow_stack_bank_log.csv")
nov_stack = nov_stack[pd.to_numeric(nov_stack["net_inr"], errors="coerce").notna()].copy()
nov_stack["date"] = pd.to_datetime(nov_stack["date"]); nov_stack["net"] = nov_stack["net_inr"]
assert len(nov_stack) == 3 and abs(nov_stack.net.sum() - (-960.0)) < 0.01, (len(nov_stack), nov_stack.net.sum())

nov_dec = pd.read_csv(TR / "november_shadow_decs1_nifty_log.csv")
nov_dec = nov_dec[pd.to_numeric(nov_dec["net_inr"], errors="coerce").notna()].copy()
nov_dec["date"] = pd.to_datetime(nov_dec["date"]); nov_dec["net"] = nov_dec["net_inr"]
nov_dec["component"] = nov_dec["system_source"].str.split().str[-1]
nov_v1 = nov_dec[~((nov_dec.component == "B") & (nov_dec.direction == "PE"))].copy()
assert len(nov_v1) == 1 and abs(nov_v1.net.sum() - 3036.50) < 0.01, (len(nov_v1), nov_v1.net.sum())

bank_res, bank_removed = run_index("bank", stack, bank_gaps, nov_stack)
nif_res, nif_removed = run_index("nifty", v1, nif_gaps, nov_v1)
all_removed = dict(bank_removed); all_removed.update(nif_removed)
OUT["bank"] = bank_res
OUT["nifty"] = nif_res
OUT["identity_check"] = identity_check(stack, v1, all_removed)
OUT["november_anchors"] = dict(bank_stack_legs=int(len(nov_stack)), bank_stack_total=float(nov_stack.net.sum()),
                               nifty_v1_legs=int(len(nov_v1)), nifty_v1_total=float(nov_v1.net.sum()),
                               nifty_v1_detail=[f"{r.date.date()} {r.component} {r.direction} {r.net:+.2f}" for r in nov_v1.itertuples()])

with open(TR / "november_fix_gapguard_2026-11-13_results.json", "w") as f:
    json.dump(OUT, f, indent=1, default=str)

for name, res in (("BANK stack v2", bank_res), ("NIFTY TUNED v1", nif_res)):
    print(f"\n===== {name} =====")
    print("incumbent:", json.dumps(res["incumbent"], default=str))
    for v, vr in res["variants"].items():
        print(f"-- {v}: cand_total={vr['candidate']['total']} legs={vr['candidate']['legs']} "
              f"removed={vr['removed']['legs']} legs net {vr['removed']['net']} on {len(vr['removed']['days'])} days "
              f"GATE_PASS={vr['gate_pass']} legs={vr['gate_legs']} flips={vr['month_flips']}")
        print(f"   placebos: rnd={vr['placebos']['random_day']} shf_p95={vr['placebos']['shuffled_gap']['p95'] if vr['placebos']['shuffled_gap'] else None} mirror={vr['placebos']['mirror']}")
    print("november lens:", json.dumps(res.get("november_lens"), default=str))
    print("november guard table:", json.dumps(res.get("november_guard_table"), default=str))
print("\nIDENTITY:", json.dumps(OUT["identity_check"], indent=1, default=str))
print("\nDONE -> november_fix_gapguard_2026-11-13_results.json")
