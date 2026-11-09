# Architecture

The project uses notebooks under `notebooks/`, with settings in the
simulation and analysis notebooks.
Each notebook combines its mathematical purpose with the relevant implementation.
There is no separate Python package: shared definitions are loaded directly from
their notebook with IPython's `%run`.

This guide describes the implemented baseline. The agreed finite-size research
question, planned controls, and proposed notebook extensions are in
[research_plan.md](research_plan.md).

## Notebook responsibilities and execution

1. **`01_graphs.ipynb`** defines the `Node` and `Graph` classes, including
   joining/unjoining nodes, adding/removing edges, and graph copying.
2. **`02_algorithms.ipynb`** loads 01 and defines `construct_k_core`,
   `construct_random_intersection_graph`, and `construct_special_triangle_RIG`.
   It also defines configuration-model pairing, simple projection, and
   multiplicity-aware adjacency-list peeling.
3. **`03_triangle_simulation.ipynb`** loads 02, defines pilot, size-comparison, and
   transition-refinement settings, assigns trial seeds, runs the selected stage,
   and saves one CSV per graph size with one row per realization.
4. **`04_triangle_analysis.ipynb`** reads a saved stage, compares graph sizes,
   examines variation near the transition, and saves figures and summary tables.
   It does not load graph classes or rerun simulations.
5. **`05_configuration_theory.ipynb`** derives the configuration-model support
   equation and limiting core density, then defines numerical prediction
   functions. Loading it does not run experiments or save files.
6. **`06_configuration_simulation.ipynb`** loads 02 and 05, samples triangle and
   configuration graphs under common settings, measures cores and graph
   diagnostics, and saves one comparison CSV per graph size.
7. **`07_configuration_analysis.ipynb`** loads 05 and saved comparison CSVs. It
   checks theory against multigraph simulations, compares all three models, and
   saves figures, summaries, and numerical theory values. It never loads 06.
8. **`08_triangle_cavity.ipynb`** derives joint support within a triangle,
   closes the message probabilities using independent incidence-tree branches,
   and defines maximal fixed-point and critical-point solvers. It only defines
   functions and imports dependencies.
9. **`09_triangle_refinement.ipynb`** loads the graph algorithms and adds
   independent seeded triangle trials near the predicted critical point,
   and writes a separate protected CSV per size. It does not rerun 06.
10. **`10_triangle_comparison.ipynb`** loads 05 and 08, reads the existing 06
    measurements and additional 09 trials, and produces the final validation
    and model comparison. It never loads graph generation.

Notebooks 01, 02, 05, and 08 contain imports and definitions only: `%run` makes their
classes and functions available in the calling notebook without starting an
experiment. Execute every notebook top to bottom. A fresh kernel is sufficient;
there is no dependency on previously executed tabs. Path setup supports kernels
started in `notebooks/` or the repository root and makes sibling `%run` calls
resolve consistently. Run Makefile commands from the repository root. They
execute the same notebooks without saving executed copies or modifying sources.

Each experiment notebook has an editable, commented `config` dictionary in a
cell tagged `parameters`. Notebook 03 selects a `stage` and configures its graph
sizes, lambda grid, repeats, master seed, workers, and `output_dir`. Notebook 04
selects a saved `stage` from `data_dir` and configures figure output, smoothing,
and which outcomes to inspect more closely. The default data directory is
`results/runs/triangle_study/`; keep the directories and selected stages aligned.
All output paths are relative to the repository root. Analysis requires saved
data; it never starts a simulation to create it.

Notebook 06 uses a flat comparison configuration: `sizes`, an explicit `lambdas`
list, `repeats`, `seed`, `jobs`, `output_dir`, and `overwrite`. This single set of
conditions applies to every model. Notebook 07 uses `data_dir` and `figure_dir`,
with additional controls for the transition close-up, degree-distribution plot,
and outcome histograms. Its `critical_exclusion` leaves a stated neighbourhood of
the theoretical critical point out of the away-from-critical error summary;
the close-up and raw data still include those measurements. Comparison trials
are written under `results/runs/configuration_comparison/`, with analysis under
`results/figures/configuration_comparison/`.

