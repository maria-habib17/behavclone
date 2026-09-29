# Methodology

## Research Problem

Programming assignments with flexible object-oriented designs may produce
solutions implementing the same required behavior using different file
structures, classes, method names, and method decompositions.

This makes file-to-file and position-dependent similarity comparison difficult
to generalize.

BehavClone investigates architecture-independent fragment matching,
cohort-relative evidence, and shared unusual program behavior.

## Research Questions

### RQ1

How robust is whole-submission fragment matching to identifier renaming,
file renaming, class renaming, and method permutation?

### RQ2

Can cohort-relative structural evidence distinguish common assignment-induced
similarity from unusually similar implementations?

### RQ3

Does shared unusual incorrect behavior improve the ranking of structurally
similar submission pairs?

### RQ4

How frequently are independently produced submissions surfaced among highly
ranked candidate pairs?

## Initial Scope

Version 0.1 supports Java assignments.

The initial system:

- does not require matching filenames;
- does not require matching class names;
- does not require matching method names;
- does not depend on method order;
- supports starter-code exclusion;
- accepts imported automated-test results;
- reports evidence rather than plagiarism classifications.

## Unit of Analysis

The primary unit of analysis is the complete submission.

Methods are initially used as structural fragments.

A submission is therefore represented as a collection of fragments rather
than one flattened token sequence.

## Cohort-relative rarity evidence

Pairwise structural similarity alone does not indicate how unusual a shared
pattern is within an assignment cohort. Common assignment-shaped constructs
may independently occur in many submissions, while a shared feature observed
in only a small part of the cohort may provide different evidence for human
review.

BehavClone therefore models cohort rarity as a separate evidence channel rather
than folding it into the pairwise matching score.

### Feature representation

For the initial baseline, each non-starter method fragment is represented using
contiguous n-grams over normalized Java tokens. Identifier spelling is
abstracted by the normalizer. The n-gram size is an experimental parameter
rather than a fixed universal constant.

Features are deduplicated within each submission before cohort frequencies are
computed. Repeating the same feature multiple times in one submission therefore
does not increase its document frequency.

For a feature g, submission-level document frequency is:

    DF(g) = number of submissions containing g

Given a cohort containing N submissions, BehavClone reports the smoothed
inverse-document-frequency quantity:

    R(g) = ln((N + 1) / (DF(g) + 1)) + 1

A feature appearing in fewer submissions receives a larger rarity value. A
feature appearing throughout the cohort receives a smaller value.

### Interpretation

Rarity is not a plagiarism probability, verdict, or universal decision
threshold. It provides cohort context for shared normalized structure.

The current pipeline:

1. discovers complete submissions;
2. removes configured starter fragments;
3. extracts normalized token n-gram features;
4. computes submission-level document frequencies across the cohort;
5. performs the existing permutation-resistant fragment assignment using
   normalized pairwise similarity; and
6. attaches cohort-frequency and rarity evidence to the selected fragment
   correspondences.

Keeping pairwise similarity and cohort rarity separate makes their contribution
independently inspectable and supports later ablation experiments.

### Current limitations

The initial rarity baseline uses contiguous normalized token n-grams. Results
may vary with n-gram size, cohort size, assignment design, and the amount of
common required structure. Rare structure is not inherently suspicious, and
common structure is not inherently irrelevant. Both remain evidence for
instructor interpretation rather than automated conclusions.

Future evaluation should measure sensitivity to n-gram size and cohort
composition, compare alternative feature representations, and quantify whether
cohort-relative evidence improves false-positive surfacing on authentic
non-plagiarized submissions.

## Behavioral evidence from imported test outcomes

BehavClone treats externally observed program behavior as a separate evidence
channel. Version 0.1 does not execute untrusted student submissions. Instead,
it imports results produced by an instructor-controlled or otherwise external
test harness.

The baseline CSV representation records:

    submission,test,status,expected,actual

Each observation identifies one submission, one test, its PASS or FAIL status,
the expected output, and the observed output.

### Correct behavior is not similarity evidence

When an assignment specifies required input/output behavior, independently
correct submissions are expected to produce the same result. BehavClone
therefore does not treat shared successful tests or identical correct outputs
as behavioral similarity evidence.

The initial behavioral comparison surfaces a test only when both compared
submissions fail that test.

For a test t, BehavClone records the cohort-level failure frequency:

    DF_fail(t) = number of submissions that fail t

Given N submissions represented in the behavioral dataset, failure rarity is:

    R_fail(t) = ln((N + 1) / (DF_fail(t) + 1)) + 1

This describes how widespread the failure is within the observed cohort.

### Identical wrong outputs

Two submissions can fail the same test in different ways. BehavClone therefore
keeps shared failure and identical wrong output as distinct observations.

For a failed test t and observed wrong output o:

    DF_wrong(t, o) =
        number of submissions that fail t with exact observed output o

The corresponding rarity quantity is:

    R_wrong(t, o) =
        ln((N + 1) / (DF_wrong(t, o) + 1)) + 1

Exact wrong-output comparison is deliberately conservative in the initial
baseline: imported output strings are preserved rather than automatically
coerced or normalized. Alternative output-equivalence definitions can be
evaluated later as separate experimental conditions.

A frequently failed test may still contain a less common wrong-output pattern.
BehavClone therefore reports failure prevalence and wrong-output prevalence
separately instead of collapsing them into one behavioral score.

### Interpretation and safety boundary

Shared failures, identical wrong outputs, and their cohort rarity values are
evidence for human review. They are not plagiarism probabilities, verdicts, or
universal thresholds.

Behavioral evidence is also kept separate from structural similarity and
structural cohort rarity. This supports ablation experiments that can compare:

- structural matching alone;
- structural matching with cohort-relative structural evidence;
- behavioral failure evidence alone; and
- combinations of structural and behavioral evidence.

Version 0.1 imports test observations rather than executing student programs.
This keeps untrusted code execution outside the BehavClone analysis process.

### Current limitations

The behavioral baseline depends on the quality and coverage of the external
test suite. A shared failure can arise independently when a test targets a
common misconception, difficult edge case, ambiguous requirement, or common
implementation bug.

Likewise, an identical wrong output is not inherently evidence of copying.
Simple or highly constrained errors may naturally produce the same output in
multiple independent submissions.

Cohort composition also affects rarity values. Behavioral evidence should
therefore be interpreted alongside assignment design, test semantics,
structural evidence, and instructor review rather than in isolation.

Future evaluation should measure whether rare shared failures and rare
identical wrong outputs improve candidate surfacing on controlled synthetic
transformations and authentic non-plagiarized submissions.
