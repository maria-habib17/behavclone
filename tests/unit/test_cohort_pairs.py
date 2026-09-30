import pytest

from experiments.cohort_pairs import all_cohort_pairs
from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)


def seeded_pair(
    left: str,
    right: str,
) -> BenchmarkPair:
    return BenchmarkPair(
        left_submission_id=left,
        right_submission_id=right,
        related=True,
        transformation=(
            TransformationKind.IDENTIFIER_RENAME
        ),
    )


def test_all_cohort_pairs_labels_complete_pair_space():
    pairs = all_cohort_pairs(
        ("C", "A", "B", "D"),
        (
            seeded_pair("A", "B"),
            seeded_pair("C", "D"),
        ),
    )

    assert len(pairs) == 6
    assert sum(pair.related for pair in pairs) == 2
    assert sum(not pair.related for pair in pairs) == 4

    assert [
        (
            pair.left_submission_id,
            pair.right_submission_id,
        )
        for pair in pairs
    ] == [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("B", "D"),
        ("C", "D"),
    ]


def test_related_pair_orientation_does_not_matter():
    pairs = all_cohort_pairs(
        ("A", "B"),
        (seeded_pair("B", "A"),),
    )

    assert len(pairs) == 1
    assert pairs[0].related is True
    assert pairs[0].left_submission_id == "A"
    assert pairs[0].right_submission_id == "B"


def test_duplicate_submission_ids_are_rejected():
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        all_cohort_pairs(
            ("A", "A"),
            (),
        )


def test_unknown_seeded_submission_is_rejected():
    with pytest.raises(
        ValueError,
        match="unknown",
    ):
        all_cohort_pairs(
            ("A", "B"),
            (seeded_pair("A", "C"),),
        )


def test_duplicate_seeded_pair_is_rejected():
    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        all_cohort_pairs(
            ("A", "B"),
            (
                seeded_pair("A", "B"),
                seeded_pair("B", "A"),
            ),
        )


def test_unrelated_seed_cannot_define_positive_label():
    unrelated = BenchmarkPair(
        left_submission_id="A",
        right_submission_id="B",
        related=False,
    )

    with pytest.raises(
        ValueError,
        match="labeled related",
    ):
        all_cohort_pairs(
            ("A", "B"),
            (unrelated,),
        )
