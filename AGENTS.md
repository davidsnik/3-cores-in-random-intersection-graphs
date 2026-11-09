# Project guidance

This WI4465 Advanced Topics in Probability project studies the 3-core transition
in random intersection graphs. The root assignment PDF defines the scope.
The selected direction is finite-size scaling and fluctuations near the
discontinuous 3-core transition in Poisson triangle-community graphs, using a
degree-matched configuration model (CM) as the benchmark.
Baseline simulation and comparison are implemented: CM theory is in notebook 05;
triangle cavity equations and baseline validation are in notebooks 08–10.
The additional finite-size investigation is planned, not implemented.

## Agreed research direction

[docs/research_plan.md](docs/research_plan.md) is the canonical research question,
methodology, completed/planned inventory, and next-pilot roadmap. The connected
aims are survival-window scaling (test `n^{-1/2}`), conditional density
fluctuations (test `n^{-1/4}`), and prediction of full conditional distributions
from theory plus survival-only calibration. The approximation may fail; a
careful account of its failure is a useful scientific result.

- Derive critical densities and density-fold amplitudes from theory. Fit
  occurrence parameters only to survival indicators; never fit the target
  conditional density's location, amplitude, or spread. Split future validation
  by complete membership vector and propagate calibration uncertainty.
- Existing 06 uses independent model streams at common settings. Future shared
  membership-vector controls match CM nominal degrees `2D`, not the triangle
  projection's actual degrees. Same-vector pairing needs common physical lambda;
  model-specific critical grids generally use different physical parameters.
- Repeated matchings sharing a vector are clusters, not independent trials.
  Plan sufficient positive outcomes, appropriate uncertainty, and absolute as
  well as jump-relative cutoffs before the new campaign.
- Distinguish CM theorems, exact local motif calculations, the triangle
  terminal-core cavity assumption, and finite-size hypotheses. The existing
  triangle message-coordinate fold is derived; density amplitudes, CM
  fluctuation-theorem specialization, and held-out tests still need work.
- The report has seven main sections: motivation; models; critical predictions;
  numerical methodology; results by question; discussion; conclusion. Preserve
  the single-author IEEEtran style. Keep this stage a writing roadmap rather
  than complete scientific prose. See [report/README.md](report/README.md).

## Start here

- `notebooks/01_graphs.ipynb`: `Node` and `Graph` classes for vertices and undirected graphs.
- `notebooks/02_algorithms.ipynb`: `construct_k_core`,
  `construct_random_intersection_graph`, `construct_special_triangle_RIG`, and
  configuration-model pairing and adjacency-list peeling helpers.
- `notebooks/03_triangle_simulation.ipynb`: seeded, parallel pilot, size-comparison,
  and transition-refinement experiments; edit its `config` dictionary to choose
  the stage and simulation settings.
- `notebooks/04_triangle_analysis.ipynb`: independent saved-data analysis and
  figures; edit its `config` dictionary to choose input, output, and smoothing.
- `notebooks/05_configuration_theory.ipynb`: the configuration-model support
  equation, core density, critical point, and numerical prediction functions.
- `notebooks/06_configuration_simulation.ipynb`: parallel triangle and
  configuration-model trials under the same experimental conditions, retaining
  both multigraph and erased-simple measurements and degree diagnostics.
- `notebooks/07_configuration_analysis.ipynb`: saved-data comparison with theory,
  finite-size diagnostics, model differences, and figures; no graph generation.
- `notebooks/08_triangle_cavity.ipynb`: triangle cavity messages, joint support
  within a motif, maximal fixed points, criticality, and numerical predictions.
- `notebooks/09_triangle_refinement.ipynb`: reproducible additional triangle
  trials near the predicted threshold, reusing the graph/simulation algorithms.
- `notebooks/10_triangle_comparison.ipynb`: saved-data validation of the triangle
  prediction and final comparison of both models, with scientific interpretation.
- `report/main.tex`: the two-column LaTeX paper scaffold; front matter lives here,
  with shared formatting in `preamble.tex`, body files in `sections/`, selected
  figures in `figures/`, and bibliography entries in `references/refs.bib`.
- [report/README.md](report/README.md): report build and writing conventions.
- [docs/research_plan.md](docs/research_plan.md): current aims and planned pilot.
- [docs/architecture.md](docs/architecture.md): data and mathematical conventions.
- [docs/development.md](docs/development.md): setup, commands, and editor workflow.

## Commands

