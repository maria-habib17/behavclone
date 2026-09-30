# JPlag-Centered Related Work and Contribution Boundary

## 1. Purpose

BehavClone is an evidence-oriented research prototype for analysing similarity
between programming-assignment submissions.

This document positions its current mechanisms relative to established source
code plagiarism and program-similarity approaches. Its purpose is not to claim
scientific novelty prematurely. Instead, it separates:

- established prior art;
- mechanisms adapted or combined by BehavClone;
- engineering design choices;
- hypotheses that still require stronger empirical validation.

BehavClone does not infer authorship or intent and does not produce a
plagiarism verdict.

## 2. Source-code plagiarism detection

Source-code plagiarism detection has a long research history. Existing systems
use representations including lexical tokens, fingerprints, syntax trees,
dependency structures, execution properties, and combinations of these
representations.

Consequently, BehavClone does not claim that source normalization, structural
similarity, behavioral analysis, or cohort-relative comparison is individually
new.

The relevant question is narrower: whether BehavClone's particular
evidence-oriented combination provides useful information for human review,
especially when programming assignments permit substantial freedom in program
architecture.

## 3. JPlag: principal baseline

JPlag is the principal established baseline used by BehavClone's current
experiments.

The original JPlag publication by Prechelt, Malpohl, and Philippsen describes
a language-aware token representation followed by pairwise comparison based on
Greedy String Tiling [1].

That paper also makes a historically important observation for BehavClone's
contribution boundary: instructors may notice suspicious similarity when two
programs produce the same unusual failure for a test input [1].

BehavClone therefore does not claim to have invented the intuition that shared
unusual failures can be informative during plagiarism review.

Instead, BehavClone investigates a systematic and deliberately limited
operationalization of related evidence: shared correct outcomes are excluded,
shared failures and identical incorrect outputs are represented explicitly,
their cohort rarity can be measured, and behavioral evidence remains separate
from structural similarity.

Modern JPlag is a mature source-code plagiarism and collusion detection system
that performs pairwise comparison across collections of submissions.

Modern JPlag should not be characterized as requiring students to use matching
filenames, class names, or a single common source file. Submission directories
can contain multiple source files.

Current JPlag functionality relevant to BehavClone includes:

- language-aware tokenization;
- comparison of complete submission directories;
- base-code handling;
- configurable minimum token-match length;
- token normalization for Java and C++;
- CSV export of pairwise similarity measurements;
- match merging;
- frequency analysis for highlighting rare matches [2].

JPlag 6.3.0 additionally introduced weighting of matches based on their rarity
within frequency analysis [3].

The presence of normalization and frequency analysis is particularly important
for BehavClone's contribution boundary. Identifier normalization and
cohort-relative rarity are therefore not claimed as independently novel
mechanisms.

BehavClone and JPlag also report different similarity quantities. BehavClone's
fragment-assignment means and JPlag's average/max similarities are not
mathematically interchangeable. Experimental comparisons in this repository
therefore treat them as side-by-side evidence rather than equivalent scores.

### Controlled observations

The controlled BehavClone/JPlag experiments in this repository showed several
configuration-dependent differences.

In the small controlled class-split example, BehavClone's whole-submission
fragment matching retained maximal normalized similarity while the evaluated
JPlag configurations did not.

Conversely, JPlag normalization changed the result of the controlled dead-code
case substantially. This prevents using that transformation as evidence of a
general BehavClone advantage.

These are operational observations on deliberately small examples, not
evidence that either system is generally superior.

## 4. Structural and architecture-aware comparison

Structural program comparison predates BehavClone. Prior work has represented
programs through syntax trees, dependence graphs, control/data relationships,
and other structural abstractions.

Research systems have also investigated robustness to transformations such as:

- identifier renaming;
- statement or method reordering;
- extraction and inlining;
- control-flow modification;
- structural rewriting.

BehavClone therefore does not claim that AST-based similarity,
transformation-resistant comparison, or architecture-aware analysis is itself
a new research direction.

BehavClone's current structural design instead uses methods and constructors as
fragments, creates raw, normalized, and structural representations, and solves
a global one-to-one fragment assignment across complete submissions.

The assignment is independent of filename, class name, method name, and
fragment position.

This is an implementation and experimental design distinction. A formal claim
that the exact combination is scientifically novel would require a more
exhaustive literature review than the current project has established.

## 5. Behavioral analysis as secondary prior art

