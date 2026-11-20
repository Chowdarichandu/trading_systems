#!/usr/bin/env python3
"""
SAPTA Design 26 — gate engine (sapta_d26_SPEC.md s.2).

The three books are Design 25's streams verbatim
(sapta_d25_engine: run_survey / summarise_stream /
placebo_d25, reused unchanged). This module adds only
the full-gate arithmetic on a book's trade rows:

  leg 1  net positive both years (EKAM attribution,
         from the D25 summary blocks)
  leg 2  placebo percentile > 90.0 both years
         (sapta_d25_engine.placebo_d25, the frozen D25
         s.2 recipe — computed by the run, passed in)
  leg 3  ex-top-3 positive both years (D25 summary)
  leg 4  month floor: worst calendar month >= -15,000
         on BOTH the exit-month basis (the standing
         sapta_owner_engine.worst_month convention) and
         the entry-month basis (the D16 SPEC text), over
         ALL book trades
  leg 5  EKAM bar: net >= Cand-1 AND >= Cand-2 in both
         years

Plus the reported-alongside figures: max drawdown (the
sapta_owner_engine.max_dd convention: cumulative net
ordered by (exit date, entry date)), month tables, and
per-year distances to Cand-1 / Cand-2 / EKAM-Daily home.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40
per completed trade. Paper only, real Rs 0.
"""
import numpy as np

MONTH_FLOOR = -15000.0
EKAM_CAND = {'Cand-1': (62164.57, 63883.60),
             'Cand-2': (45300.64, 72605.30)}
EKAM_HOME = (42954.60, 141328.40)


def month_table(rows, basis):
    """basis: 'exit' -> exit_date month; 'entry' -> entry
    (date) month. Returns {month: net} over all rows."""
    key = 'exit_date' if basis == 'exit' else 'date'
    m = {}
    for t in rows:
        k = t[key][:7]
        m[k] = round(m.get(k, 0.0) + t['net_inr'], 2)
    return m


def worst_month(rows, basis):
    m = month_table(rows, basis)
    if not m:
        return (None, 0.0)
    k = min(m, key=m.get)
    return (k, m[k])


def max_dd(rows):
    """sapta_owner_engine.max_dd convention on D25 rows:
    order by (exit_stamp, entry_stamp), cumulative net,
    min(cum - running peak)."""
    if not rows:
        return 0.0
    ts = sorted(rows, key=lambda t: (t['exit_date'], t['date']))
    cum = np.cumsum([t['net_inr'] for t in ts])
    peak = np.maximum.accumulate(cum)
    return round(float(np.min(cum - peak)), 2)


def gate_book(summary, placebo, rows):
    """Assemble the five gate lines for one book.
    summary: sapta_d25_engine.summarise_stream output.
    placebo: sapta_d25_engine.placebo_d25 output.
    rows: the book's full trade-row list."""
    y25, y26 = summary['2025'], summary['2026']
    n25, n26 = y25['net_inr'], y26['net_inr']
    p25, p26 = placebo['2025']['pct'], placebo['2026']['pct']
    wm_e = worst_month(rows, 'exit')
    wm_n = worst_month(rows, 'entry')
    legs = {}
    legs['leg1_net_pos_both'] = bool(n25 > 0 and n26 > 0)
    legs['leg2_placebo_gt90_both'] = bool(p25 > 90.0 and p26 > 90.0)
    legs['leg3_extop3_pos_both'] = bool(y25['ex_top3'] > 0
                                       and y26['ex_top3'] > 0)
    legs['leg4_month_floor'] = bool(wm_e[1] >= MONTH_FLOOR
                                    and wm_n[1] >= MONTH_FLOOR)
    legs['leg5_ekam_bar'] = bool(
        n25 >= EKAM_CAND['Cand-1'][0] and n25 >= EKAM_CAND['Cand-2'][0]
        and n26 >= EKAM_CAND['Cand-1'][1]
        and n26 >= EKAM_CAND['Cand-2'][1])
    core4 = [legs['leg1_net_pos_both'], legs['leg2_placebo_gt90_both'],
             legs['leg3_extop3_pos_both'], legs['leg4_month_floor']]
    legs['standing_legs_passed'] = int(sum(core4))
    legs['all_five_pass'] = bool(all(core4) and legs['leg5_ekam_bar'])
    detail = {
        'net': {'2025': n25, '2026': n26},
        'placebo_pct': {'2025': p25, '2026': p26},
        'placebo_draw_mean': {'2025': placebo['2025']['draw_mean'],
                              '2026': placebo['2026']['draw_mean']},
        'ex_top3': {'2025': y25['ex_top3'], '2026': y26['ex_top3']},
        'worst_month_exit_basis': {'month': wm_e[0], 'net': wm_e[1]},
        'worst_month_entry_basis': {'month': wm_n[0], 'net': wm_n[1]},
        'ekam_distance': {
            yr: {'vs_Cand-1': round(n - EKAM_CAND['Cand-1'][i], 2),
                 'vs_Cand-2': round(n - EKAM_CAND['Cand-2'][i], 2),
                 'vs_EKAM-Daily_home': round(n - EKAM_HOME[i], 2)}
            for i, (yr, n) in enumerate((('2025', n25),
                                         ('2026', n26)))},
        'max_dd': max_dd(rows),
        'month_table_exit': month_table(rows, 'exit'),
        'month_table_entry': month_table(rows, 'entry'),
    }
    return legs, detail
