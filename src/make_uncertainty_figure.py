"""Regenerate the inventory-uncertainty figure for the manuscript.

Monte Carlo simulation (1,000 iterations, fixed seed) propagates the parameter-level
uncertainty distributions embedded in ecoinvent 3.8 through the normalization
inventory. For every elementary flow the coefficient of variation (CV = standard
deviation / mean) of the resulting global annual amount is recorded; this script
plots their distribution.

Input: ``data/uncertainty_cv.csv``, extracted from the full Monte Carlo output
(``global_inventory_uncertainty.xlsx``, produced by the workflow notebook) so that
the figure can be regenerated without the 30 MB result file.

Flows with a non-positive CV are excluded: a CV is only meaningful for a strictly
positive mean, and a handful of flows have a mean at or below zero because uptake
(negative) exchanges dominate them.

Usage
-----
    python src/make_uncertainty_figure.py

Outputs (in ``figures/``): ``uncertainty_cv`` as PNG (300 dpi) and PDF.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "uncertainty_cv.csv"
FIG_DIR = ROOT / "figures"

BAR = "#c0392b"
INK = "#2b2b2b"
XMAX = 2.0          # the long tail beyond this is summarised in the annotation
BINS = 80


def main() -> None:
    plt.style.use("ggplot")
    df = pd.read_csv(DATA_FILE)
    cv = pd.to_numeric(df["cv"], errors="coerce")
    cv = cv[cv > 0]

    median, mean = cv.median(), cv.mean()
    n_total = len(cv)
    n_tail = int((cv > XMAX).sum())

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.hist(cv[cv <= XMAX], bins=BINS, color=BAR, edgecolor="white", linewidth=0.3)

    ax.axvline(median, color=INK, ls="--", lw=1.4,
               label=f"median = {median:.2f}")
    ax.axvline(mean, color="0.35", ls=":", lw=1.4,
               label=f"mean = {mean:.2f}")

    ax.set_xlim(0, XMAX)
    ax.set_xlabel("Coefficient of variation of the global annual flow amount", fontsize=10)
    ax.set_ylabel("Number of elementary flows", fontsize=10)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(True, ls=":", alpha=0.6)

    ax.text(0.985, 0.72,
            f"n = {n_total:,} flows\n{n_tail} flows with CV > {XMAX:.0f} not shown",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=8.5, color="0.35")

    fig.tight_layout()
    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"uncertainty_cv.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"flows with positive CV: {n_total:,}")
    print(f"  median {median:.3f} | mean {mean:.3f}")
    for q in (0.25, 0.5, 0.75, 0.9, 0.95, 0.99):
        print(f"  q{q:.2f} = {cv.quantile(q):.3f}")
    print(f"  CV > {XMAX:.0f}: {n_tail} flows (max {cv.max():.1f})")
    print(f"\nFigure written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
