# Evaluation

## 1. Purpose

BehavClone is an evidence-oriented system for surfacing suspiciously similar
programming submissions when students may organize equivalent functionality
using different files, classes, methods, and internal program structures.

The evaluation asks a narrower question than whether BehavClone can determine
plagiarism:

> What information do BehavClone's structural, cohort-relative, and behavioral
> evidence channels provide under controlled transformations, synthetic
> false-positive pressure, and an authentic external dataset?

BehavClone does not infer authorship or intent and does not produce a
plagiarism verdict. Similarity is treated as evidence for human review rather
than as a decision.

The evaluation therefore preserves evidence channels separately instead of
combining them into a single plagiarism score.

---

## 2. Evaluation principles

The experiments follow five principles.

First, the unit of analysis is the complete submission. Files, classes, and
methods are internal structures rather than required correspondence keys.

Second, structural representations are evaluated separately. Raw,
identifier/literal-normalized, and structural similarities are not assumed to
have identical robustness or false-positive behavior.

Third, cohort-relative evidence remains separate from pairwise similarity.
Rarity is intended to provide context about whether shared structural features
are common or unusual within a cohort.

Fourth, behavioral evidence is restricted to imported observations. BehavClone
does not execute untrusted student programs in the current prototype.

Fifth, unfavorable and null results are retained. No experiment is used to
derive a universal plagiarism threshold, and no result is interpreted as proof
of plagiarism.

---

## 3. Research questions

The current evaluation is organized around four research questions.

### RQ1: Architecture-flexible structural matching

Can whole-submission fragment matching preserve similarity evidence when
related programs undergo transformations such as identifier renaming, method
reordering, class renaming, file renaming, dead-code insertion, or class
splitting?

### RQ2: Cohort-relative structural evidence

Can cohort-level feature frequency provide additional context when pairwise
structural similarity alone is ambiguous?

### RQ3: Incorrect-behavior evidence

Can shared incorrect behavior provide an independent evidence channel when
structural evidence is ambiguous?

### RQ4: False-positive and authentic ambiguity

How does BehavClone behave on independent controls and on an external cohort
labeled non-plagiarized by its dataset, and how does that behavior compare
descriptively with JPlag?

These questions concern evidence quality and system behavior. They do not ask
whether BehavClone can autonomously determine plagiarism.

---

## 4. System under evaluation

The current prototype analyzes Java submissions.

Each complete submission is parsed and decomposed into method-level fragments.
Fragments are represented in three ways:

- raw token representation;
- normalized token representation; and
- structural representation.

Submission comparison uses maximum-weight one-to-one fragment assignment.
Consequently, fragment correspondence is not determined by method position,
filename, class name, or method name.

Starter-code exclusion is conservative. Exact or identifier-renamed starter
fragments can be excluded while changes to literals or operators remain
observable.

Cohort evidence uses submission-level document frequency. Structural n-grams
are deduplicated within each submission before cohort frequency is computed.

Behavioral evidence is imported separately. Shared correct behavior is not
treated as suspicious evidence. The current behavioral channel records shared
failures and, separately, identical wrong outputs.

No combined plagiarism score is produced.

---

## 5. Controlled transformation benchmark

### 5.1 Design

The controlled benchmark contains a base implementation, six related
transformations, and three controls.

The related transformations are:

- identifier rename;
- method reorder;
- class rename;
- file rename;
- dead-code insertion; and
- class split.

The controls include unrelated implementations and an intentionally difficult
lookalike.

The benchmark is synthetic. Its purpose is to isolate known transformations,
not to estimate real-world plagiarism accuracy.

### 5.2 Structural findings

Whole-submission matching preserved maximal normalized similarity for the
identifier-renamed, method-reordered, class-renamed, file-renamed, and
class-split examples.

The class-split case is particularly relevant to the architecture-flexible
design: related functionality can be distributed differently across files
without requiring filename correspondence.

Dead-code insertion reduced BehavClone's normalized similarity rather than
remaining perfectly invariant.

The lookalike control also reached maximal normalized and structural
similarity. This is an important negative result: transformations that increase
invariance can also remove distinctions useful for rejecting unrelated
programs.

Raw similarity retained more identifier-specific information. For example, the
identifier-renamed pair did not receive the same raw score as the base
implementation.

These results demonstrate a robustness/discriminability tradeoff rather than a
single representation that dominates all others.

### 5.3 Interpretation

