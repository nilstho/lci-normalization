"""Compare the EI-NI ReCiPe 2016 normalization references against the official
RIVM ReCiPe 2016 world normalization scores (Hierarchist, 2010)."""
import pandas as pd

POP = 6_895_889_018  # world population 2010, as stated in the RIVM workbook

# RIVM ReCiPe2016 v1.1 world normalization scores, Hierarchic, per person in 2010
RIVM = {
    "climate change": 7990.407652952963,
    "ozone depletion": 0.06001000496224004,
    "ionising radiation": 479.91735010391716,          # unit: kBq Co-60 eq (see note)
    "particulate matter formation": 25.569594920658865,
    "photochemical oxidant formation: human health": 20.567456694737732,
    "human toxicity: carcinogenic": 10.298306455189207,
    "human toxicity: non-carcinogenic": 31251.84225773112,
    "water use": 266.6392611088278,
    "photochemical oxidant formation: terrestrial ecosystems": 17.74932822136718,
    "acidification: terrestrial": 40.98051474233814,
    "ecotoxicity: terrestrial": 15200.310658799526,
    "land use": 6167.48227895003,
    "eutrophication: freshwater": 0.6498883618957024,
    "ecotoxicity: freshwater": 25.174703491092206,
    "ecotoxicity: marine": 43.44284202537615,
    "eutrophication: marine": 4.617785567879548,
    "material resources: metals/minerals": 120051.20954550793,
    # fossil resource scarcity is split by carrier in the workbook; summed here
    "energy resources: non-renewable, fossil": 569.9047635107981 + 0.4019786270870057
                                              + 381.5142606171218 + 31.456422722840287,
}

df = pd.read_csv(r"C:\Users\nilst\lci-normalization\data\normalization_references_recipe2016.csv")
rows = []
for variant in ("no LT", "with LT"):
    sub = df[df.variant == variant].set_index("category")
    for cat, nf in RIVM.items():
        if cat not in sub.index:
            continue
        mine = float(sub.loc[cat, "NR_full"])
        pub = nf * POP
        rows.append({"variant": variant, "category": cat,
                     "unit": sub.loc[cat, "unit"],
                     "EI_NI": mine, "RIVM_world": pub,
                     "diff_pct": (mine - pub) / pub * 100})

out = pd.DataFrame(rows)
for variant in ("no LT", "with LT"):
    s = out[out.variant == variant]
    print(f"=== ReCiPe 2016 (H), {variant} — EI-NI vs RIVM world 2010 ===")
    print(f"{'category':<52}{'EI-NI':>12}{'RIVM':>12}{'diff %':>10}")
    for _, r in s.iterrows():
        print(f"{r.category:<52}{r.EI_NI:>12.3e}{r.RIVM_world:>12.3e}{r.diff_pct:>+10.0f}")
    print()

out.to_csv(r"C:\Users\nilst\lci-normalization\data\recipe2016_vs_rivm.csv", index=False)
print("wrote data/recipe2016_vs_rivm.csv")
