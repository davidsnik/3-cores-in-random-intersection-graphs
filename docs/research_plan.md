# Research direction and next phase

This is the agreed scientific plan. The report outline is a writing roadmap;
the additional finite-size experiments below are **planned, not implemented**.

## Research question

**How do finite-size fluctuations affect the emergence and size of the 3-core
in Poisson triangle-community graphs, and to what extent can a stochastic
saddle-node approximation predict these fluctuations compared with a
degree-matched configuration model?**

The three connected questions are:

1. **Critical window:** How does the probability of a substantial core sharpen
   with size, and is its window width consistent with an order of $n^{-1/2}$?
2. **Conditional sizes:** How do surviving core-size distributions change with
   size, and are their density fluctuations consistent with $n^{-1/4}$?
3. **Prediction:** Can theory and survival-only calibration predict those
   distributions, and where does performance differ between models?

Community structure introduces dependence beyond the limiting degree law.
The aim is a controlled study of finite-size critical behaviour. Failure of
the proposed approximation can be informative; it does not by itself identify
a new universality class or establish an open-problem resolution.

## Mathematical starting point and testable approximation

Write $R_{n,M}=|\operatorname{Core}_3(G_{n,M})|/n$ for model $M$, and let
$A_{n,M}=\{R_{n,M}\ge\varepsilon_M\}$ define a substantial core. This is the
ordinary graph core, which need not be connected, rather than a hypergraph core.
Introduce model-specific critical values $\lambda_{c,M}$, right-hand jump
densities $\rho_{c,M}$, and the maximal positive fixed-point branch before
using them in predictions.

- **Established foundations:** configuration-model core theorems, and the
  incidence-tree local limit and degree law for community graphs.
- **Existing analytical prediction:** the CM support equation and the triangle
  cavity calculation. Triangle neighbours within a motif are resolved jointly;
  independence applies between limiting incidence-tree branches. Notebook 08
  already derives the triangle message-coordinate square-root expansion and
  checks fold nondegeneracy numerically.
- **To derive and verify:** the CM fold expansion and both density amplitudes in
  $\rho_M(\lambda)=\rho_{c,M}+a_M\sqrt{\lambda-\lambda_{c,M}}
  +O(\lambda-\lambda_{c,M})$, including the derivative calculation for $a_M$.
- **Finite-size hypothesis:** an $n^{-1/2}$ parameter window combined with that
  square root suggests $n^{-1/4}$ conditional density fluctuations, or
  $n^{3/4}$ core-count fluctuations. This scaling argument alone proves neither
  a triangle-core limit theorem nor a Gaussian effective perturbation.

A candidate occurrence model, fitted separately by size and model, is
$\Pr(A_{n,M})\approx\Phi((\lambda-\mu_{n,M})/w_{n,M})$, with $w_{n,M}>0$.
Here $\Phi$ is the standard normal distribution function. Set
$V_{n,M}=\sqrt n(\lambda-\mu_{n,M})+\sqrt n\,w_{n,M}Z$, where
$Z\sim N(0,1)$. The corresponding conditional prediction is

$$
n^{1/4}(R_{n,M}-\rho_{c,M})\mid A_{n,M}
\quad\approx\quad a_M\sqrt{V_{n,M}}\mid\{V_{n,M}>0\}.
$$

Fix $a_M$, $\rho_{c,M}$, and $\lambda_{c,M}$ from theory. Fit occurrence
parameters using survival indicators only. Split calibration and validation by
complete membership vector, keeping every matching and paired model outcome
from a vector in the same split; also reserve parameter points where feasible.
Do not fit a separate density location, amplitude, or spread. Propagate
occurrence-calibration uncertainty into the conditional predictions. Check
occurrence-model fit as well as conditional fit.

The CM fluctuation theorem is the benchmark, with its hypotheses to be
specialized to this random twice-Poisson degree family. Check the effect of
random degree sequences and divisibility conditioning explicitly. Local weak
convergence does not justify exchanging the large-graph and infinite-pruning
limits for triangles; that terminal-core step remains a cavity assumption.

## Controlled comparisons and statistical safeguards

- For a genuinely paired comparison at the **same physical $\lambda$**, sample
  one full membership vector $D$ with $\sum_iD_i$ divisible by three. Generate
  triangle matchings and CM pairings with nominal degrees $K_i=2D_i$.
  This exactly matches nominal information, not projected triangle degrees:
  repeated triangle slots, loops, and overlapping edges can reduce them.
- Retain the CM multigraph and its erased simple projection from each pairing
  as paired controls. Save actual degree histograms and projection defects.
  The multigraph, counting a loop twice in the degree, is the direct CM benchmark.
  Record the shared vector's conditioning rather than calling it unconditioned
  independent Poisson sampling.
- Repeated independent matchings conditional on the **whole** vector separate
  membership variation from matching variation. Save vector IDs, distinct
  membership/matching replay seeds, and nominal and actual degree diagnostics.
  Bootstrap vectors as clusters, preserving matching repetitions and model pairs;
  repetitions sharing a vector are not independent ensemble trials.
- Model-centred grids $\lambda=\lambda_{c,M}+u/\sqrt n$ generally use different
  physical parameters for the two models. They compare scaled behaviour, not
  paired degree sequences. Add shared physical-$\lambda$ points, including
  overlap where both models have usable survival counts, for paired contrasts.
