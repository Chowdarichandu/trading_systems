#!/usr/bin/env python3
"""PHASE-3 BUILDUP NIFTY - scorer. Spec: phase3_buildup_nifty_SPEC.md
(frozen 2026-11-14 09:09 IST, before any scoring).
Conditions TUNED v1's own 74 legs on the morning buildup/speculation
state. Research only - no book, ledger or job is touched.
Implementation reading disclosed: RELVOL/RELVOL5 prev-day volumes use
TODAY'S in-force futures contract on the previous trading days (the
spec pins the days, not the contract; same-contract avoids the
front-switch volume artefact)."""
import csv, json, random, sys
from pathlib import Path
from collections import defaultdict
import pandas as pd

TR = Path.home() / "workspace/trading"
OUTJ = TR / "phase3_buildup_nifty_results.json"
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
            "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
            "2026-09-29", "2026-10-27", "2026-11-23"]
READS = {"10:00": "09:55", "11:00": "10:55"}
GRID = ["ALIGN", "ALIGN+SPEC", "VOL-1.0", "VOL-1.1", "VOL-1.25",
        "VOL5-1.1", "PF-ALIGN", "PF-ALIGN+SPEC", "FB-ONLY", "FB-COMBO"]
TOTAL_BAR = 61830.15

def in_force(day):
    for e in EXPIRIES:
        if e >= day:
            return e
    return None

# ---------------- spot ----------------
s = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv")
s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
s["date"] = s["timestamp"].dt.strftime("%Y-%m-%d")
s["time"] = s["timestamp"].dt.strftime("%H:%M")
SPOT = {}
for d, g in s.groupby("date"):
    if len(g) >= 70:
        SPOT[d] = {r.time: float(r.close) for r in g.itertuples()}
CAL205 = sorted(r[0] for r in csv.reader(open(TR / "volrix/nifty_daily_2019_2026.csv"))
                if r and r[0].startswith("2026-") and r[0] <= "2026-10-31"
                and r[0] != "date")
SPOTDAYS = sorted(SPOT)
PREV = {SPOTDAYS[i]: SPOTDAYS[i - 1] for i in range(1, len(SPOTDAYS))}
PREV5 = {SPOTDAYS[i]: SPOTDAYS[max(0, i - 5):i] for i in range(len(SPOTDAYS))}

# ---------------- futures ----------------
FUT = {}   # exp -> {day: {time: (close, vol, oi)}}
import glob
for fn in glob.glob(str(TR / "phase3_buildup_data/futures/FUT7_NIFTY_*.json")):
    exp = fn.split("FUT7_NIFTY_")[1].split("_")[0]
    try:
        body = json.loads(Path(fn).read_text())
    except Exception:
        continue
    d = FUT.setdefault(exp, {})
    for c in ((body.get("data") or {}).get("candles") or []):
        day, t = c[0][:10], c[0][11:16]
        d.setdefault(day, {})[t] = (float(c[4]), float(c[5]), float(c[6]))

def win_times(last):
    out, t = [], "09:15"
    while t <= last:
        out.append(t)
        h, m = map(int, t.split(":"))
        m += 5
        if m >= 60:
            h, m = h + 1, m - 60
        t = f"{h:02d}:{m:02d}"
    return out

# ---------------- option OI cache ----------------
def opt_oi(exp, strike, typ, day):
    fn = TR / "oi_buildup_data" / f"candles_NIFTY_{strike}{typ}_{exp}_{day}.json"
    if not fn.exists():
        return None
    try:
        body = json.loads(fn.read_text())
    except Exception:
        return None
    out = {}
    for c in ((body.get("data") or {}).get("candles") or []):
        if c[0][:10] == day:
            out[c[0][11:16]] = float(c[6])
    return out or None

