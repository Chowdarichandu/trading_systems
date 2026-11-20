#!/usr/bin/env python3
"""
SAPTA Design 10 — engine additions (sapta_d10_SPEC.md):
  * exit_run10: the DailyStepper8 exit governance transcribed as a
    standalone function (Design 8 SPEC s.2 — itself a verbatim
    transcription of sapta_d4_engine.sim4c_gated with gate_code=None),
    with an optional trigger-window limit (last_trigger) used ONLY for
    the causal skip check of SPEC s.2;
  * run_daily_delayed_name: the entry-delay driver (offset parameter;
    offset=1 is the native machine — control C-16; offset=5 is
    Daily-10).
The intraday shells, the daily placebo and the gate are Designs 3/8's
and sapta_owner_engine's, reused verbatim.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade. Paper only.
"""
import os, sys

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E
import sapta_d8_engine as D8

BASE = E.BASE
COST = 40.0
ALLOWED = D8.ALLOWED          # ('BB', 'RSI', 'MACD')


def _trade_row(d, pos, xi, xp, why):
    e, E_ = pos['e'], pos['E']
    return dict(
        sym=d['sym'], comps='+'.join(pos['comps']),
        signal_date=pos['sig_date'], entry_date=d['dates'][e],
        exit_date=d['dates'][xi], entry=E_, exit=xp,
        net=round((xp - E_) * 100.0 - COST, 2), hold=xi - e,
        exit_kind=why, forced=(why == 'FORCED'),
        upgraded=pos['upgraded'], upgrade_date=pos['up_date'],
        upgrade_offset=(pos['up_idx'] - e) if pos['upgraded'] else None,
        counted_upgrade=bool(pos['upgraded'] and xi > pos['up_idx'])), xi


def exit_run10(d, pos, cap_mult=1.10, time_days=60, upgrade=True,
               last_trigger=None):
    """Exit governance of DailyStepper8.approve, transcribed verbatim
    (trigger evaluation starts at the entry day pos['e']).
    If last_trigger is not None, only trigger days <= last_trigger are
    evaluated and (None, None) is returned when no exit completes in
    that window — the position is still open at the open of
    last_trigger + 1. Otherwise the run completes (incl. the
    end-of-series FORCED) and returns (trade, exit_index)."""
    dates, o, h, l, c, n = d['dates'], d['o'], d['h'], d['l'], d['c'], d['n']
    pos = dict(pos)
    i = pos['e']
    while i < n:
        if last_trigger is not None and i > last_trigger:
            return None, None
        held = [k for k in ALLOWED if d['sig_in'][k][i]]
        e, E_, comps = pos['e'], pos['E'], pos['comps']
        converted_today = False
        if upgrade and comps == ('BB',) and not pos['upgraded'] \
                and 'RSI' in held:
            pos['upgraded'] = True; pos['up_idx'] = i
            pos['up_date'] = dates[i]
            converted_today = True
        done = None
        if comps == ('BB',) and pos['upgraded']:
            if not converted_today:
                if i - e >= time_days and i > e:
                    done = (i, float(o[i]), 'TIME')
                if done is None and i >= e:
                    lvl = E_ * cap_mult
                    if h[i] >= lvl:
                        done = (i, float(o[i]) if o[i] >= lvl else lvl,
                                'CAP')
            if done is None and d['sig_out']['RSI'][i]:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), 'SIGNAL-RSI')
                else:
                    done = (i, float(c[i]), 'FORCED')
        elif 'RSI' in comps:
            if i - e >= time_days and i > e:
                done = (i, float(o[i]), 'TIME')
            if done is None and i >= e:
                lvl = E_ * cap_mult
                if h[i] >= lvl:
                    done = (i, float(o[i]) if o[i] >= lvl else lvl, 'CAP')
            if done is None:
                fire = None
                for k in comps:
                    if d['sig_out'][k][i]:
                        fire = k; break
                if fire is not None:
                    if i + 1 < n:
                        done = (i + 1, float(o[i + 1]), 'SIGNAL-' + fire)
                    else:
                        done = (i, float(c[i]), 'FORCED')
        else:
            fire = None
            for k in comps:
                if d['sig_out'][k][i]:
                    fire = k; break
            if fire is not None:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), 'SIGNAL-' + fire)
                else:
                    done = (i, float(c[i]), 'FORCED')
        if done is not None:
            xi, xp, why = done
            return _trade_row(d, pos, xi, xp, why)
        i += 1
    if last_trigger is not None:
        return None, None
    e, E_ = pos['e'], pos['E']
    xp = float(c[n - 1])
    return _trade_row(d, pos, n - 1, xp, 'FORCED')


def run_daily_delayed_name(d, active, offset=5, cap_mult=1.10,
                           time_days=60, upgrade=True):
    """Daily-10 entry-delay driver for one name (SPEC s.2). `active` is
    the set of selected dates for the name. offset=1 reproduces the
    native machine (control C-16): the skip window is empty and the
    fill gate coincides with candidacy. Returns (trades, stats);
    trades are sim-shaped dicts (as DailyStepper8.approve produces)
    with added 'fill_offset' and 'native_entry_date' keys."""
    dates, o, n = d['dates'], d['o'], d['n']
    active = set(active)
    trades = []
    stats = {'signals': 0, 'filled': 0, 'skipped_native_exit': 0,
             'discarded_fill_gate': 0, 'discarded_no_room': 0,
             'by_year': {}}

    def bump(kind, sig_date):
        stats[kind] += 1
        yb = stats['by_year'].setdefault(
            sig_date[:4], {'signals': 0, 'filled': 0,
                           'skipped_native_exit': 0,
                           'discarded_fill_gate': 0,
                           'discarded_no_room': 0})
        yb[kind] += 1

    scan = 0
    while True:
        s = None
        i = scan
        while i < n:
            sigs = [k for k in ALLOWED if d['sig_in'][k][i]]
            if sigs and i + 1 < n and dates[i + 1] in active:
                s = i
                break
            i += 1
        if s is None:
            break
        bump('signals', dates[s])
        comps = tuple(k for k in ALLOWED if d['sig_in'][k][s])
        f = s + offset
        if offset != 1:
            if f >= n:
                bump('discarded_no_room', dates[s])
                scan = s + 1
                continue
            if dates[f] not in active:
                bump('discarded_fill_gate', dates[s])
                scan = s + 1
                continue
            hypo, _xi = exit_run10(
                d, dict(e=s + 1, E=float(o[s + 1]), comps=comps,
                        sig_date=dates[s], upgraded=False, up_idx=None,
                        up_date=None),
                cap_mult=cap_mult, time_days=time_days, upgrade=upgrade,
                last_trigger=f - 1)
            if hypo is not None:
                bump('skipped_native_exit', dates[s])
                scan = s + 1
                continue
        tr, xi = exit_run10(
            d, dict(e=f, E=float(o[f]), comps=comps,
                    sig_date=dates[s], upgraded=False, up_idx=None,
                    up_date=None),
            cap_mult=cap_mult, time_days=time_days, upgrade=upgrade)
        tr['fill_offset'] = offset
        tr['native_entry_date'] = dates[s + 1]
        trades.append(tr)
        bump('filled', dates[s])
        scan = xi
    return trades, stats
