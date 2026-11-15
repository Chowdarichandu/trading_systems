#!/usr/bin/env python3
"""ROUND 9 stage 2: Cycle 154 WS3 conditional candidate (separator F8,
frozen in nifty_engine_frozen.md after the Cycle-153 diagnosis) +
Cycle 155 WS4 causal union + WS5 Cycles 156-158 (combination/closure,
freeze verification, flagged restatement). Nifty only, paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
import nifty_engine_r9_harness as R9
from nifty_engine_r4_harness import DAILY, PREV

TR = Path.home() / "workspace/trading"
STATE = TR / "nifty_engine_r9_standing.json"

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

def gap_of(d):
    p = PREV.get(d)
    if not p: return None
    return DAILY[d]["o"] / DAILY[p]["c"] - 1.0

def main():
    standing, label = load_state()
    print(f"gate baseline: {label} = {R6.CURRENT['total']:+,.2f}, FT {R6.CURRENT['ft_pct']}%, "
          f"{R6.CURRENT['per_week']}/wk")
    banked_any = False

    # ---------- Cycle 154: WS3 candidate (F8 exclusion) ----------
    dropped = [l for l in standing if (gap_of(l["date"]) is not None and abs(gap_of(l["date"])) >= 0.005)]
    kept = [l for l in standing if l not in dropped]
    print(f"\n[r9_c154_ws3_f8_exclusion] dropping {len(dropped)} legs with |gap| >= 0.50%:")
    for l in dropped:
        print(f"   dropped {l['date']} {l['direction']} entry {l['entry_time']} gap {gap_of(l['date'])*100:+.3f}% src={l['sources']}")
    c154, _ = R9.run_r9("r9_c154_ws3_f8_exclusion", kept)
    b154 = c154.get("gate_relative", {}).get("banked", False)
    print(f"  candidate {'BANKS (exclusion adopted as standing)' if b154 else 'not banked'}")
    if b154:
        banked_any = True
        standing = kept
        save_state(standing, c154, "standing after r9_c154_ws3_f8_exclusion")
    standing, label = load_state()
    print(f"gate baseline now: {label} = {R6.CURRENT['total']:+,.2f}")

    # ---------- Cycle 155: WS4 causal union ----------
    skeys = R7.keys_of(standing)
    ulegs, uex = R9.union_legs(skeys)
    print(f"\n[r9_c155_ws4_causal_union] union legs {len(ulegs)}, excluded {len(uex)}: {uex}")
    for l in ulegs:
        print(f"   union {l['date']} {l['direction']} entry {(l['entry_time'])} strike {l['strike']} src={l['sources']}")
    fetch_missing(ulegs, weekly=False)
    combined = standing + ulegs
    c155, _ = R9.run_r9("r9_c155_ws4_causal_union", combined)
    b155 = c155.get("gate_relative", {}).get("banked", False)
    tot, _ = R9.score_sleeve_alone("r9_c155 union sleeve", ulegs)
    print(f"  union standalone {tot:+,.2f}; combined {c155['total']:+,.2f}; "
          f"{'BANKED — supersession' if b155 else 'not banked'}")
    if b155:
        banked_any = True
        standing = combined
        save_state(standing, c155, "standing after r9_c155_ws4_causal_union")
    standing, label = load_state()
    print(f"gate baseline now: {label} = {R6.CURRENT['total']:+,.2f}")

    # ---------- Cycle 156: WS5 combination / closure re-gate ----------
    # Chained bankings (if any) already accumulate in the standing book
    # under supersession; re-gate the standing book vs the ROUND-OPEN
    # baseline as the combination/closing record (Round-6 C130 pattern).
    open_months = {"2026-01": 17096.75, "2026-02": 12789.25, "2026-03": 7895.00,
                   "2026-04": 210.00, "2026-05": -10410.00, "2026-06": -3910.00,
                   "2026-07": 10998.75, "2026-08": -1701.00, "2026-09": 4652.75,
                   "2026-10": 16480.50}
    R6.CURRENT.update(total=54102.00, ft_pct=34.3, per_week=0.86,
                      label="Round-6/7/8 standing book (Round-9 open)", months=open_months)
    print(f"\n[r9_c156_ws5_closure] banked_any={banked_any}; re-gating standing vs round-open baseline")
    c156, _ = R9.run_r9("r9_c156_ws5_closure", standing)
    standing, label = load_state()

    # ---------- Cycle 157: candidate freeze verification ----------
    c157, _ = R9.run_r9("r9_c157_freeze_verify", standing, gate=False)
    ok157 = (c157["not_computed"] == 0 and c157["resum_ok"]
             and c157["timing_audit"]["violations"] == 0
             and abs(c157["total"] - R6.CURRENT["total"]) < 0.005)
    print(f"CYCLE 157 FREEZE VERIFICATION: {'OK' if ok157 else 'MISMATCH'} "
          f"(total {c157['total']:+,.2f} vs state {R6.CURRENT['total']:+,.2f})")

    # ---------- Cycle 158: flagged restatement on the ending book ----------
    ekeys = R7.keys_of(standing)
    R6.CURRENT.update(total=c157["total"], ft_pct=c157["ft_pct"], per_week=c157["per_week"],
                      label="ending standing book (Round-9 close)", months={m: v[0] for m, v in c157["month_table"].items()})
    fade, _ = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05", with_trend=False, exclude_keys=ekeys)
    fetch_missing(fade, weekly=False)
    c158a, _ = R9.run_r9("r9_c158_restate_fade145", standing + fade, force_no_bank=True)
    exp_legs, _ = R8.expiry_sleeve_legs(ekeys)
    fetch_missing(exp_legs, weekly=True)
    c158b, _ = R9.run_r9("r9_c158_restate_expiry", standing + exp_legs, force_no_bank=True)
    exp2, _ = R8.expiry_sleeve_legs(ekeys | R7.keys_of(fade))
    c158c, _ = R9.run_r9("r9_c158_restate_pair", standing + fade + exp2, force_no_bank=True)
    print(f"  RESTATED adoption values on ending book ({c157['total']:+,.2f}): "
          f"fade145 {c158a['total'] - c157['total']:+,.2f} | expiry {c158b['total'] - c157['total']:+,.2f} | "
          f"pair {c158c['total'] - c157['total']:+,.2f}")

if __name__ == "__main__":
    main()
