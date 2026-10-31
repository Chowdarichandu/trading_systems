#!/usr/bin/env python3
"""Build stock_event_calendar_2025.csv — SAME construction as the 2026 file.

Schema/judgement fields copied from stock_event_calendar_jan_oct_2026.csv:
stock, event_date, event_type, detail, after_market, source, source_url,
reaction_date, window_start, window_end, known_before_open, coverage.

Results dates (100 = 25 stocks x Q3 FY25/Q4 FY25/Q1 FY26/Q2 FY26) researched
2026-10-31 from TipRanks earnings-history pages (the 2026 file's own source
family) + Financial Express board meetings for INDUSTOWER. VALIDATION of the
method before use: TipRanks reproduced the 2026 file's event dates exactly
for every stock's four 2026-window rows (~96 rows checked), FE reproduced
INDUSTOWER's 4/4, and the 15 Q2 FY26 rows already present in the 2026 file
matched the fresh pulls 15/15.

Effective-reaction-date rule (identical to 2026): results announced after
market hours (after_market 'yes' or 'unverified') -> reaction = next trading
day; 'no' (verified public before/during market hours) -> same trading day;
non-trading-day event -> next trading day. News rows: public that day ->
same day, else next trading day. Trading days from NIFTY spot_daily in
data/full_hist. Dividend rows keyed to ex-date (2026 convention), inert for
scoring (not in N4's news set, ignored by P2F).

after_market evidence standard: default 'unverified' (the 2026 file's own
majority). Only exception: INDUSTOWER Q3 FY25 = 'yes' (Rediff news Jan 23,
2025 22:09 IST; market reaction Jan 24 per Capital Market). No P&L was
looked at while building this file — data infrastructure only.
"""
import csv
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
TR = "https://www.tipranks.com/stocks/in:{}/earnings"
# stock -> (tipranks slug, {quarter: event_date})  quarters: Q3FY25 Q4FY25 Q1FY26 Q2FY26
RES = {
 "GODREJCP": ("godrejcp", ["2025-01-24", "2025-05-06", "2025-08-07", "2025-10-31"]),
 "GLENMARK": ("glenmark", ["2025-02-14", "2025-05-23", "2025-08-14", "2025-11-14"]),
 "ITC": ("itc", ["2025-02-06", "2025-05-22", "2025-08-01", "2025-10-30"]),
 "RECLTD": ("recltd", ["2025-02-06", "2025-05-08", "2025-07-24", "2025-10-17"]),
 "TVSMOTOR": ("tvsmotor", ["2025-01-28", "2025-04-28", "2025-07-31", "2025-10-28"]),
 "UNITDSPR": ("unitdspr", ["2025-01-23", "2025-05-20", "2025-08-13", "2025-10-30"]),
 "OBEROIRLTY": ("oberoirlty", ["2025-01-20", "2025-04-28", "2025-07-21", "2025-10-15"]),
 "NTPC": ("ntpc", ["2025-01-25", "2025-05-24", "2025-07-29", "2025-10-30"]),
 "KALYANKJIL": ("kalyankjil", ["2025-01-30", "2025-05-08", "2025-08-07", "2025-11-07"]),
 "HDFCBANK": ("hdfcbank", ["2025-01-22", "2025-04-19", "2025-07-19", "2025-10-18"]),
 "NHPC": ("nhpc", ["2025-02-07", "2025-05-20", "2025-08-12", "2025-11-06"]),
 "PFC": ("pfc", ["2025-02-12", "2025-05-21", "2025-08-06", "2025-11-07"]),
 "IRCTC": ("irctc", ["2025-02-11", "2025-05-28", "2025-08-13", "2025-11-12"]),
 "WIPRO": ("wipro", ["2025-01-17", "2025-04-16", "2025-07-17", "2025-10-16"]),
 "NATIONALUM": ("nationalum", ["2025-02-10", "2025-05-21", "2025-08-07", "2025-11-07"]),
 "VEDL": ("vedl", ["2025-01-31", "2025-04-30", "2025-07-31", "2025-10-31"]),
 "HINDCOPPER": ("hindcopper", ["2025-02-08", "2025-05-27", "2025-08-14", "2025-11-11"]),
 "HINDZINC": ("hindzinc", ["2025-01-28", "2025-04-25", "2025-07-18", "2025-10-17"]),
 "HINDALCO": ("hindalco", ["2025-02-13", "2025-05-20", "2025-08-11", "2025-11-07"]),
 "TATASTEEL": ("tatasteel", ["2025-01-27", "2025-05-12", "2025-07-30", "2025-11-12"]),
 "ASTRAL": ("astral", ["2025-01-30", "2025-05-21", "2025-08-11", "2025-11-05"]),
 "BDL": ("bdl", ["2025-02-06", "2025-05-27", "2025-08-12", "2025-11-13"]),
 "OIL": ("oil", ["2025-02-07", "2025-05-21", "2025-08-12", "2025-11-14"]),
 "HINDUNILVR": ("hindunilvr", ["2025-01-22", "2025-04-24", "2025-07-31", "2025-10-23"]),
}
QLBL = ["Q3 FY25 / Dec-2024", "Q4 FY25 / Mar-2025", "Q1 FY26 / Jun-2025", "Q2 FY26 / Sep-2025"]
# INDUSTOWER from Financial Express board meetings (TipRanks has no page for it)
RES["INDUSTOWER"] = (None, ["2025-01-23", "2025-04-30", "2025-07-30", "2025-10-27"])
FE_INDUS = "https://www.financialexpress.com/market/indus-towers-ltd-share-price/board-meetings/"
AM_OVERRIDE = {("INDUSTOWER", "2025-01-23"): "yes"}  # Rediff 22:09 IST evidence

