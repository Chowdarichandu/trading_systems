# Geopolitics + global sentiment layer — Indian intraday stocks, 26–30 Oct 2026

**Paper only. No orders. Written Fri 2026-10-30, ~08:30 IST — i.e. BEFORE the 30 Oct Indian close.**
**Companion file:** `stocks_sentiment_tags_oct26_30.csv` — 125 rows (25 stocks × 5 days), columns: `date, stock, sentiment, factor, source`.

**Stocks covered (25):** GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC,
INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC,
HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR.

## 0. What is verified news vs what is a tag — read this first

- **Verified public news** = an item below with a named source + publication date. Figures quoted are as
  reported by that source (provisional exchange FII/DII data where stated). Where two reputable reports
  conflict, both are shown and neither is silently picked (see §6).
- **Tag / interpretation** = the `risk-on / risk-off / neutral` label in the CSV. It is **not** news.
  It is this report's classification of the day, using the rule in §1. A tag does **not** prove that
  sentiment caused any stock's move.
- **Company-specific global/geopolitical news:** for the 25 stocks individually, **no influencing news
  found** in the day-level sources checked for any stock on any day 26–30 Oct — i.e. no verified
  company-specific geopolitical item (sanction, export ban, contract, results-driven global shock)
  was found for GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER,
  KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO,
  TATASTEEL, ASTRAL, BDL, OIL or HINDUNILVR. What the CSV records for each stock-day is therefore the
  **market-wide / sector** factor for that day, not a company news item. Sector notes are included
  only where a source explicitly reported that sector's move that day (see §3).
- **Timing rule for "US close":** a US session closes ~01:30 IST the next calendar day, so the US close
  dated 26 Oct is a pre-market cue for India on 27 Oct, not an intraday driver on 26 Oct. The table in
  §2 lists the US close that was known **before** each Indian session, plus the same-day US close
  where it helps explain the next day. The 26 Oct Indian session's overnight cue was the US close of
  Fri 23 Oct, reported as lower (PTI via Rediff, 26 Oct) — no separate US 23 Oct index levels are
  claimed here because they were not re-verified in this search.

## 1. Tagging rule (applied uniformly, then sector overrides only where sourced)

- **risk-on:** Nifty up ≥ ~0.5% on the day AND the dominant reported driver is a supportive global
  factor (e.g. Fed hold, easing oil), even if one flow leg is negative.
- **risk-off:** Nifty down on the day AND the dominant reported driver is an adverse global factor
  (oil-supply shock, Fed-eve caution with a sharp intraday fall, or an overnight US tech sell-off
  for the 30 Oct pre-market tag).
- **neutral:** mixed signals — flat close, or opposing flows/sectors, or a positive close offset by
  still-elevated oil, FII selling and a rising VIX. Mixed is recorded as neutral, not forced into
  risk-on/risk-off.
- **Sector override:** only where a source explicitly reported that sector moving against the day
  (e.g. Bank Nifty +0.54% on a risk-off day, Nifty Auto the sole faller on a risk-on day). Overrides
  are flagged in the CSV `factor` field as "sector note / sector override". There are 4 override
  rows in total: HDFCBANK 27 Oct (risk-off), GLENMARK + HDFCBANK 28 Oct (neutral), TVSMOTOR 29 Oct
  (neutral). All other rows carry the day tag.

## 2. Day-by-day verified summary (source + date per item)

### Mon 26 Oct 2026 — tag: NEUTRAL (all 25 stocks)
- **India close:** Nifty 22,753.20, +153.20 (+0.68%); Sensex 73,606.75, +482.92 (+0.66%); Bank Nifty
  54,366.70, +0.15% — after opening weak (Nifty open 22,524.40, intraday low 22,387.35; Sensex
  intraday low 72,514.57), snapping a four-session losing streak. Source: Moneycontrol, 26 Oct 2026;
  DSIJ closing bell, 26 Oct 2026; Financial Express live, 26 Oct 2026.
- **Why neutral, not risk-on, despite the green close:** the rebound came off a weak, risk-off open.
  Reports cite elevated crude, Middle East geopolitical tensions and caution ahead of the US Fed
  27–28 Oct meeting as the opening drag; India VIX rose 1.78% to 17.16 even as Nifty rose.
  Sources: DSIJ, 26 Oct 2026; PTI via Rediff, 26 Oct 2026.