The controlled benchmark supports the mechanism BehavClone was designed to
provide: fragment correspondence can survive several changes in program
organization without positional file or method matching.

It does not establish that the same robustness generalizes to arbitrary
student programs or arbitrary refactorings.

---

## 6. Scaled synthetic false-positive evaluation

### 6.1 Design

A larger synthetic cohort contains 16 submissions organized into four
provenance families with four variants per family.

Across all unordered pairs there are:

- 120 total pairs;
- 24 within-family related pairs; and
- 96 cross-family controls.

The families intentionally implement different source-level semantics.
Therefore, they are useful as structural false-positive controls but should not
be interpreted as submissions to one naturally shared programming assignment.

### 6.2 Raw representation

On this specific synthetic cohort, raw similarity separated the provenance
families cleanly.

All 24 within-family related pairs appeared before the first cross-family
control in the frozen ranking.

This should not be generalized into a claim that raw tokens are universally
superior. The controlled transformation benchmark already demonstrates that
raw similarity is less invariant to identifier renaming.

Instead, the result exposes a tradeoff: retaining lexical information can
improve discrimination in some cohorts while reducing robustness to benign or
adversarial renaming.

### 6.3 Normalized and structural representations

Normalization increased transformation invariance but also created substantial
cross-family collisions.

All 24 related pairs reached normalized similarity 1.0. However, 48 of the 96
cross-family controls also reached normalized similarity 1.0.

Structural representation showed a similar discriminability problem in this
cohort.

This is a central negative finding. Strong normalization can collapse programs
that are distinct under the provenance-family labels into identical or nearly
identical representations.

A high structural similarity score therefore cannot be treated as a plagiarism
verdict.

---

## 7. Cohort-relative evidence

The scaled experiment also evaluated cohort-relative structural evidence using
normalized structural n-grams.

Among the normalized-similarity collisions, pair-specific feature count did not
separate the related and control groups:

- all 24 related collision pairs had pair-specific feature count 0; and
- all 48 control collision pairs had pair-specific feature count 0.

This is a null result for that evidence field.

Broader rarity statistics retained some information for some related pairs.
Related pairs extended to higher shared-feature counts and higher maximum and
mean rarity values than the collision controls in parts of the synthetic
cohort.

However, rarity did not resolve all structural collisions.

The appropriate interpretation is therefore that cohort-relative evidence can
provide additional context in some cases, while pair-specific rarity is not a
general solution to structural false positives.

---

## 8. Controlled behavioral evidence

### 8.1 Design

The scaled behavioral fixture contains 80 imported observations: 16 synthetic
submissions across five tests.

The fixture was constructed to include:

- passing observations;
- shared failures;
- identical wrong outputs;
- different wrong outputs on the same failing test; and
- related submissions with no shared failure.

The observations are controlled imported outcomes. They are not results from
executing the four synthetic source families against one naturally common
assignment specification.

### 8.2 Findings

Among the 24 related normalized-similarity collisions:

- 8 pairs shared at least one failing test; and
- 4 pairs shared an identical wrong output.

Among the 48 cross-family control collisions:

- 0 pairs shared a failing test; and
- 0 pairs shared an identical wrong output.

In this controlled fixture, behavioral evidence therefore supplied additional
discriminating information for some structurally ambiguous pairs.

It did not solve the false-positive problem. Sixteen of the 24 related
collision pairs had no shared-failure evidence.

### 8.3 Interpretation

The result supports a deliberately limited hypothesis:

> When structural similarity is ambiguous, shared incorrect behavior can
> provide additional independent evidence when such behavior is present.

The experiment does not establish that shared failures imply plagiarism.
Independent students can make the same mistake, tests can be correlated, and
common misconceptions can produce common wrong outputs.

Behavior therefore remains a separate evidence channel for human review.

---

## 9. Authentic external evaluation

### 9.1 Dataset and frozen cohort

The authentic experiment uses the IR-Plag dataset.

The dataset repository was pinned before measurement, and cohort selection was
performed before pairwise similarity analysis.

The primary cohort is:

- case: `case-01`;
- dataset category: `non-plagiarized`;
- language: Java;
- submissions: 15; and
- unordered pairs: 105.

The dataset-provided non-plagiarized label is used for false-positive and
similarity-ambiguity analysis. It should not be interpreted as independent
verification of every author's intent.

The 15 source files are small, with one source file per selected submission in
the frozen manifest.

