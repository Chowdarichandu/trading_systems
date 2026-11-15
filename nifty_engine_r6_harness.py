#!/usr/bin/env python3
"""RUN 3 ROUND 6 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). Baseline CHANGED by Round 5's WS0 audit: the
CAUSAL BOOK (+50,618.00, 35 trades, FT 34.3%, 0.86/wk) is the standing
baseline and the December candidate under test. Freeze:
nifty_engine_frozen.md ROUND 6 section (written before any scoring).

Gate: RELATIVE gate is the banking test (net up, FT and frequency not
degraded vs the standing baseline, no baseline-green month flips red, no
red month-ends, halves >= 0, placebo beaten, ex-top-3 >= 0, audit clean,
NC = 0, re-sum exact). The OLD ABSOLUTE lines (FT >= 42.0%, frequency
>= 1.00/wk) are printed for every verdict as STATUS ONLY — referred to
the owner (lesson 56), never decided on, never silently relaxed.

Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0.
November primary untouched (read-only at most)."""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r2_harness import candles_exact, pool_sets, audit_exact
from nifty_engine_r4_harness import spot5m
from nifty_engine_r5_harness import replay_r5
from nifty_engine_r5_ws0 import build_sysmap, causal_legs
from nifty_engine_score import controls, nsrc, pool

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
BOOK_GEOM = dict(lock=50.0, tgt2=175.0, arm=50.0, sq="15:10")

_SYSMAP = None
def sysmap():
    global _SYSMAP
    if _SYSMAP is None: _SYSMAP = build_sysmap()
    return _SYSMAP

def atm100(x):
    return int(math.floor(x / 100.0 + 0.5)) * 100

def spot_open(date, t):
    for b in spot5m().get(date, []):
        if b[0] == t: return b[1]
    return None

def sources_of(l):
    return [s.strip() for s in l["sources"].split(";") if s.strip()]

# ---------------- population builders (freeze: Round 6 WS1/WS2) ----------------
def native_population(systems_needed=2, window="09:55", solo=True):
    """Confirmation-native rebuild on the EXP0 base. Confirmed keys enter
    at t_k (k-th earliest system entry) iff t_k <= window (None = no
    window); strike re-struck ATM100 at t_k when t_k != recorded entry.
    Solo (lA) keys per the solo axis. Returns (legs, notes)."""
    S = sysmap()
    _, _, EXP0 = pool_sets()
    legs, notes = [], {"no_time": [], "insufficient_systems": 0}
    for l in EXP0:
        srcs = sources_of(l)
        if len(srcs) == 1:
            if solo: legs.append(dict(l))
            continue
        times = sorted(S.get((l["date"], l["direction"]), {}).get(s) for s in srcs)
        if any(t is None for t in times):
            notes["no_time"].append((l["date"], l["direction"], str(srcs))); continue
        if len(times) < systems_needed:
            notes["insufficient_systems"] += 1; continue
        tk = times[systems_needed - 1]
        if window is not None and tk > window: continue
        nl = dict(l); nl["entry_time"] = tk
        if tk != l["entry_time"]:
            so = spot_open(l["date"], tk)
            assert so is not None, (l["date"], tk)
            nl["strike"] = atm100(so)
        legs.append(nl)
    return legs, notes

def solo_book(system):
    """WS2: every pool key (EXP0-filtered) where `system` fired, entered
    at the system's OWN bar, strike ATM100 at that bar. Returns
    (legs, missing_named)."""
    S = sysmap()
    legs, missing = [], []
    for l in pool():
        if l["date"] == l["expiry"]: continue
        if system not in sources_of(l): continue
        t = S.get((l["date"], l["direction"]), {}).get(system)
        if t is None:
            missing.append((l["date"], l["direction"], system)); continue
        nl = dict(l); nl["entry_time"] = t
        if t != l["entry_time"]:
            so = spot_open(l["date"], t)
            assert so is not None, (l["date"], t)
            nl["strike"] = atm100(so)
        legs.append(nl)
    return legs, missing

def missing_candles(legs):
    out = []
    for l in legs:
        if not candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"]):
            out.append((int(l["strike"]), l["direction"], l["date"], l["expiry"]))
    return sorted(set(out))

# ---------------- scoring ----------------
def score_r6(legs, geom=None, delay_bars=0):
    g = geom or BOOK_GEOM
    res, nc, nc_legs = [], 0, []
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        r = replay_r5(cs, l["entry_time"], delay_bars=delay_bars, **g)
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"], l.get("strike"))); continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"],
                    "strike": l["strike"], "expiry": l["expiry"]})
    return res, nc, nc_legs

