#!/usr/bin/env python3
"""TARANG Round 6 — AMENDED universe build (owner amendment 2026-11-17 19:23 IST).

Selection basis (owner's ruling, same basis as SAPTA):
  (1) member of Nifty 100 or Nifty Midcap 150 (NSE index constituent
      CSVs, nsearchives.nseindia.com, read 2026-11-17 ~19:26 IST);
  (2) in the F&O segment (NSE fo_mktlots.csv, same read);
  (3) liquid + scorable: local daily dump (universe_daily) history
      from <= 2025-01-15, last bar 2026-11-13, >= 15 Oct-2026
      sessions, Oct-2026 median daily traded value >= Rs 1 crore
      (the programme's standing liquidity floor);
  (4) owner's Rs 2,000 cap at selection: latest dump close
      (2026-11-13) <= 2,000. Exclusions disclosed per name.

Lists below were transcribed from the three published NSE files as
rendered on 2026-11-17; counts are asserted (100 / 150 / 218) and
every symbol is checked against universe_daily/universe.csv.
Output: tarang6_universe.json (qualifying universe + exclusion ledger
+ per-name stats + data status). Research only; arms nothing.
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(ROOT, "universe_daily")

NIFTY100 = """ABB ADANIENSOL ADANIENT ADANIGREEN ADANIPORTS ADANIPOWER AMBUJACEM
APOLLOHOSP ASIANPAINT DMART AXISBANK BSE BAJAJ-AUTO BAJFINANCE BAJAJFINSV
BAJAJHLDNG BANKBARODA BEL BPCL BHARTIARTL BOSCHLTD BRITANNIA CGPOWER CANBK
CHOLAFIN CIPLA COALINDIA CUMMINSIND DLF DIVISLAB DRREDDY EICHERMOT ETERNAL
GAIL GODREJCP GRASIM HCLTECH HDFCAMC HDFCBANK HDFCLIFE HINDALCO HAL
HINDUNILVR HINDZINC POWERINDIA HYUNDAI ICICIBANK ITC IOC IRFC INFY INDIGO
JSWSTEEL JINDALSTEL JIOFIN KOTAKBANK LTM LT M&M MARUTI MAXHEALTH MAZDOCK
MUTHOOTFIN NTPC NESTLEIND ONGC PIDILITIND POLYCAB PFC POWERGRID PNB RELIANCE
SBILIFE MOTHERSON SHRIRAMFIN ENRIN SIEMENS SOLARINDS SBIN SUNPHARMA TVSMOTOR
TATACAP TCS TATACONSUM TMCV TMPV TATAPOWER TATASTEEL TECHM TITAN TORNTPHARM
TRENT ULTRACEMCO UNIONBANK VBL VAML VEDL IDEA WIPRO ZYDUSLIFE""".split()

MIDCAP150 = """360ONE AIAENG APLAPOLLO AUBANK ABBOTINDIA ATGL ABCAPITAL AJANTPHARM
ALKEM ANTHEM APARINDS ASHOKLEY ASTERDM ASTRAL AUROPHARMA AIIL BAJAJHFL
BALKRISIND BANKINDIA MAHABANK BERGEPAINT BDL BHARATFORG BHEL BHARTIHEXA
GROWW BIOCON BLUESTARCO CRISIL COCHINSHIP COFORGE COLPAL CONCOR COROMANDEL
DABUR DALBHARAT DIXON EMBASSY ENDURANCE ESCORTS EXIDEIND NYKAA FEDERALBNK
FACT FORTIS GVT&D GMRAIRPORT GICRE GLAXO GLENMARK MEDANTA GODFRYPHLP
GODREJIND GODREJPROP FLUOROCHEM HDBFS HAVELLS HEROMOTOCO HEXT HINDCOPPER
HINDPETRO HUDCO ICICILIFE ICICIGI ICICIAMC IDFCFIRSTB ITCHOTELS INDIANB
INDHOTEL IOB IRCTC IREDA INDUSTOWER INDUSINDBK NAUKRI IPCALAB JKCEMENT
JSWENERGY JSWINFRA JSL JUBLFOOD KPRMILL KEI KALYANKJIL LTF LTTS LGEINDIA
LICHSGFIN LAURUSLABS LENSKART LICI LINDEINDIA LLOYDSME LODHA LUPIN MRF
M&MFIN MANKIND MARICO MFSL MEESHO MOTILALOFS MPHASIS MCX NHPC NLCINDIA NMDC
NTPCGREEN NH NATIONALUM NAM-INDIA OBEROIRLTY OIL PAYTM OFSS POLICYBZR PIIND
PAGEIND PATANJALI PERSISTENT PETRONET PHOENIXLTD PIRAMALFIN PREMIERENE
PRESTIGE RECLTD RADICO RVNL SBICARD SRF SCHAEFFLER SHREECEM SAIL SUNDARMFIN
SUPREMEIND SUZLON SWIGGY TATACOMM TATAINVEST THERMAX TORNTPOWER TIINDIA
UNOMINDA UPL UBL UNITDSPR VMM VOLTAS WAAREEENER YESBANK""".split()

FO = """ADANIENSOL ANANDRATHI ADANIPORTS ADANIENT APLAPOLLO ALKEM ATHERENERG
AUROPHARMA BAJAJ-AUTO ABCAPITAL APOLLOHOSP BEL BHARATFORG BHARTIARTL BOSCHLTD
BLUESTARCO BAJAJFINSV BAJFINANCE ABB BSE CDSL BANDHANBNK BANKBARODA CIPLA
BIOCON COALINDIA CANBK DABUR COROMANDEL DIVISLAB COCHINSHIP CUB DMART
COFORGE COLPAL DRREDDY ETERNAL CROMPTON DATAPATTNS AMBUJACEM CUMMINSIND
DELHIVERY GODREJPROP DIXON DLF HAL HCLTECH 360ONE FORTIS GLENMARK GODREJCP
IEX INDHOTEL INDUSINDBK INFY HEROMOTOCO BANKINDIA GRASIM JIOFIN HAVELLS
JSWSTEEL HDFCAMC JUBLFOOD HINDALCO HYUNDAI ICICIBANK ICICIGI KOTAKBANK
LAURUSLABS LICHSGFIN INDIANB LT KAYNES LTM LUPIN ADANIGREEN INDUSTOWER
ADANIPOWER BRITANNIA MAHABANK INOXWIND IRFC ITC MAXHEALTH AMBER MAZDOCK MCX
KALYANKJIL MOTILALOFS NAVINFLUOR NESTLEIND NTPC NYKAA LTF OBEROIRLTY MANKIND
ONGC ANGELONE PAGEIND PETRONET PGEL PIDILITIND POWERGRID MFSL RADICO RELIANCE
NATIONALUM NAUKRI ASHOKLEY CONCOR ASTRAL SAIL AUBANK SHREECEM SONACOMS
SUPREMEIND OIL ASIANPAINT TECHM SYRMA TORNTPHARM ULTRACEMCO UNIONBANK
EICHERMOT PERSISTENT UNITDSPR AXISBANK PNB TVSMOTOR VOLTAS WAAREEENER WIPRO
UJJIVANSFB ZYDUSLIFE FEDERALBNK SBILIFE SOLARINDS SUNPHARMA SUZLON TATASTEEL
TITAN HDFCLIFE BDL HINDUNILVR HINDZINC CAMS VMM CGPOWER KPITTECH CHOLAFIN
LICI MANAPPURAM MARUTI MUTHOOTFIN NAM-INDIA GMRAIRPORT GODFRYPHLP NMDC PAYTM
HDFCBANK POWERINDIA HINDPETRO RBLBANK SBICARD SBIN SWIGGY TATAPOWER TCS
IREDA JINDALSTEL JSWENERGY UPL KEI VEDL LODHA IDFCFIRSTB INDIGO MARICO IOC
MPHASIS NBCC NHPC ICICILIFE M&M PATANJALI PFC PHOENIXLTD MOTHERSON PIIND
OFSS POLICYBZR POLYCAB PREMIERENE PRESTIGE RECLTD SAGILITY TATACONSUM
TATAELXSI RVNL TIINDIA TMPV TRENT SHRIRAMFIN VBL UNOMINDA BHEL BPCL FORCEMOT
GAIL KFINTECH KARURVYSYA SRF PNBHOUSING SIEMENS YESBANK ENRIN GVT&D
IDEA""".split()

FROZEN25 = """ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR
HINDZINC INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL
PFC RECLTD TATASTEEL TVSMOTOR UNITDSPR VEDL WIPRO""".split()

WIDE75 = """RELIANCE INFY ICICIBANK BHARTIARTL BSE TCS PCJEWELLER KOTAKBANK AXISBANK
ETERNAL SBIN BAJFINANCE LT M&M NETWEB CUPID TECHM DIVISLAB BHEL SHRIRAMFIN
HCLTECH MCX MARUTI COFORGE APOLLOHOSP PERSISTENT PAYTM IDEA ADANIPORTS
ADANIENT ADANIPOWER BEL WELCORP HAL DIXON INDHOTEL LAURUSLABS ULTRACEMCO
POWERINDIA POLICYBZR MAXHEALTH APOLLO SUZLON TITAN POWERGRID JIOFIN POLYCAB
GVT&D INDIGO EICHERMOT CHOLAFIN SUNPHARMA CHENNPETRO BAJAJ-AUTO COALINDIA
UNIONBANK HEROMOTOCO SWIGGY SOLARINDS FEDERALBNK APARINDS TRENT TDPOWERSYS
DRREDDY JSWSTEEL LICI SAIL TMPV CUMMINSIND SBILIFE NESTLEIND ADANIGREEN
CANBK ADANIENSOL TFCILTD""".split()

assert len(NIFTY100) == 100, len(NIFTY100)
assert len(MIDCAP150) == 150, len(MIDCAP150)
assert len(FO) == 218, len(FO)
assert len(set(FO)) == 218
assert len(FROZEN25) == 25 and len(WIDE75) == 75

uni = pd.read_csv(os.path.join(DUMP, "universe.csv"))
known = set(uni["symbol"])
for label, lst in (("NIFTY100", NIFTY100), ("MIDCAP150", MIDCAP150), ("FO", FO)):
    missing = [s for s in lst if s not in known]
    print(f"{label}: {len(lst)} symbols, not in universe.csv: {missing}")

members = sorted(set(NIFTY100) | set(MIDCAP150))
foset = set(FO)
print(f"index members (union): {len(members)}; in both indices: "
      f"{len(set(NIFTY100) & set(MIDCAP150))}")

man6 = {}
mpath = os.path.join(ROOT, "tarang6_fetch_manifest.json")
if os.path.exists(mpath):
    man6 = json.load(open(mpath)).get("symbols", {})

rows, excluded = [], []
for sym in members:
    p = os.path.join(DUMP, f"{sym}.parquet")
    if not os.path.exists(p):
        excluded.append({"symbol": sym, "reason": "no_dump_file"})
        continue
    df = pd.read_parquet(p, columns=["date", "close", "volume"])
    df["date"] = pd.to_datetime(df["date"])
    first, last = df["date"].min(), df["date"].max()
    oct26 = df[(df["date"] >= "2026-10-01") & (df["date"] <= "2026-10-31")]
    med_val_cr = float((oct26["close"] * oct26["volume"]).median() / 1e7) \
        if len(oct26) else 0.0
    latest_close = float(df.sort_values("date")["close"].iloc[-1])
    rec = {"symbol": sym,
           "in_nifty100": sym in set(NIFTY100),
           "in_midcap150": sym in set(MIDCAP150),
           "in_fo": sym in foset,
           "first_date": str(first.date()), "last_date": str(last.date()),
           "oct26_sessions": int(len(oct26)),
           "oct26_median_value_cr": round(med_val_cr, 2),
           "latest_close": latest_close}
    reason = None
    if not rec["in_fo"]:
        reason = "not_in_fo"
    elif first > pd.Timestamp("2025-01-15"):
        reason = f"history_starts_{rec['first_date']}"
    elif last != pd.Timestamp("2026-11-13"):
        reason = f"last_bar_{rec['last_date']}"
    elif rec["oct26_sessions"] < 15:
        reason = "thin_oct26_sessions"
    elif med_val_cr < 1.0:
        reason = "illiquid_oct26_median_below_1cr"
    elif latest_close > 2000.0:
        reason = "price_cap_above_2000"
    if reason:
        rec["reason"] = reason
        excluded.append(rec)
        continue
    if sym in FROZEN25:
        rec["data_status"] = "incumbent_tarang_vol"
    elif sym in WIDE75:
        st = man6.get(sym, {}).get("status")
        rec["data_status"] = "wide75_fetched" if st == "done" \
            else f"wide75_fetch_{st or 'pending'}"
    else:
        rec["data_status"] = "needs_fetch"
    rows.append(rec)

out = {"built": "2026-11-17 (owner amendment 19:23 IST)",
       "sources": {
           "nifty100": "nsearchives.nseindia.com/content/indices/ind_nifty100list.csv (read 2026-11-17)",
           "midcap150": "nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv (read 2026-11-17)",
           "fo": "nsearchives.nseindia.com/content/fo/fo_mktlots.csv (read 2026-11-17); 218 equity underlyings"},
       "counts": {"index_union": len(members), "qualifying": len(rows),
                  "excluded": len(excluded)},
       "qualifying": rows, "excluded": excluded}
with open(os.path.join(ROOT, "tarang6_universe.json"), "w") as f:
    json.dump(out, f, indent=1)

from collections import Counter
print("exclusion reasons:", Counter(e["reason"].split("_2")[0] if False else
      ("not_in_fo" if e["reason"] == "not_in_fo" else
       "history" if e["reason"].startswith("history") else
       "price_cap" if e["reason"] == "price_cap_above_2000" else e["reason"])
      for e in excluded))
print(f"QUALIFYING: {len(rows)}")
print("needs_fetch:", [r["symbol"] for r in rows if r["data_status"] == "needs_fetch"])
print("wide75 not yet done:", [r["symbol"] for r in rows
      if r["data_status"].startswith("wide75_fetch")])
print("incumbents qualifying:", [r["symbol"] for r in rows
      if r["data_status"] == "incumbent_tarang_vol"])
print("price-cap excluded:", [(e["symbol"], e["latest_close"]) for e in excluded
      if e["reason"] == "price_cap_above_2000"])
print("history excluded:", [(e["symbol"], e["first_date"]) for e in excluded
      if e["reason"].startswith("history")])
