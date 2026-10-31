"""LINE 7 STEP 2b — re-score MOVER-A October 2026 chains at 1-min resolution.

Legs taken verbatim from mover_A_old_trades.csv / mover_A_ext_trades.csv
(October rows only): same chain composition, same entry MOMENTS (recorded
entry_time = a 5-min slot). ONE change: entry price = open of the first
1-min bar of that slot; exits scanned at 1-min resolution.
Mover exit logic (frozen, from stocks_tuning_mover.build_batt +
replay_plain): target +1.25%, stop -0.5% of entry, stop checked before
target within a bar, square-off at the close of the 15:10 5-min bar
(= close of the 15:14 minute; minutes 15:10-15:14 are still stop/target
checked first, exactly as the 15:10 5-min bar is). Net = gross - Rs40/leg,
gross = 100 * sign * (exit - entry), provisional per 100 shares.

VALIDATION: the same legs are first re-run on 5-min bars AGGREGATED from
the fetched 1-min data; exit_reason / exit / gross must reproduce the
recorded CSV values (2dp tolerance) before the 1-min pass is trusted.
"""
import csv, json, os, collections
import pandas as pd

BASE = os.path.expanduser("~/workspace/trading")
D1 = f"{BASE}/data/1min_stocks_oct2026"
COST = 40.0
TP, SP = 1.25, 0.5

_cache = {}
def day_minutes(which, sym, day):
    key = (which, sym)
    if key not in _cache:
        df = pd.read_csv(f"{D1}/{which}/{sym}.csv", dtype=str)
        df["day"] = df["timestamp"].str[:10]
        df["hm"] = df["timestamp"].str[11:16]
        for c in ("open", "high", "low", "close"):
            df[c] = df[c].astype(float)
        _cache[key] = df
    df = _cache[key]
    d = df[df["day"] == day]
    return list(d.itertuples(index=False))


def replay(bars, entry_i, sign, entry, square_hm=None):
    """bars: list of (hm, open, high, low, close). Generic replay_plain:
    stop before target; square-off when the 15:10 bar completes unhit
    (for 5-min bars pass square_hm='15:10' meaning the bar STARTING 15:10;
    for 1-min bars the completing minute is 15:14)."""
    target = entry * (1 + sign * TP / 100)
    stop = entry * (1 - sign * SP / 100)
    for j in range(entry_i, len(bars)):
        hm, o, h, l, c = bars[j]
        if sign == 1:
            if l <= stop:
                return "stop", stop, hm
            if h >= target:
                return "target", target, hm
        else:
            if h >= stop:
                return "stop", stop, hm
            if l <= target:
                return "target", target, hm
        if hm == square_hm:
            return "square_off", c, hm
    hm, o, h, l, c = bars[-1]
    return "square_off", c, hm