- **Oil:** Brent above $114 during the session, after approaching ~$117 before easing; HDFC Sky
  pre-market: Brent −1.9% to $114.50, WTI −2.13% to $101.10, on reported Qatar/Iran diplomatic
  efforts, after Brent surged 6.2% the prior week to its highest weekly close since mid-2022 on
  Houthi attacks in Saudi Arabia. Sources: DSIJ, 26 Oct 2026; HDFC Sky, 26 Oct 2026.
- **Geopolitics:** Houthi attacks involving Saudi targets renewing regional-stability / oil-supply
  concerns. Source: DSIJ, 26 Oct 2026. No Saudi confirmation of any specific 26 Oct strike is
  claimed here.
- **FII/DII (provisional exchange data):** FII net **−₹1,462.49 cr** (buy ₹9,324.90 cr / sell
  ₹10,787.39 cr); DII net **+₹2,609.57 cr** (buy ₹17,389.57 cr / sell ₹14,780.00 cr); combined
  +₹1,147.08 cr. Source: Moneycontrol, 26 Oct 2026 (19:21 IST). Note: Friday 23 Oct flows quoted
  in the same live blogs (FII +₹887.65 cr, DII +₹3,235.36 cr) are the prior session, not 26 Oct.
- **Overnight / Asia:** Asian markets largely lower on 26 Oct; GIFT Nifty muted (~22,583–22,608 vs
  prior Nifty close 22,600). Sources: HDFC Sky, 26 Oct 2026; DSIJ, 26 Oct 2026.
- **Sector note (sourced):** "Metals and Pharma Lead" is the Finbrooks 26 Oct wrap headline.
  No stock-level metal/pharma moves are claimed beyond that headline. This is why metals
  (NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL) and GLENMARK carry a sector
  note in the CSV but keep the neutral day tag.
- **Rupee:** no single verified 26 Oct close is stated here (see §6 for why the implied level
  from the 27 Oct report, ~95.15, is not presented as a verified close).

### Tue 27 Oct 2026 — tag: NEUTRAL (24 stocks); HDFCBANK: RISK-OFF (sector override)
- **India close:** Nifty 22,749.75, −3.45 (−0.02%); Sensex 73,598.67, −8.08 (−0.01%) — effectively
  flat, on monthly-expiry volatility. Bank Nifty fell >350 points to below 54,000.
  Sources: PTI via The Print, 27 Oct 2026; Business Standard live, 27 Oct 2026; ET Now, 27 Oct 2026.
- **Overnight US close (26 Oct, known before India 27 Oct):** S&P 500 7,676.77, +0.70%; Nasdaq
  26,169.38, +0.82%; Dow 52,361.58, +0.28% — led by tech after Anthropic's IPO filing revived AI
  shares; crude retreat also cited. Sources: HDFC Sky, 27 Oct 2026; ET US live blog, 27 Oct 2026.
  This supportive US cue did **not** produce a green Indian close — a reminder that the tag is
  about the Indian day, not the US cue alone.
- **Oil / Fed:** Brent ~$115.8 (−0.03% on the day, per PTI); HDFC Sky: Brent "near $116, close to a
  six-month high". Caution ahead of the Fed decision on Wed 28 Oct is cited in every close report.
  Sources: PTI via The Print, 27 Oct 2026; HDFC Sky, 27 Oct 2026.
- **FII/DII (provisional):** FII net **+₹4,240.39 cr** (buy ₹24,517.65 cr / sell ₹20,277.26 cr) —
  reported as the largest single-day FII buying in October to that point; DII net **−₹1,250.03 cr**
  (buy ₹15,702.74 cr / sell ₹16,952.77 cr), first DII net selling since 16 Oct; combined +₹2,990.36 cr.
  Sources: Moneycontrol, 27 Oct 2026 (21:35 IST); CNBC TV18, 27 Oct 2026 (20:38 IST).
- **Rupee:** closed 95.12 (provisional), +3 paise, range 95.09–95.24. Source: Hindu BusinessLine
  live, 27 Oct 2026.
