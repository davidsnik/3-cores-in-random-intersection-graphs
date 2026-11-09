# 3-cores in random intersection graphs

WI4465 Advanced Topics in Probability course project: study how clustering
affects the 3-core phase transition. The assignment is in
`3-core-random-intersection-graphs.pdf`. The notebooks study the triangle model
and compare it with a configuration model. Both models have a mathematical
prediction and numerical validation; the triangle calculation retains the
dependence between neighbours in the same triangle.

## Start here

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and GNU Make,
then run these commands from the repository root:

```bash
make setup
make check
```

Open the root folder in VS Code and select `.venv/bin/python` as both the Python
interpreter and the notebook kernel. The implementation and its mathematical
explanation live together in the notebooks:

| Notebook | What it contains |
| --- | --- |
| [01_graphs.ipynb](notebooks/01_graphs.ipynb) | How `Node` and `Graph` represent vertices, neighbours, degrees, and edges, and how to copy a graph. |
| [02_algorithms.ipynb](notebooks/02_algorithms.ipynb) | Core pruning, random intersection graphs from fixed-size communities, and configuration-model pairing with explicit multigraph conventions. |
| [03_triangle_simulation.ipynb](notebooks/03_triangle_simulation.ipynb) | A pilot run, comparisons across graph sizes, and closer experiments near the transition, with seeded parallel trials and CSV measurements. |
| [04_triangle_analysis.ipynb](notebooks/04_triangle_analysis.ipynb) | Comparing graph sizes, inspecting individual outcomes near the transition, and checking the sensitivity of the slope marker. |
| [05_configuration_theory.ipynb](notebooks/05_configuration_theory.ipynb) | Why neighbours support each other in the 3-core; deriving the configuration-model equation, core density, and discontinuous transition. |
| [06_configuration_simulation.ipynb](notebooks/06_configuration_simulation.ipynb) | Parallel triangle and configuration-model simulations with the same sizes, lambda values, and repeat counts, plus degree and clustering checks. |
| [07_configuration_analysis.ipynb](notebooks/07_configuration_analysis.ipynb) | Validating configuration-model theory, comparing all models, and examining finite-size and graph-convention effects from saved measurements. |
| [08_triangle_cavity.ipynb](notebooks/08_triangle_cavity.ipynb) | Deriving triangle support messages, solving the maximal cavity fixed point, and locating the predicted transition. |
| [09_triangle_refinement.ipynb](notebooks/09_triangle_refinement.ipynb) | Additional seeded triangle trials concentrated near the cavity prediction, reusing the graph sampler and core algorithm. |
| [10_triangle_comparison.ipynb](notebooks/10_triangle_comparison.ipynb) | Validating the triangle prediction against saved broad and refined trials, then comparing both models and their transitions. |

Read the notebooks in that order. Each notebook runs from top to bottom in a
fresh kernel: notebook 02 loads definitions from 01 with `%run`, and notebook 03
loads 02. Notebooks 01 and 02 only define classes and functions, so loading them
does not start simulations. Notebook 04 reads saved CSV independently of those
definitions. Notebook 05 contains theory definitions only. Notebook 06 loads 02
and 05 to generate the comparison; notebook 07 loads only 05 and reads saved measurements,
so changing a plot never generates another graph. Notebook 08 contains triangle
theory definitions only. Notebook 09 generates the targeted additional data;
notebook 10 loads both theory notebooks and saved measurements, without loading
graph construction or simulation.

Notebooks 03 and 04 each have a commented `config` dictionary. Start
with `stage = "pilot"` in notebook 03 to explore a broad range of membership means and
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

## Configuration-model comparison

Read notebook 05 before running the comparison. It derives the prediction for a
configuration model with degree `2 * Poisson(lambda)`. This matches the triangle
model's limiting degree distribution: every triangle membership usually adds two
neighbours. Finite triangle graphs can lose neighbours when memberships overlap,
so notebook 06 also measures the actual degree distribution rather than assuming
an exact match.

```bash
make theory               # Load the theory definitions in a fresh kernel
make comparison           # Run 06, then analyze its CSVs in 07
make comparison-simulate  # Run only the comparison trials
make comparison-figures   # Analyze existing comparison trials without simulating
```

Notebook 06's `config` selects graph sizes, a common list of lambda values,
independent repeats, a master seed, and workers. Its default includes
`n = 1000, 3000, 10000` and 60 repeats at each lambda. It is a research run, so
reduce sizes and repeats for a quick exploration. Trials run in parallel; use
`jobs = 1` to run sequentially. Keep notebook 07's `data_dir` aligned with
notebook 06's `output_dir`. Raw trial CSVs go into
`results/runs/configuration_comparison/`; figures and summary tables go into
`results/figures/configuration_comparison/`. Existing trial files are protected:
use the figures command to inspect them again, choose another output directory
to keep a second experiment, or explicitly enable `overwrite` to replace them.

