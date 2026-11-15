#!/usr/bin/env python3
"""STEP 1 - ANATOMY for the Stock Book repair run (2026-11-14).
Mirror of november_books_fix Phase 1 method, applied to the Stock Book.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper.
Store carries per leg: comp, date, stock, dir, entry_time, net.
Entry-knowable slice dims available: comp x side x entry-time bucket.
Prior-day-move band / price band: NOT carried in the gated store -> dropped, stated.
"""
import csv, json
from collections import defaultdict

def load(fn, jan_oct_only=True):
    rows = []
    with open(fn) as f:
        for r in csv.DictReader(f):
            r['net'] = float(r['net'])
            if jan_oct_only and r['date'][5:7] in ('11', '12'):
                continue
            rows.append(r)
    return rows

def bucket(t):
    # entry-time buckets frozen for this run: open wave / mid wave / second wave
    if t <= '09:35': return 'B1 <=09:35'
    if t <= '10:25': return 'B2 09:40-10:25'
    return 'B3 >=10:30'

def stats(legs):
    nets = sorted((r['net'] for r in legs), reverse=True)
    n = len(legs)
    tot = round(sum(nets), 2)
    wr = round(100.0 * sum(1 for x in nets if x > 0) / n, 2) if n else 0.0
    ex_top3 = round(tot - sum(nets[:3]), 2) if n > 3 else None
    minus_worst = round(tot - nets[-1], 2) if n else None
    return {'legs': n, 'net': tot, 'wr': wr, 'ex_top3': ex_top3,
            'minus_worst_leg': minus_worst, 'avg_per_leg': round(tot / n, 2) if n else 0.0}

def slice_table(rows, keys):
    cells = defaultdict(list)
    for r in rows:
        cells[tuple(r[k] if k != 'bucket' else bucket(r['entry_time']) for k in keys)].append(r)
    return { ' x '.join(k): stats(v) for k, v in cells.items() }

out = {}
data = {}
for yr, fn in ((2025, 'stocks_engine_adoptedC_book2025_trades.csv'),
               (2026, 'stocks_engine_adoptedC_book2026_trades.csv')):
    rows = load(fn)
    for r in rows:
        r['bucket'] = bucket(r['entry_time'])
    data[yr] = rows
    out[f'control_{yr}'] = stats(rows)

pooled = data[2025] + data[2026]
dims = [('comp',), ('dir',), ('bucket',), ('comp', 'dir'), ('comp', 'bucket'),
        ('dir', 'bucket'), ('comp', 'dir', 'bucket')]
for keys in dims:
    name = '+'.join(keys)
    out[f'slice_{name}'] = {
        '2025': slice_table(data[2025], keys),
        '2026': slice_table(data[2026], keys),
        'pooled': slice_table(pooled, keys),
    }

with open('stocks_repair_anatomy.json', 'w') as f:
    json.dump(out, f, indent=1)

# print controls + negative cells meeting the size screen
print('CONTROLS:', json.dumps({k: out[k] for k in ('control_2025', 'control_2026')}))
print()
print('NEGATIVE CELLS (legs>=15 in a year OR >=25 pooled), sorted by pooled net:')
cands = []
for name in dims:
    nm = '+'.join(name)
    s = out[f'slice_{nm}']
    allcells = set(s['2025']) | set(s['2026']) | set(s['pooled'])
    for c in allcells:
        a = s['2025'].get(c, {'legs': 0, 'net': 0.0, 'wr': 0.0, 'ex_top3': None})
        b = s['2026'].get(c, {'legs': 0, 'net': 0.0, 'wr': 0.0, 'ex_top3': None})
        p = s['pooled'].get(c, {'legs': 0, 'net': 0.0})
        if (a['legs'] >= 15 or b['legs'] >= 15 or p['legs'] >= 25) and (a['net'] < 0 or b['net'] < 0):
            cands.append((p['net'], nm, c, a, b, p))
for pnet, nm, c, a, b, p in sorted(cands):
    print(f"{nm:22s} {c:45s} pooled {p['legs']:4d} legs {pnet:12.2f} | "
          f"2025 {a['legs']:4d} {a['net']:11.2f} wr{a['wr']:6.2f} ex3 {a['ex_top3']} | "
          f"2026 {b['legs']:4d} {b['net']:11.2f} wr{b['wr']:6.2f} ex3 {b['ex_top3']}")