No behavioral evidence is available for this authentic cohort.

### 9.2 BehavClone similarity distribution

BehavClone normalized similarity had:

- minimum approximately 0.558;
- median 1.0;
- mean approximately 0.917;
- maximum 1.0; and
- 55 of 105 pairs exactly equal to 1.0.

Raw similarity also contained 55 maximal pairs.

Structural similarity contained 56 maximal pairs.

The large maximal groups demonstrate substantial similarity ambiguity within
this dataset-provided non-plagiarized cohort.

### 9.3 JPlag comparison

The frozen primary JPlag baseline uses JPlag 6.3.0 without JPlag normalization
or frequency analysis.

JPlag average similarity had:

- minimum 0.0;
- median 1.0;
- mean approximately 0.737;
- maximum 1.0; and
- 66 of 105 pairs exactly equal to 1.0.

JPlag maximum similarity had 78 of 105 pairs exactly equal to 1.0.

BehavClone and JPlag scores are not mathematically equivalent. The comparison
is therefore descriptive rather than a direct score calibration.

Both systems nevertheless exhibit large high-similarity tie groups on this
cohort.

### 9.4 Rank association and ties

Using tie-aware average ranks, the Spearman association between BehavClone
normalized similarity and JPlag average similarity is approximately:

`rho = 0.928`

This indicates strong overall rank association in this cohort.

However, rank interpretation is constrained by the large exact-score ties.
BehavClone normalized similarity has 55 maximal pairs, while JPlag average
similarity has 66.

All 55 BehavClone normalized maximal pairs are also in the JPlag-average
maximal set. JPlag has 11 additional maximal-average pairs.

Because deterministic top-K lists must arbitrarily order many exactly tied
pairs, lexical top-K overlap is not treated as unique pair-level ranking
evidence.

### 9.5 Cohort evidence in the authentic experiment

BehavClone's pair-specific cohort signal is sparse in this cohort.

Only 2 of 105 pairs have nonzero pair-specific feature counts.

More importantly, all 55 BehavClone normalized maximal-similarity pairs have
the same pair-specific count of zero.

The broader cohort statistics are also constant across those 55 maximal pairs
in the frozen analysis.

Cohort-relative evidence therefore does not discriminate among BehavClone's
largest maximal-similarity group in this authentic experiment.

This negative result is retained rather than tuned away.

### 9.6 Architecture limitation of the authentic cohort

Every pair in the selected authentic cohort contains one fragment on each side,
one matched fragment, and full fragment coverage.

Consequently, this authentic experiment does not exercise the multi-fragment
assignment problem that motivates BehavClone's architecture-flexible matching.

The controlled experiments provide evidence about method permutation and
cross-file/class restructuring. The authentic experiment instead contributes
evidence about similarity ambiguity and false-positive pressure on small real
programs.

These two forms of evidence should not be conflated.

---

## 10. Controlled versus authentic evidence

The experiments answer different parts of the research questions.

The controlled transformation benchmark demonstrates mechanism-level behavior.
It shows that global fragment assignment can preserve correspondence under
several deliberately constructed structural transformations.

The scaled synthetic experiment stress-tests discrimination. It reveals that
normalization and structural abstraction can create substantial collisions,
and that pair-specific cohort rarity does not necessarily resolve them.

The controlled behavioral fixture shows that incorrect-behavior evidence can
add independent information when it is present, while also showing that many
related pairs may have no such evidence.

The authentic IR-Plag experiment adds external realism for false-positive and
similarity-ambiguity analysis. Both BehavClone and JPlag produce large
high-similarity tie groups in the selected dataset-provided non-plagiarized
cohort.

No single experiment supports all BehavClone claims.

---

## 11. Comparison with JPlag

The current evaluation does not attempt to establish general superiority over
JPlag.

Modern JPlag supports submission-level comparison, multiple source files, base
code, normalization, frequency analysis, and other configurable analysis
features. BehavClone should therefore not be characterized as solving a simple
same-filename limitation in JPlag.

The controlled experiments do expose operational differences.

For example, the synthetic class-split transformation retained maximal
BehavClone normalized similarity in the frozen benchmark while the tested
JPlag configurations did not retain similarity for that specific example.

Conversely, JPlag normalization changed the result of the synthetic dead-code
case, demonstrating that conclusions about a baseline depend on its
configuration.

The authentic experiment also contains pair-level disagreements between the
systems even though their overall rankings are strongly associated.

