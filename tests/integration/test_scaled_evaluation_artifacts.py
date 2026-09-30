"""Regression tests for committed scaled-evaluation artifacts."""

import csv
import json
from pathlib import Path

import pytest

RESULT_ROOT = Path(
    "results/scaled"
)

SUMMARY_PATH = (
    RESULT_ROOT / "summary.json"
)

PAIRS_PATH = (
    RESULT_ROOT / "pairs.csv"
)


def _summary():
    return json.loads(
        SUMMARY_PATH.read_text(
            encoding="utf-8"
        )
    )


def _rows():
    with PAIRS_PATH.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def test_scaled_artifacts_exist():
    assert SUMMARY_PATH.is_file()
    assert PAIRS_PATH.is_file()


def test_scaled_summary_declares_corpus_shape():
    summary = _summary()

    assert (
        summary["experiment"]
        == "scaled-controlled-cohort"
    )
    assert summary["submission_count"] == 16
    assert summary["family_count"] == 4
    assert (
        summary["assignment_metric"]
        == "normalized"
    )
    assert summary["k_values"] == [5, 10, 20]


def test_scaled_csv_contains_complete_pair_space():
    rows = _rows()

    assert len(rows) == 120

    assert (
        sum(
            row["seeded_related"] == "True"
            for row in rows
        )
        == 12
    )

    assert (
        sum(
            row["provenance_related"] == "True"
            for row in rows
        )
        == 24
    )

    assert (
        sum(
            row["provenance_related"] == "False"
            for row in rows
        )
        == 96
    )


def test_seeded_label_view_counts():
    view = (
        _summary()["label_views"]
        ["seeded_edges"]
    )

    assert view["pair_count"] == 120
    assert view["related_count"] == 12
    assert view["control_count"] == 108


def test_provenance_label_view_counts():
    view = (
        _summary()["label_views"]
        ["provenance_families"]
    )

    assert view["pair_count"] == 120
    assert view["related_count"] == 24
    assert view["control_count"] == 96


def test_raw_provenance_retrieval_separates_this_corpus():
    metrics = (
        _summary()["label_views"]
        ["provenance_families"]
        ["metrics"]["raw"]
    )

    assert metrics["average_precision"] == pytest.approx(
        1.0
    )
    assert metrics["first_control_rank"] == 25

    assert (
        metrics["precision_at_k"]["20"]
        == pytest.approx(1.0)
    )


def test_normalized_provenance_retrieval_records_collisions():
    metrics = (
        _summary()["label_views"]
        ["provenance_families"]
        ["metrics"]["normalized"]
    )

    assert metrics["average_precision"] == pytest.approx(
        0.4989409893025989
    )
    assert metrics["first_control_rank"] == 7

    assert (
        metrics["precision_at_k"]["10"]
        == pytest.approx(0.6)
    )


def test_structural_provenance_retrieval_records_collisions():
    metrics = (
        _summary()["label_views"]
        ["provenance_families"]
        ["metrics"]["structural"]
    )

    assert metrics["average_precision"] == pytest.approx(
        0.4989409893025989
    )
    assert metrics["first_control_rank"] == 7


def test_cross_family_normalized_collision_is_preserved():
    rows = _rows()

    row = next(
        row
        for row in rows
        if {
            row["left_submission_id"],
            row["right_submission_id"],
        }
        == {
            "PRICE_BASE",
            "SCORE_BASE",
        }
    )

    assert row["provenance_related"] == "False"

    assert float(
        row["normalized_similarity"]
    ) == pytest.approx(1.0)

    assert float(
        row["structural_similarity"]
    ) == pytest.approx(1.0)

    assert float(
        row["raw_similarity"]
    ) == pytest.approx(
        2 / 3
    )


def test_interpretation_limits_claim_scope():
    interpretation = (
        _summary()["interpretation"].lower()
    )

    assert "synthetic" in interpretation
    assert (
        "do not establish plagiarism-detection accuracy"
        in interpretation
    )
    assert "general superiority" in interpretation