- **Sector notes (sourced):** Nifty Media, Realty and Pharma gained 2–3%; Nifty Private Bank and
  Financial Services were top laggards; IT and oil & gas also weak; broader Midcap +1%, Smallcap
  +2.70%. Sources: Business Standard, 27 Oct 2026; HDFC Sky, 27 Oct 2026. Hence HDFCBANK =
  risk-off override (private-bank weakness), GLENMARK = neutral with pharma-strength note,
  WIPRO = neutral with IT-laggard note. No other stock gets a sector override this day.

### Wed 28 Oct 2026 — tag: RISK-OFF (23 stocks); GLENMARK + HDFCBANK: NEUTRAL (sector overrides)
- **India close:** Nifty 22,698.85, −50.90 (−0.22%); Sensex 73,246.03, −352.64 (−0.48%) — but
  intraday much worse: Sensex to 72,603 (−995, −1.35%), Nifty to 22,497 (−252, −1.11%) in the
  morning, then value buying pared losses (Sensex ~650 points off the low).
  Sources: Moneycontrol, 28 Oct 2026; Univest/Business Standard intraday, 28 Oct 2026.
- **Geopolitics / oil — the day's dominant factor:** Yemen's Iran-aligned Houthis said on Tue 27 Oct
  they had hit Saudi Arabia's biggest refinery (Ras Tanura, 550,000 bpd) with a missile; Saudi
  authorities had **not** immediately confirmed the strike. Brent rose to ~$115.36–$115.90
  (+1.3–1.8%); WTI above $101–$102. Sources: Reuters via Business Times, 28 Oct 2026;
  Moneycontrol, 28 Oct 2026 (07:31 and 09:38 IST); ET EnergyWorld, 28 Oct 2026.
  Also reported 28 Oct: Houthi attack on Aden airport, Yemen fighting escalation, and worries
  the US could strike Iran after the 3 Nov US midterms. Source: Khaleej Times, 28 Oct 2026.
- **Fed:** decision due this day (announced after Indian close — see 29 Oct). Caution ahead of it
  is cited alongside oil in every 28 Oct report. Source: PTI/Nation Press, 28 Oct 2026.
- **Overnight US close (27 Oct, known before India 28 Oct):** S&P 500 7,722.60, +0.60%; Nasdaq
  26,477.81, +1.18%; Dow 52,377.57, +0.03%; Brent settled $113.88 that US session — i.e. the US
  cue was positive, but the Saudi-refinery oil shock dominated the Indian morning.
  Source: HDFC Sky, 28 Oct 2026 (reporting 27 Oct US close).
- **FII/DII (provisional, for 28 Oct):** FII net **+₹871.83 cr**; DII net **+₹643.35 cr** — both
  buyers. Sources: CNBC TV18, 29 Oct 2026 (reporting 28 Oct flows); TradingView/Moneycontrol
  First Tick, 29 Oct 2026; MarketFreeze, 28 Oct 2026. **Caution:** the Moneycontrol 28 Oct
  article's "FII buying ₹4,240 cr" line refers to 27 Oct's flow, not 28 Oct — do not double-count it.
  FII index-futures posture remained heavily net short (reported ~2,80,183 contracts on 26 Oct;
  still "substantially net short" and rising on 28 Oct per the 28 Oct analysis) — a derivatives
  posture, not a cash-flow figure, and not conflated with it here.
- **Rupee:** see §6 — PTI/ET provisional close 95.28 (−21 paise) vs Reuters-based 95.22; both
  reported, neither treated as final.
- **Sector notes (sourced):** Nifty IT −3.5% intraday (Infosys −4.9%, TCS −3.35% by 11:26 in the
  Univest summary); only Nifty Auto and Nifty Pharma green intraday; at close BSE Healthcare
  +0.95% top gainer, Bank Nifty +0.54% to 54,267.00 bucking the Nifty fall.
  Sources: Univest, 28 Oct 2026; MarketsMojo, 28 Oct 2026; MarketFreeze, 28 Oct 2026.
  Hence GLENMARK = neutral (pharma/healthcare resilience) and HDFCBANK = neutral (Bank Nifty
  outperformance) — both still below risk-on, because the market-wide day was risk-off.
  OIL keeps the risk-off day tag with an explicit note: high Brent is a direct input for OIL,
  so the tag is market sentiment, not an OIL direction call.

