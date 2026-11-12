# Order Matters: code and data

Code and data for the paper *Order Matters: Criterion Order and the Reliability of Profile-Area Scores in Multicriteria Decision Analysis* (Sara Amar, manuscript in preparation).

Profile-area methods score an alternative by the area under a curve drawn through its criterion ratings, with the
criteria placed along an axis according to their importance. This repository contains

* `simulation/` – the simulation study (Section 6): how often the order of the criteria changes the ranking;
* `application/` – the case study (Section 7): choosing a food-distribution warehouse site among 16 U.S. Midwest metros,
  built entirely from public data.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.9 on macOS.

## Simulation (Section 6)

```bash
cd simulation
python profile_area_sim_full.py 1000   # about 30 minutes; writes results/full_results.csv
python figure2_simulation.py           # Figure 2
```

* Criteria: n = 3–7; alternatives: m = 3, 5, 10; 1,000 weight vectors per (n, interpolant), 300 for n = 7.
* Weights ~ Dirichlet(1); ratings ~ Uniform[1, 9]; every ordering of the criteria is evaluated.
* Interpolants: piecewise linear, Lagrange polynomial, natural cubic spline.
* Scores: signed area under the profile, and distance to a target profile (rating 9 on every criterion).
* Benchmark: the weighted sum with the stated weights. The seed is fixed (`20261112`).

`profile_area_sim.py` is the earlier pilot (integer ratings 1–9, signed area only); its output is
`results/pilot_results.csv`. The results used in the paper are in `results/full_results.csv`. Column definitions are
in the docstring of `profile_area_sim_full.py`.

## Application (Section 7)

All scripts are run from the `application/` folder, in this order:

| Step | Script | Output |
|---|---|---|
| 0 | `download_public.py` | Census, CFS and Cushman & Wakefield inputs in `raw/` |
| 1 | `bls.py` | `raw/bls_raw.json` – OEWS wages and employment (SOC 53-7062), LAUS unemployment, via the BLS Public Data API |
| 2 | `nhs.py` | `raw/interstate_access.csv` – interstate miles inside each metro (BTS NTAD National Highway System) |
| 3 | `cw_parse.py` | `raw/cw_q3_2026.json` – warehouse/distribution asking rents and vacancy, Q3 2026 |
| 4 | `assemble.py` | `raw/site_criteria.csv` – 20 candidate metros |
| 5 | `make_workbook.py`, `restrict16.py` | `Paper1_Site_Criteria_Data.xlsx` – restricted to the 16 markets covered by Cushman & Wakefield |
| 6 | `cfs_tally.py` | `raw/cfs2022_*.csv` – 2022 CFS truck tonnage by commodity and destination area |
| 7 | `county_demand.py` | `raw/county_food_demand.csv` – food tonnage (SCTG 05–09) allocated to counties by 2020 population |
| 8 | `metro_centers.py` | `raw/metro_centers.csv` – population-weighted centre of each metro |
| 9 | `osrm_distances.py` | `raw/osrm/*.csv` – road miles to every contiguous-US county (public OSRM server, 1 request/s) |
| 10 | `coverage.py` | food demand within 250 road miles, added to the workbook |
| 11 | `application.py`, `figure_ranks.py` | `results/` – rankings under all 720 orderings, Table 6, Figure 3 |

```bash
cd application
python scripts/download_public.py
python scripts/bls.py
# ... and so on, in the order above
```

### About the stored data

The files in `application/raw/` and `application/results/` are the snapshot used in the paper (retrieved
November 11, 2026). Re-running the download steps can give slightly different values, because the BLS API returns the
latest release, the National Highway System and OpenStreetMap are updated continuously, and preliminary figures are
revised. To reproduce the paper exactly, start from step 4 or later with the stored files.

Two inputs are not stored because of their size or license; `download_public.py` fetches them:

* the 2022 Commodity Flow Survey public-use file (`cfs_2022_pums.zip`, about 680 MB), needed only for step 6;
* the Cushman & Wakefield *U.S. Industrial MarketBeat Q3 2026* report (PDF), needed only for step 3. Only the
  figures extracted from it are stored (`raw/cw_q3_2026.json`).

`results/distance_spot_check_results.csv` compares eight OSRM road distances with Google Maps (mean absolute
difference 1.1%, maximum 3.3%).

## Data sources

* U.S. Census Bureau: CBSA population estimates (Vintage 2024); cartographic boundary files (2023); 2020 county centers
  of population; 2022 Commodity Flow Survey public-use microdata and CFS area definitions.
* U.S. Bureau of Labor Statistics: Occupational Employment and Wage Statistics (May 2025); Local Area Unemployment
  Statistics.
* U.S. Bureau of Transportation Statistics: National Transportation Atlas Database, National Highway System.
* Cushman & Wakefield: U.S. Industrial MarketBeat, Q3 2026.
* OpenStreetMap contributors, routed with OSRM (project-osrm.org).

## License

Code: MIT (see `LICENSE`). The data files remain subject to the terms of their original publishers.

## Citation

If you use this code, please cite the paper (citation to be added on publication).