The stages provide a simple progression: explore the broad range with `pilot`,
compare several increasing sizes with `comparison`, then choose tighter bounds
for `refinement` after looking at the saved results. The default runs only the
pilot. The larger stages are explicit choices and may take substantially longer.
Each stage/size saves a separate file, such as `comparison_n3000.csv`. Before
computing, the simulation checks every selected output path and refuses to
replace existing files unless `overwrite` is enabled. Use another output
directory to retain another version of a study.

## Graph representation and copying

`Node.id` is a UUID used for equality and hashing. `Node.neighbours` is a set of
adjacent node objects, and `Node.degree` caches its size. `join` and `unjoin`
update both endpoints. `Graph.nodes` is a set of nodes, and `Graph.edges` is a set
of two-node `frozenset` objects representing undirected edges.

Use `Graph.add_edge`, `remove_edge`, and `remove_node` to edit a graph so its edge
set, neighbour sets, and cached degrees remain consistent. The graph implements
deep copying by creating new node objects with the same UUIDs, then rebuilding
edges between those copies. Copies are independent graphs while corresponding
vertices retain their identities.

Improper use raises an exception before the operation changes the graph.
Examples include adding an edge twice, joining a node to itself, removing a node
that is absent, or passing something other than a `Node`. A node belongs to at
most one graph. A copied node has the same UUID as its counterpart, but cannot
be used to edit the other graph. `Node.join` and `Node.unjoin` also update the
owning graph's edge set when both vertices belong to that graph. Standalone
nodes can be joined to each other, but connections across different graphs are
rejected.

`construct_k_core(graph, k)` deep-copies the graph and peels vertices whose degree
is below `k`. It returns a `Graph` containing the survivors; the input graph is
unchanged. A neighbour enters the queue when losing an edge takes it below the
threshold. The 3-core fraction is `len(core.nodes) / n`, using the input graph
size, including isolated vertices.

Generated graphs also retain the sampled membership counts, indexed by UUID, and
community tuples containing the sampled UUID slots. These describe graph
generation, including repeated memberships. They are preserved on graph copies
as a record of how the graph was generated, so a core can still refer to
memberships of removed nodes. They do not describe the core as a newly generated
intersection graph.

## Probability and projection conventions

`construct_random_intersection_graph` accepts a membership sampler and a fixed
community size. The triangle wrapper samples one Poisson membership count with
mean lambda for each of the `n` vertices. It rejects the entire count vector
until its sum is divisible by three, then uniformly shuffles the vertex stubs and
groups them into triples. The corresponding general constructor uses community
size `k` and divisibility by `k`.

Repeated vertex UUIDs remain in community slots. Projecting each community to a
clique discards loops and merges repeated edges, producing a simple undirected
graph. Membership counts therefore need not determine projected degrees.
Matching is uniform over stubs conditional on the accepted count vector; the
result is not sampled uniformly from simple graphs.

The triangle wrapper's optional explicit NumPy generator controls Poisson
sampling and stub shuffling. In the general constructor, the caller supplies the
membership sampler and its randomness. UUID creation still uses fresh labels.
A replay seed therefore reproduces the sampled structure up to vertex relabeling
and reproduces its 3-core measurement, rather than its UUID values.

## Configuration-model benchmark

