#!/usr/bin/env python3
"""RUN 3 ROUND 10 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Baseline: the Round-6/7/8/9 standing book
(+54,102.00, causal 35 legs, lock60/TGT2-175, sq 15:20). Freeze:
nifty_engine_frozen.md ROUND 10 section (written before any Round-10
candidate scoring).

Workstreams: WS1 Bank-spot early-state agreement conditioning (+ frozen
mirror rule), WS2 OR-width admission (middle / middle+upper), WS3
post-expiry-day population at causal entries, WS4 December freeze
preparation (specification frozen in the ROUND 10 freeze; Cycle 166
transcribes + verifies), WS5 combinations/closure.

Gate: RELATIVE gate is the banking test (net up, FT and frequency not
degraded vs the standing baseline, no baseline-green month flips red, no
red month-ends, halves >= 0, placebo beaten, ex-top-3 >= 0, audit clean,
NC = 0, re-sum exact). OLD ABSOLUTE lines (FT >= 42.0%, frequency
>= 1.00/wk) printed as STATUS ONLY for every verdict.

Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0.
November primary untouched (read-only at most)."""
import sys, csv, json, math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import candles_exact, audit_exact, pool_sets
from nifty_engine_r4_harness import spot5m, DORDER, DIDX
from nifty_engine_score import controls, pool

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
STANDING_GEOM = R7.STANDING_GEOM
MONTHS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05",
          "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]

