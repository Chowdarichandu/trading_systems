#!/usr/bin/env python3
"""Line M1 — month-repair loop engine. Modes: anchor | diagnose | fix.
Equity cash, paper only, real Rs0. Provisional per 100 shares, Rs40/trade
(already deducted in the source dumps). Home 25 only, Jan-Oct 2026.
"""
import csv, json, os, sys
from collections import defaultdict

BASE = "/home/hatch/workspace/trading"
HOME25 = ["ASTRAL","BDL","GLENMARK","GODREJCP","HDFCBANK","HINDALCO",
          "HINDCOPPER","HINDUNILVR","HINDZINC","INDUSTOWER","IRCTC","ITC",
          "KALYANKJIL","NATIONALUM","NHPC","NTPC","OBEROIRLTY","OIL","PFC",
          "RECLTD","TATASTEEL","TVSMOTOR","UNITDSPR","VEDL","WIPRO"]
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]


def rd(path):
    with open(f"{BASE}/{path}") as f:
        return list(csv.DictReader(f))


def load_inv_long(exit_file="tuning_inv_T1_T125_S050_trades.csv"):
    out = []
    for r in rd(exit_file):
        if r["direction"] == "LONG":
            out.append({"date": r["date"], "stock": r["stock"], "comp": "INV-LONG",
                        "dir": "LONG", "net": float(r["net_rs_provisional_per100"]),
                        "setup": r["setup"], "round": r["round"],
                        "entry_time": r["entry_time"], "exit_reason": r["exit_reason"],
                        "event_status": r["event_status"],
                        "adr_pct": float(r["adr_pct"]), "day_gap_pct": float(r["day_gap_pct"])})
    return out


def load_inv_all(exit_file="tuning_inv_T1_T125_S050_trades.csv"):
    out = []
    for r in rd(exit_file):
        out.append({"date": r["date"], "stock": r["stock"], "comp": "INV1",
                    "dir": r["direction"], "net": float(r["net_rs_provisional_per100"]),
                    "setup": r["setup"], "round": r["round"],
                    "entry_time": r["entry_time"], "exit_reason": r["exit_reason"],
                    "event_status": r["event_status"],
                    "adr_pct": float(r["adr_pct"]), "day_gap_pct": float(r["day_gap_pct"])})
    return out


def load_n4():
    out = []
    for r in rd("eq_n4deep_v3_trades_T125_janoct.csv"):
        out.append({"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
                    "dir": r["direction"], "net": float(r["net_rs_provisional_per100"]),
                    "entry_time": r["entry_time"], "exit_reason": r["exit_reason"]})
    return out


def load_p2f(band=2.5):
    out = []
    for r in rd("stocks_tuning_event_V1_combined_trades.csv"):
        if r["leg"] == "P2F" and abs(float(r["reaction_ret_pct"])) >= band:
            out.append({"date": r["date"], "stock": r["symbol"], "comp": "P2F",
                        "dir": r["direction"], "net": float(r["net_rs"]),
                        "entry_time": r["entry_time"], "exit_reason": r["exit_reason"],
                        "R": r["R"], "reaction_ret_pct": float(r["reaction_ret_pct"])})
    return out


def load_book():
    return load_inv_long() + load_n4() + load_p2f()


def month_table(trades):
    t = {m: [0, 0.0] for m in MONTHS}
    for x in trades:
        m = x["date"][:7]
        if m in t:
            t[m][0] += 1
            t[m][1] += x["net"]
    return {m: (v[0], round(v[1], 2)) for m, v in t.items()}


def fmt_table(t, label):
    print(f"--- {label} ---")
    tot_n, tot = 0, 0.0
    for m in MONTHS:
        n, v = t[m]
        tot_n += n; tot += v
        print(f"  {m}: trades={n:4d} net={v:12.2f} {'RED' if v < 0 else ''}")
    print(f"  TOTAL: trades={tot_n} net={round(tot,2)}")
    return tot_n, round(tot, 2)


def daily_series(sym):
    rows = rd(f"data/progressive/{sym}/spot_daily.csv")
    return [(r["date"], float(r["close"])) for r in rows]


def nifty_regime():
    """date -> (prev_close, dma50_prev, depth_pct) using only prior days."""
    s = daily_series("NIFTY")
    closes = [c for _, c in s]
    out = {}
    for i, (d, _) in enumerate(s):
        if i >= 50:
            prev_close = closes[i - 1]
            dma = sum(closes[i - 50:i]) / 50.0
            out[d] = (prev_close, dma, (dma - prev_close) / dma * 100.0)
    return out


