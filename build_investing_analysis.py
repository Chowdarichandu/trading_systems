#!/usr/bin/env python3
"""Investing value analysis 2026-11-14: tiers the locked v2 screener PASS list (99 names),
adds daily technical state for the top 25 by market cap (+ South Indian Bank) from local
daily stores. Research only. All fundamental figures are the 11 Nov 2026 screener snapshot."""
import csv, json, os, statistics

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'value_screener_v2_2026-11-11.csv')

def f(x):
    try:
        return float(str(x).replace(',', ''))
    except (TypeError, ValueError):
        return None

rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
passrows = [r for r in rows if 'PASS' in r['Verdict_flags'] or 'REFERENCE' in r['Verdict_flags']]
assert len(passrows) == 99, len(passrows)

CYCLICAL = {'ONGC', 'IOC', 'BPCL', 'SAIL', 'HINDALCO', 'NATIONALUM', 'OIL', 'GESHIP', 'SCI', 'SANDUMA'}
# C tier: a specific flag the owner must clear first (decided from the screener's own flags/notes)
C_REASONS = {
    'GSPL': 'PROVISIONAL — screener page stale (May-2026 snapshot), FY26 unverifiable; re-verify before anything',
    'KISSHT': 'PARTIALLY VERIFIED — FY24 PAT and annual EPS row not extractable in the v2 run',
    'INTELLECT': 'P/E conflict — screener consolidated 19.4 vs filing mirrors 20.2-20.4 (above the <20 gate); resolve first',
    'JKIL': 'Contingent liabilities Rs 4,383 cr EXCEED net worth Rs 3,369 cr (only main-list name with this flag)',
    'MAITHANALL': 'Profits dominated by investment fair-value income — earnings quality must be cleared first',
    'GUJENERGY': 'FY25 PAT/EPS spike was an exceptional (negative-tax) year — earnings base must be cleared first',
    'HOMEFIRST': 'NNPA 1.40% is near the 1.5% limit AND promoter down 16.6 pp — both to clear first',
    'IIFL': 'Regulatory-collapse recovery (FY25 PAT Rs 578 cr in the gold-loan ban year; EPS still below FY24) + EVENT 10 Nov 2026: board approved Rs 6,414 cr preferential raise, Blackstone Rs 5,000 cr at Rs 602/share (~16% post-conversion), capital adequacy 17% -> ~30% pro forma, approvals pending — not in the 11 Nov screener figures',
    'KEC': 'D/E borderline — ~1.04 if acceptances are counted (gate is <1)',
    'PGINVIT': 'InvIT structure — equity declines by design (distributions); not comparable to an operating equity',
    'WELENT': 'Earnings lumpy — EPC plus exceptional items; quality of the profit line to clear first',
    'EDELWEISS': 'P/E 19.8 just inside the gate AND wholesale-book credit costs volatile (screener note)',
    'SATIN': 'Microfinance (MFI) book + EPS dip — the sector that failed peers (Equitas/Jana) on stress',
}

def pos52(r):
    cmp_, h, l = f(r['CMP_INR']), f(r['W52H']), f(r['W52L'])
    if None in (cmp_, h, l) or h == l:
        return None
    return (cmp_ - l) / (h - l)

