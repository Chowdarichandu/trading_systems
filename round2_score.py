#!/usr/bin/env python3
"""ROUND 2 SCORER (2026-11-13 night) — futures-basis + India-VIX families.

Specs FROZEN in new_data_round2_2026-11-13.md Part 2 BEFORE this scorer
ran. Machinery: round 1's frozen scorer (oi_buildup_score.py, imported
unmodified) — same SPOT/CAL/NEXT maps, same G0 replay, same premium
stores plus the documented full-day repair from oi_buildup_run_bank.py
(a stored series starting after 09:20 is a truncated fetch window and
is treated as missing). Gate identical to round 1. Merge protocol
identical to round 1 (increment on TUNED STACK v2 idle days).
Paper only, real money Rs0. On HTTP 429: hard stop, partial results
saved and flagged.
"""
import csv, json, random, sys
import importlib.util
from pathlib import Path

TR = Path.home() / "workspace/trading"
spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)

# ---- full-day premium repair (verbatim from round 1's bank driver)
_orig_prem_bars = obs.prem_bars


def prem_bars_full(idx, exp, strike, typ, day):
    bars, src = _orig_prem_bars(idx, exp, strike, typ, day)
    if bars and bars[0][0] <= "09:20":
        return bars, src
    fn = obs.FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if cd:
            fb = sorted((c[0][11:16], float(c[1]), float(c[2]),
                         float(c[3]), float(c[4])) for c in cd)
            if fb[0][0] <= "09:20":
                return fb, "fetched_cache"
    fb = obs.fetch_bars(idx, exp, strike, typ, day)
    if fb:
        return fb, "fetched_full"
    return bars, src


obs.prem_bars = prem_bars_full

# ---------------- round-2 signal data ----------------
R2 = TR / "round2_history"
basis_rows = list(csv.DictReader(open(R2 / "banknifty_basis_daily.csv")))
BASIS = {r["date"]: r for r in basis_rows}
MYDAYS = [r["date"] for r in basis_rows]
MYPREV = {MYDAYS[i]: MYDAYS[i - 1] for i in range(1, len(MYDAYS))}
MYPREV2 = {MYDAYS[i]: MYDAYS[i - 2] for i in range(2, len(MYDAYS))}
VIX = {}
for r in csv.DictReader(open(R2 / "india_vix_daily.csv")):
    VIX[r["date"]] = float(r["vix_close"]) if r["vix_close"] else None


def bpct(d):
    v = BASIS[d]["basis_pct"]
    return float(v) if v not in (None, "") else None


def days_to_expiry(d):
    """Trading days in (d, expiry_d] on the Part-1 calendar."""
    exp = BASIS[d]["expiry"]
    n = 0
    for x in MYDAYS:
        if d < x <= exp:
            n += 1
    return n


def roll_blocked(d):
    return days_to_expiry(d) <= 2


def sig_a1(d):
    """Basis-expansion continuation, from day d's closes only."""
    if d not in MYPREV or roll_blocked(d):
        return None
    p = MYPREV[d]
    if BASIS[p]["expiry"] != BASIS[d]["expiry"]:
        return None
    a, b = bpct(d), bpct(p)
    if a is None or b is None:
        return None
    db = a - b
    if db >= 0.05:
        return "CE"
    if db <= -0.05:
        return "PE"
    return None


def sig_a2(d):
    """Basis-extreme reversal: z vs same contract's prior in-force days."""
    if roll_blocked(d):
        return None
    exp = BASIS[d]["expiry"]
    win = []
    x = d
    while x in MYPREV and len(win) < 15:
        x = MYPREV[x]
        if BASIS[x]["expiry"] != exp:
            break
        v = bpct(x)
        if v is not None:
            win.append(v)
    if len(win) < 8:
        return None
    cur = bpct(d)
    if cur is None:
        return None
    mean = sum(win) / len(win)
    var = sum((v - mean) ** 2 for v in win) / len(win)
    sd = var ** 0.5
    if sd == 0:
        return None
    z = (cur - mean) / sd
    if z >= 1.5:
        return "PE"
    if z <= -1.5:
        return "CE"
    return None


