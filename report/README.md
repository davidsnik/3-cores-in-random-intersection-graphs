# Academic report

This directory is prepared for the future LaTeX report. No report source or
bibliography has been written yet.

Use these locations when writing begins:

- `main.tex`: the report's entry point, directly in this directory.
- `sections/`: included `.tex` files, for example `sections/introduction.tex`.
- `figures/`: deliberately selected figures referenced by the report; commit
  these so the report can be rebuilt from the repository.
- `references/refs.bib`: the future BibTeX or BibLaTeX bibliography.
- `build/`: generated PDF, logs, auxiliary files, and other build output.

Exploratory simulation figures belong in `../results/figures/`. Copy selected
figures into `figures/` when incorporating them into the report. Use paths
relative to this directory in `main.tex` and keep filenames descriptive.

Install a TeX distribution and `latexmk` separately through Fedora's package
manager when needed. TeX tools are not Python dependencies and are not managed
by `uv`. Once a `main.tex` document exists, a conventional build command from
the repository root is:

```bash
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

The appropriate engine and bibliography tool can be chosen with the report's
eventual template. Git ignores `build/` output while keeping its placeholder.
