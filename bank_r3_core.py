#!/usr/bin/env python3
"""ROUND 3 core (BANKNIFTY ONLY). Definitions frozen in bank_engine_frozen.md
(ROUND 3 appendix) BEFORE any Round-3 scoring.

- Base book = v16 via bank_r2_expiry.build_geo((50,90)) — asserted verbatim.
- Add-on admission: (date,direction) key unused by the current best book,
  entry premium outside [400,550), premium candles exist; earliest leg per
  key per family. Unfetchable legs are NOT_COMPUTED (excluded, named).
- Add-on exits: v16 assembly; segment state = anchored trailing-10 over the
  book-v4 scored stream (Cycle-11/18 definition), base stream only.
- Controls/gate: bank_r2_core.controls + gate, ref = current best book."""
import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_cycle import _entry_premium
from bank_engine_run2 import book_v4_legs, score_all
from bank_r2_core import controls, gate, seg_of, gen_replay
from bank_r2_ns1 import V15
from bank_r2_expiry import build_geo

TR = Path.home() / "workspace/trading"
BAND = (400.0, 550.0)

# ---------- base book v16 ----------
BASE_ROWS, _nc, LBK16 = build_geo((50.0, 90.0), 0)
BASE_PROWS, _pnc, _ = build_geo((50.0, 90.0), 6)
assert len(BASE_ROWS) == 82 and abs(sum(r["net"] for r in BASE_ROWS) - 106517.00) < 0.005
BASE_KEYS = {(r["date"], r["direction"]) for r in BASE_ROWS}
REF16 = controls(BASE_ROWS, 0, LBK16, BASE_PROWS, 0)

# ---------- anchored state streams (book-v4 scored stream, Cycles 11/18) ----
_STREAMS = {}
def _stream(delay):
    if delay not in _STREAMS:
        scored, _ = score_all(book_v4_legs(), delay=delay)
        _STREAMS[delay] = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    return _STREAMS[delay]

def state_at(date, entry_time, delay=0):
    """(n_known, trailing-10 net) of base-stream legs whose outcomes are
    known at (date, entry_time): signalled on an earlier date, or the same
    date with exit_time <= entry_time. Window = last 10 such legs."""
    known = [s for s in _stream(delay)
             if s["date"] < date or (s["date"] == date and s["exit_time"] <= entry_time)]
    last = known[-10:]
    return len(last), round(sum(x["net"] for x in last), 2)

# ---------- add-on admission + scoring ----------
def _delayed_entry_time(leg, delay):
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    if not cs: return None
    times = [b[0] for b in cs]
    if leg["entry_time"] not in times: return None
    i = times.index(leg["entry_time"]) + delay
    return times[i] if i < len(times) else None

def admit(legs, taken_keys):
    """Split candidate legs into admitted / key-dropped / band-dropped /
    NOT_COMPUTED. Earliest leg per (date,direction) key per family wins."""
    seen, admitted, kd, bd, nc = set(), [], [], [], []
    for l in sorted(legs, key=lambda x: (x["date"], x["entry_time"])):
        key = (l["date"], l["direction"])
        if key in seen: continue
        seen.add(key)
        if key in taken_keys: kd.append(l); continue
        ep = _entry_premium(l)
        if ep is None: nc.append(l); continue
        if BAND[0] <= ep < BAND[1]: bd.append(l); continue
        admitted.append(l)
    return admitted, kd, bd, nc

def score_addons(admitted, delay=0):
    """Score admitted add-on legs under the v16 exit assembly."""
    rows, nc = [], 0
    for l in admitted:
        ep = _entry_premium(l)
        et = l["entry_time"] if delay == 0 else _delayed_entry_time(l, delay)
        if et is None: nc += 1; continue
        n, tnet = state_at(l["date"], et, delay=delay)
        seg = seg_of(ep, n, tnet)
        if l["date"] == l["expiry"]:
            p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
        else:
            p = V15[seg]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = gen_replay(cs, l["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        rows.append({**r, "date": l["date"], "direction": l["direction"],
                     "family": l["family"], "rep": l["rep"],
                     "entry_time": l["entry_time"],
                     "leg_key": (l["date"], l["direction"], l["entry_time"]),
                     "segment": seg})
    return rows, nc

def combined(base_rows, addon_rows):
    return sorted(base_rows + addon_rows, key=lambda x: (x["date"], x["entry_time"]))

def lbk_ext(extra_legs):
    lbk = dict(LBK16)
    for l in extra_legs:
        lbk[(l["date"], l["direction"], l["entry_time"])] = l
    return lbk

def judge(label, addon_legs, ref=REF16, write=None):
    """Full Round-3 judging of one add-on family against the current best
    (base = v16 rows): admission, scoring (main + placebo), controls, gate.
    Returns a result dict; writes the combined trades file if asked."""
    admitted, kd, bd, ncl = admit(addon_legs, BASE_KEYS)
    rows, nc = score_addons(admitted, delay=0)
    prows, pnc = score_addons(admitted, delay=6)
    book = combined(BASE_ROWS, rows)
    pbook = combined(BASE_PROWS, prows)
    lbk = lbk_ext(admitted)
    c = controls(book, nc, lbk, pbook, pnc)
    resum = None
    if write:
        from bank_r2_core import write_trades
        resum = write_trades(book, write)
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, why = gate(c, ref, resum=resum)
    fam_net = round(sum(r["net"] for r in rows), 2)
    res = dict(label=label, candidates=len(addon_legs), key_dropped=len(kd),
               band_dropped=len(bd), not_computed_legs=[f"{l['date']} {l['direction']} {l['entry_time']} {l['rep']}" for l in ncl],
               admitted=len(admitted), scored_nc=nc, family_net=fam_net,
               controls=c, banked=ok, gate_why=why)
    if write:
        res["trades_file"] = write
    print(f"{label}: cand={len(addon_legs)} key_drop={len(kd)} band_drop={len(bd)} "
          f"NC={len(ncl)} admitted={len(admitted)} fam_net={fam_net:+,.2f} "
          f"book_net={c['net']:+,.2f} banked={ok} why={why}")
    return res

if __name__ == "__main__":
    print("v16 reproduced:", REF16["net"], REF16["n"], "FT90", REF16["ft90_pct"],
          "placebo", REF16["placebo"]["net"], "OK")
