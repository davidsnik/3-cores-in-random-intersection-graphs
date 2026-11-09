.DEFAULT_GOAL := help

UV ?= uv
# Jupyter runs each notebook in a fresh kernel with its own directory as cwd.
# Without --output or --inplace, it saves no notebook copies or source outputs.
EXECUTE_NOTEBOOK = $(UV) run --locked jupyter execute

.PHONY: help setup sync run simulate figures smoke test lint format format-check check

help:
	@printf '%s\n' \
	  'make setup         Synchronize the uv environment (alias: make sync)' \
	  'make run           Execute simulation, then analysis notebooks' \
	  'make simulate      Run the selected triangle-study stage and save its CSVs' \
	  'make figures       Plot saved measurements for the selected study stage' \
	  'make check         Check formatting, lint, and fresh-kernel notebook tests' \
	  'make smoke         Check the small simulation/analysis notebook workflow' \
	  'make format        Format notebook code cells and test code' \
	  '' \
	  'Edit the settings cells in notebooks/03 and notebooks/04 before running.' \
	  'Select the same study stage in both notebooks; existing trials are protected.' \
	  'Only CSV measurements, analysis summaries, and figures are saved under results/.'

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
