"""Compare the EI-NI EF v3.0 normalization references (NR_EF.xlsx, computed in the
workflow notebook) against the published global EF normalisation factors from
Sala et al. (2017), Table 4 (absolute global values for 2010)."""
import pandas as pd

# Sala et al. 2017, Table 4: "global NF for EF" (absolute, year 2010)
SALA = {
    "climate change":                      (5.79e13, "kg CO2 eq"),
    "ozone depletion":                     (1.61e08, "kg CFC-11 eq"),
    "human toxicity: carcinogenic":        (2.66e05, "CTUh"),
    "human toxicity: non-carcinogenic":    (3.27e06, "CTUh"),
    "particulate matter formation":        (4.95e06, "disease incidences"),
    "ionising radiation: human health":    (2.91e13, "kBq U-235 eq"),
    "photochemical ozone formation: human health": (2.80e11, "kg NMVOC eq"),
    "acidification":                       (3.83e11, "mol H+ eq"),
    "eutrophication: terrestrial":         (1.22e12, "mol N eq"),
    "eutrophication: freshwater":          (5.06e09, "kg P eq"),
    "eutrophication: marine":              (1.95e11, "kg N eq"),
    "land use":                            (9.64e15, "pt"),
    "ecotoxicity: freshwater":             (8.15e13, "CTUe"),
    "water use":                           (7.91e13, "m3 deprived"),
    "energy resources: non-renewable":     (4.50e14, "MJ"),
    "material resources: metals/minerals": (4.39e08, "kg Sb eq"),
}

p = r"C:\Users\nilst\OneDrive - Universiteit Leiden\Leiden\LCA\BW25\Normalization\NR_EF.xlsx"
df = pd.read_excel(p).rename(columns={"Unnamed: 0": "category", "Unnamed: 1": "unit"})
mine = df.set_index("category")

print(f"{'category':<44}{'EI-NI':>12}{'unit (BW)':>26}{'Sala2017':>11}{'unit':>21}{'diff %':>9}")
rows = []
for cat, (nf, unit_pub) in SALA.items():
    if cat not in mine.index:
        print(f"{cat:<44}{'NICHT IN NR_EF.xlsx':>12}")
        continue
    v = float(mine.loc[cat, "Global inventory"])
    u = str(mine.loc[cat, "unit"])
    d = (v - nf) / nf * 100
    rows.append({"category": cat, "EI_NI": v, "unit_bw": u,
                 "Sala2017": nf, "unit_pub": unit_pub, "diff_pct": d})
    print(f"{cat:<44}{v:>12.3e}{u:>26}{nf:>11.2e}{unit_pub:>21}{d:>+9.0f}")

out = pd.DataFrame(rows)
out.to_csv(r"C:\Users\nilst\lci-normalization\data\ef30_vs_sala2017.csv", index=False)
print("\nKategorien in NR_EF.xlsx, die hier nicht zugeordnet sind:")
print("  ", [c for c in mine.index if c not in SALA][:20])
