#!/usr/bin/env python3
"""RUN 3 ROUND 7 harness (2026-11-02 standing order: engines do NOT stop
until the floor is met). NEW SIGNAL FAMILIES alongside the Round-6 standing
book (+54,102.00, causal 35 legs, lock60/TGT2-175, sq 15:20). Freeze:
nifty_engine_frozen.md ROUND 7 section (written before any scoring).

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
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import candles_exact, audit_exact
from nifty_engine_r4_harness import spot5m, DAILY, DORDER, PREV
from nifty_engine_score import controls, pool

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65
STANDING_GEOM = dict(lock=60.0, tgt2=175.0, arm=50.0, sq="15:20")
MONTHLY_EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
                    "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
                    "2026-09-29", "2026-10-27", "2026-11-24"]

def atm100(x):
    return int(math.floor(x / 100.0 + 0.5)) * 100

def exp_in_force(day):
    for e in MONTHLY_EXPIRIES:
        if e >= day: return e
    return None

def spot_open(date, t):
    for b in spot5m().get(date, []):
        if b[0] == t: return b[1]
    return None

def standing_legs():
    b = json.loads((TR / "nifty_engine_r6_final_book.json").read_text())
    return [dict(l) for l in b["legs"]]

def keys_of(legs):
    return {(l["date"], l["direction"]) for l in legs}

# ---------------- gate / run (Round-6 form, Round-7 summaries) ----------------
def run_r7(name, legs, geom=None, save=True, quiet=False, gate=True):
    g = geom or STANDING_GEOM
    res, nc, nc_legs = R6.score_r6(legs, geom=g)
    pl, _, _ = R6.score_r6(legs, geom=g, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["nc_named_not_computed"] = ("2026-10-28 22500 PE weekly expiry 2026-11-03 — NOT_COMPUTED "
                                  "(registry 0 contracts, Rounds 3-6); not in any Round-7 population")
    if gate and R6.CURRENT["total"] is not None:
        banked, rel, abs_lines, g2r = R6.gate_r6(c)
        c["gate_relative"] = {"banked": banked, "checks": rel, "green_to_red": g2r,
                              "vs_label": R6.CURRENT["label"], "vs_total": R6.CURRENT["total"],
                              "vs_ft_pct": R6.CURRENT["ft_pct"], "vs_per_week": R6.CURRENT["per_week"]}
        c["old_absolute_lines_status"] = abs_lines
    if save:
        Path(TR / f"nifty_engine_run3r7_{name}_summary.json").write_text(
            json.dumps(c, indent=1, default=str))
    if not quiet:
        gtxt = c.get("gate_relative", {})
        a = c.get("old_absolute_lines_status", {})
        print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
              f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
              f"exT3 {c['ex_top3']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
              f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
              f"REL-GATE {'BANKED' if gtxt.get('banked') else 'FAIL ' + str([k for k, v in gtxt.get('checks', {}).items() if not v])} | "
              f"ABS-LINES FT42 {'PASS' if a.get('FT>=42.0') else 'FAIL'} / FREQ1.00 {'PASS' if a.get('freq>=1.00/wk') else 'FAIL'} (status only)")
    return c, res

def set_current(c, label):
    R6.set_current(c, label)

def score_sleeve_alone(name, legs):
    """Diagnostic print of a sleeve scored alone (not a gate, not a cycle)."""
    res, nc, _ = R6.score_r6(legs, geom=STANDING_GEOM)
    tot = round(sum(r["net"] for r in res), 2)
    print(f"  (diagnostic) {name} standalone: {tot:+,.2f} over {len(res)} legs, NC {nc}")
    return tot, res

# ---------------- WS1: index gap sleeve ----------------
def gap_days(threshold=0.005):
    out = []
    for d in DORDER:
        if not ("2026-01-01" <= d <= "2026-10-28"): continue
        p = PREV.get(d)
        if not p: continue
        g = DAILY[d]["o"] / DAILY[p]["c"] - 1.0
        if abs(g) >= threshold: out.append((d, g))
    return out

def gap_legs(mode, exclude_keys):
    """mode: 'follow' | 'fade'. Returns (legs, excluded_named)."""
    legs, excluded = [], []
    for d, g in gap_days():
        exp = exp_in_force(d)
        if exp is None or exp == d:
            excluded.append((d, "EXP0/no-expiry")); continue
        direction = ("CE" if g > 0 else "PE") if mode == "follow" else ("PE" if g > 0 else "CE")
        if (d, direction) in exclude_keys:
            excluded.append((d, direction, "key-in-standing-book")); continue
        so = spot_open(d, "09:35")
        if so is None:
            excluded.append((d, direction, "no-0935-spot-bar")); continue
        legs.append(dict(date=d, index="NIFTY", direction=direction, entry_time="09:35",
                         strike=atm100(so), expiry=exp, lot=LOT,
                         rep=f"R7-GAP-{mode.upper()}", sources="R7 gap sleeve",
                         family="R7WS1", base_net=0.0, base_reason=""))
    return legs, excluded

# ---------------- WS2: Bank confirmed state ----------------
def build_bank_sysmap():
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "BANKNIFTY" or not et: return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    for r in csv.DictReader(open(TR / "index_options_o1_janoct_trades.csv")):
        if r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2": put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["track"] == "V5-v2": put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_skillV3_jansep_spot.csv")):
        put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_volrixB_jansep_spot.csv")):
        put(r["entry_date"], r["index"], r["direction"], "Volrix (b)", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_premium_october_trades.csv")):
        if r["premium_status"] != "COMPUTED": continue
        if r["version"].startswith("(lA)"): put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["version"].startswith("V5"): put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_skill_tuned_oct30_trades.csv")):
        if r["variant"] == "V3" and r["premium_status"] == "COMPUTED":
            put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    return S

def bank_admissions():
    """Returns (admissions, named_missing): admissions = {date: [(t2_B, dir)]}
    from B2 pool keys with >=2 sources and ALL source times present."""
    import aggressive_score as A
    S = build_bank_sysmap()
    adm, missing = defaultdict(list), []
    for l in A.base_legs("BANKNIFTY"):
        srcs = [s.strip() for s in l["sources"].split(";") if s.strip()]
        if len(srcs) < 2: continue
        times = sorted(S.get((l["date"], l["direction"]), {}).get(s) for s in srcs)
        if any(t is None for t in times):
            missing.append((l["date"], l["direction"], l["sources"])); continue
        adm[l["date"]].append((times[1], l["direction"]))
    for d in adm: adm[d].sort()
    return adm, missing

def bank_state(adm, date, t):
    """Direction of the latest Bank confirmed admission strictly before t."""
    st = None
    for t2, dirn in adm.get(date, []):
        if t2 < t: st = dirn
        else: break
    return st

def add_minutes(t, mins):
    h, m = int(t[:2]), int(t[3:5]) + mins
    return f"{h + m // 60:02d}:{m % 60:02d}"

def ws2b_legs(adm, exclude_keys):
    legs, excluded, seen = [], [], set()
    for d in sorted(adm):
        for t2, dirn in adm[d]:
            if (d, dirn) in seen: continue
            seen.add((d, dirn))
            if t2 > "15:00":
                excluded.append((d, dirn, "t2-after-1500")); continue
            et = add_minutes(t2, 5)
            exp = exp_in_force(d)
            if exp is None or exp == d:
                excluded.append((d, dirn, "EXP0/no-expiry")); continue
            if (d, dirn) in exclude_keys:
                excluded.append((d, dirn, "key-in-standing-book")); continue
            so = spot_open(d, et)
            if so is None:
                excluded.append((d, dirn, "no-spot-bar")); continue
            legs.append(dict(date=d, index="NIFTY", direction=dirn, entry_time=et,
                             strike=atm100(so), expiry=exp, lot=LOT,
                             rep="R7-XIDX-BANKSTATE", sources="R7 cross-index sleeve",
                             family="R7WS2", base_net=0.0, base_reason=""))
    return legs, excluded

def missing_candles(legs):
    out = []
    for l in legs:
        if not candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"]):
            out.append((int(l["strike"]), l["direction"], l["date"], l["expiry"]))
    return sorted(set(out))

if __name__ == "__main__" and "--validate" in sys.argv:
    legs = standing_legs()
    c, _ = run_r7("r7_c131_validate_standing", legs, gate=False, save=True)
    ok = (c["total"] == 54102.00 and c["n"] == 35 and c["ft_pct"] == 34.3
          and c["per_week"] == 0.86 and c["not_computed"] == 0 and c["resum_ok"])
    print("ROUND-7 VALIDATION (Cycle 131):", "VALID" if ok else "MISMATCH",
          c["total"], c["n"], c["ft_pct"], c["per_week"])
