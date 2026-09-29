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