JPlag remains the principal comparison baseline in this project.

Behavioral program-similarity research is relevant only to the contribution
boundary: BehavClone must not imply that analyzing program behavior for
plagiarism or similarity is itself a new idea.

Systems such as BPlag have investigated substantially different behavioral
approaches, including symbolic execution and behavioral graph
representations [4].

BehavClone does not reproduce that approach and does not experimentally
benchmark itself against BPlag.

Instead, the current prototype imports externally obtained test outcomes and
uses a deliberately narrower behavioral evidence model: shared correct
outcomes are excluded, while shared failures and identical incorrect outputs
can be retained as separate evidence for human review.

All empirical baseline comparisons currently reported by BehavClone are
therefore BehavClone-versus-JPlag comparisons, not BehavClone-versus-BPlag
comparisons.

## 6. Correct behavior versus incorrect behavior

Correct input/output agreement is expected when multiple students successfully
implement the same specification.

BehavClone therefore deliberately excludes shared correct outcomes from its
behavioral evidence.

Its current behavioral channel records:

- tests failed by both submissions;
- cases where both submissions produce the same incorrect output;
- cohort-relative rarity of shared failures;
- cohort-relative rarity of identical wrong outputs.

The working hypothesis is that shared incorrect behavior can sometimes provide
complementary information when structural evidence is ambiguous.

This is not equivalent to saying that a shared mistake demonstrates copying.

Independent students can make the same mistake, particularly when an
assignment naturally induces common misconceptions or boundary-condition
errors. Shared incorrect behavior is therefore retained as evidence for human
review rather than converted into a plagiarism verdict.

## 7. Cohort-relative evidence

The informativeness of a shared program feature depends partly on how common it
is within the assignment cohort.

BehavClone records document-frequency-style structural rarity separately from
pairwise similarity.

However, rarity and frequency analysis are not unique to BehavClone. Current
JPlag includes explicit frequency analysis for rare matches, and statistical or
corpus-relative weighting has broader precedent in information retrieval and
similarity analysis.

The BehavClone research question is therefore not whether rare features can be
weighted. It is whether cohort-relative structural evidence is useful as an
interpretable channel alongside global structural correspondence and
behavioral evidence.

Current experiments show that it is not universally discriminative.

In the scaled collision experiment, pair-specific structural rarity was zero
for both all 24 related maximal-similarity pairs and all 48 control
maximal-similarity pairs.

In the authentic IR-Plag case-01 experiment, pair-specific evidence was nonzero
for only 2 of 105 pairs and did not distinguish any of BehavClone's 55
maximal-normalized-similarity pairs.

These negative results are retained as part of the contribution boundary.

## 8. Multi-signal evidence

BehavClone currently maintains three conceptually distinct evidence channels:

1. structural correspondence;
2. cohort-relative structural context;
3. imported incorrect-behavior evidence.

The system intentionally does not collapse these channels into a single
plagiarism probability or verdict.

This separation is an engineering and research-design choice motivated by the
different meanings and failure modes of the signals.

For example, two submissions may be structurally very similar while sharing no
observed incorrect behavior. Alternatively, a shared failure may be common
across the cohort and therefore weak evidence.

Keeping the channels separate makes these distinctions visible to a reviewer.

The project does not currently establish that this evidence architecture is
scientifically novel. Its value must instead be evaluated empirically.

## 9. Relationship to the current experiments

The controlled transformation experiments support mechanism-level claims about
the current implementation.

They show that the global fragment-assignment design can remain stable under
several synthetic transformations, including identifier, class, file, and
method changes and a controlled class split.

The scaled synthetic experiment also exposes an important limitation:
normalization can improve transformation invariance while reducing
discriminability. In that experiment, all 24 related pairs reached normalized
similarity 1.0, but so did 48 of 96 cross-family controls.

The controlled behavioral fixture provides evidence that behavioral
observations can add information when present. Among normalized structural
collisions, shared failures occurred for 8 of 24 related pairs and 0 of 48
controls, while identical wrong outputs occurred for 4 of 24 related pairs and
0 controls.

However, 16 of the 24 related collision pairs had no shared-failure evidence.
Behavior therefore did not solve the false-positive problem.

The authentic IR-Plag case-01 experiment provides external false-positive
pressure. Under the dataset-provided non-plagiarized label, BehavClone
normalized similarity was exactly 1.0 for 55 of 105 pairs and JPlag average
similarity was exactly 1.0 for 66 of 105 pairs.

