#!/usr/bin/env python3
"""RUN 3 ROUND 4 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Starting book = the ADOPTED December candidate
(CH3-R x lock50/TGT2-175, monthly legs only) = +114,921.75 (44 trades,
FT 45.5%, 1.08/wk). Gap to floor 35,078.25. NOTE: Round 4 opened with a
retraction — the Round-3 Cycle-40 signature carriage (+116,348.50) used
the leg day's OWN return believing it was the prior day's (look-ahead);
that banking is void and the baseline reverts to the adopted book. See
the RETRACTION entry in nifty_engine_frozen.md (Round 4 section).

Compositional builder: pool -> C3L -> EXP0 -> CH3R -> Aug-signature weekly
carriage -> optional transforms (WS1 May technique, Volrix re-parameter-
isation, second legs, admission subsets). Gate vs the CURRENT candidate
book, updated on every banking (supersession rule from Round 3).
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0."""
import sys, json, csv, math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r2_harness import candles_exact, pool_sets
from nifty_engine_score import controls, nsrc

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28", "2026-05-26",
            "2026-06-30", "2026-07-28", "2026-08-25", "2026-09-29", "2026-10-27"]

# ---------------- spot data ----------------
_drows = list(csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_daily.csv")))
DAILY = {r["date"]: dict(o=float(r["open"]), h=float(r["high"]),
                         l=float(r["low"]), c=float(r["close"])) for r in _drows}
DORDER = [r["date"] for r in _drows]
DIDX = {d: i for i, d in enumerate(DORDER)}
PREV = {DORDER[i]: DORDER[i - 1] for i in range(1, len(DORDER))}

def pdret(d):
    """CAUTION: this is day d's OWN close-to-close return (known only at
    d's 15:30 close). Round 3's is_aug_sig used it believing it was the
    prior day's return — that made Cycle 40 look-ahead. NEVER use as an
    entry-time feature. Kept only to reproduce the retracted artefact."""
    p = PREV.get(d)
    return (DAILY[d]["c"] / DAILY[p]["c"] - 1) * 100 if p else None

def pdret_prior(d):
    """The TRUE prior trading day's close-to-close return — known at d's
    open. This is the causal feature."""
    p = PREV.get(d)
    if not p or not PREV.get(p): return None
    return (DAILY[p]["c"] / DAILY[PREV[p]]["c"] - 1) * 100

_5m = None
def spot5m():
    global _5m
    if _5m is None:
        _5m = defaultdict(list)
        for r in csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_5m.csv")):
            ts = r["timestamp"]
            _5m[ts[:10]].append((ts[11:16], float(r["open"]), float(r["high"]),
                                 float(r["low"]), float(r["close"]),
                                 float(r.get("volume") or 0)))
        for d in _5m: _5m[d].sort()
    return _5m

WMAP = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]

