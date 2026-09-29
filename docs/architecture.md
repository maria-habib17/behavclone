# Architecture

## Processing Pipeline

Assignment
    |
    +-- Configuration
    +-- Starter Code
    +-- Test Results
    |
    +-- Submissions
            |
            v
        Ingestion
            |
            v
       Java Parsing
            |
            v
    Fragment Extraction
            |
            v
      Normalization
            |
            v
    Starter Exclusion
            |
            v
   Fragment Comparison
            |
            v
 Bipartite Fragment Matching
            |
       +----+----+
       |         |
       v         v
 Structural    Test
 Evidence      Evidence
       |         |
       v         v
 Cohort       Error
 Analysis     Rarity
       |         |
       +----+----+
            |
            v
      Evidence Model
            |
            v
     Instructor Review

## Primary Design Principle

The unit of analysis is the complete submission, not the filename.

Files, classes, and methods are internal structural components used to
construct evidence.

BehavClone must not require direct filename, class-name, method-name, or
method-position correspondence between two submissions.

## Evidence Philosophy

BehavClone separates measured evidence from instructor conclusions.

The system may report:

- structural similarity;
- cohort percentile;
- matched fragments;
- shared failures;
- rare shared failures;
- identical incorrect outputs.

The system must not report an unsupported probability that plagiarism occurred.
