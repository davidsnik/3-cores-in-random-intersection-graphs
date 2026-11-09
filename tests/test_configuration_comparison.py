"""Check the configuration-model conventions, theory, and saved-data workflow."""

import csv
import json
import shutil
from pprint import pformat

import nbformat
import pytest
from test_notebooks import ROOT, execute_notebook


@pytest.fixture
def comparison_project(tmp_path):
    """Copy notebook sources so checks cannot replace research measurements."""
    notebook_dir = tmp_path / "notebooks"
    notebook_dir.mkdir()
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        shutil.copy2(path, notebook_dir / path.name)
    settings = {
        "06_configuration_simulation.ipynb": {
            "sizes": [40, 80],
            "lambdas": [0.0, 1.15, 1.5, 2.2],
            "repeats": 3,
            "seed": 20261109,
            "jobs": 2,
            "output_dir": "results/runs/configuration_comparison",
            "overwrite": False,
        },
        "07_configuration_analysis.ipynb": {
            "data_dir": "results/runs/configuration_comparison",
            "figure_dir": "results/figures/configuration_comparison",
            "focus_half_width": 0.25,
            "degree_lambda": 1.5,
            "histogram_n": None,
            "histogram_lambdas": [0.0, 1.15, 1.5],
            "critical_exclusion": 0.08,
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


def test_configuration_graph_conventions(comparison_project):
    execute_notebook(
        comparison_project,
        "02_algorithms.ipynb",
        """
from itertools import combinations
import pytest

# A loop contributes two to degree, and parallel edges retain their multiplicity.
edges = [(0, 0), (0, 1), (0, 1), (1, 1)]
adjacency = configuration_adjacency(3, edges)
assert adjacency == [[0, 0, 1, 1], [0, 0, 1, 1], []]
before = [neighbours.copy() for neighbours in adjacency]
np.testing.assert_array_equal(core_mask(adjacency, 3), [True, True, False])
assert adjacency == before
erased = configuration_adjacency(3, edges, erase=True)
assert erased == [[1], [0], []]
assert not core_mask(erased, 3).any()

# A loop alone has degree two and is removed from a 3-core. Removing a vertex
# joined by repeated edges must remove every copy of that connection.
assert not core_mask(configuration_adjacency(1, [(0, 0)]), 3).any()
assert not core_mask(configuration_adjacency(2, [(0, 0), (0, 1)]), 3).any()
assert not core_mask(configuration_adjacency(2, [(0, 1)] * 2), 3).any()
assert core_mask(configuration_adjacency(2, [(0, 1)] * 3), 3).all()
assert core_mask([[], []], 0).all()

degrees = np.array([0, 2, 4, 6, 8])
model = construct_configuration_model(degrees, rng=np.random.default_rng(17))
np.testing.assert_array_equal([len(row) for row in model["adjacency"]], degrees)
np.testing.assert_array_equal(model["sampled_degrees"], degrees)
assert len(model["edges"]) == degrees.sum() // 2
assert sum(len(row) for row in model["simple_adjacency"]) <= degrees.sum()
for vertex, neighbours in enumerate(model["simple_adjacency"]):
    assert vertex not in neighbours and len(neighbours) == len(set(neighbours))
    assert all(vertex in model["simple_adjacency"][other] for other in neighbours)
replay = construct_configuration_model(degrees, rng=np.random.default_rng(17))
assert model["adjacency"] == replay["adjacency"]
np.testing.assert_array_equal(model["edges"], replay["edges"])
empty = construct_configuration_model([0, 0, 0], rng=np.random.default_rng(1))
assert empty["adjacency"] == [[], [], []]
assert not core_mask(empty["adjacency"], 3).any()
for invalid in [[-2, 2], [1, 2], [2.5, 1.5]]:
    with pytest.raises((TypeError, ValueError)):
        construct_configuration_model(invalid, rng=np.random.default_rng(1))

# For simple graphs the integer-index implementation must agree with the
# class-based pruning algorithm, including cascades and isolated vertices.
rng = np.random.default_rng(123)
for probability in [0.0, 0.15, 0.45, 1.0]:
    graph = Graph(15)
    vertices = list(graph.nodes)
    for left, right in combinations(vertices, 2):
        if rng.random() < probability:
            graph.add_edge(left, right)
    adjacency = graph_adjacency(graph)
    for threshold in [0, 1, 2, 3, 5]:
        assert core_mask(adjacency, threshold).sum() == len(
            construct_k_core(graph, threshold).nodes
        )
""",
    )


def test_configuration_theory_equations(comparison_project):
    execute_notebook(
        comparison_project,
        "05_configuration_theory.ipynb",
        """
from math import comb, exp, factorial

# These finite sums are independent evaluations of the defining probabilities,
# rather than a second copy of the generating-function formulas.
for lam in [0.2, 0.9, 1.3, 3.0]:
    for x in [0.0, 0.2, 0.6, 1.0]:
        message = 0.0
        density = 0.0
        for memberships in range(70):
            probability = exp(-lam) * lam**memberships / factorial(memberships)
            degree = 2 * memberships
            density += probability * sum(
                comb(degree, survivors) * x**survivors * (1-x)**(degree-survivors)
                for survivors in range(3, degree+1)
            )
            if degree:
                message += degree * probability / (2*lam) * sum(
                    comb(degree-1, survivors) * x**survivors
                    * (1-x)**(degree-1-survivors)
                    for survivors in range(2, degree)
                )
        np.testing.assert_allclose(cm_message(x, lam), message, atol=2e-13)
        np.testing.assert_allclose(cm_density(x, lam), density, atol=2e-13)

assert cm_message(0.5, 0.0) == 0.0
assert cm_density(0.5, 0.0) == 0.0
critical = cm_critical_point()
np.testing.assert_allclose(critical["lambda"], 1.287720370452004, atol=2e-10)
np.testing.assert_allclose(critical["x"], 0.43903221128399406, atol=2e-10)
np.testing.assert_allclose(critical["rho"], 0.13788881227715316, atol=2e-10)
assert abs(critical["residual"]) < 1e-10
assert abs(critical["tangent_residual"]) < 1e-9
x, lam = critical["x"], critical["lambda"]
step = 1e-5
slope = (cm_message(x+step, lam) - cm_message(x-step, lam)) / (2*step)
np.testing.assert_allclose(slope, 1.0, atol=2e-8)

for lam in [0.0, 0.5, critical["lambda"]-1e-6]:
    prediction = cm_prediction(lam, critical=critical)
    assert prediction["x"] == prediction["rho"] == 0.0
for lam in [critical["lambda"]+1e-6, 1.5, 2.0, 3.0]:
    prediction = cm_prediction(lam, critical=critical)
    assert critical["x"] < prediction["x"] < 1.0
    assert critical["rho"] < prediction["rho"] < 1.0
    assert abs(cm_message(prediction["x"], lam)-prediction["x"]) < 1e-10
    assert abs(prediction["residual"]) < 1e-10

# Starting the pruning recursion at full support selects the largest root.
# This independent check stays away from the slow critical bottleneck.
for lam in [1.35, 1.5, 2.0, 3.0]:
    x = 1.0
    for _ in range(10000):
        updated = cm_message(x, lam)
        if abs(updated-x) < 1e-14:
            break
        x = updated
    np.testing.assert_allclose(cm_prediction(lam, critical=critical)["x"], x,
                               atol=1e-10)
""",
        from_root=True,
    )


def test_configuration_comparison_fresh_kernels(comparison_project):
    notebook_dir = comparison_project / "notebooks"
    sources = {path: path.read_bytes() for path in notebook_dir.glob("*.ipynb")}
    execute_notebook(
        comparison_project,
        "06_configuration_simulation.ipynb",
        """
import pytest

serial = simulate_comparison(40, [0.0, 1.15, 1.5], 2, seed=13, jobs=1)
parallel = simulate_comparison(40, [0.0, 1.15, 1.5], 2, seed=13, jobs=2)
assert serial == parallel
for row in serial[::3]:
    replay = comparison_trial(row["n"], row["lambda"], row["replicate"],
                              row["trial_seed"])
    trial = [candidate for candidate in serial
             if candidate["trial_seed"] == row["trial_seed"]]
    assert replay == trial
with pytest.raises(FileExistsError):
    run_comparison(config, project_root=PROJECT_ROOT)

# If a later target already exists, no earlier new size may be generated.
with pytest.raises(FileExistsError):
    run_comparison(config | {"sizes": [20, 40]}, project_root=PROJECT_ROOT)
assert not (PROJECT_ROOT / config["output_dir"] / "comparison_n20.csv").exists()
""",
        from_root=True,
    )
    data_dir = comparison_project / "results/runs/configuration_comparison"
    data_files = sorted(data_dir.glob("*.csv"))
    assert [path.name for path in data_files] == [
        "comparison_n40.csv",
        "comparison_n80.csv",
    ]
    rows = []
    for path in data_files:
        with path.open(newline="", encoding="utf-8") as stream:
            measured = list(csv.DictReader(stream))
        assert len(measured) == 36
        assert {row["model"] for row in measured} == {
            "triangle_rig",
            "cm_multigraph",
            "cm_erased",
        }
        assert len({row["trial_seed"] for row in measured}) == 12
        for row in measured:
            n = int(row["n"])
            degree_counts = json.loads(row["degree_histogram"])
            assert sum(degree_counts) == n
            mean = sum(degree * count for degree, count in enumerate(degree_counts)) / n
            assert float(row["degree_mean"]) == pytest.approx(mean)
            variance = (
                sum(
                    (degree - mean) ** 2 * count
                    for degree, count in enumerate(degree_counts)
                )
                / n
            )
            assert float(row["degree_variance"]) == pytest.approx(variance)
            assert float(row["odd_degree_fraction"]) == sum(degree_counts[1::2]) / n
            assert float(row["core_fraction"]) == int(row["core_size"]) / n
            assert 0 <= float(row["simple_transitivity"]) <= 1
            if row["model"] == "cm_multigraph":
                assert not any(degree_counts[1::2])
            if float(row["lambda"]) == 0:
                assert int(row["core_size"]) == 0 and mean == 0
        for trial_seed in {row["trial_seed"] for row in measured}:
            trial = {
                row["model"]: row for row in measured if row["trial_seed"] == trial_seed
            }
            retained, erased = trial["cm_multigraph"], trial["cm_erased"]
            for key in ("seed", "loops", "parallel_excess", "simple_transitivity"):
                assert retained[key] == erased[key]
            assert retained["seed"] != trial["triangle_rig"]["seed"]
            assert int(retained["core_size"]) >= int(erased["core_size"])
            removed_edges = (
                (float(retained["degree_mean"]) - float(erased["degree_mean"]))
                * int(retained["n"])
                / 2
            )
            assert removed_edges == pytest.approx(
                int(retained["loops"]) + int(retained["parallel_excess"]), abs=1e-10
            )
        rows.extend(measured)
    assert len({row["trial_seed"] for row in rows}) == 24
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in data_files}
    result = execute_notebook(
        comparison_project,
        "07_configuration_analysis.ipynb",
        """
import pytest

measured = load_comparison(PROJECT_ROOT / config["data_dir"])
grouped = summarize_comparison(measured)
for group in grouped:
    fractions = [row["core_fraction"] for row in measured
                 if (row["model"], row["n"], row["lambda"]) ==
                    (group["model"], group["n"], group["lambda"])]
    assert group["trials"] == len(fractions) == 3
    np.testing.assert_allclose(group["mean"], np.mean(fractions))
    np.testing.assert_allclose(group["median"], np.median(fractions))
    np.testing.assert_allclose(group["standard_error"],
                              np.std(fractions, ddof=1)/np.sqrt(3))
with pytest.raises(FileNotFoundError):
    load_comparison(PROJECT_ROOT / "missing_comparison")
""",
    )
    assert {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in data_files
    } == before
    figure_dir = comparison_project / "results/figures/configuration_comparison"
    for name in (
        "fixed_points",
        "validation",
        "models",
        "zoom",
        "distributions",
        "degrees",
        "conventions",
    ):
        assert (
            (figure_dir / f"{name}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        )
    for name in (
        "summary",
        "validation_errors",
        "model_differences",
        "convention_differences",
        "theory_curve",
        "critical_point",
        "onset_brackets",
    ):
        with (figure_dir / f"{name}.csv").open(newline="", encoding="utf-8") as stream:
            assert list(csv.DictReader(stream))
    assert any(
        "image/png" in output.get("data", {})
        for cell in result.cells
        if cell.cell_type == "code"
        for output in cell.outputs
    )
    assert {path: path.read_bytes() for path in sources} == sources
    assert not (comparison_project / "results/notebooks").exists()
