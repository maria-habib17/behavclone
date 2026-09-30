# BehavClone

> **Evidence-oriented similarity analysis for architecture-flexible programming assignments.**

BehavClone is a research-engineering prototype for investigating similarity between programming-assignment submissions when students may choose different files, classes, method names, identifiers, and program organization.

The central design decision is simple: **compare complete submissions, not corresponding filenames.** BehavClone extracts Java methods and constructors as fragments, builds multiple representations, compares candidate fragments across complete submissions, and computes a global one-to-one correspondence.

Structural similarity, cohort-relative context, and imported behavioral evidence remain **separate evidence channels for human review**. BehavClone does **not** decide whether plagiarism occurred.

---

## Why BehavClone?

Programming assignments often specify required behavior while leaving architecture open. Related implementations can therefore use different filenames, classes, methods, identifiers, method orderings, and file organization.

```text
Submission A                    Submission B

Calculator.java                 PricingEngine.java
    calculate()  ----------->       compute()

Validator.java                  Rules.java
    valid()      ----------->       check()

Receipt.java                    OutputEngine.java
    printReceipt() ----------->     output()
```

BehavClone investigates these correspondences across the **whole submission** rather than requiring matching filenames, class names, method names, or source positions.

## Research questions

1. **Architecture flexibility:** how robust is whole-submission fragment matching to identifier, method, class, filename, ordering, and organization changes?
2. **Cohort context:** can common assignment patterns be distinguished from unusually shared structure?
3. **Incorrect behavior:** can shared failures or identical wrong outputs add useful evidence when structural similarity is ambiguous?
4. **False-positive pressure:** how often can independently labelled or control solutions still appear highly similar?

These are evidence questions, not automated misconduct decisions.

---

## Evidence model

BehavClone deliberately avoids collapsing its signals into one opaque plagiarism score.

```text
                 Submission pair
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
   Structural        Cohort        Behavioral
    evidence         context         evidence
        |              |              |
 raw similarity   shared features  shared failures
 normalized sim.  pair-specific    identical wrong outputs
 structural sim.  features         failure rarity
 fragment matches rarity           output rarity
 coverage
        |              |              |
        +--------------+--------------+
                       |
                       v
                Human interpretation
```

There is currently **no combined plagiarism score, universal plagiarism threshold, or automatic verdict**.

---

## Architecture

```text
Assignment
    |
    v
Submission discovery
    |
    v
Recursive Java discovery
    |
    v
Tree-sitter parsing
    |
    v
Method / constructor fragments
    |
    +----------------+----------------+
    |                |                |
    v                v                v
 Raw tokens     Normalized tokens   Structural syntax
    |                |                |
    +----------------+----------------+
                     |
                     v
          Pairwise fragment similarity
                     |
                     v
       Maximum-weight one-to-one assignment
                     |
                     v
          Submission-level evidence
                     |
          +----------+----------+
          |                     |
          v                     v
   Cohort context       Imported test outcomes
```

The current exact assignment solver uses dynamic programming and is a research baseline rather than the final scalability design. See [`docs/architecture.md`](docs/architecture.md) for component boundaries and design rationale.

### Fragment representations

A fragment is currently one complete Java `method_declaration` or `constructor_declaration` identified with Tree-sitter.

**Raw tokens** preserve concrete lexical information, so identifier renaming affects them. **Normalized tokens** abstract identifiers and literals while retaining relevant Java syntax, keywords, punctuation, and operators. **Structural tokens** capture syntax-tree structure with reduced dependence on concrete identifier spelling.

Keeping these representations separate makes their trade-offs measurable.

### Similarity

The current fragment baseline uses symmetric Longest Common Subsequence similarity:

```text
                 2 * LCS(A, B)
similarity = ---------------------
                  |A| + |B|
```

The value lies between `0` and `1`. A high value means the selected representations are similar; it is **not** a probability that plagiarism occurred.

### Permutation-resistant matching

