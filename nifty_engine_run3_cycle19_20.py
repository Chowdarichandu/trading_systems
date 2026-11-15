#!/usr/bin/env python3
"""RUN 3 Cycles 4-5 (engine Cycles 19-20), frozen in nifty_engine_frozen.md
before scoring (2026-11-02):
- Cycle 19 ITM100: incumbent legs on the one-strike-ITM contract
  (CE strike-100, PE strike+100), same monthly expiry.
- Cycle 20 WEEKLY: incumbent legs on the weekly expiry in force
  (earliest weekly expiry strictly after the trade date).
Candle loading is EXACT-tag only (no glob fallback) so a missing contract
is NOT_COMPUTED, never silently the monthly file. Geometry: BE50 +
lock75 + TGT2-180 (validated best-book replay, re-validated here under
exact loading). Controls in same run: timing audit, +30-min placebo,
halves, month table, ex-top-3, independent re-sum.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, controls

TR = Path.home() / "workspace/trading"
DIRS = A.DIRS
COST, LOT = 220.0, 65

def candles_exact(sym, strike, typ, day, exp):
    tag = f"{sym}_{int(strike)}{typ}_{day}_{exp}"
    for d in DIRS:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists():
                try:
                    data = json.loads(p.read_text()).get("data", {}).get("candles", [])
                except Exception:
                    continue
                rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                         float(c[5]) if len(c) > 5 else 0.0)
                        for c in sorted(data, key=lambda c: c[0]) if c[0][:10] == day]
                if rows: return rows
    return None

def replay_best(cs, entry_time, delay_bars=0):
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
            stop2, target2 = entry + 75.0, entry + 180.0
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == "15:10": return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= 50.0:
            cur_stop = max(cur_stop, entry)
        if t == "15:10":
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_exact(legs, delay_bars=0):
    res, nc, nc_legs = [], 0, []
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs:
            nc += 1; nc_legs.append((l["date"], l["direction"], l["strike"], l["expiry"])); continue
        r = replay_best(cs, l["entry_time"], delay_bars=delay_bars)
        if r is None:
            nc += 1; nc_legs.append((l["date"], l["direction"], l["strike"], l["expiry"])); continue
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

def run(name, legs):
    res, nc, nc_legs = score_exact(legs)
    pl, _, _ = score_exact(legs, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = audit_exact(legs)
    c["nc_legs"] = nc_legs
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    print(json.dumps(c, indent=1, default=str))
    Path(TR / f"nifty_engine_{name}_summary.json").write_text(json.dumps(c, indent=1, default=str))
    return c, res

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]

chk, nc_chk, _ = score_exact(EXP0)
ctot = round(sum(r["net"] for r in chk), 2)
print("incumbent check (exact loading):", len(chk), ctot, "NC", nc_chk, "expect 59 / 98001.0 / 0")
assert len(chk) == 59 and ctot == 98001.0 and nc_chk == 0
base_by_key = {(r["date"], r["direction"]): r for r in chk}

# ---- Cycle 19: ITM100 ----
ITM = []
for l in EXP0:
    sh = l["strike"] - 100 if l["direction"] == "CE" else l["strike"] + 100
    ITM.append({**l, "strike": sh})
c19, res19 = run("run3_cycle19_itm100", ITM)
chg = [dict(date=r["date"], dir=r["direction"], base_net=base_by_key[(r["date"], r["direction"])]["net"],
            cand_net=r["net"]) for r in res19
       if base_by_key[(r["date"], r["direction"])]["net"] != r["net"]]
print("ITM100 changed legs:", len(chg), "| net delta:", round(c19["total"] - 98001.0, 2))

# ---- Cycle 20: WEEKLY ----
wmap = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]
WK = [{**l, "expiry": wmap[f"{l['date']}|{l['direction']}"]} for l in EXP0]
c20, res20 = run("run3_cycle20_weekly", WK)
chg20 = [dict(date=r["date"], dir=r["direction"], base_net=base_by_key[(r["date"], r["direction"])]["net"],
              cand_net=r["net"]) for r in res20
         if base_by_key[(r["date"], r["direction"])]["net"] != r["net"]]
print("WEEKLY changed legs:", len(chg20), "| net delta:", round(c20["total"] - 98001.0, 2))
