# BehavClone

> **Evidence-oriented similarity analysis for architecture-flexible programming assignments.**

BehavClone is an experimental research-engineering project for analyzing similarities between programming-assignment submissions when students are free to choose different files, classes, method names, and method orderings.

Many source-similarity workflows become less informative when equivalent functionality is organized differently across submissions. BehavClone explores a different approach: treat the **complete submission as the unit of analysis**, extract structural fragments, compare candidate fragments across submissions, and find a global correspondence between them.

BehavClone does **not** determine whether plagiarism occurred.

Its purpose is to surface interpretable similarity evidence for human review.

---

## Research Question

> **Can suspiciously similar solutions be surfaced when students are free to use different files, classes, methods, and program structures, but must implement the same specified behavior?**

The project investigates four initial research questions:

1. How robust is fragment matching to identifier, file, class, and method transformations?
2. Can cohort-relative evidence distinguish common assignment patterns from unusually shared structure?
3. Can rare shared incorrect behavior provide useful evidence beyond source similarity?
4. How often are independently written solutions surfaced as highly similar?

---

## Motivation

Programming assignments often specify required behavior while still allowing students freedom in software design.

Two students may implement equivalent functionality using:

- different filenames,
- different class names,
- different method names,
- different variable names,
- different method orderings, and
- different class or file organization.

A comparison system should therefore not assume that:

```text
Submission A                    Submission B

Calculator.java      <------>   Calculator.java
calculate()          <------>   calculate()
method #1            <------>   method #1
```

is the only meaningful correspondence.

BehavClone instead investigates correspondence across the **whole submission**.

For example:

```text
Submission A                    Submission B

Calculator.java                 PricingEngine.java
    calculate()  ------------>      compute()

Validator.java                  Rules.java
    valid()      ------------>      check()

Receipt.java                    OutputEngine.java
    printReceipt() ----------->      output()
```

The correspondence is based on fragment evidence rather than filenames, class names, or source position.

---

## Example

Consider these two Java methods.

### Submission A

```java
public class Calculator {

    public int calculate(int price, int discount) {
        int result = price - discount;

        if (result < 0) {
            return 0;
        }

        return result;
    }
}
```

### Submission B

```java
public class PricingEngine {

    public int compute(int amount, int reduction) {
        int finalValue = amount - reduction;

        if (finalValue < 0) {
            return 0;
        }

        return finalValue;
    }
}
```

Several surface features have changed:

```text
Calculator      -> PricingEngine
calculate       -> compute
price           -> amount
discount        -> reduction
result          -> finalValue
```

The implementation structure, however, remains closely related.

The current BehavClone prototype represents this relationship using multiple evidence channels rather than relying on one raw-text score.

---

## Current Capabilities

The current prototype implements:

- recursive Java source discovery,
- whole-submission ingestion,
- Tree-sitter Java parsing,
- method extraction,
- constructor extraction,
- raw token representations,
- normalized token representations,
- structural syntax representations,
- LCS-based sequence similarity,
- all-pairs fragment comparison,
- maximum-weight one-to-one fragment assignment,
- architecture-flexible submission comparison,
- method-permutation resistance in synthetic tests,
- unmatched-fragment coverage reporting, and
- separate raw, normalized, and structural similarity evidence.

The current repository passes:

```text
39 tests
Ruff: all checks passed
```

---

## Current Analysis Pipeline

```text
                    +----------------------+
                    |      Assignment      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Submission Discovery |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Java File Discovery  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Tree-sitter Parser  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Fragment Extraction  |
                    | methods/constructors |
                    +----------+-----------+
                               |
                               v
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
       +-----------+     +-----------+     +-----------+
       |    Raw    |     |Normalized |     |Structural |
       |  Tokens   |     |  Tokens   |     |  Syntax   |
       +-----+-----+     +-----+-----+     +-----+-----+
             |                 |                 |
             +-----------------+-----------------+
                               |
                               v
                    +----------------------+
                    | Pairwise Fragment    |
                    | Similarity Evidence  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Maximum-Weight       |
                    | 1-to-1 Assignment    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Submission-Level     |
                    | Structural Evidence  |
                    +----------------------+
```

Future evidence layers will extend this pipeline with starter-code exclusion, cohort-relative rarity, and behavioral evidence.

---

## What Is a Fragment?

The definition of a fragment is explicit.

In the current prototype, a structural fragment is one complete Java:

- `method_declaration`, or
- `constructor_declaration`

identified by Tree-sitter.

BehavClone therefore does **not** currently define fragments as arbitrary token subsequences or arbitrary AST subtrees.