For fragments `A = {a1, ..., an}` and `B = {b1, ..., bm}`, BehavClone compares candidate fragments across the submissions and computes a maximum-weight one-to-one assignment rather than pairing fragments by filename or position.

```text
          b1      b2      b3

a1       0.31    1.00    0.42
a2       0.27    0.39    1.00
a3       1.00    0.33    0.29
```

This yields `a1 -> b2`, `a2 -> b3`, and `a3 -> b1`, providing resistance to simple method permutation and allowing cross-file correspondence.

---

## Starter-code exclusion

Instructor-provided starter material is a major confounder. BehavClone implements conservative starter-code exclusion using signatures that normalize identifiers while preserving literals, operators, keywords, and punctuation.

Exact or identifier-renamed starter fragments can therefore be excluded, while fragments with changed literals or operators remain available for analysis.

---

## Cohort-relative evidence

A feature appearing in nearly every submission should not necessarily carry the same evidential weight as an unusual shared feature. BehavClone computes submission-level document frequency and uses:

```text
R(g) = ln((N + 1) / (DF(g) + 1)) + 1
```

where `N` is the number of submissions and `DF(g)` is the number containing feature `g`.

Rarity remains a separate evidence channel. The experiments also preserve negative findings: pair-specific rarity was weak in the authentic cohort and did not discriminate the maximally similar BehavClone pairs.

---

## Behavioral evidence

Correct behavior is expected in a programming assignment and is not treated as suspicious by itself. BehavClone instead imports externally obtained test results and can represent shared failures, identical incorrect outputs, failure rarity, and incorrect-output rarity.

```text
Expected: 100

Submission A: 99
Submission B: 99
```

An unusual shared incorrect outcome may provide complementary evidence for review, but it remains evidence rather than proof of copying. The current prototype **imports** test outcomes; it does not execute untrusted student programs.

---

# Evaluation

The repository contains controlled, scaled, baseline, multi-signal, and authentic evaluation artifacts under [`results/`](results/). Full methodology, negative findings, and validity threats are documented in [`docs/evaluation.md`](docs/evaluation.md).

## Controlled transformation benchmark

The controlled benchmark includes identifier renaming, method reordering, class renaming, filename changes, dead-code insertion, class splitting, unrelated controls, and an intentionally difficult structural lookalike.

| Transformation | BehavClone normalized similarity |
|---|---:|
| Identifier rename | 1.000 |
| Method reorder | 1.000 |
| Class rename | 1.000 |
| Filename rename | 1.000 |
| Class split | 1.000 |
| Dead-code insertion | ~0.837 |

The deliberately unrelated lookalike also reached normalized and structural similarity `1.0`. That negative result matters: transformation robustness can reduce discriminability. The benchmark is therefore not presented as a plagiarism-accuracy result.

## Scaled false-positive pressure

A larger controlled experiment contains **16 submissions**, **4 provenance families**, and **120 unordered pairs**: 24 within-family related pairs and 96 cross-family controls.

All 24 related pairs reached normalized similarity `1.0`, but **48 of 96 cross-family controls also reached `1.0`**. On this synthetic cohort, normalization and structural abstraction increased transformation invariance while also creating substantial similarity collisions.

The raw representation separated the provenance families in this particular fixture, but that does not establish that raw comparison is universally superior.

## Multi-signal controlled evidence

Among the 24 related pairs:

```text
normalized similarity == 1.0       24 / 24
shared-failure evidence present      8 / 24
identical wrong-output evidence      4 / 24
```

Among the 96 cross-family controls:

```text
normalized similarity == 1.0       48 / 96
shared-failure evidence present      0 / 96
identical wrong-output evidence      0 / 96
```

In this controlled fixture, behavioral evidence supplied additional discriminating information **when present**. It did not solve the structural ambiguity problem: 16 of the 24 related pairs had no shared-failure evidence.

These behavioral observations are controlled imported outcomes, not executions of one common real assignment test suite.

## Authentic external evaluation

