import pandas as pd, math, os, sys
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from timing_sweep import load, day_data
spot, daily = load()
def explore(ds, mode="v4"):
    dd = day_data(spot, daily, ds)
    if not dd: print(ds, "no data"); return
    day_spot, pdh, pdc, pdl, bias, scale = dd
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    def qualifies(c):
        close=float(c["close"])
        if not (close < orl and close < pdl): return False
        if mode=="skill": return True
        nxt=[l for l in levels if l < close]; room=(close-max(nxt)) if nxt else math.inf
        return (orh-orl) <= 360*scale and room >= 200*scale
    first=None
    for i,c in enumerate(candles.itertuples()):
        if c.time>"11:30": break
        if qualifies(candles.iloc[i]): first=i; break
    if first is None: print(ds, "no first signal"); return
    bounce=None
    for j in range(first+1, len(candles)):
        if float(candles.iloc[j]["close"]) >= orl: bounce=j; break
    second=None
    if bounce is not None:
        for j in range(bounce+1, len(candles)):
            if qualifies(candles.iloc[j]): second=j; break
    def fmt(idx):
        return f"{candles.iloc[idx]['time']} close={candles.iloc[idx]['close']:.2f}" if idx is not None else "None"
    print(f"{ds} mode={mode} OR {orl}-{orh} PDL {pdl} first={fmt(first)} bounce={fmt(bounce)} second={fmt(second)} second_le1130={second is not None and candles.iloc[second]['time']<='11:30'}")
cluster1=["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
modes={"2026-04-02":"skill"}
print("== Cluster1 ==")
for ds in cluster1: explore(ds, modes.get(ds,"v4"))
print("== Winning PE ==")
win_days={"2026-01-21":9280,"2026-02-24":7350,"2026-03-16":8940,"2026-03-13":5400,"2026-03-23":7260,"2026-04-24":8820,"2026-05-05":5040,"2026-07-22":6320,"2026-08-12":6250,"2026-08-27":3000,"2026-09-29":3790,"2026-09-07":2990,"2026-10-08":5440,"2026-10-23":11390}
win_modes={"2026-03-23":"skill"}
for ds in win_days: explore(ds, win_modes.get(ds,"v4"))
print("== Cluster3 ==")
for ds in ["2026-02-13","2026-04-30","2026-05-18"]: explore(ds,"v4")
print("== Cluster2 (CE, for context - PE scan not applicable) ==")
for ds in ["2026-01-14","2026-10-26"]: explore(ds,"v4")
