#!/usr/bin/env python3
"""RUN 3 ROUND 5 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Opens with WS0: a feature-causality audit of the
ADOPTED book (CH3-R x lock50/TGT2-175 = +114,921.75, 44 trades). The audit
re-baselines the round to the CAUSAL BOOK (see nifty_engine_frozen.md,
Round-5 WS0 freeze): confirmed legs are admitted at the bar where their
confirmation completes, not at the earliest system's bar.

Per-leg geometry replay (lock / tgt2 / arm / square-off per leg) for the
WS2 strike axis, WS3 expiry-day geometry cells and WS4 entry-time split.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r2_harness import candles_exact, pool_sets, audit_exact
from nifty_engine_r4_harness import candidate_legs, spot5m, DAILY, PREV, DORDER, pdret_prior, WMAP
from nifty_engine_score import controls, nsrc

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
BOOK_GEOM = dict(lock=50.0, tgt2=175.0, arm=50.0, sq="15:10")

def replay_r5(cs, entry_time, lock=50.0, tgt2=175.0, arm=50.0, sq="15:10",
              delay_bars=0, gap_stop_open=False, min_stop_px=None):
    """Adopted-book geometry with per-leg lock/tgt2/arm/square-off.
    stop -50, BE arm -> entry, tgt1 +90 -> runner (lock, tgt2), stop before
    target on every bar incl. entry bar, terminal square-off at sq close.

    Opt-in realism guards (2026-11-25; default False/None to preserve exact
    reproduction of frozen Jan-Oct control anchors):
      - min_stop_px: e.g. 0.05 prevents negative stop prices on low-premium
        expiry options (such as 2026-11-17 CE @ 38.80 -> stop -11.20).
      - gap_stop_open: if True, a bar opening at/below the active stop fills
        at that bar's open (`o`) instead of the idealized stop level."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > sq: return None
    entry = bars[0][1]
    stop = entry - 50.0
    if min_stop_px is not None:
        stop = max(stop, float(min_stop_px))
    target = entry + 90.0
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        if gap_stop_open and o <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(o - entry, rsn, t, 0, o)
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if gap_stop_open and o2 <= stop2:
                    return out(o2 - entry, "runner_stop", t2, 1, o2)
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == sq: return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == sq:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_r5(legs, geom_by_leg=None, delay_bars=0):
    res, nc, nc_legs = [], 0, []
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        g = geom_by_leg(l) if geom_by_leg else BOOK_GEOM
        r = replay_r5(cs, l["entry_time"], delay_bars=delay_bars, **g)
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"],
                    "strike": l["strike"], "expiry": l["expiry"]})
    return res, nc, nc_legs

# ---------------- gate vs CURRENT book (Round-4 gate verbatim) ----------------
CURRENT = {"total": None, "months": {}, "label": "UNSET — WS0 must re-baseline first"}

def gate_r5(c):
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

def run_r5(name, legs, geom_by_leg=None, save=True, quiet=False, gate=True):
    res, nc, nc_legs = score_r5(legs, geom_by_leg=geom_by_leg)
    pl, _, _ = score_r5(legs, geom_by_leg=geom_by_leg, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    if gate and CURRENT["total"] is not None:
        banked, only_freq, checks, g2r = gate_r5(c)
        c["gate_vs_current"] = {"banked": banked, "flagged_freq_only": only_freq,
                                "checks": checks, "green_to_red": g2r,
                                "vs_label": CURRENT["label"], "vs_total": CURRENT["total"]}
    if save:
        Path(TR / f"nifty_engine_run3r5_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    if not quiet:
        g = c.get("gate_vs_current", {})
        print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
              f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
              f"exT3 {c['ex_top3']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
              f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
              f"GATE {'BANKED' if g.get('banked') else ('FLAGGED-FREQ' if g.get('flagged_freq_only') else ('FAIL ' + str([k for k, v in g.get('checks', {}).items() if not v]) if g else 'n/a'))}")
    return c, res

def set_current(c, label):
    CURRENT["total"] = c["total"]; CURRENT["label"] = label
    CURRENT["months"] = {m: v[0] for m, v in c["month_table"].items()}

if __name__ == "__main__" and "--validate" in sys.argv:
    # replay_r5 at book geometry must reproduce the adopted book exactly
    legs = candidate_legs()
    c, res = run_r5("validate_adopted", legs, save=False, gate=False)
    ok = (c["total"] == 114921.75 and c["n"] == 44 and c["ft_pct"] == 45.5 and c["not_computed"] == 0)
    print("R5 replay vs adopted book:", "VALID" if ok else "MISMATCH", c["total"], c["n"], c["ft_pct"])
