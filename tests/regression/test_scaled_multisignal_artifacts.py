"""Regression tests for the frozen scaled multi-signal artifacts."""

import csv
import json
from pathlib import Path

import pytest

RESULT_ROOT = Path(
    "results/scaled-multisignal"
)


def _summary():
    return json.loads(
        (
            RESULT_ROOT
            / "summary.json"
        ).read_text(
            encoding="utf-8"
        )
    )


def _rows():
    with (
        RESULT_ROOT
        / "evidence.csv"
    ).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def _related(row):
    return (
        row["related"].strip().lower()
        == "true"
    )


def _number(
    row,
    field,
):
    return float(
        row[field]
    )


def test_scaled_multisignal_summary_shape():
    summary = _summary()

    assert summary["submission_count"] == 16
    assert summary["family_count"] == 4
    assert summary["pair_count"] == 120
    assert summary["related_pair_count"] == 24
    assert summary["control_pair_count"] == 96


def test_scaled_multisignal_collision_counts_are_frozen():
    summary = _summary()

    assert (
        summary[
            "related_summary"
        ][
            "normalized_collision_pairs"
        ]
        == 24
    )

    assert (
        summary[
            "control_summary"
        ][
            "normalized_collision_pairs"
        ]
        == 48
    )


def test_scaled_multisignal_behavior_counts_are_frozen():
    summary = _summary()

    related = summary[
        "related_summary"
    ]

    controls = summary[
        "control_summary"
    ]

    assert (
        related[
            "behavior_shared_failure_pairs"
        ]
        == 8
    )

    assert (
        related[
            "behavior_identical_wrong_output_pairs"
        ]
        == 4
    )

    assert (
        controls[
            "behavior_shared_failure_pairs"
        ]
        == 0
    )

    assert (
        controls[
            "behavior_identical_wrong_output_pairs"
        ]
        == 0
    )


def test_pair_specific_features_do_not_discriminate_collisions():
    rows = _rows()

    collisions = [
        row
        for row in rows
        if _number(
            row,
            "mean_normalized_similarity",
        )
        == 1.0
    ]

    assert len(
        collisions
    ) == 72

    assert {
        _number(
            row,
            "cohort_pair_specific_feature_count",
        )
        for row in collisions
    } == {0.0}


def test_control_collision_cohort_values_are_frozen():
    rows = _rows()

    controls = [
        row
        for row in rows
        if (
            not _related(row)
            and _number(
                row,
                "mean_normalized_similarity",
            )
            == 1.0
        )
    ]

    assert len(
        controls
    ) == 48

    assert {
        _number(
            row,
            "cohort_shared_feature_count",
        )
        for row in controls
    } == {30.0}

    assert {
        _number(
            row,
            "cohort_max_rarity",
        )
        for row in controls
    } == {
        1.2682639865946794
    }

    assert {
        _number(
            row,
            "cohort_mean_rarity",
        )
        for row in controls
    } == {
        1.0715370630919143
    }


def test_some_related_collisions_have_stronger_cohort_evidence():
    rows = _rows()

    related = [
        row
        for row in rows
        if (
            _related(row)
            and _number(
                row,
                "mean_normalized_similarity",
            )
            == 1.0
        )
    ]

    assert len(
        related
    ) == 24

    assert max(
        _number(
            row,
            "cohort_shared_feature_count",
        )
        for row in related
    ) == 34.0

    assert max(
        _number(
            row,
            "cohort_max_rarity",
        )
        for row in related
    ) == 2.2237754316221157

    assert max(
        _number(
            row,
            "cohort_mean_rarity",
        )
        for row in related
    ) == pytest.approx(
        1.6478811108587672
    )


def test_behavior_adds_evidence_for_subset_of_related_collisions():
    rows = _rows()

    related_collisions = [
        row
        for row in rows
        if (
            _related(row)
            and _number(
                row,
                "mean_normalized_similarity",
            )
            == 1.0
        )
    ]

    controls = [
        row
        for row in rows
        if (
            not _related(row)
            and _number(
                row,
                "mean_normalized_similarity",
            )
            == 1.0
        )
    ]

    related_shared = sum(
        _number(
            row,
            "behavior_shared_failure_count",
        )
        > 0
        for row in related_collisions
    )

    related_identical = sum(
        _number(
            row,
            "behavior_identical_wrong_output_count",
        )
        > 0
        for row in related_collisions
    )

    control_shared = sum(
        _number(
            row,
            "behavior_shared_failure_count",
        )
        > 0
        for row in controls
    )

    control_identical = sum(
        _number(
            row,
            "behavior_identical_wrong_output_count",
        )
        > 0
        for row in controls
    )

    assert related_shared == 8
    assert related_identical == 4
    assert control_shared == 0
    assert control_identical == 0