def main():
    legs = []
    for which, fn in (("old", "mover_A_old_trades.csv"), ("ext", "mover_A_ext_trades.csv")):
        with open(f"{BASE}/{fn}") as f:
            for r in csv.DictReader(f):
                if r["date"].startswith("2026-10"):
                    r["univ"] = which
                    legs.append(r)
    print(f"October legs: {len(legs)}; dates {min(r['date'] for r in legs)}..{max(r['date'] for r in legs)}")

    out_legs, val_fail = [], 0
    for r in legs:
        mins = day_minutes(r["univ"], r["symbol"], r["date"])
        assert len(mins) == 375, (r["symbol"], r["date"], len(mins))
        mbars = [(m.hm, m.open, m.high, m.low, m.close) for m in mins]
        sign = 1 if r["dir"] == "LONG" else -1
        ei = next(i for i, b in enumerate(mbars) if b[0] == r["entry_time"])
        entry1 = mbars[ei][1]

        # --- validation: aggregate to 5-min, replay identically ---
        agg = {}
        for hm, o, h, l, c in mbars:
            slot = hm[:3] + f"{(int(hm[3:5]) // 5) * 5:02d}"
            if slot not in agg:
                agg[slot] = [slot, o, h, l, c]
            else:
                a = agg[slot]
                a[2] = max(a[2], h); a[3] = min(a[3], l); a[4] = c
        bars5 = [tuple(v) for v in agg.values()]
        e5i = next(i for i, b in enumerate(bars5) if b[0] == r["entry_time"])
        entry5 = bars5[e5i][1]
        er5, ep5, et5 = replay(bars5, e5i, sign, entry5, square_hm="15:10")
        gross5 = 100.0 * sign * (ep5 - entry5)
        ok = (er5 == r["exit_reason"] and abs(ep5 - float(r["exit"])) <= 0.011
              and abs(gross5 - float(r["gross"])) <= 0.02 and abs(entry5 - float(r["entry"])) <= 0.006)
        if not ok:
            val_fail += 1
            print(f"VAL FAIL {r['univ']} {r['date']} {r['symbol']} r{r['round']}: "
                  f"agg=({er5},{ep5:.2f},{gross5:.2f},e{entry5}) vs csv=({r['exit_reason']},{r['exit']},{r['gross']},e{r['entry']})")

        # --- 1-min pass ---
        er1, ep1, et1 = replay(mbars, ei, sign, entry1, square_hm="15:14")
        gross1 = 100.0 * sign * (ep1 - entry1)
        out_legs.append({
            "univ": r["univ"], "date": r["date"], "symbol": r["symbol"],
            "dir": r["dir"], "round": int(r["round"]), "leg": r["leg"],
            "entry_time": r["entry_time"], "entry_csv": float(r["entry"]),
            "entry_1m": round(entry1, 4),
            "exit_reason_5m": r["exit_reason"], "exit_5m": float(r["exit"]),
            "exit_time_5m": r["exit_time"], "gross_5m": float(r["gross"]),
            "net_5m": float(r["net"]),
            "exit_reason_1m": er1, "exit_1m": round(ep1, 4), "exit_time_1m": et1,
            "gross_1m": round(gross1, 2), "net_1m": round(gross1 - COST, 2),
            "val_ok": ok})
    print(f"validation failures: {val_fail}/{len(legs)}")

    with open(f"{BASE}/line7_moverA_oct_1min_legs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_legs[0].keys()))
        w.writeheader(); w.writerows(out_legs)

    def cls(x):
        return "win" if x > 0 else ("loss" if x < 0 else "flat")

    chains = collections.defaultdict(list)
    for l in out_legs:
        chains[(l["univ"], l["date"], l["symbol"])].append(l)
    rows, trans, reason_trans = [], collections.Counter(), collections.Counter()
    for k, ls in sorted(chains.items()):
        n5 = round(sum(l["net_5m"] for l in ls), 2)
        n1 = round(sum(l["net_1m"] for l in ls), 2)
        trans[(cls(n5), cls(n1))] += 1
        for l in ls:
            reason_trans[(l["exit_reason_5m"], l["exit_reason_1m"])] += 1
        rows.append({"univ": k[0], "date": k[1], "symbol": k[2], "legs": len(ls),
                     "net_5m": n5, "net_1m": n1, "delta": round(n1 - n5, 2),
                     "class_5m": cls(n5), "class_1m": cls(n1)})
    with open(f"{BASE}/line7_moverA_oct_1min_chains.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    summ = {}
    for scope in ("old", "ext", "pooled"):
        rs = rows if scope == "pooled" else [r for r in rows if r["univ"] == scope]
        summ[scope] = {
            "chains": len(rs), "legs": sum(r["legs"] for r in rs),
            "net_5m": round(sum(r["net_5m"] for r in rs), 2),
            "net_1m": round(sum(r["net_1m"] for r in rs), 2),
            "delta": round(sum(r["delta"] for r in rs), 2),
            "chains_class_changed": sum(1 for r in rs if r["class_5m"] != r["class_1m"])}
    res = {"summary": summ, "val_fail": val_fail, "legs_total": len(legs),
           "chain_transitions": {f"{a}->{b}": n for (a, b), n in sorted(trans.items())},
           "leg_reason_transitions": {f"{a}->{b}": n for (a, b), n in sorted(reason_trans.items())},
           "biggest_delta_chains": sorted(rows, key=lambda r: r["delta"])[:5] + sorted(rows, key=lambda r: -r["delta"])[:5]}
    json.dump(res, open(f"{BASE}/line7_moverA_oct_1min_results.json", "w"), indent=2, default=str)
    print(json.dumps(summ, indent=2))
    print("chain transitions:", res["chain_transitions"])
    print("leg reason transitions:", res["leg_reason_transitions"])


if __name__ == "__main__":
    main()
