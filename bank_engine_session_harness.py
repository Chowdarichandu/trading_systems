#!/usr/bin/env python3
"""Session 2026-11-02 harness (BANKNIFTY ONLY): parameterised rebuild of the
engine book from book v8 onward. Stream membership (Cycle-11 cold-(lA)
stand-aside) and anchored trailing-10 states come from the frozen book-v4
scored stream, exactly as in Cycles 18/20 - variants change ONLY the exit
replays of taken legs:
  entry premium < 400          -> runner(lock=lt400_lock, tgt2=lt400_tgt2)
  entry premium >= 400, warm   -> runner(lock=ge400_lock, tgt2=ge400_tgt2),
                                  or plain G0 if ge400_band_off contains ep
  entry premium >= 400, cold   -> plain G0
All defaults = book v8 (sanity: 82 legs, +77,196.50). Premiums, lot 30,
cost Rs220, UNIQUE-ONCE inherited. Placebo = same params at delay=6."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, agg, month_end_reds
from bank_engine_run2 import book_v4_legs
from bank_engine_run2_cycle14 import stream_keys, be_replay
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_cycle import _entry_premium

TR = Path.home() / "workspace/trading"
V8 = dict(lt400_lock=75.0, lt400_tgt2=180.0, ge400_lock=75.0, ge400_tgt2=180.0,
          ge400_band_off=None)

def build(delay=0, **params):
    p = {**V8, **params}
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=delay)
    states = anchored_states(delay=delay)
    out, nc = [], 0
    for key in keys:
        l = legs_by_key[key]
        ep = _entry_premium(l)
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if ep is not None and ep < 400.0:
            r = runner_replay(cs, l["entry_time"], delay=delay,
                              lock_pts=p["lt400_lock"], target2_pts=p["lt400_tgt2"])
        else:
            n, net = states.get(key, (0, 0.0))
            warm = (n < 10) or (net >= 0)
            band_off = warm and p["ge400_band_off"] is not None and \
                p["ge400_band_off"][0] <= ep < p["ge400_band_off"][1]
            if warm and not band_off:
                r = runner_replay(cs, l["entry_time"], delay=delay,
                                  lock_pts=p["ge400_lock"], target2_pts=p["ge400_tgt2"])
            else:
                r = be_replay(cs, l["entry_time"], delay=delay, arm=False)
        if r is None:
            nc += 1; continue
        out.append({**r, "date": l["date"], "direction": l["direction"],
                    "family": l["family"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "leg_key": key})
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc, legs_by_key

def controls(rows, nc, legs_by_key, placebo_rows, placebo_nc):
    a = agg(rows, 40.6)
    reds, tot, table = month_end_reds(rows)
    p_agg = agg(placebo_rows, 40.6)
    viol, checked = [], 0
    for r in rows:
        if r["exit_time"] < r["entry_time"]:
            viol.append((r["date"], r["entry_time"], "exit before entry"))
        l = legs_by_key[r["leg_key"]]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == r["entry_time"]]
        if not bars:
            viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005:
            viol.append((r["date"], r["entry_time"], "entry premium mismatch"))
    top3 = sorted(rows, key=lambda x: -x["net"])[:3]
    months = {m: round(sum(r["net"] for r in rows if r["date"][5:7] == m), 2)
              for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    return dict(n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
                not_computed=nc, red_month_ends=reds, month_table=table, months=months,
                halves=dict(jan_may=round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2),
                            jun_oct=round(sum(r["net"] for r in rows if r["date"] >= "2026-06-01"), 2)),
                timing_violations=viol, timing_entry_bars_checked=checked,
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

def run_cycle(cycle_name, base_params, variant_params, base_expect):
    """base_params reproduce the current banked book (sanity gate);
    variant_params = base + the one frozen change."""
    base_rows, base_nc, legs_by_key = build(delay=0, **base_params)
    b = agg(base_rows, 40.6)
    assert b["n"] == base_expect["n"] and abs(b["net"] - base_expect["net"]) < 0.005, \
        f"sanity failed: {b} vs {base_expect}"
    rows, nc, _ = build(delay=0, **variant_params)
    prows, pnc, _ = build(delay=6, **variant_params)
    s = controls(rows, nc, legs_by_key, prows, pnc)
    base_map = {r["leg_key"]: r for r in base_rows}
    s["changed_legs"] = [(r["date"], r["direction"], base_map[r["leg_key"]]["exit_reason"],
                          base_map[r["leg_key"]]["net"], r["exit_reason"], r["net"])
                         for r in rows if abs(base_map[r["leg_key"]]["net"] - r["net"]) > 0.005]
    s["sanity_base"] = dict(n=b["n"], net=b["net"], ft_pct=b["ft_pct"], per_week=b["per_week"])
    s["independent_resum"] = write_trades(rows, f"bank_engine_{cycle_name}_trades.csv")
    s["resum_matches"] = (s["independent_resum"]["n"] == s["n"]
                          and abs(s["independent_resum"]["net"] - s["net"]) < 0.005)
    s["cycle"] = cycle_name
    (TR / f"bank_engine_{cycle_name}_summary.json").write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))
    return s
