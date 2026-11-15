#!/usr/bin/env python3
"""NIFTY TUNING PROGRAMME — 2026-11-12 (owner order 16:23 IST: "tuning all 3").

Segment: NIFTY only. Frozen November primary (NF-PAPER-C3G7) untouched;
outputs are December candidates only. Paper, real Rs0, premiums per 1 lot
(65), cost Rs220/trade, UNIQUE-ONCE.

PRE-REGISTERED TESTS (fixed before any scoring in this run):
  Anchors (must reproduce exactly before any variant is scored):
    DEC-S1  = A + B + C assembly (r11 spec)      -> +91,168.50 / 97 legs
    TUNED v1 (EVE-07) = DEC-S1 minus B PE        -> +103,050.25 / 74 legs
    TUNED v2 (EVE-11) = DEC-S1 minus B PE/A CE/C CE -> +115,950.75 / 59 legs
  T-N1a: TUNED v1 legs, geometry lock 60 -> 50 (tgt2 175 unchanged).
  T-N1b: TUNED v1 legs, geometry tgt2 175 -> 150 (lock 60 unchanged).
  T-N2 : SKIPPED by design (see report): every admission-time field in the
         scored store is consumed (EVE-07/09/10/11), on a closed axis
         (EVE-14/15/16 entry-time; EVE-18 source/C3), or not an honest
         admission property (raw strike level). No variant registered.
  T-N3 : TUNED v2 + C CE restored (== DEC-S1 minus B PE minus A CE; the leg
         set gated as EVE-10 against the v1 frame on 2026-11-05 — here gated
         against the v2 frame, as pre-registered by the task). B PE is NOT
         relaxed (proven leak). A CE costs 0 November legs; C CE costs 1 —
         the second-costliest exclusion, hence the registered relaxation.

GATE (project standard, EVE-07..20 / repair programme): candidate FAILS if
total <= incumbent, any incumbent-green month flips red, H1 or H2 <
incumbent, ex-top-3 legs <= incumbent, ex-top-3 days <= incumbent, or its
shift30 placebo is not beaten. Hygiene: NC = 0, re-sum exact, timing
audit clean. Bars are not moved.
"""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r8_harness as R8
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import audit_exact
from nifty_engine_score import controls

TR = Path.home() / "workspace/trading"
GEOM = dict(R7.STANDING_GEOM)  # lock 60, tgt2 175, arm 50, sq 15:20

# ---------------- assembly (r11 spec, identical to nifty_engine_r11_verify) --
A = R7.standing_legs()
B, _fex = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                              with_trend=False, exclude_keys=R7.keys_of(A))
C, _eex = R8.expiry_sleeve_legs(R7.keys_of(A) | R7.keys_of(B))
DECS1 = A + B + C

# component tags from the frozen leg dump (written by the r11 verify run
# from this exact assembly); key-match and assert the split.
dump = json.loads((TR / "nifty_engine_r11_decs1_legs.json").read_text())
tagmap = {}
for d in dump:
    tagmap[(d["date"], d["direction"], d["entry_time"], int(d["strike"]),
            d["expiry"])] = d["component"]

def comp(l):
    return tagmap[(l["date"], l["direction"], l["entry_time"],
                   int(l["strike"]), l["expiry"])]

for l in DECS1:
    l["_comp"] = comp(l)

from collections import Counter
split = Counter((comp(l), l["direction"]) for l in DECS1)
assert len(DECS1) == 97, len(DECS1)
assert split[("B", "PE")] == 23 and split[("B", "CE")] == 26
assert split[("A", "PE")] == 25 and split[("A", "CE")] == 10
assert split[("C", "PE")] == 8 and split[("C", "CE")] == 5

def is_bpe(l): return comp(l) == "B" and l["direction"] == "PE"
def is_ace(l): return comp(l) == "A" and l["direction"] == "CE"
def is_cce(l): return comp(l) == "C" and l["direction"] == "CE"

V1 = [l for l in DECS1 if not is_bpe(l)]
V2 = [l for l in DECS1 if not (is_bpe(l) or is_ace(l) or is_cce(l))]
TN3 = [l for l in DECS1 if not (is_bpe(l) or is_ace(l))]  # v2 + C CE
MIRROR = [l for l in DECS1 if not (is_bpe(l) or is_cce(l))]  # v2 + A CE
assert len(V1) == 74 and len(V2) == 59 and len(TN3) == 64 and len(MIRROR) == 69

