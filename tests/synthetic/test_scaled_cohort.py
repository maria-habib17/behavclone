from experiments.cohort_pairs import all_cohort_pairs
from experiments.models import TransformationKind
from experiments.scaled_synthetic import (
    SCALED_FAMILIES,
    scaled_cohort,
)


def test_scaled_cohort_has_sixteen_unique_submissions():
    cohort = scaled_cohort()

    ids = [
        submission.submission_id
        for submission in cohort.submissions
    ]

    assert len(ids) == 16
    assert len(set(ids)) == 16


def test_scaled_cohort_predeclares_twelve_related_pairs():
    cohort = scaled_cohort()

    assert len(cohort.related_pairs) == 12

    transformations = [
        pair.transformation
        for pair in cohort.related_pairs
    ]

    assert transformations.count(
        TransformationKind.IDENTIFIER_RENAME
    ) == 4

    assert transformations.count(
        TransformationKind.METHOD_REORDER
    ) == 4

    assert transformations.count(
        TransformationKind.CLASS_SPLIT
    ) == 4


def test_scaled_cohort_expands_to_complete_pair_space():
    cohort = scaled_cohort()

    pairs = all_cohort_pairs(
        (
            submission.submission_id
            for submission in cohort.submissions
        ),
        cohort.related_pairs,
    )

    assert len(pairs) == 120
    assert sum(pair.related for pair in pairs) == 12
    assert sum(not pair.related for pair in pairs) == 108


def test_cross_family_pairs_are_controls():
    cohort = scaled_cohort()

    pairs = all_cohort_pairs(
        (
            submission.submission_id
            for submission in cohort.submissions
        ),
        cohort.related_pairs,
    )

    price_score = next(
        pair
        for pair in pairs
        if (
            pair.left_submission_id == "PRICE_BASE"
            and pair.right_submission_id == "SCORE_BASE"
        )
    )

    assert price_score.related is False
    assert price_score.transformation is None


def test_nonbase_same_family_pairs_are_controls():
    cohort = scaled_cohort()

    pairs = all_cohort_pairs(
        (
            submission.submission_id
            for submission in cohort.submissions
        ),
        cohort.related_pairs,
    )

    pair = next(
        pair
        for pair in pairs
        if (
            pair.left_submission_id == "PRICE_RENAMED"
            and pair.right_submission_id
            == "PRICE_REORDERED"
        )
    )

    assert pair.related is False
    assert pair.transformation is None


def test_scaled_family_metadata_covers_every_submission_once():
    cohort = scaled_cohort()

    family_ids = [
        submission_id
        for members in SCALED_FAMILIES.values()
        for submission_id in members
    ]

    cohort_ids = [
        submission.submission_id
        for submission in cohort.submissions
    ]

    assert len(family_ids) == 16
    assert len(set(family_ids)) == 16
    assert set(family_ids) == set(cohort_ids)


def test_scaled_family_metadata_has_four_families_of_four():
    assert len(SCALED_FAMILIES) == 4

    assert all(
        len(members) == 4
        for members in SCALED_FAMILIES.values()
    )
