# BehavClone

**Evidence-oriented similarity analysis for architecture-flexible programming assignments.**

BehavClone is an experimental open-source system for analyzing similarities
between programming-assignment submissions when students are free to choose
different files, classes, method names, and program structures.

Rather than making plagiarism decisions, BehavClone surfaces unusual
submission pairs and presents interpretable evidence for instructor review.

## Core Ideas

- Whole-submission analysis
- Architecture-independent fragment matching
- Method-permutation resistance
- Starter-code exclusion
- Cohort-relative similarity
- Rare shared-failure analysis
- Identical incorrect-output analysis
- Human-in-the-loop review

## Research Questions

1. How robust is fragment matching to structural transformations?
2. Can cohort-relative evidence separate common assignment patterns from unusual similarity?
3. Do rare shared failures provide useful additional evidence?
4. How often are authentic solutions surfaced as highly similar?

## Initial Scope

Version 0.1 focuses on Java OOP assignments.

BehavClone does **not** automatically determine plagiarism.

All findings require instructor interpretation.

## Status

?? Early research prototype.

## Planned Pipeline

Assignment
? Submission ingestion
? Java parsing
? Fragment extraction
? Normalization
? Starter-code exclusion
? Fragment matching
? Cohort analysis
? Test evidence
? Instructor review

## License

MIT
