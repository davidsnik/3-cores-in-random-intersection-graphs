"""Execute notebook sources in fresh kernels; keep mathematical code in notebooks."""

import csv
import shutil
import sys
from pathlib import Path
from pprint import pformat

import nbformat
import pytest
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = (
    "01_graphs.ipynb",
    "02_algorithms.ipynb",
    "03_triangle_simulation.ipynb",
    "04_triangle_analysis.ipynb",
)


@pytest.fixture
def notebook_project(tmp_path):
    """A tiny isolated project, so tests cannot overwrite research measurements."""
    notebook_dir = tmp_path / "notebooks"
    notebook_dir.mkdir()
    for name in NOTEBOOKS:
        shutil.copy2(ROOT / "notebooks" / name, notebook_dir / name)

    # Change only the editable settings cells in these temporary copies. The
    # mathematical implementations are exactly those used for research runs.
    settings = {
        NOTEBOOKS[2]: {
            "stage": "pilot",
            "seed": 2026,
            "jobs": 2,
            "output_dir": "results/runs/triangle_study",
            "overwrite": False,
            "experiments": {
                stage: {
                    "sizes": [30, 60],
                    "lambda_min": 0.0,
                    "lambda_max": 3.0,
                    "lambda_count": 5,
                    "repeats": 2,
                }
                for stage in ("pilot", "comparison", "refinement")
            },
        },
        NOTEBOOKS[3]: {
            "data_dir": "results/runs/triangle_study",
            "stage": "pilot",
            "figure_dir": "results/figures/triangle_study",
            "smoothing_window": 3,
            "sensitivity_windows": [1, 3, 7],
            "zoom_width": 0.5,
            "histogram_n": None,
            "histogram_lambdas": None,
        },
    }
    for name, config in settings.items():
        path = notebook_dir / name
        notebook = nbformat.read(path, as_version=4)
        parameter_cells = [
            cell
            for cell in notebook.cells
            if "parameters" in cell.metadata.get("tags", [])
        ]
        assert len(parameter_cells) == 1, f"{name} must have one settings cell"
        parameter_cells[0].source = "config = " + pformat(config, sort_dicts=False)
        nbformat.write(notebook, path)
    return tmp_path


