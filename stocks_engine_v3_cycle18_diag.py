#!/usr/bin/env python3
"""V3 CYCLE 18 DIAG — INV-ABOVE incumbent population split by round.
Rebuilds the audited INV population with C2's exact pick (g1 gate,
round<=2, law {HINDALCO, UNITDSPR, TATASTEEL}, base exclusions) and
diffs it against the CURRENT (post-C16) book's INV-ABOVE rows — the
C13 deletion (INV-ABOVE x TATAMOTORS x LONG, 2 trades, 2025) postdates
C2, so the diff is expected to be exactly that frozen set. Prints the
round split per year on the CURRENT book rows (round recovered from
the population match) and the desert-month detail. Diagnosis only."""
import json, sys
from collections import Counter
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, load_books, WS

g, LABELS = boot()
print("BUILD CONTROLS ALL PASS in this pass")
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
g1, SYMBOLS = g["g1"], g["SYMBOLS"]
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
books = load_books(state["book_files"])

def key(r):
    return (r["date"], r["stock"], r["entry_time"], round(float(r["net"]), 2), r["direction"])

out = {}
for yr, days in (("2025", g["days25"]), ("2026", g["days26"])):
    pop = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            pop.extend(rs)
    above = [r for r in pop if r["round"] <= 2 and r["entry_time"] < "10:30"
             and (r["adr"] or 0) >= 3.0 and g1(r["date"])
             and r["direction"] == "LONG" and not wk(r["date"])
             and r["stock"] not in BASE_EXCL and r["stock"] not in LAW]
    inc = [t for t in books[yr] if t["comp"] == "INV-ABOVE"]
    cp, ci = Counter(map(key, above)), Counter(
        (t["date"], t["stock"], t["entry_time"], round(float(t["net"]), 2), t["dir"]) for t in inc)
    extra, missing = cp - ci, ci - cp
    print(f"{yr}: population {sum(cp.values())} vs incumbent {sum(ci.values())} | "
          f"pop-only {list(extra.items())} | book-only {list(missing.items())}")
    round_of = {}
    for r in above:
        round_of[key(r)] = r["round"]
    cur = []
    for t in inc:
        k = (t["date"], t["stock"], t["entry_time"], round(float(t["net"]), 2), t["dir"])
        assert k in round_of, f"{yr} book row not in population: {k}"
        cur.append({**t, "round": round_of[k]})
    by_round = {}
    for rnd in (1, 2):
        rs = [t for t in cur if t["round"] == rnd]
        by_round[rnd] = {"trades": len(rs), "net": round(sum(float(t["net"]) for t in rs), 2),
                         "months": {m: round(sum(float(t["net"]) for t in rs if t["date"][:7] == m), 2)
                                    for m in sorted({t["date"][:7] for t in rs})}}
        print(f"  CURRENT round {rnd}: {len(rs)} tr net {by_round[rnd]['net']} months {by_round[rnd]['months']}")
    desert = {m: [{"stock": t["stock"], "round": t["round"], "net": float(t["net"]), "date": t["date"]}
                  for t in cur if t["date"][:7] == m]
              for m in ("2025-06", "2025-07", "2025-10", "2025-11")}
    out[yr] = {"by_round": by_round, "desert": desert,
               "pop_only": [list(k) for k in extra], "book_only": [list(k) for k in missing]}
    for m, rows in desert.items():
        if rows: print(f"  {m}: {rows}")
json.dump(out, open(f"{WS}/v3_out/v3_cycle18_diag.json", "w"), indent=1)
print("wrote v3_out/v3_cycle18_diag.json")
