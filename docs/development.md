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
make run           # Execute 03 to save measurements, then 04 to save the figure
make simulate      # Execute 03 and replace the configured CSV
make figures       # Execute 04 against an existing CSV; no simulation
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

Edit the commented `config` dictionary in the **Experiment settings** cell of
`notebooks/03_triangle_simulation.ipynb`. For example, set `"n": 5000`,
`"repeats": 50`, and `"jobs": 4`, then run `make run`. The lambda grid includes
its endpoints. Set `data_file`, `figure_file`, and `smoothing_window` in the
settings cell of `notebooks/04_triangle_analysis.ipynb`. The smoothing window
must be positive and odd. Paths are relative to the repository root. In the
editor, restart and run the relevant notebook from top to bottom after changing
settings; in the terminal, Make reads the saved notebook cells.

Simulation replaces the selected CSV. To retain another run, choose distinct
`data_file` and `figure_file` paths. Figure generation reuses an existing CSV even
if simulation settings changed: rerun the simulation explicitly to measure new
settings. If the CSV does not exist, run `make simulate` before `make figures`.
When choosing another CSV path, update `data_file` in both notebooks. The figure
file extension selects a format such as PNG or PDF. There is no separate settings
file or environment-variable configuration.

## Modifying the project

- Change the graph representation, edge operations, or copying in
  `notebooks/01_graphs.ipynb`. Keep cached degrees, neighbour sets, and edge sets
  consistent.
- Change core peeling and community matching in `notebooks/02_algorithms.ipynb`.
  `construct_special_triangle_RIG` is the Poisson/triangle wrapper;
  `construct_random_intersection_graph` accepts other membership samplers and
  fixed community sizes.
- Change trial measurements, seed assignment, parameter sweeps, or CSV output in
  `notebooks/03_triangle_simulation.ipynb`. Assign seeds before dispatch and retain individual
  replay seeds in saved rows.
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