A triangle membership normally gives a vertex two neighbours. With a fixed
membership mean lambda and increasing graph size, repeated vertices and
overlapping neighbours become rare around a uniformly chosen vertex. Its degree
therefore converges to `2 * Poisson(lambda)`, with mean `2 * lambda` and variance
`4 * lambda`. This is a limiting distribution, not an exact identity for the
finite simple triangle graph. The random-sum degree limit in
[van der Hofstad, Komjáthy, and Vadon, Corollary 2.9](https://arxiv.org/pdf/1809.02514)
gives this specialization when each community is a triangle.

The configuration model samples those even degrees independently, creates one
stub per degree, shuffles all stubs, and pairs consecutive entries. Every sampled
sum is even, so there is no parity rejection. This is different from the triangle
model's whole-vector conditioning on a sum divisible by three.

Notebook 02 adds a small integer-index adjacency representation for this
benchmark. An adjacency list retains one entry per incident edge; a self-loop
adds two entries and each parallel edge adds its own entry. This representation
keeps the sampled degrees exactly and allows linear-time queue-based peeling
without changing the simple `Node`/`Graph` classes. `core_mask` marks the vertices
remaining after peeling; it does not mutate the adjacency lists. For simple
graphs its result is checked against `construct_k_core`.

Each pairing also gives a simple projection by removing loops and merging
parallel edges. The three model labels mean:

| Saved label | Graph used for its core |
| --- | --- |
| `triangle_rig` | The simple projection of triangle communities. |
| `cm_multigraph` | The configuration model retaining every matched edge. |
| `cm_erased` | The same configuration pairings with loops and repeated edges removed. |

The two configuration measurements from a trial are paired observations. They
are not independent replications. The retained multigraph is the direct check of
theory; the erased version checks whether the edge convention noticeably affects
the finite-size comparison. Erasing edges changes finite degrees and may matter
near a transition even when relatively few edges are removed. Clustering is
measured on simple projections for all three labels, so the two configuration
labels share that diagnostic. The stored loop and parallel-edge counts refer to
the original pairings; `parallel_excess` counts repeated non-loop edges beyond
the first copy.

Matching the limiting degree law makes this a useful comparison, but the models
also differ in degree correlations and community dependence. Observed differences
therefore cannot automatically be attributed to clustering alone. Saved degree
moments, odd-degree frequencies, and simple-projection clustering help check the
comparison instead of assuming that finite graphs have identical degrees.

## Configuration-model prediction

Let `x` be the probability that the vertex reached along an edge can support the
other endpoint: it needs at least two other supporting edges to remain in a
3-core. The configuration model is locally tree-like in the sparse limit, so
these other branches are asymptotically independent. The reached degree is
size-biased, giving

\[
x = \frac{\mathbb E[K\,\mathbb P(\operatorname{Bin}(K-1,x)\ge2\mid K)]}
              {\mathbb E[K]},
\qquad
\rho = \mathbb P(\operatorname{Bin}(K,x)\ge3).
\]

Notebook 05 derives closed forms using the generating function
`G_0(z) = exp(lambda * (z*z - 1))`. It selects the **largest** support-equation
root, as obtained by pruning from full initial support. The zero root always
exists and would otherwise hide the physical positive branch.

[Janson and Łuczak, Theorem 2.3](https://arxiv.org/pdf/math/0508453) supplies the
configuration-model law of large numbers under degree regularity and a crossing
condition. The notebook connects its notation to the support equation and checks
the degree-law assumptions. For the even-Poisson family, the positive branch first
appears at a tangency near `lambda = 1.28772037045`, with a limiting right-hand
core fraction near `0.13788881228`. This predicts a discontinuous transition.
The theorem's usual crossing condition does not hold at the tangency itself;
the plotted positive critical value is a right-hand branch limit, not a
deterministic prediction for a finite graph at exactly critical lambda.

The numerical solver brackets roots and checks equation residuals. Tests also
evaluate the defining Poisson/binomial sums independently, check tangency, and
compare supercritical roots with repeated pruning from full support. No
configuration-model formula is used as a theoretical prediction for the triangle
graph.

## Triangle cavity prediction

The simple graph is made from triangle communities. Its incidence graph has a
vertex for each individual and a factor for each triangle. For fixed positive
lambda and increasing size, a uniformly chosen individual sees independent
Poisson(lambda) descendant triangle branches in the local limit. An incident
triangle still contains two linked neighbours; independence is used between
distinct factor branches, never between those two neighbours.

Notebook 08 resolves this local triangle exactly. Conditional on the target
vertex remaining available, its other two vertices can jointly supply zero,
one, or two neighbours. The maximal local state accounts for the edge joining
them. Poisson thinning then gives the distribution of support arriving from
the target's other triangles, closing a two-probability message map. The target
belongs to the ordinary graph 3-core when its total support is at least three.
This differs from requiring three complete hyperedges in a hypergraph core.

The physical solution is obtained from full initial support. A separate scalar
parameterization of nonzero fixed points allows bracketed critical-point and
upper-branch calculations, avoiding arbitrarily slow fixed-point convergence
near a tangency. The full two-dimensional iteration remains available as an
independent numerical check. The critical core fraction is the positive
branch's limiting value, with the same finite-size caution as the CM prediction.

The local equations are exact on the limiting triangle factor tree. Predicting
the terminal core of this finite simple-graph ensemble also requires passing
from finite pruning depth to infinite pruning depth and controlling the simple
projection and global correlations. The notebook states that step as a cavity
prediction rather than citing the CM theorem as proof for triangles.

Notebook 09 refines only the triangle transition region. It reuses the existing
triangle constructor and adjacency-list peeling, assigns independent seeds
before parallel dispatch, and writes the same seven basic measurement fields
as the triangle study in 03. Its `cavity_refinement_n<size>.csv` files live in a
separate directory so they supplement rather than replace the broad comparison.
The full saved comparison from 06 continues to supply both models at matching
sizes, lambda values, and repeat counts.

Notebook 10 reads these datasets independently of simulation. A refinement point
is additional triangle evidence; it must not be drawn as a new matched CM
experiment. Means, empirical quantiles, and standard errors refer to different
questions: the first summarizes the ensemble, the second describes variation
between graphs, and the third estimates uncertainty in the mean. Near a
discontinuous transition the individual-outcome plots and probability of a
substantial core help distinguish a mixture of small and large outcomes from a
single intermediate-sized outcome. Any cutoff-defined onset remains a
finite-size operational summary, not a theorem or confidence interval for the
asymptotic critical parameter.

## Measurements and interpretation

The triangle-only study's measurement dictionaries and CSV rows contain
`model, n, lambda, replicate, seed, core_size, core_fraction`. Trial seeds are
assigned before optional parallel execution, so worker count does not change
measurements. Study stages and graph sizes have separate seed streams. The
parallel work consists of independent trials, with no nested parallel loops.
Changing grid order or repeat count can change which seed is assigned to a
parameter/replicate pair. Record the configuration and code version with any
research results you retain; each saved row also contains its replay seed.

The configuration comparison retains the same core measurements and adds
`trial_seed`, nominal and observed degree means, degree variance, the fraction of
vertices with odd degree, simple-projection transitivity, loop and repeated-edge
counts, and a degree histogram. The histogram is a JSON list inside its CSV
field: entry `k` counts vertices of degree `k`. This keeps the full measured
distribution available without saving graph objects.

Each comparison trial seed creates separate triangle and configuration streams.
The saved `seed` identifies the graph stream; `trial_seed` replays the complete
three-row trial. Both configuration rows share their pairing seed. Trial seeds
are assigned before dispatch; size streams are separate and worker count does
not affect results. Repeats are independent; the two configuration conventions
within a repeat are paired and must not be treated as independent samples.

The comparison analysis saves unsmoothed core curves, a theoretical-transition
close-up, outcome histograms, degree/clustering checks, and a paired check of
erasing loops and repeated edges. Error summaries compare configuration-model
means with the infinite-size prediction outside a configurable critical
neighbourhood. These finite-size errors need not decrease monotonically with
size in a finite experiment; show the actual values and uncertainty rather than
enforcing convergence. Notebook 07 retains this initial empirical triangle
comparison; notebook 10 adds the separately derived triangle cavity overlay.

An additional onset table brackets the first sampled lambda where at least half
the graphs retain a specified positive fraction of their vertices. The
`large_core_cutoff` and the parameter grid define this operational summary. It
is not a confidence interval or either model's asymptotic critical value; with a
continuous transition, a fixed positive cutoff would move it above the true
onset. The CM critical point is obtained separately from its support equation.

Analysis groups measurements by graph size and lambda. The comparison figure
shows how mean core fractions and variation change with size. A closer plot
focuses on the estimated transition, and histograms show whether averages hide a
mixture of individual graphs with small and substantial cores. These describe
variation between graphs. The summary table also reports the standard error of
each mean, estimated from independent trials; it is unavailable for a single
trial.

The maximum-slope marker uses a smoothed mean and is an exploratory finite-size
heuristic. A second table compares several smoothing windows and both the
available grid and a coarser subset. It records when too few points or a flat
curve make the marker unavailable. The marker depends on graph size, grid, and
smoothing; it does not establish a theoretical critical value or decide the
order of the transition. Use the plots and their trial variability to explain
what the finite-size evidence suggests and what remains uncertain.

Generated CSVs live under `results/runs/` and exploratory figures under
`results/figures/`, alongside analysis summary CSVs; both are ignored by Git.
Selected report figures and future
LaTeX source belong in `report/`.
