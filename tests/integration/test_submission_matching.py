from pathlib import Path

import pytest

from behavclone.matching.submission import (
    build_similarity_matrix,
    compare_submissions,
    extract_submission_fragments,
)


def write_java(
    path: Path,
    source: str,
) -> Path:
    """Write a Java source file used by an integration test."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

    return path


def test_submission_matching_survives_architecture_renaming_and_permutation(
    tmp_path: Path,
):
    left_first = write_java(
        tmp_path / "left" / "Calculator.java",
        """
        class Calculator {
            int calculate(int price, int discount) {
                return price - discount;
            }

            boolean valid(int value) {
                return value >= 0;
            }
        }
        """,
    )

    left_second = write_java(
        tmp_path / "left" / "Receipt.java",
        """
        class Receipt {
            void printReceipt(int total) {
                System.out.println(total);
            }
        }
        """,
    )

    right_first = write_java(
        tmp_path / "right" / "OutputEngine.java",
        """
        class OutputEngine {
            void output(int amount) {
                System.out.println(amount);
            }

            int compute(int amount, int reduction) {
                return amount - reduction;
            }
        }
        """,
    )

    right_second = write_java(
        tmp_path / "right" / "Rules.java",
        """
        class Rules {
            boolean check(int number) {
                return number >= 0;
            }
        }
        """,
    )

    result = compare_submissions(
        [left_first, left_second],
        [right_first, right_second],
    )

    pairs = {
        (match.left_name, match.right_name)
        for match in result.matches
    }

    assert result.left_fragment_count == 3
    assert result.right_fragment_count == 3
    assert result.matched_count == 3

    assert pairs == {
        ("calculate", "compute"),
        ("valid", "check"),
        ("printReceipt", "output"),
    }

    assert result.left_coverage == pytest.approx(1.0)
    assert result.right_coverage == pytest.approx(1.0)
    assert result.mean_normalized_similarity == pytest.approx(1.0)
    assert result.mean_structural_similarity == pytest.approx(1.0)


def test_coverage_exposes_unmatched_fragments(
    tmp_path: Path,
):
    left = write_java(
        tmp_path / "left" / "Left.java",
        """
        class Left {
            int calculate(int price, int discount) {
                return price - discount;
            }
        }
        """,
    )

    right = write_java(
        tmp_path / "right" / "Right.java",
        """
        class Right {
            int compute(int amount, int reduction) {
                return amount - reduction;
            }

            boolean extra(int value) {
                return value > 10;
            }
        }
        """,
    )

    result = compare_submissions(
        [left],
        [right],
    )

    assert result.left_fragment_count == 1
    assert result.right_fragment_count == 2
    assert result.matched_count == 1

    assert result.left_coverage == pytest.approx(1.0)
    assert result.right_coverage == pytest.approx(0.5)


def test_empty_submission_produces_no_matches(
    tmp_path: Path,
):
    empty = write_java(
        tmp_path / "empty" / "Empty.java",
        """
        class Empty {
        }
        """,
    )

    populated = write_java(
        tmp_path / "populated" / "Work.java",
        """
        class Work {
            int work(int value) {
                return value + 1;
            }
        }
        """,
    )

    result = compare_submissions(
        [empty],
        [populated],
    )

    assert result.left_fragment_count == 0
    assert result.right_fragment_count == 1
    assert result.matched_count == 0
    assert result.left_coverage == 0.0
    assert result.right_coverage == 0.0


def test_global_assignment_prefers_true_correspondence_over_distractor(
    tmp_path: Path,
):
    left = write_java(
        tmp_path / "left" / "Original.java",
        """
        class Original {
            int calculate(int price, int discount) {
                return price - discount;
            }

            boolean valid(int value) {
                return value >= 0;
            }
        }
        """,
    )

    right = write_java(
        tmp_path / "right" / "Reworked.java",
        """
        class Reworked {
            boolean looksSimilar(int number) {
                int adjusted = number - 1;
                return adjusted >= 0;
            }

            int compute(int amount, int reduction) {
                return amount - reduction;
            }

            boolean check(int number) {
                return number >= 0;
            }
        }
        """,
    )

    left_fragments = extract_submission_fragments([left])
    right_fragments = extract_submission_fragments([right])

    _, evidence_matrix = build_similarity_matrix(
        left_fragments,
        right_fragments,
    )

    print()
    print("SELECTED ASSIGNMENT")
    print("=" * 80)

    for left_index, left_fragment in enumerate(left_fragments):
        for right_index, right_fragment in enumerate(right_fragments):
            similarity = evidence_matrix[left_index][right_index]

            print(
                f"{left_fragment.name:15} -> "
                f"{right_fragment.name:15} "
                f"raw={similarity.raw:.4f} "
                f"normalized={similarity.normalized:.4f} "
                f"structural={similarity.structural:.4f}"
            )

    result = compare_submissions(
        [left],
        [right],
    )

    print()
    print("SELECTED ASSIGNMENT")
    print("=" * 80)

    for match in result.matches:
        print(
            f"{match.left_name:15} -> "
            f"{match.right_name:15} "
            f"raw={match.similarity.raw:.4f} "
            f"normalized={match.similarity.normalized:.4f} "
            f"structural={match.similarity.structural:.4f}"
        )

    pairs = {
        (match.left_name, match.right_name)
        for match in result.matches
    }

    assert result.left_fragment_count == 2
    assert result.right_fragment_count == 3
    assert result.matched_count == 2

    assert pairs == {
        ("calculate", "compute"),
        ("valid", "check"),
    }

    assert result.left_coverage == pytest.approx(1.0)
    assert result.right_coverage == pytest.approx(2 / 3)


def test_submission_matching_excludes_normalized_starter_fragments(
    tmp_path: Path,
):
    from behavclone.fragments.starter import build_starter_signatures

    starter = write_java(
        tmp_path / "starter" / "Template.java",
        """
        class Template {
            int helper(int value) {
                return value + 1;
            }
        }
        """,
    )

    left = write_java(
        tmp_path / "left" / "Left.java",
        """
        class Left {
            int renamedHelper(int number) {
                return number + 1;
            }

            int calculate(int price, int discount) {
                return price - discount;
            }
        }
        """,
    )

    right = write_java(
        tmp_path / "right" / "Right.java",
        """
        class Right {
            int anotherHelper(int input) {
                return input + 1;
            }

            int compute(int amount, int reduction) {
                return amount - reduction;
            }
        }
        """,
    )

    starter_signatures = build_starter_signatures(
        [starter]
    )

    result = compare_submissions(
        [left],
        [right],
        starter_signatures=starter_signatures,
    )

    pairs = {
        (match.left_name, match.right_name)
        for match in result.matches
    }

    assert result.left_fragment_count == 1
    assert result.right_fragment_count == 1
    assert result.matched_count == 1

    assert pairs == {
        ("calculate", "compute"),
    }

    assert result.left_coverage == pytest.approx(1.0)
    assert result.right_coverage == pytest.approx(1.0)
