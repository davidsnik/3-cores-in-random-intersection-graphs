# Project guidance

This WI4465 Advanced Topics in Probability project studies the 3-core transition
in random intersection graphs. The root assignment PDF defines the scope.
Triangle simulation is implemented; configuration-model comparisons and cavity
equations remain future work.

## Start here

- `notebooks/01_graphs.ipynb`: the initial notebook's UUID-based `Node` and `Graph` classes.
- `notebooks/02_algorithms.ipynb`: `construct_k_core`,
  `construct_random_intersection_graph`, and `construct_special_triangle_RIG`.
- `notebooks/03_triangle_simulation.ipynb`: seeded trials, sweeps, and CSV output;
  edit its `config` dictionary to choose simulation settings.
- `notebooks/04_triangle_analysis.ipynb`: independent saved-data analysis and
  figures; edit its `config` dictionary to choose input, output, and smoothing.
- [docs/architecture.md](docs/architecture.md): data and mathematical conventions.
- [docs/development.md](docs/development.md): setup, commands, and editor workflow.

## Commands

```sh
make setup     # Synchronize .venv from uv.lock (alias: make sync)
make check     # Ruff checks and tests, including fresh-kernel notebook execution
make smoke     # Tiny simulation and analysis with temporary outputs
make run       # Execute simulation, then analysis
make simulate  # Rerun the configured sweep and replace its CSV
make figures   # Replot an existing CSV; run make simulate first if it is missing
```

## Changes

- Keep mathematical explanations and implementations together in the notebooks.
  Preserve the initial notebook's class-based graph representation and algorithms
  unless a concrete correctness or usability need justifies a change. Do not
  duplicate domain implementations in Python modules or test files.
- Reuse notebook definitions with `%run`: 02 loads 01, and 03 loads 02.
  Notebooks 01 and 02 must only define classes/functions and import dependencies;
  loading them must not simulate, plot, or write files. Keep analysis independent
  of graph construction so saved measurements can be plotted in a fresh kernel.
- Keep notebooks executable from top to bottom. Clear source outputs before
  committing; command-line execution neither saves notebook copies nor changes
  source outputs. Notebook path setup supports kernels started in `notebooks/`
  or the repository root; output paths are relative to the repository root.
- Keep experiment settings in the relevant notebook's commented `config`
  dictionary, in its cell tagged `parameters`. Keep the simulation and analysis
  `data_file` settings aligned. Analysis must report missing data rather than
  starting a simulation implicitly.
- Pass explicit NumPy generators and assign trial seeds before parallel dispatch.
  Seeds reproduce membership sampling, matching, and measurements; UUID labels
  are intentionally not reproducible. Save replay parameters with measurements.
- Retain original community slots and membership counts on generated graphs and
  their copies as generation provenance. Preserve full-vector divisibility
  conditioning and simple-graph projection. Core construction must leave its
  input unchanged. Distinguish measurements, heuristics, and theory.
- Add meaningful small tests for changed behavior; run `make check`. Tests load
  notebook implementations in fresh kernels. Workflow tests use tiny settings
  and temporary outputs, leaving research measurements untouched.
- Use `uv add`, `uv add --dev`, and `uv remove` for dependencies; commit
  `pyproject.toml` and `uv.lock` together. Do not edit the lockfile by hand. This
  is a notebook project, with no installable Python package or build target.
- Update relevant short guides when behavior changes. Preserve the assignment
  PDF. Keep `.venv`, generated results, caches, and builds out of Git.
