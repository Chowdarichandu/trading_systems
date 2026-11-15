#!/usr/bin/env python3
"""ROUND 2 Family 3 (Cycles 34-37): ENTRY-SIDE PERMUTATIONS.
Re-pool from stored component candidates (o1 (lA) v2 + V5-v2 tracks,
Skill V3 jansep, Volrix (b) jansep; October legs frozen from the B2 file),
UNIQUE-ONCE earliest entry, then the B2 post-pool filters exactly as measured
on the frozen files (drop rep == Skill V3 & CE; drop Skill-solo legs with
entry <= 09:55). Sanity: the frozen-parameter re-pool must reproduce the
89-leg B2 base exactly before any variant is read.
Variants: (lA) rescan cutoff 11:30 / 12:30 (signal_time filter on (lA)
candidates); bias thresholds (40,85) / (30,75) (V5-v2 winner removal -
measured zero-effect, see cycle entry); expiry-day strike 100 ITM."""
import sys, csv, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from aggressive_score import EXPIRIES
from bank_engine_repro import base_legs
from bank_engine_cycle import signal_map as frozen_signal_map
from bank_r2_ns1 import gen_ns1, V15
from bank_r2_core import build_pool, build_fixed, controls, full_run, rescore_keys
from daytrader_cash_backtest import bias_of

TR = "/home/hatch/workspace/trading"
_spot = pd.read_csv(f"{TR}/data/progressive/BANKNIFTY/spot_5m.csv")
SPOT_OPEN = {(r["timestamp"][:10], r["timestamp"][11:16]): float(r["open"])
             for _, r in _spot.iterrows()}
_daily = pd.read_csv(f"{TR}/data/progressive/BANKNIFTY/spot_daily.csv").to_dict("records")
CS = {}
for i, r in enumerate(_daily):
    if i == 0: continue
    CS[str(r["date"])[:10]] = bias_of(_daily[i - 1])[1]

def candidates():
    out = []
    for r in csv.DictReader(open(f"{TR}/index_options_o1_janoct_trades.csv")):
        if r["index"] != "BANKNIFTY" or r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2":
            system = "(lA) v2"
        elif r["track"] == "V5-v2":
            system = "V5 v2"
        else:
            continue
        out.append(dict(date=r["date"], direction=r["direction"], entry_time=r["entry_time"],
                        system=system, signal_time=r["signal_time"],
                        entry_spot=SPOT_OPEN.get((r["date"], r["entry_time"]))))
    for r in csv.DictReader(open(f"{TR}/index_options_U1_skillV3_jansep_spot.csv")):
        if r["index"] != "BANKNIFTY": continue
        out.append(dict(date=r["date"], direction=r["direction"], entry_time=r["entry_time"],
                        system="Skill V3", signal_time=None,
                        entry_spot=float(r["entry_spot"])))
    for r in csv.DictReader(open(f"{TR}/index_options_U1_volrixB_jansep_spot.csv")):
        if r["index"] != "BANKNIFTY": continue
        out.append(dict(date=r["entry_date"], direction=r["direction"], entry_time=r["entry_time"],
                        system="Volrix (b)", signal_time=None,
                        entry_spot=float(r["entry_spot"])))
    return out

def repooled_base(cutoff=None, bias_variant=None):
    cands = candidates()
    if cutoff is not None:
        cands = [c for c in cands if not (c["system"] == "(lA) v2" and c["signal_time"] > cutoff)]
    if bias_variant is not None:
        b_cut, u_cut = bias_variant
        def allowed(c):
            if c["system"] != "V5 v2": return True
            cs = CS.get(c["date"])
            if cs is None: return True
            bias = "bearish" if cs < b_cut else "bullish" if cs >= u_cut else "neutral"
            return c["direction"] in ({"PE"} if bias == "bearish" else
                                      {"CE"} if bias == "bullish" else {"CE", "PE"})
        cands = [c for c in cands if allowed(c)]
    by_key = {}
    for c in cands:
        by_key.setdefault((c["date"], c["direction"]), []).append(c)
    legs = []
    prio = {"(lA) v2": 0, "V5 v2": 1, "Skill V3": 2, "Volrix (b)": 3}
    for (date, direction), cs_ in by_key.items():
        win = sorted(cs_, key=lambda c: (c["entry_time"], prio[c["system"]]))[0]
        sources = sorted({c["system"] for c in cs_})
        if win["system"] == "Skill V3" and direction == "CE": continue
        if sources == ["Skill V3"] and win["entry_time"] <= "09:55": continue
        if win["entry_spot"] is None: continue
        legs.append({"date": date, "index": "BANKNIFTY", "direction": direction,
                     "entry_time": win["entry_time"],
                     "strike": int(round(win["entry_spot"] / 100.0) * 100),
                     "expiry": next(e for e in EXPIRIES if e >= date), "lot": 30,
                     "family": "BASE", "rep": win["system"]})
    october = [l for l in base_legs("BANKNIFTY") if l["date"] >= "2026-10-01"]
    return legs + october

