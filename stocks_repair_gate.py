#!/usr/bin/env python3
"""STEP 2 + 3 data - Stock Book repair gate (spec: stocks_repair_SPEC.md, frozen
before this scoring) and the three-lines month table data.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper."""
import csv, json, random
from collections import defaultdict

RAW_TOT = {2025: 119813.44, 2026: 247178.79}
RAW_RED = {2025: {'2025-07', '2025-10'}, 2026: set()}
TOL = {2025: round(0.02 * RAW_TOT[2025], 2), 2026: round(0.02 * RAW_TOT[2026], 2)}

def load(fn):
    rows = []
    with open(fn) as f:
        for r in csv.DictReader(f):
            r['net'] = float(r['net'])
            if r['date'][5:7] in ('11', '12'):
                continue
            rows.append(r)
    return rows

def months_of(rows):
    m = defaultdict(float)
    for r in rows:
        m[r['date'][:7]] += r['net']
    return {k: round(v, 2) for k, v in sorted(m.items())}

def halves_of(rows):
    h1 = round(sum(r['net'] for r in rows if r['date'][5:7] in ('01','02','03','04','05')), 2)
    h2 = round(sum(r['net'] for r in rows if r['date'][5:7] in ('06','07','08','09','10')), 2)
    return h1, h2

def total(rows): return round(sum(r['net'] for r in rows), 2)
def wr(rows): return round(100.0 * sum(1 for r in rows if r['net'] > 0) / len(rows), 2) if rows else 0.0

CANDS = {
    'S-FIX-1': lambda r: r['comp'] == 'INV-ABOVE' and r['entry_time'] <= '09:35',
    'S-FIX-2': lambda r: r['comp'] == 'INV-LONG' and r['entry_time'] <= '09:35',
}

data = {2025: load('stocks_engine_adoptedC_book2025_trades.csv'),
        2026: load('stocks_engine_adoptedC_book2026_trades.csv')}
res = {'control': {}, 'candidates': {}}
for yr in (2025, 2026):
    assert total(data[yr]) == RAW_TOT[yr], (yr, total(data[yr]))
    res['control'][yr] = {'legs': len(data[yr]), 'total': total(data[yr]), 'wr': wr(data[yr]),
                          'months': months_of(data[yr]), 'halves': halves_of(data[yr])}

# November log
nov = []
with open('stocks_sarvaritu_paper_log.csv') as f:
    for r in csv.DictReader(f):
        if r['date'].startswith('2026-11'):
            r['net'] = float(r['net'])
            nov.append(r)
assert len(nov) == 32 and round(sum(r['net'] for r in nov), 2) == 7517.94
res['november_actual'] = {'legs': 32, 'total': 7517.94}

for name, rule in CANDS.items():
    c = {'per_year': {}, 'november': {}}
    pooled_impr = 0.0
    for yr in (2025, 2026):
        rows = data[yr]
        skipped = [r for r in rows if rule(r)]
        kept = [r for r in rows if not rule(r)]
        rep_tot, raw_tot = total(kept), total(rows)
        impr = round(rep_tot - raw_tot, 2)
        pooled_impr += impr
        rep_months = months_of(kept)
        new_red = sorted(m for m, v in rep_months.items() if v < 0 and m not in RAW_RED[yr])
        rh1, rh2 = halves_of(kept)
        h1, h2 = halves_of(rows)
        half_drops = {'H1': round(rh1 - h1, 2), 'H2': round(rh2 - h2, 2)}
        half_fail = any(d < -TOL[yr] for d in half_drops.values())
        entry = {'skipped_legs': len(skipped), 'skipped_net': total(skipped),
                 'kept_legs': len(kept), 'repaired_total': rep_tot, 'raw_total': raw_tot,
                 'improvement': impr, 'degrade_pct_of_raw': round(-100.0 * impr / raw_tot, 2) if impr < 0 else 0.0,
                 'repaired_wr': wr(kept), 'months': rep_months, 'new_red_months': new_red,
                 'halves_repaired': [rh1, rh2], 'halves_raw': [h1, h2],
                 'half_deltas': half_drops, 'half_fail_d': half_fail}
        if impr > 0:  # placebo in improved years only (spec leg c)
            k = len(skipped)
            nets = [r['net'] for r in rows]
            beats = 0
            for s in range(2000, 2200):
                draw = random.Random(s).sample(nets, k)
                if rep_tot > round(raw_tot - sum(draw), 2):
                    beats += 1
            entry['placebo_pct_beaten'] = round(100.0 * beats / 200, 1)
            entry['placebo_pass_c'] = entry['placebo_pct_beaten'] >= 95.0
        c['per_year'][yr] = entry
    # gate verdict legs (a),(b),(d) here; (c) inside improved years
    yrs = c['per_year']
    improves = [yr for yr in (2025, 2026) if yrs[yr]['improvement'] > 0]
    a_pass = bool(improves) and all(yrs[yr]['improvement'] >= -TOL[yr] for yr in (2025, 2026))
    b_pass = all(not yrs[yr]['new_red_months'] for yr in (2025, 2026))
    c_pass = all(yrs[yr].get('placebo_pass_c', False) for yr in improves) if improves else False
    d_pass = all(not yrs[yr]['half_fail_d'] for yr in (2025, 2026))
    c['gate'] = {'a_cross_year': a_pass, 'b_no_new_red': b_pass, 'c_placebo': c_pass,
                 'd_halves': d_pass, 'verdict': 'PASS' if (a_pass and b_pass and c_pass and d_pass) else 'FAIL',
                 'improved_years': improves, 'pooled_improvement': round(pooled_impr, 2)}
    # November application (descriptive)
    nskip = [r for r in nov if rule(r)]
    c['november'] = {'skipped': [{'date': r['date'], 'comp': r['comp'], 'stock': r['stock'],
                                  'entry_time': r['entry_time'], 'net': r['net']} for r in nskip],
                     'skipped_net': total(nskip),
                     'repaired_nov_total': round(7517.94 - total(nskip), 2)}
    res['candidates'][name] = c

# Confidence T70 month detail from the frozen confidence run (verify anchors)
conf = json.load(open('phase2_confidence_stocks_results.json'))
t70 = {}
for yr in (2025, 2026):
    m = conf[f'year_{yr}']['levels']['T70']['months']
    t70[yr] = {k: round(v, 2) for k, v in m.items()}
    s = round(sum(t70[yr].values()), 2)
    anchor = 81309.57 if yr == 2025 else 190757.68
    assert s == anchor, (yr, s, anchor)
    t70[f'{yr}_kept_legs'] = conf[f'year_{yr}']['levels']['T70']['kept']
res['confidence_T70_months'] = t70
res['confidence_T70_november'] = {'kept_basis_total': 6794.44, 'unscored_excluded_total': 731.77,
    'note': 'UNSCORED-kept basis: only Nov 2 (4 legs) scorable; T70 idled +723.50 that day (HINDZINC F4)'}

with open('stocks_repair_results.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
