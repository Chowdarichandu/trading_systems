#!/usr/bin/env python3
"""RUN 3 ROUND 3 harness (2026-11-02 standing order, adopted-book work).
Extends the round-2 harness replay with a CONFIGURABLE BE arm level
(round-2 replay_g hardwires +50). Exact-tag candle loading (no glob
fallback). All comparisons measured against the ADOPTED book:
CH3-R x lock50/TGT2-175 = +114,921.75 (44 trades, FT 45.5%, 1.08/wk).
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE. Paper, real Rs0."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r2_harness import candles_exact, pool_sets
from nifty_engine_score import controls, nsrc

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65

ADOPTED_TOTAL = 114921.75
ADOPTED_FT = 45.5
ADOPTED_MONTHS = {"2026-01": 23974.75, "2026-02": 14882.25, "2026-03": 21650.0,
                  "2026-04": 7471.5, "2026-05": -2323.0, "2026-06": 7584.0,
                  "2026-07": 17054.5, "2026-08": -5187.25, "2026-09": 5020.0,
                  "2026-10": 24795.0}

def replay_r3(cs, entry_time, lock=50.0, tgt2=175.0, arm=50.0, delay_bars=0):
    """Adopted-book geometry with configurable lock / TGT2 / BE arm.
    stop -50, tgt1 +90, stop before target, square-off 15:10.
    Identical bar-order semantics to round-2 replay_g (validated)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == "15:10": return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == "15:10":
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_r3(legs, lock=50.0, tgt2=175.0, arm=50.0, delay_bars=0, geom_by_leg=None):
    res, nc, nc_legs = [], 0, []
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"])); continue
        lk, t2, ar = (geom_by_leg(l) if geom_by_leg else (lock, tgt2, arm))
        r = replay_r3(cs, l["entry_time"], lock=lk, tgt2=t2, arm=ar, delay_bars=delay_bars)
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"])); continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"]})
    return res, nc, nc_legs

def audit_exact(legs):
    bad = checked = 0
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs or not any(b[0] == l["entry_time"] for b in cs): bad += 1
        else: checked += 1
    return {"checked": checked, "violations": bad}

def gate_r3(c):
    """Banking gate vs the ADOPTED book (pre-registered in frozen.md,
    Run 3 Round 3 section, before any round-3 scoring)."""
    g2r = [m for m, v in ADOPTED_MONTHS.items()
           if v > 0 and c["month_table"].get(m, [0, 0])[0] < 0]
    checks = {
        "net_above_adopted": c["total"] > ADOPTED_TOTAL,
        "ft_not_collapsed>=42.0": c["ft_pct"] >= 42.0,
        "no_green_month_flips_red": not g2r,
        "no_red_month_ends": not c["red_month_ends"],
        "halves_both>=0": c["halves"]["Jan-May"] >= 0 and c["halves"]["Jun-Oct"] >= 0,
        "placebo_beaten": c["placebo_shift30_total"] is not None and c["total"] > c["placebo_shift30_total"],
        "timing_audit_clean": c["timing_audit"]["violations"] == 0,
        "not_computed_zero": c["not_computed"] == 0,
        "resum_exact": bool(c["resum_ok"]),
        "frequency>=1.00/wk": c["per_week"] >= 1.00,
    }
    return all(checks.values()), checks, g2r

def run_r3(name, legs, lock=50.0, tgt2=175.0, arm=50.0, geom_by_leg=None, save=True, quiet=False):
    res, nc, nc_legs = score_r3(legs, lock=lock, tgt2=tgt2, arm=arm, geom_by_leg=geom_by_leg)
    pl, _, _ = score_r3(legs, lock=lock, tgt2=tgt2, arm=arm, delay_bars=6, geom_by_leg=geom_by_leg)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = nc_legs
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    ok, checks, g2r = gate_r3(c)
    c["gate_vs_adopted"] = {"banked": ok, "checks": checks, "green_to_red": g2r}
    if save:
        Path(TR / f"nifty_engine_{name}_summary.json").write_text(json.dumps(c, indent=1, default=str))
    if not quiet:
        print(f"[{name}] TOTAL {c['total']:+,.2f} | n {c['n']} | FT {c['ft_pct']}% | {c['per_week']}/wk | "
              f"halves {c['halves']['Jan-May']:+,.2f}/{c['halves']['Jun-Oct']:+,.2f} | placebo {c['placebo_shift30_total']:+,.2f} | "
              f"exT3 {c['ex_top3']:+,.2f} | May {c['may']:+,.2f} | Aug {c['august']:+,.2f} | "
              f"audit {c['timing_audit']['checked']}/{c['timing_audit']['violations']} | resum {c['resum_ok']} | NC {c['not_computed']} | "
              f"GATE {'BANKED' if ok else 'FAIL ' + str([k for k, v in checks.items() if not v])}")
    return c, res

def adopted_set():
    _, _, EXP0 = pool_sets()
    CH3R = [l for l in EXP0 if not (nsrc(l) >= 2 and l["entry_time"] > "09:55")]
    DIFF = [l for l in EXP0 if (nsrc(l) >= 2 and l["entry_time"] > "09:55")]
    return EXP0, CH3R, DIFF

if __name__ == "__main__" and "--validate" in sys.argv:
    EXP0, CH3R, DIFF = adopted_set()
    # 1) adopted book exact reproduction
    res, nc, _ = score_r3(CH3R, lock=50.0, tgt2=175.0, arm=50.0)
    tot = round(sum(r["net"] for r in res), 2)
    ft = round(100.0 * sum(r["ft"] for r in res) / len(res), 1)
    print(f"adopted CH3R lock50/175 arm50: n={len(res)} total={tot} FT={ft} NC={nc} (expect 44 / 114921.75 / 45.5 / 0)")
    assert len(res) == 44 and tot == 114921.75 and ft == 45.5 and nc == 0
    # 2) incumbent banked book (cycle 30 geometry on EXP0)
    res, nc, _ = score_r3(EXP0, lock=50.0, tgt2=175.0, arm=50.0)
    tot = round(sum(r["net"] for r in res), 2)
    print(f"incumbent EXP0 lock50/175 arm50: n={len(res)} total={tot} NC={nc} (expect 59 / 98209.0 / 0)")
    assert len(res) == 59 and tot == 98209.0 and nc == 0
    # 3) incumbent Run-2 geometry (lock75/180) for cross-check
    res, nc, _ = score_r3(EXP0, lock=75.0, tgt2=180.0, arm=50.0)
    tot = round(sum(r["net"] for r in res), 2)
    print(f"incumbent EXP0 lock75/180 arm50: n={len(res)} total={tot} NC={nc} (expect 59 / 98001.0 / 0)")
    assert len(res) == 59 and tot == 98001.0 and nc == 0
    print("R3 HARNESS VALID")
