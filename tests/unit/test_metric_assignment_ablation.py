from behavclone.matching.assignment import maximum_weight_assignment
from behavclone.matching.models import FragmentSimilarity
from behavclone.matching.submission import _metric_score


def _assignment_for_metric(
    evidence_matrix: list[list[FragmentSimilarity]],
    metric: str,
) -> tuple[tuple[int, int], ...]:
    score_matrix = [
        [
            _metric_score(similarity, metric)
            for similarity in row
        ]
        for row in evidence_matrix
    ]

    assignment = maximum_weight_assignment(
        score_matrix
    )

    return tuple(
        (
            match.left_index,
            match.right_index,
        )
        for match in assignment.matches
    )


def test_raw_and_normalized_can_select_different_correspondences():
    evidence_matrix = [
        [
            FragmentSimilarity(
                raw=0.95,
                normalized=0.40,
                structural=0.50,
            ),
            FragmentSimilarity(
                raw=0.30,
                normalized=0.90,
                structural=0.50,
            ),
        ],
        [
            FragmentSimilarity(
                raw=0.25,
                normalized=0.85,
                structural=0.50,
            ),
            FragmentSimilarity(
                raw=0.90,
                normalized=0.35,
                structural=0.50,
            ),
        ],
    ]

    raw_assignment = _assignment_for_metric(
        evidence_matrix,
        "raw",
    )
    normalized_assignment = _assignment_for_metric(
        evidence_matrix,
        "normalized",
    )

    assert raw_assignment == (
        (0, 0),
        (1, 1),
    )

    assert normalized_assignment == (
        (0, 1),
        (1, 0),
    )

    assert raw_assignment != normalized_assignment


def test_structural_can_select_a_third_correspondence_pattern():
    evidence_matrix = [
        [
            FragmentSimilarity(
                raw=0.90,
                normalized=0.40,
                structural=0.30,
            ),
            FragmentSimilarity(
                raw=0.20,
                normalized=0.85,
                structural=0.95,
            ),
            FragmentSimilarity(
                raw=0.30,
                normalized=0.25,
                structural=0.20,
            ),
        ],
        [
            FragmentSimilarity(
                raw=0.25,
                normalized=0.90,
                structural=0.20,
            ),
            FragmentSimilarity(
                raw=0.85,
                normalized=0.30,
                structural=0.25,
            ),
            FragmentSimilarity(
                raw=0.20,
                normalized=0.20,
                structural=0.90,
            ),
        ],
        [
            FragmentSimilarity(
                raw=0.20,
                normalized=0.20,
                structural=0.85,
            ),
            FragmentSimilarity(
                raw=0.25,
                normalized=0.25,
                structural=0.20,
            ),
            FragmentSimilarity(
                raw=0.80,
                normalized=0.80,
                structural=0.25,
            ),
        ],
    ]

    raw_assignment = _assignment_for_metric(
        evidence_matrix,
        "raw",
    )
    normalized_assignment = _assignment_for_metric(
        evidence_matrix,
        "normalized",
    )
    structural_assignment = _assignment_for_metric(
        evidence_matrix,
        "structural",
    )

    assert raw_assignment == (
        (0, 0),
        (1, 1),
        (2, 2),
    )

    assert normalized_assignment == (
        (0, 1),
        (1, 0),
        (2, 2),
    )

    assert structural_assignment == (
        (0, 1),
        (1, 2),
        (2, 0),
    )

    assert len(
        {
            raw_assignment,
            normalized_assignment,
            structural_assignment,
        }
    ) == 3
