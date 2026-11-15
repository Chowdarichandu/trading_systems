#!/usr/bin/env python3
"""ROUND 3 WORKSTREAM 4 (Cycles 58-63): combinations. The Round-3 banking
(v17 = v16 with square-off 15:20, Cycle 57) becomes the base; the
net-positive-but-unbanked families and (for completeness) the two rejected
WS1 families are re-judged as add-ons ON v17 — add-on exits take the v17
assembly including square-off 15:20 (replay_x, verified identical to
gen_replay at 15:10). Gate vs v17 controls. Sequential admission for the
grand stack: NS3, then S3-A, then S3-E, then S3-D."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_cycle import _entry_premium
from bank_r2_core import controls, gate, seg_of, write_trades
from bank_r2_ns1 import V15
from bank_r3_core import state_at, admit, BASE_KEYS
from bank_r3_ws1 import build as build_ws1
from bank_r3_setups import generate
from bank_r3_ws3 import build_x, replay_x

TR = Path.home() / "workspace/trading"
SQ = "15:20"
V17_ROWS, _ = build_x("open", SQ, delay=0)
V17_PROWS, _ = build_x("open", SQ, delay=6)
assert abs(sum(r["net"] for r in V17_ROWS) - 107930.00) < 0.005
from bank_r2_expiry import LBK
V17_KEYS = {(r["date"], r["direction"]) for r in V17_ROWS}
REF17 = controls(V17_ROWS, 0, LBK, V17_PROWS, 0)

def score_addons_sq(admitted, delay=0):
    rows, nc = [], 0
    for l in admitted:
        ep = _entry_premium(l)
        et = l["entry_time"]
        if delay:
            cs0 = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
            times = [b[0] for b in cs0] if cs0 else []
            if et not in times: nc += 1; continue
            i = times.index(et) + delay
            if i >= len(times): nc += 1; continue
            et_state = times[i]
        else:
            et_state = et
        n, tnet = state_at(l["date"], et_state, delay=delay)
        seg = seg_of(ep, n, tnet)
        p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None) if l["date"] == l["expiry"] else V15[seg]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = replay_x(cs, l["entry_time"], delay, p, "open", SQ)
        if r is None: nc += 1; continue
        rows.append({**r, "date": l["date"], "direction": l["direction"],
                     "family": l["family"], "rep": l["rep"],
                     "entry_time": l["entry_time"],
                     "leg_key": (l["date"], l["direction"], l["entry_time"]),
                     "segment": seg})
    return rows, nc

def judge_on(label, fam_leg_sets, write=None):
    """fam_leg_sets: list of leg lists, admitted sequentially (each family's
    keys are blocked by the base and by earlier families' admitted keys)."""
    taken = set(V17_KEYS)
    all_admitted, all_rows, all_prows = [], [], []
    detail = []
    for legs in fam_leg_sets:
        admitted, kd, bd, ncl = admit(legs, taken)
        taken |= {(l["date"], l["direction"]) for l in admitted}
        rows, nc = score_addons_sq(admitted, delay=0)
        prows, pnc = score_addons_sq(admitted, delay=6)
        all_admitted += admitted; all_rows += rows; all_prows += prows
        detail.append(dict(family=legs[0]["family"] if legs else "?",
                           admitted=len(admitted), net=round(sum(r["net"] for r in rows), 2),
                           nc_legs=len(ncl)))
    book = sorted(V17_ROWS + all_rows, key=lambda x: (x["date"], x["entry_time"]))
    pbook = sorted(V17_PROWS + all_prows, key=lambda x: (x["date"], x["entry_time"]))
    lbk = dict(LBK)
    for l in all_admitted:
        lbk[(l["date"], l["direction"], l["entry_time"])] = l
    nc_tot = 0
    c = controls(book, nc_tot, lbk, pbook, 0)
    resum = None
    if write:
        resum = write_trades(book, write)
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, why = gate(c, REF17, resum=resum)
    print(f"{label}: book_net={c['net']:+,.2f} n={c['n']} FT90={c['ft90_pct']} "
          f"placebo={c['placebo']['net']:+,.2f} banked={ok} why={why} detail={detail}")
    return dict(label=label, controls=c, banked=ok, gate_why=why, detail=detail)

def main():
    ns3 = build_ws1("index_options_newsetup_ns3_trades_jan_oct_2026.csv", "NS3_gapclass", "NS3")
    ns5a = build_ws1("index_options_newsetup_ns5a_trades_jan_oct_2026.csv", "NS5A_skillrescan", "NS5a")
    ns5b = build_ws1("index_options_newsetup_ns5b_trades_jan_oct_2026.csv", "NS5B_ce_mirror_rescan", "NS5b")
    gen = generate()
    results = {}
    results["C58"] = judge_on("Cycle 58 v17+NS3", [ns3])
    results["C59"] = judge_on("Cycle 59 v17+S3-A", [gen["S3A"]])
    results["C60"] = judge_on("Cycle 60 v17+S3-E", [gen["S3E"]])
    results["C61"] = judge_on("Cycle 61 v17+NS5a", [ns5a])
    results["C62"] = judge_on("Cycle 62 v17+NS5b", [ns5b])
    results["C63"] = judge_on("Cycle 63 v17+NS3+S3A+S3E+S3D",
                              [ns3, gen["S3A"], gen["S3E"], gen["S3D"]])
    (TR / "bank_r3_ws4_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r3_ws4_results.json")

if __name__ == "__main__":
    main()