Alternative granularities, such as blocks and AST subtrees, can later be evaluated experimentally rather than being hidden implementation assumptions.

---

## Multiple Representations

BehavClone deliberately keeps different representations separate.

### 1. Raw Tokens

Raw tokens preserve concrete source tokens.

Identifier renaming therefore affects this representation.

Conceptually:

```text
calculate price discount result
```

and:

```text
compute amount reduction finalValue
```

remain different.

---

### 2. Normalized Tokens

Identifiers and literal values are abstracted while relevant Java syntax, keywords, and operators remain available.

For example, renamed identifiers can map toward a representation such as:

```text
<ID> <ID> <ID> <ID>
```

while operations such as:

```text
+
-
*
/
<
>
```

remain distinguishable.

This reduces sensitivity to superficial renaming without intentionally erasing all implementation information.

---

### 3. Structural Representation

The structural representation captures syntax-tree structure while retaining relevant distinctions such as operators.

This provides a representation less dependent on concrete identifier spelling.

---

## Why Keep the Signals Separate?

BehavClone does not currently collapse the representations into an arbitrary weighted "plagiarism score."

Instead, evidence such as:

```text
raw similarity
normalized similarity
structural similarity
fragment coverage
```

can remain separately inspectable.

This supports later ablation experiments and makes it possible to ask which representation actually contributes useful information.

---

## Similarity

The current baseline uses **Longest Common Subsequence (LCS)** based sequence similarity.

For token sequences `A` and `B`, the current normalized sequence similarity is:

```text
                  2 * LCS(A, B)
similarity = -------------------------
                |A| + |B|
```

The measure is symmetric and bounded between `0` and `1`.

A high value is similarity evidence.

It is **not** interpreted as a probability that plagiarism occurred.

---

## Architecture-Flexible Matching

Suppose one submission contains:

```text
A = {a1, a2, ..., an}
```

and another contains:

```text
B = {b1, b2, ..., bm}
```

BehavClone compares candidate fragments across the two submissions rather than pairing fragments by filename or position.

This produces a fragment-similarity matrix:

```text
                    Submission B

                  b1      b2      b3

Submission   a1   s11     s12     s13
A            a2   s21     s22     s23
             a3   s31     s32     s33
```

The current research baseline then computes a **maximum-weight one-to-one assignment**.

For example, a matrix such as:

```text
0.31    1.00    0.42
0.27    0.39    1.00
1.00    0.33    0.29
```

produces the correspondence:

```text
a1 -> b2
a2 -> b3
a3 -> b1
```

rather than assuming:

```text
a1 -> b1
a2 -> b2
a3 -> b3
```

This makes the baseline resistant to simple method permutation.

---

## Why Global Assignment?

Greedy matching can select a locally attractive fragment pair that prevents a better overall correspondence.

BehavClone therefore currently uses exact maximum-weight assignment via dynamic programming.

This gives the optimal one-to-one assignment for the current similarity matrix.

The implementation is intentionally a research baseline: its complexity grows exponentially with the candidate-column count.

A polynomial-time assignment algorithm, such as a Hungarian-style implementation, is a future scalability improvement.

---

## Coverage Matters

A pair of submissions should not look completely matched simply because one similar method exists.

BehavClone therefore exposes fragment coverage.

For example, if:

```text
Submission A: 1 fragment
Submission B: 2 fragments
Matched:      1 fragment
```

then:

```text
left coverage  = 1.0
right coverage = 0.5
```

The unmatched fragment remains visible rather than disappearing into a single aggregate score.

---

## Tested Transformations

The current synthetic tests exercise cases including:

```text
identifier renaming
method renaming
class renaming
filename changes
method permutation
different file organization
extra unmatched fragments
distractor fragments
```

An adversarial integration test also verifies that global assignment can prefer the intended overall correspondence when an additional distractor fragment is present.

These are controlled synthetic tests.

They should **not** be interpreted as evidence of real-world plagiarism-detection accuracy.

---

## Evidence, Not Verdicts

BehavClone follows a deliberately conservative interpretation model.

The system is intended to produce evidence such as:

```text
Pair: S001 <-> S002

Structural evidence
-------------------
Matched fragments:        ...
Normalized similarity:    ...
Structural similarity:    ...
Coverage:                 ...

Behavioral evidence
-------------------
Shared rare failures:     ...
Identical wrong outputs:  ...

Cohort context
-------------------
Pattern frequency:        ...
Rarity evidence:          ...
```

The final interpretation remains a human responsibility.

