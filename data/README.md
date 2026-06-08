# Data

## Included in this repository

### `figure_data.csv`
Aggregated global annual totals used to draw the validation figures (Figures 2–3)
via `../src/make_figures.py`. One row per benchmark substance.

| column | meaning |
|---|---|
| `substance` | substance identifier |
| `label` | matplotlib label (math text) |
| `classification` | `GHG` or `Air pollutant` (selects the figure) |
| `ecoinvent_kg` | global annual amount from the ecoinvent-derived normalization inventory (this study), kg yr⁻¹ |
| `edgar_kg` | EDGAR v4.3.2 global anthropogenic total, kg yr⁻¹ |
| `edgar_year` | EDGAR reference year (2010 for GHGs, 2012 for CO/air pollutants) |
| `edgar_source` | EDGAR source publication |

EDGAR references:
- Greenhouse gases (CO₂, CH₄, N₂O): Janssens-Maenhout et al. (2019), *Earth Syst. Sci. Data* 11, 959–1002 — https://doi.org/10.5194/essd-11-959-2019
- CO and air pollutants (NOₓ, SO₂, NH₃, NMVOC, PM₂.₅): Crippa et al. (2018), *Earth Syst. Sci. Data* 10, 1987–2013 — https://doi.org/10.5194/essd-10-1987-2018

The `ecoinvent_kg` values are produced by `notebooks/Normalization_full_workflow.ipynb`.

> ⚠️ The **N₂O** EDGAR value (7.2 Tg) may be reported on an N₂O-N vs N₂O basis — verify before final use.

### `ISIC.xlsx`
ISIC rev.4 division codes and labels, used to aggregate the sector contribution
analysis (manuscript Figure 5).

## NOT included (licensed / large)

- **ecoinvent 3.8 cut-off** (ecoSpold02) — a commercial licence is required; obtain it from https://ecoinvent.org and set `ECOINVENT_DIR` in the notebook configuration cell.
- **LCIA method packages** (e.g. IMPACTWorld+ Brightway package) — set `LCIA_METHODS_FILE` in the notebook.
- Large cached/derived files (`ei_complete.pkl`, `*.bw2package`, the full inventory spreadsheets) are produced by running the workflow and are git-ignored.
