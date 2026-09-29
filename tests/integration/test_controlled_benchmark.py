from pathlib import Path

import pytest

from behavclone.ingestion.assignment import load_assignment
from experiments.controlled import controlled_pairs
from experiments.evaluation import rank_benchmark
from experiments.models import TransformationKind
from experiments.runner import run_structural_benchmark
from experiments.synthetic import (
    controlled_submissions,
    write_synthetic_assignment,
)


def run_controlled(tmp_path: Path):
    root = tmp_path / "assignment"

    write_synthetic_assignment(
        root,
        controlled_submissions(),
    )

    assignment = load_assignment(root)

    return run_structural_benchmark(
        assignment,
        controlled_pairs(),
    )


def by_right_submission(result):
    return {
        pair.right_submission_id: pair
        for pair in result.pairs
    }


def test_controlled_benchmark_contains_related_and_controls(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)

    assert len(result.pairs) == 9
    assert len(result.related_pairs) == 6
    assert len(result.unrelated_pairs) == 3

    assert {
        pair.transformation
        for pair in result.related_pairs
    } == {
        TransformationKind.IDENTIFIER_RENAME,
        TransformationKind.METHOD_REORDER,
        TransformationKind.CLASS_RENAME,
        TransformationKind.FILE_RENAME,
        TransformationKind.DEAD_CODE,
        TransformationKind.CLASS_SPLIT,
    }


def test_identifier_rename_is_recovered_by_normalization(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["ID_RENAME"]

    assert pair.matched_count == 2
    assert pair.left_coverage == pytest.approx(1.0)
    assert pair.right_coverage == pytest.approx(1.0)

    assert pair.mean_raw_similarity < (
        pair.mean_normalized_similarity
    )
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )
    assert pair.mean_structural_similarity == pytest.approx(
        1.0
    )


def test_method_reorder_preserves_complete_matching(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["METHOD_REORDER"]

    assert pair.matched_count == 2
    assert pair.left_coverage == pytest.approx(1.0)
    assert pair.right_coverage == pytest.approx(1.0)
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )


def test_class_rename_does_not_define_correspondence(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["CLASS_RENAME"]

    assert pair.matched_count == 2
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )


def test_file_rename_does_not_define_correspondence(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["FILE_RENAME"]

    assert pair.matched_count == 2
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )


def test_class_split_matches_across_multiple_files(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["CLASS_SPLIT"]

    assert pair.matched_count == 2
    assert pair.left_coverage == pytest.approx(1.0)
    assert pair.right_coverage == pytest.approx(1.0)
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )


def test_dead_code_reduces_similarity_without_losing_coverage(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["DEAD_CODE"]

    assert pair.matched_count == 2
    assert pair.left_coverage == pytest.approx(1.0)
    assert pair.right_coverage == pytest.approx(1.0)

    assert 0.0 < pair.mean_normalized_similarity < 1.0
    assert 0.0 < pair.mean_structural_similarity < 1.0


def test_unrelated_controls_are_not_assumed_to_be_zero(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)

    assert len(result.unrelated_pairs) == 3

    for pair in result.unrelated_pairs:
        assert 0.0 <= pair.mean_raw_similarity <= 1.0
        assert (
            0.0
            <= pair.mean_normalized_similarity
            <= 1.0
        )
        assert (
            0.0
            <= pair.mean_structural_similarity
            <= 1.0
        )


def test_lookalike_exposes_normalization_false_positive_pressure(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)
    pair = by_right_submission(result)["LOOKALIKE"]

    assert pair.related is False

    assert pair.mean_raw_similarity < (
        pair.mean_normalized_similarity
    )

    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )

    assert pair.mean_structural_similarity == pytest.approx(
        1.0
    )


def test_normalized_ranking_retains_all_pairs(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)

    evaluation = rank_benchmark(
        result,
        "normalized",
    )

    assert len(evaluation.ranked_pairs) == 9
    assert len(evaluation.related_ranks) == 6
    assert len(evaluation.unrelated_ranks) == 3

    assert {
        item.pair.right_submission_id
        for item in evaluation.ranked_pairs
    } == {
        pair.right_submission_id
        for pair in result.pairs
    }


def test_structural_ranking_retains_all_pairs(
    tmp_path: Path,
):
    result = run_controlled(tmp_path)

    evaluation = rank_benchmark(
        result,
        "structural",
    )

    assert len(evaluation.ranked_pairs) == 9
    assert len(evaluation.related_ranks) == 6
    assert len(evaluation.unrelated_ranks) == 3
