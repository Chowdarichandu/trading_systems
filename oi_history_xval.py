#!/usr/bin/env python3
"""OI HISTORY — cross-validation (2026-11-13).
(a) Chain archive overlap: this morning's archived front-expiry chains
    (option_chain_archive/*_2026-11-13.csv, pre-open bucket) embed
    ce_oi/pe_oi = Nov 12 close OI and ce_prev_oi/pe_prev_oi = Nov 11
    close OI per strike. Sum both over the dataset's Nov 11 / Nov 12
    ATM bands and compare against the reconstructed dataset rows.
(b) Raw 5-min premium stores: for sampled contract-days present both
    in oi_history/contracts/ (daily OI) and in a raw chain-build store
    (nifty_weekly_expiry_chain / btst_data / november_shadow_data),
    compare the store's last-bar OI (7th candle field) against the
    reconstructed daily OI for that date."""
import csv, json, random
from pathlib import Path

TR = Path.home() / "workspace/trading"
OI = TR / "oi_history"
out = []

# ---- (a) chain archive ----
arch = {}
for idx, tag in (("BANKNIFTY", "banknifty"), ("NIFTY", "nifty")):
    rows = list(csv.DictReader(open(TR / f"option_chain_archive/{tag}_2026-11-13.csv")))
    arch[idx] = {float(r["strike"]): r for r in rows}
ds = {}
for idx in arch:
    ds[idx] = {r["date"]: r for r in csv.DictReader(
        open(OI / f"{idx.lower()}_daily_oi.csv"))}
for idx in arch:
    step = 100 if idx == "BANKNIFTY" else 50
    for day, field in (("2026-11-11", "prev_oi"), ("2026-11-12", "oi")):
        row = ds[idx].get(day)
        if row is None:
            out.append(f"{idx} {day}: NO DATASET ROW")
            continue
        a = int(float(row["atm"]))
        band = [a + k * step for k in range(-5, 6)]
        ce = sum(float(arch[idx][float(s)][f"ce_{field}"]) for s in band
                 if float(s) in arch[idx])
        pe = sum(float(arch[idx][float(s)][f"pe_{field}"]) for s in band
                 if float(s) in arch[idx])
        out.append(f"{idx} {day} band@{a}: archive CE {ce:,.0f} vs dataset "
                   f"{float(row['ce_oi']):,.0f} (diff {ce - float(row['ce_oi']):+,.0f}) | "
                   f"archive PE {pe:,.0f} vs dataset {float(row['pe_oi']):,.0f} "
                   f"(diff {pe - float(row['pe_oi']):+,.0f}) | "
                   f"archive spot {arch[idx][float(a)]['spot']} vs dataset close "
                   f"{row['spot_close']}")

# ---- (b) raw 5-min stores, last-bar OI vs daily OI ----
random.seed(7)
checked = exact = 0
mism = []
contract_files = sorted((OI / "contracts").glob("*.json"))
sample = random.sample(contract_files, min(60, len(contract_files)))
for fn in sample:
    parts = fn.stem.split("_")
    idx, exp = parts[0], parts[1]
    strike = int(parts[2][:-2]); typ = parts[2][-2:]
    series = {r[0]: r[6] for r in json.loads(fn.read_text())}
    for folder in ("nifty_weekly_expiry_chain", "btst_data",
                   "november_shadow_data"):
        for day, oi in series.items():
            f2 = TR / folder / f"candles_{idx}_{strike}{typ}_{exp}_{day}.json"
            if f2.exists():
                body = json.loads(f2.read_text())
                cd = [c for c in ((body.get("data") or {}).get("candles")
                                  or []) if c[0][:10] == day]
                if cd and len(cd[-1]) > 6:
                    checked += 1
                    if float(cd[-1][6]) == oi:
                        exact += 1
                    else:
                        mism.append(f"{idx} {exp} {strike}{typ} {day}: "
                                    f"store {cd[-1][6]} vs daily {oi}")
                break
        else:
            continue
        break
out.append(f"5-min store check: {checked} contract-days sampled, "
           f"{exact} exact OI matches, {checked - exact} mismatches")
out += mism[:10]
print("\n".join(out))
(OI / "xval_report.txt").write_text("\n".join(out) + "\n")
