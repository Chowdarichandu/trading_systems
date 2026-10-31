"""LINE 4 Step 1 fixup — refetch stocks whose original ISIN 400'd because the
ISIN changed after a stock split (Upstox serves only the CURRENT ISIN):
  KOTAKBANK  INE237A01028 -> INE237A01036 (1:5 split; new ISIN per current listings)
  BAJFINANCE INE296A01024 -> INE296A01032 (NSE circular NSE/CML/68472, 11 Jun 2025:
             "Change in ISIN - Bajaj Finance", sub-division Rs2 -> Re1, w.e.f. 16 Jun 2025)
  NESTLEIND  INE239A01016 -> INE239A01024 (1:10 split Jan 2024 changed the ISIN;
             INE239A01024 per post-split exchange/security lists)
  DRREDDY    INE089A01023 -> INE089A01031 (1:5 split Oct 2024, FV Rs5 -> Re1;
             INE089A01031 per Moneycontrol listing page / exchange listings)
Reuses fetch_vol_ext_janoct.fetch_5m / fetch_daily verbatim (same code path as
the main fetch); per-stock write block copied from its main(). Updates
keys_ext.json and fetch_counts.json for the refetched symbols.
"""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
import fetch_vol_ext_janoct as F

FIX = {"KOTAKBANK": "INE237A01036", "BAJFINANCE": "INE296A01032",
       "NESTLEIND": "INE239A01024", "DRREDDY": "INE089A01031"}

def main():
    keys = json.load(open(os.path.join(F.EBASE, "keys_ext.json")))
    counts_p = os.path.join(F.VBASE, "fetch_counts.json")
    summary = json.load(open(counts_p)) if os.path.exists(counts_p) else {}
    for sym, isin in FIX.items():
        key = f"NSE_EQ|{isin}"
        print(f"== FIXUP {sym} {key}", flush=True)
        vdir = os.path.join(F.VBASE, sym); edir = os.path.join(F.EBASE, sym)
        os.makedirs(vdir, exist_ok=True); os.makedirs(edir, exist_ok=True)
        f5 = F.fetch_5m(key)
        f5.to_csv(os.path.join(vdir, "spot_5m_vol.csv"), index=False)
        fd = F.fetch_daily(key)
        fd.to_csv(os.path.join(vdir, "daily_api.csv"), index=False)
        e5 = f5.copy()
        if not e5.empty:
            e5["timestamp"] = pd.to_datetime(e5["timestamp"]).dt.tz_localize(None)
            e5[["timestamp", "open", "high", "low", "close"]].to_csv(
                os.path.join(edir, "spot_5m.csv"), index=False)
            d = e5.copy(); d["date"] = d["timestamp"].dt.normalize()
            daily26 = d.groupby("date").agg(open=("open", "first"), high=("high", "max"),
                                            low=("low", "min"), close=("close", "last")).reset_index()
        else:
            daily26 = pd.DataFrame(columns=["date", "open", "high", "low", "close"])
        rows = []
        have = set(pd.to_datetime(daily26["date"]).dt.strftime("%Y-%m-%d")) if not daily26.empty else set()
        for _, r in fd.iterrows():
            ds = pd.to_datetime(r["timestamp"]).strftime("%Y-%m-%d")
            if ds < "2026-01-01" and ds not in have:
                rows.append({"date": pd.Timestamp(ds), "open": r["open"], "high": r["high"],
                             "low": r["low"], "close": r["close"]})
        daily_all = pd.concat([pd.DataFrame(rows), daily26]).sort_values("date") if rows or not daily26.empty else daily26
        daily_all.to_csv(os.path.join(edir, "spot_daily.csv"), index=False)
        summary[sym] = {"bars_5m": int(len(f5)), "daily_api_rows": int(len(fd)),
                        "daily_rows_total": int(len(daily_all))}
        keys[sym] = key
        print(f"== FIXUP {sym} DONE 5m={len(f5)} daily_api={len(fd)} daily_total={len(daily_all)}", flush=True)
    json.dump(keys, open(os.path.join(F.EBASE, "keys_ext.json"), "w"), indent=2)
    json.dump(summary, open(counts_p, "w"), indent=2)
    print("FIXUP ALL DONE", flush=True)

if __name__ == "__main__":
    main()
