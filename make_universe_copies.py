"""LINE 4 — generate the ext engine copies by EXACT string substitution only
(no logic edits). Every replacement is asserted (occurrence count), and a
reverse-substitution audit must reproduce the original file byte-for-byte.

Copies:
  stocks_equity_reentry_ext.py    data path -> progressive_ext, SYMBOLS -> new 25,
                                  calendar -> ext calendar
  stocks_equity_round8_ext.py     exec target -> reentry_ext, adr paths -> progressive_ext
  stocks_reaction_profiles_ext.py data paths -> *_ext, SYMBOLS -> new 25,
                                  calendar -> ext calendar, outputs prefixed universe_ext_
  stocks_reaction_profiles_val.py ONLY output prefixes (validation copy: must
                                  reproduce the published P1/P2 anchors)
"""
import difflib, os, sys

T = os.path.expanduser("~/workspace/trading")
OLD_SYMS = '''SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]'''
NEW_SYMS = '''SYMBOLS = ["RELIANCE","TCS","ICICIBANK","INFY","BHARTIARTL","SBIN","LT",
           "AXISBANK","KOTAKBANK","BAJFINANCE","HCLTECH","MARUTI","SUNPHARMA",
           "TITAN","M&M","ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","COALINDIA",
           "JSWSTEEL","GRASIM","CIPLA","DRREDDY","EICHERMOT"]'''

def sub(src, pairs, fname):
    for old, new, n in pairs:
        c = src.count(old)
        assert c == n, f"{fname}: expected {n} occurrence(s) of {old[:60]!r}, found {c}"
        src = src.replace(old, new)
    return src

def rev_audit(orig, gen, pairs, fname):
    back = gen
    for old, new, n in pairs:
        back = back.replace(new, old)
    ok = back == orig
    print(f"REVERSE-AUDIT {fname}: {'BYTE-IDENTICAL to original' if ok else 'MISMATCH!'}")
    return ok

def show_diff(orig, gen, fname):
    d = list(difflib.unified_diff(orig.splitlines(), gen.splitlines(), lineterm="", n=0))
    body = [x for x in d if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
    print(f"--- {fname}: {len(body)} changed lines")
    for x in body: print("   ", x)

ok_all = True

# ---- reentry_ext
orig = open(f"{T}/stocks_equity_reentry.py").read()
pairs = [
    ('BASE = "/home/hatch/workspace/trading/data/progressive"',
     'BASE = "/home/hatch/workspace/trading/data/progressive_ext"', 1),
    (OLD_SYMS, NEW_SYMS, 1),
    ("stock_event_calendar_jan_oct_2026.csv", "stock_event_calendar_ext_jan_oct_2026.csv", 1),
]
gen = sub(orig, pairs, "reentry_ext")
open(f"{T}/stocks_equity_reentry_ext.py", "w").write(gen)
show_diff(orig, gen, "stocks_equity_reentry_ext.py")
ok_all &= rev_audit(orig, gen, pairs, "reentry_ext")

# ---- round8_ext
orig = open(f"{T}/stocks_equity_round8.py").read()
pairs = [
    ('open(f"{BASE}/stocks_equity_reentry.py")', 'open(f"{BASE}/stocks_equity_reentry_ext.py")', 1),
    ('os.listdir(f"{BASE}/data/progressive")', 'os.listdir(f"{BASE}/data/progressive_ext")', 1),
    ('p = f"{BASE}/data/progressive/{sym}/spot_daily.csv"',
     'p = f"{BASE}/data/progressive_ext/{sym}/spot_daily.csv"', 1),
]
gen = sub(orig, pairs, "round8_ext")
open(f"{T}/stocks_equity_round8_ext.py", "w").write(gen)
show_diff(orig, gen, "stocks_equity_round8_ext.py")
ok_all &= rev_audit(orig, gen, pairs, "round8_ext")

# ---- profiles_ext
orig = open(f"{T}/stocks_reaction_profiles.py").read()
pairs = [
    ('BASE = "/home/hatch/workspace/trading/data/progressive"',
     'BASE = "/home/hatch/workspace/trading/data/progressive_ext"', 1),
    ('VBASE = "/home/hatch/workspace/trading/data/progressive_vol"',
     'VBASE = "/home/hatch/workspace/trading/data/progressive_vol_ext"', 1),
    (OLD_SYMS, NEW_SYMS, 1),
    ("stock_event_calendar_jan_oct_2026.csv", "stock_event_calendar_ext_jan_oct_2026.csv", 1),
    ("stock_reaction_profiles_", "universe_ext_reaction_profiles_", 4),
    ("stock_profiles_", "universe_ext_profiles_", 2),
]
gen = sub(orig, pairs, "profiles_ext")
open(f"{T}/stocks_reaction_profiles_ext.py", "w").write(gen)
show_diff(orig, gen, "stocks_reaction_profiles_ext.py")
ok_all &= rev_audit(orig, gen, pairs, "profiles_ext")

# ---- profiles_val (output prefixes only)
pairs_val = [
    ("stock_reaction_profiles_", "val_reaction_profiles_", 4),
    ("stock_profiles_", "val_profiles_", 2),
]
gen = sub(orig, pairs_val, "profiles_val")
open(f"{T}/stocks_reaction_profiles_val.py", "w").write(gen)
show_diff(orig, gen, "stocks_reaction_profiles_val.py")
ok_all &= rev_audit(orig, gen, pairs_val, "profiles_val")

print("ALL REVERSE AUDITS PASS:", ok_all)
sys.exit(0 if ok_all else 1)
