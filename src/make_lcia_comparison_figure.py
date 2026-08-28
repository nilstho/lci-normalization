"""Figure: deviation of the EI-NI normalization references from the published
global normalisation factors of two LCIA methods.

  * EF v3.0     -> Sala et al. (2017), Table 4, global NF for EF, year 2010
  * ReCiPe 2016 -> RIVM ReCiPe2016 v1.1 world normalization scores (Hierarchist,
                   2010), converted from per-person to absolute with the world
                   population of 6,895,889,018 stated in that workbook

Both published references use the same population basis, so the two series are
directly comparable. The ReCiPe series uses the variant without ecoinvent
long-term emissions, since the published factors represent actual annual
emissions rather than long-term releases.

Categories are omitted per method where the two sides are not the same quantity:
  * EF: land use (dimensionless vs pt) and freshwater eutrophication
    (kg PO4-eq vs kg P eq)
  * ReCiPe: ionising radiation (kg Co-60-Eq vs kBq Co-60 eq) and mineral
    resource scarcity (EI-NI covers only the mineral extraction represented in
    ecoinvent)

Usage: python src/make_lcia_comparison_figure.py
Outputs: figures/lcia_comparison.{png,pdf}
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "figures"

# display name -> (EF v3.0 category, ReCiPe 2016 category); None = not comparable
MAP = {
    "climate change":            ("climate change", "climate change"),
    "ozone depletion":           ("ozone depletion", "ozone depletion"),
    "acidification":             ("acidification", "acidification: terrestrial"),
    "particulate matter form.":  ("particulate matter formation", "particulate matter formation"),
    "photochem. ozone form.":    ("photochemical ozone formation: human health",
                                  "photochemical oxidant formation: human health"),
    "eutrophication: terrestrial": ("eutrophication: terrestrial", None),
    "eutrophication: freshwater": (None, "eutrophication: freshwater"),
    "eutrophication: marine":    ("eutrophication: marine", "eutrophication: marine"),
    "land use":                  (None, "land use"),
    "water use":                 ("water use", "water use"),
    "fossil resources":          ("energy resources: non-renewable",
                                  "energy resources: non-renewable, fossil"),
    "human toxicity: carcinog.": ("human toxicity: carcinogenic", "human toxicity: carcinogenic"),
    "human toxicity: non-carc.": ("human toxicity: non-carcinogenic",
                                  "human toxicity: non-carcinogenic"),
    "ecotoxicity: freshwater":   ("ecotoxicity: freshwater", "ecotoxicity: freshwater"),
    "ecotoxicity: marine":       (None, "ecotoxicity: marine"),
    "ecotoxicity: terrestrial":  (None, "ecotoxicity: terrestrial"),
}
TOXIC = {"human toxicity: carcinog.", "human toxicity: non-carc.",
         "ecotoxicity: freshwater", "ecotoxicity: marine", "ecotoxicity: terrestrial"}
C_EF, C_RC = "#1f4e79", "#c0392b"


def main() -> None:
    plt.style.use("ggplot")
    ef = pd.read_csv(ROOT / "data" / "ef30_vs_sala2017.csv").set_index("category")
    rc = pd.read_csv(ROOT / "data" / "recipe2016_vs_rivm.csv")
    rc = rc[rc.variant == "no LT"].set_index("category")

    rows = []
    for name, (c_ef, c_rc) in MAP.items():
        rows.append({
            "name": name,
            "EF": float(ef.loc[c_ef, "diff_pct"]) if c_ef in ef.index else np.nan,
            "ReCiPe": float(rc.loc[c_rc, "diff_pct"]) if c_rc in rc.index else np.nan,
            "toxic": name in TOXIC,
        })
    d = pd.DataFrame(rows)
    d["sort"] = d[["EF", "ReCiPe"]].mean(axis=1)
    d = d.sort_values(["toxic", "sort"]).reset_index(drop=True)

    y = np.arange(len(d))
    h = 0.38
    fig, ax = plt.subplots(figsize=(9.8, 6.6))
    ax.barh(y + h / 2, d["EF"].fillna(0), height=h, color=C_EF,
            label="EF v3.0  vs  Sala et al. (2017)")
    ax.barh(y - h / 2, d["ReCiPe"].fillna(0), height=h, color=C_RC,
            label="ReCiPe 2016 (H)  vs  RIVM world scores")
    for i, r in d.iterrows():          # mark the non-comparable combinations
        for val, off in ((r["EF"], h / 2), (r["ReCiPe"], -h / 2)):
            if np.isnan(val):
                ax.text(0.6, i + off, "n/a", va="center", ha="left",
                        fontsize=7.5, color="0.5", style="italic")

    ax.axvline(0, color="0.3", lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(d["name"], fontsize=9)
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlim(-200, 5000)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xlabel("Deviation of the EI-NI reference from the published "
                  "normalisation factor  [%]", fontsize=10)
    ax.tick_params(axis="x", labelsize=9)

    split = int((~d["toxic"]).sum())
    ax.axhline(split - 0.5, color="0.45", ls="--", lw=1.0)
    ax.text(0.015, len(d) - 0.35, "toxicity-related categories",
            transform=ax.get_yaxis_transform(), fontsize=9,
            color="0.35", ha="left", va="center", style="italic")

    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.grid(True, axis="x", ls=":", alpha=0.6)
    fig.tight_layout()

    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"lcia_comparison.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(d[["name", "EF", "ReCiPe", "toxic"]].round(0).to_string(index=False))
    print(f"\nFigure written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
