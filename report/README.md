# LaTeX report

The report uses the same `IEEEtran` conference style as the supplied
`GLA_Software` project: `10pt,conference,compsoc`, with the class's fonts,
two-column layout, headings, title block, and captions. It uses the class's
default US Letter paper size. One author and an abstract are prepared;
sections contain writing placeholders only.

The compact space below the title and around figures follows the reference
project. The abstract and mathematical environments support this report's needs;
the bibliography uses IEEEtran's standard two-column placement.

## Files and build

- `main.tex`: front matter, section order, and bibliography commands.
- `preamble.tex`: typography, mathematical notation, theorem environments,
  figures, tables, citations, and cross-references.
- `sections/`: one source file per main section, plus `appendices.tex` for
  supporting details. Section order is explicit in `main.tex`.
- `figures/`: deliberately selected report figures, committed with the source.
- `references/refs.bib`: the BibTeX database.
- `IEEEtran.cls` and `IEEEtran.bst`: unchanged upstream document class and
  bibliography style, included so this template builds without a separate
  IEEEtran installation.
- `build/`: generated PDF, logs, and auxiliary files, ignored by Git.

Install a TeX distribution with `pdflatex`, BibTeX, `latexmk`, and the packages
listed in `preamble.tex`. TeX tools are installed separately from the Python
environment; `make setup` installs only the locked `uv` dependencies. The
template uses IEEEtran's native typography with standard mathematical and
referencing packages. Avoid adding font, margin, heading, or caption overrides
when maintaining the reference style.

A minimal TeX installation also needs the standard Times, Helvetica, and Courier
fonts (TeX Live packages `times`, `helvetic`, and `courier`). These are TeX
dependencies, separate from Python. If you use fonts installed in a user TeX
tree, run `updmap-user` after system font packages change to refresh the user
font maps.