def sig_b1(d):
    """VIX-spike reversal: fear expansion >= +8%, fade day d's spot move."""
    if d not in MYPREV:
        return None
    p = MYPREV[d]
    a, b = VIX.get(d), VIX.get(p)
    if a is None or b is None or b == 0:
        return None
    if (a - b) / b < 0.08:
        return None
    s = float(BASIS[d]["spot_chg_pts"])
    if s < 0:
        return "CE"
    if s > 0:
        return "PE"
    return None


SIG = {"A1": sig_a1, "A2": sig_a2, "B1": sig_b1}
oi = obs.load_oi("BANKNIFTY")


def run_book_r2(family, mode):
    cfg = obs.CONF["BANKNIFTY"]
    rng = random.Random(42)
    trades, nc = [], []
    sig_days = [d for d in MYDAYS
                if "2026-01-01" <= d <= "2026-11-11" and d in obs.NEXT]
    for d in sig_days:
        if mode == "shifted":
            pd = MYPREV.get(d)
            dirn = SIG[family](pd) if pd else None
            src_day = pd
        else:
            dirn = SIG[family](d)
            src_day = d
        if dirn is None:
            continue
        if mode == "reversed":
            dirn = "PE" if dirn == "CE" else "CE"
        elif mode == "coin":
            dirn = "CE" if rng.random() < 0.5 else "PE"
        tday = obs.NEXT[d]
        exp = oi[tday]["expiry"] if tday in oi else None
        sbar = obs.SPOT["BANKNIFTY"].get(tday, {}).get("09:20")
        if exp is None or sbar is None:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="no_spot_or_expiry"))
            continue
        strike = int(round(sbar[0] / cfg["step"])) * cfg["step"]
        bars, src = obs.prem_bars("BANKNIFTY", exp, strike, dirn, tday)
        if not bars:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="no_premium_candles"))
            continue
        r = obs.replay_g0(bars, cfg["lot"])
        if r is None:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="replay_none"))
            continue
        trades.append(dict(index="BANKNIFTY", variant=family, mode=mode,
                           signal_date=d, src_signal_date=src_day,
                           trade_date=tday, direction=dirn, strike=strike,
                           expiry=exp, store=src, **r))
    return trades, nc


def gate_legs(s, e, nc):
    return dict(
        total_pos=s["total"] > 0,
        halves_pos=s["h1"] > 0 and s["h2"] > 0,
        ex_top3_pos=s["ex_top3"] > 0,
        beats_reversed=s["total"] > e["reversed"]["total"],
        beats_coin=s["total"] > e["coin"]["total"],
        beats_shifted=s["total"] > e["shifted"]["total"],
        timing_clean=e["timing_violations"] == 0,
        nc_ok=len(nc) <= max(1, int(0.05 * (s["n"] + len(nc)))))


results = {"scope": "BANKNIFTY only — Round 2 (futures basis + India VIX)"}
all_trades = []
try:
    for family in ("A1", "A2", "B1"):
        entry = {}
        real, nc = run_book_r2(family, "real")
        entry["real"] = obs.stats(real)
        entry["nc"] = nc
        entry["timing_violations"] = sum(
            1 for t in real if not t["signal_date"] < t["trade_date"])
        for mode in ("reversed", "coin", "shifted"):
            pl, _ = run_book_r2(family, mode)
            entry[mode] = obs.stats(pl)
            all_trades += pl
        all_trades += real
        entry["gate_legs"] = gate_legs(entry["real"], entry, nc)
        entry["gate_pass"] = all(entry["gate_legs"].values())
        results[family] = entry
        s = entry["real"]
        print(f"{family}: n={s['n']} total={s['total']} "
              f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
              f"pace={s['pace_per_month']} NC={len(nc)} "
              f"PASS={entry['gate_pass']} legs={entry['gate_legs']}",
              flush=True)
        print(f"   placebos: rev={entry['reversed']['total']} "
              f"coin={entry['coin']['total']} "
              f"shift={entry['shifted']['total']} | NOV n={s['nov_n']} "
              f"total={s['nov_total']}", flush=True)
except obs.RateLimited:
    print("RATE_LIMIT_STOP during scoring — partial results", flush=True)
    results["rate_limited"] = True

# ---------------- B2 — VIX permission overlay on the stack ----------------
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack = [{"date": r["date"], "net": float(r["x1_net"])} for r in stack_rows]
stack_days = {l["date"] for l in stack}
stack_total = round(sum(l["net"] for l in stack), 2)
stack_td = len(stack_days)
assert len(stack) == 111 and stack_total == 127351.50, \
    f"stack ledger anchor failed: {len(stack)} legs, {stack_total}"


