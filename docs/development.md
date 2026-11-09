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
make theory        # Execute the definitions-only theory notebook 05
make comparison    # Run the common-condition simulations in 06, then analysis in 07
make comparison-simulate  # Execute 06 and save one comparison CSV per size
make comparison-figures   # Execute 07 against saved comparison data; no simulation
make triangle-theory  # Execute triangle cavity definitions in 08
make triangle-refine  # Execute targeted additional triangle trials in 09
make triangle-figures # Execute 10 against saved 06 and 09 measurements
make triangle-study  # Run 09, then 10; existing trial CSVs remain protected
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

## Running the configuration comparison

Notebook 05 explains the theory and defines its numerical functions without
running simulations. Notebook 06 loads those definitions and the graph
algorithms. Its `parameters` cell contains a single flat `config` dictionary:

- `sizes` lists the numbers of vertices.
- `lambdas` lists the membership means; it is also the Poisson mean before
  doubling configuration-model degrees. An explicit list makes a denser grid
  near the transition easy to read.
- `repeats` sets independent trials per lambda and size.
- `seed` controls replay; `jobs` controls parallel trials without changing their
  measurements. There is no nested parallel loop.
- `output_dir` selects raw comparison CSVs. `overwrite = False` protects existing
  measurements; use another directory to retain a second run.

All models use these same settings. Each trial generates a triangle graph and
one configuration-model pairing, then measures the retained multigraph and its
erased simple projection separately. The latter two outcomes share a graph and
are paired observations. `make comparison-simulate` checks all selected output
paths before generating graphs, avoiding an incomplete rerun if a later target
already exists.

The default comparison includes larger graph sizes and more repeats than the
triangle pilot. Begin with smaller values if you want a timing check. You can
then select increasing sizes and a denser lambda list to investigate finite-size
effects near the theoretical critical value, approximately `1.28772`. Each row
retains a replay seed; keep the notebook settings and code version with any
research results you use.

Notebook 07 reads saved comparison data independently of graph generation. Match
its `data_dir` to notebook 06's `output_dir`. `figure_dir` controls its analysis
outputs; `focus_half_width` selects the close-up around the theoretical
transition; `degree_lambda` selects the degree-distribution comparison;
`histogram_n` and `histogram_lambdas` select individual-outcome histograms.
`large_core_cutoff` defines the fraction of surviving vertices called a
substantial core in a descriptive onset table. The table brackets where that
event first occurs in at least half of the trials; the cutoff and the grid
affect the answer, so it is not a theoretical critical-point estimate.
`critical_exclusion` controls the neighbourhood omitted from the
away-from-critical numerical error summary. It does not hide observations from
the curves or CSVs. Missing input is an error, not a request to launch a sweep.

Use `make comparison` for a new simulation followed by analysis, or
`make comparison-figures` to regenerate plots from saved data. The latter leaves
raw trial CSVs unchanged and does not load graph classes. Figures include
unsmoothed means, trial variation, theoretical predictions for the configuration
model, and diagnostics checking the degree and edge conventions.

## Running the triangle cavity study

Notebook 08 presents the triangle derivation and its numerical functions. It
does not generate graphs or save files. `make triangle-theory` executes it in a
fresh kernel; interactive readers can call the functions in its final sections.
The maximal fixed point is selected explicitly, and an independent direct
iteration is available to check the scalar branch solver away from its slow
critical bottleneck.

Reuse the existing raw comparison files from notebook 06. Notebook 09 supplies
additional triangle trials only where a finer grid is useful near the cavity
prediction. Its flat `config` contains `sizes`, `lambdas`, `repeats`, `seed`,
`jobs`, `output_dir`, and `overwrite`. Trial seeds are assigned before parallel
dispatch, so changing `jobs` leaves measurements unchanged. Refinement CSVs use
the name `cavity_refinement_n<size>.csv` and the basic triangle measurement
columns, including the replay seed. Graph sampling and core peeling are reused
from notebook 02; the whole broad study is not run again.

