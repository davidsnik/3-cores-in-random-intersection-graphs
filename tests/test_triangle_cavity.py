"""Verify joint triangle support and the saved-data cavity-study workflow."""

import csv
import shutil
from pprint import pformat

import nbformat
import pytest
from test_notebooks import ROOT, execute_notebook


@pytest.fixture
def cavity_project(tmp_path):
    """Use copied notebook sources and tiny trials, never research results."""
    notebook_dir = tmp_path / "notebooks"
    notebook_dir.mkdir()
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        shutil.copy2(path, notebook_dir / path.name)
    settings = {
        "06_configuration_simulation.ipynb": {
            "sizes": [40, 80],
            "lambdas": [0.0, 1.1, 1.25, 1.5, 2.2],
            "repeats": 3,
            "seed": 20261109,
            "jobs": 2,
            "output_dir": "results/runs/configuration_comparison",
            "overwrite": False,
        },
        "09_triangle_refinement.ipynb": {
            "sizes": [40, 80],
            "lambdas": [1.2, 1.23, 1.26],
            "repeats": 3,
            "seed": 20261110,
            "jobs": 2,
            "output_dir": "results/runs/triangle_cavity_refinement",
            "overwrite": False,
        },
        "10_triangle_comparison.ipynb": {
            "comparison_dir": "results/runs/configuration_comparison",
            "refinement_dir": "results/runs/triangle_cavity_refinement",
            "figure_dir": "results/figures/triangle_cavity",
            "focus_half_width": 0.065,
            "critical_exclusion": 0.025,
            "histogram_n": None,
            "histogram_lambdas": [1.2, 1.23, 1.26],
            "large_core_cutoff": 0.05,
            "onset_cutoffs": [0.02, 0.05, 0.08],
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


def test_triangle_refinement_replay_and_saved_data(cavity_project):
    notebook_dir = cavity_project / "notebooks"
    sources = {path: path.read_bytes() for path in notebook_dir.glob("*.ipynb")}
    execute_notebook(
        cavity_project,
        "09_triangle_refinement.ipynb",
        """
import pytest

serial = simulate_refinement(40, [0.0, 1.2, 1.5], 2, seed=19, jobs=1)
parallel = simulate_refinement(40, [0.0, 1.2, 1.5], 2, seed=19, jobs=2)
assert serial == parallel
assert len({row['seed'] for row in serial}) == len(serial)
for row in serial:
    assert row == refinement_trial(row['n'], row['lambda'], row['replicate'], row['seed'])
    graph = construct_special_triangle_RIG(row['n'], row['lambda'],
                                          rng=np.random.default_rng(row['seed']))
    assert row['core_size'] == len(construct_k_core(graph, 3).nodes)
    assert row['core_fraction'] == row['core_size']/row['n']

with pytest.raises(FileExistsError):
    run_refinement(config, project_root=PROJECT_ROOT)
with pytest.raises(FileExistsError):
    run_refinement(config | {'sizes': [20, 40]}, project_root=PROJECT_ROOT)
assert not (PROJECT_ROOT / config['output_dir'] / 'cavity_refinement_n20.csv').exists()
for invalid in [{'n': 0}, {'lambdas': [1.2, 1.2]}, {'repeats': 0}, {'jobs': 0}]:
    settings = dict(n=40, lambdas=[1.2], repeats=1, seed=1, jobs=1) | invalid
    with pytest.raises(ValueError):
        simulate_refinement(**settings)
""",
        from_root=True,
    )
    data_dir = cavity_project / "results/runs/triangle_cavity_refinement"
    data_files = sorted(data_dir.glob("*.csv"))
    assert [path.name for path in data_files] == [
        "cavity_refinement_n40.csv",
        "cavity_refinement_n80.csv",
    ]
    for path in data_files:
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 9
        assert {row["model"] for row in rows} == {"triangle_rig"}
        assert len({row["seed"] for row in rows}) == 9
        for row in rows:
            assert float(row["core_fraction"]) == int(row["core_size"]) / int(row["n"])

    # Reuse the real comparison notebook with temporary, tiny settings. This
    # exercises its actual CSV format rather than inventing synthetic fixtures.
    execute_notebook(cavity_project, "06_configuration_simulation.ipynb")
    comparison_dir = cavity_project / "results/runs/configuration_comparison"
    raw_files = data_files + sorted(comparison_dir.glob("*.csv"))
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in raw_files}
    result = execute_notebook(
        cavity_project,
        "10_triangle_comparison.ipynb",
        """
import pytest

loaded = load_triangle_study(PROJECT_ROOT / config['comparison_dir'],
                             PROJECT_ROOT / config['refinement_dir'])
assert len(loaded) == 108
assert {row['dataset'] for row in loaded} == {'comparison', 'refinement'}
summary_rows = summarize_triangle_study(loaded)
for group in summary_rows:
    fractions = [row['core_fraction'] for row in loaded
                 if (row['dataset'], row['model'], row['n'], row['lambda']) ==
                    (group['dataset'], group['model'], group['n'], group['lambda'])]
    assert group['trials'] == len(fractions) == 3
    np.testing.assert_allclose(group['mean'], np.mean(fractions))
    np.testing.assert_allclose(group['median'], np.median(fractions))
    np.testing.assert_allclose(group['standard_error'],
                               np.std(fractions, ddof=1)/np.sqrt(3))
with pytest.raises(FileNotFoundError):
    load_triangle_study(PROJECT_ROOT / 'missing_comparison')
broad_only = load_triangle_study(PROJECT_ROOT / config['comparison_dir'])
assert len(broad_only) == 90
assert {row['dataset'] for row in broad_only} == {'comparison'}
""",
    )
    assert {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in raw_files
    } == before
    figure_dir = cavity_project / "results/figures/triangle_cavity"
    for name in (
        "branches",
        "triangle_validation",
        "refinement",
        "distributions",
        "models",
        "model_difference",
        "onset",
        "iteration",
    ):
        assert (
            (figure_dir / f"{name}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        )
    for name in (
        "summary",
        "validation_errors",
        "critical_comparison",
        "theory_curves",
        "onset_brackets",
        "model_differences",
        "numerical_diagnostics",
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
    assert not (cavity_project / "results/notebooks").exists()


def test_triangle_local_support_and_probabilities(cavity_project):
    execute_notebook(
        cavity_project,
        "08_triangle_cavity.ipynb",
        """
from math import exp, factorial
import pytest

# Keep the target present, and explicitly prune the other two vertices of one
# triangle. Their external supporters stay fixed. This independently checks
# the joint local rule, including mutual support through the third edge.
for left_support in range(5):
    for right_support in range(5):
        support = [left_support, right_support]
        alive = {0, 1}
        while True:
            removed = {vertex for vertex in alive
                       if support[vertex] + 1 + int(1-vertex in alive) < 3}
            if not removed:
                break
            alive -= removed
        assert triangle_local_support(left_support, right_support) == len(alive)
assert triangle_local_support(0, 0) == 0
assert triangle_local_support(0, 1) == 0
assert triangle_local_support(0, 2) == 1
assert triangle_local_support(1, 1) == 2

# Realize the same local cases as ordinary simple graphs. A complete five-vertex
# anchor keeps the target and all supplied external neighbours present. Standard
# graph peeling must then give exactly the predicted two-neighbour support.
%run "02_algorithms.ipynb"
from itertools import combinations

for left_support in range(5):
    for right_support in range(5):
        graph = Graph(8)
        *anchor, target, left, right = list(graph.nodes)
        for first, second in combinations(anchor, 2):
            graph.add_edge(first, second)
        for vertex in anchor:
            graph.add_edge(target, vertex)
        graph.add_edge(target, left)
        graph.add_edge(target, right)
        graph.add_edge(left, right)
        for vertex in anchor[:left_support]:
            graph.add_edge(left, vertex)
        for vertex in anchor[:right_support]:
            graph.add_edge(right, vertex)
        peeled = construct_k_core(graph, 3)
        assert target in peeled.nodes
        retained = int(left in peeled.nodes) + int(right in peeled.nodes)
        assert triangle_local_support(left_support, right_support) == retained

# Independently enumerate the compound-Poisson support distribution. Do not
# reuse the generating-function expression or assume independent triangle edges.
for lam in [0.0, 0.2, 1.2, 3.0]:
    for q in [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.2, 0.6], [0.3, 0.1]]:
        probabilities = np.zeros(3)
        density = 0.0
        for singles in range(60):
            p_single = exp(-lam*q[0]) * (lam*q[0])**singles / factorial(singles)
            for doubles in range(60):
                probability = (p_single * exp(-lam*q[1])
                               * (lam*q[1])**doubles / factorial(doubles))
                total_support = singles + 2*doubles
                if total_support < 3:
                    probabilities[total_support] += probability
                else:
                    density += probability
        np.testing.assert_allclose(triangle_support_probabilities(q, lam),
                                   probabilities, atol=3e-14)
        np.testing.assert_allclose(triangle_density(q, lam), density, atol=3e-14)

        # Values at least two have the same role in the local triangle rule.
        states = [probabilities[0], probabilities[1],
                  1-probabilities[0]-probabilities[1]]
        messages = np.zeros(3)
        for left in range(3):
            for right in range(3):
                messages[triangle_local_support(left, right)] += states[left]*states[right]
        np.testing.assert_allclose(triangle_messages(q, lam), messages[1:], atol=3e-14)

for invalid in [[-0.1, 0.5], [0.7, 0.7], [0.2], [0.1, float('nan')]]:
    with pytest.raises(ValueError):
        triangle_messages(invalid, 1.0)
with pytest.raises(ValueError):
    triangle_local_support(-1, 2)
""",
    )


def test_triangle_critical_point_and_maximal_branch(cavity_project):
    execute_notebook(
        cavity_project,
        "08_triangle_cavity.ipynb",
        """
critical = triangle_critical_point()
np.testing.assert_allclose(critical['lambda'], 1.22859823946, atol=2e-9)
np.testing.assert_allclose(critical['rho'], 0.08111206, atol=1e-8)
assert 0 < critical['q1'] + critical['q2'] < 1
assert 0 < critical['rho'] < 1
assert abs(critical['residual']) < 1e-9
assert abs(critical['tangent_residual']) < 1e-9
q = np.array([critical['q1'], critical['q2']])
np.testing.assert_allclose(triangle_messages(q, critical['lambda']), q, atol=1e-10)

# Independently differentiate the full two-dimensional map: a saddle-node
# has a unit eigenvalue, rather than instability of the always-present zero root.
step = 1e-5
jacobian = np.column_stack([
    (triangle_messages(q + step*np.eye(2)[column], critical['lambda'])
     - triangle_messages(q - step*np.eye(2)[column], critical['lambda']))/(2*step)
    for column in range(2)
])
assert np.min(np.abs(np.linalg.eigvals(jacobian)-1)) < 2e-8

for lam in [0.0, 0.5, critical['lambda']-1e-6]:
    prediction = triangle_prediction(lam, critical=critical)
    assert prediction['q1'] == prediction['q2'] == prediction['rho'] == 0.0
    np.testing.assert_array_equal(triangle_messages([0.0, 0.0], lam), [0.0, 0.0])

# Bracketing the upper scalar branch must agree with a genuinely different
# calculation: two-dimensional peeling from initially complete motif support.
for lam in [critical['lambda']+1e-3, 1.3, 1.5, 2.5]:
    prediction = triangle_prediction(lam, critical=critical)
    iteration = triangle_iteration(lam, tolerance=1e-13, max_iterations=100000)
    assert iteration['converged']
    assert iteration['iterations'] < 100000
    assert abs(prediction['residual']) < 1e-10
    assert abs(iteration['residual']) < 1e-11
    for field in ['q1', 'q2', 'rho']:
        np.testing.assert_allclose(prediction[field], iteration[field], atol=1e-9)
    assert prediction['rho'] > critical['rho']

# The positive critical value is a branch limit, with a jump from the zero
# subcritical prediction; it is not a deterministic finite-graph assertion.
at_critical = triangle_prediction(critical['lambda'], critical=critical)
np.testing.assert_allclose(at_critical['rho'], critical['rho'], atol=1e-10)
just_above = triangle_prediction(critical['lambda']+1e-6, critical=critical)
assert just_above['rho'] > critical['rho']
assert just_above['rho'] - critical['rho'] < 0.003
assert triangle_prediction(20.0, critical=critical)['rho'] > 0.999999
""",
        from_root=True,
    )