def mode_anchor():
    inv, n4, p2f = load_inv_long(), load_n4(), load_p2f()
    book = inv + n4 + p2f
    print(f"INV-LONG: {len(inv)} trades net={round(sum(x['net'] for x in inv),2)} (published 249 / +24185.73)")
    print(f"N4-V3:    {len(n4)} trades net={round(sum(x['net'] for x in n4),2)} (published 56 / +7990.43)")
    print(f"P2F2.5:   {len(p2f)} trades net={round(sum(x['net'] for x in p2f),2)} (published 39 / +15489.08)")
    t = month_table(book)
    n, tot = fmt_table(t, "COMBINED BOOK anchor (published: 344 / +47665.24, Feb only red -5533.46, Oct +6845.39)")
    pub = {"2026-01": (53, 6682.89), "2026-02": (57, -5533.46), "2026-03": (62, 7283.60),
           "2026-04": (42, 3339.69), "2026-05": (46, 14836.37), "2026-06": (21, 1305.20),
           "2026-07": (9, 3282.63), "2026-08": (16, 5802.73), "2026-09": (9, 3820.20),
           "2026-10": (29, 6845.39)}
    ok = all(t[m] == pub[m] for m in MONTHS) and (n, tot) == (344, 47665.24)
    print("COMBINED ANCHOR MATCHES T1 TO THE PAISA:", ok)

    # Fade home anchor from O1 P2 dump
    fade = [r for r in rd("stocks_O1_P2_1100_1_fade_fixed_T125S065_all_trades.csv")
            if r["symbol"] in HOME25]
    ft = {m: [0, 0.0] for m in MONTHS}
    for r in fade:
        ft[r["date"][:7]][0] += 1
        ft[r["date"][:7]][1] += float(r["net"])
    ft = {m: (v[0], round(v[1], 2)) for m, v in ft.items()}
    fn, ftot = fmt_table(ft, "FADE HOME anchor (published: 1073 / +4243.18, Oct +341.29)")
    pubf = {"2026-01": (133, 9778.35), "2026-02": (108, -2074.65), "2026-03": (168, 4682.40),
            "2026-04": (134, -12241.39), "2026-05": (97, 9952.21), "2026-06": (78, -326.34),
            "2026-07": (95, -5982.82), "2026-08": (68, -11963.12), "2026-09": (65, 12077.25),
            "2026-10": (127, 341.29)}
    okf = all(ft[m] == pubf[m] for m in MONTHS) and (fn, ftot) == (1073, 4243.18)
    print("FADE HOME ANCHOR MATCHES O2 RECORD TO THE PAISA:", okf)

    # ---- timing audits ----
    bad_n4 = [x for x in n4 if x["entry_time"] != "09:35"]
    print(f"AUDIT N4-V3 entry==09:35 (trigger complete 09:30): violations={len(bad_n4)}")
    p2f_all = []
    for r in rd("stocks_tuning_event_V1_combined_trades.csv"):
        if r["leg"] == "P2F":
            p2f_all.append(r)
    bad_t = [r for r in p2f_all if r["entry_time"] != "09:15"]
    # R+1 check against each symbol's own trading days
    cal = {s: [d for d, _ in daily_series(s)] for s in HOME25}
    bad_r1 = []
    for r in p2f_all:
        days = cal[r["symbol"]]
        if r["R"] in days:
            nxt = days[days.index(r["R"]) + 1] if days.index(r["R"]) + 1 < len(days) else None
            if nxt != r["date"]:
                bad_r1.append((r["symbol"], r["R"], r["date"], nxt))
    print(f"AUDIT P2F entry==09:15: violations={len(bad_t)}; entry==R+1 trading day: violations={len(bad_r1)}")
    reg = nifty_regime()
    inv_dates = sorted({x["date"] for x in inv})
    bad_reg = [d for d in inv_dates if d not in reg or reg[d][0] > reg[d][1]]
    print(f"AUDIT INV-LONG dates satisfy prev_close<=50DMA (recomputed): {len(inv_dates)} dates, violations={len(bad_reg)} {bad_reg[:5]}")
    bad_f = [r for r in fade if r["entry_time"] != "11:00" or r["meas_time"] != "11:00"]
    print(f"AUDIT FADE home entry_time==meas_time==11:00: violations={len(bad_f)}")
    json.dump({"combined": {m: t[m] for m in MONTHS}, "fade_home": {m: ft[m] for m in MONTHS}},
              open(f"{BASE}/stocks_M1_anchor.json", "w"), indent=1)


