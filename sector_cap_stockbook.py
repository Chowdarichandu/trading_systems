#!/usr/bin/env python3
"""SECTOR-CAP RETEST — Stock Book (build_book machinery) on the
capped enlarged universe (frozen 25 + 12 capped additions),
within-machinery comparison vs the additions test's 25-name control
(wide100_stockbook_sector25w_*, cross-checked by recomputation).

The Rs3,000 cap is applied as an entry filter on the assembled book
(the book's own law, apply_law, is likewise a post-assembly filter):
a trade whose ENTRY price exceeds Rs3,000 is removed and counted as
cap-blocked. build_book rows carry exit + net but not entry; the
entry price is recovered exactly as implied = exit -/+ (net+40)/100
(LONG/SHORT) — the book's own fill arithmetic (per 100 shares,
Rs40/trade) — and VALIDATED against the 5-min stores over the full
population: every implied entry must equal the entry bar's open or
the prior bar's close (the two entry conventions the components
use). Validation counts are reported; the gate uses the implied
entry (the price the book's net was actually computed from).
Caveat, stated in the report: component-internal sequencing (e.g.
INV-ABOVE intra-day chains) is not re-simulated after removal.
Research only. Basis: equity cash, per 100 shares PROVISIONAL,
Rs40/trade."""
import csv, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import wide100_stockbook as SB

WS = "/home/hatch/workspace/trading"
ROOT = f"{WS}/data/wide100"
CAP = 3000.0
COST = 40.0
FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]
ADD_CAP = ["SBILIFE", "ICICIBANK", "SBIN", "RELIANCE", "INFY",
           "BHARTIARTL", "SUNPHARMA", "AMBUJACEM", "BHEL", "MAXHEALTH",
           "TMPV", "ASIANPAINT"]


def load_rows(path):
    rows = []
    for r in csv.DictReader(open(path)):
        r["net"] = float(r["net"])
        r["exit"] = float(r["exit"]) if r["exit"] not in ("", None) else None
        rows.append(r)
    return rows


def windows(rows):
    return {
        "2025_jan_oct": [t for t in rows if t["window"] == "2025"
                         and t["date"] <= "2025-10-31"],
        "2026_jan_oct": [t for t in rows if t["window"] == "2026"
                         and t["date"] <= "2026-10-31"],
        "november": [t for t in rows if t["window"] == "november"],
    }


def implied_entry(t):
    if t["dir"] == "LONG":
        return t["exit"] - (t["net"] + COST) / 100.0
    return t["exit"] + (t["net"] + COST) / 100.0


_bars = {}
def bars(sym):
    if sym not in _bars:
        p = f"{ROOT}/{sym}/spot_5m.csv"
        d = {}
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                d[(r["timestamp"][:10], r["timestamp"][11:16])] = (
                    float(r["open"]), float(r["close"]))
        _bars[sym] = d
    return _bars[sym]


def prev_stamp(stamp):
    hh, mm = int(stamp[:2]), int(stamp[3:5]) - 5
    if mm < 0:
        hh -= 1
        mm += 60
    return f"{hh:02d}:{mm:02d}"


def validate(rows):
    """Every implied entry must match the entry bar's open or the
    prior bar's close within Rs0.011. Returns counts + failures."""
    ok_open = ok_prevclose = 0
    fails = []
    for t in rows:
        e = implied_entry(t)
        b = bars(t["stock"])
        bar = b.get((t["date"], t["entry_time"]))
        prev = b.get((t["date"], prev_stamp(t["entry_time"])))
        if bar and abs(bar[0] - e) < 0.011:
            ok_open += 1
        elif prev and abs(prev[1] - e) < 0.011:
            ok_prevclose += 1
        else:
            fails.append(dict(comp=t["comp"], date=t["date"],
                              stock=t["stock"], dir=t["dir"],
                              entry_time=t["entry_time"],
                              implied=round(e, 2),
                              bar_open=(bar[0] if bar else None),
                              prev_close=(prev[1] if prev else None)))
    return dict(checked=len(rows), match_entry_open=ok_open,
                match_prev_close=ok_prevclose, unmatched=len(fails),
                unmatched_rows=fails[:20])


def added_block(rows):
    sel = [t for t in rows if t["stock"] in ADD_CAP]
    by_name = {}
    for t in sel:
        by_name[t["stock"]] = round(by_name.get(t["stock"], 0.0)
                                    + t["net"], 2)
    return dict(trades=len(sel), net=round(sum(t["net"] for t in sel), 2),
                names_traded=len(by_name), by_name=by_name)


def main():
    # ---- control cross-check: recompute the additions test's
    # 25-name control stats from its own trades CSV
    ctl_json = json.load(open(f"{WS}/wide100_stockbook_sector25w_results.json"))
    ctl_rows = load_rows(f"{WS}/wide100_stockbook_sector25w_trades.csv")
    chk = {}
    for wname, jname in (("2025_jan_oct", "2025_jan_oct"),
                         ("2026_jan_oct", "2026_jan_oct"),
                         ("november", "november")):
        s = SB.stats(windows(ctl_rows)[wname])
        j = ctl_json["windows"][jname]
        chk[wname] = all(s[k] == j[k] for k in
                         ("trades", "net", "wr", "ex_top3", "max_drawdown"))
    print("CONTROL cross-check (recomputed == sector25w JSON):", chk,
          flush=True)
    if not all(chk.values()):
        return 2

    # ---- enlarged capped-universe build (uncapped generation)
    rc = SB.run_build(ROOT, FROZEN25 + ADD_CAP, "sectorcap")
    if rc != 0:
        return rc
    rows = load_rows(f"{WS}/wide100_stockbook_sectorcap_trades.csv")
    val = validate(rows)
    print(f"ENTRY-PRICE VALIDATION: {val['checked']} checked, "
          f"{val['match_entry_open']} entry-open, "
          f"{val['match_prev_close']} prev-close, "
          f"{val['unmatched']} unmatched", flush=True)

    win = windows(rows)
    out = {"cap": CAP, "additions": ADD_CAP,
           "control25w": {k: ctl_json["windows"][k] for k in
                          ("2025_jan_oct", "2026_jan_oct", "november")},
           "control_crosscheck": chk,
           "entry_validation": val, "windows": {}, "trades": []}
    for wname in ("2025_jan_oct", "2026_jan_oct", "november"):
        wrows = win[wname]
        kept = [t for t in wrows if implied_entry(t) <= CAP]
        blocked = [t for t in wrows if implied_entry(t) > CAP]
        b_by = {}
        for t in blocked:
            b_by[t["stock"]] = b_by.get(t["stock"], 0) + 1
        out["windows"][wname] = dict(
            uncapped=SB.stats(wrows), capped=SB.stats(kept),
            added=added_block(kept),
            blocked=dict(entries_blocked=len(blocked), by_name=b_by,
                         net_of_blocked=round(
                             sum(t["net"] for t in blocked), 2)))
        print(f"[{wname}] uncapped {out['windows'][wname]['uncapped']['net']} "
              f"-> capped {out['windows'][wname]['capped']['net']} "
              f"(blocked {len(blocked)})", flush=True)
        for t in kept:
            out["trades"].append(dict(
                book="Stock Book", run="enlarged37_capped", window=wname,
                comp=t["comp"], date=t["date"], sym=t["stock"],
                side=t["dir"], entry=round(implied_entry(t), 2),
                exit=t["exit"], net=t["net"],
                added=t["stock"] in ADD_CAP))
    json.dump(out, open(f"{WS}/sector_cap_stockbook_results.json", "w"),
              indent=1)
    print("WROTE sector_cap_stockbook_results.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
