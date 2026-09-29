from pathlib import Path

import pytest

from behavclone.cohort.assignment import (
    build_assignment_cohort_profile,
    compare_assignment_pair_with_cohort,
)
from behavclone.ingestion.assignment import load_assignment


def write(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_text(
        content,
        encoding="utf-8",
    )


def create_assignment(
    root: Path,
) -> None:
    write(
        root / "assignment.yaml",
        """
assignment:
  name: cohort-test
  language: java
  submissions_directory: submissions
  starter_directory: starter
""".strip(),
    )

    write(
        root / "starter" / "Starter.java",
        """
class Starter {
    int clamp(int value) {
        return value < 0 ? 0 : value;
    }
}
""".strip(),
    )

    write(
        root / "submissions" / "S001" / "First.java",
        """
class First {
    int clamp(int number) {
        return number < 0 ? 0 : number;
    }

    int calculate(int price, int discount) {
        int adjusted = price * 7;
        return adjusted - discount;
    }
}
""".strip(),
    )

    write(
        root / "submissions" / "S002" / "Second.java",
        """
class Second {
    int clamp(int amount) {
        return amount < 0 ? 0 : amount;
    }

    int compute(int amount, int reduction) {
        int changed = amount * 7;
        return changed - reduction;
    }
}
""".strip(),
    )

    write(
        root / "submissions" / "S003" / "Third.java",
        """
class Third {
    boolean validate(boolean flag) {
        return !flag;
    }
}
""".strip(),
    )


def test_assignment_profile_excludes_starter_fragments(
    tmp_path: Path,
):
    create_assignment(tmp_path)

    assignment = load_assignment(tmp_path)

    profile, fragments = build_assignment_cohort_profile(
        assignment,
        n=4,
    )

    assert profile.cohort_size == 3

    assert [
        item.name
        for item in fragments["S001"]
    ] == ["calculate"]

    assert [
        item.name
        for item in fragments["S002"]
    ] == ["compute"]

    assert [
        item.name
        for item in fragments["S003"]
    ] == ["validate"]


def test_assignment_pair_preserves_architecture_flexible_matching(
    tmp_path: Path,
):
    create_assignment(tmp_path)

    assignment = load_assignment(tmp_path)

    evidence = compare_assignment_pair_with_cohort(
        assignment,
        "S001",
        "S002",
        n=4,
    )

    assert evidence.cohort_size == 3
    assert evidence.ngram_size == 4
    assert len(evidence.matches) == 1

    match = evidence.matches[0]

    assert match.left_name == "calculate"
    assert match.right_name == "compute"
    assert match.shared_feature_count > 0


def test_assignment_pair_surfaces_pair_specific_rare_features(
    tmp_path: Path,
):
    create_assignment(tmp_path)

    assignment = load_assignment(tmp_path)

    evidence = compare_assignment_pair_with_cohort(
        assignment,
        "S001",
        "S002",
        n=4,
    )

    match = evidence.matches[0]

    pair_specific = [
        feature
        for feature in match.shared_features
        if feature.document_frequency == 2
    ]

    assert pair_specific

    assert all(
        feature.document_proportion
        == pytest.approx(2 / 3)
        for feature in pair_specific
    )


def test_assignment_pair_reports_empty_matches_when_one_side_has_no_methods(
    tmp_path: Path,
):
    create_assignment(tmp_path)

    write(
        tmp_path
        / "submissions"
        / "S004"
        / "Empty.java",
        """
class Empty {
}
""".strip(),
    )

    assignment = load_assignment(tmp_path)

    evidence = compare_assignment_pair_with_cohort(
        assignment,
        "S001",
        "S004",
        n=4,
    )

    assert evidence.cohort_size == 4
    assert evidence.matches == ()


def test_assignment_pair_rejects_unknown_submission(
    tmp_path: Path,
):
    create_assignment(tmp_path)

    assignment = load_assignment(tmp_path)

    with pytest.raises(
        ValueError,
        match="Unknown submission: UNKNOWN",
    ):
        compare_assignment_pair_with_cohort(
            assignment,
            "S001",
            "UNKNOWN",
            n=4,
        )


def test_cohort_rarity_distinguishes_common_from_pair_specific_structure(
    tmp_path: Path,
):
    write(
        tmp_path / "assignment.yaml",
        """
assignment:
  name: rarity-adversarial-test
  language: java
  submissions_directory: submissions
  starter_directory: starter
""".strip(),
    )

    write(
        tmp_path / "submissions" / "S001" / "First.java",
        """
class First {
    int common(int value) {
        return value + 1;
    }

    int unusual(int value) {
        int transformed = value * 17;
        transformed = transformed - 23;
        return transformed;
    }
}
""".strip(),
    )

    write(
        tmp_path / "submissions" / "S002" / "Second.java",
        """
class Second {
    int ordinary(int number) {
        return number + 1;
    }

    int distinctive(int number) {
        int changed = number * 17;
        changed = changed - 23;
        return changed;
    }
}
""".strip(),
    )

    write(
        tmp_path / "submissions" / "S003" / "Third.java",
        """
class Third {
    int helper(int amount) {
        return amount + 1;
    }
}
""".strip(),
    )

    write(
        tmp_path / "submissions" / "S004" / "Fourth.java",
        """
class Fourth {
    int helper(int input) {
        return input + 1;
    }
}
""".strip(),
    )

    assignment = load_assignment(tmp_path)

    evidence = compare_assignment_pair_with_cohort(
        assignment,
        "S001",
        "S002",
        n=4,
    )

    matches = {
        (match.left_name, match.right_name): match
        for match in evidence.matches
    }

    assert (
        "common",
        "ordinary",
    ) in matches

    assert (
        "unusual",
        "distinctive",
    ) in matches

    common_match = matches[
        ("common", "ordinary")
    ]

    unusual_match = matches[
        ("unusual", "distinctive")
    ]

    common_frequencies = {
        feature.document_frequency
        for feature in common_match.shared_features
    }

    unusual_frequencies = {
        feature.document_frequency
        for feature in unusual_match.shared_features
    }

    assert 4 in common_frequencies
    assert 2 in unusual_frequencies

    common_everywhere = [
        feature
        for feature in common_match.shared_features
        if feature.document_frequency == 4
    ]

    pair_specific = [
        feature
        for feature in unusual_match.shared_features
        if feature.document_frequency == 2
    ]

    assert common_everywhere
    assert pair_specific

    assert max(
        feature.rarity
        for feature in pair_specific
    ) > max(
        feature.rarity
        for feature in common_everywhere
    )