def vix_lag(d, lag):
    x = d
    for _ in range(lag):
        x = MYPREV.get(x)
        if x is None:
            return None, None
    return VIX.get(x), x


def b2_book(rule):
    """rule: 'real' | 'reversed' | 'shifted' -> kept legs."""
    kept = []
    for leg in stack:
        if rule == "real":
            v, _ = vix_lag(leg["date"], 1)
            keep = v is None or v <= 20.0
        elif rule == "reversed":
            v, _ = vix_lag(leg["date"], 1)
            keep = v is not None and v > 20.0
        else:  # shifted: rule read off VIX_{T-2}
            v, _ = vix_lag(leg["date"], 2)
            keep = v is None or v <= 20.0
        if keep:
            kept.append(leg)
    return kept


def book_stats(legs):
    total = round(sum(l["net"] for l in legs), 2)
    tds = {l["date"] for l in legs}
    months = {}
    for l in legs:
        months[l["date"][:7]] = round(months.get(l["date"][:7], 0.0)
                                      + l["net"], 2)
    h1 = round(sum(l["net"] for l in legs if l["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(l["net"] for l in legs if l["date"][:7] >= "2026-06"), 2)
    top3 = sorted((l["net"] for l in legs), reverse=True)[:3]
    return dict(legs=len(legs), total=total, trade_days=len(tds),
                per_trade_day=round(total / len(tds), 2) if tds else None,
                months=months,
                red_months=[m for m, v in months.items() if v < 0],
                h1=h1, h2=h2, ex_top3=round(total - sum(top3), 2))


b2 = {}
kept = b2_book("real")
b2["real"] = book_stats(kept)
b2["kept_legs"] = kept
b2["dropped_legs"] = [l for l in stack if l not in kept]
b2["reversed"] = book_stats(b2_book("reversed"))
b2["shifted"] = book_stats(b2_book("shifted"))
rng = random.Random(42)
coin_legs = rng.sample(stack, len(kept)) if kept else []
b2["coin"] = book_stats(coin_legs)
missing_vix_legs = [l["date"] for l in stack
                    if vix_lag(l["date"], 1)[0] is None]
b2["legs_with_missing_prior_vix"] = missing_vix_legs
k = b2["real"]
b2["gate_legs"] = dict(
    total_beats_stack=k["total"] > stack_total,
    per_trade_day_beats_stack=k["per_trade_day"] > 1430.92,
    halves_pos=k["h1"] > 0 and k["h2"] > 0,
    ex_top3_pos=k["ex_top3"] > 0,
    beats_reversed=k["total"] > b2["reversed"]["total"],
    beats_coin=k["total"] > b2["coin"]["total"],
    beats_shifted=k["total"] > b2["shifted"]["total"])
b2["gate_pass"] = all(b2["gate_legs"].values())
# B2 November: the stack's four logged November legs under the same rule
NOV_STACK = [("2026-11-04", 2480.00), ("2026-11-09", -1720.00),
             ("2026-11-12", -1720.00), ("2026-11-13", -1720.00)]
SUPP = json.loads((R2 / "nov12_supplementary.json").read_text())
nov_b2 = []
for d, net in NOV_STACK:
    if d == "2026-11-13":
        v = SUPP["vix_close"]  # VIX of Nov 12 (supplementary row)
        vdate = "2026-11-12"
    else:
        v, vdate = vix_lag(d, 1)
    keep = v is None or v <= 20.0
    nov_b2.append(dict(date=d, net=net, vix_prior=v, vix_date=vdate,
                       kept=keep))
b2["november"] = dict(
    legs=nov_b2,
    filtered_total=round(sum(x["net"] for x in nov_b2 if x["kept"]), 2),
    unfiltered_total=-2680.00)
results["B2"] = b2
for l in kept:
    all_trades.append(dict(index="BANKNIFTY", variant="B2", mode="real",
                             signal_date=None, src_signal_date=None,
                             trade_date=l["date"], direction="STACK_LEG",
                             strike=None, expiry=None, store="stack_ledger",
                             entry=None, exit=None, exit_time=None,
                             exit_reason="stack_leg_kept", ft=None,
                             net=l["net"]))
print(f"B2: kept {k['legs']}/111 legs total={k['total']} "
      f"TD={k['trade_days']} /TD={k['per_trade_day']} "
      f"H=({k['h1']},{k['h2']}) ex3={k['ex_top3']} "
      f"PASS={b2['gate_pass']} legs={b2['gate_legs']}", flush=True)
print(f"   placebos: rev={b2['reversed']['total']} "
      f"coin={b2['coin']['total']} shift={b2['shifted']['total']} | "
      f"dropped {len(b2['dropped_legs'])} legs; missing-prior-VIX legs: "
      f"{missing_vix_legs}; Nov filtered total "
      f"{b2['november']['filtered_total']}", flush=True)

# ---------------- supplementary Nov-13 legs (Nov 12 signals) -------------
supp_out = {"signal_date": "2026-11-12",
            "basis_pct": SUPP["basis_pct"], "vix_close": SUPP["vix_close"]}
try:
    prev11 = "2026-11-11"
    # A1: same contract (2026-11-23) both days; spot chg Nov 12 needed
    # only by B1: spot_chg = supp close - Nov 11 close.
    chg12 = round(SUPP["spot_close"] - float(BASIS[prev11]["spot_close"]), 2)
    db = round(SUPP["basis_pct"] - bpct(prev11), 4)
    supp_out["A1_dbasis_pct"] = db
    supp_out["A1"] = "CE" if db >= 0.05 else ("PE" if db <= -0.05 else None)
    # A2: z of Nov 12 vs Nov-23 contract's prior in-force days
    win = []
    x = prev11
    while BASIS[x]["expiry"] == "2026-11-23" and len(win) < 15:
        win.append(bpct(x))
        if x not in MYPREV:
            break
        x = MYPREV[x]
    mean = sum(win) / len(win)
    sd = (sum((v - mean) ** 2 for v in win) / len(win)) ** 0.5
    z = (SUPP["basis_pct"] - mean) / sd if sd else None
    supp_out["A2_z"] = round(z, 3) if z is not None else None
    supp_out["A2"] = ("PE" if z is not None and z >= 1.5 else
                      "CE" if z is not None and z <= -1.5 else None)
    dv = (SUPP["vix_close"] - VIX[prev11]) / VIX[prev11]
    supp_out["B1_dvix_pct"] = round(dv * 100, 2)
    supp_out["spot_chg_pts_nov12"] = chg12
    supp_out["B1"] = (("CE" if chg12 < 0 else "PE")
                      if dv >= 0.08 and chg12 != 0 else None)
    # score any fired leg (Nov 13 is stack-busy: reported, never merged)
    arch_spot = None
    fn = TR / "option_chain_archive/banknifty_2026-11-13.csv"
    if fn.exists():
        with open(fn) as f:
            for r in csv.DictReader(f):
                if r["bucket_ist"].startswith("2026-11-13T09:15"):
                    arch_spot = float(r["spot"])
                    break
    supp_out["spot_open_proxy"] = arch_spot
    for fam in ("A1", "A2", "B1"):
        dirn = supp_out[fam]
        if dirn is None:
            supp_out[fam + "_trade"] = "no signal"
            continue
        if arch_spot is None:
            supp_out[fam + "_trade"] = "NC — no archive spot proxy"
            continue
        strike = int(round(arch_spot / 100.0)) * 100
        bars, src = obs.prem_bars("BANKNIFTY", "2026-11-23", strike, dirn,
                                  "2026-11-13")
        if not bars:
            supp_out[fam + "_trade"] = "NC — no premium candles"
            continue
        r = obs.replay_g0(bars, 30)
        supp_out[fam + "_trade"] = dict(
            strike=strike, entry=r["entry"], exit=r["exit"],
            exit_time=r["exit_time"], exit_reason=r["exit_reason"],
            net=r["net"], store=src) if r else "NC — replay none"
except obs.RateLimited:
    supp_out["error"] = "RATE_LIMIT_STOP"
    results["rate_limited"] = True
results["nov13_supplementary"] = supp_out
print(f"Nov13 supplementary: {supp_out}", flush=True)

# ---------------- MERGE (registered protocol) ---------------------------
merge = {"stack_anchor": dict(legs=len(stack), total=stack_total,
                              trade_days=stack_td, per_trade_day=1430.92)}
nov_stack_days = set()
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack_days.add(r["date"])
NOV_STACK_TOTAL = -2680.00
real_by_family = {}
for t in all_trades:
    if t["mode"] == "real" and t["variant"] in ("A1", "A2", "B1"):
        real_by_family.setdefault(t["variant"], []).append(t)
candidates = []
for fam in ("A1", "A2", "B1"):
    if fam in results and isinstance(results[fam], dict) \
            and "real" in results[fam]:
        candidates.append((fam, results[fam]["real"]["total"],
                           results[fam]["gate_pass"]))
merge_family = None
passers = [c for c in candidates if c[2]]
if passers:
    merge_family = passers[0][0]
    merge["basis_of_selection"] = f"{merge_family} passed its gate"
elif candidates:
    merge_family = max(candidates, key=lambda c: c[1])[0]
    merge["basis_of_selection"] = (
        f"no standalone pass; strongest failing family by Jan-Oct total "
        f"= {merge_family} (merge-only evidence)")
if merge_family:
    trades = real_by_family.get(merge_family, [])
    gate_trades = [t for t in trades if t["trade_date"] <= "2026-10-31"]
    incr = [t for t in gate_trades if t["trade_date"] not in stack_days]
    incr_total = round(sum(t["net"] for t in incr), 2)
    merged_total = round(stack_total + incr_total, 2)
    merged_days = stack_days | {t["trade_date"] for t in incr}
    months = {}
    all_legs = [(l["date"], l["net"]) for l in stack] + \
               [(t["trade_date"], t["net"]) for t in incr]
    for d, n in all_legs:
        months[d[:7]] = round(months.get(d[:7], 0.0) + n, 2)
    nov_legs = [t for t in trades
                if "2026-11-02" <= t["trade_date"] <= "2026-11-12"]
    nov_incr = [t for t in nov_legs
                if t["trade_date"] not in nov_stack_days]
    nov_merged = round(NOV_STACK_TOTAL +
                       sum(t["net"] for t in nov_incr), 2)
    merge[merge_family] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_days),
        merged_per_trade_day=round(merged_total / len(merged_days), 2),
        merged_months=months,
        merged_red_months=[m for m, v in months.items() if v < 0],
        merge_pass=bool(incr_total > 0 and merged_total > stack_total),
        november_family_legs=[{k: t[k] for k in
                               ("signal_date", "trade_date", "direction",
                                "strike", "entry", "exit", "exit_reason",
                                "net")} for t in nov_legs],
        november_increment_legs=[{k: t[k] for k in
                                  ("signal_date", "trade_date", "direction",
                                   "strike", "entry", "exit", "exit_reason",
                                   "net")} for t in nov_incr],
        november_merged_total=nov_merged)
    print(f"MERGE {merge_family}: incr {len(incr)} legs {incr_total} | "
          f"merged {merged_total} on {len(merged_days)} TD = "
          f"{merge[merge_family]['merged_per_trade_day']}/TD | Nov merged "
          f"{nov_merged} (family Nov legs {len(nov_legs)}, incr "
          f"{len(nov_incr)})", flush=True)
results["merge"] = merge

# ---------------- write trades + independent re-sum ---------------------
with open(TR / "round2_trades.csv", "w", newline="") as f:
    if all_trades:
        keys = list(all_trades[0].keys())
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round2_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            k = r["variant"]
            chk[k] = round(chk.get(k, 0.0) + float(r["net"]), 2)
resum_ok = True
for fam in ("A1", "A2", "B1"):
    if fam in results and isinstance(results[fam], dict) \
            and "real" in results[fam]:
        mine = results[fam]["real"]["total"]
        if chk.get(fam) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH {fam}: file {chk.get(fam)} vs {mine}",
                  flush=True)
if chk.get("B2") != b2["real"]["total"]:
    resum_ok = False
    print(f"RESUM MISMATCH B2: file {chk.get('B2')} vs {b2['real']['total']}",
          flush=True)
results["resum_check"] = ("EXACT for all scored books" if resum_ok
                          else "MISMATCH — see log")
(TR / "new_data_round2_results.json").write_text(json.dumps(results,
                                                           indent=1))
print("re-sum:", results["resum_check"],
      "| results -> new_data_round2_results.json", flush=True)