# news rows: (stock, type, event_date, reaction_date or None=same day, detail, source, source_url)
NEWS = [
 ("BDL", "large_order", "2025-01-16", None,
  "MoD MRSAM contract Rs2,960cr for Indian Navy, exchange filing intraday 13:49, stock +8% same day",
  "Moneycontrol / Sharekhan filing feed", "https://www.moneycontrol.com/news/business/markets/bharat-dynamics-shares-jump-8-on-rs-2-960-crore-defence-ministry-order-12912267.html"),
 ("BDL", "large_order", "2025-03-26", None,
  "MoD contract for supply of armament to Indian Armed Forces, disclosed to exchanges intraday 13:56",
  "Sharekhan filing feed (BDL announcements)", "https://www.sharekhan.com/stock/bharat-dynamics-ltd"),
 ("BDL", "large_order", "2025-11-13", "2025-11-14",
  "MoD INVAR anti-tank missile contract Rs2,095.70cr signed 13 Nov; shares surged 5% on 14 Nov",
  "EnrichMoney / MoD reports", "https://enrichmoney.in/blog/bharat-dynamics-share-price-news"),
 ("WIPRO", "management_change", "2025-02-14", "2025-02-17",
  "Wipro hires Accenture executive Amit Kumar as Global Head of Consulting, reporting to CEO; ET reported 14 Feb evening",
  "Economic Times", "http://widgets.economictimes.com/topic/wipro-ceo-resignation"),
 ("GLENMARK", "fda_approval", "2025-03-25", None,
  "US FDA ANDA approval for Olopatadine Hydrochloride Ophthalmic Solution USP 0.2% (OTC)",
  "Glenmark Pharmaceuticals announcements 2025", "https://glenmarkpharma.com/other-announcements-2025/"),
 ("ITC", "dividend", "2025-02-12", None,
  "Interim dividend Rs6.50/share, ex/record 12 Feb 2025",
  "5paisa / Financial Express dividend history", "https://www.5paisa.com/stocks/itc-share-price/itc-dividend"),
 ("ITC", "block_deal", "2025-05-28", None,
  "BAT sells 2.5% stake (31.3cr shares) ~Rs12,941cr via block deals; announced 27 May after market (LSE), executed pre-open 28 May",
  "Hindu BusinessLine / PTI", "https://www.thehindubusinessline.com/markets/bat-sells-25-per-cent-stake-in-itc-worth-15-billion-via-block-deals/article69628834.ece"),
 ("ITC", "dividend", "2025-05-28", None,
  "Final dividend Rs7.85/share, ex/record 28 May 2025",
  "5paisa / Financial Express dividend history", "https://www.5paisa.com/stocks/itc-share-price/itc-dividend"),
 ("HDFCBANK", "dividend", "2025-06-27", None,
  "Final dividend Rs22/share, ex/record 27 Jun 2025",
  "ET Now / Moneycontrol dividends", "https://www.etnownews.com/markets/hdfc-bank-dividend-2025-record-date-next-week-highest-ever-amount-since-stock-split-article-152121170"),
 ("HDFCBANK", "dividend", "2025-07-25", None,
  "Special interim dividend Rs5/share, ex-date 25 Jul 2025 (announced 19 Jul with Q1 results)",
  "Moneycontrol dividends", "https://www.moneycontrol.com/company-facts/hdfcbank/dividends/HDF01/"),
 ("HDFCBANK", "corporate_action", "2025-08-26", None,
  "First-ever 1:1 bonus issue ex-date 26 Aug 2025 (record date 27 Aug was a market holiday); price halved at open",
  "Business Standard / NDTV Profit", "https://www.business-standard.com/amp/markets/news/down-50pc-whats-behind-the-drop-in-hdfc-bank-share-price-today-125082600312_1.html"),
 ("ITC", "sector_policy", "2025-09-03", "2025-09-04",
  "GST Council 56th meeting approves 40% slab for tobacco under GST 2.0 (deferred until compensation-cess loans repaid); announced late evening 3 Sep (sector event, ITC-exposed)",
  "Times Now / Ministry of Finance release via Upstox", "https://www.timesnownews.com/business-economy/economy/from-cigarettes-to-colas-the-big-list-of-items-now-in-gsts-40-bracket-article-152654104"),
 ("TATASTEEL", "management_change", "2025-09-18", None,
  "Senior management changes filed 18 Sep: Uttam Singh re-designated VP Operations Kalinganagar, Sudhir Mehta appointed VP Operations Meramandali, effective 1 Dec 2025",
  "Tata Steel exchange filing via Business Standard", "https://www.business-standard.com/markets/capital-market-news/tata-steel-announces-change-in-senior-management-125091800530_1.html"),
 ("TVSMOTOR", "corporate_action", "2025-11-06", "2025-11-07",
  "TVS Motor to divest Rapido stake (Roppen Transportation) for Rs287.93cr to Accel India and MIH Investments; filed 6 Nov evening, shares in focus 7 Nov",
  "Moneycontrol / BusinessToday", "https://www.moneycontrol.com/news/business/accel-picks-up-stake-in-rapido-as-tvs-motor-company-sells-its-shares-13658361.html"),
]

