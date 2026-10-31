#!/usr/bin/env python3
"""Bank recursive engine — reproduce incumbent V1 working book (BANKNIFTY ONLY).
V1 = B2 base legs + NS1 second legs, UNIQUE-ONCE (date,index,direction) earliest entry,
G0 exits -50/+90, stop before target, square-off 15:10, lot 30, cost Rs220.
Uses aggressive_score.py construction exactly. Verifies against recorded reference:
Jan-Oct +23,703.50, 130 trades, FT 55 (42.3%), October +17,160.00 (12 trades),
month table from aggressive_results_check.json BANKNIFTY V1."""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import base_legs, ns_oct_legs, ns_jansep_legs, unique_once, score_legs, agg, month_end_reds

TR = Path.home() / "workspace/trading"
SYM = "BANKNIFTY"

def build_v1_legs():
    B = base_legs(SYM)  # all Jan-Oct (89)
    ns1 = [l for l in ns_jansep_legs(SYM) if l["family"].startswith("NS1")] + \
          [l for l in ns_oct_legs(SYM) if l["family"].startswith("NS1")]
    return unique_once(B + ns1), len(B), len(ns1)

def main():
    legs, nb, nns = build_v1_legs()
    print(f"legs: base={nb} ns1_raw={nns} pooled_unique_once={len(legs)}")
    res, nc = score_legs(legs)  # G0 default
    print("not_computed:", nc)
    a = agg(res, 40.6)
    print("Jan-Oct agg:", a)
    reds, tot, table = month_end_reds(res)
    print("total:", tot, "red month-ends:", reds)
    for m in sorted(table): print(m, table[m])
    oct_res = [r for r in res if r["date"][5:7] == "10"]
    print("October:", agg(oct_res, 3.6), "net", round(sum(r["net"] for r in oct_res), 2))
    # verify vs reference
    ref = json.loads((TR / "aggressive_results_check.json").read_text())["BANKNIFTY"]["V1_base+NS1second"]
    ok = True
    def chk(name, got, want):
        nonlocal ok
        good = abs(got - want) < 0.005
        ok = ok and good
        print(f"VERIFY {name}: got {got} want {want} {'OK' if good else 'MISMATCH'}")
    chk("n", a["n"], ref["n"]); chk("net", a["net"], ref["net"]); chk("ft", a["ft"], ref["ft"])
    for m, (mn, cum) in ref["month_table"].items():
        chk(f"month {m} net", table[m][0], mn); chk(f"month {m} cum", table[m][1], cum)
    chk("october net", round(sum(r["net"] for r in oct_res), 2), 17160.00)
    chk("october n", len(oct_res), 12)
    # write trades file
    legmap = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    with open(TR / "bank_engine_V1_trades.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","entry_time","entry_premium","exit_time","exit_premium","exit_reason","full_target","net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    # independent re-sum from the written file
    s = 0.0; n = 0
    for r in csv.DictReader(open(TR / "bank_engine_V1_trades.csv")):
        s += float(r["net_inr"]); n += 1
    chk("independent re-sum net", round(s, 2), ref["net"]); chk("independent re-sum n", n, ref["n"])
    print("RECONCILIATION:", "PASS" if ok else "FAIL")
    # ---- diagnosis breakdowns (working book) ----
    def breakdown(keyfn, label):
        d = defaultdict(lambda: [0, 0.0, 0])
        for r in res:
            k = keyfn(r); d[k][0] += 1; d[k][1] += r["net"]; d[k][2] += r["ft"]
        print(f"--- by {label} ---")
        for k in sorted(d): print(f"{k}: n={d[k][0]} net={round(d[k][1],2)} ft={d[k][2]}")
    breakdown(lambda r: r["family"], "family")
    breakdown(lambda r: r["direction"], "direction")
    breakdown(lambda r: r["exit_reason"], "exit_reason")
    breakdown(lambda r: r["entry_time"][:2], "entry hour")
    breakdown(lambda r: r["date"][5:7], "month (dup of table)")
    print("--- October trades ---")
    for r in sorted(oct_res, key=lambda x: (x["date"], x["entry_time"])):
        print(r["date"], r["entry_time"], r["direction"], r["family"], r["rep"], r["exit_reason"], r["net"])
    print("--- October by family ---")
    breakdown_oct = defaultdict(lambda: [0, 0.0])
    for r in oct_res:
        breakdown_oct[r["family"]][0] += 1; breakdown_oct[r["family"]][1] += r["net"]
    for k in sorted(breakdown_oct): print(k, breakdown_oct[k])
    print("--- entry-premium bands (all) ---")
    def band(r):
        e = r["entry"]
        return "<200" if e < 200 else "200-350" if e < 350 else "350-500" if e < 500 else ">=500"
    breakdown(band, "entry premium band")
    print("--- top3 trades ---")
    for r in sorted(res, key=lambda x: -x["net"])[:3]: print(r["date"], r["direction"], r["net"])
    print("ex-top3 total:", round(tot - sum(r["net"] for r in sorted(res, key=lambda x: -x["net"])[:3]), 2))

if __name__ == "__main__":
    main()
