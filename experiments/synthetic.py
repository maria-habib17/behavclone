from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyntheticSubmission:
    """One generated Java submission used in controlled experiments."""

    submission_id: str
    files: dict[str, str]


def _write_submission(
    submissions_root: Path,
    submission: SyntheticSubmission,
) -> None:
    root = submissions_root / submission.submission_id
    root.mkdir(parents=True, exist_ok=True)

    for relative_path, source in submission.files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            source.strip() + "\n",
            encoding="utf-8",
        )


def write_synthetic_assignment(
    root: Path,
    submissions: tuple[SyntheticSubmission, ...],
    behavioral_results: str | None = None,
) -> None:
    """Write a deterministic Java assignment for benchmark experiments."""
    submissions_root = root / "submissions"
    submissions_root.mkdir(parents=True, exist_ok=True)

    (root / "assignment.yaml").write_text(
        (
            "assignment:\n"
            "  name: controlled-transformations\n"
            "  language: java\n"
            "  submissions_directory: submissions\n"
            "  starter_directory: null\n"
            + (
                "  test_results: test-results.csv\n"
                if behavioral_results is not None
                else "  test_results: null\n"
            )
        ),
        encoding="utf-8",
    )

    for submission in submissions:
        _write_submission(
            submissions_root,
            submission,
        )

    if behavioral_results is not None:
        (root / "test-results.csv").write_text(
            behavioral_results.strip() + "\n",
            encoding="utf-8",
        )


def controlled_submissions() -> tuple[SyntheticSubmission, ...]:
    """Return baseline, isolated transformations, and unrelated controls."""
    baseline = SyntheticSubmission(
        submission_id="BASE",
        files={
            "Calculator.java": """
class Calculator {
    int increase(int value) {
        int result = value + 1;
        return result;
    }

    int multiply(int value) {
        int result = value * 17;
        return result;
    }
}
""",
        },
    )

    identifier_rename = SyntheticSubmission(
        submission_id="ID_RENAME",
        files={
            "Calculator.java": """
class Calculator {
    int increase(int input) {
        int changed = input + 1;
        return changed;
    }

    int multiply(int input) {
        int changed = input * 17;
        return changed;
    }
}
""",
        },
    )

    method_reorder = SyntheticSubmission(
        submission_id="METHOD_REORDER",
        files={
            "Calculator.java": """
class Calculator {
    int multiply(int value) {
        int result = value * 17;
        return result;
    }

    int increase(int value) {
        int result = value + 1;
        return result;
    }
}
""",
        },
    )

    class_rename = SyntheticSubmission(
        submission_id="CLASS_RENAME",
        files={
            "Calculator.java": """
class PricingEngine {
    int increase(int value) {
        int result = value + 1;
        return result;
    }

    int multiply(int value) {
        int result = value * 17;
        return result;
    }
}
""",
        },
    )

    file_rename = SyntheticSubmission(
        submission_id="FILE_RENAME",
        files={
            "PricingEngine.java": """
class Calculator {
    int increase(int value) {
        int result = value + 1;
        return result;
    }

    int multiply(int value) {
        int result = value * 17;
        return result;
    }
}
""",
        },
    )

    dead_code = SyntheticSubmission(
        submission_id="DEAD_CODE",
        files={
            "Calculator.java": """
class Calculator {
    int increase(int value) {
        int unused = value * 99;
        int result = value + 1;
        return result;
    }

    int multiply(int value) {
        int ignored = value + 42;
        int result = value * 17;
        return result;
    }
}
""",
        },
    )

    class_split = SyntheticSubmission(
        submission_id="CLASS_SPLIT",
        files={
            "Incrementer.java": """
class Incrementer {
    int increase(int value) {
        int result = value + 1;
        return result;
    }
}
""",
            "Multiplier.java": """
class Multiplier {
    int multiply(int value) {
        int result = value * 17;
        return result;
    }
}
""",
        },
    )

    unrelated_a = SyntheticSubmission(
        submission_id="UNRELATED_A",
        files={
            "TextStats.java": """
class TextStats {
    int length(String text) {
        return text.length();
    }

    boolean empty(String text) {
        return text.isEmpty();
    }
}
""",
        },
    )

    unrelated_b = SyntheticSubmission(
        submission_id="UNRELATED_B",
        files={
            "Threshold.java": """
class Threshold {
    boolean positive(int number) {
        return number > 0;
    }

    int clamp(int number) {
        if (number < 0) {
            return 0;
        }
        return number;
    }
}
""",
        },
    )

    lookalike = SyntheticSubmission(
        submission_id="LOOKALIKE",
        files={
            "Inventory.java": """
class Inventory {
    int addFee(int quantity) {
        int total = quantity + 8;
        return total;
    }

    int scaleStock(int quantity) {
        int total = quantity * 3;
        return total;
    }
}
""",
        },
    )

    return (
        baseline,
        identifier_rename,
        method_reorder,
        class_rename,
        file_rename,
        dead_code,
        class_split,
        unrelated_a,
        unrelated_b,
        lookalike,
    )


def controlled_behavioral_results() -> str:
    """Return deterministic imported behavior for the controlled cohort.

    Correct behavior is intentionally common and therefore not pair evidence.
    BASE and transformed variants share an incorrect output on EDGE_17.
    LOOKALIKE passes that test despite its high normalized structural
    similarity to BASE. The dataset is synthetic and exists to demonstrate
    evidence-channel disagreement, not to estimate plagiarism accuracy.
    """
    submission_ids = (
        "BASE",
        "ID_RENAME",
        "METHOD_REORDER",
        "CLASS_RENAME",
        "FILE_RENAME",
        "DEAD_CODE",
        "CLASS_SPLIT",
        "UNRELATED_A",
        "UNRELATED_B",
        "LOOKALIKE",
    )

    related_ids = {
        "BASE",
        "ID_RENAME",
        "METHOD_REORDER",
        "CLASS_RENAME",
        "FILE_RENAME",
        "DEAD_CODE",
        "CLASS_SPLIT",
    }

    lines = [
        "submission,test,status,expected,actual",
    ]

    for submission_id in submission_ids:
        lines.append(
            f"{submission_id},BASIC_01,PASS,2,2"
        )
        lines.append(
            f"{submission_id},BASIC_02,PASS,34,34"
        )

        if submission_id in related_ids:
            lines.append(
                f"{submission_id},EDGE_17,FAIL,289,288"
            )
        else:
            lines.append(
                f"{submission_id},EDGE_17,PASS,289,289"
            )

    return "\n".join(lines)