def tier_and_reason(r):
    t = r['Ticker']
    pe, pb, roe = f(r['PE']), f(r['PB']), f(r['ROE_pct'])
    pg, sg = f(r['ProfitG3Y_pct']), f(r['SalesG3Y_pct'])
    pat24, pat25, pat26 = f(r['PAT_FY24_Cr']), f(r['PAT_FY25_Cr']), f(r['PAT_FY26_Cr'])
    mcap = f(r['MarketCap_Cr'])
    p = pos52(r)
    flags = r['Verdict_flags']
    fig = (f"P/E {r['PE']} · P/B {r['PB']} · EPS {r['EPS_FY24']}->{r['EPS_FY25']}->{r['EPS_FY26']} ({r['EPS_3yr_direction']}) · "
           f"PAT FY26 Rs {r['PAT_FY26_Cr']} cr · ROE {r['ROE_pct']}% · profit G {r['ProfitG3Y_pct']}% · "
           f"BS: {r['DE_or_GNPA_NNPA']} · "
           f"price {p*100:.0f}% of 52w range · mcap Rs {r['MarketCap_Cr']} cr" if p is not None else
           f"P/E {r['PE']} · P/B {r['PB']} · EPS {r['EPS_FY24']}->{r['EPS_FY25']}->{r['EPS_FY26']} ({r['EPS_3yr_direction']}) · "
           f"PAT FY26 Rs {r['PAT_FY26_Cr']} cr · ROE {r['ROE_pct']}% · profit G {r['ProfitG3Y_pct']}% · "
           f"BS: {r['DE_or_GNPA_NNPA']} · mcap Rs {r['MarketCap_Cr']} cr")
    if t in C_REASONS:
        return 'C', f"Clear first: {C_REASONS[t]}. Figures: {fig}."
    watch = []
    if r['Section'] == 'No-growth':
        watch.append(f"no 3Y profit growth (printed {r['ProfitG3Y_pct']}%)")
    if 'FLAG EPS-dip' in flags or 'FLAG EPS-dip FY25' in flags:
        watch.append('EPS dipped mid-window')
    if pat26 is not None and pat25 is not None and pat26 < pat25:
        watch.append('PAT fell in FY26')
    if r['EPS_3yr_direction'] == 'Stable':
        watch.append('EPS flat over the window')
    if roe is not None and roe < 12:
        watch.append(f"ROE thin at {r['ROE_pct']}%")
    if pb is not None and pb > 2.5:
        watch.append(f"P/B high inside the gate at {r['PB']}")
    if pe is not None and pe > 18:
        watch.append(f"P/E near the gate at {r['PE']}")
    if pg is not None and 0 < pg < 10 and r['Section'] != 'No-growth':
        watch.append(f"profit growth thin at {r['ProfitG3Y_pct']}%")
    if p is not None and p > 0.90:
        watch.append('price at/near the 52w high')
    if 'promoter decline' in flags:
        watch.append('promoter/sponsor holding declining (see screener note)')
    if 'holdco' in flags:
        watch.append('holding-company structure (discount/opacity)')
    if t in CYCLICAL:
        watch.append('cyclical earnings')
    if t in ('UCOBANK', 'IDBI'):
        watch.append('thin free float (govt holding ~91-95%)')
    if t in ('LICI', 'GICRE'):
        watch.append('insurer — earnings not comparable line-by-line; LIC ROE is a small-equity-base print')
    if t == 'MUTHOOTFIN':
        watch.append('FY26 PAT +98% in the gold rally — a spike year inside the trend')
    if 'data from screener cache' in flags:
        watch.append('verified from 9 Nov cache excerpts')
    if mcap is not None and mcap < 9000:
        watch.append(f"small cap (Rs {r['MarketCap_Cr']} cr) — liquidity to check")
    de = r['DE_or_GNPA_NNPA']
    if 'NNPA 1.' in de or 'NNPA 1,' in de:
        watch.append(f"asset quality shown: {de}")
    is_a = (r['Section'] != 'No-growth' and r['EPS_3yr_direction'] == 'Rising'
            and pat26 is not None and pat25 is not None and pat26 > pat25
            and roe is not None and roe >= 12 and pe is not None and pe <= 19
            and pb is not None and pb <= 2.7 and pg is not None and pg >= 10
            and p is not None and p <= 0.90 and mcap is not None and mcap >= 9000
            and not watch)
    if is_a:
        return 'A', f"Clean on every v2 field: {fig}."
    return 'B', f"Watch: {'; '.join(watch) if watch else 'no single hard flag — ranked below Tier A on the combined figures'}. Figures: {fig}."

for r in passrows:
    r['_tier'], r['_reason'] = tier_and_reason(r)
    r['_pos52'] = pos52(r)

