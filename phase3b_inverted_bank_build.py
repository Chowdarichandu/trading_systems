#!/usr/bin/env python3
"""Phase-3B tuning, Bank Nifty — INVERTED conditioning (quiet-volume +
speculation-fade) on TUNED STACK v2. Spec: phase3b_inverted_bank_SPEC.md
(frozen 2026-11-14 09:09 IST, before scoring). Research only.

State code, metrics, NC philosophy and flipped-book definition are phase 3's
own (phase3_buildup_bank_build.py), copied verbatim so the state is
identical by construction; phase-3 grid points A/B/C1.0/C5-1.0 are then
recomputed and asserted equal to phase 3's published numbers BEFORE any
phase-3B point is scored. The phase-2 confidence kept set is recomputed
with phase 2's own scoring code and asserted against its published values.
"""
import csv, json, random, glob
from collections import defaultdict
from pathlib import Path

D = "/home/hatch/workspace/trading/"
TOTAL_DAYS = 205
READS = ("10:00", "11:00")

def t2m(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)

def last_state_time(R):
    m = t2m(R) - 5
    return f"{m // 60:02d}:{m % 60:02d}"

def window_times(R):
    out, m = [], t2m("09:15")
    while m < t2m(R):
        out.append(f"{m // 60:02d}:{m % 60:02d}")
        m += 5
    return out

def key(l):
    return (l["date"], l["entry_time"], l["premium"])

# ================= legs (loaded exactly as phase 2: features join) =================
feat = {}
for r in csv.DictReader(open(D + "solid60_programme_2026-11-13_bank_A_stack_features.csv")):
    feat[(r["date"], r["entry_time"], float(r["entry_premium"]))] = r
legs = []
for r in csv.DictReader(open(D + "november_books_fix_anatomy_legs.csv")):
    if r["book"] != "BANK_STACK":
        continue
    k = (r["date"], r["entry_time"], float(r["entry_premium"]))
    fr = feat[k]
    legs.append({"date": r["date"], "side": r["side"], "family": r["family"],
                 "rep": r["rep"], "entry_time": r["entry_time"],
                 "premium": float(r["entry_premium"]), "net": float(r["net"]),
                 "gap_pct": float(r["gap_pct"]), "agree": int(fr["agree"]),
                 "second": int(fr["second"]), "tod": fr["tod"]})
assert len(legs) == 111, len(legs)

# ================= metrics (phase 3's, verbatim) =================
def metrics(ls):
    total = round(sum(l["net"] for l in ls), 2)
    dm = defaultdict(float)
    for l in ls: dm[l["date"]] += l["net"]
    wins = sum(1 for l in ls if l["net"] > 0)
    months = {}
    for m in sorted({l["date"][:7] for l in ls}):
        months[m] = round(sum(l["net"] for l in ls if l["date"][:7] == m), 2)
    h1 = round(sum(l["net"] for l in ls if l["date"][:7] in
                   ("2026-01", "2026-02", "2026-03", "2026-04", "2026-05")), 2)
    srt = sorted(ls, key=lambda l: -l["net"])
    extop3 = round(total - sum(l["net"] for l in srt[:3]), 2) if len(ls) > 3 else None
    return {"legs": len(ls), "total": total, "trade_days": len(dm),
            "per_trade_day": round(total / len(dm), 2) if dm else 0.0,
            "win_rate_pct": round(100 * wins / len(ls), 1) if ls else 0.0,
            "green_days": sum(1 for v in dm.values() if v > 0),
            "red_days": sum(1 for v in dm.values() if v < 0),
            "no_trade_days": TOTAL_DAYS - len(dm),
            "months": months, "red_months": [m for m, v in months.items() if v < 0],
            "halves": {"H1": h1, "H2": round(total - h1, 2)}, "ex_top3_total": extop3}

# ================= CONTROL =================
ctrl = metrics(legs)
raw_sum = round(sum(float(r["x1_net"]) for r in
                    csv.DictReader(open(D + "solid60_programme_2026-11-13_bank_A_stack_features.csv"))), 2)
ctrl_ok = (ctrl["legs"] == 111 and ctrl["total"] == 127351.50 and ctrl["trade_days"] == 89
           and ctrl["per_trade_day"] == 1430.92 and ctrl["win_rate_pct"] == 59.5
           and ctrl["green_days"] == 60 and ctrl["red_days"] == 29
           and ctrl["no_trade_days"] == 116 and ctrl["halves"]["H1"] == 83082.00
           and ctrl["halves"]["H2"] == 44269.50 and ctrl["ex_top3_total"] == 100528.50
           and ctrl["red_months"] == [] and raw_sum == 127351.50)
