"""Schematic of the method: how a unit-process LCI database and activity data
combine into a normalization inventory and, after characterization, into
normalization references.

Produces figures/method_overview.{png,pdf}. Pure matplotlib (no data inputs).
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"

# palette: (fill, edge)
BLUE = ("#dbe9f6", "#3a6ea5")
GREEN = ("#e2f0d9", "#548235")
ORANGE = ("#fbe5d6", "#c55a11")
RED = ("#f2dcdb", "#c0392b")
GREY = "#444444"


def box(ax, x, y, w, h, title, body, colours, title_size=12, body_size=9.5):
    fill, edge = colours
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.6, edgecolor=edge, facecolor=fill, zorder=2,
        )
    )
    cx = x + w / 2
    ax.text(cx, y + h - 0.30, title, ha="center", va="top",
            fontsize=title_size, fontweight="bold", color=edge, zorder=3)
    ax.text(cx, y + h - 0.72, body, ha="center", va="top",
            fontsize=body_size, color="#222222", zorder=3, linespacing=1.45)


def main():
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # --- top row: LCI database  x  activity data  =  normalization inventory ---
    box(ax, 0.15, 3.25, 2.55, 2.05,
        "Unit-process\nLCI database",
        "ecoinvent 3.8 cut-off\n\nemission & resource\nintensities  $q_{s,p}$",
        BLUE)

    ax.text(2.95, 4.27, r"$\times$", ha="center", va="center",
            fontsize=26, color=GREY, fontweight="bold")

    box(ax, 3.25, 2.95, 3.25, 2.65,
        "Activity data",
        "annual production\nvolumes  $PV_p$\n\n"
        "sources:\n"
        "• ecoinvent production volumes\n"
        "• trade statistics\n"
        "• industry / association reports\n"
        "• peer-reviewed literature",
        GREEN, body_size=9.0)

    ax.text(6.78, 4.27, r"$=$", ha="center", va="center",
            fontsize=26, color=GREY, fontweight="bold")

    box(ax, 7.05, 3.25, 2.80, 2.05,
        "Normalization\ninventory",
        "global annual emissions\n& resource extractions\n\n"
        r"$Q_s=\sum_p q_{s,p}\,PV_p$",
        ORANGE)

    # --- downstream: x characterization factors -> normalization references ---
    arrow = FancyArrowPatch((8.45, 3.25), (8.45, 1.95),
                            arrowstyle="-|>", mutation_scale=18,
                            linewidth=1.8, color=GREY, zorder=1)
    ax.add_patch(arrow)
    ax.text(8.62, 2.62,
            "$\\times$ characterization factors\n(EF v3.0, ReCiPe 2016,\nIMPACTWorld+)",
            ha="left", va="center", fontsize=8.6, color=GREY, linespacing=1.4)

    box(ax, 5.55, 0.20, 4.30, 1.70,
        "Normalization references",
        r"$NR_i=\sum_s Q_s\,CF_{i,s}$"
        "\n(per impact category $i$; with Monte Carlo uncertainty)",
        RED, body_size=9.5)

    fig.tight_layout()
    FIG_DIR.mkdir(exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"method_overview.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"method overview written to {FIG_DIR}")


if __name__ == "__main__":
    main()