days = sorted(r["date"][:10] for r in csv.DictReader(open(f"{WS}/data/full_hist/NIFTY/spot_daily.csv"))
              if r["date"][:10].startswith(("2024", "2025", "2026")))
dset = set(days)
def next_td(d):
    x = date.fromisoformat(d) + timedelta(days=1)
    while x.isoformat() not in dset:
        x += timedelta(days=1)
    return x.isoformat()
def td_offset(d, n):
    i = days.index(d)
    j = min(max(i + n, 0), len(days) - 1)
    return days[j]

rows = []
for sym, (slug, dates) in sorted(RES.items()):
    for qi, ev in enumerate(dates):
        am = AM_OVERRIDE.get((sym, ev), "unverified")
        # all 2025 results rows are 'unverified' or 'yes' -> next trading day
        react = next_td(ev)
        kb = "event_day_open" if react == ev else "reaction_day_onwards"
        if slug:
            src, surl = "TipRanks earnings history", TR.format(slug)
        else:
            src, surl = "Financial Express board meetings", FE_INDUS
        rows.append({"stock": sym, "event_date": ev, "event_type": "results",
                     "detail": QLBL[qi], "after_market": am, "source": src,
                     "source_url": surl, "reaction_date": react,
                     "window_start": td_offset(react, -5), "window_end": td_offset(react, 4),
                     "known_before_open": kb, "coverage": "verified_v2"})
for sym, et, ev, react, detail, src, surl in NEWS:
    r = react if react else ev
    kb = "event_day_open" if r == ev else "reaction_day_onwards"
    rows.append({"stock": sym, "event_date": ev, "event_type": et, "detail": detail,
                 "after_market": "n/a", "source": src, "source_url": surl,
                 "reaction_date": r,
                 "window_start": (date.fromisoformat(r) - timedelta(days=12)).isoformat(),
                 "window_end": (date.fromisoformat(r) + timedelta(days=12)).isoformat(),
                 "known_before_open": kb, "coverage": "curated_search_2026-10-31"})
rows.sort(key=lambda x: (x["event_date"], x["stock"]))
cols = ["stock", "event_date", "event_type", "detail", "after_market", "source",
        "source_url", "reaction_date", "window_start", "window_end",
        "known_before_open", "coverage"]
with open(f"{WS}/stock_event_calendar_2025.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
from collections import Counter
print("total rows:", len(rows), "| results:", sum(1 for r in rows if r["event_type"] == "results"),
      "| news:", sum(1 for r in rows if r["event_type"] != "results"))
print("per-stock results:", Counter(r["stock"] for r in rows if r["event_type"] == "results").most_common(3), "... all 25 x4:",
      all(v == 4 for v in Counter(r["stock"] for r in rows if r["event_type"] == "results").values()))
print("news by type:", Counter(r["event_type"] for r in rows if r["event_type"] != "results"))
print("reaction<=event anomalies:", [r for r in rows if r["reaction_date"] < r["event_date"]])
print("sample:", rows[0], rows[-1], sep="\n  ")
