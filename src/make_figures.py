"""Regenerate the ecoinvent-vs-EDGAR validation figures (manuscript Figures 2 and 3).

The figures compare the ecoinvent-derived normalization inventory (this study)
against the public EDGAR v8.0 / v8.1 global emission inventory, for greenhouse gases
and for air pollutants, on log-log axes with a 1:1 reference line.

This script is intentionally decoupled from the heavy LCI pipeline: it reads the
pre-aggregated global totals from ``data/figure_data.csv`` and needs only pandas
and matplotlib. The figures can therefore be regenerated without an ecoinvent
licence or a Brightway installation. The ecoinvent totals in that CSV are produced
by the main workflow notebook; the EDGAR totals are taken from the cited sources.

Usage
-----
    python src/make_figures.py

Outputs (written to ``figures/``): ``ei_vs_EDGAR_ghg`` and ``ei_vs_EDGAR_ap``,
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

POINT_COLOUR = "#c0392b"
ONE_TO_ONE_COLOUR = "0.5"


def load_data() -> pd.DataFrame:
    """Load the figure data and add the relative deviation column."""
    df = pd.read_csv(DATA_FILE)
    df["deviation_pct"] = (df["ecoinvent_kg"] - df["edgar_kg"]) / df["edgar_kg"] * 100.0
    return df


def scatter_loglog(subset: pd.DataFrame, stem: str, title: str) -> None:
    """Save a log-log ecoinvent-vs-EDGAR scatter with a 1:1 line and point labels."""
    x = np.log10(subset["ecoinvent_kg"].to_numpy())
    y = np.log10(subset["edgar_kg"].to_numpy())
    lo = min(x.min(), y.min()) - 0.6
    hi = max(x.max(), y.max()) + 0.6

    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.plot([lo, hi], [lo, hi], "--", color=ONE_TO_ONE_COLOUR, lw=1.0, label="1:1 (y = x)")
    ax.scatter(x, y, s=48, color=POINT_COLOUR, zorder=3)
    for xi, yi, label in zip(x, y, subset["label"]):
        ax.annotate(label, (xi, yi), textcoords="offset points", xytext=(6, 5), fontsize=10)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel(r"ecoinvent normalization inventory  [log$_{10}$ kg yr$^{-1}$]")
    ax.set_ylabel(r"EDGAR reference (v8.0 / v8.1, 2018)  [log$_{10}$ kg yr$^{-1}$]")
    ax.set_title(title)
    ax.grid(True, ls=":", alpha=0.6)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()

    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    plt.style.use("ggplot")
    df = load_data()

    scatter_loglog(df[df["classification"] == "GHG"], "ei_vs_EDGAR_ghg", "Greenhouse gases")
    scatter_loglog(df[df["classification"] == "Air pollutant"], "ei_vs_EDGAR_ap", "Air pollutants")

    cols = ["substance", "ecoinvent_kg", "edgar_kg", "deviation_pct"]
    print("Relative deviation of the ecoinvent inventory vs EDGAR v8.0 / v8.1:")
    print(df[cols].to_string(index=False, float_format=lambda v: f"{v:.3e}"))
    print(f"\nFigures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
