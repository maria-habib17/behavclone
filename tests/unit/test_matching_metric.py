import pytest

from behavclone.matching.models import FragmentSimilarity
from behavclone.matching.submission import _metric_score


@pytest.mark.parametrize(
    ("metric", "expected"),
    [
        ("raw", 0.2),
        ("normalized", 0.6),
        ("structural", 0.9),
    ],
)
def test_metric_score_selects_requested_representation(
    metric,
    expected,
):
    similarity = FragmentSimilarity(
        raw=0.2,
        normalized=0.6,
        structural=0.9,
    )

    assert _metric_score(
        similarity,
        metric,
    ) == pytest.approx(expected)


def test_metric_score_rejects_unknown_metric():
    similarity = FragmentSimilarity(
        raw=0.2,
        normalized=0.6,
        structural=0.9,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported matching metric",
    ):
        _metric_score(
            similarity,
            "unknown",
        )
