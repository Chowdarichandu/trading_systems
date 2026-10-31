import csv, json
from collections import defaultdict

def load(p): return list(csv.DictReader(open(p)))
T='/home/hatch/workspace/trading/'
out=[]
def add_leg(key, system, entry_time, exit_reason, net, full_target, net_unit, entry_val='', exit_val='', strike='', expiry='', exit_time=''):
    out.append(dict(date=key[0], index=key[1], direction=key[2], system=system,
        entry_time=entry_time, exit_reason=exit_reason, net=float(net),
        full_target=(full_target in (True,'True','1',1,'target')),
        net_unit=net_unit, entry_val=entry_val, exit_val=exit_val, strike=strike, expiry=expiry, exit_time=exit_time))

# --- Jan-Sep spot provisional ---
for r in load(T+'index_options_o1_janoct_trades.csv'):
    if r['date']>='2026-10-01': continue
    if r['track'] not in ('(lA) v2','V5-v2'): continue
    sysname='(lA) v2' if r['track']=='(lA) v2' else 'V5 v2'
    add_leg((r['date'],r['index'],r['direction']), sysname, r['entry_time'], r['exit_reason'], r['net_rs'], r['full_target'], 'spot_provisional')
for r in load(T+'index_options_U1_skillV3_jansep_spot.csv'):
    add_leg((r['date'],r['index'],r['direction']), 'Skill V3', r['entry_time'], r['exit_reason'], r['spot_net_rs'], r['full_target'], 'spot_provisional', entry_val=r['entry_spot'], exit_val=r['exit_spot'], exit_time=r['exit_time'])
for r in load(T+'index_options_U1_volrixB_jansep_spot.csv'):
    add_leg((r['entry_date'],r['index'],r['direction']), 'Volrix (b)', r['entry_time'], r['exit_reason'], r['spot_net_rs'], r['full_target'], 'spot_provisional', entry_val=r['entry_spot'], exit_val=r['exit_spot'], exit_time=r['exit_time'])

# --- October premium ---
for r in load(T+'index_options_premium_october_trades.csv'):
    if r['premium_status']!='COMPUTED': continue
    ver=r['version']
    if ver.startswith('(lA)'): sysname='(lA) v2'
    elif ver.startswith('V5'): sysname='V5 v2'
    else: continue  # Skill base rows excluded: same system as V3
    add_leg((r['date'],r['index'],r['direction']), sysname, r['entry_time'], r['exit_reason'], r['premium_net'], (r['exit_reason']=='target'), 'premium_per_1_lot', entry_val=r['entry_premium'], exit_val=r['exit_premium'], strike=r['strike'], expiry=r['expiry'], exit_time=r['exit_time'])
for r in load(T+'index_options_skill_tuned_oct30_trades.csv'):
    if r['variant']!='V3' or r['premium_status']!='COMPUTED': continue
    add_leg((r['date'],r['index'],r['direction']), 'Skill V3', r['entry_time'], r['exit_reason'], r['premium_net'], (r['exit_reason']=='target'), 'premium_per_1_lot', entry_val=r['entry_premium'], exit_val=r['exit_premium'], strike=r['strike'], expiry=r['expiry'], exit_time=r['exit_time'])
# Volrix (b) Oct premium, from volrix_tuned report §3 (both target)
add_leg(('2026-10-09','NIFTY','CE'), 'Volrix (b)', '09:20', 'target', 5630, True, 'premium_per_1_lot', entry_val='398.00', exit_val='488.00', strike='22200', expiry='2026-10-27', exit_time='09:45')
add_leg(('2026-10-26','BANKNIFTY','CE'), 'Volrix (b)', '09:20', 'target', 2480, True, 'premium_per_1_lot', entry_val='238.55', exit_val='328.55', strike='54300', expiry='2026-10-27', exit_time='09:55')

# unique-once: earliest entry_time per key
groups=defaultdict(list)
for l in out: groups[(l['date'],l['index'],l['direction'])].append(l)
rows=[]
for k, legs in groups.items():
    legs_sorted=sorted(legs, key=lambda x: x['entry_time'])
    rep=legs_sorted[0]
    rows.append(dict(date=k[0], index=k[1], direction=k[2],
        source_systems=';'.join(sorted(set(x['system'] for x in legs))),
        representative_system=rep['system'], entry_time=rep['entry_time'],
        entry_value=rep['entry_val'], strike=rep['strike'], expiry=rep['expiry'],
        exit_time=rep['exit_time'], exit_value=rep['exit_val'], exit_reason=rep['exit_reason'],
        net_rs=rep['net'], net_unit=rep['net_unit'], full_target=int(rep['full_target']),
        n_systems=len(set(x['system'] for x in legs))))
rows.sort(key=lambda r: (r['date'], r['index'], r['direction']))
with open(T+'index_options_U1_janoct_trades.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def summ(rs, label):
    for idx in ['NIFTY','BANKNIFTY']:
        s=[r for r in rs if r['index']==idx]
        print(f"{label} {idx}: {len(s)} trades net {sum(r['net_rs'] for r in s):.2f} FT {sum(r['full_target'] for r in s)} ({sum(r['full_target'] for r in s)/len(s)*100:.1f}%)" if s else f"{label} {idx}: 0")
    print(f"{label} TOTAL: {len(rs)} net {sum(r['net_rs'] for r in rs):.2f}")
summ([r for r in rows if r['date']>='2026-10-01'], "OCT premium check (expect NIFTY 16 +14169.75, BANK 18 +11040, total 34 +25209.75)")
summ([r for r in rows if r['date']<'2026-10-01'], "JAN-SEP spot")
summ(rows, "JAN-OCT mixed")
# monthly
for idx in ['NIFTY','BANKNIFTY']:
    print(f"-- {idx} monthly (month net, cumulative mixed) --")
    cum=0
    for m in range(1,11):
        s=[r for r in rows if r['index']==idx and int(r['date'][5:7])==m]
        net=sum(r['net_rs'] for r in s); cum+=net
        print(f"  {m:02d}: {len(s)} trades net {net:.2f} cum {cum:.2f} FT {sum(r['full_target'] for r in s)}")
print("legs fed:", len(out), "unique rows:", len(rows), "duplicate legs removed:", len(out)-len(rows))
