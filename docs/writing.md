# Scientific writing guide

Use these principles when drafting and reviewing the paper. They also apply to
mathematical explanations in notebooks, where more computational detail is
appropriate. The introduction illustrates the preferred tone; its level of
detail is not a template for every section. Adapt the exposition to the material
without fixed paragraph patterns or word limits.

Consult [research_plan.md](research_plan.md) for scientific scope and actual
progress, [architecture.md](architecture.md) for model and measurement
conventions, and [the report guide](../report/README.md) for section roles,
notebook sources, formatting, and build commands.

## Voice and accessibility

- Write for a mathematically trained reader who is new to this project. Use
  precise definitions and familiar language; accessibility does not require an
  elementary opening or removing necessary mathematics.
- Use an impersonal paper voice. Prefer the specific model, equation, or analysis
  as the subject, or use "this work", "this study", or "this paper". Avoid "we",
  "our", "us", and "this report" in manuscript prose. Do not replace every
  first-person sentence with the same stock phrase.
- Use connected sentences instead of a claim followed by a colon and an
  elaboration. This preference does not prohibit colons in notation or lists.
  Avoid inflated academic language, generic importance claims, and formulaic
  transitions.
- Keep enough information for a sentence to make sense immediately. Say what a
  benchmark compares, what an approximation predicts, and which quantity
  fluctuates. Replace abstract shorthand with a concrete explanation before
  relying on it. Shorter is not better if the reader must reconstruct the meaning.
- Write the manuscript as a scientific paper, not a work plan. Use present tense
  for its aims and mathematical statements and an appropriate tense for completed
  procedures. This does not license claims that unfinished experiments were run
  or produced results. Keep outstanding tasks in project documentation and flag
  missing evidence when delivering a draft.

## Narrative and choice of detail

- Make the research objective clear early, including the object studied, the
  quantity predicted, and why the comparison or method helps answer the question.
  Introduce distinct models by name and explain their different constructions
  and roles before comparing them. State what a control holds fixed and what it
  changes.
- Introduce concepts before using them and connect each paragraph to the
  preceding argument. Keep related explanation together. If a method is
  introduced, interrupted by background, and then reintroduced, reconsider the
  order before polishing individual sentences.
- **Introduction.** Give the problem, aim, model distinction, general approach,
  and scope. Explain what the approximation approximates and its basic idea.
  Defer equations, derivations, fitted parameters, and theorem conditions unless
  essential to understanding the aim. A short roadmap should describe the actual
  section structure using cross-references.
- **Models and theory.** Define the objects and observables precisely, then
  develop the results needed by the investigation. Show the reasoning behind
  substantive steps; do not compress a derivation merely to match the
  introduction's brevity.
- **Methods and results.** Explain why the experimental design tests the stated
  questions. Present results by those questions, with direct comparisons and
  interpretation, rather than narrating notebook execution or listing every
  output. Keep software commands and incidental implementation details in the
  repository guides or experiment appendix.
- **Discussion and conclusion.** Explain what the evidence supports, where the
  approximation fails or remains uncertain, and how that answers the aims.
  Avoid repeating the results section or introducing unsupported new findings.
  Write the abstract from the completed evidence.
- Keep assumptions, definitions, and methodological choices needed to judge a
  claim beside that claim in the main text. Move lengthy algebra, auxiliary
  checks, and detailed settings to appendices with explicit references. Define
  an idea fully where it belongs, then use brief reminders instead of repeating
  its motivation throughout the paper.

## Mathematical exposition and references

- Introduce symbols with their meaning and role before using them in a
  derivation. Specify the model, limit, and conditioning when they matter.
  Distinguish counts from fractions and survival probabilities from the
  distribution of sizes conditional on survival.
- Explain why an equation is introduced, justify nontrivial transformations,
  and interpret the resulting expression. Intuition should clarify the formal
  argument without substituting for it. Routine algebra can be omitted when the
  route remains recoverable; explain consequential assumptions such as
  independence, branch selection, or exchanging limits.
- Separate established theorems, exact local calculations, assumptions needed
  to apply them, theoretical predictions, and numerical observations. State a
  qualification where it changes the claim rather than attaching a generic
  disclaimer later. Follow the model-specific distinctions in `AGENTS.md` and
  the research plan; a result for one ensemble does not automatically transfer
  to another.
- Verify the relevant passage of a primary source before attributing a result
  or method to it. Check its assumptions and model against the claim being made.
  Distinguish a construction motivated by a paper from one established there.
  A descriptive name coined for this work must not be presented as an established
  method from the literature.
- Put citations next to the claims they support. Do not cite the course project
  manual in the paper. In the introduction, ordinary paper citations suffice;
  avoid author-name narration and exact theorem numbers. In theoretical sections
  or appendices, give precise theorem references and assumptions when needed to
  justify an application. Bibliography membership alone does not support a claim.

## Computational evidence and interpretation

- Describe the ensemble, parameter and size ranges, survival event, and relevant
  sampling or conditioning choices so the reader can tell what a result means.
  Explain what is fixed by theory, what is calibrated from data, and what is
  evaluated independently. Follow the research plan's validation protocol.
- Identify the evidence behind numerical claims using reproducible notebook
  outputs, figures, or tables. Give relevant sample counts and uncertainty;
  distinguish variation between graphs from uncertainty in an estimated mean
  or probability. Respect paired or clustered observations in the interpretation.
- Explain what a figure demonstrates and how it relates to the question, rather
  than only describing its curves. Label illustrative examples, theoretical
  predictions, and simulation measurements clearly in captions. Specify
  conditioning and the meaning of error bars when present.
- Qualify conclusions by the sizes, parameter range, and precision actually
  studied. Agreement in a plot is not a proof, and passing implementation tests
  does not establish a scientific result. Keep exploratory observations separate
  from independent validation. Report discrepancies and inconclusive evidence
  directly; do not force a positive conclusion or a causal explanation the
  comparison cannot support.

## Reviewing a draft

1. Read the requested section together with its neighbours, the research plan,
   and the relevant calculations or sources. Identify its role and the evidence
   available. Preserve approved material outside the requested revision.
2. Review the argument before editing sentences. Check that definitions precede
   use, model and method roles are explicit, and the progression answers the
   research question. Remove duplicated explanations and relocate misplaced
   detail without losing necessary reasoning.
3. Read for clarity and accuracy together. Resolve vague referents, unexplained
   jargon, and overly compressed steps. Check notation, claim strength, source
   support, and consistency between prose, equations, and figures.
4. For manuscript edits, run `make report`, resolve new citation or reference
   issues, and inspect the affected PDF pages. Do not rerun experiments for a
   wording change. Documentation-only edits need link and consistency checks,
   not a PDF rebuild or simulation run.
