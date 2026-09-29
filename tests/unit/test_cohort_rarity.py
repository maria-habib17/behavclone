import math
from pathlib import Path

import pytest

from behavclone.cohort.rarity import (
    build_cohort_profile,
    feature_rarity,
    fragment_features,
    shared_feature_evidence,
    submission_features,
    token_ngrams,
)
from behavclone.fragments.models import MethodFragment


def fragment(
    name: str,
    source: str,
) -> MethodFragment:
    """Create a method fragment for cohort-rarity tests."""
    return MethodFragment(
        file_path=Path(f"{name}.java"),
        kind="method_declaration",
        name=name,
        start_line=1,
        end_line=1,
        source=source,
    )


def test_token_ngrams_extracts_contiguous_features():
    result = token_ngrams(
        ("a", "b", "c", "d"),
        3,
    )

    assert result == frozenset({
        ("a", "b", "c"),
        ("b", "c", "d"),
    })


def test_token_ngrams_rejects_non_positive_n():
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        token_ngrams(
            ("a", "b"),
            0,
        )


def test_token_ngrams_returns_empty_when_fragment_is_too_short():
    result = token_ngrams(
        ("a", "b"),
        3,
    )

    assert result == frozenset()


def test_identifier_renaming_preserves_fragment_features():
    first = fragment(
        "calculate",
        """
        int calculate(int price, int discount) {
            return price - discount;
        }
        """,
    )

    second = fragment(
        "compute",
        """
        int compute(int amount, int reduction) {
            return amount - reduction;
        }
        """,
    )

    assert fragment_features(
        first,
        4,
    ) == fragment_features(
        second,
        4,
    )


def test_duplicate_feature_counts_once_per_submission():
    repeated = fragment(
        "repeated",
        """
        int repeated(int value) {
            value = value + 1;
            value = value + 1;
            return value;
        }
        """,
    )

    features = submission_features(
        [repeated, repeated],
        3,
    )

    profile = build_cohort_profile(
        [
            [repeated, repeated],
        ],
        3,
    )

    assert features

    assert all(
        frequency == 1
        for frequency in profile.document_frequencies.values()
    )


def test_document_frequency_counts_submissions_not_occurrences():
    first = fragment(
        "first",
        """
        int first(int value) {
            int result = value * 7;
            return result;
        }
        """,
    )

    renamed = fragment(
        "renamed",
        """
        int renamed(int number) {
            int changed = number * 7;
            return changed;
        }
        """,
    )

    unrelated = fragment(
        "unrelated",
        """
        boolean unrelated(boolean flag) {
            return !flag;
        }
        """,
    )

    n = 4

    first_features = fragment_features(
        first,
        n,
    )
    renamed_features = fragment_features(
        renamed,
        n,
    )
    unrelated_features = fragment_features(
        unrelated,
        n,
    )

    pair_specific_features = (
        first_features
        & renamed_features
        - unrelated_features
    )

    assert pair_specific_features

    profile = build_cohort_profile(
        [
            [first, first],
            [renamed],
            [unrelated],
        ],
        n,
    )

    assert all(
        profile.document_frequencies[feature] == 2
        for feature in pair_specific_features
    )


def test_rare_feature_has_more_rarity_than_common_feature():
    common = (
        "return",
        "<ID>",
        ";",
    )

    rare = (
        "<ID>",
        "*",
        "<INT>",
    )

    profile = build_cohort_profile(
        [],
        3,
    )

    profile = type(profile)(
        cohort_size=10,
        ngram_size=3,
        document_frequencies={
            common: 10,
            rare: 2,
        },
    )

    common_evidence = feature_rarity(
        profile,
        common,
    )

    rare_evidence = feature_rarity(
        profile,
        rare,
    )

    assert rare_evidence.rarity > common_evidence.rarity

    assert common_evidence.document_proportion == pytest.approx(
        1.0
    )

    assert rare_evidence.document_proportion == pytest.approx(
        0.2
    )


def test_rarity_formula_is_explicit_and_reproducible():
    feature = (
        "a",
        "b",
        "c",
    )

    profile = build_cohort_profile(
        [],
        3,
    )

    profile = type(profile)(
        cohort_size=8,
        ngram_size=3,
        document_frequencies={
            feature: 2,
        },
    )

    evidence = feature_rarity(
        profile,
        feature,
    )

    expected = math.log(
        (8 + 1) / (2 + 1)
    ) + 1.0

    assert evidence.rarity == pytest.approx(
        expected
    )


def test_shared_feature_evidence_contains_only_shared_features():
    first = fragment(
        "calculate",
        """
        int calculate(int price, int discount) {
            return price - discount;
        }
        """,
    )

    second = fragment(
        "compute",
        """
        int compute(int amount, int reduction) {
            return amount - reduction;
        }
        """,
    )

    third = fragment(
        "other",
        """
        boolean other(boolean flag) {
            return !flag;
        }
        """,
    )

    profile = build_cohort_profile(
        [
            [first],
            [second],
            [third],
        ],
        4,
    )

    evidence = shared_feature_evidence(
        first,
        second,
        profile,
    )

    expected_shared = (
        fragment_features(first, 4)
        & fragment_features(second, 4)
    )

    assert {
        item.feature
        for item in evidence
    } == expected_shared


def test_shared_feature_evidence_is_sorted_rarest_first():
    first = fragment(
        "first",
        """
        int first(int value) {
            int adjusted = value * 7;
            return adjusted + 3;
        }
        """,
    )

    second = fragment(
        "second",
        """
        int second(int number) {
            int changed = number * 7;
            return changed + 3;
        }
        """,
    )

    common = fragment(
        "common",
        """
        int common(int input) {
            return input + 3;
        }
        """,
    )

    profile = build_cohort_profile(
        [
            [first],
            [second],
            [common],
        ],
        3,
    )

    evidence = shared_feature_evidence(
        first,
        second,
        profile,
    )

    rarities = [
        item.rarity
        for item in evidence
    ]

    assert rarities == sorted(
        rarities,
        reverse=True,
    )