print("CONTROL:", json.dumps(ctrl), "| re-sum:", raw_sum, "| OK:", ctrl_ok, flush=True)
if not ctrl_ok:
    raise SystemExit("CONTROL FAILED — stopping per spec, no scoring performed.")

# ================= phase-2 reference sets (phase 2's own code) =================
MEDIAN_PREM = 692.50
v21 = list(csv.DictReader(open(D + "bank_engine_r6_v21_trades.csv")))
for l in legs:
    l["f6"] = 0.0
    if l["second"] != 1:
        continue
    anchor_net = None
    if l["family"] == "EVE06_REENTRY":
        prior = [x for x in legs if x["date"] == l["date"] and t2m(x["entry_time"]) < t2m(l["entry_time"])]
        if prior:
            anchor_net = sorted(prior, key=lambda x: t2m(x["entry_time"]))[-1]["net"]
    elif l["family"] == "NS1_second":
        cand = [x for x in v21 if x["date"] == l["date"] and x["family"] == "BASE"
                and t2m(x["exit_time"]) <= t2m(l["entry_time"])]
        if cand:
            anchor_net = float(sorted(cand, key=lambda x: t2m(x["exit_time"]))[-1]["net_inr"])
    if anchor_net is not None:
        l["f6"] = 0.5 if anchor_net > 0 else -0.5

def score_leg(l):
    f1 = 1.0 if l["agree"] >= 2 else (0.5 if l["agree"] == 1 else 0.0)
    r = l["premium"] / MEDIAN_PREM
    f2 = 1.0 if r < 0.75 else (0.5 if r < 1.0 else (0.0 if r < 1.45 else -0.5))
    f3 = {"early": 0.5, "mid": 0.0, "late": -0.5}[l["tod"]]
    aligned = (l["side"] == "CE" and l["gap_pct"] > 0) or (l["side"] == "PE" and l["gap_pct"] < 0)
    against = (l["side"] == "CE" and l["gap_pct"] < 0) or (l["side"] == "PE" and l["gap_pct"] > 0)
    ag = abs(l["gap_pct"])
    f4 = 0.0 if ag < 0.05 else (0.5 if (aligned and ag >= 0.30) else
                                (0.25 if aligned else -0.5 if against else 0.0))
    f5 = 0.5 if l["second"] == 1 else 0.0
    return f1 + f2 + f3 + f4 + f5 + l["f6"]
for l in legs:
    l["score"] = score_leg(l)

confgate_kept = [l for l in legs if l["score"] >= 0.5]
confgate_keys = {key(l) for l in confgate_kept}
cm = metrics(confgate_kept)
bfix1_kept = [l for l in legs if not (l["side"] == "PE" and l["gap_pct"] < 0
                                      and 500 <= l["premium"] <= 800)]
bfix1_keys = {key(l) for l in bfix1_kept}
bm = metrics(bfix1_kept)
inter2 = len(confgate_keys & bfix1_keys)
ref_ok = (len(confgate_kept) == 88 and cm["total"] == 122337.50
          and cm["win_rate_pct"] == 62.5 and len(bfix1_kept) == 94
          and bm["total"] == 131510.00 and inter2 == 71
          and round(100 * inter2 / len(confgate_keys), 1) == 80.7
          and round(100 * inter2 / len(confgate_keys | bfix1_keys), 1) == 64.0)
print("REF SETS: confgate kept", len(confgate_kept), cm["total"], "WR", cm["win_rate_pct"],
      "| B-FIX-1 kept", len(bfix1_kept), bm["total"], "| intersection", inter2,
      "| OK:", ref_ok, flush=True)
if not ref_ok:
    raise SystemExit("REFERENCE SET VALIDATION FAILED — stopping per spec.")

# ================= day map / sequence (phase 3's, verbatim) =================
oi_rows = {}
for r in csv.DictReader(open(D + "oi_history/banknifty_daily_oi.csv")):
    oi_rows[r["date"]] = r
JANOCT = sorted(d for d in oi_rows if "2026-01-01" <= d <= "2026-10-31")
assert len(JANOCT) == 205, len(JANOCT)
NOV = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
       "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