def run_r10(name, legs, save=True, gate=True, force_no_bank=False):
    """Round-9 run form, Round-10 summary prefix."""
    res, nc, nc_legs = R6.score_r6(legs, geom=STANDING_GEOM)
    pl, _, _ = R6.score_r6(legs, geom=STANDING_GEOM, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    for m in MONTHS:
        c[m] = c["month_table"].get(m, [0, 0])[0]
    c["nc_named_not_computed"] = ("2026-10-28 22500 PE weekly expiry 2026-11-03 — NOT_COMPUTED "
                                  "(registry 0 contracts, Rounds 3-6); not in any Round-10 population")
    if force_no_bank:
        c["decision_support_force_no_bank"] = True
    if gate and R6.CURRENT["total"] is not None:
        banked, rel, abs_lines, g2r = R6.gate_r6(c)
        c["gate_relative"] = {"banked": banked, "checks": rel, "green_to_red": g2r,
                              "vs_label": R6.CURRENT["label"], "vs_total": R6.CURRENT["total"],
                              "vs_ft_pct": R6.CURRENT["ft_pct"], "vs_per_week": R6.CURRENT["per_week"]}
        c["old_absolute_lines_status"] = abs_lines
    if save:
        Path(TR / f"nifty_engine_run3r10_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    g = c.get("gate_relative", {})
    a = c.get("old_absolute_lines_status", {})
    tag = " [DECISION SUPPORT — FORCE NO BANK]" if force_no_bank else ""
    print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
          f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
          f"exT3 {c['ex_top3']:+,.2f} | Mar {c['2026-03']:+,.2f} | Apr {c['2026-04']:+,.2f} | May {c['2026-05']:+,.2f} | "
          f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
          f"REL-GATE {'BANKED' if g.get('banked') else 'FAIL ' + str([k for k, v in g.get('checks', {}).items() if not v])} | "
          f"ABS-LINES FT42 {'PASS' if a.get('FT>=42.0') else 'FAIL'} / FREQ1.00 {'PASS' if a.get('freq>=1.00/wk') else 'FAIL'} (status only){tag}")
    return c, res

def score_sleeve_alone(name, legs):
    return R7.score_sleeve_alone(name, legs)

def missing_candles(legs):
    return R7.missing_candles(legs)

# ---------------- WS1: Bank spot state ----------------
_BANK = None
def bank5m():
    """Bank Nifty 5m bars {date: {time: (open, close)}} from the monthly
    files + the Round-10 patch (3 fetched days, real candles)."""
    global _BANK
    if _BANK is None:
        _BANK = defaultdict(dict)
        for m in range(1, 11):
            p = TR / f"data/banknifty-2026-{m:02d}/spot_5m.csv"
            if not p.exists(): continue
            for r in csv.DictReader(open(p)):
                ts = r["timestamp"]
                _BANK[ts[:10]][ts[11:16]] = (float(r["open"]), float(r["close"]))
        patch = TR / "nifty_engine_r10_bank_spot_patch.csv"
        if patch.exists():
            for r in csv.DictReader(open(patch)):
                ts = r["timestamp"]
                _BANK[ts[:10]][ts[11:16]] = (float(r["open"]), float(r["close"]))
    return _BANK

def bank_move(date, t):
    """Frozen WS1 feature (certification (a)): (close of the last Bank
    bar starting STRICTLY BEFORE t / open of the day's first Bank bar
    - 1) * 100. None if not computable."""
    bars = bank5m().get(date)
    if not bars: return None
    times = sorted(bars)
    prior = [x for x in times if x < t]
    if not prior: return None
    return (bars[prior[-1]][1] / bars[times[0]][0] - 1) * 100

def bank_bucket(leg):
    mv = bank_move(leg["date"], leg["entry_time"])
    if mv is None: return None, None
    if leg["direction"] == "CE":
        b = "agree" if mv >= 0.20 else ("disagree" if mv <= -0.20 else "neutral")
    else:
        b = "agree" if mv <= -0.20 else ("disagree" if mv >= 0.20 else "neutral")
    return b, mv

def ws1_agree_legs(standing):
    """Standing legs in the AGREE bucket (frozen WS1 construction)."""
    out, diag = [], []
    for l in standing:
        b, mv = bank_bucket(l)
        diag.append((l["date"], l["direction"], l["entry_time"], b,
                     None if mv is None else round(mv, 3)))
        if b == "agree": out.append(l)
    return out, diag

# ---------------- WS2: OR-width terciles ----------------
_S5W = None
def _widths():
    global _S5W
    if _S5W is None:
        S5 = spot5m()
        _S5W = {}
        for d, bars in S5.items():
            orr = [b for b in bars if b[0] in ("09:15", "09:20", "09:25")]
            if len(orr) < 3: continue
            hi = max(b[2] for b in orr); lo = min(b[3] for b in orr)
            _S5W[d] = (hi - lo) / orr[0][1] * 100
    return _S5W

def or_tercile(d):
    """Frozen WS2 feature (certification (b)): tercile of D's OR width
    vs the 20 trading days strictly before D. None if not computable."""
    W = _widths()
    i = DIDX.get(d)
    if i is None or i < 20 or d not in W: return None
    prev = sorted(W[DORDER[j]] for j in range(i - 20, i) if DORDER[j] in W)
    if len(prev) < 20: return None
    w = W[d]
    return "lower" if w <= prev[6] else ("upper" if w > prev[13] else "middle")

def ws2_legs(standing, keep):
    out, diag = [], []
    for l in standing:
        t = or_tercile(l["date"])
        diag.append((l["date"], l["direction"], l["entry_time"], t))
        if t in keep: out.append(l)
    return out, diag

# ---------------- WS3: post-expiry-day population ----------------
def post_expiry_sessions():
    exps = json.loads((TR / "nifty_engine_run3_expiries.json").read_text())
    out = set()
    for e in exps:
        i = DIDX.get(e)
        if i is not None and i + 1 < len(DORDER):
            nd = DORDER[i + 1]
            if "2026-01-01" <= nd <= "2026-10-31": out.add(nd)
    return out

def ws3_legs(exclude_keys):
    """Pool keys on post-expiry sessions not in the standing book, at
    CAUSAL entries (certification (c)): confirmed keys at t2 (2nd-
    earliest sysmap time, no 09:55 window), solo keys at their system's
    own sysmap time; strike re-struck ATM100 at the entry bar when the
    entry time differs from the recorded one. Returns (legs, excluded)."""
    S = R6.sysmap()
    days = post_expiry_sessions()
    legs, excluded = [], []
    for l in pool():
        if l["date"] not in days: continue
        if (l["date"], l["direction"]) in exclude_keys: continue
        if l["date"] == l["expiry"]:
            excluded.append((l["date"], l["direction"], "EXP0")); continue
        srcs = R6.sources_of(l)
        times = {s: S.get((l["date"], l["direction"]), {}).get(s) for s in srcs}
        if any(t is None for t in times.values()):
            excluded.append((l["date"], l["direction"], "sysmap-time-missing", str(times))); continue
        if len(srcs) >= 2:
            et = sorted(times.values())[1]
        else:
            et = times[srcs[0]]
        nl = dict(l); nl["entry_time"] = et
        if et != l["entry_time"]:
            so = R6.spot_open(l["date"], et)
            if so is None:
                excluded.append((l["date"], l["direction"], "no-spot-bar")); continue
            nl["strike"] = R6.atm100(so)
        nl["rep"] = "R10-POSTEXP"
        nl["family"] = "R10WS3"
        legs.append(nl)
    return legs, excluded