The bundled class (version 1.8b) and bibliography style (version 1.14) are an
unchanged subset of Michael Shell's IEEEtran distribution, under LPPL 1.3.
Their original copyright and license headers are retained. The complete work,
including its documentation and example files, is available from the
[official CTAN package](https://ctan.org/pkg/ieeetran) and
[full distribution archive](https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip).
Keep these upstream files unchanged; project-specific settings belong in
`preamble.tex`.

From the repository root:

```bash
make report        # Build report/build/main.pdf without running experiments
make report-clean  # Remove generated report build files
```

`latexmk` runs LaTeX and BibTeX as needed, resolving references automatically.
The equivalent direct command is:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error -outdir=build report/main.tex
```

## Experiments and figures

```bash
make report-full   # Run 06, 07, 09, and 10 in order, then build the PDF
```

This runs the broad configuration-model comparison and focused triangle study
using their saved notebook settings. These are the existing baseline studies;
the proposed finite-size calibration/validation pilot is not implemented by
this command. The defaults are research runs, so reduce
sizes and repeats first if desired. Existing trial CSVs remain protected. For a
new run, select fresh output directories in notebooks 06 and 09, and align the
input directories in 07 and 10. Explicitly set `overwrite = True` only when
replacement is intended. With existing measurements, use
`make comparison-figures` and `make triangle-figures` to regenerate plots, then
`make report` to compile; no simulations are needed.

Notebook output stays under `results/figures/`. Copy only the plots selected for
the paper into `report/figures/`, using descriptive filenames. The build does not
copy exploratory figures automatically. Commit selected figures so a fresh
checkout can build the report without rerunning experiments. Existing PNG plots
are supported; PDF is useful for future vector exports from Matplotlib.

## Writing conventions

The outline follows the scientific questions rather than the order of notebook
execution. It contains headings, writing prompts, and source comments only;
no scientific prose or numerical conclusions have been drafted.

| Section | Intended role | Notebook sources |
| --- | --- | --- |
| 1. Introduction | Finite-size question, three linked aims, literature, and scope | Assignment and cited literature |
| 2. Graph models and core observables | 3-core and size; Poisson triangle communities; degree-matched CM | 02, 05, 06, 08 |
| 3. Critical behavior and finite-size predictions | CM equations/theorems; joint triangle cavity equations; saddle-node/density expansion; window/fluctuation scales; stochastic conditional law | 05, 08, literature; density amplitudes and finite-size specialization planned |
| 4. Numerical methodology | Sampling/pruning/verification; scaled grids and controls; survival calibration/validation; distributions/uncertainty/sensitivity | Existing 02/05/06/08/09/10 patterns; new finite-size study planned |
| 5. Finite-size results and model comparisons | Limiting benchmarks; survival/windows; conditional distributions/prediction; degree/randomness/cutoff controls | Baselines in 07/10 and exploratory 04; new results not yet collected |
| 6. Discussion | Explain finite-size behavior and approximation performance; limitations and possible extensions | Eventual evidence and literature |
| 7. Conclusion | Answer the three connected questions, including supported negative or inconclusive findings | Main report results |
| Appendix A | Longer support/fold derivations, theorem assumptions, independent numerical/local checks | 05, 08, 10; new derivations planned |
| Appendix B | Configurations, split/allocation provenance, supplementary diagnostics and sensitivity | Existing and future experiment records |

The exact question, subquestions, scientific status, and next pilot are recorded
once in [the research plan](../docs/research_plan.md). This guide maps that plan
to the paper; it does not prescribe new experiments through the build commands.

Definitions come before support equations; the equations supply critical
densities and fold coefficients; those quantities define the independent
finite-size prediction tested by the numerical methodology. Results follow
the same three questions for both models. Comments in the `.tex` files reserve
derivations, figures, tables, and comparisons. Essential assumptions and
calibration rules belong in the main paper, with longer details in appendices.
The former computational-methods and experimental-design files are merged into
`sections/numerical_methodology.tex`.

When filling the outline, preserve these distinctions:

- The CM theorem and the triangle cavity prediction have different levels of
  justification. An exact local triangle calculation is not a terminal-core
  limit theorem. Select the maximal branch and state the critical right-hand
  convention explicitly.
- Existing broad-run model streams are independent. New shared-vector controls
  would match nominal degrees, while triangle projection can change actual
  degrees. Common physical-parameter pairing and model-specific critical grids
  are complementary designs. The paired CM erased control remains separate.
- Theory fixes the critical density and density amplitude; survival indicators
  fit occurrence parameters. Held-out conditional sizes must not fit their own
  location, amplitude, or spread. Existing inspected data remain exploratory.
- Evaluate full distributions and positive counts, with uncertainty appropriate
  to independent vectors or repeated-vector clusters. Keep cutoffs relative to
  the critical jump in view. The detailed protocol is in the research plan.
- Retain provenance for broad/refined baselines and planned pilot/calibration/
  validation cohorts. Error scores need their grid and exclusion conventions.
  Onset brackets and smoothed slope markers are not critical-parameter intervals.
- Full warning propagation and larger-clique experiments are possible extensions,
  not completed results promised by this outline.

Edit front matter in `main.tex` and write prose in the relevant section file.
The title, author, affiliation, and email are placeholders; the PDF title and
author metadata are set alongside them. Keep both consistent when filling them in.
Keep shared commands in `preamble.tex`; equations use IEEEtran's continuous
numbering. The class supplies the title layout through `\IEEEauthorblockN` and
`\IEEEauthorblockA`. Use `\appendices` before multiple appendix sections.
For example, the following patterns can be added when writing begins:

```latex
\begin{equation}\label{eq:example}
  a = b.
\end{equation}
\begin{theorem}\label{thm:example}
  [Theorem statement.]
\end{theorem}
\begin{proof}
  [Proof.]
\end{proof}
```

Use `\cref{eq:example}` or `\cref{thm:example}` for named, clickable references.
Theorem, lemma, proposition, corollary, definition, and remark environments share
a counter within each section. `\Prob`, `\E`, `\Var`, and `\Core` provide common
notation. Use `align` for multiline equations.

For a one-column figure, use `\includegraphics[width=\linewidth]{filename}`
inside a `figure` environment. For a plot spanning both columns, use `figure*`
and `width=\textwidth`. Place `\label{fig:name}` after `\caption{...}`. Figure
paths are resolved from `figures/`. Use `table` or `table*` for tables, with
`booktabs` commands `\toprule`, `\midrule`, and `\bottomrule` rather than vertical
rules. Refer to figures and tables with `\cref` as well.

Add verified sources to `references/refs.bib` using stable descriptive keys.
Use `\cite{key}` for bracketed numeric citations. The `IEEEtran` bibliography
style numbers references in citation order. Links are clickable without visible
colours or borders, matching the reference project. The initial five verified
sources cover CM core/fluctuation results, the community-graph framework, and
motif-aware calculations in other ensembles. The temporary `\nocite` list
prints this working bibliography; replace it with citations at the relevant
claims when prose is written. Bibliography inclusion alone is not evidence that
a theorem applies to our triangle model.
