"""Figure: deviation of the EI-NI normalization references from the published
ReCiPe 2016 world normalization scores.

The EI-NI references are characterised with ReCiPe 2016 v1.03 midpoint (H); the
published reference is the official RIVM ReCiPe2016 v1.1 world normalization score
(Hierarchist, 2010), converted from a per-person to an absolute basis with the
world population of 6,895,889,018 stated in that workbook.

Two variants of the EI-NI are shown, differing only in whether ecoinvent
long-term emissions are included. The choice is immaterial for the non-toxic
categories and decisive for the toxicity-related ones, which is itself a result.

Two categories are excluded and reported in the caption instead:
  * ionising radiation - the Brightway implementation reports kg Co-60-Eq while
    the RIVM score is given in kBq Co-60 eq, so the two are not comparable as is;
  * mineral resource scarcity - the EI-NI covers only the subset of mineral
    extraction represented in ecoinvent, giving a difference of -100 % that
    reflects scope rather than a deviation in the same quantity.

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
DATA = ROOT / "data" / "recipe2016_vs_rivm.csv"
FIG_DIR = ROOT / "figures"

EXCLUDE = {"ionising radiation", "material resources: metals/minerals"}
TOXIC = {
    "human toxicity: carcinogenic", "human toxicity: non-carcinogenic",
    "ecotoxicity: freshwater", "ecotoxicity: marine", "ecotoxicity: terrestrial",
}
SHORT = {
    "photochemical oxidant formation: human health": "photochem. ozone form.: human health",
    "photochemical oxidant formation: terrestrial ecosystems": "photochem. ozone form.: terrestrial",
    "energy resources: non-renewable, fossil": "fossil resources",
}
C_NOLT, C_LT = "#1f4e79", "#c0392b"


def main() -> None:
    plt.style.use("ggplot")
    df = pd.read_csv(DATA)
    df = df[~df["category"].isin(EXCLUDE)]

    piv = df.pivot_table(index="category", columns="variant",
                         values="diff_pct", aggfunc="first")
    piv["toxic"] = [c in TOXIC for c in piv.index]
    # non-toxic first, each block sorted by the no-LT deviation
    piv = piv.sort_values(["toxic", "no LT"])

    labels = [SHORT.get(c, c) for c in piv.index]
    y = np.arange(len(piv))
    h = 0.38

    fig, ax = plt.subplots(figsize=(9.6, 6.4))
    ax.barh(y + h / 2, piv["no LT"], height=h, color=C_NOLT,
            label="EI-NI, long-term emissions excluded")
    ax.barh(y - h / 2, piv["with LT"], height=h, color=C_LT,
            label="EI-NI, long-term emissions included")

    ax.axvline(0, color="0.3", lw=1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlim(-200, 20000)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xlabel("Deviation of the EI-NI reference from the published "
                  "ReCiPe 2016 world score  [%]", fontsize=10)
    ax.tick_params(axis="x", labelsize=9)

    # separate the toxicity block
    split = int((~piv["toxic"]).sum())
    ax.axhline(split - 0.5, color="0.45", ls="--", lw=1.0)
    ax.text(0.015, len(piv) - 0.35, "toxicity-related categories",
            transform=ax.get_yaxis_transform(), fontsize=9,
            color="0.35", ha="left", va="center", style="italic")

    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.grid(True, axis="x", ls=":", alpha=0.6)
    fig.tight_layout()

    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"lcia_comparison.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(piv.round(0).to_string())
    print(f"\nFigure written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