ALLDAYS = JANOCT + NOV
EXPIRY = {d: oi_rows[d]["expiry"] for d in JANOCT}
for d in NOV: EXPIRY[d] = "2026-11-23"
PREV = {ALLDAYS[i]: ALLDAYS[i - 1] for i in range(1, len(ALLDAYS))}
PREV5 = {ALLDAYS[i]: ALLDAYS[max(0, i - 5):i] for i in range(len(ALLDAYS))}

# ================= spot (band anchor) =================
SPOT = {}
raw = json.load(open(D + "daily2leg/spot.json"))["BANKNIFTY"]
for d, bars in raw.items():
    SPOT[d] = {b[0]: float(b[4]) for b in bars}
nov_bars = json.loads(Path(D + "oi_history/spot_nov_bars.json").read_text())
for d, bars in nov_bars.get("BANKNIFTY", {}).items():
    SPOT.setdefault(d, {b[0]: float(b[4]) for b in bars})

def open_band(day):
    bars = SPOT.get(day)
    if not bars or "09:15" not in bars:
        return None
    atm = int(round(bars["09:15"] / 100.0)) * 100
    return [atm + 100 * k for k in range(-5, 6)]

# ================= futures =================
FUT = {}
for exp in sorted(set(EXPIRY.values())):
    fn = Path(D + f"round5_history/FUT7_{exp}.json")
    if not fn.exists():
        continue
    days = {}
    for r in json.loads(fn.read_text()):
        days.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]), float(r[4]),
                                           float(r[5]), float(r[6]), float(r[7]))
    FUT[exp] = days

def fut_window(day, R):
    days = FUT.get(EXPIRY[day], {})
    bars = days.get(day)
    if not bars:
        return None, False
    wt = window_times(R)
    if any(t not in bars for t in wt):
        return None, False
    return {t: bars[t] for t in wt}, True

# ================= options chunks =================
_chunk_cache = {}
def contract_bars(exp, s, t):
    ck = (exp, s, t)
    if ck in _chunk_cache:
        return _chunk_cache[ck]
    days = {}
    for fn in sorted(glob.glob(D + f"round5_ioi_data/chunks/chunk_{exp}_{s}{t}_*.json")):
        body = json.loads(Path(fn).read_text())
        for c in ((body.get("data") or {}).get("candles") or []):
            days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                float(c[5]), float(c[6]))
    _chunk_cache[ck] = days
    return days

# ================= morning state (phase 3's, verbatim) =================
def fut_state(day, R):
    bars, ok = fut_window(day, R)
    if not ok:
        return None
    lst = last_state_time(R)
    c0, oi0 = bars["09:15"][3], bars["09:15"][5]
    c1, oi1 = bars[lst][3], bars[lst][5]
    if oi0 == 0:
        return None
    pchg = (c1 - c0) / c0 * 100.0
    ochg = (oi1 - oi0) / oi0 * 100.0
    vol = sum(b[4] for b in bars.values())
    if abs(ochg) <= 0.5 or pchg == 0:
        cls = "NEUTRAL"
    elif pchg > 0 and ochg > 0: cls = "LONG_BUILDUP"
    elif pchg < 0 and ochg > 0: cls = "SHORT_BUILDUP"
    elif pchg < 0 and ochg < 0: cls = "LONG_UNWINDING"
    else: cls = "SHORT_COVERING"
    return {"class": cls, "price_chg_pct": round(pchg, 4), "oi_chg_pct": round(ochg, 4),
            "cum_vol": vol}

def vol_ratios(day, R):
    st = fut_state(day, R)
    if st is None:
        return None, None
    pd = PREV.get(day)
    rp = None
    if pd:
        pb, ok = fut_window(pd, R)
        if ok:
            pv = sum(b[4] for b in pb.values())
            rp = st["cum_vol"] / pv if pv > 0 else None
    r5 = None
    p5 = PREV5.get(day, [])
    if len(p5) == 5:
        vols = []
        for q in p5:
            qb, ok = fut_window(q, R)
            if not ok:
                vols = None; break
            vols.append(sum(b[4] for b in qb.values()))
        if vols:
            m = sum(vols) / 5.0
            r5 = st["cum_vol"] / m if m > 0 else None
    return rp, r5

def spec_state(day, R):
    band = open_band(day)
    if band is None:
        return None
    lst = last_state_time(R)
    exp = EXPIRY[day]
    agg = {}
    for t in ("CE", "PE"):
        tot = 0.0
        for s in band:
            bars = contract_bars(exp, s, t).get(day, {})
            b0, b1 = bars.get("09:15"), bars.get(lst)
            if b0 is None or b1 is None:
                return None
            tot += b1[5] - b0[5]
        agg[t] = tot
    den = abs(agg["CE"]) + abs(agg["PE"])
    idx = 0.0 if den == 0 else (agg["CE"] - agg["PE"]) / den
    lean = "LONG" if idx > 0.15 else ("SHORT" if idx < -0.15 else "FLAT")
    return {"lean": lean, "index": round(idx, 4),
            "d_ce": agg["CE"], "d_pe": agg["PE"]}

