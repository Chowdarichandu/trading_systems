#!/usr/bin/env python3
"""Historical proof stage 3: score Jan-Sep legs on real premiums with the
uniform October overlay (entry = open of option candle at the entry bar;
stop entry-50 checked before target entry+90 on every bar incl. entry bar;
square-off 15:10 close; cost Rs220; net=(exit-entry)*lot-220). October legs
are taken as already premium-scored in the frozen U1 B2/N1 files.
Outputs per-index trades CSVs + stats JSON."""
import json, csv
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
OUT = TR / "historical_proof_data"
COST = 220.0

def score_leg(l):
    p = OUT / f"candles_{l['tag']}.json"
    d = json.loads(p.read_text())
    cs = sorted(d["data"]["candles"], key=lambda c: c[0])
    bars = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs]
    et = l["entry_time"]
    seq = [b for b in bars if b[0] >= et]
    if not seq or seq[0][0] != et:
        return None, "no option candle at entry bar"
    entry = seq[0][1]
    stop, target = entry - 50.0, entry + 90.0
    lot = int(l["lot"])
    for (t, o, h, lo, cl) in seq:
        if t > "15:10": break
        if lo <= stop:
            return {"entry_premium": entry, "exit_premium": stop, "exit_time": t,
                    "exit_reason": "stop", "net_rs": round((stop - entry) * lot - COST, 2)}, None
        if h >= target:
            return {"entry_premium": entry, "exit_premium": target, "exit_time": t,
                    "exit_reason": "target", "net_rs": round((target - entry) * lot - COST, 2)}, None
        if t == "15:10":
            return {"entry_premium": entry, "exit_premium": cl, "exit_time": t,
                    "exit_reason": "square_off", "net_rs": round((cl - entry) * lot - COST, 2)}, None
    t, o, h, lo, cl = seq[-1]
    return {"entry_premium": entry, "exit_premium": cl, "exit_time": t,
            "exit_reason": "square_off", "net_rs": round((cl - entry) * lot - COST, 2)}, None

def main():
    legs = list(csv.DictReader(open(OUT / "legs_jansep.csv")))
    scored = {"BANKNIFTY": [], "NIFTY": []}
    for l in legs:
        s, err = score_leg(l)
        row = {"date": l["date"], "index": l["index"], "direction": l["direction"],
               "representative_system": l["representative_system"], "source_systems": l["source_systems"],
               "entry_time": l["entry_time"], "entry_spot": l["entry_spot"],
               "strike": l["strike"], "expiry": l["expiry"], "lot": l["lot"],
               "old_spot_net_rs": l["old_spot_net"], "old_spot_exit_reason": l["old_exit_reason"]}
        if s is None:
            row.update({"status": "NOT_COMPUTED", "not_computed_reason": err})
        else:
            row.update({"status": "COMPUTED", **s})
        scored[l["index"]].append(row)
    # October legs from frozen files (already premium-scored, same overlay)
    for fname, sym in [("index_options_U1_B2_bank_trades.csv", "BANKNIFTY"),
                       ("index_options_U1_N1_nifty_trades.csv", "NIFTY")]:
        for r in csv.DictReader(open(TR / fname)):
            if r["net_unit"] != "premium_per_1_lot":
                continue
            scored[sym].append({
                "date": r["date"], "index": sym, "direction": r["direction"],
                "representative_system": r["representative_system"], "source_systems": r["source_systems"],
                "entry_time": r["entry_time"], "entry_spot": "",
                "strike": int(float(r["strike"])), "expiry": r["expiry"],
                "lot": 30 if sym == "BANKNIFTY" else 65,
                "old_spot_net_rs": "", "old_spot_exit_reason": "",
                "status": "COMPUTED", "entry_premium": float(r["entry_value"]),
                "exit_premium": float(r["exit_value"]), "exit_time": r["exit_time"],
                "exit_reason": r["exit_reason"], "net_rs": float(r["net_rs"]),
                "note": "October leg, premium-scored in the frozen U1 run (same overlay), carried in unchanged"})
    stats = {}
    for sym, rows in scored.items():
        rows.sort(key=lambda x: (x["date"], x["entry_time"]))
        fname = "historical_proof_bank_B2_trades.csv" if sym == "BANKNIFTY" else "historical_proof_nifty_N1_trades.csv"
        fields = ["date","index","direction","representative_system","source_systems","entry_time","entry_spot",
                  "strike","expiry","lot","entry_premium","exit_premium","exit_time","exit_reason","net_rs",
                  "status","not_computed_reason","old_spot_net_rs","old_spot_exit_reason","note"]
        for r in rows: r.setdefault("not_computed_reason", ""); r.setdefault("note", "")
        with open(TR / fname, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r in rows: w.writerow({k: r.get(k, "") for k in fields})
        comp = [r for r in rows if r["status"] == "COMPUTED"]
        months = {}
        cum = 0.0; peak = 0.0; maxdd = 0.0; curve = []
        for r in comp:
            cum += float(r["net_rs"]); curve.append((r["date"], cum))
            peak = max(peak, cum); maxdd = max(maxdd, peak - cum)
        bym = defaultdict(list)
        for r in comp: bym[r["date"][:7]].append(r)
        mrows = []; run = 0.0
        for m in sorted(bym):
            rs = bym[m]; net = round(sum(float(x["net_rs"]) for x in rs), 2); run = round(run + net, 2)
            mrows.append({"month": m, "trades": len(rs),
                          "targets": sum(1 for x in rs if x["exit_reason"] == "target"),
                          "stops": sum(1 for x in rs if x["exit_reason"] == "stop"),
                          "square_offs": sum(1 for x in rs if x["exit_reason"] == "square_off"),
                          "full_target_pct": round(100.0 * sum(1 for x in rs if x["exit_reason"] == "target") / len(rs), 1),
                          "net": net, "cumulative": run, "cum_green": run > 0})
        total = round(sum(float(x["net_rs"]) for x in comp), 2)
        # sign disagreements Jan-Sep (old spot vs new premium)
        dis = []
        for r in comp:
            if r["old_spot_net_rs"] != "":
                old = float(r["old_spot_net_rs"]); new = float(r["net_rs"])
                if (old > 0) != (new > 0):
                    dis.append({"date": r["date"], "direction": r["direction"], "rep": r["representative_system"],
                                "old_spot_net": old, "premium_net": new, "swing": round(new - old, 2),
                                "premium_exit": r["exit_reason"]})
        dis.sort(key=lambda x: -abs(x["swing"]))
        stats[sym] = {"computed": len(comp), "not_computed": len(rows) - len(comp),
                      "total": total, "months": mrows, "max_drawdown": round(maxdd, 2),
                      "curve": curve, "disagreements": dis,
                      "targets": sum(1 for x in comp if x["exit_reason"] == "target"),
                      "stops": sum(1 for x in comp if x["exit_reason"] == "stop"),
                      "square_offs": sum(1 for x in comp if x["exit_reason"] == "square_off")}
        print(sym, "computed", len(comp), "nc", len(rows) - len(comp), "total", total, "maxdd", round(maxdd, 2))
    (OUT / "stats.json").write_text(json.dumps(stats, indent=1))
    print("done")

if __name__ == "__main__":
    main()
