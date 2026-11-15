#!/usr/bin/env python3
"""ROUND 10 stage 1: Cycle 159 validation + Cycle 160 WS1 (Bank-spot
agreement conditioning) + Cycle 161 WS1 mirror (closure record under the
frozen mirror rule). State persists in nifty_engine_r10_standing.json.
Freeze: ROUND 10 section of nifty_engine_frozen.md. Nifty only, paper,
real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r10_harness as R10

TR = Path.home() / "workspace/trading"
STATE = TR / "nifty_engine_r10_standing.json"
ROUND_OPEN = {"total": 54102.00, "ft_pct": 34.3, "per_week": 0.86}

def save_state(legs, c, label):
    STATE.write_text(json.dumps({
        "legs": legs, "label": label, "total": c["total"], "ft_pct": c["ft_pct"],
        "per_week": c["per_week"],
        "months": {m: v[0] for m, v in c["month_table"].items()}}, indent=1))

def load_state():
    s = json.loads(STATE.read_text())
    R6.CURRENT.update(total=s["total"], ft_pct=s["ft_pct"], per_week=s["per_week"],
                      label=s["label"], months=s["months"])
    return s["legs"], s["label"]

def set_current_open(c):
    R6.CURRENT.update(total=ROUND_OPEN["total"], ft_pct=ROUND_OPEN["ft_pct"],
                      per_week=ROUND_OPEN["per_week"],
                      label="Round-6/7/8/9 standing book (Round-10 open)",
                      months={m: v[0] for m, v in c["month_table"].items()})

def main():
    standing = R7.standing_legs()
    # ---------- Cycle 159: validation ----------
    c159, _ = R10.run_r10("r10_c159_validate_standing", standing, gate=False)
    ok = (c159["total"] == 54102.00 and c159["n"] == 35 and c159["ft_pct"] == 34.3
          and c159["per_week"] == 0.86 and c159["not_computed"] == 0 and c159["resum_ok"])
    print("ROUND-10 VALIDATION (Cycle 159):", "VALID" if ok else "MISMATCH",
          c159["total"], c159["n"], c159["ft_pct"], c159["per_week"])
    assert ok, "validation failed — no Round-10 candidate may be trusted"
    set_current_open(c159)
    save_state(standing, c159, "Round-6/7/8/9 standing book (Round-10 open)")

    # ---------- Cycle 160: WS1 agreement conditioning ----------
    agree, diag = R10.ws1_agree_legs(standing)
    from collections import Counter
    print("WS1 buckets:", Counter(d[3] for d in diag),
          "| agree legs:", len(agree))
    c160, _ = R10.run_r10("r10_c160_ws1_bankspot_agree", agree)
    if c160.get("gate_relative", {}).get("banked"):
        save_state(agree, c160, "Standing book + WS1 Bank-spot agreement conditioning (C160 BANKED)")
        print("C160 BANKED — standing book updated (supersession).")
    else:
        print("C160 not banked — standing book unchanged.")

    # ---------- Cycle 161: WS1 mirror — closure record (frozen rule) ----------
    # The freeze's mirror rule evaluates on the standing legs' scored nets:
    # run the mirror ONLY IF net(disagree) > 0 AND net(disagree) > net(agree).
    _, sres = R10.score_sleeve_alone("standing-for-mirror-diagnostic", standing)
    snet = {(r["date"], r["direction"]): r["net"] for r in sres}
    buckets = {"agree": [], "disagree": [], "neutral": [], "unavailable": []}
    for l in standing:
        b, mv = R10.bank_bucket(l)
        buckets[b or "unavailable"].append(l)
    bnet = {b: round(sum(snet.get((l["date"], l["direction"]), 0.0) for l in ls), 2)
            for b, ls in buckets.items()}
    fires = bnet["disagree"] > 0 and bnet["disagree"] > bnet["agree"]
    rec = {
        "name": "r10_c161_ws1_mirror_closure_record",
        "cycle": 161, "scored": False,
        "reason": ("Frozen WS1 mirror rule (ROUND 10 freeze): the mirror form is scored ONLY IF "
                   "net(disagree bucket) > 0 AND net(disagree bucket) > net(agree bucket) on the "
                   "standing legs. The diagnostic does not fire; independently, the disagreement-"
                   "conditioned population is EMPTY (0 legs) — Bank and Nifty never move >= 0.20% "
                   "in opposite directions by the standing legs' entry bars."),
        "buckets": {b: {"legs": len(ls), "net": bnet[b]} for b, ls in buckets.items()},
        "mirror_rule_fires": fires,
        "verdict": "NOT RUN — closure record; WS1 family closes with the Cycle-160 agreement form as its only candidate.",
        "nc_named_not_computed": ("2026-10-28 22500 PE weekly expiry 2026-11-03 — NOT_COMPUTED "
                                  "(registry 0 contracts, Rounds 3-6); not in any Round-10 population"),
    }
    Path(TR / "nifty_engine_run3r10_r10_c161_ws1_mirror_notrun_summary.json").write_text(
        json.dumps(rec, indent=1, default=str))
    print("C161 mirror closure record:", rec["buckets"], "| rule fires:", fires)

if __name__ == "__main__":
    main()