# ---------------- morning state ----------------
def morning_state(day, read):
    """Returns dict with components; each component None if NC."""
    last = READS[read]
    exp = in_force(day)
    st = {"exp": exp, "buildup": None, "relvol": None, "relvol5": None,
          "crowd": None, "spec_idx": None, "dp": None, "doi": None}
    fut = FUT.get(exp, {}).get(day, {})
    times = win_times(last)
    if "09:15" in fut and last in fut:
        c0, _, oi0 = fut["09:15"]
        c1, _, oi1 = fut[last]
        if oi0 > 0 and c0 > 0:
            dp = (c1 / c0 - 1) * 100
            doi = (oi1 / oi0 - 1) * 100
            st["dp"], st["doi"] = round(dp, 4), round(doi, 4)
            if abs(dp) < 0.05 or abs(doi) < 0.50:
                st["buildup"] = "NEUTRAL"
            elif dp > 0 and doi > 0:
                st["buildup"] = "LONG_BUILDUP"
            elif dp > 0 and doi < 0:
                st["buildup"] = "SHORT_COVERING"
            elif dp < 0 and doi > 0:
                st["buildup"] = "SHORT_BUILDUP"
            else:
                st["buildup"] = "LONG_UNWINDING"
        # relative volume (same contract on prev days)
        def cumvol(d):
            fd = FUT.get(exp, {}).get(d, {})
            if "09:15" not in fd or last not in fd:
                return None
            tot, ok = 0.0, True
            for t in times:
                if t not in fd:
                    return None
                tot += fd[t][1]
            return tot
        cv = cumvol(day)
        if cv is not None:
            pv = PREV.get(day)
            if pv:
                cpv = cumvol(pv)
                if cpv:
                    st["relvol"] = round(cv / cpv, 4)
            p5 = PREV5.get(day, [])
            if len(p5) == 5:
                vals = [cumvol(d) for d in p5]
                if all(v is not None for v in vals) and sum(vals) > 0:
                    st["relvol5"] = round(cv / (sum(vals) / 5.0), 4)
    # speculation
    sp = SPOT.get(day, {})
    if last in sp:
        atm = round(sp[last] / 50.0) * 50
        doi_s, oi0_s, ok = {}, {}, True
        for typ in ("CE", "PE"):
            doi_s[typ], oi0_s[typ] = 0.0, 0.0
            for k in range(-5, 6):
                oi = opt_oi(exp, atm + 50 * k, typ, day)
                if oi is None or "09:15" not in oi or last not in oi:
                    ok = False
                    break
                doi_s[typ] += oi[last] - oi["09:15"]
                oi0_s[typ] += oi["09:15"]
            if not ok:
                break
        if ok and (oi0_s["CE"] + oi0_s["PE"]) > 0:
            idx = (doi_s["CE"] - doi_s["PE"]) / (oi0_s["CE"] + oi0_s["PE"]) * 100
            st["spec_idx"] = round(idx, 4)
            st["crowd"] = "LONG" if idx >= 0.25 else ("SHORT" if idx <= -0.25 else "FLAT")
    return st

BULL = {"LONG_BUILDUP", "SHORT_COVERING"}
BEAR = {"SHORT_BUILDUP", "LONG_UNWINDING"}

def buildup_dir(b):
    if b in BULL:
        return "BULL"
    if b in BEAR:
        return "BEAR"
    if b == "NEUTRAL":
        return "NONE"
    return None

# ---------------- legs ----------------
legs = []
for r in csv.DictReader(open(TR / "november_books_fix_repair_nifty_legs.csv")):
    legs.append(dict(date=r["date"], side=r["side"], family=r["family"],
                     rep=r["rep"], entry_time=r["entry_time"],
                     premium=float(r["entry_premium"]),
                     gap=float(r["gap_pct"]), net=float(r["net_inr"]),
                     stood_down=r["stood_down"]))
assert len(legs) == 74

def metrics(kept):
    tot = round(sum(l["net"] for l in kept), 2)
    wins = sum(1 for l in kept if l["net"] > 0)
    tdays = len(set(l["date"] for l in kept))
    daynet = defaultdict(float)
    for l in kept:
        daynet[l["date"]] += l["net"]
    g = sum(1 for d in CAL205 if daynet.get(d, 0) > 0 and d in daynet)
    rd = sum(1 for d in CAL205 if d in daynet and daynet[d] < 0)
    nt = len(CAL205) - len(daynet)
    months = {}
    for m in range(1, 11):
        months[f"2026-{m:02d}"] = round(sum(
            l["net"] for l in kept if l["date"][5:7] == f"{m:02d}"), 2)
    h1 = round(sum(l["net"] for l in kept if l["date"][5:7] <= "05"), 2)
    h2 = round(sum(l["net"] for l in kept if l["date"][5:7] >= "06"), 2)
    top3 = sum(sorted((l["net"] for l in kept), reverse=True)[:3])
    return dict(legs=len(kept), total=tot,
                wr=round(100.0 * wins / len(kept), 1) if kept else 0.0,
                wins=wins, trade_days=tdays,
                rs_per_td=round(tot / tdays, 2) if tdays else 0.0,
                green=g, red=rd, no_trade=nt, months=months,
                h1=h1, h2=h2, ex_top3=round(tot - top3, 2),
                red_months=[m for m, v in months.items() if v < 0])

# ---- Step 0 control ----
ctrl = metrics(legs)
nfix = [l for l in legs if l["stood_down"]]
assert ctrl["total"] == 103050.25, ctrl
assert ctrl["legs"] == 74 and ctrl["wr"] == 51.4 and ctrl["trade_days"] == 66
assert ctrl["rs_per_td"] == 1561.37, ctrl
assert ctrl["months"]["2026-03"] == -1216.50, ctrl["months"]
assert ctrl["red_months"] == ["2026-03"], ctrl["red_months"]
assert len(nfix) == 8 and round(sum(l["net"] for l in nfix), 2) == -14119.75
import statistics
assert abs(statistics.median([l["premium"] for l in legs]) - 213.025) < 1e-9
print("CONTROL OK:", {k: ctrl[k] for k in ("legs", "total", "wr", "trade_days", "rs_per_td")})