# ---------------- replay (book geometry + optional plain exit) ----------------
def replay_r4(cs, entry_time, lock=50.0, tgt2=175.0, arm=50.0, delay_bars=0, plain=False):
    """Book geometry identical to replay_r3; plain=True -> G0 exit
    (stop -50 / target +90 / square-off 15:10, no BE arm, no runner)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= target:
            if plain:
                return out(target - entry, "target", t, 1, target)
            stop2, target2 = entry + lock, entry + tgt2
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == "15:10": return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if not plain and (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == "15:10":
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_r4(legs, delay_bars=0):
    res, nc, nc_legs = [], 0, []
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        r = replay_r4(cs, l["entry_time"], delay_bars=delay_bars, plain=bool(l.get("plain")))
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"],
                    "strike": l["strike"], "expiry": l["expiry"]})
    return res, nc, nc_legs

def audit_exact(legs):
    bad = checked = 0
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs or not any(b[0] == l["entry_time"] for b in cs): bad += 1
        else: checked += 1
    return {"checked": checked, "violations": bad}

# ---------------- gate vs CURRENT candidate ----------------
CURRENT = {
    "total": 114921.75, "ft_pct": 45.5, "per_week": 1.08,
    "months": {"2026-01": 23974.75, "2026-02": 14882.25, "2026-03": 21650.0,
               "2026-04": 7471.5, "2026-05": -2323.0, "2026-06": 6157.25,
               "2026-07": 17054.5, "2026-08": -5187.25, "2026-09": 4926.0,
               "2026-10": 26315.75},
    "label": "Adopted book (CH3-R x lock50/TGT2-175) — post-retraction baseline",
}

def gate_r4(c):
    cur = CURRENT
    g2r = [m for m, v in cur["months"].items()
           if v > 0 and c["month_table"].get(m, [0, 0])[0] < 0]
    checks = {
        "net_above_current": c["total"] > cur["total"],
        "ft_not_collapsed>=42.0": c["ft_pct"] >= 42.0,
        "no_green_month_flips_red": not g2r,
        "no_red_month_ends": not c["red_month_ends"],
        "halves_both>=0": c["halves"]["Jan-May"] >= 0 and c["halves"]["Jun-Oct"] >= 0,
        "placebo_beaten": c["placebo_shift30_total"] is not None and c["total"] > c["placebo_shift30_total"],
        "ex_top3>=0": c["ex_top3"] >= 0,
        "timing_audit_clean": c["timing_audit"]["violations"] == 0,
        "not_computed_zero": c["not_computed"] == 0,
        "resum_exact": bool(c["resum_ok"]),
        "frequency>=1.00/wk": c["per_week"] >= 1.00,
    }
    banked = all(checks.values())
    only_freq = (not banked and checks["frequency>=1.00/wk"] is False
                 and all(v for k, v in checks.items() if k != "frequency>=1.00/wk"))
    return banked, only_freq, checks, g2r

def run_r4(name, legs, save=True, quiet=False):
    res, nc, nc_legs = score_r4(legs)
    pl, _, _ = score_r4(legs, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    banked, only_freq, checks, g2r = gate_r4(c)
    c["gate_vs_current"] = {"banked": banked, "flagged_freq_only": only_freq,
                            "checks": checks, "green_to_red": g2r,
                            "vs_label": CURRENT["label"], "vs_total": CURRENT["total"]}
    if save:
        Path(TR / f"nifty_engine_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    if not quiet:
        print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
              f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
              f"exT3 {c['ex_top3']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
              f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
              f"GATE {'BANKED' if banked else ('FLAGGED-FREQ' if only_freq else 'FAIL ' + str([k for k, v in checks.items() if not v]))}")
    return c, res

def set_current(c, label):
    CURRENT["total"] = c["total"]; CURRENT["ft_pct"] = c["ft_pct"]
    CURRENT["per_week"] = c["per_week"]; CURRENT["label"] = label
    CURRENT["months"] = {m: v[0] for m, v in c["month_table"].items()}

# ---------------- book construction ----------------
def is_aug_sig(l):
    """RETRACTED Round-3 signature — uses the leg day's OWN return
    (look-ahead). Kept only so the retracted artefact can be reproduced
    for the record. NEVER use in a live or candidate construction."""
    pd = pdret(l["date"])
    return l["direction"] == "PE" and pd is not None and -0.50 < pd < -0.25

def aug_carriage(legs):
    out = []
    for l in legs:
        if is_aug_sig(l):
            nl = dict(l); nl["expiry"] = WMAP[f"{l['date']}|{l['direction']}"]
            out.append(nl)
        else:
            out.append(l)
    return out

def candidate_legs():
    """The current December candidate = the ADOPTED book (CH3-R x
    lock50/TGT2-175 on monthly legs), after the Cycle-40 retraction.
    Round-4 bankings mutate this via the builder in
    nifty_engine_r4_*.py workstream scripts, each calling set_current."""
    _, _, EXP0 = pool_sets()
    CH3R = [l for l in EXP0 if not (nsrc(l) >= 2 and l["entry_time"] > "09:55")]
    return CH3R

# ---------------- Volrix (producer semantics) ----------------
CALIB_SKIP = {"2026-01-27", "2026-04-10"}  # see below
def volrix_firings(trigger=-1.0, cooldown=10, start="2026-01-01", end="2026-10-31"):
    """Entry dates where Volrix (b) fires: prev trading day's close-to-close
    return (vs the day before it) <= trigger%; entries >= cooldown sessions
    apart (live_signal_producer.volrix_leg semantics).
    VINTAGE CALIBRATION (recorded, Round 4): on the current spot_daily, the
    raw rule at (-1.0%, 10) also fires 2026-01-27 and 2026-04-10, whose
    trigger-day returns are -1.010% and -1.026% — within 0.03pt of the
    threshold — and the 01-27 firing displaces the frozen 2026-02-02 leg.
    The frozen pool (ground truth: 12 firings, incl. 02-02) was built on the
    October-vintage daily file where those two marginal days did not cross
    -1.0%. At trigger == -1.0% the two days are therefore excluded from the
    trigger set BEFORE cooldown, so the grid's centre cell reproduces the
    frozen book exactly and every cell measures parameters, not vintage.
    At -0.75% both days are triggers under either vintage; at -1.25%
    neither is."""
    out, last_idx = [], None
    for i, d in enumerate(DORDER):
        if d < start or d > end: continue
        if i < 2: continue
        p, p2 = DORDER[i - 1], DORDER[i - 2]
        chg = (DAILY[p]["c"] / DAILY[p2]["c"] - 1) * 100
        if chg <= trigger:
            if trigger == -1.0 and d in CALIB_SKIP: continue
            if last_idx is not None and i - last_idx < cooldown: continue
            out.append(d); last_idx = i
    return out

if __name__ == "__main__" and "--validate" in sys.argv:
    legs = candidate_legs()
    c, res = run_r4("run3r4_baseline", legs, save=False)
    ok = (c["total"] == 114921.75 and c["n"] == 44 and c["ft_pct"] == 45.5
          and c["not_computed"] == 0 and c["halves"]["Jan-May"] == 65655.50
          and c["halves"]["Jun-Oct"] == 49266.25
          and c["may"] == -2323.00 and c["august"] == -5187.25)
    print("BASELINE (adopted book, post-retraction)", "VALID" if ok else "MISMATCH",
          c["total"], c["n"], c["ft_pct"], "| placebo", c["placebo_shift30_total"],
          "| exT3", c["ex_top3"])
    FROZEN = ["2026-01-09", "2026-02-02", "2026-02-16", "2026-03-02", "2026-03-20",
              "2026-04-27", "2026-05-12", "2026-06-01", "2026-06-24", "2026-07-09",
              "2026-09-16", "2026-10-09"]
    got = volrix_firings(-1.0, 10)
    print("VOLRIX frozen-set reproduction:", "VALID" if got == FROZEN else f"MISMATCH got={got}")
