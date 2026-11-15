#!/usr/bin/env python3
"""ROUND 5 WS0 — feature-causality audit of the ADOPTED book + causal
re-baseline (freeze: nifty_engine_frozen.md Round-5 WS0). Stage 1 prints
diagnostics (strike-convention validation); stage 2 (run after review)
builds and scores the causal book. No candidate is scored here."""
import sys, csv, json, math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r5_harness import run_r5, set_current, CURRENT
from nifty_engine_r4_harness import candidate_legs, spot5m
from nifty_engine_r2_harness import candles_exact, pool_sets
from nifty_engine_score import nsrc

TR = Path.home() / "workspace/trading"

# ---------- per-system entry times from the merge's own input files ----------
def build_sysmap():
    S = defaultdict(dict)
    def put(date, idx, dirn, sysname, et):
        if idx != "NIFTY" or not et: return
        k = (date, dirn)
        if sysname not in S[k] or et < S[k][sysname]: S[k][sysname] = et
    for r in csv.DictReader(open(TR / "index_options_o1_janoct_trades.csv")):
        if r["date"] >= "2026-10-01": continue
        if r["track"] == "(lA) v2": put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["track"] == "V5-v2": put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_skillV3_jansep_spot.csv")):
        put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_U1_volrixB_jansep_spot.csv")):
        put(r["entry_date"], r["index"], r["direction"], "Volrix (b)", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_premium_october_trades.csv")):
        if r["premium_status"] != "COMPUTED": continue
        if r["version"].startswith("(lA)"): put(r["date"], r["index"], r["direction"], "(lA) v2", r["entry_time"])
        elif r["version"].startswith("V5"): put(r["date"], r["index"], r["direction"], "V5 v2", r["entry_time"])
    for r in csv.DictReader(open(TR / "index_options_skill_tuned_oct30_trades.csv")):
        if r["variant"] == "V3" and r["premium_status"] == "COMPUTED":
            put(r["date"], r["index"], r["direction"], "Skill V3", r["entry_time"])
    put("2026-10-09", "NIFTY", "CE", "Volrix (b)", "09:20")  # merge hardcode
    return S

def atm100(x):
    return int(math.floor(x / 100.0 + 0.5)) * 100

def spot_bar(date, t):
    for b in spot5m().get(date, []):
        if b[0] == t: return b
    return None

def classify(leg, S):
    """Returns dict: status in {solo_lA, tie, lA_earliest, violation},
    t2 (second-earliest system entry), times per system."""
    srcs = [s.strip() for s in leg["sources"].split(";") if s.strip()]
    times = {s: S.get((leg["date"], leg["direction"]), {}).get(s) for s in srcs}
    ets = sorted(t for t in times.values() if t)
    t2 = ets[1] if len(ets) >= 2 else None
    if len(srcs) == 1:
        status = "solo_lA" if leg["rep"] == "(lA) v2" else "solo_other"
    elif leg["rep"] == "(lA) v2" and times.get("(lA) v2") == leg["entry_time"]:
        status = "tie" if t2 == leg["entry_time"] else "lA_earliest"
    elif t2 == leg["entry_time"]:
        status = "tie"
    else:
        status = "violation"
    return dict(status=status, t2=t2, times=times)

def causalise(leg, S):
    """Returns (causal_leg or None, classification dict). None = dropped."""
    c = classify(leg, S)
    if c["status"] in ("solo_lA", "tie", "lA_earliest"):
        return dict(leg), c
    # violation: admitted at t2 if t2 <= 09:55, else dropped
    if c["t2"] is None or c["t2"] > "09:55":
        return None, c
    b = spot_bar(leg["date"], c["t2"])
    nl = dict(leg)
    nl["entry_time"] = c["t2"]
    nl["strike"] = atm100(b[1]) if b else leg["strike"]
    return nl, c

if __name__ == "__main__" and "--build" in sys.argv:
    S = build_sysmap()
    legs = candidate_legs()
    # adopted-book per-leg nets (baseline, adopted geometry)
    _, base_res = run_r5("ws0_adopted_baseline", legs, save=True, gate=False, quiet=True)
    base_net = {(r["date"], r["direction"]): r["net"] for r in base_res}
    causal, detail = [], []
    for l in legs:
        cl, c = causalise(l, S)
        row = dict(date=l["date"], direction=l["direction"], rep=l["rep"],
                   recorded_entry=l["entry_time"], recorded_strike=l["strike"],
                   status=c["status"], t2=c["t2"], times=c["times"],
                   adopted_net=base_net.get((l["date"], l["direction"])))
        if cl is None:
            row["causal"] = "DROPPED"
        else:
            row["causal"] = "kept" if cl["entry_time"] == l["entry_time"] else "RETIMED"
            row["causal_entry"] = cl["entry_time"]; row["causal_strike"] = cl["strike"]
            causal.append(cl)
        detail.append(row)
    # candle availability for causal legs
    missing = []
    for cl in causal:
        if not candles_exact(cl["index"], cl["strike"], cl["direction"], cl["date"], cl["expiry"]):
            missing.append((cl["date"], cl["direction"], cl["strike"], cl["expiry"], cl["entry_time"]))
    print("causal legs:", len(causal), "| dropped:", sum(1 for d in detail if d["causal"] == "DROPPED"),
          "| retimed:", sum(1 for d in detail if d["causal"] == "RETIMED"))
    print("missing candles for causal legs:", missing)
    Path(TR / "nifty_engine_r5_ws0_detail.json").write_text(json.dumps(
        {"classification": detail, "missing_candles": [str(m) for m in missing]}, indent=1, default=str))
    if not missing:
        c, res = run_r5("run3r5_ws0_causal", causal, save=True, gate=False)
        new_net = {(r["date"], r["direction"]): r["net"] for r in res}
        eff_drop = -sum(d["adopted_net"] for d in detail if d["causal"] == "DROPPED")
        eff_retime = sum(new_net.get((d["date"], d["direction"]), 0) - d["adopted_net"]
                         for d in detail if d["causal"] == "RETIMED")
        print(f"EFFECT: dropped legs remove {eff_drop:+,.2f} | retiming changes {eff_retime:+,.2f} | "
              f"causal total {c['total']:+,.2f} vs adopted +114,921.75 -> delta {c['total'] - 114921.75:+,.2f}")
        for d in detail:
            if d["causal"] == "RETIMED":
                d["causal_net"] = new_net.get((d["date"], d["direction"]))
        Path(TR / "nifty_engine_r5_ws0_detail.json").write_text(json.dumps(
            {"classification": detail, "missing_candles": [],
             "causal_total": c["total"], "causal_summary": c}, indent=1, default=str))

def causal_legs():
    """The Round-5 working book: adopted legs read causally (WS0 remedy)."""
    S = build_sysmap()
    out = []
    for l in candidate_legs():
        cl, _ = causalise(l, S)
        if cl is not None: out.append(cl)
    return out

def dte0_population():
    """WS3 population (frozen): C3L legs with date == expiry, causally
    admissible under the WS0 remedy (solo (lA), or confirmation completing
    <= 09:55 entered at t2 with ATM strike at t2)."""
    S = build_sysmap()
    _, C3L, _ = pool_sets()
    out, excluded = [], []
    for l in C3L:
        if l["date"] != l["expiry"]: continue
        srcs = [s.strip() for s in l["sources"].split(";") if s.strip()]
        if len(srcs) == 1 and l["rep"] == "(lA) v2":
            out.append(dict(l)); continue
        c = classify(l, S)
        if c["t2"] is not None and c["t2"] <= "09:55":
            nl = dict(l); nl["entry_time"] = c["t2"]
            b = spot_bar(l["date"], c["t2"])
            if b: nl["strike"] = atm100(b[1])
            out.append(nl)
        else:
            excluded.append((l["date"], l["direction"], c["status"], c["t2"]))
    return out, excluded

if __name__ == "__main__" and "--diag" in sys.argv:
    S = build_sysmap()
    legs = candidate_legs()
    pool = {(r["date"], r["direction"]): r for r in csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv")) if r["index"] == "NIFTY"}
    # strike-convention validation: recorded strike vs ATM100(entry_spot),
    # vs ATM100(spot5m open at entry bar), vs ATM100(spot5m close at entry bar)
    n_ok = {"entry_spot": 0, "spot_open": 0, "spot_close": 0}
    n_es = 0
    for l in legs:
        es_raw = pool[(l["date"], l["direction"])]["entry_spot"]
        b = spot_bar(l["date"], l["entry_time"])
        if es_raw:
            n_es += 1
            if atm100(float(es_raw)) == l["strike"]: n_ok["entry_spot"] += 1
        if b and atm100(b[1]) == l["strike"]: n_ok["spot_open"] += 1
        if b and atm100(b[4]) == l["strike"]: n_ok["spot_close"] += 1
    print("strike convention matches of 44 (entry_spot present on", n_es, "):", n_ok)
    # classification table
    from collections import Counter
    cnt = Counter()
    for l in legs:
        c = classify(l, S)
        cnt[c["status"]] += 1
        if c["status"] == "violation":
            print("VIOL", l["date"], l["direction"], "entry", l["entry_time"], "rep", l["rep"],
                  "t2", c["t2"], c["times"], "->", "DROP" if c["t2"] > "09:55" else "RETIME")
    print("classification:", dict(cnt))
    # DTE-0 population (C3L legs with date == expiry)
    _, C3L, EXP0 = pool_sets()
    dte0 = [l for l in C3L if l["date"] == l["expiry"]]
    print("DTE0 legs in C3L:", len(dte0))
    for l in dte0:
        c = classify(l, S)
        print("DTE0", l["date"], l["direction"], "entry", l["entry_time"], "rep", l["rep"],
              "nsrc", nsrc(l), c["status"], "t2", c["t2"], c["times"])
