#!/usr/bin/env python3
"""REPAIR PROGRAMME 2026-11-12 — gated computations.
All variants are drop-only admission filters on pre-scored leg lists.
Gate (project standard, per EVE-07..20 summaries): candidate FAILS if any of
  total <= incumbent | a month flips green->red | H1 < inc H1 | H2 < inc H2 |
  ex-top-3 legs <= inc | ex-top-3 days <= inc | placebo not beaten (total <= placebo).
Independent re-sum: totals computed twice (row loop + day-aggregate loop)."""
import csv, json, collections

def load(f):
    rows = list(csv.DictReader(open(f)))
    for r in rows:
        r['net'] = float(r['net_inr'])
    return rows

def battery(rows):
    months = collections.defaultdict(float)
    days = collections.defaultdict(float)
    for r in rows:
        months[r['date'][:7]] += r['net']
        days[r['date']] += r['net']
    nets = sorted((r['net'] for r in rows), reverse=True)
    dnets = sorted(days.values(), reverse=True)
    total = sum(r['net'] for r in rows)
    total2 = sum(days.values())
    assert abs(total - total2) < 0.01, 're-sum mismatch'
    return {
        'n_legs': len(rows), 'n_days': len(days), 'total': round(total, 2),
        'months': {k: round(v, 2) for k, v in sorted(months.items())},
        'H1': round(sum(v for k, v in months.items() if k <= '2026-06'), 2),
        'H2': round(sum(v for k, v in months.items() if k >= '2026-07'), 2),
        'ex_top3_legs': round(total - sum(nets[:3]), 2),
        'ex_top3_days': round(total - sum(dnets[:3]), 2),
        'worst_day': round(min(days.values()), 2) if days else 0.0,
        'resum_check': round(total2, 2),
    }

def gate(cand, inc, placebo_totals):
    fails = []
    if cand['total'] <= inc['total']:
        fails.append(f"total {cand['total']} !> incumbent {inc['total']}")
    for m, v in inc['months'].items():
        cv = cand['months'].get(m, 0.0)
        if v > 0 and cv <= 0:
            fails.append(f"month {m} flips green->red ({v} -> {cv})")
    if cand['H1'] < inc['H1']:
        fails.append(f"H1 {cand['H1']} < incumbent {inc['H1']}")
    if cand['H2'] < inc['H2']:
        fails.append(f"H2 {cand['H2']} < incumbent {inc['H2']}")
    if cand['ex_top3_legs'] <= inc['ex_top3_legs']:
        fails.append(f"ex-top3 legs {cand['ex_top3_legs']} !> incumbent {inc['ex_top3_legs']}")
    if cand['ex_top3_days'] <= inc['ex_top3_days']:
        fails.append(f"ex-top3 days {cand['ex_top3_days']} !> incumbent {inc['ex_top3_days']}")
    for name, pt in placebo_totals.items():
        if cand['total'] <= pt:
            fails.append(f"placebo not beaten: {name} {pt} >= cand {cand['total']}")
    return fails

out = {}

# ============ BANK B1: v21 frame (incumbent = BNF-PAPER-V1's Jan-Oct frame) ============
v21 = load('bank_engine_r8_v21_regen_trades.csv')
inc = battery(v21)
out['B1_incumbent_v21'] = inc
assert inc['n_legs'] == 99 and abs(inc['total'] - 83650.50) < 0.01, inc

skill_pe = [r for r in v21 if r['rep'] == 'Skill V3' and r['direction'] == 'PE']
skill_pe_late = [r for r in skill_pe if r['entry_time'] >= '10:15']
out['B1_skill_pe_population'] = {
    'all_skill_pe': {'n': len(skill_pe), 'net': round(sum(r['net'] for r in skill_pe), 2)},
    'skill_pe_late>=10:15': {'n': len(skill_pe_late), 'net': round(sum(r['net'] for r in skill_pe_late), 2),
                             'legs': [(r['date'], r['entry_time'], r['net']) for r in skill_pe_late]},
    'skill_pe_early<10:15': {'n': len(skill_pe) - len(skill_pe_late),
                             'net': round(sum(r['net'] for r in skill_pe) - sum(r['net'] for r in skill_pe_late), 2)},
}

def drop(rows, keys):
    ks = set(keys)
    return [r for r in rows if id(r) not in ks]

