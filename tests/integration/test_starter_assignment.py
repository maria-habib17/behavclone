from pathlib import Path

from behavclone.ingestion.assignment import load_assignment
from behavclone.matching.submission import (
    compare_assignment_submissions,
)


def write_text(
    path: Path,
    content: str,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def make_assignment_config(root: Path) -> None:
    write_text(
        root / "assignment.yaml",
        """
assignment:
  name: "Starter Exclusion Test"
  language: "java"
  submissions_directory: "submissions"
  starter_directory: "starter"
""",
    )


def test_assignment_discovers_starter_java_files(
    tmp_path: Path,
):
    make_assignment_config(tmp_path)

    write_text(
        tmp_path / "submissions" / "S001" / "Work.java",
        """
        class Work {
            int work(int value) {
                return value * 2;
            }
        }
        """,
    )

    starter = write_text(
        tmp_path / "starter" / "nested" / "Template.java",
        """
        class Template {
            int helper(int value) {
                return value + 1;
            }
        }
        """,
    )

    assignment = load_assignment(tmp_path)

    assert assignment.starter_files == [starter.resolve()]


def test_missing_starter_directory_is_allowed(
    tmp_path: Path,
):
    make_assignment_config(tmp_path)

    write_text(
        tmp_path / "submissions" / "S001" / "Work.java",
        """
        class Work {
            int work(int value) {
                return value * 2;
            }
        }
        """,
    )

    assignment = load_assignment(tmp_path)

    assert assignment.starter_files == []


def test_configured_starter_code_is_excluded_from_comparison(
    tmp_path: Path,
):
    make_assignment_config(tmp_path)

    write_text(
        tmp_path / "starter" / "Template.java",
        """
        class Template {
            int helper(int value) {
                return value + 1;
            }
        }
        """,
    )

    write_text(
        tmp_path / "submissions" / "S001" / "First.java",
        """
        class First {
            int renamedHelper(int number) {
                return number + 1;
            }

            int calculate(int price, int discount) {
                return price - discount;
            }
        }
        """,
    )

    write_text(
        tmp_path / "submissions" / "S002" / "Second.java",
        """
        class Second {
            int anotherHelper(int input) {
                return input + 1;
            }

            int compute(int amount, int reduction) {
                return amount - reduction;
            }
        }
        """,
    )

    assignment = load_assignment(tmp_path)

    left = assignment.submissions[0]
    right = assignment.submissions[1]

    result = compare_assignment_submissions(
        left.source_files,
        right.source_files,
        assignment.starter_files,
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