- Evaluate probabilities, quantile-based window widths, conditional means,
  standard deviations, quantiles, empirical CDFs, and a predeclared distribution
  discrepancy such as Wasserstein distance. Use binomial intervals for batches
  with one realization per independent vector, separately for each model;
  repeated-vector batches require cluster-aware intervals, not graph-level
  binomial intervals. Preserve pairs in model contrasts. Distinguish ensemble
  spread from uncertainty in its estimate. Account for fitted parameters in
  goodness-of-fit calibration and show unscaled outcomes as well as collapses.
- Plan realization counts using pilot survival probabilities and conservative
  positive-count forecasts. Predeclare any allocation update, maximum budget,
  and final analysis batch. Do not stop naively at a fixed number of survivors
  and treat the resulting sample as fixed-size binomial data. Mark sparse
  conditional samples as inconclusive, and report their actual positive counts.
- Start with absolute cutoffs $\varepsilon=0.05$ and $0.02$; also predeclare
  model-relative cutoffs, for example $\varepsilon_M=c\rho_{c,M}$ for
  $c\in\{1/4,1/2\}$. Check whether these select the same substantial-core
  population. An absolute cutoff of $0.08$ is close to the triangle jump and
  should be a stress test. Operational onset brackets are not confidence
  intervals for $\lambda_{c,M}$.

## Completed foundation and remaining implementation

| Component | Existing evidence and planned extension |
| --- | --- |
| Theory: 05 and 08 | Fixed points, maximal branches, critical points, density predictions and numerical checks exist; 08 also derives the triangle message-coordinate fold expansion. Both density amplitudes, the CM fold expansion and finite-size theorem specialization still need documentation and verification. |
| Sampling and peeling: 02, 06, 09 | Reproducible generation, pruning, parallel trials and protected CSV output exist. Notebook 02 already accepts a fixed-count sampler for triangles and an explicit degree vector for CM; add paired/repeated-vector orchestration, IDs and checks rather than a new graph algorithm. |
| Analysis: 07 and 10 | Saved-data density validation, individual outcomes, degree/erasure diagnostics, uncertainty in means and cutoff sensitivity exist. Survival fits, width scaling and independently validated conditional distribution predictions are not implemented. |
| Saved measurements | Reuse the broad 06 comparison and focused 09 triangle data for exploratory baselines; retain their different grids and provenance. Existing triangle refinement CSVs have seven basic fields and lack the proposed vector and defect diagnostics. |

The reported preliminary $n=30{,}000$ agreement in conditional mean and mismatch
in standard deviation motivate the pilot. They are exploratory observations,
not independently validated findings. The survival fit and distributional
prediction behind that comparison are not yet reproducible notebook outputs.
The existing 06 triangle and CM streams do not share a membership vector;
their common experimental settings must not be described as exact degree pairing.

## Immediate roadmap

1. **Theory and protocol:** extend 05/08 with the remaining fold/density
   derivatives and independent checks; verify CM theorem assumptions. Freeze cutoffs, metrics,
   calibration/validation splits and uncertainty rules before new measurements.
2. **Focused pilot:** start with $n\in\{10000,30000\}$ and each model's grid
   $u\in\{-2,-1,0,1,2\}$. The aim is to reassess conditional spread, not estimate
   an asymptotic exponent from two sizes. Use an initial screening batch of
   about 50 independent vectors per point for runtime and allocation only;
   this count is not a claim of adequate conditional precision. Select a small
   shared physical-$\lambda$ grid from the observed overlap for paired contrasts.
   If overlap gives too few survivors, report that limitation rather than
   claiming a paired conditional-distribution comparison.
   Use conservative screening probabilities to fix sample sizes for separate
   occurrence-calibration and validation batches. For validation, target at
   least 100 positives with 90% forecast probability, subject to a declared
   runtime cap; fewer than 50 positives makes conditional summaries inconclusive.
   Tail estimates require particular caution even when this minimum is met.
   Freeze counts before drawing calibration/validation vectors; label targets
   exceeding the cap unresolved. A small control, such as 20 independent vectors
   with three matchings each at selected shared parameters, can diagnose
   matching variation, with cluster-aware uncertainty and separate vector IDs.
3. **Separate collection from analysis:** proposed future notebooks
   `11_finite_size_simulation.ipynb` and `12_finite_size_analysis.ipynb` would
   reuse 02/05/08 and the 06/09 sampling pattern. These files do not yet exist.
   Analysis must read saved data without generating graphs. Save the protocol,
   split membership, code version and diagnostics with replayable measurements.
4. **Evaluate before expansion:** compare held-out occurrence and full
   conditional distributions; bootstrap calibration and vector-level variation.
   Use cutoff and model controls to distinguish poor prediction, sparse data
   and plausible finite-size corrections. Expand sizes or repetitions only if
   the pilot identifies a question that the larger campaign can resolve.
   A later scaling study needs several well-separated sizes, uncertainty on
   fitted exponents, and size-range sensitivity; two pilot sizes cannot establish
   the proposed asymptotic exponents.

## Primary references and their scope

- [Janson and Łuczak (2008)](https://doi.org/10.1214/07-AAP478): CM critical
  fluctuations and non-normal threshold limits under stated assumptions; does
  not establish the triangle finite-size law.
- [Bhat, Shrestha and Hébert-Dufresne (2017)](https://doi.org/10.1103/PhysRevE.95.012314):
  established motif-aware core calculations; context for the triangle equations,
  not a fluctuation theorem for this ensemble.
- [van der Hofstad, Komjáthy and Vadon (2021)](https://doi.org/10.1017/apr.2021.12):
  community-graph local convergence and degree distributions; does not by itself
  prove the terminal 3-core cavity prediction.
