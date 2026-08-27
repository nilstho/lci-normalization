"""Compute EDGAR global anthropogenic totals for a target year from the
official 'TOTALS BY COUNTRY' sheets. Unit in the files is Gg (= 1e6 kg)."""
import glob, os
import pandas as pd

YEAR = "Y_2018"
GG_TO_KG = 1e6
FILES = {
    "CO2 (fossil)": "IEA_EDGAR_CO2_1970_2022.xlsx",
    "CH4":          "EDGAR_CH4_1970_2022.xlsx",
    "N2O":          "EDGAR_N2O_1970_2022.xlsx",
    "CO":           "EDGAR_CO_1970_2022.xlsx",
    "NOx":          "EDGAR_NOx_1970_2022.xlsx",
    "SO2":          "EDGAR_SO2_1970_2022.xlsx",
    "NH3":          "EDGAR_NH3_1970_2022.xlsx",
    "NMVOC":        "EDGAR_NMVOC_1970_2022.xlsx",
    "PM2.5":        "EDGAR_PM2.5_1970_2022.xlsx",
}
base = r"C:\Users\nilst\AppData\Local\Temp\edgar"

print(f"{'species':<14}{'rows':>6}{'Gg':>16}{'kg/yr':>14}   sanity")
results = {}
for label, fn in FILES.items():
    path = os.path.join(base, fn)
    df = pd.read_excel(path, sheet_name="TOTALS BY COUNTRY", skiprows=9)
    # guard against aggregate rows that would double-count
    names = df["Name"].astype(str).str.strip().str.lower()
    bad = df[names.isin(["world", "total", "global"])]
    total_gg = pd.to_numeric(df[YEAR], errors="coerce").sum()
    results[label] = total_gg * GG_TO_KG
    print(f"{label:<14}{len(df):>6}{total_gg:>16,.0f}{total_gg*GG_TO_KG:>14.3e}   "
          f"aggregate-rows={len(bad)}")

print("\n--- unique 'Substance' values (should be one per file) ---")
for label, fn in FILES.items():
    df = pd.read_excel(os.path.join(base, fn), sheet_name="TOTALS BY COUNTRY", skiprows=9)
    print(f"  {label:<14}{df['Substance'].unique()[:3]}")

pd.Series(results).to_csv(os.path.join(base, "edgar_2018_totals_kg.csv"), header=["kg_per_year"])
print("\nsaved edgar_2018_totals_kg.csv")
