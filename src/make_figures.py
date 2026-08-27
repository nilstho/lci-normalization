"""Regenerate the ecoinvent-vs-EDGAR validation figures (manuscript Figures 2 and 3).

The figures compare the ecoinvent-derived normalization inventory (this study)
against the public EDGAR global emission inventory for reference year 2018,
chosen to match the reference period of ecoinvent 3.8 (~2017-2018):

  * greenhouse gases and F-gases  -> EDGAR Community GHG database v8.0 (2023)
  * air pollutants                -> EDGAR v8.1 (release August 2024)

Both are plotted on log-log axes against a 1:1 reference line.

This script is intentionally decoupled from the heavy LCI pipeline: it reads the
pre-aggregated global totals from ``data/figure_data.csv`` and needs only pandas
and matplotlib, so the figures can be regenerated without an ecoinvent licence or
a Brightway installation. The ecoinvent totals in that CSV come from the main
workflow notebook; the EDGAR totals are reproduced by ``edgar_global_totals.py``.

Species flagged ``in_figure = no`` are essentially absent from ecoinvent (zero or
near-zero) and cannot be placed on logarithmic axes; they are named in the figure
instead.

Usage
-----
    python src/make_figures.py

Outputs (in ``figures/``): ``ei_vs_EDGAR_ghg`` and ``ei_vs_EDGAR_ap``,
each as PNG (300 dpi) and PDF (vector).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "figure_data.csv"
FIG_DIR = ROOT / "figures"

ONE_TO_ONE_COLOUR = "0.5"
STYLE = {  # classification -> (colour, marker, legend label)
    "GHG":           ("#c0392b", "o", "Greenhouse gases"),
    "F-gas":         ("#1f4e79", "^", "F-gases"),
    "Air pollutant": ("#c0392b", "o", "Air pollutants"),
}
# manual nudges (points) where the default offset would overlap a neighbour
LABEL_OFFSET = {
    "HFC-23": (-46, 6), "SF6": (10, -4), "CF4": (8, -12),
    "CO": (7, -12), "PM2.5": (7, -12),
}
DEFAULT_OFFSET = (6, 5)


def load_data() -> pd.DataFrame:
    """Load the figure data and add the relative deviation column."""
    df = pd.read_csv(DATA_FILE)
    df["deviation_pct"] = (df["ecoinvent_kg"] - df["edgar_kg"]) / df["edgar_kg"] * 100.0
    return df


def scatter_loglog(subset: pd.DataFrame, stem: str, title: str,
                   missing: list[str] | None = None) -> None:
    """Save a log-log ecoinvent-vs-EDGAR scatter with a 1:1 line and point labels."""
    plotted = subset[subset["in_figure"] == "yes"]
    x = np.log10(plotted["ecoinvent_kg"].to_numpy())
    y = np.log10(plotted["edgar_kg"].to_numpy())
    lo = min(x.min(), y.min()) - 0.8
    hi = max(x.max(), y.max()) + 0.8

    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.plot([lo, hi], [lo, hi], "--", color=ONE_TO_ONE_COLOUR, lw=1.0, label="1:1 (y = x)")

    for cls, grp in plotted.groupby("classification", sort=False):
        colour, marker, legend = STYLE[cls]
        gx = np.log10(grp["ecoinvent_kg"].to_numpy())
        gy = np.log10(grp["edgar_kg"].to_numpy())
        ax.scatter(gx, gy, s=48, color=colour, marker=marker, zorder=3,
                   label=legend if plotted["classification"].nunique() > 1 else None)
        for xi, yi, label, sub in zip(gx, gy, grp["label"], grp["substance"]):
            ax.annotate(label, (xi, yi), textcoords="offset points",
                        xytext=LABEL_OFFSET.get(sub, DEFAULT_OFFSET), fontsize=9.5)

    if missing:
        ax.text(0.03, 0.03,
                "Absent from ecoinvent:\n" + ", ".join(missing),
                transform=ax.transAxes, fontsize=8.5, color="0.35",
                va="bottom", ha="left")

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel(r"ecoinvent normalization inventory  [log$_{10}$ kg yr$^{-1}$]")
    ax.set_ylabel(r"EDGAR reference, 2018  [log$_{10}$ kg yr$^{-1}$]")
    ax.set_title(title)
    ax.grid(True, ls=":", alpha=0.6)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()

    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    plt.style.use("ggplot")
    df = load_data()

    ghg = df[df["classification"].isin(["GHG", "F-gas"])]
    absent = ghg.loc[ghg["in_figure"] == "no", "substance"].tolist()
    scatter_loglog(ghg, "ei_vs_EDGAR_ghg", "Greenhouse gases and F-gases", missing=absent)
    scatter_loglog(df[df["classification"] == "Air pollutant"],
                   "ei_vs_EDGAR_ap", "Air pollutants")

    cols = ["substance", "classification", "ecoinvent_kg", "edgar_kg", "deviation_pct"]
    print("Relative deviation of the ecoinvent inventory vs EDGAR (2018):")
    print(df[cols].to_string(index=False, float_format=lambda v: f"{v:.3e}"))
    print(f"\nFigures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
