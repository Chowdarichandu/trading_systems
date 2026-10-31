"""Family 2 — Volrix-for-stocks, frozen spec stocks_family2_volrix_for_stocks_frozen.md.
Paper only, cash intraday, no options. Trigger: prev-day close <= -2% vs close before.
Entry next trading day 09:15 open, exit 15:10 close, no stop/target.
Cooldown 10 trading sessions per stock after an entry. Cap 1/day, 1/stock/week,
ranking largest prev-day drop first.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
STOCKS = [s for s in SYMBOLS if s not in ("NIFTY","BANKNIFTY")]

def main():
    rows, trig_days = [], []
    for sym in STOCKS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        # trading days list for this stock (use its daily dates)
        dates = [d["date"].date().isoformat() for d in dl]
        last_entry_idx = -100
        for i in range(2, len(dl)):
            if not ("2026-01-01" <= dl[i]["date"].date().isoformat() <= "2026-10-28"):
                continue
            prev, prev2 = dl[i-1], dl[i-2]
            pct = (float(prev["close"])-float(prev2["close"]))/float(prev2["close"])*100
            if pct > -2.0:
                continue
            d = dl[i]["date"]
            day = spot[spot["date"] == d]
            if day.empty:
                continue
            trig_days.append((sym, d.date().isoformat(), round(pct,2)))
            # cooldown: entry index is i (trading-day index in dl); skip if within 10 sessions of last entry
            if i - last_entry_idx <= 10:
                continue
            entry = float(day.iloc[0]["open"])
            # 15:10 close: last candle with time <= 15:10, else last candle
            sub = day[day["time"] <= "15:10"]
            exitp = float(sub.iloc[-1]["close"]) if not sub.empty else float(day.iloc[-1]["close"])
            net = round((exitp-entry)*100 - 40, 2)
            rows.append({"symbol": sym, "date": d.date().isoformat(), "month": d.month,
                         "week": f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}",
                         "prev_day_drop_pct": round(pct,2), "entry": entry, "exit_price": exitp,
                         "net_rs": net, "direction": "LONG"})
            last_entry_idx = i
    unc = pd.DataFrame(rows)
    unc.to_csv("/home/hatch/workspace/trading/stocks_family2_volrix_uncapped_jan_oct_2026.csv", index=False)
    # cap 1/day, 1/stock/week, ranking largest drop first
    taken, used = [], set()
    for date, grp in unc.sort_values(["date","prev_day_drop_pct"]).groupby("date"):
        for _, t in grp.iterrows():
            if (t["symbol"], t["week"]) in used: continue
            taken.append(t); used.add((t["symbol"], t["week"])); break
    cap = pd.DataFrame(taken)
    cap.to_csv("/home/hatch/workspace/trading/stocks_family2_volrix_trades_jan_oct_2026.csv", index=False)
    for name, df in [("uncapped", unc), ("capped", cap)]:
        print(name, len(df), "net", df["net_rs"].sum() if len(df) else 0,
              "win", (df["net_rs"]>0).mean() if len(df) else 0,
              "exp", df["net_rs"].mean() if len(df) else 0,
              "days", df["date"].nunique() if len(df) else 0)
    print("trigger days (before cooldown/cap):", len(trig_days))
    print("month cumulative capped:", cap.groupby("month")["net_rs"].sum().cumsum().to_dict() if len(cap) else {})
    print("this week 26-29:", cap[cap["date"]>="2026-10-26"].to_dict("records") if len(cap) else [])
    print("per stock capped:", cap.groupby("symbol")["net_rs"].agg(["count","sum"]).to_dict() if len(cap) else {})

if __name__ == "__main__":
    main()
