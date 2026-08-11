"""A cleaner, publication-quality Figure 1 (method overview) in Heijungs notation."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse, Arc, Rectangle
import matplotlib.patheffects as pe

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})

# cool -> warm palette mirroring the pipeline
B_C   = ("#e7eef6", "#1f4e79")   # fill, accent
S_C   = ("#e3f0ec", "#2e7d6b")
G_C   = ("#fbeed6", "#b9791b")
H_C   = ("#f6e4de", "#a63a25")
GREY  = "#8a8a8a"
INK   = "#2b2b2b"

fig, ax = plt.subplots(figsize=(10.2, 4.8))
ax.set_xlim(0, 102); ax.set_ylim(0, 48); ax.axis("off"); ax.set_aspect("equal")

def card(x, y, w, h, fill, edge):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.6",
                       linewidth=1.8, edgecolor=edge, facecolor=fill, zorder=2)
    p.set_path_effects([pe.withSimplePatchShadow(offset=(1.6, -1.6), alpha=0.12)])
    ax.add_patch(p)

def T(x, y, s, size, color=INK, weight="normal", ha="center", style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va="center",
            fontweight=weight, style=style, zorder=4)

def db_icon(cx, cy, color):  # small database cylinder
    w, h = 4.2, 1.6
    ax.add_patch(Ellipse((cx, cy + 3.0), w, h, facecolor="none", edgecolor=color, lw=1.3, zorder=4))
    ax.add_patch(Rectangle((cx - w/2, cy - 3.0), w, 6.0, facecolor="none", edgecolor="none", zorder=3))
    for yy in (cx*0+cy+3.0, cy, cy-3.0):
        ax.add_patch(Arc((cx, yy), w, h, theta1=180, theta2=360, edgecolor=color, lw=1.3, zorder=4))
    ax.plot([cx - w/2, cx - w/2], [cy - 3.0, cy + 3.0], color=color, lw=1.3, zorder=4)
    ax.plot([cx + w/2, cx + w/2], [cy - 3.0, cy + 3.0], color=color, lw=1.3, zorder=4)

def globe(cx, cy, r, color):
    ax.add_patch(Circle((cx, cy), r, facecolor="none", edgecolor=color, lw=1.3, zorder=4))
    ax.add_patch(Ellipse((cx, cy), r*0.9, 2*r, facecolor="none", edgecolor=color, lw=1.0, zorder=4))
    ax.plot([cx-r, cx+r], [cy, cy], color=color, lw=1.0, zorder=4)

# ---- top row: B (x) s = g ----
card(3, 27, 25, 15, *B_C)
T(15.5, 38.6, r"Intervention matrix $\mathbf{B}$", 12.5, B_C[1], "bold")
T(15.5, 33.6, "ecoinvent 3.8 cut-off", 9.5)
T(15.5, 30.2, r"direct flow intensities $b_{e,p}$", 9.5)

T(31, 34.5, r"$\times$", 26, GREY, "bold")

card(34, 24.5, 28, 17.5, *S_C)
T(48, 39.0, r"Scaling vector $\dot{s}$", 12.5, S_C[1], "bold")
T(48, 34.8, r"annual production volumes  $\dot{s}_p = PV_p$", 9.3)
T(48, 30.6, "sources", 8.5, GREY, "bold")
T(48, 27.8, "ecoinvent · trade statistics ·\nreports · literature", 8.2)

T(65, 34.5, r"$=$", 26, GREY, "bold")

card(68, 27, 30, 15, *G_C)
T(83, 38.6, r"Normalization inventory $\dot{g}$", 12, G_C[1], "bold")
T(83, 34.2, r"$\dot{g} = \mathbf{B}\,\dot{s}$", 14, INK, "bold")
T(83, 30.2, "global annual amount of each flow", 8.8)

# ---- characterization arrow g -> h ----
arr = FancyArrowPatch((83, 27), (83, 19.5), arrowstyle="-|>", mutation_scale=20,
                      lw=2.4, color=GREY, zorder=3)
ax.add_patch(arr)
T(80, 23.3, r"$\times\ \mathbf{Q}$   characterization matrix", 9.3, INK, "bold", ha="right")
T(80, 20.6, "(EF v3.0,  ReCiPe 2016,  IMPACTWorld+)", 8.2, GREY, ha="right")

# ---- normalization reference h ----
card(68, 3.5, 30, 15, *H_C)
T(83, 15.0, r"Normalization reference $\dot{h}$", 12, H_C[1], "bold")
T(83, 10.4, r"$\dot{h} = \mathbf{Q}\,\dot{g}$", 13, INK, "bold")
T(83, 6.5, r"per impact category $i$", 8.8)

# ---- footnote: normalized result ----
T(4, 10.5, "Applied to a product\nsystem under study:", 9.2, INK, "bold", ha="left")
T(4, 5.2, r"$\tilde{h}_i = h_i\,/\,\dot{h}_i$      (unit: yr)", 12, INK, "bold", ha="left")

fig.tight_layout(pad=0.4)
OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(exist_ok=True)
fig.savefig(OUT / "method_overview.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "method_overview.pdf", bbox_inches="tight")
print("saved to", OUT)