# ---------------- states for all leg days + Nov 3 ----------------
leg_days = sorted(set(l["date"] for l in legs))
STATES = {}
for d in leg_days + ["2026-11-03"]:
    for read in READS:
        STATES[(d, read)] = morning_state(d, read)

cov = {}
for read in READS:
    cov[read] = dict(
        buildup_nc=sum(1 for d in leg_days if STATES[(d, read)]["buildup"] is None),
        relvol_nc=sum(1 for d in leg_days if STATES[(d, read)]["relvol"] is None),
        relvol5_nc=sum(1 for d in leg_days if STATES[(d, read)]["relvol5"] is None),
        crowd_nc=sum(1 for d in leg_days if STATES[(d, read)]["crowd"] is None),
        leg_days=len(leg_days))
print("COVERAGE (leg-days NC):", json.dumps(cov))

# ---------------- rules ----------------
def aligned(leg, st):
    d = buildup_dir(st["buildup"])
    if d is None:
        return None     # NC
    return (leg["side"] == "CE" and d == "BULL") or \
           (leg["side"] == "PE" and d == "BEAR")

def spec_agree(leg, st):
    if st["crowd"] is None:
        return None
    return (leg["side"] == "CE" and st["crowd"] == "LONG") or \
           (leg["side"] == "PE" and st["crowd"] == "SHORT")

def fb_inverted(leg, st):
    """Keep B leg unless buildup agrees with the leg's own side."""
    d = buildup_dir(st["buildup"])
    if d is None:
        return None
    agrees = (leg["side"] == "CE" and d == "BULL") or \
             (leg["side"] == "PE" and d == "BEAR")
    return not agrees

def rule_eval(rule, leg, st):
    """True = keep, False = drop, None = NC for this rule."""
    if rule == "ALIGN":
        return aligned(leg, st)
    if rule == "ALIGN+SPEC":
        a, b = aligned(leg, st), spec_agree(leg, st)
        if a is None or b is None:
            return None
        return a and b
    if rule.startswith("VOL-"):
        thr = float(rule.split("-")[1])
        return None if st["relvol"] is None else st["relvol"] >= thr
    if rule == "VOL5-1.1":
        return None if st["relvol5"] is None else st["relvol5"] >= 1.1
    if rule == "PF-ALIGN":
        return True if leg["family"] == "B" else aligned(leg, st)
    if rule == "PF-ALIGN+SPEC":
        if leg["family"] == "B":
            return True
        a, b = aligned(leg, st), spec_agree(leg, st)
        if a is None or b is None:
            return None
        return a and b
    if rule == "FB-ONLY":
        return fb_inverted(leg, st) if leg["family"] == "B" else True
    if rule == "FB-COMBO":
        return fb_inverted(leg, st) if leg["family"] == "B" else aligned(leg, st)
    raise ValueError(rule)

