"""V6 INDEX — aggressive tuning, history first (Chandu 2026-10-29 10:48 IST).
Paper only, no orders. Index only: NIFTY and BANKNIFTY, NO stocks.
Pool = V5 index pool (V4 index + Skill index candidates, deduped by
symbol+date keeping higher conviction), Jan 2026 to 28 Oct 2026.
Provisional choices, NOT Chandu's rule (he only said: tune aggressively,
Nifty first, history first, then November paper):
- Conviction only: setup_rank >= 2 (setup4 reclaim/pullback = 3,
  setup3 bounce rejection = 2). setup2 and skill OR (rank 0-1) dropped.
- Nifty first: in pooled variants, Nifty candidates rank before
  Bank Nifty candidates at the same setup rank.
- Higher prospective target filter: >= Rs 1000 or >= Rs 1500 on the
  ORIGINAL 2x-risk target (net of Rs 40 cost), vs V5 Rs 500.
- Stop-cap sensitivity: losing trades floored at -Rs 5040
  (50 points x 100 shares + Rs 40 cost). This is an UPPER-BOUND
  sensitivity only: it keeps original target wins and only truncates
  losses. A true 50-point stop would also shrink targets to
  100 points (Rs 9960 max) and change exit timing, so the floored
  numbers must NOT be read as a real backtest of a 50-point stop rule.
  They are reported only to count how many large stops exist and how
  much they dominate.
- Cap: max 3 index trades/ISO week, max 1 trade/symbol/week (2/week
  practical max with 2 symbols, as in V5).
- Walk-forward: tune Jan-Jun 2026, validate Jul-Oct 2026 unseen.
  A variant that only looks good on Jan-Oct tuned together is NOT
  a progression.
Same provisional cash rules as V5 otherwise: 100 shares equivalent,
Rs 40/trade, signal-candle stop, 2x target, square-off 15:10, short
paper-only. Index nets are point-scaled cash-equivalents, NOT
portfolio rupees.
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from v5_index import candidates_for_month_index, dedup_pool

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
OUT = os.path.join(BASE, "v6_index_summary_{y}-{m:02d}.json")
STOP_FLOOR = -5040.0

def cap_select(cands, nifty_only=False, nifty_first=True, min_target=1000.0, stop_floor=False):
    pool = [dict(t) for t in cands
            if t["setup_rank"] >= 2 and t["target_net_rs"] >= min_target]
    if nifty_only:
        pool = [t for t in pool if t["symbol"] == "NIFTY"]
    if stop_floor:
        for t in pool:
            if t["exit_reason"] == "stop":
                t["net_rs_capped"] = max(float(t["net_rs"]), STOP_FLOOR)
            else:
                t["net_rs_capped"] = float(t["net_rs"])
    def rank_key(t):
        sym_rank = 0 if t["symbol"] == "NIFTY" else 1
        if not nifty_first:
            sym_rank = 0
        return (-t["setup_rank"], sym_rank, -t["bias_strong"], -t["room_ratio"],
                -t["target_net_rs"], t["date"], t["symbol"])
    ranked = sorted(pool, key=rank_key)
    picked, week_n, sym_week = [], {}, set()
    for t in ranked:
        w = t["week"]
        if week_n.get(w, 0) >= 3:
            continue
        if (t["symbol"], w) in sym_week:
            continue
        picked.append(t)
        week_n[w] = week_n.get(w, 0) + 1
        sym_week.add((t["symbol"], w))
    return picked, ranked

def summarise(trades, use_capped=False):
    key = "net_rs_capped" if use_capped else "net_rs"
    nets = [float(t.get(key, t["net_rs"])) for t in trades]
    targets = sum(1 for t in trades if t["exit_reason"] == "target")
    bn = [t for t in trades if t["symbol"] == "BANKNIFTY"]
    nf = [t for t in trades if t["symbol"] == "NIFTY"]
    def leg(ts):
        ns = [float(t.get(key, t["net_rs"])) for t in ts]
        return {"trades": len(ts), "net": round(sum(ns), 2),
                "win": round(sum(1 for t in ts if t["exit_reason"] == "target") / len(ts) * 100, 1) if ts else 0.0}
    return {"trades": len(trades), "targets": targets,
            "win_pct": round(targets / len(trades) * 100, 1) if trades else 0.0,
            "net": round(sum(nets), 2),
            "expectancy": round(sum(nets) / len(nets), 2) if nets else 0.0,
            "banknifty": leg(bn), "nifty": leg(nf)}

VARIANTS = {
    "V6-A_nifty_only_t1000": dict(nifty_only=True, min_target=1000.0),
    "V6-B_pooled_niftyfirst_t1000": dict(nifty_only=False, min_target=1000.0),
    "V6-C_pooled_niftyfirst_t1500": dict(nifty_only=False, min_target=1500.0),
    "V6-D_nifty_only_t1500": dict(nifty_only=True, min_target=1500.0),
    "V6-E_pooled_t1000_stopfloor": dict(nifty_only=False, min_target=1000.0, stop_floor=True),
    "V6-F_nifty_only_t1000_stopfloor": dict(nifty_only=True, min_target=1000.0, stop_floor=True),
}

def run_month(year, month):
    ndays, v4, skill_raw, skill_filt = candidates_for_month_index(year, month)
    pool = dedup_pool(v4, skill_filt)
    weeks = sorted(set(t["week"] for t in pool))
    # large stops in the conviction pool (before cap, before target filter)
    conv = [t for t in pool if t["setup_rank"] >= 2]
    large = [t for t in conv if float(t["net_rs"]) < STOP_FLOOR]
    out = {"year": year, "month": month, "days": ndays, "weeks": len(weeks),
           "v4_index_candidates": len(v4), "skill_index_filtered": len(skill_filt),
           "dedup_pool": len(pool), "conviction_pool": len(conv),
           "large_stops_below_floor": len(large),
           "large_stops_by_symbol": {"BANKNIFTY": sum(1 for t in large if t["symbol"] == "BANKNIFTY"),
                                      "NIFTY": sum(1 for t in large if t["symbol"] == "NIFTY")},
           "large_stop_net_sum": round(sum(float(t["net_rs"]) for t in large), 2),
           "variants": {}}
    for name, kw in VARIANTS.items():
        picked, ranked = cap_select(pool, **kw)
        use_capped = kw.get("stop_floor", False)
        out["variants"][name] = {"pool_pass": len(ranked),
                                 "summary": summarise(picked, use_capped),
                                 "trades": picked}
    return out

if __name__ == "__main__":
    y, m = int(sys.argv[1]), int(sys.argv[2])
    out = run_month(y, m)
    print(f"{y}-{m:02d} days={out['days']} pool={out['dedup_pool']} conv={out['conviction_pool']} large_stops={out['large_stops_below_floor']} net={out['large_stop_net_sum']}")
    for name, v in out["variants"].items():
        s = v["summary"]
        print(f"  {name}: pool_pass={v['pool_pass']} trades={s['trades']} win={s['win_pct']}% net={s['net']} BN={s['banknifty']} NF={s['nifty']}")
    with open(OUT.format(y=y, m=m), "w") as f:
        json.dump(out, f, indent=2, default=str)
