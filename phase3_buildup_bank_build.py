#!/usr/bin/env python3
"""Phase-3 tuning, Bank Nifty — buildup/speculation conditioning on TUNED STACK v2.
Spec: phase3_buildup_bank_SPEC.md (frozen before scoring). Research only."""
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

# ================= legs (loaded exactly as phase 2) =================
feat = {}
for r in csv.DictReader(open(D + "solid60_programme_2026-11-13_bank_A_stack_features.csv")):
    feat[(r["date"], r["entry_time"], float(r["entry_premium"]))] = r
legs = []
for r in csv.DictReader(open(D + "november_books_fix_anatomy_legs.csv")):
    if r["book"] != "BANK_STACK":
        continue
    k = (r["date"], r["entry_time"], float(r["entry_premium"]))
    legs.append({"date": r["date"], "side": r["side"], "family": r["family"],
                 "rep": r["rep"], "entry_time": r["entry_time"],
                 "premium": float(r["entry_premium"]), "net": float(r["net"])})
assert len(legs) == 111, len(legs)

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

# ================= day map / sequence =================
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
    """(bars_dict, complete?) for day's in-force futures over 09:15..R-5."""
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

# ================= morning state =================
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
    if day in ("2026-01-01", "2026-06-01", "2026-11-02"):
        print("state sample", day, {R: (STATE[(day, R)]["fut"], STATE[(day, R)]["spec"],
                                        STATE[(day, R)]["vol"]) for R in READS}, flush=True)

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

# ================= conditioners =================
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

def make_rule(name):
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
    if name.startswith("D"):
        t = float(name[1:])
        return (("fut", "vol"), lambda l, st: not opposed_align(l["side"], st["fut"]["class"])
                and st["vol"][0] is not None and st["vol"][0] >= t)
    if name == "E":
        return (("fut", "spec", "vol"), lambda l, st: not opposed_align(l["side"], st["fut"]["class"])
                and not opposed_spec(l["side"], st["spec"]["lean"])
                and st["vol"][0] is not None and st["vol"][0] >= 1.0)
    raise ValueError(name)

GRID = ["A", "B", "C1.0", "C1.1", "C1.25", "C5-1.0", "C5-1.1", "C5-1.25",
        "D1.0", "D1.1", "E"]

def component_ok(needs, st):
    for n in needs:
        if n == "fut" and st["fut"] is None: return False
        if n == "spec" and st["spec"] is None: return False
        if n == "vol" and (st["fut"] is None or st["vol"][0] is None): return False
        if n == "vol5" and (st["fut"] is None or st["vol"][1] is None): return False
    return True

FULL_MONTHS = sorted({l["date"][:7] for l in legs})
random.seed(42)
results = {"control": ctrl, "control_ok": ctrl_ok, "coverage": coverage, "grid": {}}

for R in READS:
    results["grid"][R] = {}
    for name in GRID:
        needs, rule = make_rule(name)
        kept, dropped, nc_kept = [], [], 0
        for l in legs:
            if l["entry_time"] < R:
                kept.append(l); continue
            st = STATE[(l["date"], R)]
            if not component_ok(needs, st):
                kept.append(l); nc_kept += 1; continue
            (kept if rule(l, st) else dropped).append(l)
        m = metrics(kept)
        k = len(kept)
        draws = sorted(round(sum(x["net"] for x in random.sample(legs, k)), 2)
                       for _ in range(200))
        p95 = draws[int(0.95 * 200) - 1]
        pct = round(100 * sum(1 for d in draws if d < m["total"]) / 200, 1)
        kept_ids = {id(x) for x in kept}
        flipped = [l for l in legs if id(l) not in kept_ids]
        # flipped book per spec = pre-read + NC-kept + dropped = all legs minus
        # the post-read legs the conditioner kept. kept set already includes
        # pre-read + NC; the conditioned-kept post-read legs are:
        cond_kept = [l for l in kept if l["entry_time"] >= R
                     and component_ok(needs, STATE[(l["date"], R)])]
        flipped_book = [l for l in legs if id(l) not in {id(x) for x in cond_kept}]
        flip_total = round(sum(l["net"] for l in flipped_book), 2)
        checks = {"wr_ge_60": m["win_rate_pct"] >= 60.0,
                  "per_td_ge_900": m["per_trade_day"] >= 900,
                  "total_ge_60pct": m["total"] >= 0.60 * 127351.50,
                  "halves_positive": m["halves"]["H1"] > 0 and m["halves"]["H2"] > 0,
                  "ex_top3_positive": (m["ex_top3_total"] or 0) > 0,
                  "placebo_beats_95pct": m["total"] > p95,
                  "beats_flipped": m["total"] > flip_total,
                  "no_red_month": m["red_months"] == []}
        idled_months = [mm for mm in FULL_MONTHS if mm not in m["months"]]
        results["grid"][R][name] = {
            "metrics": m, "kept_legs": k, "dropped_legs": len(dropped),
            "dropped_total": round(sum(l["net"] for l in dropped), 2),
            "nc_kept": nc_kept, "placebo": {"p95_total": p95, "kept_percentile": pct},
            "flipped_total": flip_total, "fully_idled_months": idled_months,
            "checks": checks, "verdict": "PASS" if all(checks.values()) else "FAIL",
            "failing": [c for c, v in checks.items() if not v]}
        print(R, name, "kept", k, "drop", len(dropped), "total", m["total"],
              "WR", m["win_rate_pct"], "perTD", m["per_trade_day"], "pct", pct,
              "flip", flip_total, results["grid"][R][name]["verdict"],
              results["grid"][R][name]["failing"], flush=True)

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
nov_state = {}
for n in nov_legs:
    row = {"date": n["date"], "rep": n["rep"], "side": n["side"],
           "entry_time": n["entry_time"], "premium": n["premium"], "net": n["net"],
           "state": {}}
    for R in READS:
        st = STATE[(n["date"], R)]
        row["state"][R] = {"fut_class": st["fut"]["class"] if st["fut"] else None,
                           "spec_lean": st["spec"]["lean"] if st["spec"] else None,
                           "ratio_prev": (round(st["vol"][0], 3) if st["vol"][0] is not None else None),
                           "ratio_5d": (round(st["vol"][1], 3) if st["vol"][1] is not None else None)}
    nov_out["legs"].append(row)
for R in READS:
    nov_out["by_grid"][R] = {}
    for name in GRID:
        needs, rule = make_rule(name)
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
    print("NOV", R, {g: nov_out["by_grid"][R][g]["kept_total"] for g in GRID}, flush=True)
results["november"] = nov_out

with open(D + "phase3_buildup_bank_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("WROTE phase3_buildup_bank_results.json")
