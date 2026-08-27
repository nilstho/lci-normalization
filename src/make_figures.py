"""Regenerate the ecoinvent-vs-EDGAR validation figure(s) for the manuscript.

The figure compares the ecoinvent-based normalization inventory (EI-NI, this
study) against the public EDGAR global emission inventory for reference year
2018, chosen to match the reference period of ecoinvent 3.8 (~2017-2018):

  * greenhouse gases and F-gases  -> EDGAR Community GHG database v8.0 (2023)
  * air pollutants                -> EDGAR v8.1 (release August 2024)

Both are plotted on logarithmic axes in Mt/year against a 1:1 reference line.
Axes are kept on an equal aspect so that the 1:1 line runs at 45 degrees.

This script is intentionally decoupled from the heavy LCI pipeline: it reads the
pre-aggregated global totals from ``data/figure_data.csv`` and needs only pandas
and matplotlib, so the figure can be regenerated without an ecoinvent licence or
a Brightway installation. The ecoinvent totals in that CSV come from the main
workflow notebook; the EDGAR totals are reproduced by ``edgar_global_totals.py``.

Species flagged ``in_figure = no`` are essentially absent from ecoinvent (zero or
near-zero) and cannot be placed on logarithmic axes; they are named in the panel.

Usage
-----
    python src/make_figures.py

Outputs (in ``figures/``), each as PNG (300 dpi) and PDF (vector):
    ei_vs_EDGAR_combined   two-panel figure (recommended for the manuscript)
    ei_vs_EDGAR_ghg        panel (a) on its own
    ei_vs_EDGAR_ap         panel (b) on its own
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "figure_data.csv"
FIG_DIR = ROOT / "figures"

KG_PER_MT = 1e9  # 1 Mt = 1e9 kg
ONE_TO_ONE_COLOUR = "0.5"
STYLE = {  # classification -> (colour, marker, legend label)
    "GHG":           ("#c0392b", "o", "Greenhouse gases"),
    "F-gas":         ("#1f4e79", "^", "F-gases"),
    "Air pollutant": ("#c0392b", "o", "Air pollutants"),
}
# manual nudges (points) where the default offset would overlap a neighbour
LABEL_OFFSET = {
    "HFC-23": (-46, 5), "SF6": (9, -4), "CF4": (7, -13),
    "CO": (7, -13), "PM2.5": (6, -14), "PM10": (7, 4),
}
DEFAULT_OFFSET = (6, 5)

XLABEL = r"EI-based normalization inventory  [Mt yr$^{-1}$]"
YLABEL = r"EDGAR reference, 2018  [Mt yr$^{-1}$]"


def load_data() -> pd.DataFrame:
    """Load the figure data, convert to Mt/year and add the relative deviation."""
    df = pd.read_csv(DATA_FILE)
    df["ecoinvent_mt"] = df["ecoinvent_kg"] / KG_PER_MT
    df["edgar_mt"] = df["edgar_kg"] / KG_PER_MT
    df["deviation_pct"] = (df["ecoinvent_kg"] - df["edgar_kg"]) / df["edgar_kg"] * 100.0
    return df


def draw_panel(ax, subset: pd.DataFrame, title: str,
               missing: list[str] | None = None, show_ylabel: bool = True) -> None:
    """Draw one log-log ecoinvent-vs-EDGAR panel (values in Mt/year)."""
    plotted = subset[subset["in_figure"] == "yes"]
    lo = min(plotted["ecoinvent_mt"].min(), plotted["edgar_mt"].min()) / 3.0
    hi = max(plotted["ecoinvent_mt"].max(), plotted["edgar_mt"].max()) * 3.0

    ax.plot([lo, hi], [lo, hi], "--", color=ONE_TO_ONE_COLOUR, lw=1.0, label="1:1 (y = x)")
    for cls, grp in plotted.groupby("classification", sort=False):
        colour, marker, legend = STYLE[cls]
        ax.scatter(grp["ecoinvent_mt"], grp["edgar_mt"], s=46, color=colour,
                   marker=marker, zorder=3,
                   label=legend if plotted["classification"].nunique() > 1 else None)
        for xi, yi, label, sub in zip(grp["ecoinvent_mt"], grp["edgar_mt"],
                                      grp["label"], grp["substance"]):
            ax.annotate(label, (xi, yi), textcoords="offset points",
                        xytext=LABEL_OFFSET.get(sub, DEFAULT_OFFSET), fontsize=9)

    if missing:
        # placed bottom-right, where the area below the 1:1 line is empty
        ax.text(0.97, 0.03, "Absent from ecoinvent:\n" + ", ".join(missing),
                transform=ax.transAxes, fontsize=8, color="0.35",
                va="bottom", ha="right")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")          # keeps the 1:1 line at 45 degrees

    # narrow ranges get plain numeric ticks (incl. minor) instead of 10^n only
    if np.log10(hi / lo) < 2.5:
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0,)))
            axis.set_minor_locator(mticker.LogLocator(base=10, subs=(0.3, 0.5, 2.0, 3.0, 5.0)))
            axis.set_major_formatter(mticker.ScalarFormatter())
            axis.set_minor_formatter(mticker.ScalarFormatter())
        ax.tick_params(axis="both", which="minor", labelsize=8)

    ax.set_xlabel(XLABEL, fontsize=10)
    if show_ylabel:
        ax.set_ylabel(YLABEL, fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.grid(True, ls=":", alpha=0.6, which="major")
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)


def main() -> None:
    plt.style.use("ggplot")
    df = load_data()

    ghg = df[df["classification"].isin(["GHG", "F-gas"])]
    ap = df[df["classification"] == "Air pollutant"]
    absent = ghg.loc[ghg["in_figure"] == "no", "substance"].tolist()

    FIG_DIR.mkdir(exist_ok=True)

    # --- combined two-panel figure (recommended for the manuscript) ---
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.4))
    draw_panel(axes[0], ghg, "(a) Greenhouse gases and F-gases", missing=absent)
    draw_panel(axes[1], ap, "(b) Air pollutants")
    fig.tight_layout(w_pad=2.0)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"ei_vs_EDGAR_combined.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # --- the same panels as standalone figures ---
    for subset, stem, title, miss in [
        (ghg, "ei_vs_EDGAR_ghg", "Greenhouse gases and F-gases", absent),
        (ap, "ei_vs_EDGAR_ap", "Air pollutants", None),
    ]:
        fig, ax = plt.subplots(figsize=(6.2, 5.8))
        draw_panel(ax, subset, title, missing=miss)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(FIG_DIR / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
        plt.close(fig)

    cols = ["substance", "classification", "ecoinvent_mt", "edgar_mt", "deviation_pct"]
    print("ecoinvent-based normalization inventory vs EDGAR (2018), Mt/year:")
    print(df[cols].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print(f"\nFigures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
