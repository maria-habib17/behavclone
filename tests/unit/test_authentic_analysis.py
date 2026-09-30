from pathlib import Path

import pytest

from experiments.analyze_authentic import (
    _describe,
    _pearson,
    _tie_summary,
)


def test_describe_reports_ties_and_extremes():
    result = _describe(
        [0.0, 0.5, 1.0, 1.0]
    )

    assert result == {
        "min": 0.0,
        "median": 0.75,
        "mean": 0.625,
        "max": 1.0,
        "zero_count": 1,
        "one_count": 2,
        "unique_values": 3,
    }


def test_pearson_identical_vectors():
    assert _pearson(
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    ) == pytest.approx(1.0)


def test_tie_summary_reports_largest_group():
    rows = {
        ("A001", "A002"): {"score": 1.0},
        ("A001", "A003"): {"score": 1.0},
        ("A002", "A003"): {"score": 0.5},
    }

    result = _tie_summary(
        rows,
        "score",
    )

    assert result["distinct_score_count"] == 2
    assert result["largest_tie_group"] == 2
    assert result["groups"] == [
        {
            "score": 1.0,
            "pair_count": 2,
        },
        {
            "score": 0.5,
            "pair_count": 1,
        },
    ]


def test_analysis_output_does_not_exist_yet():
    assert not Path(
        "results/authentic/analysis"
    ).exists()
