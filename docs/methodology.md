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