Three labels appear in the results. `triangle_rig` is the simple triangle graph.
`cm_multigraph` retains configuration-model loops and parallel edges, preserving
its sampled degrees exactly; a loop counts twice toward degree. `cm_erased`
removes loops and merges repeated edges from the **same pairings**, checking the
effect of using a simple graph. These two configuration measurements are paired
observations, not twice as many independent trials. Clustering is measured on
simple projections in every case.

The theory predicts a jump at approximately `lambda = 1.28772`, from zero to a
right-hand core fraction of approximately `0.13789`. Notebook 07 compares that
prediction with the retained multigraph at increasing sizes and shows trial
variation without smoothing the measurements. At the critical point itself,
the plotted positive value represents the branch limit; finite graphs need not
have that deterministic fraction. Notebook 07's triangle comparison is empirical;
notebooks 08–10 supply and validate a separate triangle cavity prediction.
The models differ in community dependence and degree correlations as well as
clustering, so observed differences should be interpreted accordingly.

The default study was run at all three sizes with 60 repeats per lambda and
seed `20261109`. Outside the stated exclusion band of width `0.08` on either
side of the CM critical value, the root mean squared differences between CM
multigraph means and theory were approximately `0.00743`, `0.00208`, and
`0.000732` for `n = 1000, 3000, 10000`. This run supports the predicted
large-size behaviour; it does not establish a convergence rate. The triangle
graph's descriptive 5%-core event became common earlier on this grid. Notebook
07 records and interprets the findings, including the finite-size and cutoff
limitations. These observations refer to the saved default run, not every
configuration a reader may choose later.

## Triangle cavity study and final comparison

Read notebook 08 for the triangle derivation. A vertex-to-triangle message
records support from its other incident triangles, with the receiving triangle
excluded. The two other vertices of that triangle are then resolved jointly,
giving a triangle-to-vertex message of zero, one, or two supporting neighbours.
Treating its two edges as independent would lose the dependence that distinguishes
this model from a locally tree-like graph. These are
messages for the ordinary graph 3-core, not a hypergraph-core definition.

The calculation uses the locally tree-like limit of the triangle incidence
graph, retaining the cycle inside each triangle. It predicts the maximal
fixed point reached by pruning from full support. Passing from that infinite
factor-graph calculation to the terminal core of the finite simple graph is
stated as a cavity prediction, separately from the established
configuration-model theorem.

| Prediction | Critical membership mean | Right-hand core fraction | Transition |
| --- | ---: | ---: | --- |
| Triangle cavity calculation | 1.22860 | 0.08111 | Discontinuous |
| Configuration model | 1.28772 | 0.13789 | Discontinuous |

The triangle calculation therefore predicts an earlier onset with a smaller
jump. These are limiting branch values; graphs at either critical parameter
need not retain that deterministic fraction of their vertices.

```bash
make triangle-theory   # Execute 08; no simulation or saved outputs
make triangle-refine   # Run only the additional near-transition triangle trials
make triangle-figures  # Analyze saved 06 and 09 data; never regenerate graphs
make triangle-study    # Execute 09, then 10, in that order
```

Notebook 06's existing three-size comparison is reused. Notebook 09 adds only a
finer triangle grid around the predicted transition, with its own settings and
protected output directory, `results/runs/triangle_cavity/`. Notebook 10 writes
its figures and summary tables to `results/figures/triangle_cavity/`. Choose a
new directory to retain another refinement run, and match the input setting in
notebook 10. Running `make triangle-study`
again encounters the saved-measurement guard; use `make triangle-figures` to
regenerate figures and tables from an existing study.

On a fresh checkout without saved data, run `make comparison-simulate` once
first; reduce notebook 06's settings for a quick exploration. Saved research
measurements are ignored by Git and are not downloaded with the source.

Notebook 10 compares empirical means with cavity predictions, separates trial
variation from uncertainty in the mean, and shows individual outcomes near the
transition. It also compares the models' predicted thresholds and jump sizes,
checks agreement away from each critical window, and discusses the finite-size
limitations. Degree matching controls a limiting marginal distribution; it does
not isolate clustering from all community and degree correlations.

The default refinement was run on 4,000 additional graphs: ten lambda values,
100 repeats, and sizes `1000, 3000, 10000, 30000`. On the reused broad grid,
the triangle mean's root mean squared difference from its cavity prediction was
approximately `0.0197`, `0.0132`, and `0.00307` for the first three sizes,
excluding points within `0.025` of its predicted threshold. These are measured
finite-size errors from the saved default run, rather than an established
convergence rate. Notebook 10 examines the critical region separately.

See [development.md](docs/development.md) for setup and modification commands,
[architecture.md](docs/architecture.md) for graph and probability conventions,
and [report/README.md](report/README.md) for the future report layout.