# ---------------- battery ----------------------------------------------------
def day_ex_top3(res):
    byd = defaultdict(float)
    for r in res: byd[r["date"]] += r["net"]
    top3 = sorted(byd.values(), reverse=True)[:3]
    return round(sum(byd.values()) - sum(top3), 2), len(byd)

def battery(name, legs, geom):
    res, nc, nc_legs = R6.score_r6(legs, geom=geom)
    pl, _, _ = R6.score_r6(legs, geom=geom, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = [str(x) for x in nc_legs]
    det, ndays = day_ex_top3(res)
    c["ex_top3_days"] = det
    c["leg_days"] = ndays
    assert c["resum_ok"], name
    assert c["not_computed"] == 0, (name, c["nc_legs"])
    assert c["timing_audit"]["violations"] == 0, name
    return c, res

def gate(cand, inc):
    flips = [m for m, v in inc["month_table"].items()
             if v[0] > 0 and cand["month_table"].get(m, [0, 0])[0] < 0]
    checks = {
        "total_gt_incumbent": cand["total"] > inc["total"],
        "no_green_month_flips_red": not flips,
        "h1_ge_incumbent": cand["halves"]["Jan-May"] >= inc["halves"]["Jan-May"],
        "h2_ge_incumbent": cand["halves"]["Jun-Oct"] >= inc["halves"]["Jun-Oct"],
        "ex_top3_legs_gt_incumbent": cand["ex_top3"] > inc["ex_top3"],
        "ex_top3_days_gt_incumbent": cand["ex_top3_days"] > inc["ex_top3_days"],
        "placebo_beaten": cand["placebo_shift30_total"] is not None
                          and cand["total"] > cand["placebo_shift30_total"],
    }
    return all(checks.values()), checks, flips

def brief(c):
    return {k: c[k] for k in ("name", "n", "total", "ft", "ft_pct", "per_week",
                              "halves", "ex_top3", "ex_top3_days",
                              "placebo_shift30_total", "month_table",
                              "red_month_ends", "leg_days")}

out = {}

# ---------------- anchors ------------------------------------------------------
c_dec, res_dec = battery("DEC-S1 anchor", DECS1, GEOM)
assert c_dec["total"] == 91168.50 and c_dec["n"] == 97, c_dec["total"]
out["DEC-S1"] = brief(c_dec)

c_v1, res_v1 = battery("TUNED v1 anchor (EVE-07)", V1, GEOM)
assert c_v1["total"] == 103050.25 and c_v1["n"] == 74, c_v1["total"]
assert c_v1["halves"] == {"Jan-May": 52319.25, "Jun-Oct": 50731.0}
assert c_v1["ex_top3"] == 69585.25
out["TUNED_v1"] = brief(c_v1)

c_v2, res_v2 = battery("TUNED v2 anchor (EVE-11)", V2, GEOM)
assert c_v2["total"] == 115950.75 and c_v2["n"] == 59, c_v2["total"]
assert c_v2["halves"] == {"Jan-May": 67064.25, "Jun-Oct": 48886.5}
assert c_v2["ex_top3"] == 82485.75
out["TUNED_v2"] = brief(c_v2)
print("anchors reproduced: DEC-S1 +91,168.50/97 · v1 +103,050.25/74 · "
      "v2 +115,950.75/59")

# class values (Jan-Oct, incumbent geometry) for the T-N3 accounting
def class_stats(res, pred, tagmap_res):
    sel = [r for r in res if pred(r)]
    return {"legs": len(sel), "net": round(sum(r["net"] for r in sel), 2)}
res_by_key = {(r["date"], r["direction"], r["entry_time"], int(r["strike"]),
               r["expiry"]): r for r in res_dec}
def class_of(r):
    return tagmap[(r["date"], r["direction"], r["entry_time"],
                   int(r["strike"]), r["expiry"])]
out["excluded_classes_jan_oct"] = {
    "B_PE": class_stats(res_dec, lambda r: class_of(r) == "B" and r["direction"] == "PE", res_by_key),
    "A_CE": class_stats(res_dec, lambda r: class_of(r) == "A" and r["direction"] == "CE", res_by_key),
    "C_CE": class_stats(res_dec, lambda r: class_of(r) == "C" and r["direction"] == "CE", res_by_key),
}

# v2 frequency by month (legs + net), for T-N3 quantification
bym = defaultdict(lambda: [0, 0.0])
for r in res_v2:
    bym[r["date"][:7]][0] += 1
    bym[r["date"][:7]][1] = round(bym[r["date"][:7]][1] + r["net"], 2)
out["v2_by_month"] = {m: bym[m] for m in sorted(bym)}

# ---------------- T-N1: exit-geometry variants on v1 legs ----------------------
for tag, g in (("T-N1a_lock50", dict(GEOM, lock=50.0)),
               ("T-N1b_tgt2_150", dict(GEOM, tgt2=150.0))):
    c, res = battery(tag, V1, g)
    ok, checks, flips = gate(c, c_v1)
    out[tag] = {"battery": brief(c), "gate_pass": ok, "checks": checks,
                "flips": flips, "delta_vs_v1": round(c["total"] - c_v1["total"], 2)}
    print(f"{tag}: total {c['total']:+,.2f} (delta {c['total']-c_v1['total']:+,.2f}) "
          f"gate {'PASS' if ok else 'FAIL'}")

# ---------------- T-N3: v2 + C CE, gated vs v2 ---------------------------------
c_tn3, res_tn3 = battery("T-N3 (v2 + C CE)", TN3, GEOM)
ok3, checks3, flips3 = gate(c_tn3, c_v2)
out["T-N3"] = {"battery": brief(c_tn3), "gate_pass_vs_v2": ok3,
              "checks_vs_v2": checks3, "flips": flips3,
              "delta_vs_v2": round(c_tn3["total"] - c_v2["total"], 2),
              "delta_vs_v1": round(c_tn3["total"] - c_v1["total"], 2)}
print(f"T-N3: total {c_tn3['total']:+,.2f} (vs v2 {c_tn3['total']-c_v2['total']:+,.2f}) "
      f"gate vs v2 {'PASS' if ok3 else 'FAIL'}")

c_mir, _ = battery("T-N3 mirror placebo (v2 + A CE)", MIRROR, GEOM)
out["T-N3_mirror_placebo"] = brief(c_mir)
out["T-N3"]["mirror_placebo_total"] = c_mir["total"]
out["T-N3"]["beats_mirror"] = c_tn3["total"] > c_mir["total"]
print(f"T-N3 mirror (v2 + A CE): {c_mir['total']:+,.2f}")

# ---------------- November counterfactual derivation ---------------------------
# November DEC-S1 shadow log legs (candle-scored): B PE x4, C CE x1.
# v1 keeps only the C CE leg; T-N1 variants alter only the runner branch
# (lock / tgt2), which the C CE leg never entered (incumbent exit_reason
# square_off at +50.10 pts; tgt1 +90 never touched) and leave arm/stop
# untouched -> identical November net under T-N1a and T-N1b: +3,036.50.
# T-N3 admits the same C CE leg under unchanged geometry -> +3,036.50.
# v2 admits none -> Rs0. Direct candle replay attempted as a cross-check.
nov_check = {"method": "derivation from candle-scored shadow log + replay-semantics proof",
             "v1_nov": 3036.50, "T-N1a_nov": 3036.50, "T-N1b_nov": 3036.50,
             "v2_nov": 0.0, "T-N3_nov": 3036.50}
try:
    from nifty_engine_r2_harness import candles_exact
    from nifty_engine_r5_harness import replay_r5
    cs = candles_exact("NIFTY", 23600, "CE", "2026-11-03", "2026-11-03")
    if cs:
        nov_check["direct_replay"] = {}
        for tag, g in (("incumbent", GEOM), ("T-N1a", dict(GEOM, lock=50.0)),
                       ("T-N1b", dict(GEOM, tgt2=150.0))):
            r = replay_r5(cs, "09:50", **g)
            nov_check["direct_replay"][tag] = r
        nov_check["method"] += " + direct candle replay (candles in store)"
except Exception as e:
    nov_check["replay_error"] = str(e)
out["november_counterfactuals"] = nov_check

(TR / "tuning_nifty_2026-11-12_results.json").write_text(
    json.dumps(out, indent=1, default=str))
print(json.dumps({k: out[k] for k in ("T-N1a_lock50", "T-N1b_tgt2_150")},
                 indent=1, default=str)[:1500])
print("DONE")
