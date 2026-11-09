# Architecture

The project uses four notebooks under `notebooks/`, with settings in the
simulation and analysis notebooks.
Each notebook combines its mathematical purpose with the relevant implementation.
There is no separate Python package: shared definitions are loaded directly from
their notebook with IPython's `%run`.

## Notebook responsibilities and execution

1. **`01_graphs.ipynb`** defines the `Node` and `Graph` classes, including
   joining/unjoining nodes, adding/removing edges, and graph copying.
2. **`02_algorithms.ipynb`** loads 01 and defines `construct_k_core`,
   `construct_random_intersection_graph`, and `construct_special_triangle_RIG`.
3. **`03_triangle_simulation.ipynb`** loads 02, defines its experiment settings,
   assigns trial seeds, runs the sweep, and saves one CSV row per realization.
4. **`04_triangle_analysis.ipynb`** reads those saved rows, computes summaries,
   estimates a slope marker, and saves the figure. It does not load graph classes
   or rerun simulations.

The first two notebooks contain imports and definitions only: `%run` makes their
classes and functions available in the calling notebook without starting an
experiment. Execute every notebook top to bottom. A fresh kernel is sufficient;
there is no dependency on previously executed tabs. Path setup supports kernels
started in `notebooks/` or the repository root and makes sibling `%run` calls
resolve consistently. Run Makefile commands from the repository root. They
execute the same notebooks without saving executed copies or modifying sources.

Each experiment notebook has an editable, commented `config` dictionary in a
cell tagged `parameters`. Notebook 03 configures graph size, the lambda grid,
repeats, seed, workers, and the CSV path. Notebook 04 configures its CSV input,
figure output, and smoothing. Keep `data_file` aligned between these notebooks;
both default to `results/runs/triangle_transition.csv`. All output paths are
relative to the repository root. Analysis requires an existing CSV; it never
starts a simulation to create one.

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

## Measurements and interpretation

Each measurement dictionary and CSV row contains
`model, n, lambda, replicate, seed, core_size, core_fraction`. Trial seeds are
assigned before optional parallel execution, so worker count does not change
measurements. Changing grid order or repeat count can change which seed is
assigned to a parameter/replicate pair. Record the configuration with any research
results you retain.

Analysis groups one graph size by lambda and plots means, medians, full ranges,
and interquartile ranges. Bands show variation between realizations; they are
not confidence intervals for the mean. The maximum-slope marker uses a smoothed
mean and is an exploratory finite-size heuristic. It depends on graph size,
parameter grid, and smoothing, and is separate from future theoretical
predictions.

Generated CSVs live under `results/runs/` and exploratory figures under
`results/figures/`; both are ignored by Git. Selected report figures and future
LaTeX source belong in `report/`.
