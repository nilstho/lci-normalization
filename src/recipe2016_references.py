"""Final ReCiPe 2016 v1.03 midpoint (H) normalization references for the EI-NI,
computed for both the full inventory and the negative-free variant."""
import warnings
import pandas as pd
import bw2data as bd

warnings.filterwarnings("ignore")

bd.projects.set_current("Normalization")
db = bd.Database("Normalization")
inv = {}
for code in ("norm", "norm_without_negative"):
    d = {}
    for e in db.get(code).biosphere():
        d[e.input["code"]] = d.get(e.input["code"], 0.0) + e["amount"]
    inv[code] = d

bd.projects.set_current("unc")
rows = []
for fam, tag in [("ReCiPe 2016 v1.03, midpoint (H)", "with LT"),
                 ("ReCiPe 2016 v1.03, midpoint (H) no LT", "no LT")]:
    for m in sorted(m for m in bd.methods if m[0] == fam):
        cfs = {}
        for k, v in bd.Method(m).load():
            c = k[1] if isinstance(k, (tuple, list)) else k
            cfs[c] = cfs.get(c, 0.0) + v
        s_full = sum(inv["norm"].get(c, 0.0) * v for c, v in cfs.items())
        s_pos = sum(inv["norm_without_negative"].get(c, 0.0) * v for c, v in cfs.items())
        n_char = sum(1 for c in inv["norm"] if c in cfs)
        rows.append({
            "variant": tag,
            "category": m[1].replace(" no LT", ""),
            "unit": bd.methods[m]["unit"],
            "NR_full": s_full,
            "NR_without_negative": s_pos,
            "flows_characterised": n_char,
        })

df = pd.DataFrame(rows)
piv = df.pivot_table(index=["category", "unit"], columns="variant",
                     values="NR_full", aggfunc="first").reset_index()
piv["ratio_LT"] = piv["with LT"] / piv["no LT"]

print("ReCiPe 2016 v1.03 midpoint (H) - normalization references for the EI-NI\n")
print(f"{'category':<44}{'no LT':>13}{'with LT':>13}{'ratio':>8}  unit")
for _, r in piv.iterrows():
    print(f"{r.category:<44}{r['no LT']:>13.4e}{r['with LT']:>13.4e}"
          f"{r.ratio_LT:>8.2f}  {r.unit}")

out = r"C:\Users\nilst\lci-normalization\data\normalization_references_recipe2016.csv"
df.to_csv(out, index=False)
print("\nwrote", out)
