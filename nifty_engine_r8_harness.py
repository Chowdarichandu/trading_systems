#!/usr/bin/env python3
"""RUN 3 ROUND 8 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Baseline: the Round-6/7 standing book
(+54,102.00, causal 35 legs, lock60/TGT2-175, sq 15:20). Freeze:
nifty_engine_frozen.md ROUND 8 section (written before any Round-8
candidate scoring; the March diagnosis in nifty_engine_r8_diag_march.py
is a re-score of the already-gated Round-7 Cycle-133 construction).

Gate: RELATIVE gate is the banking test (net up, FT and frequency not
degraded vs the standing baseline, no baseline-green month flips red, no
red month-ends, halves >= 0, placebo beaten, ex-top-3 >= 0, audit clean,
NC = 0, re-sum exact). OLD ABSOLUTE lines (FT >= 42.0%, frequency
>= 1.00/wk) printed as STATUS ONLY for every verdict.

Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0.
November primary untouched (read-only at most)."""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import candles_exact, audit_exact
from nifty_engine_r4_harness import spot5m, DAILY, PREV, DORDER, pdret_prior
from nifty_engine_r5_harness import replay_r5
from nifty_engine_score import controls, pool

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
STANDING_GEOM = R7.STANDING_GEOM
EXPIRY_GEOM = dict(stop_pts=40.0, tgt1_pts=60.0, lock=30.0, tgt2=110.0, arm=50.0, sq="15:20")

