"""LINE 4 Step 1 — results-event calendar for the NEW 25 (Jan-Oct 2026),
same method as stock_event_calendar_jan_oct_2026.csv: board-meeting dates
from Moneycontrol Board Meetings tables, cross-checked against Financial
Express board-meeting tables (web search, 2026-10-31; both agreed in every
case). after_market = "unverified" -> reaction_date = next trading day in
the stock's OWN fetched daily series (data/progressive_ext), mirroring the
original calendar's convention; blank when beyond 2026-10-28 (outside data).
window_start = 7 trading days before event, window_end = 7 trading days
after reaction (original convention, e.g. UNITDSPR rows). Q2 rows dated
after 2026-10-28 are included for completeness; the engines' window
filters exclude them. EICHERMOT Q2 FY27 is EXCLUDED: no confirmed board
date as of 2026-10-31 (NSE calendar listing suggested late Oct, TipRanks
estimated 6 Nov) — its R+1 would fall outside the window either way.
"""
import csv, os

TRADING = os.path.expanduser("~/workspace/trading")
EBASE = os.path.join(TRADING, "data/progressive_ext")
OUTF = os.path.join(TRADING, "stock_event_calendar_ext_jan_oct_2026.csv")
SRC = "Moneycontrol Board Meetings + Financial Express (web search 2026-10-31)"

# board-meeting (announcement) dates in chronological order per stock
EVENTS = {
    "RELIANCE":   ["2026-01-16", "2026-04-24", "2026-07-17", "2026-10-30"],
    "TCS":        ["2026-01-12", "2026-04-09", "2026-07-09", "2026-10-08"],
    "ICICIBANK":  ["2026-01-17", "2026-04-18", "2026-07-18", "2026-10-17"],
    "INFY":       ["2026-01-14", "2026-04-23", "2026-07-23", "2026-10-23"],
    "BHARTIARTL": ["2026-02-05", "2026-05-13", "2026-08-04", "2026-11-05"],
    "SBIN":       ["2026-02-07", "2026-05-08", "2026-08-07", "2026-11-03"],
    "LT":         ["2026-01-28", "2026-05-05", "2026-07-28", "2026-10-27"],
    "AXISBANK":   ["2026-01-26", "2026-04-25", "2026-07-18", "2026-10-17"],
    "KOTAKBANK":  ["2026-01-24", "2026-05-02", "2026-07-18", "2026-10-24"],
    "BAJFINANCE": ["2026-02-03", "2026-04-29", "2026-07-30", "2026-10-19"],
    "HCLTECH":    ["2026-01-12", "2026-04-21", "2026-07-13", "2026-10-12"],
    "MARUTI":     ["2026-01-28", "2026-04-28", "2026-07-31", "2026-10-27"],
    "SUNPHARMA":  ["2026-01-31", "2026-05-22", "2026-07-31", "2026-10-30"],
    "TITAN":      ["2026-02-10", "2026-05-08", "2026-08-07", "2026-11-05"],
    "M&M":        ["2026-02-11", "2026-05-05", "2026-07-30", "2026-11-05"],
    "ULTRACEMCO": ["2026-01-24", "2026-04-27", "2026-07-20", "2026-10-19"],
    "NESTLEIND":  ["2026-01-30", "2026-04-21", "2026-07-22", "2026-10-15"],
    "POWERGRID":  ["2026-01-30", "2026-05-15", "2026-08-05", "2026-11-01"],
    "ONGC":       ["2026-02-12", "2026-05-26", "2026-08-04", "2026-11-05"],
    "COALINDIA":  ["2026-02-12", "2026-04-27", "2026-07-27", "2026-10-29"],
    "JSWSTEEL":   ["2026-01-23", "2026-05-14", "2026-07-17", "2026-10-23"],
    "GRASIM":     ["2026-02-10", "2026-05-20", "2026-08-12", "2026-11-13"],
    "CIPLA":      ["2026-01-23", "2026-05-13", "2026-07-23", "2026-10-27"],
    "DRREDDY":    ["2026-01-21", "2026-05-12", "2026-07-22", "2026-10-23"],
    "EICHERMOT":  ["2026-02-10", "2026-05-22", "2026-07-29"],
}
QUARTERS = ["Q3 FY26 / Dec-2025", "Q4 FY26 / Mar-2026",
            "Q1 FY27 / Jun-2026", "Q2 FY27 / Sep-2026"]
HI = "2026-10-28"

def daily_dates(sym):
    p = os.path.join(EBASE, sym, "spot_daily.csv")
    with open(p) as f:
        return sorted(r["date"][:10] for r in csv.DictReader(f))

rows = []
for sym, dates in EVENTS.items():
    dd = daily_dates(sym)
    idx = {d: i for i, d in enumerate(dd)}
    for qi, ev in enumerate(dates):
        # reaction: first trading day strictly after event date, within data
        react = next((d for d in dd if d > ev), None)
        if react is None or react > HI:
            react = ""
        # window_start: 7 trading days before the event (anchor = first
        # trading day >= event date); window_end: 7 trading days after reaction
        anchor = next((i for i, d in enumerate(dd) if d >= ev), None)
        ws = dd[anchor - 7] if anchor is not None and anchor - 7 >= 0 else ""
        we = ""
        if react and react in idx and idx[react] + 7 < len(dd) and dd[idx[react] + 7] <= HI:
            we = dd[idx[react] + 7]
        rows.append({"stock": sym, "event_date": ev, "event_type": "results",
                     "detail": QUARTERS[qi], "after_market": "unverified",
                     "source": SRC, "source_url": "", "reaction_date": react,
                     "window_start": ws, "window_end": we,
                     "known_before_open": "reaction_day_onwards",
                     "coverage": "verified_v1_ext"})

cols = ["stock", "event_date", "event_type", "detail", "after_market", "source",
        "source_url", "reaction_date", "window_start", "window_end",
        "known_before_open", "coverage"]
with open(OUTF, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r["stock"], r["event_date"])):
        w.writerow(r)
print(f"wrote {OUTF}: {len(rows)} events for {len(EVENTS)} stocks")
inwin = [r for r in rows if r["reaction_date"] and r["reaction_date"] <= HI]
print(f"events with in-window reaction date: {len(inwin)}")