```sh
make setup     # Synchronize .venv from uv.lock (alias: make sync)
make check     # Ruff checks and tests, including fresh-kernel notebook execution
make smoke     # Tiny simulation and analysis with temporary outputs
make run       # Execute simulation, then analysis
make simulate  # Run the selected stage; protect existing CSVs unless overwrite is enabled
make figures   # Analyze a saved stage; run make simulate first if data is missing
make comparison           # Execute 06, then analyze its saved data in 07
make comparison-simulate  # Run matched-condition triangle and configuration trials
make comparison-figures   # Regenerate comparison plots without simulating
make theory               # Execute 05, which defines theory without saving files
make triangle-theory      # Execute the definitions-only triangle theory in 08
make triangle-refine      # Run additional triangle trials near the prediction
make triangle-figures     # Analyze saved 06/09 data against both predictions
make triangle-study       # Execute 09, then 10; existing measurements are protected
make report               # Build report/build/main.pdf without running notebooks
make report-full          # Run existing baseline studies, then build the report
make report-clean         # Remove generated report build files
```

## Changes

- Keep mathematical explanations and implementations together in the notebooks.
  Preserve the class-based graph representation and existing algorithms
  unless a concrete correctness or usability need justifies a change. Do not
  duplicate domain implementations in Python modules or test files.
- Write explanations for a reader who is new to the project. Explain what the
  code does and why, introduce technical terms, and use plain language. Avoid
  references to earlier implementations or conversations as explanations.
- Reuse notebook definitions with `%run`: 02 loads 01, and 03 loads 02.
  Notebook 06 loads 02 and 05; notebook 07 loads only 05.
  Notebook 10 loads only the two theory notebooks, 05 and 08.
  Notebooks 01, 02, 05, and 08 must only define classes/functions and import dependencies;
  loading them must not simulate, plot, or write files. Keep analysis independent
  of graph construction so saved measurements can be plotted in a fresh kernel.
- Keep notebooks executable from top to bottom. Clear source outputs before
  committing; command-line execution neither saves notebook copies nor changes
  source outputs. Notebook path setup supports kernels started in `notebooks/`
  or the repository root; output paths are relative to the repository root.
- Keep experiment settings in the relevant notebook's commented `config`
  dictionary, in its cell tagged `parameters`. Keep the simulation `output_dir`
  and analysis `data_dir` aligned. For notebooks 03 and 04, select the same
  `stage`, keep the default a manageable pilot, and choose refinement bounds
  from observed data.
  Notebook 06 has one flat comparison configuration with `sizes`, `lambdas`,
  `repeats`, and seed/worker/output settings; notebook 07 reads those saved CSVs.
  Notebook 09 adds a targeted triangle grid; notebook 10 reuses the saved 06
  comparison and the separate 09 refinement, without duplicating the broad run.
  Protect existing measurements unless `overwrite` is explicitly enabled.
  Analysis must report missing data rather than
  starting a simulation implicitly.
- Pass explicit NumPy generators and assign trial seeds before parallel dispatch.
  Seeds reproduce membership sampling, matching, and measurements; UUID labels
  are intentionally not reproducible. Save replay parameters with measurements.
- Retain sampled community slots and membership counts on generated graphs and
  their copies as a record of how they were generated. Preserve full-vector
  divisibility conditioning and simple-graph projection. Core construction must
  leave its input unchanged. Distinguish measurements, heuristics, and theory.
- For the configuration-model benchmark sample degrees as twice a Poisson
  variable with mean lambda. Retain loops (degree two) and parallel edges in the
  multigraph used to validate theory; compare its erased simple projection from
  the same pairings as a separate control. Never silently substitute a simple
  graph and claim its finite degrees still equal the sampled degrees. Compute
  clustering on simple projections and state that convention.
- Select the largest support-equation root. The prediction at the critical
  parameter is the positive branch's right-hand limit, not a deterministic
  finite-size claim at the critical point. Keep theoretical CM predictions
  separate from empirical triangle transition estimates. Matching limiting
  degree distributions does not isolate clustering from every other correlation.
- In triangle cavity calculations, resolve the two neighbours within a triangle
  jointly; only distinct branches of the incidence graph are independent in the
  local limit. The equations describe the ordinary graph 3-core. Distinguish the
  exact local calculation from assumptions needed to predict the finite graph's
  terminal core; do not present the triangle cavity argument as a proved theorem.
  Show individual outcomes near criticality: averaging small and substantial
  cores can conceal a predicted discontinuous transition.
- Invalid graph operations must raise informative errors before changing state;
  do not print a message and continue. Keep edge sets, neighbour sets, cached
  degrees, and graph ownership consistent.
- Add meaningful small tests for changed behavior; run `make check`. Tests load
  notebook implementations in fresh kernels. Workflow tests use tiny settings
  and temporary outputs, leaving research measurements untouched.
- Use `uv add`, `uv add --dev`, and `uv remove` for dependencies; commit
  `pyproject.toml` and `uv.lock` together. Do not edit the lockfile by hand. This
  is a notebook project, with no installable Python package or build target.
- Update relevant short guides when behavior changes. Preserve the assignment
  PDF. Keep `.venv`, generated results, caches, and builds out of Git.
- Future finite-size collection/analysis notebooks are proposed in the research
  plan; they do not exist yet. Existing make targets do not run that future pilot.
