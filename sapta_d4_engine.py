#!/usr/bin/env python3
"""
SAPTA Design 4 — engine additions: Daily-3's machine (sim3c_gated)
FROZEN at its base form plus the 200DMA trend gate on entries
(sapta_d4_SPEC.md s.4), and the Daily-4 placebo (SPEC s.5).
The intraday books reuse sapta_d3_engine verbatim (EKAM shell).
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40/trade. Paper only.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E
import sapta_d2_engine as D2

COST = 40.0

def ma200_gate_code(c):
    """Per-day gate code for the 200DMA trend gate (SPEC s.4):
    -1 = short history (fewer than 200 closes up to and including the
    day), 0 = close <= MA200 (below trend), 1 = close > MA200 (pass).
    MA200[i] = mean(c[i-199 .. i]), causal."""
    n = len(c)
    code = np.zeros(n, dtype=np.int8)
    if n == 0:
        return code
    cs = np.concatenate([[0.0], np.cumsum(c)])
    for i in range(n):
        if i < 199:
            code[i] = -1
        else:
            ma = (cs[i + 1] - cs[i - 199]) / 200.0
            code[i] = 1 if c[i] > ma else 0
    return code

def sim4c_gated(d, active=None, upgrade=True, time_days=60,
                allowed=('BB', 'RSI', 'MACD'), gate_code=None):
    """sapta_d3_engine.sim3c_gated with ONE change (SPEC s.4): when flat
    at day i with a non-empty firing set and an active entry day i+1, the
    entry fills only if gate_code is None or gate_code[i] == 1;
    otherwise the machine stays flat and advances (the single-day signal
    is missed, exactly as a non-active entry day is missed in D2/D3).
    Returns (trades, vetoes): vetoes = [{signal_date, reason}] for every
    while-flat signal the gate blocked (reason 'below_trend' /
    'short_history'). With gate_code=None this is sim3c_gated verbatim
    and vetoes is empty."""
    dates, o, h, l, c, n = d["dates"], d["o"], d["h"], d["l"], d["c"], d["n"]
    ALLOWED = list(allowed)
    trades = []; vetoes = []; pos = None; i = 0
    while i < n:
        if pos is None:
            sigs = [k for k in ALLOWED if d["sig_in"][k][i]]
            if sigs and i + 1 < n and (active is None or dates[i + 1] in active):
                if gate_code is not None and gate_code[i] != 1:
                    vetoes.append({'signal_date': dates[i],
                                   'reason': 'short_history'
                                   if gate_code[i] == -1 else 'below_trend'})
                    i += 1; continue
                pos = dict(e=i + 1, E=float(o[i + 1]), comps=tuple(sigs),
                           sig_date=dates[i], upgraded=False, up_idx=None,
                           up_date=None)
                i += 1; continue
            i += 1; continue
        held = [k for k in ALLOWED if d["sig_in"][k][i]]
        e, E_, comps = pos["e"], pos["E"], pos["comps"]
        converted_today = False
        if upgrade and comps == ("BB",) and not pos["upgraded"] and "RSI" in held:
            pos["upgraded"] = True; pos["up_idx"] = i; pos["up_date"] = dates[i]
            converted_today = True
        done = None
        if comps == ("BB",) and pos["upgraded"]:
            if not converted_today:
                if i - e >= time_days and i > e:
                    done = (i, float(o[i]), "TIME")
                if done is None and i >= e:
                    lvl = E_ * 1.10
                    if h[i] >= lvl:
                        done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
            if done is None and d["sig_out"]["RSI"][i]:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-RSI")
                else:
                    done = (i, float(c[i]), "FORCED")
        elif "RSI" in comps:
            if i - e >= time_days and i > e:
                done = (i, float(o[i]), "TIME")
            if done is None and i >= e:
                lvl = E_ * 1.10
                if h[i] >= lvl:
                    done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
            if done is None:
                fire = None
                for k in comps:
                    if d["sig_out"][k][i]:
                        fire = k; break
                if fire is not None:
                    if i + 1 < n:
                        done = (i + 1, float(o[i + 1]), "SIGNAL-" + fire)
                    else:
                        done = (i, float(c[i]), "FORCED")
        else:
            fire = None
            for k in comps:
                if d["sig_out"][k][i]:
                    fire = k; break
            if fire is not None:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-" + fire)
                else:
                    done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            trades.append(dict(
                sym=d["sym"], comps="+".join(comps),
                signal_date=pos["sig_date"], entry_date=dates[e],
                exit_date=dates[xi], entry=E_, exit=xp,
                net=round((xp - E_) * 100.0 - COST, 2), hold=xi - e,
                exit_kind=why, forced=(why == "FORCED"),
                upgraded=pos["upgraded"], upgrade_date=pos["up_date"],
                upgrade_offset=(pos["up_idx"] - e) if pos["upgraded"] else None,
                counted_upgrade=bool(pos["upgraded"] and xi > pos["up_idx"])))
            pos = None; i = xi; continue
        i += 1
    if pos is not None:
        e, E_ = pos["e"], pos["E"]
        xp = float(c[n - 1])
        trades.append(dict(
            sym=d["sym"], comps="+".join(pos["comps"]),
            signal_date=pos["sig_date"], entry_date=dates[e],
            exit_date=dates[n - 1], entry=E_, exit=xp,
            net=round((xp - E_) * 100.0 - COST, 2), hold=n - 1 - e,
            exit_kind="FORCED", forced=True,
            upgraded=pos["upgraded"], upgrade_date=pos["up_date"],
            upgrade_offset=(pos["up_idx"] - e) if pos["upgraded"] else None,
            counted_upgrade=bool(pos["upgraded"] and (n - 1) > pos["up_idx"])))
    return trades, vetoes

def placebo_daily_d4(d, real_trades, windows, variant, gate_code,
                     draws=200, seed=E.SEED, single_cache=None):
    """SPEC s.5 daily: per real trade, an entry day drawn uniformly from
    the name's selected days in the same quarter-window whose prior day
    carries a non-empty Design-3 firing set (BB or RSI or MACD) AND
    passes the 200DMA gate, and which is not the series' last day; a
    standalone gated machine (only that entry day allowed, gate active)
    produces the placebo trade's net; an empty sample space contributes
    0. Returns (draws x 2) nets by the REAL trade's entry year."""
    rng = np.random.default_rng(seed)
    out = np.zeros((draws, 2))
    pos = {dt: i for i, dt in enumerate(d['dates'])}
    last_date = d['dates'][-1]
    dv = D2.prep_with_rsiexit(d, variant['rsiexit'])
    vkey = (variant['upgrade'], variant['time'], variant['rsiexit'], 'D4G')
    cache = single_cache if single_cache is not None else {}

    def single_net(D_):
        key = (d['sym'], vkey, D_)
        if key not in cache:
            tr, _v = sim4c_gated(dv, active={D_}, upgrade=variant['upgrade'],
                                 time_days=variant['time'],
                                 gate_code=gate_code)
            mine = [t for t in tr if t['entry_date'] == D_]
            cache[key] = float(mine[0]['net']) if mine else 0.0
        return cache[key]

    items = []
    for t in real_trades:
        days = windows.get(t['date'], [])
        space = []
        for D_ in days:
            pi = pos.get(D_)
            if pi is None or pi == 0 or D_ == last_date:
                continue
            si = pi - 1
            if gate_code[si] != 1:
                continue
            if (d['sig_in']['BB'][si] or d['sig_in']['RSI'][si]
                    or d['sig_in']['MACD'][si]):
                space.append(D_)
        items.append((t, space))
    for dr in range(draws):
        for t, space in items:
            if not space:
                continue
            D_ = space[rng.integers(0, len(space))]
            yr = 0 if t['date'] < '2026-01-01' else 1
            out[dr, yr] += single_net(D_)
    return out