# ---------------- dual gate vs standing baseline ----------------
CURRENT = {"total": None, "ft_pct": None, "per_week": None, "months": {}, "label": "UNSET"}

def gate_r6(c):
    cur = CURRENT
    g2r = [m for m, v in cur["months"].items()
           if v > 0 and c["month_table"].get(m, [0, 0])[0] < 0]
    rel = {
        "net_above_baseline": c["total"] > cur["total"],
        "ft_not_degraded": c["ft_pct"] >= cur["ft_pct"],
        "frequency_not_degraded": c["per_week"] >= cur["per_week"],
        "no_green_month_flips_red": not g2r,
        "no_red_month_ends": not c["red_month_ends"],
        "halves_both>=0": c["halves"]["Jan-May"] >= 0 and c["halves"]["Jun-Oct"] >= 0,
        "placebo_beaten": c["placebo_shift30_total"] is not None and c["total"] > c["placebo_shift30_total"],
        "ex_top3>=0": c["ex_top3"] >= 0,
        "timing_audit_clean": c["timing_audit"]["violations"] == 0,
        "not_computed_zero": c["not_computed"] == 0,
        "resum_exact": bool(c["resum_ok"]),
    }
    abs_lines = {"FT>=42.0": c["ft_pct"] >= 42.0, "freq>=1.00/wk": c["per_week"] >= 1.00}
    return all(rel.values()), rel, abs_lines, g2r

def run_r6(name, legs, geom=None, save=True, quiet=False, gate=True):
    res, nc, nc_legs = score_r6(legs, geom=geom)
    pl, _, _ = score_r6(legs, geom=geom, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["nc_named_not_computed"] = ("2026-10-28 22500 PE weekly expiry 2026-11-03 — NOT_COMPUTED "
                                  "(registry 0 contracts, Rounds 3-5); not in any Round-6 population")
    if gate and CURRENT["total"] is not None:
        banked, rel, abs_lines, g2r = gate_r6(c)
        c["gate_relative"] = {"banked": banked, "checks": rel, "green_to_red": g2r,
                              "vs_label": CURRENT["label"], "vs_total": CURRENT["total"],
                              "vs_ft_pct": CURRENT["ft_pct"], "vs_per_week": CURRENT["per_week"]}
        c["old_absolute_lines_status"] = abs_lines
    if save:
        Path(TR / f"nifty_engine_run3r6_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    if not quiet:
        g = c.get("gate_relative", {})
        a = c.get("old_absolute_lines_status", {})
        print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
              f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
              f"exT3 {c['ex_top3']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
              f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
              f"REL-GATE {'BANKED' if g.get('banked') else 'FAIL ' + str([k for k, v in g.get('checks', {}).items() if not v])} | "
              f"ABS-LINES FT42 {'PASS' if a.get('FT>=42.0') else 'FAIL'} / FREQ1.00 {'PASS' if a.get('freq>=1.00/wk') else 'FAIL'} (status only)")
    return c, res

def set_current(c, label):
    CURRENT["total"] = c["total"]; CURRENT["ft_pct"] = c["ft_pct"]
    CURRENT["per_week"] = c["per_week"]; CURRENT["label"] = label
    CURRENT["months"] = {m: v[0] for m, v in c["month_table"].items()}

if __name__ == "__main__" and "--validate" in sys.argv:
    # 1) causal book via the Round-5 machinery must equal the WS0 figures
    c0, _ = run_r6("validate_causal", causal_legs(), save=False, gate=False)
    ok0 = (c0["total"] == 50618.00 and c0["n"] == 35 and c0["ft_pct"] == 34.3
           and c0["per_week"] == 0.86 and c0["not_computed"] == 0)
    print("CAUSAL BOOK via r6 harness:", "VALID" if ok0 else "MISMATCH",
          c0["total"], c0["n"], c0["ft_pct"], c0["per_week"])
    set_current(c0, "Causal book (Round-5 WS0 baseline)")
    # 2) WS1 centre cell must reproduce the causal book exactly
    legs, notes = native_population(2, "09:55", True)
    c1, _ = run_r6("validate_centre", legs, save=False)
    same = sorted((l["date"], l["direction"], l["entry_time"], l["strike"]) for l in legs) == \
           sorted((l["date"], l["direction"], l["entry_time"], l["strike"]) for l in causal_legs())
    ok1 = same and c1["total"] == 50618.00 and c1["n"] == 35
    print("WS1 CENTRE == causal book:", "VALID" if ok1 else f"MISMATCH legs_same={same}",
          c1["total"], c1["n"], "| notes:", notes)