### Thu 29 Oct 2026 — tag: RISK-ON (24 stocks); TVSMOTOR: NEUTRAL (sector override)
- **India close:** Nifty 22,936.75, +237.90 (+1.05%); Sensex 74,151.04, +905.01 (+1.24%) — the
  session's highs, snapping a two-day losing streak. Nifty Realty +2.7%, Nifty FMCG +2.3%,
  Midcap +0.98–0.99%, Smallcap +0.93–0.95%; all sectoral indices positive **except Nifty Auto**.
  Sources: The Hindu, 29 Oct 2026; Business Standard, 29 Oct 2026; ET Now, 29 Oct 2026.
- **Fed (announced 28 Oct US time, driving 29 Oct India):** FOMC voted **10–2 to hold** the
  federal funds target at **3.75–4.00%**; dissenters Lisa Cook and Beth Hammack preferred a
  +25 bp hike. September had seen the first hike in three years (+25 bp). Inflation still above
  the 2% target (CPI 3.7% y/y in September, up from 3.4% in August); next meeting 8–9 Dec, with
  markets pricing a high chance of a December hike. Sources: Al Jazeera, 28 Oct 2026;
  USA Today, 28 Oct 2026; Financial Express, 28 Oct 2026; Channel NewsAsia, 29 Oct 2026.
- **Overnight US close (28 Oct, known before India 29 Oct):** S&P 500 7,743.98, +0.28%; Nasdaq
  26,549.85, +0.27%; Dow 52,475.10, +0.19% (third straight gain). Sources: Zacks, 29 Oct 2026;
  Portfolio Terminal, 28 Oct 2026 close table. (ET's live blog gave marginally different
  levels — S&P 7,748.03 — see §6.)
- **Oil:** Brent eased to ~$113.96–$114.64 during 29 Oct (down ~1–1.18%), WTI ~$101–$102, on
  renewed US–Iran diplomatic engagement / Tehran signalling willingness to negotiate; still
  "elevated" and above $110. Sources: The Hindu, 29 Oct 2026; CNBC TV18, 29 Oct 2026;
  Hindu BusinessLine, 29 Oct 2026.
- **FII/DII (provisional, for 29 Oct):** FII net **−₹943.60 cr** (buy ₹13,400.29 cr / sell
  ₹14,343.89 cr); DII net **+₹1,924.41 cr** (buy ₹18,458.64 cr / sell ₹16,534.23 cr); combined
  +₹980.81 cr. Sources: CNBC TV18, 29 Oct 2026 (20:31 IST); EconoTimes, 30 Oct 2026.
  Risk-on here is **not** FII-led — it is Fed-hold + easing-oil + DII/earnings-led, and the CSV
  factor says so.
- **Rupee:** provisional close 95.25 (+3 paise) per PTI/ET, 29 Oct 2026; Reuters-based close
  95.26 — see §6. Intraday low 95.38 (fortnight low); RBI intervention reported as capping
  losses. Sources: ET, 29 Oct 2026; ET BFSI, 29 Oct 2026.
- **Sector notes (sourced):** banking + FMCG buying led the rally (The Hindu, 29 Oct);
  FMCG +2.3%, Realty +2.7% (Business Standard, 29 Oct); Adani Ports +6.17% on Q2 profit is a
  stock-specific earnings item, **not** one of the 25 stocks, and is not transferred to any of
  them. Hence TVSMOTOR = neutral override (Auto sole faller); GODREJCP/HINDUNILVR/ITC/UNITDSPR
  carry an FMCG note, OBEROIRLTY a Realty note, HDFCBANK a banking note — all keep risk-on.
- **Index-only note (per task):** the 29 Oct Bank/Nifty file
  (`v4_options_from_spot_signals_oct19_30_trades.csv`) shows both 29 Oct index rows as
  NOT_COMPUTED / UNDETERMINED (Bank option chain returned 0 rows; no Nifty 5-min data).
  Those are **index** rows, not stock trades, and are excluded from the stock test in §4.

### Fri 30 Oct 2026 — tag: RISK-OFF, PRE-MARKET ONLY (all 25 stocks; full-day tag NOT assigned)
- **Status at writing (~08:30 IST, before the 09:15 open):** no 30 Oct Indian close, no 30 Oct
  FII/DII (published after close), and no 30 Oct sector moves exist yet. The tag below is a
  **pre-market sentiment tag only** and must be replaced after the close; it must not be
  backfilled as if it were the day's outcome.