STATE = {}
for day in ALLDAYS:
    for R in READS:
        STATE[(day, R)] = {"fut": fut_state(day, R), "spec": spec_state(day, R),
                           "vol": vol_ratios(day, R)}

coverage = {}
for R in READS:
    coverage[R] = {
        "fut_complete_days_janoct": sum(1 for d in JANOCT if STATE[(d, R)]["fut"]),
        "spec_complete_days_janoct": sum(1 for d in JANOCT if STATE[(d, R)]["spec"]),
        "legs_post_read": sum(1 for l in legs if l["entry_time"] >= R),
        "legs_post_read_fut_ok": sum(1 for l in legs if l["entry_time"] >= R
                                     and STATE[(l["date"], R)]["fut"]),
        "legs_post_read_spec_ok": sum(1 for l in legs if l["entry_time"] >= R
                                      and STATE[(l["date"], R)]["spec"]),
    }
print("COVERAGE:", json.dumps(coverage), flush=True)

# ================= shared conditioner machinery (phase 3's) =================
BULL = {"LONG_BUILDUP", "SHORT_COVERING"}
BEAR = {"SHORT_BUILDUP", "LONG_UNWINDING"}

def opposed_align(side, cls):
    if cls in BULL: return side == "PE"
    if cls in BEAR: return side == "CE"
    return False

def opposed_spec(side, lean):
    if lean == "LONG": return side == "PE"
    if lean == "SHORT": return side == "CE"
    return False

def component_ok(needs, st):
    for n in needs:
        if n == "fut" and st["fut"] is None: return False
        if n == "spec" and st["spec"] is None: return False
        if n == "vol" and (st["fut"] is None or st["vol"][0] is None): return False
        if n == "vol5" and (st["fut"] is None or st["vol"][1] is None): return False
    return True

def apply_rule(legs_in, R, needs, rule):
    kept, dropped, cond_kept = [], [], []
    nc_kept = 0
    for l in legs_in:
        if l["entry_time"] < R:
            kept.append(l); continue
        st = STATE[(l["date"], R)]
        if not component_ok(needs, st):
            kept.append(l); nc_kept += 1; continue
        if rule(l, st):
            kept.append(l); cond_kept.append(l)
        else:
            dropped.append(l)
    return kept, dropped, nc_kept, cond_kept

# ================= STATE VALIDATION: phase-3 points recomputed =================
def p3_rule(name):
    if name == "A":
        return (("fut",), lambda l, st: not opposed_align(l["side"], st["fut"]["class"]))
    if name == "B":
        return (("fut", "spec"), lambda l, st: not opposed_align(l["side"], st["fut"]["class"])
                and not opposed_spec(l["side"], st["spec"]["lean"]))
    if name.startswith("C5-"):
        t = float(name[3:])
        return (("vol5",), lambda l, st: st["vol"][1] is not None and st["vol"][1] >= t)
    if name.startswith("C"):
        t = float(name[1:])
        return (("vol",), lambda l, st: st["vol"][0] is not None and st["vol"][0] >= t)
    raise ValueError(name)

P3_EXPECT = {
    ("10:00", "A"):     (93, 18, 24603.00, 102748.50),
    ("10:00", "B"):     (82, 29, 33056.50, 94295.00),
    ("10:00", "C1.0"):  (55, 56, 53717.50, 73634.00),
    ("10:00", "C5-1.0"): (54, 57, 75847.50, 51504.00),
    ("11:00", "A"):     (100, 11, 13469.50, 113882.00),
    ("11:00", "B"):     (94, 17, 17549.50, 109802.00),
    ("11:00", "C1.0"):  (76, 35, 29051.50, 98300.00),
    ("11:00", "C5-1.0"): (77, 34, 27771.50, 99580.00),
}
val_ok = (coverage["10:00"]["fut_complete_days_janoct"] == 205
          and coverage["11:00"]["fut_complete_days_janoct"] == 205
          and coverage["10:00"]["spec_complete_days_janoct"] == 116
          and coverage["11:00"]["spec_complete_days_janoct"] == 116
          and coverage["10:00"]["legs_post_read"] == 76
          and coverage["11:00"]["legs_post_read"] == 42
          and coverage["10:00"]["legs_post_read_spec_ok"] == 44
          and coverage["11:00"]["legs_post_read_spec_ok"] == 27)
