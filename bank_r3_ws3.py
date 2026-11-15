#!/usr/bin/env python3
"""ROUND 3 WORKSTREAM 3 (Cycles 53-57): execution optimisation on the v16
legs. Definitions frozen in bank_engine_frozen.md (ROUND 3 appendix):
EC-A entry at the frozen entry bar's CLOSE (scan from the next bar),
EC-B entry at the NEXT bar's OPEN (scan from that bar), SQ-1445/1500/1520
square-off moves. Segment follows the variant's own entry premium with the
frozen anchored state; expiry-day legs keep plain (-50/+90). Placebo =
+30 min in the same convention. Sanity asserted in-run: the frozen
convention (open entry, 15:10) reproduces v16 to the paisa, main + placebo."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_cycle import _entry_premium
from bank_r2_core import controls, gate, seg_of, write_trades, LOT, COST
from bank_r2_ns1 import V15
from bank_r2_expiry import KEYS, STATES, LBK
from bank_r3_core import REF16, BASE_ROWS, BASE_PROWS

TR = Path.home() / "workspace/trading"

def replay_x(cs, entry_time, delay, p, mode, sq):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if mode == "open":
        if i0 >= len(cs): return None
        entry = cs[i0][1]; start = i0
    elif mode == "close":
        if i0 >= len(cs): return None
        entry = cs[i0][4]; start = i0 + 1
    elif mode == "nextopen":
        if i0 + 1 >= len(cs): return None
        entry = cs[i0 + 1][1]; start = i0 + 1
    if start >= len(cs) or cs[start][0] > sq:
        return None
    stop, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[start:]
    if not bars:
        return mk(entry, "square_off", cs[i0][0], 0)
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        if l <= stop:
            return mk(stop, "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2:
                    rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2:
                    rest = (tgt2, "runner_target", t2); break
                if t2 == sq:
                    rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if t == sq:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

def build_x(mode, sq, delay=0):
    rows, nc = [], 0
    for key in KEYS[delay]:
        l = LBK[key]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        # segment premium = the variant's UNDELAYED entry premium (the
        # build_geo precedent: segment from the reference entry premium,
        # state from the run's own delay stream)
        probe = replay_x(cs, l["entry_time"], 0,
                         dict(stop=50.0, trig=90.0, lock=None, tgt2=None), mode, sq)
        if probe is None: nc += 1; continue
        new_ep = probe["entry"]
        seg = seg_of(new_ep, *STATES[delay].get(key, (0, 0.0)))
        p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None) if l["date"] == l["expiry"] else V15[seg]
        r = replay_x(cs, l["entry_time"], delay, p, mode, sq)
        if r is None: nc += 1; continue
        rows.append({**r, "date": l["date"], "direction": l["direction"],
                     "family": l["family"], "rep": l["rep"],
                     "entry_time": l["entry_time"], "leg_key": key, "segment": seg})
    return sorted(rows, key=lambda x: (x["date"], x["entry_time"])), nc

def judge_x(label, mode, sq, write=None):
    rows, nc = build_x(mode, sq, delay=0)
    prows, pnc = build_x(mode, sq, delay=6)
    c = controls(rows, nc, LBK, prows, pnc)
    resum = None
    if write:
        resum = write_trades(rows, write)
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, why = gate(c, REF16, resum=resum)
    print(f"{label}: net={c['net']:+,.2f} n={c['n']} FT90={c['ft90_pct']} "
          f"placebo={c['placebo']['net']:+,.2f} nc={nc}/{pnc} banked={ok} why={why}")
    return dict(label=label, mode=mode, sq=sq, controls=c, banked=ok, gate_why=why)

def main():
    base, bnc = build_x("open", "15:10", delay=0)
    assert bnc == 0 and len(base) == len(BASE_ROWS)
    same = all(any(a["leg_key"] == b["leg_key"] and abs(a["net"] - b["net"]) < 0.005
                   and a["exit_time"] == b["exit_time"] for b in BASE_ROWS) for a in base)
    assert same and abs(sum(r["net"] for r in base) - 106517.00) < 0.005, "frozen-convention reproduction FAILED"
    pbase, _ = build_x("open", "15:10", delay=6)
    assert abs(sum(r["net"] for r in pbase) - sum(r["net"] for r in BASE_PROWS)) < 0.005
    print("sanity: frozen convention reproduces v16 exactly (main + placebo)")
    results = {}
    for label, mode, sq in [("Cycle 53 EC-A close entry", "close", "15:10"),
                            ("Cycle 54 EC-B next-bar open", "nextopen", "15:10"),
                            ("Cycle 55 SQ-1445", "open", "14:45"),
                            ("Cycle 56 SQ-1500", "open", "15:00"),
                            ("Cycle 57 SQ-1520", "open", "15:20")]:
        results[label] = judge_x(label, mode, sq)
    (TR / "bank_r3_ws3_results.json").write_text(json.dumps(results, indent=1, default=str))
    print("results -> bank_r3_ws3_results.json")

if __name__ == "__main__":
    main()