Notebook 10 reads the saved comparison and refinement directories selected in
its settings cell. `comparison_dir` selects the 06 measurements and
`refinement_dir` selects the 09 measurements; set the latter to `None` to analyze
only the broad comparison. Keep the refinement input aligned with notebook 09's
`output_dir`, which defaults to `results/runs/triangle_cavity/`. `figure_dir`
defaults to `results/figures/triangle_cavity/`. `focus_half_width` controls the
transition close-up; `histogram_n` and `histogram_lambdas` select individual
outcomes. `critical_exclusion` specifies the critical neighbourhood omitted from
the away-from-critical error summary, while leaving those observations visible
in the plots. `large_core_cutoff` and `onset_cutoffs` control the operational
large-core event and its sensitivity check. The analysis does not import either
simulation notebook and never
starts a graph-generation run. It saves the triangle validation, transition
close-up, individual-outcome diagnostics, and final model comparison under its
configured figure directory, alongside numerical summary tables.

For a new targeted study run `make triangle-study`. To regenerate its figures
after editing the analysis, run `make triangle-figures`. Raw measurements are
protected; a second simulation requires a new output directory or explicit
`overwrite = True`. Missing input is reported as an error, not filled in
implicitly. The source notebooks retain no execution outputs or saved copies.
On a fresh checkout, first generate comparison data with
`make comparison-simulate`; generated measurements are not stored in Git.

The triangle cavity prediction and CM theorem have different mathematical
status. Keep that distinction in explanations and captions. When interpreting
the transition, inspect individual outcomes and empirical quantiles as well as
mean curves. A finite-size cutoff or a smoothed slope marker does not determine
the asymptotic transition type.

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
- Change configuration-model pairing and multiplicity-aware peeling in
  `notebooks/02_algorithms.ipynb`. A loop contributes twice to degree; erasing a
  multigraph is an explicit, separate measurement, not an implicit constructor
  option for theory validation. Keep the class-based graph representation simple.
- Change theory derivations and numerical root selection in
  `notebooks/05_configuration_theory.ipynb`. Select the largest support root and
  retain equation-residual checks and the special treatment of criticality.
- Change the common-condition comparison trials in
  `notebooks/06_configuration_simulation.ipynb` and saved-data figures in
  `notebooks/07_configuration_analysis.ipynb`. Preserve separate graph seeds and
  the pairing between multigraph and erased outcomes.
- Change the triangle support derivation or fixed-point solvers in
  `notebooks/08_triangle_cavity.ipynb`. Keep the joint triangle rule and both the
  branch solver and independent iteration checks. Explain which statements are
  exact on the limiting factor tree and which remain predictions for the finite
  simple graph.
- Change targeted triangle trials in `notebooks/09_triangle_refinement.ipynb`
  and the final saved-data comparison in `notebooks/10_triangle_comparison.ipynb`.
  Reuse the broad 06 measurements, preserve independent seeds and protected
  outputs, and identify which observations come from additional refinement.
- Add another notebook for a distinct mathematical question. Reuse definitions
  with `%run`; keep reusable definition notebooks free of experiment side effects.
- Add small correctness tests under `tests/`. Tests execute notebook definitions
  in fresh kernels rather than maintaining separate algorithm implementations.
  Workflow checks replace the cells tagged `parameters` in temporary notebook
  copies and use temporary outputs, leaving research settings and results
  untouched.

`tests/test_configuration_comparison.py` checks exact stub degrees, loop and
parallel-edge peeling, agreement with class-based pruning on small simple
graphs, the theory formulas against independent probability sums, critical-point
tangency, and the physical root. Its fresh-kernel workflow uses temporary
measurements to check parallel replay and saved-data analysis without touching
research results. The tests verify implementation; convergence and scientific
conclusions still need representative simulations and interpretation.

`tests/test_triangle_cavity.py` checks the local triangle rule against explicit
pruning, message probabilities against direct probability sums, and criticality
and maximal root selection using independent calculations. Its fresh-kernel
workflow runs a tiny refinement and comparison in temporary directories,
checking reproducible parallel trials and preservation of raw data and source
notebooks. Research figures and convergence evidence come from the separate
representative runs described in notebook 10.

Manage dependencies through `uv add PACKAGE`, `uv add --dev TOOL`, and
`uv remove PACKAGE`. Commit `pyproject.toml` and `uv.lock` together; never edit
the lockfile manually. To intentionally upgrade one dependency, run
`uv lock --upgrade-package numpy`, then `uv sync --locked`.

Before committing, run `make check`, clear source notebook outputs, and review
the staged diff. Start Codex sessions at the root so `AGENTS.md` is found.
See [report/README.md](../report/README.md) for report conventions.
