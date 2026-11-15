#!/usr/bin/env python3
"""ROUND 10 stage 2: Cycle 162-163 WS2 (OR-width admission) + Cycle 164
WS3 (post-expiry-day addition) + Cycle 165 WS5 combinations/closure +
Cycle 166 WS4 December-freeze regeneration verification + Cycle 167 WS5
closure re-gate + flagged restatement. State persists in
nifty_engine_r10_standing.json. Freeze: ROUND 10 section of
nifty_engine_frozen.md. Nifty only, paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
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

def set_gate_baseline(legs, label):
    c, _ = R10.run_r10("r10_baseline_probe", legs, save=False, gate=False)
    R6.CURRENT.update(total=c["total"], ft_pct=c["ft_pct"], per_week=c["per_week"],
                      label=label, months={m: v[0] for m, v in c["month_table"].items()})
    return c

def fetch_missing(legs, weekly=False):
    miss = R10.missing_candles(legs)
    if not miss: return
    print(f"  fetching {len(miss)} missing contracts (weekly={weekly}) ...")
    import nifty_engine_r7_fetch as F
    jobs = [(st, ty, d, exp, weekly) for (st, ty, d, exp) in miss]
    out = F.fetch_jobs(jobs)
    ok = sum(1 for _, r in out if isinstance(r, tuple) and r[0] not in ("NO_CONTRACTS_FILE",) and r[1])
    print(f"  fetch done: {ok}/{len(jobs)} returned candles")
    still = R10.missing_candles(legs)
    print(f"  still missing after fetch: {len(still)} {still if still else ''}")

def main():
    standing, label = load_state()
    bankings = []

    # ---------- Cycles 162-163: WS2 OR-width admission ----------
    mid, diag = R10.ws2_legs(standing, {"middle"})
    from collections import Counter
    print("WS2 terciles:", Counter(d[3] for d in diag), "| middle legs:", len(mid))
    c162, _ = R10.run_r10("r10_c162_ws2_orwidth_middle", mid)
    if c162.get("gate_relative", {}).get("banked"):
        standing = mid; bankings.append(("C162 OR-width middle", c162))
        save_state(standing, c162, "Standing book x OR-width middle (C162 BANKED)")
        print("C162 BANKED — standing book updated (supersession).")

    midup, _ = R10.ws2_legs(standing, {"middle", "upper"})
    print("WS2 middle+upper legs:", len(midup))
    c163, _ = R10.run_r10("r10_c163_ws2_orwidth_midupper", midup)
    if c163.get("gate_relative", {}).get("banked"):
        standing = midup; bankings.append(("C163 OR-width middle+upper", c163))
        save_state(standing, c163, "Standing book x OR-width middle+upper (C163 BANKED)")
        print("C163 BANKED — standing book updated (supersession).")

    # ---------- Cycle 164: WS3 post-expiry-day addition ----------
    skeys = R7.keys_of(standing)
    sleeve, excluded = R10.ws3_legs(skeys)
    print(f"WS3 population: {len(sleeve)} legs | named exclusions: {excluded}")
    tot_solo, _ = R10.score_sleeve_alone("R10-WS3-postexpiry", sleeve)
    fetch_missing(sleeve)
    c164, _ = R10.run_r10("r10_c164_ws3_postexpiry_add", standing + sleeve)
    if c164.get("gate_relative", {}).get("banked"):
        standing = standing + sleeve; bankings.append(("C164 WS3 post-expiry sleeve", c164))
        save_state(standing, c164, "Standing book + WS3 post-expiry sleeve (C164 BANKED)")
        print("C164 BANKED — standing book updated (supersession).")

    # ---------- Cycle 165: WS5 combinations / closure ----------
    if len(bankings) >= 2:
        # the banked standing book IS the combination (sequential supersession);
        # re-gate it whole-book vs the ROUND-OPEN baseline.
        cbase = set_gate_baseline(R7.standing_legs(), "Round-open standing book (C165 combination baseline)")
        R6.CURRENT.update(total=ROUND_OPEN["total"], ft_pct=ROUND_OPEN["ft_pct"],
                          per_week=ROUND_OPEN["per_week"], label="Round-open standing book",
                          months={m: v[0] for m, v in cbase["month_table"].items()})
        c165, _ = R10.run_r10("r10_c165_ws5_combination", standing)
        print("C165 combination re-gate vs round-open done.")
        load_state()
    elif len(bankings) == 1:
        cbase = set_gate_baseline(R7.standing_legs(), "Round-open standing book (C165 baseline)")
        R6.CURRENT.update(total=ROUND_OPEN["total"], ft_pct=ROUND_OPEN["ft_pct"],
                          per_week=ROUND_OPEN["per_week"], label="Round-open standing book",
                          months={m: v[0] for m, v in cbase["month_table"].items()})
        c165, _ = R10.run_r10("r10_c165_ws5_single_banked_regate", standing)
        print("C165 single-banking re-gate vs round-open done.")
        load_state()
    else:
        rec = {"name": "r10_c165_ws5_closure_statement", "cycle": 165, "scored": False,
               "reason": ("Freeze rule: combinations of Round-10 bankings only, and only bankings. "
                          "Round 10 banked nothing through Cycle 164 (WS1 agreement rejected; "
                          "WS1 mirror not run under the frozen rule; WS2 both cells rejected; "
                          "WS3 gated at Cycle 164), so there is no combination to re-gate."),
               "verdict": "CLOSED BY STATEMENT — no combinations."}
        Path(TR / "nifty_engine_run3r10_r10_c165_ws5_closure_summary.json").write_text(
            json.dumps(rec, indent=1, default=str))
        print("C165 closure by statement (no bankings).")

    # ---------- Cycle 166: WS4 December freeze — regeneration verification ----------
    regen, notes = R6.native_population(2, "09:55", True)
    base35 = R7.standing_legs()
    key = lambda l: (l["date"], l["direction"], l["entry_time"], int(l["strike"]), l["expiry"])
    same = sorted(map(key, regen)) == sorted(map(key, base35))
    c166, _ = R10.run_r10("r10_c166_ws4_regen_verify", regen, gate=False)
    cstand, _ = R10.run_r10("r10_c166_ws4_standing_rescore", standing, gate=False)
    ver = {"name": "r10_c166_ws4_december_freeze_verification", "cycle": 166,
           "regen_legs": len(regen), "base_legs": len(base35), "leg_for_leg_identical": same,
           "regen_total": c166["total"], "regen_n": c166["n"], "regen_nc": c166["not_computed"],
           "regen_resum_ok": c166["resum_ok"], "regen_audit": c166["timing_audit"],
           "standing_total_rescored": cstand["total"], "standing_n": cstand["n"],
           "native_population_notes": {k: str(v) for k, v in notes.items()},
           "specification": ("December candidate specification as frozen in the ROUND 10 freeze, "
                             "WS4 section (rules 1-9) of nifty_engine_frozen.md."),
           "verdict": ("VERIFIED" if (same and c166["total"] == 54102.00 and c166["not_computed"] == 0
                                      and c166["resum_ok"] and cstand["total"] == R6.CURRENT["total"])
                       else "MISMATCH — see fields")}
    Path(TR / "nifty_engine_run3r10_r10_c166_ws4_verification.json").write_text(
        json.dumps(ver, indent=1, default=str))
    print("C166 WS4 regeneration verification:", ver["verdict"],
          "| regen total", c166["total"], "| leg-identical:", same,
          "| standing re-scored:", cstand["total"])

    # ---------- Cycle 167: closure re-gate + flagged restatement ----------
    c167, _ = R10.run_r10("r10_c167_ws5_closure_regate", standing)
    skeys = R7.keys_of(standing)
    fade, _ = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                  with_trend=False, exclude_keys=skeys)
    fetch_missing(fade)
    c_fade, _ = R10.run_r10("r10_c167_restate_fade1005", standing + fade, force_no_bank=True)
    exp, _ = R8.expiry_sleeve_legs(skeys)
    fetch_missing(exp)
    c_exp, _ = R10.run_r10("r10_c167_restate_expiry", standing + exp, force_no_bank=True)
    fkeys = skeys | R7.keys_of(fade)
    exp2, _ = R8.expiry_sleeve_legs(fkeys)
    c_pair, _ = R10.run_r10("r10_c167_restate_pair", standing + fade + exp2, force_no_bank=True)
    combo, _ = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                   with_trend=True, exclude_keys=skeys)
    fetch_missing(combo)
    c_combo, _ = R10.run_r10("r10_c167_restate_fadecombo", standing + combo, force_no_bank=True)
    base_total = R6.CURRENT["total"]
    print("C167 flagged restatement (adoption values vs ending book "
          f"{base_total:+,.2f}): fade1005 {c_fade['total'] - base_total:+,.2f} | "
          f"expiry {c_exp['total'] - base_total:+,.2f} | pair {c_pair['total'] - base_total:+,.2f} | "
          f"fadecombo {c_combo['total'] - base_total:+,.2f}")

if __name__ == "__main__":
    main()