BehavClone does not automatically output:

```text
PLAGIARISM = TRUE
```

and a similarity value is not presented as a plagiarism probability.

---

## Correct Behavior Is Not Suspicious by Itself

Programming assignments explicitly require students to produce the same correct behavior.

If two correct submissions both produce:

```text
expected: 80
actual:   80
```

that agreement is expected.

Therefore, future behavioral analysis will not treat ordinary shared correct output as plagiarism evidence.

A more interesting signal is a **rare shared incorrect behavior**.

For example:

```text
Expected output: 100

S001 actual: 99
S002 actual: 99
```

If most of the cohort does not make that mistake, the shared failure may be useful supporting evidence.

Even then, it remains evidence rather than proof of copying.

---

## Cohort-Relative Analysis

A fixed threshold such as:

```text
similarity > X
```

may behave differently across assignments, languages, starter code, and cohort composition.

BehavClone therefore plans to investigate **cohort-relative evidence**.

The central idea is:

> Common patterns should generally contribute less evidence than unusual shared patterns.

Future experiments will investigate frequency-aware or IDF-like weighting and percentile/rank-based evidence rather than assuming one universal plagiarism threshold.

---

## Starter Code

Instructor-provided starter code is a major confounder.

If every student receives the same implementation scaffold, shared starter material should not artificially increase the evidence against a pair of students.

Starter-code exclusion is therefore the next major research milestone.

It is **not yet implemented** in the current prototype.

---

## Behavioral Evidence

The repository already contains synthetic automated-test-result data for future experiments.

The planned behavioral layer will distinguish:

```text
shared PASS
shared common FAIL
shared rare FAIL
identical incorrect output
different incorrect output
```

The research question is not simply whether two submissions behave the same.

It is whether **unusual shared incorrect behavior** adds useful evidence beyond structural similarity.

This layer is **planned, not yet implemented**.

---

## Threat Model

The project considers transformations such as:

### Current baseline targets

- formatting changes,
- comments,
- identifier renaming,
- method renaming,
- class renaming,
- filename changes,
- method permutation, and
- file reorganization.

### Harder transformations for later study

- dead-code insertion,
- statement reordering,
- method extraction,
- method inlining,
- class splitting,
- class merging,
- control-flow rewriting,
- alternative algorithms, and
- deeper semantic rewrites.

The goal is not to claim universal robustness.

The goal is to measure which transformations each evidence layer can and cannot tolerate.

See [`docs/threat-model.md`](docs/threat-model.md) for the evolving threat model.

---

## Evaluation Strategy

Evaluation will focus on controlled, interpretable research questions rather than a single unsupported accuracy number.

Planned measurements include:

- transformation robustness,
- seeded suspicious-pair retrieval,
- ranking behavior,
- false-positive surfacing,
- fragment correspondence quality,
- method-permutation robustness,
- representation ablations,
- starter-code exclusion ablations,
- cohort-frequency ablations, and
- behavioral-evidence ablations.

A particularly important question is:

> How often are independently written solutions surfaced as highly similar?

This makes false-positive analysis a first-class part of the research design.

---

## Synthetic Benchmark Philosophy

The project begins with synthetic submissions because transformations can be controlled precisely.

A benchmark can start from a base implementation and create variants involving:

```text
rename identifiers
rename methods
rename classes
rename files
permute methods
move methods between files
insert unrelated fragments
change literals
change operators
insert dead code
rewrite control flow
```

Because the transformation is known, robustness can be measured without pretending that synthetic labels establish real-world authorship.

Evaluation on real student submissions should only be performed with appropriate authorization, anonymization, and privacy safeguards.

---

## Installation

BehavClone currently targets Python 3.11+ and Java source analysis.

Clone the repository:

```bash
git clone https://github.com/maria-habib17/behavclone.git
cd behavclone
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

---

## Run the Synthetic Demo

The repository includes a small synthetic Java assignment.

Run:

```powershell
behavclone analyze datasets/synthetic/demo-assignment
```

The demo uses pseudonymous synthetic submissions rather than real student work.

---

## Run the Test Suite

```powershell
python -m pytest -q
```

Current verified result:

```text
.......................................  [100%]
39 passed
```

Run the static quality check:

```powershell
python -m ruff check .
```

Current verified result:

```text
All checks passed!
```

---

## Project Structure

```text
behavclone/
|
|-- behavclone/
|   |-- api/
|   |-- behavior/
|   |-- cohort/
|   |-- evidence/
|   |-- fragments/
|   |-- ingestion/
|   |-- matching/
|   |-- normalization/
|   `-- parsing/
|
|-- datasets/
|   `-- synthetic/
|
|-- docs/
|   |-- architecture.md
|   |-- methodology.md
|   `-- threat-model.md
|
|-- experiments/
|
|-- tests/
|   |-- integration/
|   |-- regression/
|   |-- synthetic/
|   `-- unit/
|
|-- README.md
|-- LICENSE
`-- pyproject.toml
```