BehavClone was also evaluated on a frozen external Java cohort from the IR-Plag dataset: **15 dataset-labelled non-plagiarized submissions**, **105 unordered pairs**, one Java source file per submission, and one extracted fragment per submission.

This experiment examines false-positive / similarity ambiguity pressure. The dataset label does not establish author intent.

### BehavClone

For normalized similarity across the 105 pairs:

| Statistic | Value |
|---|---:|
| Minimum | 0.557692 |
| Median | 1.000000 |
| Mean | 0.916794 |
| Maximum | 1.000000 |
| Exact `1.0` pairs | 55 / 105 |

### JPlag 6.3.0

**JPlag is the principal established baseline used by this project.** For JPlag average similarity on the same cohort:

| Statistic | Value |
|---|---:|
| Minimum | 0.000000 |
| Median | 1.000000 |
| Mean | 0.737415 |
| Maximum | 1.000000 |
| Exact `1.0` pairs | 66 / 105 |
| Zero-similarity pairs | 27 / 105 |

JPlag maximum similarity reached `1.0` for 78 of 105 pairs. Tie-aware analysis found high overall rank association between BehavClone normalized similarity and JPlag average similarity (`Spearman rho ≈ 0.928`), while the systems still disagreed operationally on some pairs.

The scores are not mathematically equivalent, and neither is interpreted as a plagiarism probability.

### Important authentic-evaluation limitation

Every submission in the frozen authentic cohort produced exactly **one fragment** under the current extraction pipeline. The authentic experiment therefore does **not** validate BehavClone's multi-fragment architecture-flexible matching mechanism; that mechanism is currently supported by controlled experiments.

The authentic cohort also has no independently established common behavioral observations in this project, so behavioral evidence is unavailable for that experiment.

---

## BehavClone and JPlag

Modern JPlag supports submission-level comparison across multiple files, base-code handling, normalization, configurable matching, CSV export, and frequency-aware analysis. BehavClone should therefore **not** be described as fixing a simplistic limitation where JPlag can only compare matching filenames or classes.

The current research instead investigates an evidence architecture combining complete-submission fragment correspondence, global one-to-one assignment, separately inspectable structural representations, cohort-relative context, shared-failure evidence, and identical incorrect-output evidence.

The controlled benchmark contains cases where the systems behave differently. For example, BehavClone normalized matching retained full similarity for the small controlled class-split fixture while the evaluated JPlag configurations did not. This is fixture-specific and is **not** a claim of general superiority.

See [`docs/related-work.md`](docs/related-work.md) for the JPlag-centered contribution boundary and prior-work discussion.

---

## What the current evidence supports

The current experiments support bounded conclusions: whole-submission fragment assignment tolerates several controlled naming, ordering, and organization transformations; normalization can improve transformation invariance while increasing false-positive pressure; cohort rarity exposes feature commonness but is not consistently discriminative; controlled shared incorrect behavior can add information when present; and dataset-labelled non-plagiarized authentic programs can still produce high similarity under both BehavClone and JPlag.

## What the evidence does not support

The current experiments do **not** establish plagiarism-detection accuracy, author intent, a universal similarity threshold, a universal false-positive rate, superiority over JPlag, scientific novelty of every component, authentic behavioral effectiveness, or authentic validation of multi-fragment architecture flexibility.

These boundaries are part of the research result.

---

# Reproducibility

Protocols, experiment runners, result artifacts, and regression tests are kept together.

```text
results/
|-- controlled/
|-- scaled/
|-- multisignal/
|-- scaled-multisignal/
|-- baselines/
|   |-- jplag/
|   `-- jplag-configurations/
`-- authentic/
    |-- behavclone/
    |-- jplag/
    `-- analysis/
```

The authentic source dataset and JPlag executable are intentionally kept outside the repository. Public metadata, pinned provenance, experiment code, and derived artifacts are retained in the project. Frozen result artifacts are protected by regression tests.

## Installation

Requirements: Python `>=3.11` and Java source submissions for the current analysis pipeline.

```bash
git clone https://github.com/maria-habib17/behavclone.git
cd behavclone
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Synthetic demo

