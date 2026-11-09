.DEFAULT_GOAL := help

UV ?= uv
# TeX tools are installed separately from the uv Python environment.
LATEXMK ?= latexmk
LATEXMK_FLAGS ?= -pdf -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1
# Jupyter runs each notebook in a fresh kernel with its own directory as cwd.
# Without --output or --inplace, it saves no notebook copies or source outputs.
EXECUTE_NOTEBOOK = $(UV) run --locked jupyter execute

.PHONY: help setup sync run simulate figures theory comparison comparison-simulate \
        comparison-figures triangle-theory triangle-refine triangle-figures \
        triangle-study report report-full report-clean smoke test lint format format-check check

help:
	@printf '%s\n' \
	  'make setup         Synchronize the uv environment (alias: make sync)' \
	  'make run           Execute simulation, then analysis notebooks' \
	  'make simulate      Run the selected triangle-study stage and save its CSVs' \
	  'make figures       Plot saved measurements for the selected study stage' \
	  'make theory        Execute the configuration-model derivation and definitions' \
	  'make comparison    Run the three-model comparison, then analyze saved CSVs' \
	  'make comparison-simulate  Save matched-condition triangle and CM trials' \
	  'make comparison-figures   Plot saved comparison data against CM theory' \
	  'make triangle-theory     Execute the triangle cavity derivation and definitions' \
	  'make triangle-refine     Save additional triangle trials near the predicted transition' \
	  'make triangle-figures    Compare both theories with saved comparison/refinement data' \
	  'make triangle-study     Run targeted refinement, then the final comparison' \
	  'make report        Build report/build/main.pdf; reuse existing figures' \
	  'make report-full   Run both research studies and their analyses, then build the PDF' \
	  'make report-clean  Remove generated report build files' \
	  'make check         Check formatting, lint, and fresh-kernel notebook tests' \
	  'make smoke         Check the small simulation/analysis notebook workflow' \
	  'make format        Format notebook code cells and test code' \
	  '' \
	  'Edit the settings cells in notebooks/03 and notebooks/04 before running.' \
	  'Select the same study stage in both notebooks; existing trials are protected.' \
	  'For the configuration comparison, edit notebooks/06 and notebooks/07 instead.' \
	  'The comparison default includes larger runs; use smaller settings for a pilot.' \
	  'For the triangle cavity study, edit notebooks/09 and notebooks/10.' \
	  'report-full respects notebook settings and existing-measurement guards.' \
	  'See report/README.md before starting a full research run.' \
	  'Experiment output is saved under results/; the report PDF is under report/build/.'

setup sync:
	$(UV) sync --locked

# Recursive invocations keep both stages ordered even with make -j.
run:
	$(MAKE) simulate
	$(MAKE) figures

simulate:
	$(EXECUTE_NOTEBOOK) notebooks/03_triangle_simulation.ipynb --timeout=-1

# Analysis selects saved CSVs from its own settings cell; missing data gives a message
# directing the developer to run make simulate. Plotting never launches a sweep.
figures:
	$(EXECUTE_NOTEBOOK) notebooks/04_triangle_analysis.ipynb --timeout=-1

# The theory notebook defines the numerical predictions without generating data.
theory:
	$(EXECUTE_NOTEBOOK) notebooks/05_configuration_theory.ipynb --timeout=-1

# Keep simulation and saved-data analysis ordered, including under make -j.
# Existing trial CSVs are protected; use comparison-figures to analyze them again.
comparison:
	$(MAKE) comparison-simulate
	$(MAKE) comparison-figures

comparison-simulate:
	$(EXECUTE_NOTEBOOK) notebooks/06_configuration_simulation.ipynb --timeout=-1

comparison-figures:
	$(EXECUTE_NOTEBOOK) notebooks/07_configuration_analysis.ipynb --timeout=-1

# Triangle theory retains correlations inside each triangle; this defines its
# numerical functions without generating graphs or writing results.
triangle-theory:
	$(EXECUTE_NOTEBOOK) notebooks/08_triangle_cavity.ipynb --timeout=-1

# Reuse the broad comparison data from 06. Only missing transition resolution
# needs a new simulation: 09 writes a separate, protected triangle dataset.
triangle-refine:
	$(EXECUTE_NOTEBOOK) notebooks/09_triangle_refinement.ipynb --timeout=-1

# Reading saved 06 and 09 measurements never starts a simulation.
triangle-figures:
	$(EXECUTE_NOTEBOOK) notebooks/10_triangle_comparison.ipynb --timeout=-1

# Keep these dependent steps ordered even when invoked with make -j.
triangle-study:
	$(MAKE) triangle-refine
	$(MAKE) triangle-figures

# -cd resolves TeX inputs from report/; latexmk runs BibTeX and repeats LaTeX
# as needed for citations and cross-references. This target never runs notebooks.
report:
	$(LATEXMK) -cd $(LATEXMK_FLAGS) -outdir=build report/main.tex

# Use the common-condition broad study and the focused triangle study. Keep
# these steps ordered even with make -j. Existing CSVs remain protected: choose
# fresh notebook output/data directories or explicitly enable overwrite first.
# Figures are selected into report/figures/ deliberately when writing begins.
report-full:
	$(MAKE) comparison
	$(MAKE) triangle-study
	$(MAKE) report

# Remove latexmk-managed products while preserving source and directory markers.
report-clean:
	$(LATEXMK) -cd -C -outdir=build report/main.tex

smoke:
	$(UV) run --locked pytest -q tests/test_notebooks.py::test_simulation_and_analysis_fresh_kernels

test:
	$(UV) run --locked pytest

lint:
	$(UV) run --locked ruff check

format:
	$(UV) run --locked ruff format

format-check:
	$(UV) run --locked ruff format --check

check: lint format-check test