for (R, name), (ek, ed, edt, ekt) in P3_EXPECT.items():
    needs, rule = p3_rule(name)
    kept, dropped, nc, ck = apply_rule(legs, R, needs, rule)
    got = (len(kept), len(dropped), round(sum(l["net"] for l in dropped), 2),
           round(sum(l["net"] for l in kept), 2))
    ok = got == (ek, ed, edt, ekt)
    val_ok = val_ok and ok
    print("VALIDATE", R, name, "got", got, "expect", (ek, ed, edt, ekt), "OK:", ok, flush=True)
print("STATE VALIDATION OK:", val_ok, flush=True)
if not val_ok:
    raise SystemExit("STATE VALIDATION FAILED — stopping per spec, no phase-3B scoring.")

# ================= phase-3B grid =================
def agrees_spec(side, lean):
    return (lean == "LONG" and side == "CE") or (lean == "SHORT" and side == "PE")

def sf_rule(l, st):
    return not agrees_spec(l["side"], st["spec"]["lean"])

def make_rule3b(name):
    if name.startswith("QVP-"):
        t = float(name[4:])
        return (("vol",), lambda l, st: st["vol"][0] <= t)
    if name.startswith("QV5-"):
        t = float(name[4:])
        return (("vol5",), lambda l, st: st["vol"][1] <= t)
    if name == "SF":
        return (("spec",), sf_rule)
    if name == "QFP-0.9":
        return (("vol", "spec"), lambda l, st: st["vol"][0] <= 0.9 and sf_rule(l, st))
    if name == "QF5-0.9":
        return (("vol5", "spec"), lambda l, st: st["vol"][1] <= 0.9 and sf_rule(l, st))
    raise ValueError(name)

GRID = ["QVP-1.0", "QVP-0.9", "QVP-0.8", "QV5-1.0", "QV5-0.9", "QV5-0.8",
        "SF", "QFP-0.9", "QF5-0.9"]
FULL_MONTHS = sorted({l["date"][:7] for l in legs})

def overlap_block(kept):
    kk = {key(l) for l in kept}
    out = {}
    for label, ref in (("phase2_confgate_ge0.5", confgate_keys), ("bfix1", bfix1_keys)):
        inter = len(kk & ref)
        out[label] = {"ref_kept": len(ref), "intersection": inter,
                      "share_of_kept_pct": round(100 * inter / len(kk), 1) if kk else 0.0,
                      "jaccard_pct": round(100 * inter / len(kk | ref), 1) if kk else 0.0}
    return out

random.seed(42)
results = {"control": ctrl, "control_ok": ctrl_ok, "coverage": coverage,
           "state_validation": "PASS — coverage + phase-3 points A/B/C1.0/C5-1.0 at both "
                               "reads reproduced exactly",
           "reference_sets": {"phase2_confgate_ge0.5": {"kept": len(confgate_kept),
                                                       "total": cm["total"],
                                                       "win_rate_pct": cm["win_rate_pct"]},
                              "bfix1": {"kept": len(bfix1_kept), "total": bm["total"]},
                              "intersection_confgate_bfix1": inter2},
           "grid": {}}