# ---------------- parameterised replay (WS2 own geometry) ----------------
def replay_r8(cs, entry_time, stop_pts=50.0, tgt1_pts=90.0, lock=60.0,
              tgt2=175.0, arm=50.0, sq="15:20", delay_bars=0):
    """replay_r5's exact bar logic with parameterised stop/tgt1, tracking
    two FT readings: ft (FT90 — the traded path, stop checked first on each
    bar per the book convention, reaches entry+90) and ft_own (the leg
    reaches its own tgt1 and enters the runner phase)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > sq: return None
    entry = bars[0][1]
    stop, target = entry - stop_pts, entry + tgt1_pts
    state = {"ft90": 0}
    def out(net_pts, reason, t, ft_own, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=state["ft90"], ft_own=ft_own,
                    entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= entry + 90.0: state["ft90"] = 1
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= entry + 90.0: state["ft90"] = 1
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

def score_r8_mixed(spec, delay_bars=0):
    """spec: list of (leg, kind), kind in {'standing','expiry'}. Standing
    legs score through replay_r5 at STANDING_GEOM (their ft IS the FT90
    reading and their own target is +90, so ft_own = ft). Expiry legs
    score through replay_r8 at EXPIRY_GEOM with ft set to the FT90
    reading and ft_own carried alongside."""
    res, nc, nc_legs = [], 0, []
    for l, kind in spec:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        if kind == "standing":
            r = replay_r5(cs, l["entry_time"], delay_bars=delay_bars, **STANDING_GEOM)
            if r is not None: r = {**r, "ft_own": r["ft"]}
        else:
            r = replay_r8(cs, l["entry_time"], delay_bars=delay_bars, **EXPIRY_GEOM)
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"],
                    "strike": l["strike"], "expiry": l["expiry"], "kind": kind})
    return res, nc, nc_legs

def run_r8_mixed(name, spec, save=True, gate=True):
    """Gate a mixed-geometry book. controls() reads r['ft'] = the FT90
    reading, so the relative gate below IS the FT90-reading gate (the only
    banking basis). The own-target FT verdict is computed alongside and
    stored as DECISION SUPPORT ONLY."""
    legs = [l for l, _ in spec]
    res, nc, nc_legs = score_r8_mixed(spec)
    pl, _, _ = score_r8_mixed(spec, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    n = c["n"]
    ft_own_pct = round(100.0 * sum(r["ft_own"] for r in res) / n, 1) if n else 0.0
    c["ft90_pct_banking_basis"] = c["ft_pct"]
    c["ft_own_target_pct_DECISION_SUPPORT_ONLY"] = ft_own_pct
    if gate and R6.CURRENT["total"] is not None:
        banked, rel, abs_lines, g2r = R6.gate_r6(c)
        c["gate_relative_FT90_reading"] = {"banked": banked, "checks": rel, "green_to_red": g2r,
                                           "vs_label": R6.CURRENT["label"], "vs_total": R6.CURRENT["total"],
                                           "vs_ft_pct": R6.CURRENT["ft_pct"], "vs_per_week": R6.CURRENT["per_week"]}
        c["old_absolute_lines_status"] = abs_lines
        rel_own = dict(rel)
        rel_own["ft_not_degraded"] = ft_own_pct >= R6.CURRENT["ft_pct"]
        c["gate_relative_OWN_TARGET_FT_reading_DECISION_SUPPORT_ONLY"] = {
            "would_bank": all(rel_own.values()), "checks": rel_own, "green_to_red": g2r,
            "note": "Decision support for the owner's flagged decision. NEVER a banking basis."}
    if save:
        Path(TR / f"nifty_engine_run3r8_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    g = c.get("gate_relative_FT90_reading", {})
    a = c.get("old_absolute_lines_status", {})
    print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT90 {c['ft_pct']}% | FT-own {ft_own_pct}% (DS) | "
          f"{c['per_week']}/wk | halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | "
          f"placebo {c['placebo_shift30_total']:+,.2f} | exT3 {c['ex_top3']:+,.2f} | "
          f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
          f"REL-GATE(FT90) {'BANKED' if g.get('banked') else 'FAIL ' + str([k for k, v in g.get('checks', {}).items() if not v])} | "
          f"ABS FT42 {'PASS' if a.get('FT>=42.0') else 'FAIL'} / FREQ {'PASS' if a.get('freq>=1.00/wk') else 'FAIL'} (status only)")
    return c, res

# ---------------- WS1: gap-fade refined ----------------
def gap_fade_legs_r8(threshold=0.005, entry_time="09:35", with_trend=False,
                     exclude_keys=frozenset()):
    """The Round-7 Cycle-133 FADE construction with one axis varied.
    with_trend: admit iff sign(gap) == sign(pdret_prior) and pdret_prior
    != 0 (frozen WS1(b) form, Round-8 freeze)."""
    legs, excluded = [], []
    for d, g in R7.gap_days(threshold):
        exp = R7.exp_in_force(d)
        if exp is None or exp == d:
            excluded.append((d, "EXP0/no-expiry")); continue
        direction = "PE" if g > 0 else "CE"
        if with_trend:
            pr = pdret_prior(d)
            if pr is None or pr == 0 or ((g > 0) != (pr > 0)):
                excluded.append((d, direction, "trend-filter")); continue
        if (d, direction) in exclude_keys:
            excluded.append((d, direction, "key-in-standing-book")); continue
        so = R7.spot_open(d, entry_time)
        if so is None:
            excluded.append((d, direction, "no-spot-bar")); continue
        legs.append(dict(date=d, index="NIFTY", direction=direction, entry_time=entry_time,
                         strike=R7.atm100(so), expiry=exp, lot=LOT,
                         rep="R8-GAP-FADE", sources="R8 gap fade refined",
                         family="R8WS1", base_net=0.0, base_reason=""))
    return legs, excluded

# ---------------- WS2: expiry-day sleeve (Round-7 C138 rebuild) ----------------
def weekly_expiry_days():
    exps = json.loads((TR / "nifty_engine_run3_expiries.json").read_text())
    return sorted(e for e in exps
                  if "2026-01-01" <= e <= "2026-10-31" and e not in R7.MONTHLY_EXPIRIES)

def expiry_sleeve_legs(exclude_keys):
    S = R6.sysmap()
    days = set(weekly_expiry_days())
    legs, excluded = [], []
    for l in pool():
        if l["date"] not in days: continue
        srcs = [s.strip() for s in l["sources"].split(";") if s.strip()]
        if "Skill V3" not in srcs: continue
        t = S.get((l["date"], l["direction"]), {}).get("Skill V3")
        if t is None:
            excluded.append((l["date"], l["direction"], "skill-time-missing")); continue
        if not ("09:15" <= t <= "11:00"):
            excluded.append((l["date"], l["direction"], "skill-time-outside-0915-1100")); continue
        if (l["date"], l["direction"]) in exclude_keys:
            excluded.append((l["date"], l["direction"], "key-in-standing-book")); continue
        so = R7.spot_open(l["date"], t)
        if so is None:
            excluded.append((l["date"], l["direction"], "no-spot-bar")); continue
        legs.append(dict(date=l["date"], index="NIFTY", direction=l["direction"],
                         entry_time=t, strike=R7.atm100(so), expiry=l["date"], lot=LOT,
                         rep="R8-EXP-SLEEVE", sources=l["sources"],
                         family="R8WS2", base_net=0.0, base_reason=""))
    return legs, excluded

# ---------------- WS3: afternoon-range sleeve ----------------
def afternoon_legs(exclude_keys):
    S5 = spot5m()
    legs, excluded = [], []
    for d in DORDER:
        if not ("2026-01-01" <= d <= "2026-10-28"): continue
        bars = S5.get(d, [])
        rng = [b for b in bars if "12:00" <= b[0] <= "12:55"]
        if len(rng) < 12:
            excluded.append((d, "incomplete-afternoon-range")); continue
        hi = max(b[2] for b in rng); lo = min(b[3] for b in rng)
        brk = None
        for b in bars:
            if "13:00" <= b[0] <= "14:55":
                if b[4] > hi: brk = (b[0], "CE"); break
                if b[4] < lo: brk = (b[0], "PE"); break
        if brk is None: continue
        bt, direction = brk
        et = R7.add_minutes(bt, 5)
        exp = R7.exp_in_force(d)
        if exp is None or exp == d:
            excluded.append((d, direction, "EXP0/no-expiry")); continue
        if (d, direction) in exclude_keys:
            excluded.append((d, direction, "key-in-standing-book")); continue
        so = R7.spot_open(d, et)
        if so is None:
            excluded.append((d, direction, "no-spot-bar")); continue
        legs.append(dict(date=d, index="NIFTY", direction=direction, entry_time=et,
                         strike=R7.atm100(so), expiry=exp, lot=LOT,
                         rep="R8-AFT-RANGE", sources="R8 afternoon range",
                         family="R8WS3", base_net=0.0, base_reason=""))
    return legs, excluded

def missing_candles(legs):
    return R7.missing_candles(legs)

if __name__ == "__main__" and "--selfcheck" in sys.argv:
    # replay_r8 at standing parameters must equal replay_r5 leg-for-leg on
    # the standing book (machinery check only — not a candidate).
    legs = R7.standing_legs()
    bad = 0
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        a = replay_r5(cs, l["entry_time"], **STANDING_GEOM)
        b = replay_r8(cs, l["entry_time"], stop_pts=50.0, tgt1_pts=90.0, **{k: STANDING_GEOM[k] for k in ("lock", "tgt2", "arm", "sq")})
        if (a is None) != (b is None) or (a and (a["net"] != b["net"] or a["ft"] != b["ft"] or b["ft"] != b["ft_own"])):
            bad += 1; print("MISMATCH", l["date"], l["direction"], a, b)
    print("replay_r8 == replay_r5 on standing book:", "OK" if bad == 0 else f"{bad} MISMATCHES")
