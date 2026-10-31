"""Driver for one progressive month: aggregate progressive_engine per symbol.
Paper only, no orders. Appends a section to progressive_jan2025_oct2026_progress.md.
Usage: python3 progressive_month.py YEAR MONTH
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from progressive_engine import run_month, metrics

SYMBOLS = ["NIFTY","BANKNIFTY","GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY","NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO","NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL","ASTRAL","BDL","OIL","HINDUNILVR"]
PROG = "/home/hatch/workspace/trading/progressive_jan2025_oct2026_progress.md"

def main():
    year, month = int(sys.argv[1]), int(sys.argv[2])
    all_v, all_s, per = [], [], []
    ndays = None
    for sym in SYMBOLS:
        nd, v, s = run_month(sym, year, month)
        if ndays is None: ndays = nd
        elif nd != ndays: print(f"WARN days differ {sym} {nd} vs {ndays}")
        all_v += v; all_s += s
        mv, ms = metrics(nd, v), metrics(nd, s)
        per.append(f"{sym} {mv['trades']} / {mv['win_rate_pct']}% / {mv['net_rs']:+.0f} | {ms['trades']} / {ms['win_rate_pct']}% / {ms['net_rs']:+.0f}")
        print(f"{sym}: V4 {mv} | SKILL {ms}", flush=True)
    mv, ms = metrics(ndays, all_v), metrics(ndays, all_s)
    idx_v = [t for t in all_v if t['symbol'] in ("NIFTY","BANKNIFTY")]
    idx_s = [t for t in all_s if t['symbol'] in ("NIFTY","BANKNIFTY")]
    stk_v = [t for t in all_v if t['symbol'] not in ("NIFTY","BANKNIFTY")]
    stk_s = [t for t in all_s if t['symbol'] not in ("NIFTY","BANKNIFTY")]
    def net(ts): return round(sum(t['net_rs'] for t in ts),2)
    def split(ts):
        # per-index breakdown
        out=[]
        for sym in ("NIFTY","BANKNIFTY"):
            sub=[t for t in ts if t['symbol']==sym]
            out.append(f"{sym} {net(sub):+.0f}")
        return ", ".join(out)
    # cumulative: parse previous cumulative from progress file if present in last DONE section? Instead caller computes from run file; here just report month + split.
    section = f"""
### {year}-{month:02d} — DONE, all 27 instruments, {ndays} counted trading days
- V4 (cash): {mv['trades']} trades, {mv['targets']} targets, {mv['stops']} stops, {mv['square_offs']} square-offs, win {mv['win_rate_pct']}%, net ₹{mv['net_rs']:+,.0f} combined; indices ₹{net(idx_v):+,.0f} ({split(idx_v)}), stocks ₹{net(stk_v):+,.0f}.
- Day Trader skill (cash): {ms['trades']} trades, {ms['targets']} targets, {ms['stops']} stops, {ms['square_offs']} square-offs, win {ms['win_rate_pct']}%, net ₹{ms['net_rs']:+,.0f} combined; indices ₹{net(idx_s):+,.0f} ({split(idx_s)}), stocks ₹{net(stk_s):+,.0f}.
- Portfolio trades/week (raw, NO cap): V4 {mv['trades_per_week']}/week, Skill {ms['trades_per_week']}/week.
- X verdict so far: STILL FAILS frequency for both raw runs (see cumulative below). No V5/skill v2 adoption yet unless cumulative validation shows progression on net + win rate + frequency together.
- Detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): {'; '.join(per)}.
"""
    print(section)
    # Save machine-readable month summary for cumulative computation
    out = {"year":year,"month":month,"days":ndays,"v4":mv,"skill":ms,
           "v4_indices_net":net(idx_v),"v4_stocks_net":net(stk_v),
           "skill_indices_net":net(idx_s),"skill_stocks_net":net(stk_s),
           "per":per, "v4_trades":all_v, "skill_trades":all_s}
    with open(f"/home/hatch/workspace/trading/data/progressive/summary_{year}-{month:02d}.json","w") as f:
        json.dump(out, f, indent=2, default=str)
    # Append section, replacing NEXT marker if present, else append at end
    txt = open(PROG).read()
    marker = f"### NEXT: {year}-{month:02d} — not yet run"
    if marker in txt:
        txt = txt.replace(marker, section.strip())
        # add next month marker
        ny, nm = (year, month+1) if month<12 else (year+1,1)
        txt = txt.rstrip() + f"\n\n### NEXT: {ny}-{nm:02d} — not yet run\n"
    else:
        txt = txt.rstrip() + "\n" + section
    open(PROG,"w").write(txt)
    print("APPENDED to progress file")

if __name__ == "__main__":
    main()
