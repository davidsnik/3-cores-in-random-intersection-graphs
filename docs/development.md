# Development

Run commands from the repository root. [README.md](../README.md) gives the
workflow; [architecture.md](architecture.md) explains the scientific conventions.

## Environment and editor

`make setup` (or `make sync`) runs `uv sync --locked`: it creates `.venv` and
installs the locked dependencies. This is a notebook project, so no local Python
package needs installing. Python 3.12 or newer is supported; `.python-version`
selects the development Python. Run `make sync` after pulling dependency changes.

NumPy, Matplotlib, and joblib are runtime dependencies. Development dependencies
include pytest, Ruff, ipykernel, nbclient, and nbformat. They provide the notebook
kernel, command-line notebook execution, and fresh-kernel tests. VS Code supplies
the notebook editor; a separate JupyterLab installation is unnecessary.

Open the root folder in VS Code and install the recommended Python, Pylance,
Jupyter, and Ruff extensions. Choose `.venv/bin/python` with **Python: Select
Interpreter**, then select the same environment separately in each notebook's
**Select Kernel** menu. Run notebook cells top to bottom. When changing an
upstream definition, restart and rerun the dependent notebook so its `%run` loads
the updated definitions.

Manual activation is optional: `uv run --locked python` already uses `.venv`.
To activate it in one terminal, use `source .venv/bin/activate`; leave it with
`deactivate`. The environment is disposable and is not committed.

## Commands and configuration

```bash
make run           # Run the selected stage in 03, then analyze its data in 04
make simulate      # Execute 03 and save the selected stage's CSVs
make figures       # Execute 04 against a saved stage; no simulation
make test          # Run pytest, including fresh-kernel notebook checks
make smoke         # Run a tiny simulation and analysis with temporary outputs
make lint          # Ruff lint checks for Python and notebook code
make format        # Apply Ruff formatting
make format-check  # Check formatting without rewriting files
make check         # Lint, formatting checks, and tests
make help          # List available tasks
```

Terminal execution runs notebooks under `notebooks/` without saving executed
copies or adding execution counts or outputs to source notebooks. Clear any
outputs created during interactive work before committing. Notebook path setup
supports kernels started in `notebooks/` or the repository root; sibling `%run`
calls work in either case.

Edit the commented `config` dictionary in the **Study settings** cell of
`notebooks/03_triangle_simulation.ipynb`. Its `experiments` dictionary contains
settings for three stages:

1. Run `"stage": "pilot"` to explore the range and measure runtime.
2. Select `"comparison"` to compare increasing graph sizes on a common grid.
3. Set the bounds for `"refinement"` from those results, then select that stage
   to collect more trials on a finer grid near the transition.

Inside a stage, `sizes` lists graph sizes; `lambda_min`, `lambda_max`, and
`lambda_count` define a grid including both endpoints; `repeats` sets independent
trials at each point. The shared `jobs` setting controls parallel trials: use
`1` for sequential execution, a positive number for that many workers, or `-1`
for all available CPUs. Start with the pilot and use its timing information to
decide whether the proposed larger runs are practical on your machine.

Select the same `stage` in notebook 04 and set its `data_dir` to match notebook
03's `output_dir`. Its `figure_dir` receives comparison, close-up, and histogram
PNGs plus summary and transition-estimate CSVs. `smoothing_window` controls the
main slope marker; `sensitivity_windows` compares several choices. Windows must
be positive and odd. `zoom_width`, `histogram_n`, and `histogram_lambdas` control
which outcomes are shown more closely; the notebook explains their defaults.

Simulation checks every selected file before doing work and refuses to replace
existing measurements. To intentionally repeat a stage, set `overwrite` to
`True`; to keep another study, choose a different `output_dir` and update
analysis to match. Analysis may regenerate its figures and summary tables without
changing trial CSVs. It uses saved data even if simulation settings have changed;
missing data is an error directing you to run the selected stage first.

Paths are relative to the repository root. In the editor, restart and run the
relevant notebook from top to bottom after changing settings; in the terminal,
Make reads the saved notebook cells. There is no separate settings file or
environment-variable configuration.

## Modifying the project

- Change the graph representation, edge operations, or copying in
  `notebooks/01_graphs.ipynb`. Keep cached degrees, neighbour sets, and edge sets
  consistent. Invalid operations must raise an error without leaving partial
  changes. Edge edits through either a node or its graph must update all three
  representations of the connection.
- Change core peeling and community matching in `notebooks/02_algorithms.ipynb`.
  `construct_special_triangle_RIG` is the Poisson/triangle wrapper;
  `construct_random_intersection_graph` accepts other membership samplers and
  fixed community sizes.
- Change trial measurements, seed assignment, study stages, or CSV output in
  `notebooks/03_triangle_simulation.ipynb`. Assign seeds before dispatch and
  retain individual replay seeds in saved rows. Keep stages and graph sizes on
  separate streams, and protect saved measurements unless replacement is explicit.
- Change summaries, smoothing, or figure styles in
  `notebooks/04_triangle_analysis.ipynb`.
  Analyze saved measurements without loading or generating graphs.
- Add another notebook for a distinct mathematical question. Reuse definitions
  with `%run`; keep reusable definition notebooks free of experiment side effects.
- Add small correctness tests under `tests/`. Tests execute notebook definitions
  in fresh kernels rather than maintaining separate algorithm implementations.
  Workflow checks replace the cells tagged `parameters` in temporary notebook
  copies and use temporary outputs, leaving research settings and results
  untouched.

Manage dependencies through `uv add PACKAGE`, `uv add --dev TOOL`, and
`uv remove PACKAGE`. Commit `pyproject.toml` and `uv.lock` together; never edit
the lockfile manually. To intentionally upgrade one dependency, run
`uv lock --upgrade-package numpy`, then `uv sync --locked`.

Before committing, run `make check`, clear source notebook outputs, and review
the staged diff. Start Codex sessions at the root so `AGENTS.md` is found.
See [report/README.md](../report/README.md) for report conventions.