- **Overnight US close (29 Oct, known before India 30 Oct):** Nasdaq 26,184.72, **−1.38%**;
  S&P 500 7,720.39, **−0.30%**; Dow 52,342.56, **−0.25%** — ending a three-day winning streak.
  Driver: Alphabet −12.6–13% after missing Q3 EPS/revenue and reporting −$9.07 bn free cash
  flow while keeping $195–205 bn capex guidance, reviving AI-spend/return worries; Microsoft
  ~flat-to-down despite Azure +48%; Caterpillar −9%. Sources: Invezz, 29 Oct 2026;
  KuCoin/Yicai, 30 Oct 2026; MarketBriefer, 29 Oct 2026.
- **After-hours overhang for 30 Oct:** Amazon −7%+ and Intel −23% in extended trading after
  their 29 Oct US close (Amazon soft holiday outlook / surging AI capex; Intel weak forecast).
  Nasdaq-100 futures −1.5–1.6%, S&P futures −0.5–0.6% on 30 Oct morning reports.
  Sources: Trading Economics, 29 Oct 2026; CNBC TV18, 30 Oct 2026 (07:03 IST).
- **Asia / GIFT Nifty (30 Oct morning):** Kospi −3.96% (closed, per CNBC TV18 30 Oct),
  Nikkei down ~1.88–3% intraday, Taiwan TAIEX −3.19%; GIFT Nifty flat-to-muted: 23,027.50
  (−15, −0.07%) per Financial Express live 07:17 IST, 23,028 (−14.5) per ET pre-market,
  22,981 at 07:42 IST per Reuters — i.e. a muted/red open signal, not a firm direction.
  Sources: CNBC TV18, 30 Oct 2026; Financial Express live, 30 Oct 2026; Reuters, 30 Oct 2026;
  ET pre-market, 30 Oct 2026.
- **Oil (30 Oct morning, snapshots differ by time):** Brent $111.29–$111.47 (Financial Express
  live, 07:17 IST) vs $115.50 (+0.54%) in the NDTV Profit 30 Oct pre-market piece and $117.40
  (+2.2%) in the Reuters 30 Oct pre-market piece citing a further Houthi claim on Ras Tanura
  and Saudi airports. **Do not quote a single 30 Oct Brent level from this report** — the
  snapshots are time-stamped differently and conflict; what is consistent is "still elevated,
  above $110". Sources as cited.
- **Central banks / earnings due later 30 Oct (not outcomes):** Bank of Japan decision due
  30 Oct (widely expected hold at 1.25%, per Reuters 30 Oct); Reliance, Sun Pharma and Bharat
  Electronics earnings due later 30 Oct (Reuters 30 Oct) — none is a 25-stock item except
  via index sentiment, and none is counted as a 30 Oct result.
- **Dollar/rupee:** Reuters 30 Oct pre-market: $1 = ₹95.19. US 10-year yield ~4.90% on 30 Oct
  morning (Reuters), down from ~5.02–5.05% after the Fed — a Treasury rally on AI jitters.
  Source: Reuters, 30 Oct 2026.
- **Sector note:** WIPRO carries the US-tech-sell-off factor explicitly (IT/tech most directly
  exposed). No other 30 Oct sector override is made pre-market.

## 3. Stock-day tag summary (from the CSV)

| Date | Day tag | Overrides | Count in CSV |
|---|---|---|---|
| 2026-10-26 | neutral | none (sector notes only: metals, pharma, OIL input note) | 25 neutral |
| 2026-10-27 | neutral | HDFCBANK risk-off | 24 neutral, 1 risk-off |
| 2026-10-28 | risk-off | GLENMARK neutral, HDFCBANK neutral | 23 risk-off, 2 neutral |
| 2026-10-29 | risk-on | TVSMOTOR neutral | 24 risk-on, 1 neutral |
| 2026-10-30 | risk-off (pre-market only) | none (WIPRO factor note only) | 25 risk-off |
| **Total** | | | **125 rows: 24 risk-on, 49 risk-off, 52 neutral** |

