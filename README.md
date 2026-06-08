# Globally consistent normalization references for LCA from unit-process LCI databases

Code and data accompanying the manuscript:

> **A Novel Approach to Deriving Globally Consistent Normalization References for LCA Using Unit Process Databases**
> Nils Thonemann & Alexis Laurent. *Manuscript prepared for the International Journal of Life Cycle Assessment (IJLCA), GLAM special issue.*

This repository derives **external normalization references** for life cycle assessment (LCA) directly from a unit-process life cycle inventory (LCI) database (ecoinvent 3.8 cut-off), rather than from top-down statistical inventories. The aim is consistency between the normalization reference and the LCI data used in typical LCA studies.

## Method in brief

For each elementary flow *s*, an annual global amount is built from unit-process emission/extraction intensities weighted by annual production volumes:

```
Q_s   = Σ_p ( q_{s,p} × PV_p )          # global annual amount of flow s
NR_i  = Σ_s ( Q_s × CF_{i,s} )          # normalization reference for impact category i
```

where `q_{s,p}` is the amount of flow *s* per unit output of process *p*, `PV_p` the annual production volume of *p*, and `CF_{i,s}` the characterization factor. Calculations use the [Brightway 2.5](https://docs.brightway.dev/) framework. Normalization references are produced for **EF v3.0**, **ReCiPe 2016**, and **IMPACTWorld+**, with Monte Carlo uncertainty propagation from ecoinvent's lognormal parameter distributions.

The resulting inventory is validated against the public **EDGAR v4.3.2** global emission inventory (greenhouse gases and air pollutants).

## Repository structure

```
lci-normalization/
├── notebooks/
│   ├── Normalization_full_workflow.ipynb     # complete, end-to-end pipeline
│   ├── 01_setup_and_database_import.ipynb     # Brightway project + ecoinvent import
│   └── 02_production_volume_corrections.ipynb # documented PV corrections (run once)
├── src/
│   └── make_figures.py        # regenerates the EDGAR validation figures (Figs 2–3)
├── data/
│   ├── figure_data.csv        # aggregated global totals used by make_figures.py
│   ├── ISIC.xlsx              # ISIC rev.4 division labels (sector analysis)
│   └── README.md              # data provenance and the ecoinvent licence note
├── figures/                   # generated figures (PNG + PDF)
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Requirements

- Python 3.11
- A licensed **ecoinvent 3.8 cut-off** database (ecoSpold02) — *not redistributed here* (see `data/README.md`)
- The LCIA method package used for IMPACTWorld+ (set in the notebook configuration cell)

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Only `pandas`, `numpy` and `matplotlib` are needed to regenerate the figures (see below); the full Brightway stack is needed to rebuild the inventory.

## Reproducing the results

1. **Set paths** — open `notebooks/Normalization_full_workflow.ipynb` and edit the *USER CONFIGURATION* cell at the top (`ECOINVENT_DIR`, `LCIA_METHODS_FILE`, …).
2. **Run the workflow** — execute the notebook top to bottom. It imports ecoinvent, applies the production-volume corrections, builds the database-wide inventory (cached to `ei_complete.pkl`), assembles the normalization inventory, characterises it, runs the sector and uncertainty analyses, and writes the comparison/output files.
3. **Regenerate the figures** (no ecoinvent licence required):

   ```bash
   python src/make_figures.py
   ```

   This reads `data/figure_data.csv` and writes `figures/ei_vs_EDGAR_ghg.{png,pdf}` and `figures/ei_vs_EDGAR_ap.{png,pdf}`, and prints the relative deviations.

## Validation against EDGAR v4.3.2

ecoinvent reproduces global anthropogenic emissions of the major species within roughly a factor of two:

| Species | ecoinvent vs EDGAR | Species | ecoinvent vs EDGAR |
|---|---|---|---|
| CO₂ (fossil) | +43% | NOₓ | −6% |
| CO | +73% | SO₂ | +33% |
| CH₄ | −24% | NH₃ | −38% |
| N₂O | +35% *(see note)* | NMVOC | −80% |
|  |  | PM₂.₅ | −16% |

GHG totals: Janssens-Maenhout et al. (2019), EDGAR v4.3.2, 2010. CO and air pollutants: Crippa et al. (2018), EDGAR v4.3.2, 2012.

**Notes / open items**
- The **N₂O** reference (EDGAR 7.2 Tg) may be reported on an N₂O-N vs N₂O basis — verify before final use.
- **Fluorinated gases** (PFCs, HFCs, SF₆, NF₃) are underestimated by ecoinvent by 1–5 orders of magnitude (incomplete process coverage, e.g. no semiconductor/metal etching). EDGAR v4.3.2 does not provide per-species F-gas totals, so they are not included in the figures; add them from a newer EDGAR F-gas product if required.

## Citation

If you use this code, please cite the manuscript (see `CITATION.cff`). The underlying databases must be cited separately: ecoinvent 3.8 (Wernet et al. 2016), EDGAR v4.3.2 (Crippa et al. 2018; Janssens-Maenhout et al. 2019), and the LCIA methods used.

## License

Code is released under the MIT License (`LICENSE`). The ecoinvent database and the LCIA method packages are subject to their own licences and are not included in this repository.
