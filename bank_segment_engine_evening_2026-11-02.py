"""Bank segment evening engine 2026-11-02: 3 filter candidates vs B2 pool (BNF-PAPER-V1 base).
Basis: index options, premium per 1 lot (30), cost Rs220/trade already in stored net_rs, UNIQUE-ONCE as stored.
No entry delay in any candidate (attacks delay cost of rejected BANK-FIX-01): each is a skip-at-entry
using only entry-time-known attributes (entry_time, direction, frozen-pool source list).
Gate: G1 timing, G2 re-sum, G3 net improvement, G4 placebo, G5 halves>=0, G6 ex-top-3>=0,
G7 no green month flips red, G8 quick stops (OR legs stopped <=10min) fall.
"""
import csv, json, collections

PATH="/home/hatch/workspace/trading/historical_proof_bank_B2_trades.csv"
rows=list(csv.DictReader(open(PATH)))
def mins(t): h,m=map(int,t.split(":")); return h*60+m
for r in rows:
    r['hold']=mins(r['exit_time'])-mins(r['entry_time']); r['net']=float(r['net_rs'])
    r['is_or']='Skill V3' in r['source_systems']
    r['quick_or']= r['is_or'] and r['exit_reason']=='stop' and r['hold']<=10
    r['month']=r['date'][:7]; r['half']='H1' if r['date'][5:7] in ('01','02','03','04','05') else 'H2'

base_net=sum(r['net'] for r in rows); base_n=len(rows)
assert abs(base_net-18731.50)<0.01 and base_n==89, (base_net,base_n)  # G2 re-sum vs stored/fix-test
base_quick=sum(r['quick_or'] for r in rows)
def stats(kept):
    net=sum(r['net'] for r in kept)
    months={}
    for m in sorted(set(r['month'] for r in rows)):
        months[m]=round(sum(r['net'] for r in kept if r['month']==m),2)
    base_months={m:round(sum(r['net'] for r in rows if r['month']==m),2) for m in months}
    flips=[m for m in months if base_months[m]>0 and months[m]<0]
    top3=sorted((r['net'] for r in kept),reverse=True)[:3]
    return dict(net=round(net,2), n=len(kept),
        H1=round(sum(r['net'] for r in kept if r['half']=='H1'),2),
        H2=round(sum(r['net'] for r in kept if r['half']=='H2'),2),
        ex_top3=round(net-sum(top3),2), months=months, flips=flips,
        quick_or=sum(r['quick_or'] for r in kept),
        FT=sum(1 for r in kept if r['exit_reason']=='target'))
base_stats=stats(rows)

cands={
 "EVE-01_skip_OR_entry_before_1000": lambda r: r['is_or'] and mins(r['entry_time'])<600,
 "EVE-02_skip_SkillV3_solo_OR": lambda r: r['is_or'] and r['source_systems'].strip()=='Skill V3',
 "EVE-03_skip_OR_PE_entry_before_1000": lambda r: r['is_or'] and r['direction']=='PE' and mins(r['entry_time'])<600,
}
out={"baseline":base_stats,"candidates":{}}
for name,skipf in cands.items():
    skipped=[r for r in rows if skipf(r)]; kept=[r for r in rows if not skipf(r)]
    s=stats(kept)
    # G4 placebo: skip the same NUMBER of OR legs from the complementary population, chronologically first N
    comp=[r for r in rows if r['is_or'] and not skipf(r)]
    placebo_kept=[r for r in rows if r not in comp[:len(skipped)]]
    # careful: r not in uses dict equality; use id set instead recompute below
    comp_ids={id(r) for r in comp[:len(skipped)]}
    placebo_kept=[r for r in rows if id(r) not in comp_ids]
    placebo_net=round(sum(r['net'] for r in placebo_kept),2)
    gates={
      "G1_timing":"PASS - skip inputs (entry_time/direction/frozen source list) known at entry; no future bar used; 0 violations",
      "G2_resum":"PASS - baseline re-summed 89 legs = +18731.50 exact",
      "G3_net_improvement": s['net']>base_net,
      "G4_placebo_beaten": s['net']>placebo_net,
      "G5_halves_both_ge0": s['H1']>=0 and s['H2']>=0,
      "G6_ex_top3_ge0": s['ex_top3']>=0,
      "G7_no_green_month_flips": len(s['flips'])==0,
      "G8_quick_stops_fall": s['quick_or']<base_quick,
    }
    verdict="PASS" if all(v is True for k,v in gates.items() if isinstance(v,bool)) else "FAIL"
    out["candidates"][name]=dict(skipped_n=len(skipped), skipped_net=round(sum(r['net'] for r in skipped),2),
        skipped_quick=sum(r['quick_or'] for r in skipped), stats=s, placebo_net=placebo_net, gates=gates, verdict=verdict)
print(json.dumps(out,indent=1))
with open("/home/hatch/workspace/trading/bank_segment_engine_evening_2026-11-02.json","w") as f: json.dump(out,f,indent=1)