# ---------------- technicals ----------------
def load_series(ticker):
    """Longest local daily series; merge stores verified identical on overlap."""
    cands = []
    for store in ('data/sarvaritu_fwd', 'data/full_hist', 'data/progressive_ext', 'data/progressive', 'data/wide_nse_fwd'):
        p = os.path.join(BASE, store, ticker, 'spot_daily.csv')
        if os.path.exists(p):
            d = {}
            for row in csv.DictReader(open(p)):
                d[row['date']] = (float(row['open']), float(row['high']), float(row['low']), float(row['close']))
            cands.append((store, d))
    if not cands:
        return None, None
    # start from the longest-history store, append later dates from any other store
    cands.sort(key=lambda sd: (min(sd[1]), -len(sd[1])))
    merged = dict(cands[0][1])
    src = cands[0][0]
    for store, d in cands[1:]:
        for dt, v in d.items():
            if dt not in merged:
                merged[dt] = v
    dates = sorted(merged)
    return [merged[d] for d in dates], (dates, src)

def rsi_wilder(closes, period=14):
    if len(closes) <= period:
        return [None] * len(closes)
    out = [None] * len(closes)
    gains = [max(closes[i] - closes[i - 1], 0.0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0.0) for i in range(1, len(closes))]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    out[period] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(period, len(gains)):
        ag = (ag * (period - 1) + gains[i]) / period
        al = (al * (period - 1) + losses[i]) / period
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out

def tech_state(ticker):
    series, meta = load_series(ticker)
    if not series or len(series) < 21:
        return 'TECH: n/a'
    dates, src = meta
    closes = [s[3] for s in series]
    last = closes[-1]
    n = len(closes)
    parts = [f"last close Rs {last:.2f} ({dates[-1]}, local daily store)"]
    if n >= 50:
        sma50 = statistics.mean(closes[-50:])
        parts.append(f"{'above' if last >= sma50 else 'below'} 50-DMA Rs {sma50:.2f} ({(last/sma50-1)*100:+.1f}%)")
    if n >= 200:
        sma200 = statistics.mean(closes[-200:])
        parts.append(f"{'above' if last >= sma200 else 'below'} 200-DMA Rs {sma200:.2f} ({(last/sma200-1)*100:+.1f}%)")
    else:
        parts.append(f"200-DMA n/a (only {n} daily bars)")
    rs = rsi_wilder(closes)
    r_last = rs[-1]
    zone = ('oversold' if r_last <= 30 else 'low' if r_last <= 45 else 'neutral' if r_last <= 55
            else 'firm' if r_last <= 70 else 'overbought')
    parts.append(f"RSI(14) {r_last:.0f} ({zone})")
    # Bollinger(20,2) on closes
    ma = [statistics.mean(closes[i - 19:i + 1]) for i in range(19, n)]
    sd = [statistics.pstdev(closes[i - 19:i + 1]) for i in range(19, n)]
    lower = [ma[k] - 2 * sd[k] for k in range(len(ma))]
    upper = [ma[k] + 2 * sd[k] for k in range(len(ma))]
    pctb = (last - lower[-1]) / (upper[-1] - lower[-1]) if upper[-1] != lower[-1] else None
    bb = 'no signal'
    for k in range(max(1, len(ma) - 5), len(ma)):
        gi = k + 19
        if closes[gi - 1] < lower[k - 1] and closes[gi] >= lower[k]:
            bb = f"BB band-return FIRED {dates[gi]}"
    if bb == 'no signal':
        if pctb is not None and pctb <= 0.10:
            bb = f"BB NEAR ( %B {pctb:.2f})"
        else:
            bb = f"BB no signal (%B {pctb:.2f})" if pctb is not None else 'BB no signal'
    rt = 'RSI-turn no signal'
    for i in range(max(15, n - 5), n):
        if rs[i - 1] is not None and rs[i] is not None and rs[i - 1] <= 30 < rs[i]:
            rt = f"RSI oversold-turn FIRED {dates[i]}"
    if rt == 'RSI-turn no signal' and r_last <= 35:
        rt = f"RSI-turn NEAR (RSI {r_last:.0f} <= 35)"
    parts.append(bb)
    parts.append(rt)
    return ' · '.join(parts)