# BV-1: drop Skill V3 PE legs entering >= 10:15
bv1_dropped = skill_pe_late
bv1 = [r for r in v21 if not (r['rep'] == 'Skill V3' and r['direction'] == 'PE' and r['entry_time'] >= '10:15')]
# placebo: chrono-skip-first-N Skill V3 PE legs (any entry time), N = |dropped|
n1 = len(bv1_dropped)
pe_chrono = sorted(skill_pe, key=lambda r: (r['date'], r['entry_time']))
placebo1_rows = [r for r in v21 if r not in pe_chrono[:n1]]
out['BV1'] = {'candidate': battery(bv1), 'dropped_n': n1,
              'placebo_chrono_firstN_skillPE': battery(placebo1_rows)['total']}
out['BV1']['gate_fails'] = gate(out['BV1']['candidate'], inc,
                                {'chrono_firstN_skillPE': out['BV1']['placebo_chrono_firstN_skillPE']})

# BV-2: drop ALL Skill V3 PE legs
bv2 = [r for r in v21 if not (r['rep'] == 'Skill V3' and r['direction'] == 'PE')]
n2 = len(skill_pe)
skill_all = sorted([r for r in v21 if r['rep'] == 'Skill V3'], key=lambda r: (r['date'], r['entry_time']))
placebo2_rows = [r for r in v21 if r not in skill_all[:n2]]
mirror2 = [r for r in v21 if not (r['rep'] == 'Skill V3' and r['direction'] == 'CE')]
out['BV2'] = {'candidate': battery(bv2), 'dropped_n': n2,
              'placebo_chrono_firstN_skill': battery(placebo2_rows)['total'],
              'placebo_mirror_drop_skillCE': battery(mirror2)['total']}
out['BV2']['gate_fails'] = gate(out['BV2']['candidate'], inc,
                                {'chrono_firstN_skill': out['BV2']['placebo_chrono_firstN_skill'],
                                 'mirror_drop_skillCE': out['BV2']['placebo_mirror_drop_skillCE']})

# ============ BANK B2: stack v2 (EVE-19) centred variants ============
stack = load('bank_positive_tuning_2026-11-10_eve19_trades.csv')
sinc = battery(stack)
out['B2_incumbent_stackv2'] = sinc
assert sinc['n_legs'] == 111 and abs(sinc['total'] - 127351.50) < 0.01, sinc

SECOND = {'NS1_second', 'NS3_gapclass', 'S3-R1', 'S3-PDC', 'EVE06_REENTRY'}
by_date = collections.defaultdict(list)
for r in stack:
    by_date[r['date']].append(r)

# B2-LITERAL (day-level existence) — NON-CAUSAL, observation only
lit = [r for r in stack if r['family'] in SECOND or
       any(x['family'] in SECOND for x in by_date[r['date']])]
out['B2_LITERAL_observation_only'] = {'candidate': battery(lit),
                                      'note': 'uses end-of-day knowledge for morning BASE legs — timing audit FAIL, never a candidate'}

# B2-FOLLOWER (causal): BASE leg kept only if a second-leg-family leg entered EARLIER same day
fol = []
for r in stack:
    if r['family'] in SECOND:
        fol.append(r)
    elif any(x['family'] in SECOND and x['entry_time'] < r['entry_time'] for x in by_date[r['date']]):
        fol.append(r)
dropped_base = [r for r in stack if r['family'] == 'BASE' and r not in fol]
nd = len(dropped_base)
base_chrono = sorted([r for r in stack if r['family'] == 'BASE'], key=lambda r: (r['date'], r['entry_time']))
placebo_fol = [r for r in stack if r not in base_chrono[-nd:]] if nd else stack[:]  # latest-skip placebo (EVE-19 convention)
anti = [r for r in stack if r['family'] in SECOND or
        not any(x['family'] in SECOND for x in by_date[r['date']])]  # anti-rule: BASE only on days with NO second leg
out['B2_FOLLOWER'] = {'candidate': battery(fol), 'dropped_base_n': nd,
                      'placebo_latest_skip_BASE': battery(placebo_fol)['total'],
                      'placebo_antirule': battery(anti)['total']}
out['B2_FOLLOWER']['gate_fails'] = gate(out['B2_FOLLOWER']['candidate'], sinc,
                                        {'latest_skip_BASE': out['B2_FOLLOWER']['placebo_latest_skip_BASE'],
                                         'antirule': out['B2_FOLLOWER']['placebo_antirule']})
# pure second-leg-only subset (observation)
pure = [r for r in stack if r['family'] in SECOND]
out['B2_pure_second_only_observation'] = battery(pure)

print(json.dumps(out, indent=1))
json.dump(out, open('repair_programme_2026-11-12_results.json', 'w'), indent=1)
