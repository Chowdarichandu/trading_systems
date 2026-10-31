#!/usr/bin/env python3
"""Line 6: Morning-Mover flagship risk card + regime diagnostic.
Analysis only on existing trade dumps. No new rules, no pass claims.
Figures provisional per 100 shares, Rs 40/trade, paper only.
"""
import csv, json
from collections import defaultdict, Counter
from datetime import date

BASE = '/home/hatch/workspace/trading/'

def load(fn):
    rows = list(csv.DictReader(open(BASE + fn)))
    for r in rows:
        r['net'] = float(r['net']); r['gross'] = float(r['gross'])
    return rows

old = load('mover_A_old_trades.csv')
ext = load('mover_A_ext_trades.csv')
poolb = load('mover_M1_poolB_trades.csv')
poola = old + ext

# ---- Nifty daily series + 50DMA (INV definition: prev close <= 50DMA) ----
nifty = []
for r in csv.DictReader(open(BASE + 'volrix/nifty_daily_2019_2026.csv')):
    nifty.append((r['date'][:10], float(r['close'])))
nifty.sort()
closes = [c for _, c in nifty]
dates = [d for d, _ in nifty]
sma50 = {}
for i in range(len(nifty)):
    if i >= 49:
        sma50[dates[i]] = sum(closes[i - 49:i + 1]) / 50.0

def regime(chain_date):
    """MET if Nifty close on the trading day before chain_date <= its 50DMA."""
    prev = None
    for i, d in enumerate(dates):
        if d < chain_date:
            prev = i
        else:
            break
    if prev is None or dates[prev] not in sma50:
        return None
    return 'MET' if closes[prev] <= sma50[dates[prev]] else 'NOT_MET'

# ---- chain builder: chain = (date, symbol) group of legs ----
def chains_of(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r['date'], r['symbol']), []).append(r)
    chains = []
    for (d, sym), legs in groups.items():
        legs.sort(key=lambda r: r['entry_time'])
        chains.append({
            'date': d, 'symbol': sym,
            'net': sum(l['net'] for l in legs),
            'gross': sum(l['gross'] for l in legs),
            'nlegs': len(legs),
            'first_entry': legs[0]['entry_time'],
            'double_stop': len(legs) == 2 and all(l['exit_reason'] == 'stop' for l in legs),
            'any_stop2': len(legs) == 2,
        })
    chains.sort(key=lambda c: (c['date'], c['first_entry'], c['symbol']))
    return chains

def longest_neg_streak(vals):
    best = cur = 0
    for v in vals:
        cur = cur + 1 if v < 0 else 0
        best = max(best, cur)
    return best

def risk_card(rows, label):
    chains = chains_of(rows)
    daily = defaultdict(float)
    for r in rows:
        daily[r['date']] += r['net']
    days = sorted(daily)
    # cumulative curve incl. start at 0
    cum, peak, maxdd = 0.0, 0.0, 0.0
    for d in days:
        cum += daily[d]
        peak = max(peak, cum)
        maxdd = min(maxdd, cum - peak)
    final_net = cum
    monthly = defaultdict(float)
    for d in days:
        monthly[d[:7]] += daily[d]
    worst_month = min(monthly.items(), key=lambda kv: kv[1])
    worst_days = sorted(days, key=lambda d: daily[d])[:5]
    ds_chains = [c for c in chains if c['double_stop']]
    two_leg = [c for c in chains if c['any_stop2']]
    worst_chain = min(chains, key=lambda c: c['net'])
    return {
        'label': label,
        'trades': len(rows), 'chains': len(chains),
        'final_net': round(final_net, 2),
        'gross_total': round(sum(r['gross'] for r in rows), 2),
        'active_days': len(days),
        'max_dd_rs': round(maxdd, 2),
        'max_dd_pct_of_final': round(100 * maxdd / final_net, 1) if final_net else None,
        'worst_day': (min(days, key=lambda d: daily[d]), round(min(daily.values()), 2)),
        'best_day': (max(days, key=lambda d: daily[d]), round(max(daily.values()), 2)),
        'losing_day_streak': longest_neg_streak([daily[d] for d in days]),
        'losing_chain_streak': longest_neg_streak([c['net'] for c in chains]),
        'pct_days_positive': round(100 * sum(1 for d in days if daily[d] > 0) / len(days), 1),
        'worst_month': (worst_month[0], round(worst_month[1], 2)),
        'monthly': {k: round(v, 2) for k, v in sorted(monthly.items())},
        'top5_worst_days': [(d, round(daily[d], 2)) for d in worst_days],
        'worst_chain': (worst_chain['date'], worst_chain['symbol'], round(worst_chain['net'], 2)),
        'double_stop_chains': len(ds_chains),
        'double_stop_share_all_pct': round(100 * len(ds_chains) / len(chains), 1),
        'two_leg_chains': len(two_leg),
        'double_stop_share_twoleg_pct': round(100 * len(ds_chains) / len(two_leg), 1) if two_leg else None,
        'double_stop_net': round(sum(c['net'] for c in ds_chains), 2),
    }, chains

cards, chain_sets = {}, {}
for rows, label in [(poola, 'MOVER-A pooled 50 (10:00)'), (poolb, 'MOVER-B pooled 50 (10:15)'), (ext, 'MOVER-A ext 25 (10:00)')]:
    card, ch = risk_card(rows, label)
    cards[label] = card
    chain_sets[label] = ch

# ---- regime split on MOVER-A pooled chains ----
buckets = defaultdict(lambda: {'chains': 0, 'net': 0.0})
unclassified = 0
for c in chain_sets['MOVER-A pooled 50 (10:00)']:
    reg = regime(c['date'])
    if reg is None:
        unclassified += 1
        continue
    buckets[reg]['chains'] += 1
    buckets[reg]['net'] += c['net']
split = {}
for k, v in buckets.items():
    split[k] = {'chains': v['chains'], 'net': round(v['net'], 2),
                'exp_per_chain': round(v['net'] / v['chains'], 2)}
split['unclassified'] = unclassified

# ---- size translation (accounting only): net(N) = gross*(N/100) - 40*trades ----
size = {}
for rows, label in [(poola, 'MOVER-A pooled 50'), (poolb, 'MOVER-B pooled 50')]:
    gross = sum(r['gross'] for r in rows)
    n = len(rows)
    size[label] = {sh: round(gross * sh / 100 - 40 * n, 2) for sh in (100, 200, 500, 1000)}
    size[label]['trades'] = n
    size[label]['gross_100'] = round(gross, 2)

out = {'cards': cards, 'regime_split_moverA_pooled': split, 'size_translation': size}
json.dump(out, open(BASE + 'stocks_mover_risk_card.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
