#!/usr/bin/env python3
"""ROUND 2 core (BANKNIFTY ONLY): generalised exit replay + book builders +
full controls + banking gate. Definitions frozen in bank_engine_frozen.md
(ROUND 2 appendix, 2026-11-02, before scoring).
Conventions inherited exactly: premiums per 1 lot (30), cost Rs220/trade,
UNIQUE-ONCE, entry = open of the 5-min option candle at the entry bar,
stop checked before target on every bar incl. entry bar, square-off 15:10,
placebo = identical construction with entries delayed +30 min (6 bars)."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, agg, month_end_reds
from bank_engine_run2 import book_v4_legs, score_all, trailing_state
from bank_engine_run2_cycle14 import stream_keys
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_cycle import _entry_premium, FILTERS

TR = Path.home() / "workspace/trading"
COST, LOT, WEEKS = 220.0, 30, 40.6

# ---------- generalised replay ----------
def gen_replay(cs, entry_time, delay=0, stop_pts=50.0, trig_pts=90.0,
               lock_pts=None, tgt2_pts=None):
    """Runner when tgt2_pts is not None (lock None = stop stays at phase-1
    stop in phase 2); plain target exit when both lock and tgt2 are None.
    Mirrors bank_engine_run2_cycle16.runner_replay / cycle14.be_replay
    bar-order semantics exactly at the frozen parameters."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, trig = entry - stop_pts, entry + trig_pts
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= stop:
            return mk(stop, "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if lock_pts is None and tgt2_pts is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + lock_pts if lock_pts is not None else stop
            tgt2 = entry + tgt2_pts if tgt2_pts is not None else None
            rest = None
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2:
                    rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2:
                    rest = (tgt2, "runner_target", t2); break
                if t2 == "15:10":
                    rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        if t == "15:10":
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

# ---------- book parameterisation ----------
V14 = {"lt400": dict(stop=50.0, trig=90.0, lock=75.0, tgt2=330.0),
       "ge400_warm": dict(stop=50.0, trig=90.0, lock=90.0, tgt2=180.0),
       "ge400_cold": dict(stop=50.0, trig=90.0, lock=None, tgt2=None)}
V8 = {"lt400": dict(stop=50.0, trig=90.0, lock=75.0, tgt2=180.0),
      "ge400_warm": dict(stop=50.0, trig=90.0, lock=75.0, tgt2=180.0),
      "ge400_cold": dict(stop=50.0, trig=90.0, lock=None, tgt2=None)}

def seg_of(ep, n_known, trail_net):
    if ep is not None and ep < 400.0: return "lt400"
    warm = (n_known < 10) or (trail_net >= 0)
    return "ge400_warm" if warm else "ge400_cold"

def rescore_keys(keys, legs_by_key, states, params, delay=0):
    out, nc = [], 0
    for key in keys:
        l = legs_by_key[key]
        ep = _entry_premium(l)
        seg = seg_of(ep, *states.get(key, (0, 0.0)))
        p = params[seg]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = gen_replay(cs, l["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        out.append({**r, "date": l["date"], "direction": l["direction"],
                    "family": l["family"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "leg_key": key, "segment": seg})
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc

def build_fixed(params, delay=0):
    """Fixed v14 stream (book-v4 legs + cold-(lA) skip), exits = params."""
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=delay)
    states = anchored_states(delay=delay)
    rows, nc = rescore_keys(keys, legs_by_key, states, params, delay=delay)
    return rows, nc, legs_by_key

def build_pool(candidate_legs, params, delay=0):
    """Pool-variant book: unique-once -> B2-style NS1-CE block -> premium
    band [400,550) block -> v4-scored stream -> anchored states ->
    cold-(lA) skip -> rescore taken legs with params."""
    from aggressive_score import unique_once
    pooled = unique_once(candidate_legs)
    pooled = FILTERS["drop_ns1_ce"](pooled)
    pooled = FILTERS["drop_prem_400_550"](pooled)
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in pooled}
    scored, nc0 = score_all(pooled, delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    states, taken_keys = {}, []
    for row in stream:
        n, net, _ = trailing_state(stream, row)
        states[row["leg_key"]] = (n, net)
        if not (n >= 10 and net < 0 and row["rep"] == "(lA) v2"):
            taken_keys.append(row["leg_key"])
    rows, nc = rescore_keys(taken_keys, legs_by_key, states, params, delay=delay)
    return rows, nc + 0, legs_by_key, states, taken_keys, nc0

# ---------- controls ----------
def controls(rows, nc, legs_by_key, placebo_rows, placebo_nc, signal_map=None):
    a = agg(rows, WEEKS)
    reds, tot, table = month_end_reds(rows)
    p_agg = agg(placebo_rows, WEEKS)
    viol, checked, external = [], 0, 0
    for r in rows:
        if r["exit_time"] < r["entry_time"]:
            viol.append((r["date"], r["entry_time"], "exit before entry"))
        if r["leg_key"] not in legs_by_key:
            external += 1  # audited by the caller against its own candle source
            continue
        l = legs_by_key[r["leg_key"]]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == r["entry_time"]]
        if not bars:
            viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005:
            viol.append((r["date"], r["entry_time"], "entry premium mismatch"))
        if signal_map is not None and r["family"].startswith("NS1"):
            sig = signal_map.get(r["leg_key"])
            if sig is None:
                viol.append((r["date"], r["entry_time"], "NS1 signal time not found"))
            elif r["entry_time"] <= sig:
                viol.append((r["date"], r["entry_time"], "NS1 entry not after signal"))
    top3 = sorted(rows, key=lambda x: -x["net"])[:3]
    months = {m: round(sum(r["net"] for r in rows if r["date"][5:7] == m), 2)
              for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    ft90 = round(100.0 * sum(r.get("ft90", 0) for r in rows) / len(rows), 1) if rows else 0.0
    return dict(n=a["n"], net=a["net"], ft_pct=a["ft_pct"], ft90_pct=ft90,
                per_week=a["per_week"], per_week_raw=round(len(rows) / WEEKS, 4),
                not_computed=nc, red_month_ends=reds, month_table=table, months=months,
                halves=dict(jan_may=round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2),
                            jun_oct=round(sum(r["net"] for r in rows if r["date"] >= "2026-06-01"), 2)),
                timing_violations=viol, timing_entry_bars_checked=checked,
                timing_external_rows=external,
                placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=placebo_nc),
                ex_top3_total=round(tot - sum(r["net"] for r in top3), 2),
                top3=[(r["date"], r["direction"], r["net"]) for r in top3])