top25 = sorted(passrows, key=lambda r: f(r['MarketCap_Cr']) or 0, reverse=True)[:25]
tech = {}
for r in top25:
    tech[r['Ticker']] = tech_state(r['Ticker'])
tech['SOUTHBANK'] = tech_state('SOUTHBANK')

# ---------------- outputs ----------------
out_csv = os.path.join(BASE, 'investing_value_analysis_2026-11-14.csv')
with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['Company', 'Ticker', 'Screener_Section', 'Tier', 'Reason', 'CMP_INR_11Nov', 'PE', 'PB',
                'EPS_FY24', 'EPS_FY25', 'EPS_FY26', 'PAT_FY26_Cr', 'ROE_pct', 'ProfitG3Y_pct', 'MarketCap_Cr',
                'Pos_in_52w_range_pct', 'Tech_State_Top25_and_SIB_only'])
    for r in sorted(passrows, key=lambda r: f(r['MarketCap_Cr']) or 0, reverse=True):
        w.writerow([r['Company'], r['Ticker'], r['Section'], r['_tier'], r['_reason'], r['CMP_INR'], r['PE'], r['PB'],
                    r['EPS_FY24'], r['EPS_FY25'], r['EPS_FY26'], r['PAT_FY26_Cr'], r['ROE_pct'], r['ProfitG3Y_pct'],
                    r['MarketCap_Cr'], f"{r['_pos52']*100:.0f}" if r['_pos52'] is not None else '',
                    tech.get(r['Ticker'], '')])

json.dump({'tiers': {r['Ticker']: r['_tier'] for r in passrows}, 'tech': tech},
          open('/tmp/investing_analysis_meta.json', 'w'), indent=1)

from collections import Counter
counts = Counter(r['_tier'] for r in passrows)

# ---------------- markdown report ----------------
bymcap = sorted(passrows, key=lambda r: f(r['MarketCap_Cr']) or 0, reverse=True)
sib = next(r for r in passrows if r['Ticker'] == 'SOUTHBANK')
L = []
L.append('# Investing — Value List Analysis (from the locked v2 screener)')
L.append('')
L.append('**Date:** 2026-11-14 · **Fundamental figures:** the locked v2 screener snapshot of **11 Nov 2026** '
         '(value_screener_v2_2026-11-11.csv — 99 PASS names: 86 with growth + 13 value-without-growth), unless a refresh flag says otherwise. '
         '**Technicals:** computed from local daily price stores (last bars 12–13 Nov 2026). **Research only — no recommendation; the owner does his own confirmation before investing.**')
L.append('')
L.append('## Tier counts')
L.append('')
L.append(f"- **Tier A — {counts['A']} names:** clean on every v2 field under the rules below (rising EPS and FY26 PAT, ROE ≥ 12%, P/E ≤ 19, P/B ≤ 2.7, 3Y profit growth ≥ 10%, price ≤ 90% of its 52w range, market cap ≥ ₹9,000 cr, no screener flag).")
L.append(f"- **Tier B — {counts['B']} names:** value holds, one or more watch items (named in each line).")
L.append(f"- **Tier C — {counts['C']} names:** passes the numbers but carries a specific flag the owner must clear first (named in each line).")
L.append('')
L.append('## Caveats (apply to every tier)')
L.append('')
L.append('1. **Promoter pledge is "n/s" (not shown) for most names** — the screener page exposed a pledge figure for only a minority. Every name needs a **pledge check on the exchange shareholding filing before investing**; the v2 governance pass rests on promoter-trend and page-visible proxies only.')
L.append('2. **GNPA/NNPA is n/s on many bank/NBFC pages** (premium-gated on screener) — where a line says "n/s", asset quality was not verified in v2 and needs the results/filing check.')
L.append('3. ASM/GSM surveillance status was not checked for any name. Ratios are point-in-time (11 Nov); cyclical P/Es can swing on one quarter.')
L.append('4. Technical state uses standard indicators only (50/200-DMA, RSI(14), Bollinger(20,2)) on local daily stores; names with only the Sep–Nov 2026 store (50 bars) have no 200-DMA — marked n/a in their line, never estimated. EKAM pattern labels: "FIRED" = the pattern completed within the last 5 sessions; "NEAR" = %B ≤ 0.10 (Bollinger) or RSI ≤ 35 (RSI-turn).')
L.append('')
for tier, head in (('A', '## Tier A — strongest all-round'), ('B', '## Tier B — value holds, watch items named'), ('C', '## Tier C — clear the named flag first')):
    L.append(head)
    L.append('')
    L.append('| Company | One-line basis |')
    L.append('|---|---|')
    for r in bymcap:
        if r['_tier'] == tier:
            L.append(f"| {r['Company']} ({r['Ticker']}) | {r['_reason']} |")
    L.append('')