for R in READS:
    results["grid"][R] = {}
    for name in GRID:
        needs, rule = make_rule3b(name)
        kept, dropped, nc_kept, cond_kept = apply_rule(legs, R, needs, rule)
        m = metrics(kept)
        k = len(kept)
        draws = sorted(round(sum(x["net"] for x in random.sample(legs, k)), 2)
                       for _ in range(200))
        p95 = draws[int(0.95 * 200) - 1]
        pct = round(100 * sum(1 for d in draws if d < m["total"]) / 200, 1)
        cond_ids = {id(x) for x in cond_kept}
        flipped_book = [l for l in legs if id(l) not in cond_ids]
        flip_total = round(sum(l["net"] for l in flipped_book), 2)
        dropped_total = round(sum(l["net"] for l in dropped), 2)
        checks = {"wr_ge_60": m["win_rate_pct"] >= 60.0,
                  "per_td_ge_900": m["per_trade_day"] >= 900,
                  "total_ge_60pct": m["total"] >= 0.60 * 127351.50,
                  "halves_positive": m["halves"]["H1"] > 0 and m["halves"]["H2"] > 0,
                  "ex_top3_positive": (m["ex_top3_total"] or 0) > 0,
                  "placebo_beats_95pct": m["total"] > p95,
                  "beats_flipped": m["total"] > flip_total,
                  "beats_dropped": m["total"] > dropped_total,
                  "no_red_month": m["red_months"] == []}
        # boundary ties (post-read, component-ok legs sitting exactly on the threshold)
        ties = None
        if name.startswith(("QVP-", "QV5-")):
            t = float(name[4:])
            idx = 0 if name.startswith("QVP-") else 1
            ties = sum(1 for l in legs if l["entry_time"] >= R
                       and STATE[(l["date"], R)]["vol"][idx] is not None
                       and abs(STATE[(l["date"], R)]["vol"][idx] - t) < 1e-12)
        results["grid"][R][name] = {
            "metrics": m, "kept_legs": k, "dropped_legs": len(dropped),
            "dropped_total": dropped_total, "nc_kept": nc_kept,
            "nc_share_of_kept_pct": round(100 * nc_kept / k, 1) if k else 0.0,
            "placebo": {"p95_total": p95, "kept_percentile": pct},
            "flipped_total": flip_total,
            "fully_idled_months": [mm for mm in FULL_MONTHS if mm not in m["months"]],
            "boundary_ties_at_threshold": ties,
            "overlap": overlap_block(kept),
            "checks": checks, "verdict": "PASS" if all(checks.values()) else "FAIL",
            "failing": [c for c, v in checks.items() if not v]}
        print(R, name, "kept", k, "drop", len(dropped), "dropRs", dropped_total,
              "total", m["total"], "WR", m["win_rate_pct"], "perTD", m["per_trade_day"],
              "pct", pct, "flip", flip_total, "nc", nc_kept,
              results["grid"][R][name]["verdict"], results["grid"][R][name]["failing"],
              flush=True)

# ================= November counterfactual =================
nov_legs = []
for r in csv.DictReader(open(D + "november_shadow_stack_bank_log.csv")):
    if not r.get("entry_premium"):
        continue
    nov_legs.append({"date": r["date"], "side": r["direction"], "rep": r["rep"],
                     "entry_time": r["entry_time"],
                     "premium": float(r["entry_premium"]), "net": float(r["net_inr"])})
nov_actual = round(sum(n["net"] for n in nov_legs), 2)
nov_out = {"actual_total": nov_actual, "legs": [], "by_grid": {}}
for n in nov_legs:
    row = {"date": n["date"], "rep": n["rep"], "side": n["side"],
           "entry_time": n["entry_time"], "premium": n["premium"], "net": n["net"],
           "state": {}}
    for R in READS:
        st = STATE[(n["date"], R)]
        row["state"][R] = {"fut_class": st["fut"]["class"] if st["fut"] else None,
                           "spec_lean": st["spec"]["lean"] if st["spec"] else None,
                           "spec_nc": st["spec"] is None,
                           "ratio_prev": (round(st["vol"][0], 3) if st["vol"][0] is not None else None),
                           "ratio_5d": (round(st["vol"][1], 3) if st["vol"][1] is not None else None)}
    nov_out["legs"].append(row)
spec_nc_all_nov = all(row["state"][R]["spec_nc"] for row in nov_out["legs"] for R in READS)
print("NOV speculation NC on all leg-days/reads:", spec_nc_all_nov, flush=True)
nov_out["spec_nc_all_leg_days"] = spec_nc_all_nov
NOVG = GRID  # same points
for R in READS:
    nov_out["by_grid"][R] = {}
    for name in NOVG:
        needs, rule = make_rule3b(name)
        kept, detail = [], []
        for n in nov_legs:
            if n["entry_time"] < R:
                kept.append(n); detail.append((n["date"], "KEPT-pre-read")); continue
            st = STATE[(n["date"], R)]
            if not component_ok(needs, st):
                kept.append(n); detail.append((n["date"], "KEPT-NC")); continue
            if rule(n, st):
                kept.append(n); detail.append((n["date"], "KEPT"))
            else:
                detail.append((n["date"], "IDLED"))
        nov_out["by_grid"][R][name] = {
            "kept_total": round(sum(n["net"] for n in kept), 2), "detail": detail}
    print("NOV", R, {g: nov_out["by_grid"][R][g]["kept_total"] for g in NOVG}, flush=True)
results["november"] = nov_out

with open(D + "phase3b_inverted_bank_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE phase3b_inverted_bank_results.json")