def write_trades(rows, fname):
    out_csv = TR / fname
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "full_target", "net_inr"])
        for r in rows:
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(out_csv)):
        rs += float(r["net_inr"]); rn += 1
    return dict(n=rn, net=round(rs, 2))

def gate(c, ref, resum=None):
    """Round-2 banking gate vs reference controls `ref`. Returns (pass, failed legs)."""
    failed = []
    if not c["net"] > ref["net"]: failed.append(f"net {c['net']} !> ref {ref['net']}")
    if c["red_month_ends"]: failed.append(f"red month-ends {c['red_month_ends']}")
    for m, v in ref["months"].items():
        if v > 0 and c["months"].get(m, 0.0) < 0:
            failed.append(f"month {m} flips green->red ({v} -> {c['months'].get(m)})")
    if c["ft90_pct"] < ref["ft90_pct"]: failed.append(f"FT90 {c['ft90_pct']} < ref {ref['ft90_pct']}")
    if c["per_week_raw"] < 2.0: failed.append(f"frequency {c['per_week_raw']}/wk < 2.0")
    if c["halves"]["jan_may"] < 0 or c["halves"]["jun_oct"] < 0:
        failed.append(f"a half is negative {c['halves']}")
    if not c["net"] > c["placebo"]["net"]: failed.append(f"placebo not beaten ({c['placebo']['net']})")
    if c["timing_violations"]: failed.append(f"timing violations {len(c['timing_violations'])}")
    if c["not_computed"]: failed.append(f"NOT_COMPUTED {c['not_computed']}")
    if resum is not None and not (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005):
        failed.append(f"re-sum mismatch {resum} vs n={c['n']} net={c['net']}")
    return (len(failed) == 0), failed

def full_run(build_fn, ref, cycle_name=None, signal_map=None):
    """build_fn(delay) -> (rows, nc, legs_by_key). Runs controls + gate."""
    rows, nc, legs_by_key = build_fn(0)
    prows, pnc, _ = build_fn(6)
    c = controls(rows, nc, legs_by_key, prows, pnc, signal_map=signal_map)
    resum = None
    if cycle_name:
        resum = write_trades(rows, f"bank_engine_{cycle_name}_trades.csv")
        c["independent_resum"] = resum
        c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    ok, failed = gate(c, ref, resum=resum)
    c["gate_pass"] = ok; c["gate_failed_legs"] = failed
    return c, rows
