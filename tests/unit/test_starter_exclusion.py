from pathlib import Path

from behavclone.fragments.starter import (
    build_starter_signatures,
    discover_starter_signatures,
    filter_starter_fragments,
)
from behavclone.parsing.java import extract_method_fragments


def write_java(
    path: Path,
    source: str,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def test_exact_starter_fragment_is_excluded(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            int adjust(int value) {
                return value + 1;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            int adjust(int value) {
                return value + 1;
            }

            int studentWork(int value) {
                return value * 2;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert [fragment.name for fragment in retained] == [
        "studentWork",
    ]


def test_identifier_renamed_starter_fragment_is_excluded(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            int adjust(int value) {
                int result = value + 1;
                return result;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Different.java",
        """
        class Different {
            int transform(int number) {
                int changed = number + 1;
                return changed;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert retained == []


def test_modified_starter_logic_is_retained(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            int adjust(int value) {
                return value + 1;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            int transform(int number) {
                return number + 2;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert len(retained) == 1
    assert retained[0].name == "transform"


def test_student_authored_fragment_is_retained(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            boolean valid(int value) {
                return value >= 0;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            int calculate(int price, int discount) {
                return price - discount;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert len(retained) == 1
    assert retained[0].name == "calculate"


def test_constructor_starter_fragment_is_excluded(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            Base(int value) {
                this.value = value;
            }

            int value;
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Renamed.java",
        """
        class Renamed {
            Renamed(int number) {
                this.number = number;
            }

            int number;
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert retained == []


def test_missing_starter_directory_produces_empty_signature_set(
    tmp_path: Path,
):
    signatures = discover_starter_signatures(
        tmp_path / "does-not-exist"
    )

    assert signatures == frozenset()


def test_none_starter_directory_produces_empty_signature_set():
    assert discover_starter_signatures(None) == frozenset()


def test_starter_discovery_is_recursive(
    tmp_path: Path,
):
    write_java(
        tmp_path / "starter" / "nested" / "Base.java",
        """
        class Base {
            int work(int value) {
                return value + 1;
            }
        }
        """,
    )

    signatures = discover_starter_signatures(
        tmp_path / "starter"
    )

    assert len(signatures) == 1


def test_changed_operator_is_not_excluded(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            int adjust(int value) {
                return value + 1;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            int transform(int number) {
                return number - 1;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert len(retained) == 1
    assert retained[0].name == "transform"


def test_changed_literal_is_not_excluded(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            boolean allowed(int value) {
                return value > 10;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            boolean permitted(int number) {
                return number > 20;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert len(retained) == 1
    assert retained[0].name == "permitted"


def test_comments_do_not_prevent_starter_exclusion(
    tmp_path: Path,
):
    starter = write_java(
        tmp_path / "starter" / "Base.java",
        """
        class Base {
            int adjust(int value) {
                return value + 1;
            }
        }
        """,
    )

    submission = write_java(
        tmp_path / "submission" / "Work.java",
        """
        class Work {
            int transform(int number) {
                // Only the comment changed.
                return number + 1;
            }
        }
        """,
    )

    signatures = build_starter_signatures([starter])
    fragments = extract_method_fragments(submission)

    retained = filter_starter_fragments(
        fragments,
        signatures,
    )

    assert retained == []