def agg(trades, key):
    d = defaultdict(lambda: [0, 0.0, 0])
    for x in trades:
        k = key(x)
        d[k][0] += 1
        d[k][1] += x["net"]
        d[k][2] += 1 if x["net"] > 0 else 0
    return sorted(d.items(), key=lambda kv: kv[1][1])


def show(label, rows):
    print(f"  [{label}]")
    for k, (n, v, w) in rows:
        print(f"    {k}: n={n} net={round(v,2)} win={w}/{n}")


def stock_dma(sym):
    """date -> (prev_close, dma20_prev) from the stock's own daily bars."""
    s = daily_series(sym)
    closes = [c for _, c in s]
    out = {}
    for i, (d, _) in enumerate(s):
        if i >= 20:
            out[d] = (closes[i - 1], sum(closes[i - 20:i]) / 20.0)
    return out


def mode_diagnose():
    book = load_book()
    feb = [x for x in book if x["date"][:7] == "2026-02"]
    print(f"FEBRUARY combined: {len(feb)} trades net={round(sum(x['net'] for x in feb),2)}")
    show("by component", agg(feb, lambda x: x["comp"]))
    show("by direction", agg(feb, lambda x: x["dir"]))
    inv = load_inv_long()
    invf = [x for x in inv if x["date"][:7] == "2026-02"]
    print(f"INV-LONG Feb: {len(invf)} trades net={round(sum(x['net'] for x in invf),2)}")
    show("INV Feb by setup", agg(invf, lambda x: x["setup"]))
    show("INV Feb by round", agg(invf, lambda x: f"round{x['round']}"))
    show("INV Feb by exit", agg(invf, lambda x: x["exit_reason"]))
    show("INV Feb by event", agg(invf, lambda x: x["event_status"]))
    show("INV Feb by stock", agg(invf, lambda x: x["stock"]))
    show("INV Feb by entry bucket", agg(invf, lambda x: "before10" if x["entry_time"] < "10:00"
                                       else ("10-12" if x["entry_time"] < "12:00" else "after12")))
    show("INV Feb by gap sign", agg(invf, lambda x: "gap_down" if x["day_gap_pct"] < 0 else "gap_up/flat"))
    show("INV Feb by date", agg(invf, lambda x: x["date"]))
    # Nifty depth (prev close below 50DMA by %) on INV-LONG trades, Feb vs all
    reg = nifty_regime()
    def depth_band(x):
        dep = reg[x["date"]][2]
        return "shallow<0.5%" if dep < 0.5 else ("0.5-1.5%" if dep < 1.5 else "deep>=1.5%")
    show("INV ALL months by Nifty depth band", agg(inv, depth_band))
    show("INV Feb by Nifty depth band", agg(invf, depth_band))
    # ADR bands, all months vs Feb
    def adr_band(x):
        return "adr<3" if x["adr_pct"] < 3 else ("3-4.5" if x["adr_pct"] < 4.5 else ">=4.5")
    show("INV ALL by ADR band", agg(inv, adr_band))
    show("INV Feb by ADR band", agg(invf, adr_band))
    # DBL counterfactual on INV-LONG trades (stock prev close <= own 20DMA)
    dmas = {s: stock_dma(s) for s in HOME25}
    def is_dbl(x):
        v = dmas[x["stock"]].get(x["date"])
        return v is not None and v[0] <= v[1]
    inv_dbl = [x for x in inv if is_dbl(x)]
    inv_nodbl = [x for x in inv if not is_dbl(x)]
    print(f"INV-LONG split by DBL condition (recomputed): DBL-pass {len(inv_dbl)} net={round(sum(x['net'] for x in inv_dbl),2)} | "
          f"DBL-fail {len(inv_nodbl)} net={round(sum(x['net'] for x in inv_nodbl),2)}")
    f_dbl = [x for x in invf if is_dbl(x)]
    f_nodbl = [x for x in invf if not is_dbl(x)]
    print(f"  Feb: DBL-pass {len(f_dbl)} net={round(sum(x['net'] for x in f_dbl),2)} | DBL-fail {len(f_nodbl)} net={round(sum(x['net'] for x in f_nodbl),2)}")
    # Actual DBL-LONG dump (Line 1b frozen candidate) month table
    dbl = []
    for r in rd("tuning_inv_L1b_S2_DBL_LONG_T125_S050_trades.csv"):
        dbl.append({"date": r["date"], "stock": r.get("stock") or r.get("symbol"),
                    "net": float(r["net_rs_provisional_per100"])})
    print(f"DBL-LONG dump: {len(dbl)} trades net={round(sum(x['net'] for x in dbl),2)} (published 133 / +24327.37)")
    fmt_table(month_table(dbl), "DBL-LONG month table")
    # INV-LONG at T100 exit (existing tuning dump) month table
    inv100 = load_inv_long("tuning_inv_T1_T100_S050_trades.csv")
    print(f"INV-LONG@T100: {len(inv100)} trades net={round(sum(x['net'] for x in inv100),2)}")
    fmt_table(month_table(inv100), "INV-LONG@T100 month table")
    # Book if INV-LONG swapped to DBL-LONG / to T100 (DIAGNOSTIC ONLY - not scored as fix yet)
    n4, p2f = load_n4(), load_p2f()
    fmt_table(month_table(dbl + n4 + p2f), "DIAGNOSTIC book: DBL-LONG + N4 + P2F")
    fmt_table(month_table(inv100 + n4 + p2f), "DIAGNOSTIC book: INV-LONG@T100 + N4 + P2F")
    # N4/P2F February detail
    for comp, rows in (("N4-V3", n4), ("P2F", p2f)):
        f = [x for x in rows if x["date"][:7] == "2026-02"]
        print(f"{comp} Feb: {len(f)} trades net={round(sum(x['net'] for x in f),2)}")
        show(f"{comp} Feb by stock", agg(f, lambda x: x["stock"]))


