# TSP Food Tour: Simulated Annealing vs Genetic Algorithm

Finds the optimal visiting order for a 20-stop Hanoi Old Quarter food tour by
solving it as a closed-loop Travelling Salesman Problem, comparing two local
search techniques: **Simulated Annealing (SA)** and a **Genetic Algorithm
(GA)**.

## Project structure

```
tsp/
  distances.py          # OSRM walking-distance matrix fetch + caching
  problem.py             # loads locations, holds distance matrix, tour cost
  simulated_annealing.py
  genetic_algorithm.py
  compare.py              # runs both algorithms N trials, collects metrics
  visualize.py             # route map + convergence plots
run_distance_matrix.py     # one-off: fetch + cache OSRM distance matrix
run_tsp_compare.py         # run SA vs GA, print/save comparison
data_collection/           # geocoding + location map scripts, locations.csv
data/                      # cached distance matrix (OSRM output)
results/                   # comparison_summary.csv, convergence.png, route maps
tests/                     # pytest test suite
report/                    # written report, notebook, rubric
```

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Copy `.env.example` to `.env` and set `GOOGLE_MAPS_API_KEY` if re-running the
geocoding scripts in `data_collection/`.

## Usage

```bash
# One-off: fetch and cache the walking-distance matrix from OSRM
uv run python run_distance_matrix.py

# Run SA vs GA comparison (10 trials each), save results and plots
uv run python run_tsp_compare.py
```

Outputs are written to `results/`: `comparison_summary.csv`,
`convergence.png`, and the best route plotted on a map.

## Testing

```bash
uv run pytest
```
