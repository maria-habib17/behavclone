# Threat Model

BehavClone initially evaluates robustness against transformations commonly
encountered in programming assignments.

| Transformation | Expected Robustness |
|---|---|
| Formatting changes | High |
| Comment changes | High |
| Identifier renaming | High |
| Method renaming | High |
| Class renaming | High |
| File renaming | High |
| Method permutation | High |
| File permutation | High |
| Dead-code insertion | Medium |
| Statement reordering | Medium |
| Method extraction | Future evaluation |
| Method inlining | Future evaluation |
| Class splitting | Future evaluation |
| Class merging | Future evaluation |
| Control-flow rewriting | Future evaluation |
| Algorithm replacement | Future evaluation |

## Non-goal

BehavClone does not automatically determine whether academic misconduct
occurred.

Similarity may legitimately result from:

- assignment requirements;
- starter code;
- required APIs;
- common algorithms;
- teaching materials;
- independently selected implementation strategies.

Every surfaced pair therefore requires instructor interpretation.