def judge(book, label, base_feb_trades=57):
    t = month_table(book)
    feb_n, feb_v = t["2026-02"]
    a = feb_v > 0
    b = all(t[m][1] > 0 for m in MONTHS if m != "2026-02")
    c = feb_n >= 23
    print(f"== {label}: Feb trades={feb_n} (floor 23) net={feb_v} | (a) Feb>0: {a} | "
          f"(b) all other months>0: {b} | (c) activity: {c} | ACCEPT: {a and b and c}")
    n, tot = fmt_table(t, label)
    reds = [m for m in MONTHS if t[m][1] <= 0]
    print(f"   months not positive: {reds}")
    return a and b and c, t


def mode_fix():
    n4, p2f = load_n4(), load_p2f()
    inv = load_inv_long()
    results = {}
    # MF-1: INV-LONG event-window exclusion
    inv1 = [x for x in inv if x["event_status"] != "event_window"]
    print(f"MF-1 leg: INV-LONG no-event {len(inv1)} trades net={round(sum(x['net'] for x in inv1),2)}")
    results["MF-1"], _ = judge(inv1 + n4 + p2f, "MF-1 book (INV-LONG event-window exclusion)")
    # MF-2: DBL-LONG leg swap
    dbl = []
    for r in rd("tuning_inv_L1b_S2_DBL_LONG_T125_S050_trades.csv"):
        dbl.append({"date": r["date"], "stock": r.get("stock") or r.get("symbol"), "comp": "DBL-LONG",
                    "dir": "LONG", "net": float(r["net_rs_provisional_per100"])})
    results["MF-2"], _ = judge(dbl + n4 + p2f, "MF-2 book (DBL-LONG leg swap)")
    # MF-3: INV-LONG T125/S065 leg
    inv65 = load_inv_long("tuning_inv_T1_T125_S065_trades.csv")
    print(f"MF-3 leg: INV-LONG@S065 {len(inv65)} trades net={round(sum(x['net'] for x in inv65),2)}")
    results["MF-3"], _ = judge(inv65 + n4 + p2f, "MF-3 book (INV-LONG T125/S065)")
    # MF-4: INV-LONG ADR>=4.5 only
    inv45 = [x for x in inv if x["adr_pct"] >= 4.5]
    print(f"MF-4 leg: INV-LONG ADR>=4.5 {len(inv45)} trades net={round(sum(x['net'] for x in inv45),2)}")
    results["MF-4"], _ = judge(inv45 + n4 + p2f, "MF-4 book (INV-LONG ADR>=4.5 only)")
    print("SUMMARY:", results)


if __name__ == "__main__":
    if sys.argv[1] == "anchor":
        mode_anchor()
    elif sys.argv[1] == "diagnose":
        mode_diagnose()
    elif sys.argv[1] == "fix":
        mode_fix()
    print("DONE", sys.argv[1])
