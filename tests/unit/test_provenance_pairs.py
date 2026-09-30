import pytest

from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)
from experiments.provenance_pairs import provenance_family_pairs


def families():
    return {
        "PRICE": (
            "PRICE_BASE",
            "PRICE_RENAMED",
            "PRICE_REORDERED",
            "PRICE_SPLIT",
        ),
        "SCORE": (
            "SCORE_BASE",
            "SCORE_RENAMED",
            "SCORE_REORDERED",
            "SCORE_SPLIT",
        ),
        "STOCK": (
            "STOCK_BASE",
            "STOCK_RENAMED",
            "STOCK_REORDERED",
            "STOCK_SPLIT",
        ),
        "TEMP": (
            "TEMP_BASE",
            "TEMP_RENAMED",
            "TEMP_REORDERED",
            "TEMP_SPLIT",
        ),
    }


def test_related_pair_can_omit_isolated_transformation():
    pair = BenchmarkPair(
        left_submission_id="A",
        right_submission_id="B",
        related=True,
    )

    assert pair.related is True
    assert pair.transformation is None


def test_unrelated_pair_still_rejects_transformation():
    with pytest.raises(
        ValueError,
        match="Unrelated",
    ):
        BenchmarkPair(
            left_submission_id="A",
            right_submission_id="B",
            related=False,
            transformation=(
                TransformationKind.IDENTIFIER_RENAME
            ),
        )


def test_provenance_labels_complete_pair_space():
    pairs = provenance_family_pairs(
        families()
    )

    assert len(pairs) == 120
    assert sum(pair.related for pair in pairs) == 24
    assert sum(not pair.related for pair in pairs) == 96


def test_base_variant_retains_transformation_metadata():
    pairs = provenance_family_pairs(
        families()
    )

    pair = next(
        pair
        for pair in pairs
        if (
            pair.left_submission_id == "PRICE_BASE"
            and pair.right_submission_id
            == "PRICE_RENAMED"
        )
    )

    assert pair.related is True
    assert (
        pair.transformation
        == TransformationKind.IDENTIFIER_RENAME
    )


def test_transformed_pair_is_related_without_fake_transformation():
    pairs = provenance_family_pairs(
        families()
    )

    pair = next(
        pair
        for pair in pairs
        if (
            pair.left_submission_id == "PRICE_RENAMED"
            and pair.right_submission_id
            == "PRICE_SPLIT"
        )
    )

    assert pair.related is True
    assert pair.transformation is None


def test_cross_family_pair_is_control():
    pairs = provenance_family_pairs(
        families()
    )

    pair = next(
        pair
        for pair in pairs
        if (
            pair.left_submission_id == "PRICE_BASE"
            and pair.right_submission_id == "SCORE_BASE"
        )
    )

    assert pair.related is False
    assert pair.transformation is None


def test_duplicate_family_membership_is_rejected():
    with pytest.raises(
        ValueError,
        match="exactly one family",
    ):
        provenance_family_pairs(
            {
                "A": ("S1", "S2"),
                "B": ("S2", "S3"),
            }
        )


def test_empty_family_is_rejected():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        provenance_family_pairs(
            {
                "A": (),
            }
        )


def test_empty_family_mapping_is_rejected():
    with pytest.raises(
        ValueError,
        match="At least one",
    ):
        provenance_family_pairs({})
