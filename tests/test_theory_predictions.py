"""Verify theory against independent differences, probability sums, and exports."""

import csv
import shutil

import pytest
from test_notebooks import ROOT, execute_notebook


@pytest.fixture
def theory_project(tmp_path):
    """Isolate all deterministic paper exports from the working report."""
    notebook_dir = tmp_path / "notebooks"
    notebook_dir.mkdir()
    for name in [
        "05_configuration_theory.ipynb",
        "08_triangle_cavity.ipynb",
        "theory_comparison.ipynb",
    ]:
        shutil.copy2(ROOT / "notebooks" / name, notebook_dir / name)
    return tmp_path


def test_theory_checks_and_paper_exports(theory_project):
    paths = list((theory_project / "notebooks").glob("*.ipynb"))
    before = {path: path.read_bytes() for path in paths}
    execute_notebook(
        theory_project,
        "theory_comparison.ipynb",
        r"""
from math import comb, exp, factorial
import pytest

# Check derivatives away from the fold as well: a correct derivative must
# differentiate the specified map, not an identity valid only on its roots.
for x, lam in [(0.2, 0.9), (0.45, 1.3), (0.7, 2.0)]:
    step = 1e-5
    np.testing.assert_allclose(
        cm_message_lambda_derivative(x, lam),
        (cm_message(x, lam+step)-cm_message(x, lam-step))/(2*step),
        rtol=1e-8, atol=1e-9,
    )
    np.testing.assert_allclose(
        cm_message_second_derivative(x, lam),
        (cm_message_derivative(x+step, lam)-cm_message_derivative(x-step, lam))/(2*step),
        rtol=1e-7, atol=1e-8,
    )
    np.testing.assert_allclose(
        cm_density_derivative(x, lam),
        (cm_density(x+step, lam)-cm_density(x-step, lam))/(2*step),
        rtol=1e-8, atol=1e-9,
    )

for z, lam in [(0.3, 0.9), (0.7, 1.3), (1.2, 2.0)]:
    step = 1e-5
    analytic = _triangle_fold_derivatives(z, lam)
    np.testing.assert_allclose(
        analytic["H_lambda"],
        (_triangle_scalar_residual(z,lam+step)-_triangle_scalar_residual(z,lam-step))/(2*step),
        rtol=1e-8, atol=1e-9,
    )
    np.testing.assert_allclose(
        analytic["H_zz"],
        (_triangle_scalar_derivative(z+step,lam)-_triangle_scalar_derivative(z-step,lam))/(2*step),
        rtol=1e-7, atol=1e-8,
    )
    np.testing.assert_allclose(
        analytic["rho_z"],
        (_triangle_prediction_at_z(z+step,lam)["rho"]-_triangle_prediction_at_z(z-step,lam)["rho"])/(2*step),
        rtol=1e-8, atol=1e-9,
    )

# Independent binomial summation checks the thinned moment shortcuts used
# for the new CM variance. The covariance integral has a separate check in
# the comparison notebook, evaluated from the paper's original formula.
x, lam = cm["x"], cm["lambda"]
conditional_variance, degree_mean, degree_second = 0.0, 0.0, 0.0
for memberships in range(40):
    weight = exp(-lam)*lam**memberships/factorial(memberships)
    k = 2*memberships
    first = sum(j*comb(k,j)*x**j*(1-x)**(k-j) for j in range(3,k+1))
    second = sum(j*j*comb(k,j)*x**j*(1-x)**(k-j) for j in range(3,k+1))
    conditional_variance += weight*(second-first*first)
    value = k*x*x-first
    degree_mean += weight*value
    degree_second += weight*value*value
np.testing.assert_allclose(cm_noise["variance_degree"],
                           degree_second-degree_mean**2, atol=2e-14)
np.testing.assert_allclose(cm_noise["variance_matching"],
                           conditional_variance-4*lam*x*x*(1-x*x), atol=2e-14)
assert cm_noise["variance_matching"] > 0 and cm_noise["variance_degree"] > 0
assert cm_noise["poisson_tail_bound"] < 1e-40

# CDF and inverse are checked for both model amplitudes and several effective
# threshold locations. No simulated conditional sizes enter these laws.
for amplitude in [cm["a"], triangle["a"]]:
    for centre in [-5.0, -1.0, 0.0, 2.0]:
        for probability in [0.001, 0.1, 0.5, 0.9, 0.999]:
            quantile = stochastic_fold_quantile(probability, amplitude, centre, 1.2)
            recovered = stochastic_fold_cdf(quantile, amplitude, centre, 1.2)
            np.testing.assert_allclose(recovered, probability, atol=2e-13)
        assert stochastic_fold_cdf(-1, amplitude, centre, 1.2) == 0
        assert stochastic_fold_cdf(float("inf"), amplitude, centre, 1.2) == 1
        assert stochastic_fold_quantile(0, amplitude, centre, 1.2) == 0
        assert stochastic_fold_quantile(1, amplitude, centre, 1.2) == float("inf")
for operation in [
    lambda: stochastic_fold_cdf(1, 0, 0, 1),
    lambda: stochastic_fold_cdf(1, 1, 0, -1),
    lambda: stochastic_fold_cdf(float("nan"), 1, 0, 1),
    lambda: stochastic_fold_quantile(1.1, 1, 0, 1),
]:
    with pytest.raises(ValueError):
        operation()
""",
        from_root=True,
    )
    diagnostic_dir = theory_project / "results/figures/theory"
    for name in [
        "critical_values",
        "derivative_checks",
        "branch_checks",
        "density_curves",
        "cm_fluctuation_constants",
        "cm_covariance_checks",
    ]:
        with (diagnostic_dir / f"{name}.csv").open(newline="") as stream:
            assert list(csv.DictReader(stream)), f"{name} must contain evaluations"
    table = theory_project / "report/tables/theory_critical_values.tex"
    assert (
        "CM multigraph" in table.read_text() and "Triangle cavity" in table.read_text()
    )
    assert (
        (theory_project / "report/figures/theory_fold_comparison.pdf")
        .read_bytes()
        .startswith(b"%PDF-")
    )
    assert not (theory_project / "results/runs").exists()
    assert {path: path.read_bytes() for path in paths} == before
