"""V5 INDEX (Chandu request 2026-10-29 10:13 IST).
Paper only, no orders. Index only: NIFTY and BANKNIFTY, NO stocks.
Pool = V4 index candidates + Skill index candidates (OR-only, V4-style
filters), Jan 2026 to 28 Oct 2026 (Oct truncated to 2026-10-28; 29 Oct
excluded as still in progress that day).
Provisional choices, NOT Chandu's rule (he only said take inputs from
both Skill index and V4 index, run index only):
- Dedup same symbol+date: keep higher conviction (setup4=3 > setup3=2 >
  setup2=1 > skill OR=0), then higher prospective net target, then
  bias-strong, then room ratio.
- Filter: prospective net target >= Rs 500 (same as capped-v2).
- Rank (signal-time/prospective only, never realised outcome):
  setup_rank, bias_strong, room_ratio, prospective net target.
- Cap: max 3 index trades/ISO week, max 1 trade/symbol/week. With only
  2 symbols this caps at 2/week in practice; repeats are NOT allowed
  silently to reach 3/week. Actual trades/week is reported.
- Same provisional cash rules as capped-v2: 100 shares equivalent
  (index points x 100), Rs 40/trade, signal-candle stop, 2x target,
  square-off 15:10, Setup 1 skipped, short paper-only.
Index nets are point-scaled cash-equivalents, NOT portfolio rupees.
Reuses candidate logic from progressive_capped_v2.py, index-only.
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from progressive_capped import load, room_ratio, skill_or_outcome, SETUP_RANK, metrics
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
OUT = os.path.join(BASE, "v5_index_summary_{y}-{m:02d}.json")
QTY, COST = 100, 40.0
INDEX = ("NIFTY", "BANKNIFTY")
CUTOFF = "2026-10-28"

def candidates_for_month_index(year, month):
    v4, skill_filt, skill_raw = [], [], 0
    ndays = None
    for sym in INDEX:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        days = 0
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != year or d.month != month or i == 0:
                continue
            if d.date().isoformat() > CUTOFF:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            days += 1
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            week = d.isocalendar()[:2]
            wk = f"{week[0]}-W{week[1]:02d}"
            r = run_day(day_spot, pdh, pdc, pdl, bias, scale, QTY, COST)
            if r["exit_reason"] in ("target", "stop", "square_off"):
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                sig_close = float(sig["close"]) if sig is not None else float(r["entry_price"])
                rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
                dirc = 1 if direction == "CE" else -1
                tnet = round(dirc * (float(r["target_price"]) - float(r["entry_price"])) * QTY - COST, 2)
                v4.append({"method": "V4", "symbol": sym, "date": d.date().isoformat(), "week": wk,
                           "setup": setup, "direction": direction, "exit_reason": r["exit_reason"],
                           "net_rs": round(float(r["net_rs"]), 2), "target_net_rs": tnet,
                           "setup_rank": SETUP_RANK.get(setup, 0),
                           "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                           "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
            raw = day_spot.to_dict("records")
            for c in raw:
                c["timestamp"] = str(c["timestamp"])
            setup, direction, sig = find_skill_signal(raw, ("or",))
            if setup is None:
                continue
            skill_raw += 1
            if direction not in allowed:
                continue
            sig_close = float(sig["close"])
            if direction == "CE" and not (sig_close < pdh):
                continue
            if direction == "PE" and not (sig_close < pdl):
                continue
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            if rr < 1.0:
                continue
            out = skill_or_outcome(raw, sig, direction)
            if out is None:
                continue
            dirc = 1 if direction == "CE" else -1
            tnet = round(dirc * (out["target"] - out["entry"]) * QTY - COST, 2)
            skill_filt.append({"method": "Skill", "symbol": sym, "date": d.date().isoformat(), "week": wk,
                               "setup": setup, "direction": direction, "exit_reason": out["exit_reason"],
                               "net_rs": out["net_rs"], "target_net_rs": tnet, "setup_rank": 0,
                               "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                               "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
        if ndays is None:
            ndays = days
    return ndays, v4, skill_raw, skill_filt

def dedup_pool(v4, skill):
    pool = {}
    for t in v4 + skill:
        k = (t["symbol"], t["date"])
        cur = pool.get(k)
        if cur is None or (t["setup_rank"], t["target_net_rs"], t["bias_strong"], t["room_ratio"]) > \
                          (cur["setup_rank"], cur["target_net_rs"], cur["bias_strong"], cur["room_ratio"]):
            pool[k] = t
    return list(pool.values())

def cap_select_v5(cands, min_target=500.0, cap_week=3):
    pool = [t for t in cands if t["target_net_rs"] >= min_target]
    ranked = sorted(pool, key=lambda t: (-t["setup_rank"], -t["bias_strong"], -t["room_ratio"],
                                         -t["target_net_rs"], t["date"], t["symbol"]))
    picked, week_n, sym_week = [], {}, set()
    for t in ranked:
        w = t["week"]
        if week_n.get(w, 0) >= cap_week:
            continue
        if (t["symbol"], w) in sym_week:
            continue
        picked.append(t)
        week_n[w] = week_n.get(w, 0) + 1
        sym_week.add((t["symbol"], w))
    return picked, ranked

def run_v5_month(year, month, min_target=500.0):
    ndays, v4, skill_raw, skill_filt = candidates_for_month_index(year, month)
    weeks = sorted(set(t["week"] for t in v4 + skill_filt))
    nweeks = len(weeks)
    pool = dedup_pool(v4, skill_filt)
    picked, ranked = cap_select_v5(pool, min_target)
    # input legs, index-only, from capped-v2 JSONs for comparison (recomputed here from capped picks is not possible;
    # comparison totals are taken from jan_oct_2026_v4_and_skill.md / capped_v2 JSON legs, verified separately)
    bn = [t for t in picked if t["symbol"] == "BANKNIFTY"]
    nf = [t for t in picked if t["symbol"] == "NIFTY"]
    return {"year": year, "month": month, "days": ndays, "weeks": nweeks,
            "v4_index_candidates": len(v4), "skill_index_filtered": len(skill_filt),
            "skill_index_or_signals": skill_raw,
            "dedup_pool": len(pool), "pass500_pool": len(ranked),
            "v5": metrics(picked, ndays, nweeks),
            "v5_banknifty": metrics(bn, ndays, nweeks), "v5_nifty": metrics(nf, ndays, nweeks),
            "v5_trades": picked,
            "avg_target_net_v5": round(sum(t["target_net_rs"] for t in picked) / len(picked), 2) if picked else 0}

if __name__ == "__main__":
    y, m = int(sys.argv[1]), int(sys.argv[2])
    out = run_v5_month(y, m)
    print(f"{y}-{m:02d} days={out['days']} weeks={out['weeks']} v4_idx_cand={out['v4_index_candidates']} "
          f"skill_idx_filt={out['skill_index_filtered']} pool={out['dedup_pool']} pass500={out['pass500_pool']} v5={out['v5']}")
    print("  BANKNIFTY:", out["v5_banknifty"])
    print("  NIFTY:", out["v5_nifty"])
    with open(OUT.format(y=y, m=m), "w") as f:
        json.dump(out, f, indent=2, default=str)