L.append('## Technical state — top 25 PASS names by market cap')
L.append('')
L.append('| Company | Technical state (local daily store) |')
L.append('|---|---|')
for r in top25:
    L.append(f"| {r['Company']} ({r['Ticker']}) | {tech[r['Ticker']]} |")
L.append('')
L.append('**Read of the table (facts only):** most of the top 25 sit above their 50-DMA after the recent run, several with RSI in the 70s (PNB 80, Bank of Baroda 79, ICICI 77, Union Bank 76, SBI 75, Indian Bank 73, HDFC Bank 72). **No EKAM entry pattern (Bollinger band-return / RSI oversold-turn) has fired or is near in any of the top 25** — both patterns enter on washouts, and there has been no washout in these names. ONGC is the only top-25 name below both its 50- and 200-DMA; PFC and REC are below their 200-DMAs (−15.5% / −10.8%) with neutral RSI — the closest to a cooling zone, still not at either pattern.')
L.append('')
L.append('## South Indian Bank (SOUTHBANK) — the owner\'s holding')
L.append('')
L.append(f"**Tier in this analysis: {sib['_tier']}** — {sib['_reason']}")
L.append('')
L.append('| CMP (11 Nov) | P/E | Book value | P/B | ROE | PAT FY24/25/26 (₹ cr) | EPS FY24/25/26 (₹) | Latest qtr PAT | 3Y sales/profit growth | Market cap | 52w H/L | GNPA/NNPA |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
L.append(f"| ₹{sib['CMP_INR']} | {sib['PE']} | ₹{sib['BV_INR']} | {sib['PB']} | {sib['ROE_pct']}% | {sib['PAT_FY24_Cr']} / {sib['PAT_FY25_Cr']} / {sib['PAT_FY26_Cr']} | {sib['EPS_FY24']} / {sib['EPS_FY25']} / {sib['EPS_FY26']} (rising) | ₹{sib['LatestQtrPAT_Cr']} cr (Sep-2026) | {sib['SalesG3Y_pct']}% / {sib['ProfitG3Y_pct']}% | ₹{sib['MarketCap_Cr']} cr | {sib['W52H']} / {sib['W52L']} | n/s on the v2 fetch (v1 fetch: 1.24% / 0.09%) |")
L.append('')
L.append(f"**Technical state:** {tech['SOUTHBANK']}")
L.append('')
L.append('**Position:** bought at ~₹41; ₹61.3 at the 11 Nov snapshot (~+50%); the stock printed fresh all-time highs after the snapshot (₹62.2–62.57 intraday on 13 Nov in the refresh check) and closed ₹61.32 on 12 Nov in the local store — RSI 76, +21.3% above its 50-DMA. Extended, not washed out: neither EKAM pattern is near.')
L.append('')
L.append('**What has to stay true for the thesis:** (1) EPS keeps rising — 4.09 → 4.98 → 5.56, TTM ~₹6.1 in a 12 Nov published analysis, P/E ~10; (2) PAT keeps compounding — ₹1,070 → 1,303 → 1,456 cr, latest quarter ₹426 cr is the bank\'s best; (3) asset quality stays in the reported zone — GNPA 1.24% / NNPA 0.09% (v1 fetch and Q2 FY27 reports; it was n/s on the v2 screener page, so the filing check still applies); (4) book value keeps building — ₹46.1/share with reserves up ₹8,565 cr → ₹11,815 cr, so the P/B (1.33 at ₹61.3) does not stretch on a static book; (5) ROE holds near 13.5% and capital adequacy near the reported 15.95%.')
L.append('')
L.append('**Watch items:** price at an all-time high after a ~61% one-year run (valuation now carries the momentum, not a margin of safety); one published analysis of the latest quarter flags **non-operating income at 81.65% of PBT** and a **credit-deposit ratio down to 78.95%** (loan growth lagging deposits) — earnings-mix and growth items to verify in the results, not in the screener data; pledge is n/s (widely held, no promoter — the exchange-filing check is a formality here, but it is still outstanding like every other name).')
L.append('')
L.append('## Refresh check (events since the 11 Nov snapshot)')
L.append('')
L.append('- **IIFL Finance — material, flagged in its Tier C line:** board approved a ₹6,414 cr preferential capital raise on 10 Nov 2026 (Blackstone funds ₹5,000 cr via CCPS at ₹602/share, ~16% on conversion; promoters ₹1,264 cr; Anchorage ₹150 cr), lifting capital adequacy from ~17% to ~30% pro forma; subject to shareholder/regulatory approvals. The screener figures (CMP ₹678, P/E 11.6) predate any market reaction to it.')
L.append('- **South Indian Bank — price event only:** fresh all-time highs on 13 Nov (see its section). No results/pledge/regulatory item surfaced.')
L.append('- The quick public search covered South Indian Bank and the flagged financial names (IIFL, Indus Towers, GSPL). **No other material post-snapshot event surfaced; for all other names the list stands as of the 11 Nov data.** This was a quick check, not a filing-by-filing review.')
L.append('')
L.append('## How the tiers were set (frozen rules, applied mechanically)')
L.append('')
L.append('Tier C = a named clear-first flag (provisional/stale data, partial verification, P/E source conflict, contingent liabilities > net worth, one-off/fair-value-driven profits, NNPA near limit + promoter fall, regulatory-collapse recovery + dilutive raise, D/E borderline, InvIT structure, lumpy EPC earnings, P/E at the gate + volatile wholesale book, MFI stress sector). Tier A = passes ALL of: growth section, EPS rising, FY26 PAT > FY25, ROE ≥ 12%, P/E ≤ 19, P/B ≤ 2.7, 3Y profit growth ≥ 10%, price ≤ 90% of 52w range, market cap ≥ ₹9,000 cr, and zero watch items. Everything else = Tier B, with its watch items named. Watch items: no-growth section, EPS dip, FY26 PAT fall, flat EPS, ROE < 12%, P/B > 2.5, P/E > 18, profit growth < 10%, price > 90% of 52w range, promoter/sponsor decline, holdco, cyclical sector, thin float, insurer, cache-verified data, market cap < ₹9,000 cr.')
L.append('')
L.append('Files: `investing_value_analysis_2026-11-14.csv` (all 99 PASS names with tier + reason + technical state for the top 25 and SIB) · source `value_screener_v2_2026-11-11.csv` (locked) · builder `build_investing_analysis.py`.')
open(os.path.join(BASE, 'investing_value_analysis_2026-11-14.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

print('tier counts:', Counter(r['_tier'] for r in passrows))
print('TIER A:', [(r['Company'], r['Ticker']) for r in passrows if r['_tier'] == 'A'])
print('TIER C:', [(r['Company'], r['Ticker']) for r in passrows if r['_tier'] == 'C'])
for t, s in tech.items():
    print(t, '|', s)
