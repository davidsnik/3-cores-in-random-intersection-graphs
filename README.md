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
| [01_graphs.ipynb](notebooks/01_graphs.ipynb) | How `Node` and `Graph` represent vertices, neighbours, degrees, and edges, and how to copy a graph. |
| [02_algorithms.ipynb](notebooks/02_algorithms.ipynb) | Finding a graph's k-core and building random intersection graphs from communities of a fixed size. |
| [03_triangle_simulation.ipynb](notebooks/03_triangle_simulation.ipynb) | A pilot run, comparisons across graph sizes, and closer experiments near the transition, with seeded parallel trials and CSV measurements. |
| [04_triangle_analysis.ipynb](notebooks/04_triangle_analysis.ipynb) | Comparing graph sizes, inspecting individual outcomes near the transition, and checking the sensitivity of the slope marker. |

Read the notebooks in that order. Each notebook runs from top to bottom in a
fresh kernel: notebook 02 loads definitions from 01 with `%run`, and notebook 03
loads 02. Notebooks 01 and 02 only define classes and functions, so loading them
does not start simulations. Notebook 04 reads saved CSV independently of those
definitions.

Both experiment notebooks have a commented `config` dictionary. Start with
`stage = "pilot"` in notebook 03 to explore a broad range of membership means and
measure runtime. Then select `"comparison"` to compare increasing graph sizes.
Finally, choose `"refinement"`, adjusting its lambda bounds after inspecting the
pilot and comparison plots, to take more measurements near the transition.
The supplied bounds are starting settings, not an established critical region.

Notebook 03 lets you choose graph sizes, the lambda grid, repeats, seed, workers,
and output directory for each stage. `jobs = 1` runs sequentially;
`jobs = -1` uses all available CPUs. Independent trials run in parallel, with
their seeds assigned beforehand. Notebook 04 selects a saved stage and controls
the analysis and figure settings. Keep its `stage` and `data_dir` aligned with
the simulation's `stage` and `output_dir`. Paths are relative to the repository
root. The default stage is the smaller pilot, so running the notebooks does not
automatically launch all of the larger experiments.

## Terminal workflow

```bash
make run       # Execute simulation, save CSV, then execute analysis
make simulate  # Run the selected stage and save one CSV per graph size
make figures   # Analyze the selected stage's saved CSVs; no simulation
make smoke     # Tiny simulation/analysis check using temporary outputs
make help      # List development commands
```

These commands execute the same notebooks used interactively, without saving
executed notebook copies or adding outputs to the source notebooks. Measurements
and exploratory figures go in `results/runs/` and `results/figures/`. Generated
results are ignored by Git.

The simulation saves files such as `pilot_n1000.csv` in
`results/runs/triangle_study/`. It refuses to replace existing measurements unless
you explicitly set `overwrite = True`. Choose another output directory to keep
another study, and update the analysis directory to match. `make figures` reuses
saved measurements even when simulation settings have changed; if data is missing,
run the selected simulation stage first.

Generated graphs keep a record of each individual's community memberships.
Each simulation trial also saves the random seed used to generate it. With the
same code and dependencies, that seed reproduces the community assignments and
core measurements. Vertex labels are newly generated each time; the labels do
not affect the graph's structure or core size.

The analysis compares mean core fractions across sizes, shows variation between
graphs and individual outcomes near the transition, and records summary tables.
It also checks how the maximum-slope marker changes with smoothing and graph
size. These markers are finite-size heuristics rather than theoretical critical
values. The experiments supply evidence to interpret; they do not automatically
decide whether the limiting transition is continuous or discontinuous.

See [development.md](docs/development.md) for setup and modification commands,
[architecture.md](docs/architecture.md) for graph and probability conventions,
and [report/README.md](report/README.md) for the future report layout.
