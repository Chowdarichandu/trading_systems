#!/usr/bin/env python3
"""ROUND 8 stage 1: Cycle 141 validation + WS1 gap-fade refined
(Cycles 142-145). State (current standing legs + gate baseline) persists
in nifty_engine_r8_standing.json across stages. Freeze: ROUND 8 section
of nifty_engine_frozen.md. Nifty only, paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8

TR = Path.home() / "workspace/trading"
STATE = TR / "nifty_engine_r8_standing.json"

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
    # ---------- Cycle 141: validation ----------
    c141, _ = R7.run_r7("r8_c141_validate_standing", standing, gate=False)
    ok = (c141["total"] == 54102.00 and c141["n"] == 35 and c141["ft_pct"] == 34.3
          and c141["per_week"] == 0.86 and c141["not_computed"] == 0 and c141["resum_ok"]
          and c141["timing_audit"]["violations"] == 0)
    print("CYCLE 141 VALIDATION:", "VALID" if ok else "MISMATCH — STOP")
    if not ok: sys.exit(1)
    if not STATE.exists():
        save_state(standing, c141, "Round-6/7 standing book (Round-8 open)")
    standing, label = load_state()
    print(f"gate baseline: {label} = {R6.CURRENT['total']:+,.2f}, FT {R6.CURRENT['ft_pct']}%, "
          f"{R6.CURRENT['per_week']}/wk")

    # ---------- WS1 cycles 142-145 ----------
    cells = [
        ("r8_c142_ws1a_thr075", dict(threshold=0.0075)),
        ("r8_c143_ws1a_thr100", dict(threshold=0.0100)),
        ("r8_c144_ws1b_withtrend", dict(threshold=0.005, with_trend=True)),
        ("r8_c145_ws1c_entry1005", dict(threshold=0.005, entry_time="10:05")),
    ]
    for name, kw in cells:
        skeys = R7.keys_of(standing)
        sleeve, excluded = R8.gap_fade_legs_r8(exclude_keys=skeys, **kw)
        print(f"\n[{name}] sleeve legs {len(sleeve)}, excluded {len(excluded)}: {excluded}")
        fetch_missing(sleeve, weekly=False)
        combined = standing + sleeve
        c, _ = R7.run_r7(name, combined)
        banked = c.get("gate_relative", {}).get("banked", False)
        tot, res = R7.score_sleeve_alone(name + " sleeve", sleeve)
        print(f"  sleeve standalone {tot:+,.2f}; combined {c['total']:+,.2f}; "
              f"{'BANKED — supersession' if banked else 'not banked'}")
        if banked:
            standing = combined
            save_state(standing, c, f"standing after {name}")
            print(f"  standing book updated: {len(standing)} legs, {c['total']:+,.2f}")

if __name__ == "__main__":
    main()
