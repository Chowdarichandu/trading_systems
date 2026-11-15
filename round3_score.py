#!/usr/bin/env python3
"""ROUND 3 SCORER (2026-11-13 night) — FII/DII participant-flow families.

Specs FROZEN in new_data_round3_2026-11-13.md Part 2 BEFORE this scorer
ran. Machinery: round 1's frozen scorer (oi_buildup_score.py, imported
unmodified) — same SPOT maps, same G0 replay, same premium stores plus
the documented full-day repair from oi_buildup_run_bank.py (a stored
series starting after 09:20 is a truncated fetch window and is treated
as missing). Calendar: the participant dataset's own session calendar
(299 sessions, 2025-09-01..2026-11-13; set-identical to the spot
calendar on the Jan-Oct gate window; chains through the Nov 8 short
session exactly as rounds 1-2 did). Gate identical to rounds 1-2.
Merge protocol identical (increment on TUNED STACK v2 idle days).
Paper only, real money Rs0. On HTTP 429: hard stop, partial results
saved and flagged.
"""
import csv, json, random
import importlib.util
from pathlib import Path
from urllib.parse import quote

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

# ---------------- round-3 participant data ----------------
R3 = TR / "round3_history"
prows = list(csv.DictReader(open(R3 / "participant_daily.csv")))
PDAYS = [r["date"] for r in prows]
PPREV = {PDAYS[i]: PDAYS[i - 1] for i in range(1, len(PDAYS))}
PNEXT = {PDAYS[i]: PDAYS[i + 1] for i in range(len(PDAYS) - 1)}
PPREV3 = {PDAYS[i]: PDAYS[i - 3] for i in range(3, len(PDAYS))}
LR = {r["date"]: float(r["fii_lr"]) for r in prows}
NET = {r["date"]: int(r["fii_fut_net"]) for r in prows}
oi = obs.load_oi("BANKNIFTY")


def sig_f1(d):
    """FII crowding reversal: LR percentile rank in its trailing 60."""
    win = []
    x = d
    while x in PPREV and len(win) < 60:
        x = PPREV[x]
        win.append(LR[x])
    if len(win) < 40:
        return None
    rho = sum(1 for v in win if v < LR[d]) / len(win)
    if rho <= 0.20:
        return "CE"
    if rho >= 0.80:
        return "PE"
    return None


def sig_f2(d):
    """FII flow momentum: 3-session change in FII net index futures."""
    if d not in PPREV3:
        return None
    dn = NET[d] - NET[PPREV3[d]]
    if dn > 0:
        return "CE"
    if dn < 0:
        return "PE"
    return None


SIG = {"F1": sig_f1, "F2": sig_f2}


def fetch_spot_open(day):
    """09:20 index 5-min bar open via the v3 route (Nov 12 only)."""
    try:
        body = obs.get(f"{obs.API}/v3/historical-candle/"
                       f"{quote(obs.IDXKEY['BANKNIFTY'], safe='')}"
                       f"/minutes/5/{day}/{day}")
    except obs.RateLimited:
        raise
    except Exception:
        return None
    for c in (body.get("data") or {}).get("candles") or []:
        if c[0][:10] == day and c[0][11:16] == "09:20":
            return float(c[1])
    return None


def archive_spot(day):
    """Chain-archive 09:15 bucket spot (Nov 13 supplementary proxy)."""
    fn = TR / f"option_chain_archive/banknifty_{day}.csv"
    if not fn.exists():
        return None
    with open(fn) as f:
        for r in csv.DictReader(f):
            if r["bucket_ist"].startswith(f"{day}T09:15"):
                return float(r["spot"])
    return None


def spot_open_for(tday):
    """(09:20 spot open, source) or (None, reason)."""
    sbar = obs.SPOT["BANKNIFTY"].get(tday, {}).get("09:20")
    if sbar is not None:
        return sbar[0], "spot_store"
    if tday == "2026-11-12":
        v = fetch_spot_open(tday)
        if v is not None:
            return v, "fetched_spot_v3"
        return None, "no_spot_reference"
    return None, "no_spot_reference"


def expiry_for(tday):
    if tday in oi:
        return oi[tday]["expiry"]
    if tday in ("2026-11-12", "2026-11-13"):
        return "2026-11-23"
    return None


def run_book_r3(family, mode):
    cfg = obs.CONF["BANKNIFTY"]
    rng = random.Random(42)
    trades, nc = [], []
    sig_days = [d for d in PDAYS
                if "2026-01-01" <= d <= "2026-11-12" and d in PNEXT]
    for d in sig_days:
        if mode == "shifted":
            pd = PPREV.get(d)
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
        tday = PNEXT[d]
        exp = expiry_for(tday)
        sopen, ssrc = spot_open_for(tday)
        if exp is None or sopen is None:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="no_spot_or_expiry"))
            continue
        strike = int(round(sopen / cfg["step"])) * cfg["step"]
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
                           expiry=exp, store=src, spot_src=ssrc, **r))
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


results = {"scope": "BANKNIFTY — Round 3 (FII/DII participant flows)"}
all_trades = []
try:
    for family in ("F1", "F2"):
        entry = {}
        real, nc = run_book_r3(family, "real")
        entry["real"] = obs.stats(real)
        entry["nc"] = nc
        entry["timing_violations"] = sum(
            1 for t in real if not t["signal_date"] < t["trade_date"])
        for mode in ("reversed", "coin", "shifted"):
            pl, _ = run_book_r3(family, mode)
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

# ------------- supplementary Nov-13 legs (Nov 12 signals) -------------
supp_out = {"signal_date": "2026-11-12"}
try:
    arch_spot = archive_spot("2026-11-13")
    supp_out["spot_open_proxy"] = arch_spot
    for fam in ("F1", "F2"):
        dirn = SIG[fam]("2026-11-12")
        supp_out[fam] = dirn
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
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack = [{"date": r["date"], "net": float(r["x1_net"])} for r in stack_rows]
stack_days = {l["date"] for l in stack}
stack_total = round(sum(l["net"] for l in stack), 2)
assert len(stack) == 111 and stack_total == 127351.50, \
    f"stack ledger anchor failed: {len(stack)} legs, {stack_total}"
merge = {"stack_anchor": dict(legs=len(stack), total=stack_total,
                              trade_days=len(stack_days),
                              per_trade_day=1430.92)}
nov_stack_days = set()
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack_days.add(r["date"])
NOV_STACK_TOTAL = -2680.00
real_by_family = {}
for t in all_trades:
    if t["mode"] == "real" and t["variant"] in ("F1", "F2"):
        real_by_family.setdefault(t["variant"], []).append(t)
candidates = []
for fam in ("F1", "F2"):
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
with open(TR / "round3_trades.csv", "w", newline="") as f:
    if all_trades:
        keys = list(all_trades[0].keys())
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round3_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            k = r["variant"]
            chk[k] = round(chk.get(k, 0.0) + float(r["net"]), 2)
resum_ok = True
for fam in ("F1", "F2"):
    if fam in results and isinstance(results[fam], dict) \
            and "real" in results[fam]:
        mine = results[fam]["real"]["total"]
        if chk.get(fam) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH {fam}: file {chk.get(fam)} vs {mine}",
                  flush=True)
results["resum_check"] = ("EXACT for all scored books" if resum_ok
                          else "MISMATCH — see log")
(TR / "new_data_round3_results.json").write_text(json.dumps(results,
                                                           indent=1))
print("re-sum:", results["resum_check"],
      "| results -> new_data_round3_results.json", flush=True)