def execute_notebook(project, name, assertions="", *, from_root=False):
    """Append test assertions in memory, then run every source cell in order."""
    notebook_dir = project / "notebooks"
    notebook = nbformat.read(notebook_dir / name, as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.execution_count = None
            cell.outputs = []
    if assertions:
        notebook.cells.append(nbformat.v4.new_code_cell(assertions))
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [
        sys.executable,
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ]
    working_dir = project if from_root else notebook_dir
    NotebookClient(
        notebook,
        km=manager,
        timeout=90,
        resources={"metadata": {"path": str(working_dir)}},
    ).execute(cleanup_kc=True)
    return notebook


def test_graph_operations_and_errors(notebook_project):
    execute_notebook(
        notebook_project,
        NOTEBOOKS[0],
        """
import copy
from itertools import combinations
from uuid import UUID
import pytest

left, right = Node(), Node()
assert isinstance(left.id, UUID)
left.join(right)
assert left.degree == right.degree == 1
assert left in right.neighbours and right in left.neighbours
for operation, error in [
    (lambda: left.join(right), ValueError),
    (lambda: left.join(left), ValueError),
    (lambda: left.join("not a node"), TypeError),
]:
    with pytest.raises(error):
        operation()
    assert left.degree == right.degree == 1
    assert left.neighbours == {right} and right.neighbours == {left}
left.unjoin(right)
assert left.degree == right.degree == 0
with pytest.raises(ValueError):
    left.unjoin(right)
with pytest.raises(TypeError):
    left.unjoin(None)
assert not left.neighbours and not right.neighbours

for invalid_size in [-1, 1.5, True]:
    with pytest.raises(ValueError):
        Graph(invalid_size)

graph = Graph(4)
nodes = list(graph.nodes)
for left, right in combinations(nodes, 2):
    graph.add_edge(left, right)
assert len(graph.edges) == 6
assert all(node.degree == 3 for node in graph.nodes)
copied = copy.deepcopy(graph)
assert copied.nodes == graph.nodes
assert all(next(node for node in copied.nodes if node.id == original.id) is not original
           for original in graph.nodes)
copied.remove_node(next(iter(copied.nodes)))
assert len(copied.nodes) == 3 and len(copied.edges) == 3
assert len(graph.nodes) == 4 and len(graph.edges) == 6

def state(graph):
    return (set(graph.nodes), set(graph.edges),
            {node: (node.degree, frozenset(node.neighbours)) for node in graph.nodes})

left, right = nodes[:2]
foreign = Node()
copied_left = next(node for node in copy.deepcopy(graph).nodes if node.id == left.id)
before = state(graph)
for operation, error in [
    (lambda: graph.add_node(left), ValueError),
    (lambda: graph.add_node(None), TypeError),
    (lambda: graph.add_edge(left, left), ValueError),
    (lambda: graph.add_edge(left, right), ValueError),
    (lambda: graph.add_edge(left, foreign), ValueError),
    (lambda: graph.add_edge(left, "not a node"), TypeError),
    (lambda: graph.remove_edge(left, foreign), ValueError),
    (lambda: graph.remove_node(foreign), ValueError),
    (lambda: graph.remove_node(None), TypeError),
    (lambda: graph.remove_node(copied_left), ValueError),
]:
    with pytest.raises(error):
        operation()
    assert state(graph) == before

graph.remove_edge(left, right)
before = state(graph)
with pytest.raises(ValueError):
    graph.remove_edge(left, right)
assert state(graph) == before

standalone = Node()
standalone.join(foreign)
with pytest.raises(ValueError):
    graph.add_node(standalone)
assert standalone not in graph.nodes and state(graph) == before

# Node and Graph operations can be mixed: both keep the owning graph's edge
# set synchronized with its vertices' neighbours and cached degrees.
owned = Graph(2)
left, right = tuple(owned.nodes)
edge = frozenset((left, right))
left.join(right)
assert owned.edges == {edge} and left.degree == right.degree == 1
owned.remove_edge(left, right)
assert not owned.edges and left.degree == right.degree == 0
owned.add_edge(left, right)
left.unjoin(right)
assert not owned.edges and not left.neighbours and not right.neighbours
before = state(owned)
for operation in [lambda: left.unjoin(right), lambda: owned.remove_edge(left, right)]:
    with pytest.raises(ValueError):
        operation()
    assert state(owned) == before

# Removing a node releases it, so an isolated vertex can be added again or
# moved to another graph. It must never belong to both graphs at once.
owned.remove_node(left)
owned.add_node(left)
assert left in owned.nodes
owned.remove_node(left)
other = Graph(1)
other.add_node(left)
neighbour = next(node for node in other.nodes if node is not left)
left.join(neighbour)
assert other.edges == {frozenset((left, neighbour))}
with pytest.raises(ValueError):
    owned.add_node(left)
with pytest.raises(ValueError):
    left.join(right)
assert left not in owned.nodes and other.edges == {frozenset((left, neighbour))}
""",
    )


@pytest.mark.parametrize(
    "from_root", [False, True], ids=["notebook-cwd", "project-cwd"]
)
def test_core_and_community_algorithms(notebook_project, from_root):
    execute_notebook(
        notebook_project,
        NOTEBOOKS[1],
        """
from collections import Counter
from itertools import combinations

def clique(n):
    graph = Graph(n)
    for left, right in combinations(graph.nodes, 2):
        graph.add_edge(left, right)
    return graph

assert not construct_k_core(clique(3), 3).nodes
graph = clique(4)
core = construct_k_core(graph, 3)
assert len(core.nodes) == 4 and len(core.edges) == 6
assert all(node.degree >= 3 for node in core.nodes)
left, right = tuple(next(iter(graph.edges)))
graph.remove_edge(left, right)
assert not construct_k_core(graph, 3).nodes
assert len(graph.nodes) == 4 and len(graph.edges) == 5
assert len(construct_k_core(Graph(3), 0).nodes) == 3

graph = construct_random_intersection_graph(1, 3, lambda n: [3], rng=np.random.default_rng(1))
assert len(graph.nodes) == 1 and not graph.edges
assert len(graph.communities) == 1 and len(set(graph.communities[0])) == 1
counts = Counter(vertex for group in graph.communities for vertex in group)
assert counts == graph.memberships
copied = construct_k_core(graph, 3)
assert copied.memberships == graph.memberships and copied.communities == graph.communities

samples = iter(([1, 0], [2, 1]))
graph = construct_random_intersection_graph(2, 3, lambda n: next(samples), rng=np.random.default_rng(1))
assert sorted(graph.memberships.values()) == [1, 2]
assert len(graph.edges) == 1
empty = construct_special_triangle_RIG(3, 0, rng=np.random.default_rng(1))
assert len(empty.nodes) == 3 and not empty.edges and not empty.communities
""",
        from_root=from_root,
    )


def test_simulation_and_analysis_fresh_kernels(notebook_project):
    source_paths = [notebook_project / "notebooks" / name for name in NOTEBOOKS]
    source_contents = [path.read_bytes() for path in source_paths]
    execute_notebook(
        notebook_project,
        NOTEBOOKS[2],
        """
import pytest

serial = simulate_triangle(30, [0.0, 1.5, 2.0], 2, seed=19, jobs=1)
parallel = simulate_triangle(30, [0.0, 1.5, 2.0], 2, seed=19, jobs=2)
assert serial == parallel
assert len({row["seed"] for row in serial}) == 6
for row in serial:
    assert triangle_trial(row["n"], row["lambda"], row["replicate"], row["seed"]) == row

# Try each study stage with tiny parameters, rather than running research sizes.
for stage in ["comparison", "refinement"]:
    stage_config = config | {"stage": stage, "jobs": 1}
    paths = run_triangle_study(stage_config, project_root=PROJECT_ROOT)
    assert len(paths) == 2 and all(path.exists() for path in paths)

with pytest.raises(FileExistsError):
    run_triangle_study(config, project_root=PROJECT_ROOT)

# A later existing target must stop the whole request before an earlier new
# size is simulated and written. This avoids accidentally starting half a rerun.
guarded = config | {"experiments": config["experiments"] | {
    "pilot": config["experiments"]["pilot"] | {"sizes": [15, 30]}
}}
with pytest.raises(FileExistsError):
    run_triangle_study(guarded, project_root=PROJECT_ROOT)
assert not (PROJECT_ROOT / config["output_dir"] / "pilot_n15.csv").exists()
""",
    )
    data_dir = notebook_project / "results/runs/triangle_study"
    data_files = sorted(data_dir.glob("*.csv"))
    assert len(data_files) == 6
    all_seeds = []
    for data_file in data_files:
        with data_file.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 10
        assert {row["n"] for row in rows} == {data_file.stem.split("_n")[1]}
        assert {row["model"] for row in rows} == {"triangle_rig"}
        assert len({(row["lambda"], row["replicate"]) for row in rows}) == 10
        assert all(
            float(row["core_fraction"]) == int(row["core_size"]) / int(row["n"])
            for row in rows
        )
        assert all(
            int(row["core_size"]) == 0 for row in rows if float(row["lambda"]) == 0
        )
        all_seeds.extend(row["seed"] for row in rows)
    assert len(set(all_seeds)) == len(all_seeds)
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in data_files}
    result = execute_notebook(
        notebook_project,
        NOTEBOOKS[3],
        """
import pytest

assert estimate_transition([0, 1], [0, 1]) is None
assert estimate_transition([0, 1, 2], [0.1, 0.1, 0.1]) is None
sample = [{"n": 10, "lambda": lam, "core_fraction": fraction}
          for lam, fraction in [(2, .6), (0, 0), (1, .2), (2, 1), (0, .2), (1, .6)]]
sample += [{"n": 20, "lambda": 0, "core_fraction": .9}]
grouped = summarize_results(sample)
small = [row for row in grouped if row["n"] == 10]
np.testing.assert_allclose([row["mean"] for row in small], [.1, .4, .8])
np.testing.assert_allclose([row["median"] for row in small], [.1, .4, .8])
np.testing.assert_allclose([row["standard_error"] for row in small], [.1, .2, .2])
assert all(row["trials"] == 2 for row in small)
assert next(row for row in grouped if row["n"] == 20)["standard_error"] is None
assert estimate_transition([0, 1, 2], [.1, .4, .8], window=1) == 1.0

distribution = plot_distributions(sample, n=10, lambdas=[0, 1, 2], smoothing_window=1)
assert len(distribution.axes) == 3
assert all(sum(patch.get_height() for patch in axis.patches) == 2
           for axis in distribution.axes)
with pytest.raises(FileNotFoundError):
    load_study(PROJECT_ROOT / "missing_measurements", "pilot")
""",
    )
    assert {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in data_files
    } == before
    figure_dir = notebook_project / "results/figures/triangle_study"
    for kind in ("comparison", "zoom", "distributions"):
        assert (
            (figure_dir / f"pilot_{kind}.png")
            .read_bytes()
            .startswith(b"\x89PNG\r\n\x1a\n")
        )
    for name in ("summary", "transition_estimates"):
        with (figure_dir / f"pilot_{name}.csv").open(
            newline="", encoding="utf-8"
        ) as stream:
            rows = list(csv.DictReader(stream))
        assert {row["n"] for row in rows} == {"30", "60"}
    assert any(
        "image/png" in output.get("data", {})
        for cell in result.cells
        if cell.cell_type == "code"
        for output in cell.outputs
    )
    assert [path.read_bytes() for path in source_paths] == source_contents
    assert not (notebook_project / "results/notebooks").exists()
