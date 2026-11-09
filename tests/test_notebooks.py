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
            "n": 60,
            "repeats": 2,
            "lambda_min": 0.7,
            "lambda_max": 2.5,
            "lambda_count": 5,
            "seed": 2026,
            "jobs": 2,
            "data_file": "results/runs/trials.csv",
        },
        NOTEBOOKS[3]: {
            "data_file": "results/runs/trials.csv",
            "figure_file": "results/figures/transition.png",
            "smoothing_window": 3,
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


def test_original_graph_classes(notebook_project):
    execute_notebook(
        notebook_project,
        NOTEBOOKS[0],
        """
import copy
from itertools import combinations
from uuid import UUID

left, right = Node(), Node()
assert isinstance(left.id, UUID)
left.join(right)
assert left.degree == right.degree == 1
assert left in right.neighbours and right in left.neighbours
left.unjoin(right)
assert left.degree == right.degree == 0

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
""",
    )


@pytest.mark.parametrize(
    "from_root", [False, True], ids=["notebook-cwd", "project-cwd"]
)
def test_original_algorithms(notebook_project, from_root):
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
serial = simulate_triangle(30, [0.0, 1.5, 2.0], 2, seed=19, jobs=1)
parallel = simulate_triangle(30, [0.0, 1.5, 2.0], 2, seed=19, jobs=2)
assert serial == parallel
assert len({row["seed"] for row in serial}) == 6
for row in serial:
    assert triangle_trial(row["n"], row["lambda"], row["replicate"], row["seed"]) == row
""",
    )
    data_file = notebook_project / "results/runs/trials.csv"
    with data_file.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 10
    assert {row["n"] for row in rows} == {"60"}
    before = data_file.read_bytes(), data_file.stat().st_mtime_ns
    result = execute_notebook(
        notebook_project,
        NOTEBOOKS[3],
        """
assert estimate_transition([0, 1], [0, 1]) is None
assert estimate_transition([0, 1, 2], [0.1, 0.1, 0.1]) is None
sample = [{"n": 10, "lambda": lam, "core_fraction": fraction}
          for lam, fraction in [(2, .6), (0, 0), (1, .2), (2, 1), (0, .2), (1, .6)]]
figure, estimate = plot_results(sample, smoothing_window=1)
lines = {line.get_label(): line for line in figure.axes[0].lines}
np.testing.assert_allclose(lines["Mean"].get_ydata(), [.1, .4, .8])
np.testing.assert_allclose(lines["Median"].get_ydata(), [.1, .4, .8])
assert estimate == 1.0
""",
    )
    assert (data_file.read_bytes(), data_file.stat().st_mtime_ns) == before
    assert (
        (notebook_project / "results/figures/transition.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )
    assert any(
        "image/png" in output.get("data", {})
        for cell in result.cells
        if cell.cell_type == "code"
        for output in cell.outputs
    )
    assert [path.read_bytes() for path in source_paths] == source_contents
    assert not (notebook_project / "results/notebooks").exists()