Note the 30 Oct count: 25 "risk-off" rows are pre-market tags, not closed-day outcomes.
Excluding 30 Oct, the closed-day split is 24 risk-on, 24 risk-off, 52 neutral (100 rows).

## 4. Test: do S8 trades differ by sentiment? — ANSWER: NO TEST IS POSSIBLE IN THIS WINDOW

**Source file checked:** `~/workspace/trading/s8_trades_jan_oct_2026.csv` (54 trades total,
latest date 2026-10-12) and, as a cross-check, `s8_uncapped_jan_oct_2026.csv` (81 trades total).
Both were filtered for 2026-10-26, 2026-10-27 and 2026-10-28.

| Sentiment (S8 trade day) | S8 trades (n) | Wins (net > 0) | Full-target (full_target = True) | Net (₹) |
|---|---|---|---|---|
| risk-on | 0 | — | — | — |
| risk-off | 0 | — | — | — |
| neutral | 0 | — | — | — |
| **Total, 26–28 Oct** | **0** | **—** | **—** | **—** |

- **Win rate, full-target rate and net by sentiment are undefined (0/0), not 0%.** Reporting
  0% would falsely imply trades lost; the correct statement is: **no S8 trades exist in the
  window to test, so no sentiment edge — or lack of one — can be claimed from S8 for 26–28 Oct.**
- 30 Oct is excluded from the trade test for two independent reasons: (a) the session had not
  closed at writing, and (b) the task specifies the S8 list for 26–28 Oct and 29 Oct Bank/Nifty
  context for index only, not stocks. 29 Oct has no S8 stock trades in the file either, and
  its index rows are NOT_COMPUTED (see §2, 29 Oct).
- **Cross-check only (NOT S8, NOT counted above):** the only capped-set trade in the window
  found across s1–s8 files is S6 KALYANKJIL on 2026-10-26 (neutral day): setup4_reclaim CE,
  09:55 signal, entry 515.65, stop 508.65, exit stop 11:10, net −₹740, full_target False
  (`s6_trades_jan_oct_2026.csv`, same row in the uncapped file). n = 1, on a neutral day, in a
  different system version — it proves nothing about sentiment and is recorded here only so
  the parent does not mistake "no S8 trades" for "no trades at all that week".
- **What the parent needs to decide (not decided here):** either (i) extend the S8 sentiment
  test to a window where S8 actually traded, or (ii) supply the missing 26–28 Oct S8 trade
  list if one exists under a different filename. Until then, any claim of the form "S8 works
  better on risk-on days" would be invented.

## 5. How to use this layer (and how not to)

- Use it as a **day filter / context flag** for November paper logging: log the day tag alongside
  the trade, do not filter trades by it until a window with actual trades exists.
- Do not use the 30 Oct pre-market risk-off tag as a closed-day result, and do not carry any
  26–29 Oct tag forward as a prediction for November.
- OIL is the exception to "tag = direction": on oil-spike days the market tag is risk-off while
  the oil-price driver itself is directionally different for an oil producer vs an oil consumer.
  The CSV flags this on OIL rows.
- Index options are separate: 26 Oct Nifty/Bank V4 rows in the index file (Nifty setup4 CE stop
  −₹3,470/lot; Bank setup3 PE target +₹2,480/lot) and the 28 Oct Nifty setup2 PE stop are
  **index options, per 1 lot, not stock trades**, and are not mixed into §4.

## 6. Discrepancies and limits (explicit)

1. **28 Oct Sensex close:** 73,246.03 (−352.64) per Moneycontrol/TradingView — arithmetically
   consistent with the 27 Oct close 73,598.67. MarketsMojo's 73,108.25 (−490.42) for the same
   close is inconsistent with that arithmetic and with the Nifty close both sources agree on
   (22,698.85); it was **not** used. Nifty levels are consistent across sources.
2. **Rupee closes:** 28 Oct: PTI/ET provisional 95.28 vs Reuters-based 95.22; 29 Oct: PTI/ET
   provisional 95.25 vs Reuters-based 95.26. Both are reported above; the difference is
   provisional vs final interbank reporting, and no single figure is asserted as final.