# ---------------- grid + placebos ----------------
rng = random.Random(20261114)
results = {"control": ctrl, "coverage_leg_days": cov, "grid": []}
for read in ("10:00", "11:00"):
    for rule in GRID:
        structural, pop, kept_pop, dropped_pop = [], [], [], []
        nc_kept = 0
        for leg in legs:
            if leg["entry_time"] < read:
                structural.append(leg)
                continue
            v = rule_eval(rule, leg, STATES[(leg["date"], read)])
            if v is None:
                structural.append(leg)
                nc_kept += 1
            else:
                pop.append(leg)
                (kept_pop if v else dropped_pop).append(leg)
        kept = structural + kept_pop
        m = metrics(kept)
        k = len(kept_pop)
        pop_nets = [l["net"] for l in pop]
        struct_tot = sum(l["net"] for l in structural)
        draws = []
        for _ in range(200):
            draws.append(struct_tot + sum(rng.sample(pop_nets, k)) if k else struct_tot)
        pct = sum(1 for x in draws if x < m["total"]) / 200.0
        kept_mean = (sum(l["net"] for l in kept_pop) / k) if k else None
        drop_mean = (sum(l["net"] for l in dropped_pop) / len(dropped_pop)) \
            if dropped_pop else None
        drop_tot = round(sum(l["net"] for l in dropped_pop), 2)
        drop_ctrl = (kept_mean is not None and drop_mean is not None
                     and kept_mean > drop_mean)
        fails = []
        if m["wr"] < 60:
            fails.append(f"WR {m['wr']} < 60")
        if m["rs_per_td"] < 900:
            fails.append(f"Rs/TD {m['rs_per_td']} < 900")
        if m["total"] < TOTAL_BAR:
            fails.append(f"total {m['total']} < {TOTAL_BAR}")
        if not (m["h1"] > 0 and m["h2"] > 0):
            fails.append(f"halves {m['h1']}/{m['h2']}")
        if m["ex_top3"] <= 0:
            fails.append(f"ex-top-3 {m['ex_top3']}")
        if pct < 0.95:
            fails.append(f"placebo {pct} < 0.95")
        if not drop_ctrl:
            fails.append("dropped-set control")
        new_red = [x for x in m["red_months"] if x != "2026-03"]
        if new_red:
            fails.append(f"new red months {new_red}")
        results["grid"].append(dict(
            read=read, rule=rule, kept=m, conditioned_pop=len(pop),
            kept_conditioned=k, dropped=len(dropped_pop),
            dropped_total=drop_tot, kept_cond_mean=
            round(kept_mean, 2) if kept_mean is not None else None,
            dropped_cond_mean=round(drop_mean, 2) if drop_mean is not None else None,
            nc_kept=nc_kept, placebo_pct=round(pct, 3),
            dropped_control_pass=bool(drop_ctrl),
            verdict="PASS" if not fails else "FAIL", fails=fails))
        print(f"{read} {rule:14s} kept {m['legs']:3d} tot {m['total']:>11.2f} "
              f"WR {m['wr']:5.1f} RsTD {m['rs_per_td']:>8.2f} pct {pct:.3f} "
              f"dropTot {drop_tot:>10.2f} {'PASS' if not fails else 'FAIL ' + '; '.join(fails)}")

# ---------------- diagnostics at R10 ----------------
diag = {}
pop10 = [l for l in legs if l["entry_time"] >= "10:00"]
def bucket(rows):
    return dict(n=len(rows), total=round(sum(l["net"] for l in rows), 2),
                mean=round(sum(l["net"] for l in rows) / len(rows), 2) if rows else None)
by_class = {}
for cls in ("LONG_BUILDUP", "SHORT_COVERING", "SHORT_BUILDUP",
            "LONG_UNWINDING", "NEUTRAL"):
    sel = [l for l in pop10 if STATES[(l["date"], "10:00")]["buildup"] == cls]
    by_class[cls] = bucket(sel)
    by_class[cls + "|B"] = bucket([l for l in sel if l["family"] == "B"])
    by_class[cls + "|AC"] = bucket([l for l in sel if l["family"] != "B"])
diag["by_buildup_R10"] = by_class
b_legs = [l for l in pop10 if l["family"] == "B" and STATES[(l["date"], "10:00")]["buildup"]]
def bagrees(l):
    d = buildup_dir(STATES[(l["date"], "10:00")]["buildup"])
    if d == "NONE":
        return "neutral"
    ag = (l["side"] == "CE" and d == "BULL") or (l["side"] == "PE" and d == "BEAR")
    return "agrees" if ag else "opposes"
diag["familyB_R10"] = {k: bucket([l for l in b_legs if bagrees(l) == k])
                       for k in ("agrees", "opposes", "neutral")}
diag["by_crowd_R10"] = {c: bucket([l for l in pop10
                                   if STATES[(l["date"], "10:00")]["crowd"] == c])
                        for c in ("LONG", "SHORT", "FLAT")}
rv = sorted(((STATES[(l["date"], "10:00")]["relvol"], i, l)
             for i, l in enumerate(pop10)
             if STATES[(l["date"], "10:00")]["relvol"] is not None),
            key=lambda x: (x[0], x[1]))
rv = [(v, l) for v, _, l in rv]
if rv:
    n = len(rv)
    diag["relvol_terciles_R10"] = {
        "low": bucket([l for _, l in rv[:n // 3]]),
        "mid": bucket([l for _, l in rv[n // 3:2 * n // 3]]),
        "high": bucket([l for _, l in rv[2 * n // 3:]]),
        "range": [rv[0][0], rv[-1][0]]}
results["diagnostics"] = diag

# ---------------- November ----------------
nov = {}
for read in READS:
    st = STATES[("2026-11-03", read)]
    nov[read] = {k: st[k] for k in ("buildup", "relvol", "relvol5", "crowd",
                                    "spec_idx", "dp", "doi", "exp")}
    fake = dict(date="2026-11-03", side="CE", family="C")
    nov[read]["would_say"] = {rule: rule_eval(rule, fake, st) for rule in GRID}
results["november_nov3"] = nov
print("NOV3:", json.dumps(nov, indent=1))

OUTJ.write_text(json.dumps(results, indent=1))
print("WROTE", OUTJ)
