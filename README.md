# 3-cores in random intersection graphs

WI4465 Advanced Topics in Probability course project: study how clustering
affects the 3-core phase transition. The assignment is in
`3-core-random-intersection-graphs.pdf`. Triangle-RIG simulation is implemented;
configuration-model comparisons and cavity equations are future work.

## Start here

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and GNU Make,
then run these commands from the repository root:

```bash
make setup
make check
```

Open the root folder in VS Code and select `.venv/bin/python` as both the Python
interpreter and the notebook kernel. The implementation and its mathematical
explanation live together in four notebooks:

| Notebook | What it contains |
| --- | --- |
| [01_graphs.ipynb](notebooks/01_graphs.ipynb) | The original `Node` and `Graph` classes: neighbours, degrees, edges, and graph copying. |
| [02_algorithms.ipynb](notebooks/02_algorithms.ipynb) | The original queue-based k-core algorithm and fixed-size-community RIG constructors. |
| [03_triangle_simulation.ipynb](notebooks/03_triangle_simulation.ipynb) | Seeded triangle-RIG trials, parallel parameter sweeps, and individual CSV measurements. |
| [04_triangle_analysis.ipynb](notebooks/04_triangle_analysis.ipynb) | Loading saved measurements, summary statistics, the slope heuristic, and plotting. |

Read the notebooks in that order. Each notebook runs from top to bottom in a
fresh kernel: notebook 02 loads definitions from 01 with `%run`, and notebook 03
loads 02. Notebooks 01 and 02 only define classes and functions, so loading them
does not start simulations. Notebook 04 reads saved CSV independently of those
definitions.

Edit the **Experiment settings** cell in notebook 03 to change graph size,
membership-mean grid, repeats, seed, workers, or the CSV path. Edit the settings
cell in notebook 04 to select that CSV, smoothing, and the figure path. Both cells
contain a commented `config` dictionary. `jobs = 1` runs sequentially;
`jobs = -1` uses all available CPUs. Keep `data_file` the same in both notebooks
when analyzing a new run. Output paths are relative to the repository root.

## Terminal workflow

```bash
make run       # Execute simulation, save CSV, then execute analysis
make simulate  # Execute simulation and replace the configured CSV
make figures   # Analyze an existing CSV without rerunning simulations
make smoke     # Tiny simulation/analysis check using temporary outputs
make help      # List development commands
```

These commands execute the same notebooks used interactively, without saving
executed notebook copies or adding outputs to the source notebooks. Measurements
and exploratory figures go in `results/runs/` and `results/figures/`. Generated
results are ignored by Git.

After changing simulation settings, use `make run` or `make simulate` to create
new measurements. `make figures` reuses an existing CSV even when settings have
changed; if it is missing, run `make simulate` first. Use distinct CSV and figure
paths in the settings cells to retain different experiments.

The graph classes and core/generation algorithms follow the initial notebook
implementation. Additions retain community memberships and give each trial an
explicit random seed. A saved seed replays membership sampling, stub matching,
and core measurements; UUID vertex labels themselves are freshly generated.

The plot's bands describe variation between graphs, and its maximum-slope marker
is a finite-size heuristic rather than a theoretical critical value.

See [development.md](docs/development.md) for setup and modification commands,
[architecture.md](docs/architecture.md) for graph and probability conventions,
and [report/README.md](report/README.md) for the future report layout.