3. **28 Oct US close levels:** S&P 7,743.98 / Nasdaq 26,549.85 / Dow 52,475.10 (Zacks,
   Portfolio Terminal, NordFX, IC — mutually consistent) vs ET live blog 7,748.03 / 26,561.24 /
   52,503.78. The consistent set is used; the ET variant is noted, not hidden.
4. **30 Oct Brent:** $111.29–$111.47 (FE live, ~07:17 IST) vs $115.50 (NDTV Profit pre-market)
   vs $117.40 (Reuters pre-market, citing a further Houthi claim). Time-stamped snapshots
   differ; only "still elevated, above $110" is asserted for 30 Oct morning.
5. **28 Oct FII/DII:** one low-authority summary claimed ~₹6,000 cr FII selling on 28 Oct;
   it contradicts the provisional exchange figures (+₹871.83 cr FII, +₹643.35 cr DII) reported
   by CNBC TV18, TradingView/Moneycontrol and MarketFreeze, and was **not** used.
6. **Sources are secondary market reporting** (PTI/Reuters via Indian outlets, exchange
   provisional data as reported), not NSE/BSE primary files. FII/DII figures should be
   re-checked against NSE/BSE provisional data before any publication use.
7. **Coverage limit:** this is a web-search layer, not a live-browser or exchange-data pull.
   Intraday timing (e.g. whether a 26 Oct stock signal came before or after the oil easing)
   cannot be established from close reports alone.

## 7. Key sources (verbatim URLs from search results)

- Moneycontrol 26 Oct FII/DII: https://www.moneycontrol.com/news/business/markets/fiis-net-sell-rs-1462-crore-of-indian-equities-while-diis-net-buy-rs-2610-crore-on-oct-26-14060450.html
- DSIJ 26 Oct closing bell: https://insights.dsij.in/dsijarticledetail/closing-bell-sensex-rebounds-over-1000-points-from-day%E2%80%99s-low-nifty-50-rises-068-above-22750-mark-60164
- HDFC Sky 26 Oct global cues: https://hdfcsky.com/news/global-markets-today-october-26-2026-asian-shares-decline-oil-eases-from-six-month-high-indian-markets-seen-opening-cautiously
- PTI via The Print 27 Oct: https://theprint.in/economy/sensex-nifty-close-largely-unchanged-amid-selling-in-bank-it-stocks-elevated-crude-oil-prices/3083060/
- Moneycontrol 27 Oct FII/DII: https://www.moneycontrol.com/news/business/markets/fiis-net-buy-rs-4-240-crore-as-their-biggest-net-purchase-in-october-14061576.html
- Reuters via Business Times 28 Oct oil: https://www.businesstimes.com.sg/companies-markets/energy-commodities/oil-rises-over-1-after-saudi-arabian-refinery-attack-reignites-supply-risk
- Moneycontrol 28 Oct close: https://www.moneycontrol.com/news/business/markets/sensex-rises-400-pts-from-day-s-low-nifty-reclaims-22-600-key-reasons-behind-markets-paring-losses-14062174.html/amp
- Al Jazeera Fed 28 Oct: https://www.aljazeera.com/amp/economy/2026/10/28/fed-leaves-interest-rates-unchanged-despite-inflation-in-the-us
- The Hindu 29 Oct rally: https://www.thehindu.com/business/markets/sensex-surges-905-pts-nifty-tops-22900-on-heavy-buying-in-banking-fmcg-stocks/article71640234.ece
- CNBC TV18 29 Oct FII/DII: https://www.cnbctv18.com/market/fiis-turn-net-sellers-at-rs944-crore-as-sensex-jumps-905-points-20022757.htm
- Invezz 29 Oct US close: https://invezz.com/news/2026/10/29/nasdaq-closes-1-38-lower-on-ai-spending-and-inflation-concerns/
- Reuters 30 Oct pre-market: https://www.reuters.com/world/india/indian-shares-seen-opening-higher-after-earnings-led-rebound-higher-oil-cap-2026-10-30/
- CNBC TV18 30 Oct Asia: https://www.cnbctv18.com/market/asia-market-stocks-share-price-kospi-nikkei-taiex-ai-stocks-amazon-intel-earnings-wall-street-selloff-20022913.htm
- Financial Express live 30 Oct: https://www.financialexpress.com/market/share-market-today-live-stock-market-sensex-nifty-gold-silver-rate-30th-october-2026-4372711/
