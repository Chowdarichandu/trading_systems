#!/usr/bin/env python3
"""V3 shared scoring library — one arithmetic for every v3 cycle.

boot(): execs the audited v2 build (ALL controls asserted in-pass) and the
frozen REGIME-CLASSIFIER-1 labels (price leg asserted == below50 on every
window day). score(): the v3 report block — 22-month vector (sorted +
labelled), bottom-5, year totals, combined, regime cells x year, ex-top-3
per year. decide(): the v3 banking test — lexicographic maximin beat AND
the hard constraints (neither year falls / neither negative / every cell
positive / combined does not fall).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
M25 = [f"2025-{i:02d}" for i in range(1, 13)]
M26 = [f"2026-{i:02d}" for i in range(1, 11)]
ALL_MONTHS = M25 + M26

def boot():
    g = {"__name__": "v2_build_exec"}
    exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
                 "stocks_engine_v2_build.py", "exec"), g)
    assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
    NIFTY_REG, below50 = g["NIFTY_REG"], g["below50"]
    axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
    labels = {}
    for j, d in enumerate(axis):
        if j < 5:
            continue
        pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
        s = m - NIFTY_REG[axis[j - 5]]["ma50"]
        labels[d] = "UP" if (pc > m and s >= 0) else \
            ("DOWN" if (pc <= m and s <= 0) else "FLAT")
    for d in axis:
        if "2025-01-01" <= d <= "2026-10-30":
            assert (NIFTY_REG[d]["prev_close"] <= NIFTY_REG[d]["ma50"]) == below50(d)
    return g, labels

def load_books(book_files):
    out = {}
    for yr in ("2025", "2026"):
        with open(f"{WS}/{book_files[yr]}") as f:
            out[yr] = [{**t, "net": float(t["net"])} for t in csv.DictReader(f)]
    return out

def dump_books(books, fn25, fn26):
    for yr, fn in (("2025", fn25), ("2026", fn26)):
        rows = sorted(books[yr], key=lambda t: (t["date"], t.get("entry_time", "09:15"),
                                                t["stock"], t["comp"]))
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["comp", "date", "stock", "dir",
                                              "entry_time", "net"])
            w.writeheader()
            for t in rows:
                w.writerow({k: t[k] for k in ("comp", "date", "stock", "dir",
                                               "entry_time", "net")})

def score(books, labels):
    months = {}
    for yr, ms in (("2025", M25), ("2026", M26)):
        m = defaultdict(float)
        for t in books[yr]:
            m[t["date"][:7]] += t["net"]
        for k in ms:
            months[k] = round(m.get(k, 0.0), 2)
    vec = sorted(months.values())
    bottom5 = sorted(months.items(), key=lambda kv: kv[1])[:5]
    years = {yr: round(sum(t["net"] for t in books[yr]), 2) for yr in ("2025", "2026")}
    trades = {yr: len(books[yr]) for yr in ("2025", "2026")}
    cells = {}
    for yr in ("2025", "2026"):
        cells[yr] = {}
        for cell in ("UP", "DOWN", "FLAT"):
            ts = [t for t in books[yr] if labels.get(t["date"]) == cell]
            cells[yr][cell] = round(sum(t["net"] for t in ts), 2)
    extop3 = {}
    for yr in ("2025", "2026"):
        p = defaultdict(float)
        for t in books[yr]:
            p[t["stock"]] += t["net"]
        top = {k for k, _ in sorted(p.items(), key=lambda kv: -kv[1])[:3]}
        extop3[yr] = round(sum(t["net"] for t in books[yr] if t["stock"] not in top), 2)
    return {"months": months, "vector_sorted": vec, "bottom5": bottom5,
            "years": years, "combined": round(years["2025"] + years["2026"], 2),
            "trades": trades, "cells": cells, "ex_top3": extop3}

def lexi_beats(new_vec, old_vec):
    """True iff sorted month vector improves lexicographically."""
    for a, b in zip(new_vec, old_vec):
        if round(a, 2) > round(b, 2):
            return True
        if round(a, 2) < round(b, 2):
            return False
    return False

def decide(old, new):
    """old/new are score() dicts. Returns (banked, checks dict)."""
    checks = {
        "lexi_maximin_beat": lexi_beats(new["vector_sorted"], old["vector_sorted"]),
        "y2025_not_fall": new["years"]["2025"] >= old["years"]["2025"],
        "y2026_not_fall": new["years"]["2026"] >= old["years"]["2026"],
        "neither_year_negative": new["years"]["2025"] >= 0 and new["years"]["2026"] >= 0,
        "combined_not_fall": new["combined"] >= old["combined"],
        "all_cells_positive": all(v > 0 for yr in ("2025", "2026")
                                  for v in new["cells"][yr].values()),
    }
    return all(checks.values()), checks
