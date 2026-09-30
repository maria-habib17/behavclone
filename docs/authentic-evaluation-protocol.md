# Authentic Evaluation Protocol

## Purpose

This experiment examines how BehavClone surfaces similarity among
independently produced Java solutions to the same assignment
specification.

The primary purpose is false-positive and ambiguity analysis under
conditions that were not constructed specifically for BehavClone.

The experiment does not determine plagiarism, authorship, intent, or
academic misconduct.

## Unit of analysis

The unit of analysis is the complete submission.

Files, classes, methods, names, and source positions are internal
features of a submission and are not assumed to correspond across
different submissions.

## Dataset requirements

The primary cohort must contain at least 10 submissions answering the
same assignment specification.

Before repository use:

- submission identifiers must be anonymized;
- personally identifying student information must be removed;
- dataset provenance must be documented;
- use of the submissions must be ethically and legally permitted;
- starter code must be identified when provided by the assignment;
- submissions with unclear permission or provenance must be excluded;
- generated duplicates must not be used to inflate the cohort;
- known copied pairs must not be included in the primary
  false-positive cohort.

The repository does not need to publish source submissions when
licensing, privacy, institutional policy, or consent prevents
redistribution. Reproducibility limitations must be stated explicitly
in that case.

## Frozen BehavClone configuration

- Language: Java
- Unit: complete submission
- Fragment correspondence: maximum-weight one-to-one assignment
- Assignment metric: normalized similarity
- Cohort n-gram size: 4
- Structural channels:
  - raw similarity
  - normalized similarity
  - structural similarity
- Cohort evidence:
  - shared feature count
  - pair-specific feature count
  - maximum rarity
  - mean rarity
- Behavioral evidence, when common imported test results exist:
  - shared failure count
  - identical wrong-output count
  - maximum failure rarity
  - maximum wrong-output rarity

Evidence channels remain separate. No combined plagiarism score or
automated verdict is introduced.

## JPlag baseline

When JPlag can be run on the same source cohort, the primary baseline
uses the previously established standard configuration:

- Java language
- normalization disabled
- frequency analysis disabled
- all available pairwise comparisons retained
- average similarity recorded
- maximum similarity recorded

Additional JPlag configurations may be reported as secondary
ablations, but they must not replace the frozen primary baseline after
results are observed.

## Analysis

Report:

1. cohort size;
2. source-file and size characteristics where available;
3. all pairwise BehavClone structural evidence;
4. cohort-relative evidence as a separate channel;
5. behavioral evidence only when common test observations exist;
6. JPlag evidence separately when available;
7. the highest-similarity independently produced pairs;
8. cases where evidence channels disagree;
9. unfavorable, ambiguous, and null findings;
10. limitations caused by missing provenance, behavioral observations,
    labels, redistribution rights, or other unavailable information.

No universal threshold is selected from this cohort.

## Interpretation boundary

An unlabeled independently produced cohort can provide evidence about
false-positive surfacing and similarity ambiguity.

It cannot by itself estimate plagiarism-detection accuracy.

The experiment must not claim:

- a plagiarism verdict;
- authorship or intent;
- plagiarism accuracy from an unlabeled cohort;
- general superiority over JPlag;
- a universal similarity threshold.

Any manual inspection is evidence interpretation by a reviewer, not an
automated misconduct decision.