Their rankings were strongly associated, with Spearman rho approximately
0.928, but both systems produced large tied groups.

The authentic cohort contained one fragment per submission and no behavioral
observations. It therefore does not validate BehavClone's architecture-flexible
matching or incorrect-behavior hypothesis on authentic multi-file student
submissions.

## 10. Current contribution boundary

Based on the implementation, experiments, and related work reviewed so far,
BehavClone should not be presented as inventing:

- source-code plagiarism detection;
- token-based similarity;
- identifier normalization;
- structural or AST-based similarity;
- transformation-resistant program comparison;
- behavioral plagiarism detection;
- rarity or frequency analysis;
- human review of similarity evidence.

A defensible current description is:

> BehavClone investigates an evidence-oriented architecture for
> programming-assignment similarity in which permutation-resistant
> whole-submission structural correspondence, cohort-relative structural
> context, and shared incorrect-behavior evidence are maintained as separate,
> interpretable channels for human review.

A corresponding research hypothesis is:

> When correct behavior is expected across an assignment cohort, shared
> incorrect behavior, particularly uncommon shared failures or identical wrong
> outputs, may provide complementary evidence for structurally ambiguous pairs
> without treating functional correctness itself as similarity evidence.

These statements describe the research direction. They do not establish
scientific novelty.

## 11. Strongest unresolved research question

The strongest unresolved empirical question is whether shared incorrect
behavior provides useful complementary evidence on authentic submissions to a
common assignment.

The current behavioral result is synthetic.

The current authentic result has no behavioral observations.

Consequently, the project cannot yet claim that behavioral evidence improves
review quality on real student submissions.

An especially valuable future evaluation would use an ethically and legally
available authentic assignment cohort with:

- multiple independent submissions;
- a common specification;
- common instructor tests;
- retained incorrect outputs;
- enough submissions to estimate failure rarity;
- independently justified provenance labels where possible.

Such an experiment should be designed before inspecting pairwise behavioral
results.

## 12. Scientific novelty status

Scientific novelty remains an open question.

The current review establishes substantial prior art for each broad mechanism
used by BehavClone. The potentially distinctive aspect is the particular
evidence architecture and the narrow treatment of shared incorrect outcomes as
complementary, cohort-aware review evidence.

Before making a formal novelty claim, the project would require a deeper
systematic review specifically targeting prior systems that combine:

- structural source similarity;
- cohort-relative evidence;
- test-result or failure-pattern evidence;
- identical incorrect outputs;
- separate rather than fused evidence channels.

Until that review is complete, BehavClone should be described as a research
prototype investigating this combination rather than as a novel plagiarism
detector.

## 13. References and source basis

JPlag is the principal baseline for BehavClone. References [1]-[3] therefore
form the primary source basis for claims about the baseline.

1. L. Prechelt, G. Malpohl, and M. Philippsen, "Finding Plagiarisms among a
   Set of Programs with JPlag," *Journal of Universal Computer Science*,
   vol. 8, no. 11, pp. 1016-1038, 2002.
   DOI: 10.3217/jucs-008-11-1016.

2. JPlag project, "How to Use JPlag," official JPlag documentation.
   The current CLI documents Java/C++ normalization, CSV export, base-code
   configuration, match merging, and frequency analysis for rare matches.

3. JPlag project, "JPlag v6.3.0," official release notes, 11 December 2025.
   The release adds frequency-based weighting of matches according to rarity.

4. H. Cheers, Y. Lin, and S. P. Smith, "Academic Source Code Plagiarism
   Detection by Measuring Program Behavioral Similarity," 2021.
   This work is included only as secondary prior art establishing that
   behavioral plagiarism analysis predates BehavClone; it is not BehavClone's
   experimental baseline.

### Citation boundary

Reference [1] is particularly important because the original JPlag paper
already notes that identical unusual test failures can draw an instructor's
attention.

BehavClone's research hypothesis is therefore not that shared incorrect
behavior is a newly discovered plagiarism signal.

The narrower question is whether systematically excluding expected correct
agreement while retaining shared failures, identical wrong outputs, and their
cohort context as a separate evidence channel provides useful complementary
information when structural similarity is ambiguous.

This document intentionally avoids assigning scientific novelty to that
combination until a deeper targeted literature search establishes whether the
same evidence architecture has already been studied.
