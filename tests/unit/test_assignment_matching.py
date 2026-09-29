import pytest

from behavclone.matching.assignment import maximum_weight_assignment


def test_empty_matrix_has_empty_assignment():
    result = maximum_weight_assignment([])

    assert result.matches == ()
    assert result.total_similarity == 0.0


def test_single_fragment_assignment():
    result = maximum_weight_assignment([[0.8]])

    assert result.matched_count == 1
    assert result.total_similarity == pytest.approx(0.8)
    assert result.matches[0].left_index == 0
    assert result.matches[0].right_index == 0


def test_assignment_finds_permuted_correspondence():
    matrix = [
        [0.31, 1.00, 0.42],
        [0.27, 0.39, 1.00],
        [1.00, 0.33, 0.29],
    ]

    result = maximum_weight_assignment(matrix)

    pairs = {
        (match.left_index, match.right_index)
        for match in result.matches
    }

    assert pairs == {
        (0, 1),
        (1, 2),
        (2, 0),
    }

    assert result.total_similarity == pytest.approx(3.0)


def test_assignment_is_not_greedy():
    matrix = [
        [0.90, 0.80],
        [0.85, 0.10],
    ]

    result = maximum_weight_assignment(matrix)

    pairs = {
        (match.left_index, match.right_index)
        for match in result.matches
    }

    assert pairs == {
        (0, 1),
        (1, 0),
    }

    assert result.total_similarity == pytest.approx(1.65)


def test_rectangular_matrix_matches_smaller_side():
    matrix = [
        [1.00, 0.20, 0.10],
        [0.10, 0.30, 0.90],
    ]

    result = maximum_weight_assignment(matrix)

    assert result.matched_count == 2
    assert result.total_similarity == pytest.approx(1.90)


def test_more_rows_than_columns_is_supported():
    matrix = [
        [1.00, 0.10],
        [0.20, 0.90],
        [0.30, 0.40],
    ]

    result = maximum_weight_assignment(matrix)

    pairs = {
        (match.left_index, match.right_index)
        for match in result.matches
    }

    assert result.matched_count == 2
    assert pairs == {
        (0, 0),
        (1, 1),
    }

    assert result.total_similarity == pytest.approx(1.90)


def test_non_rectangular_matrix_is_rejected():
    with pytest.raises(
        ValueError,
        match="rectangular",
    ):
        maximum_weight_assignment(
            [
                [1.0, 0.5],
                [0.2],
            ]
        )