```powershell
behavclone analyze datasets/synthetic/demo-assignment
```

The demo uses synthetic pseudonymous submissions rather than private student work.

## Quality checks

```powershell
python -m ruff check .
python -m pytest -q
```

Current frozen research milestone:

```text
Ruff: all checks passed
pytest: 296 passed
```

GitHub Actions runs automated quality checks on pushes and pull requests.

---

# Project structure

```text
behavclone/
|-- behavclone/
|   |-- baselines/
|   |-- behavior/
|   |-- cohort/
|   |-- evidence/
|   |-- fragments/
|   |-- ingestion/
|   |-- matching/
|   |-- normalization/
|   `-- parsing/
|-- datasets/
|   `-- synthetic/
|-- docs/
|   |-- architecture.md
|   |-- evaluation.md
|   |-- methodology.md
|   |-- related-work.md
|   `-- threat-model.md
|-- experiments/
|-- results/
|-- tests/
|   |-- integration/
|   |-- regression/
|   |-- synthetic/
|   `-- unit/
|-- .github/workflows/
|-- README.md
|-- LICENSE
`-- pyproject.toml
```

## Implemented research components

- [x] whole-submission Java ingestion
- [x] recursive Java discovery
- [x] Tree-sitter method and constructor extraction
- [x] raw, normalized, and structural representations
- [x] LCS-based fragment similarity
- [x] exact maximum-weight one-to-one fragment assignment
- [x] fragment coverage reporting
- [x] conservative starter-code exclusion
- [x] cohort document-frequency and rarity evidence
- [x] imported behavioral-result validation
- [x] shared-failure and identical wrong-output evidence
- [x] behavioral rarity evidence
- [x] separate multi-signal evidence reports
- [x] controlled transformation benchmark
- [x] scaled false-positive experiment
- [x] JPlag 6.3.0 baseline integration
- [x] authentic external-cohort measurement
- [x] frozen reproducibility regression tests
- [x] automated CI quality checks

## Research directions

Current extensions include larger and more architecture-diverse authentic cohorts, authentic behavioral observations, behavior-guided structural alignment, richer fragment granularities, assignment sensitivity analysis, scalable assignment algorithms, and instructor-facing evidence review.

---

# Responsible use

Source-code similarity is not proof of authorship or misconduct. Similarity can arise from assignment requirements, starter code, common algorithms, course examples, standard APIs, conventional implementation patterns, or independent work.

BehavClone is designed around **human-in-the-loop review**. Automated analysis may help prioritize candidate pairs and organize evidence, but consequential academic-integrity decisions require instructor judgment, appropriate context, and applicable institutional processes.

## Privacy and security

The project favors pseudonymous identifiers, synthetic or appropriately licensed public datasets, minimal retention of identifying information, explicit authorization for private student submissions, and avoiding publication of private student code.

The current behavioral layer imports results rather than executing untrusted submissions. Any future execution should occur only in an appropriately isolated environment with resource and network restrictions.

---

# Documentation

- [`docs/architecture.md`](docs/architecture.md) — architecture and evidence philosophy
- [`docs/methodology.md`](docs/methodology.md) — research methodology
- [`docs/evaluation.md`](docs/evaluation.md) — experiments, quantitative findings, negative results, and threats to validity
- [`docs/related-work.md`](docs/related-work.md) — JPlag-centered related work and contribution boundary
- [`docs/threat-model.md`](docs/threat-model.md) — transformations and known limitations

---

# Research status

BehavClone is an experimental research prototype, not an academic-integrity decision system.

The current project investigates whether **architecture-flexible structural correspondence, cohort context, and shared incorrect-behavior evidence can provide complementary, interpretable evidence for reviewing suspicious programming-assignment similarity**.

JPlag is the principal established baseline. The strongest unresolved empirical question is whether this multi-signal evidence design remains useful on larger, genuinely architecture-diverse authentic assignment cohorts with independently available behavioral observations.

---

# License

This project is licensed under the MIT License.