def sanity():
    mine = sorted((l["date"], l["direction"], l["entry_time"], l["strike"], l["expiry"], l["rep"])
                  for l in repooled_base())
    ref = sorted((l["date"], l["direction"], l["entry_time"], l["strike"], l["expiry"], l["rep"])
                 for l in base_legs("BANKNIFTY"))
    print(f"repooled base: {len(mine)} | frozen B2 base: {len(ref)} | identical: {mine == ref}")
    if mine != ref:
        sm, sr = set(mine), set(ref)
        print(" only in repool:", sorted(sm - sr)[:8])
        print(" only in frozen:", sorted(sr - sm)[:8])
    return mine == ref

def run_pool_variant(base, cyc_name, REF):
    seconds, _ = gen_ns1(1.5, "14:30")
    pool = base + seconds
    def bf(delay):
        rows, nc, lbk, states, taken, nc0 = build_pool(pool, V15, delay=delay)
        return rows, nc, lbk
    return full_run(bf, REF, cycle_name=cyc_name, signal_map=frozen_signal_map())

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sanity":
        sanity()
    elif mode == "run":
        assert sanity(), "re-pool sanity failed - variants not read"
        ref_rows, ref_nc, ref_lbk = build_fixed(V15, delay=0)
        ref_prows, ref_pnc, _ = build_fixed(V15, delay=6)
        REF = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
        assert REF["net"] == 105167.00
        out = {}
        for name, kw in (("r2c34_cutoff1130", dict(cutoff="11:30")),
                         ("r2c35_cutoff1230", dict(cutoff="12:30"))):
            c, _ = run_pool_variant(repooled_base(**kw), name, REF)
            out[name] = {k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw",
                                           "halves", "months", "ex_top3_total", "not_computed",
                                           "gate_pass", "gate_failed_legs")}
            out[name]["placebo_net"] = c["placebo"]["net"]
            print(f"{name}: n={c['n']} net={c['net']} ft90={c['ft90_pct']} pl={c['placebo']['net']} "
                  f"PASS={c['gate_pass']} fail={c['gate_failed_legs'][:3]}")
        # bias variants: prove the removal sets are empty on stored winners
        for name, bv in (("r2c36_bias_40_85", (40.0, 85.0)), ("r2c36_bias_30_75", (30.0, 75.0))):
            removed = []
            for r in csv.DictReader(open(f"{TR}/index_options_o1_janoct_trades.csv")):
                if r["index"] != "BANKNIFTY" or r["track"] != "V5-v2": continue
                cs = CS.get(r["date"])
                if cs is None: continue
                bias = "bearish" if cs < bv[0] else "bullish" if cs >= bv[1] else "neutral"
                allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
                if r["direction"] not in allowed:
                    removed.append((r["date"], r["direction"], round(cs, 2)))
            frozen_removed = []
            for r in csv.DictReader(open(f"{TR}/index_options_o1_janoct_trades.csv")):
                if r["index"] != "BANKNIFTY" or r["track"] != "V5-v2": continue
                cs = CS.get(r["date"])
                if cs is None: continue
                bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
                allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
                if r["direction"] not in allowed:
                    frozen_removed.append((r["date"], r["direction"]))
            new = [x for x in removed if (x[0], x[1]) not in frozen_removed]
            out[name] = dict(removal_set_new=new, verdict="book identical to v15 by construction"
                             if not new else "REMOVALS EXIST - must re-pool")
            print(f"{name}: variant-only removals: {new}")
        json.dump(out, open(f"{TR}/bank_r2_entry_results.json", "w"), indent=1)
        print("saved bank_r2_entry_results.json")
