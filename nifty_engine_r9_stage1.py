#!/usr/bin/env python3
"""ROUND 9 stage 1: Cycle 150 validation + Cycle 151 WS1 (fade's last
cell) + Cycle 152 WS2 (flagged-pair gate, DECISION SUPPORT force-no-bank).
State persists in nifty_engine_r9_standing.json. Freeze: ROUND 9 section
of nifty_engine_frozen.md. Nifty only, paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
import nifty_engine_r9_harness as R9

TR = Path.home() / "workspace/trading"
STATE = TR / "nifty_engine_r9_standing.json"
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

def set_current_open(c141):
    R6.CURRENT.update(total=ROUND_OPEN["total"], ft_pct=ROUND_OPEN["ft_pct"],
                      per_week=ROUND_OPEN["per_week"],
                      label="Round-6/7/8 standing book (Round-9 open)",
                      months={m: v[0] for m, v in c141["month_table"].items()})

def fetch_missing(legs, weekly=False):
    miss = R7.missing_candles(legs)
    if not miss: return
    print(f"  fetching {len(miss)} missing contracts (weekly={weekly}) ...")
    import nifty_engine_r7_fetch as F
    jobs = [(st, ty, d, exp, weekly) for (st, ty, d, exp) in miss]
    out = F.fetch_jobs(jobs)
    ok = sum(1 for _, r in out if isinstance(r, tuple) and r[0] not in ("NO_CONTRACTS_FILE",) and r[1])
    print(f"  fetch done: {ok}/{len(jobs)} returned candles")
    still = R7.missing_candles(legs)
    print(f"  still missing after fetch: {len(still)} {still if still else ''}")

def main():
    standing = R7.standing_legs()
    # ---------- Cycle 150: validation ----------
    c150, _ = R9.run_r9("r9_c150_validate_standing", standing, gate=False)
    ok = (c150["total"] == 54102.00 and c150["n"] == 35 and c150["ft_pct"] == 34.3
          and c150["per_week"] == 0.86 and c150["not_computed"] == 0 and c150["resum_ok"]
          and c150["timing_audit"]["violations"] == 0)
    print("CYCLE 150 VALIDATION:", "VALID" if ok else "MISMATCH — STOP")
    if not ok: sys.exit(1)
    if not STATE.exists():
        save_state(standing, c150, "Round-6/7/8 standing book (Round-9 open)")
    set_current_open(c150)
    standing, label = load_state()
    print(f"gate baseline: {label} = {R6.CURRENT['total']:+,.2f}, FT {R6.CURRENT['ft_pct']}%, "
          f"{R6.CURRENT['per_week']}/wk")

    # ---------- Cycle 151: WS1 fade's last cell ----------
    skeys = R7.keys_of(standing)
    sleeve, excluded = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                           with_trend=True, exclude_keys=skeys)
    print(f"\n[r9_c151_ws1_fade_combo] sleeve legs {len(sleeve)}, excluded {len(excluded)}: {excluded}")
    fetch_missing(sleeve, weekly=False)
    combined = standing + sleeve
    c151, _ = R9.run_r9("r9_c151_ws1_fade_combo", combined)
    banked = c151.get("gate_relative", {}).get("banked", False)
    tot, _ = R9.score_sleeve_alone("r9_c151 sleeve", sleeve)
    print(f"  sleeve standalone {tot:+,.2f}; combined {c151['total']:+,.2f}; "
          f"{'BANKED — supersession' if banked else 'not banked'}")
    if banked:
        standing = combined
        save_state(standing, c151, "standing after r9_c151_ws1_fade_combo")
        print(f"  standing book updated: {len(standing)} legs, {c151['total']:+,.2f}")
    standing, label = load_state()
    print(f"gate baseline now: {label} = {R6.CURRENT['total']:+,.2f}")

    # ---------- Cycle 152: WS2 flagged-pair gate (DECISION SUPPORT) ----------
    # Always vs the ROUND-OPEN book (freeze): prices the owner's recorded
    # decision on the two flagged items. NEVER banks.
    open_legs = R7.standing_legs()
    okeys = R7.keys_of(open_legs)
    set_current_open(c150)
    fade, fex = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                                    with_trend=False, exclude_keys=okeys)
    print(f"\n[r9_c152_ws2_pair] fade legs {len(fade)}, excluded {len(fex)}: {fex}")
    fetch_missing(fade, weekly=False)
    exp_legs, eex = R8.expiry_sleeve_legs(okeys | R7.keys_of(fade))
    print(f"[r9_c152_ws2_pair] expiry legs {len(exp_legs)}, excluded {len(eex)}: {eex}")
    fetch_missing(exp_legs, weekly=True)
    pair = open_legs + fade + exp_legs
    c152, _ = R9.run_r9("r9_c152_ws2_flagged_pair", pair, force_no_bank=True)
    gr = c152.get("gate_relative", {})
    print(f"  PAIR total {c152['total']:+,.2f}; adoption value vs round-open book "
          f"{c152['total'] - 54102.00:+,.2f}; gate banked-flag (DS only): {gr.get('banked')}; "
          f"failing legs: {[k for k, v in gr.get('checks', {}).items() if not v]}; "
          f"green-to-red flips: {gr.get('green_to_red')}")
    ftot, _ = R9.score_sleeve_alone("r9_c152 fade sleeve", fade)
    etot, _ = R9.score_sleeve_alone("r9_c152 expiry sleeve", exp_legs)
    print(f"  fade standalone {ftot:+,.2f} (expect +33,624.75); expiry standalone {etot:+,.2f} (expect +3,651.75)")
    # restore CURRENT to the live standing state for later stages
    standing, label = load_state()
    print(f"gate baseline restored: {label} = {R6.CURRENT['total']:+,.2f}")

if __name__ == "__main__":
    main()