These observations motivate feature-by-feature comparison rather than claims
that one similarity value is directly equivalent to another.

A formal related-work and current-system review is required before making a
scientific novelty claim.

---

## 12. Threats to validity

### Synthetic construction

Controlled transformations are intentionally simple and cannot represent the
full diversity of real student code.

The scaled provenance families are also synthetic and implement different
semantics. They provide structural controls rather than a natural common
assignment cohort.

### Small authentic programs

The selected IR-Plag case contains only 15 submissions and 105 pairs.

The selected programs are small and reduce to one BehavClone fragment each.
They therefore do not test the architecture-flexible multi-fragment matching
problem on authentic code.

### Dataset labels

The authentic analysis relies on the dataset-provided `non-plagiarized`
category. The experiment does not independently infer or verify author intent.

### Baseline configuration

JPlag behavior depends on configuration. The primary authentic baseline is a
frozen standard configuration without normalization or frequency analysis.
Results should not be generalized to every possible JPlag configuration.

### Ties

Large exact-score groups occur in the authentic experiment. Deterministic
ordering inside a tie can change top-K membership without changing any
similarity value.

For this reason, tie structure and tie-aware rank association are more
informative than a lexically tie-broken top-K list.

### Behavioral availability

Behavioral evidence is controlled and synthetic in the current evaluation.
The authentic cohort does not provide an independently established common set
of imported behavioral observations.

The strongest differentiating behavioral hypothesis therefore still requires
evaluation on an appropriate authentic common-assignment dataset.

### Thresholds

No universal threshold is derived from these experiments.

Threshold behavior is expected to depend on assignment design, cohort
composition, representation, starter code, and analysis configuration.

---

## 13. What the current evidence supports

The current evidence supports several bounded conclusions.

Whole-submission maximum-weight fragment assignment can preserve similarity
under the specific architecture and naming transformations represented in the
controlled benchmark.

Normalization improves invariance to some transformations but can substantially
reduce discriminability.

Cohort-relative rarity can add contextual information, but the current
pair-specific feature signal fails to distinguish important collision groups in
both the scaled and authentic experiments.

Shared incorrect behavior can provide an independent evidence channel in a
controlled fixture when structural evidence is ambiguous.

Authentic evaluation shows substantial similarity ambiguity for both BehavClone
and the frozen JPlag baseline on the selected IR-Plag non-plagiarized cohort.

Together, these results support an evidence-oriented workflow in which
structural similarity, cohort context, and behavioral observations remain
inspectable rather than being collapsed into an automatic plagiarism verdict.

---

## 14. What the current evidence does not support

The current evaluation does not establish:

- plagiarism detection accuracy;
- author intent;
- a universal similarity threshold;
- general superiority over JPlag;
- that rare shared failures imply plagiarism;
- that cohort rarity eliminates false positives;
- that behavioral evidence always exists for related submissions;
- authentic robustness to architecture-flexible multi-fragment refactoring; or
- scientific novelty relative to the full research literature.

These questions require additional evidence or formal related-work analysis.

---

## 15. Reproducibility

The evaluation artifacts are committed with deterministic generation and
regression checks.

The authentic evaluation was frozen in stages:

1. evaluation protocol;
2. deterministic cohort selection;
3. BehavClone measurement;
4. portable canonical serialization;
5. JPlag measurement protocol;
6. JPlag measurement;
7. tie-aware authentic analysis protocol; and
8. authentic analysis artifact.

The authentic analysis artifact is independently reproducible byte-for-byte
from the frozen BehavClone and JPlag pairwise results.

Its canonical SHA-256 is:

`E48CF0F9A8A5C2A50EA4F78B6DE408E9C492E727AB5BA62754B927A382E249A0`

This reproducibility chain is intended to make post-hoc changes to unfavorable
results visible rather than silently replacing them.

---

## 16. Next research step

The next research task is not threshold tuning.

The next step is a formal related-work and system-capability review covering
JPlag and relevant source-code similarity and plagiarism-detection research.

That review should determine which BehavClone mechanisms are established prior
art, which are engineering combinations of existing ideas, and whether the
integration of architecture-flexible structural correspondence,
cohort-relative evidence, and shared incorrect-behavior evidence supports a
defensible research contribution.

Until that review is complete, BehavClone should be described as a research
prototype with experimentally characterized design choices rather than as a
novel plagiarism detector.
