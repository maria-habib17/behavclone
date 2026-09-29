from pathlib import Path

import pytest

from behavclone.matching.models import (
    FragmentSimilarity,
    SubmissionComparison,
    SubmissionFragmentMatch,
)


def match(raw: float) -> SubmissionFragmentMatch:
    return SubmissionFragmentMatch(
        left_file=Path("left.java"),
        left_name="left",
        left_start_line=1,
        right_file=Path("right.java"),
        right_name="right",
        right_start_line=1,
        similarity=FragmentSimilarity(
            raw=raw,
            normalized=0.5,
            structural=0.6,
        ),
    )


def test_mean_raw_similarity_averages_selected_matches():
    comparison = SubmissionComparison(
        left_fragment_count=2,
        right_fragment_count=2,
        matches=(
            match(0.4),
            match(0.8),
        ),
    )

    assert comparison.mean_raw_similarity == pytest.approx(
        0.6
    )


def test_mean_raw_similarity_is_zero_without_matches():
    comparison = SubmissionComparison(
        left_fragment_count=0,
        right_fragment_count=0,
        matches=(),
    )

    assert comparison.mean_raw_similarity == 0.0