Some modules and test directories are reserved for later research layers and may not yet contain implemented functionality.

---

## Research Status

### Implemented

- [x] Assignment configuration
- [x] Submission discovery
- [x] Recursive Java-file discovery
- [x] Tree-sitter Java parsing
- [x] Method extraction
- [x] Constructor extraction
- [x] Raw token representation
- [x] Normalized token representation
- [x] Structural representation
- [x] LCS-based fragment similarity
- [x] Pairwise fragment-similarity matrices
- [x] Maximum-weight fragment assignment
- [x] Whole-submission comparison
- [x] Architecture-renaming integration tests
- [x] Method-permutation tests
- [x] Distractor-fragment integration test
- [x] Fragment coverage reporting

### Next Research Milestones

- [ ] Starter-code exclusion
- [ ] Larger synthetic transformation benchmark
- [ ] Cohort-relative fragment rarity
- [ ] Automated-test-result ingestion
- [ ] Shared-failure analysis
- [ ] Identical incorrect-output evidence
- [ ] Combined evidence reports
- [ ] Instructor review workflow
- [ ] Scalability experiments
- [ ] Polynomial-time fragment assignment
- [ ] Behavior-guided structural alignment

---

## Planned Behavior-Guided Structural Alignment

A longer-term research direction is to use behavioral information to help identify which structurally different fragments perform corresponding roles.

Instead of asking only:

> Which methods look most alike?

a future system could also ask:

> Which methods participate in producing the same observable behavior under the same tests?

This may help align functionality across substantially different program architectures.

This is a research direction only and is **not implemented in the current prototype**.

---

## Responsible Use

Source-code similarity is not proof of authorship or misconduct.

Similarities can arise from:

- assignment requirements,
- starter code,
- common algorithms,
- course examples,
- standard APIs,
- conventional programming patterns, or
- independently written solutions.

BehavClone is therefore designed around **human-in-the-loop review**.

Automated analysis may help prioritize candidate pairs and organize evidence, but consequential academic-integrity decisions require instructor judgment and appropriate institutional processes.

---

## Privacy

Real student source code can contain sensitive educational information.

The project therefore favors:

- pseudonymous submission identifiers,
- synthetic public datasets,
- minimal retention of identifying information,
- explicit authorization before using real submissions, and
- avoiding publication of student code without permission.

---

## Security

The current prototype analyzes source text and does not require executing untrusted student programs.

If automated execution is introduced later, student submissions should be treated as untrusted code and executed only inside an appropriately isolated environment with resource and network restrictions.

---

## Design Principles

BehavClone is guided by several principles:

**Whole submission over filename correspondence**  
A submission is the analysis unit; filenames are metadata rather than required matching keys.

**Evidence over verdicts**  
Similarity signals should remain inspectable rather than being silently converted into misconduct decisions.

**Behavior requires context**  
Correct shared behavior is expected. Rare shared incorrect behavior is a more meaningful research target.

**Cohort context matters**  
Common assignment patterns should not carry the same evidential weight as unusual shared structures.

**Assumptions should be testable**  
Fragment definitions, normalization strategies, matching algorithms, and thresholds should be exposed to ablation and robustness experiments.

**Human review remains mandatory**  
The system supports investigation; it does not replace it.

---

## Documentation

More detailed design notes are available in:

- [`docs/architecture.md`](docs/architecture.md) — system architecture and component boundaries
- [`docs/methodology.md`](docs/methodology.md) — research methodology and evidence philosophy
- [`docs/threat-model.md`](docs/threat-model.md) — transformations, risks, and known limitations

---

## Roadmap

The immediate development sequence is:

```text
Current structural baseline
          |
          v
Starter-code exclusion
          |
          v
Synthetic transformation benchmark
          |
          v
Cohort-relative rarity
          |
          v
Behavioral test-result ingestion
          |
          v
Rare shared-failure evidence
          |
          v
Interpretable pair evidence report
          |
          v
Instructor review workflow
```

Later work can investigate semantic representations, execution-guided alignment, larger datasets, and scalability.

---

## License

This project is licensed under the MIT License.
