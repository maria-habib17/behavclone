from functools import cache

from behavclone.matching.models import (
    FragmentAssignment,
    FragmentMatch,
)


def maximum_weight_assignment(
    matrix: list[list[float]],
) -> FragmentAssignment:
    """Find an exact maximum-weight one-to-one assignment.

    Rows and columns represent fragments from two submissions. The
    algorithm is independent of source order: each row may match any
    unused column.

    This dynamic-programming baseline is intended for small research
    datasets. A polynomial-time assignment algorithm can replace it
    later without changing the public result model.
    """

    if not matrix:
        return FragmentAssignment(
            matches=(),
            total_similarity=0.0,
        )

    column_count = len(matrix[0])

    if column_count == 0:
        return FragmentAssignment(
            matches=(),
            total_similarity=0.0,
        )

    if any(len(row) != column_count for row in matrix):
        raise ValueError("Similarity matrix must be rectangular.")

    if len(matrix) <= column_count:
        return _assign_rows(matrix)

    transposed = [
        [matrix[row][column] for row in range(len(matrix))]
        for column in range(column_count)
    ]

    assignment = _assign_rows(transposed)

    matches = tuple(
        FragmentMatch(
            left_index=match.right_index,
            right_index=match.left_index,
            similarity=match.similarity,
        )
        for match in assignment.matches
    )

    return FragmentAssignment(
        matches=tuple(
            sorted(
                matches,
                key=lambda match: (
                    match.left_index,
                    match.right_index,
                ),
            )
        ),
        total_similarity=assignment.total_similarity,
    )


def _assign_rows(
    matrix: list[list[float]],
) -> FragmentAssignment:
    """Assign every row to a distinct column."""

    row_count = len(matrix)
    column_count = len(matrix[0])

    @cache
    def solve(
        row_index: int,
        used_columns: int,
    ) -> tuple[float, tuple[tuple[int, int], ...]]:
        if row_index == row_count:
            return 0.0, ()

        best_score = float("-inf")
        best_pairs: tuple[tuple[int, int], ...] = ()

        for column_index in range(column_count):
            column_bit = 1 << column_index

            if used_columns & column_bit:
                continue

            remaining_score, remaining_pairs = solve(
                row_index + 1,
                used_columns | column_bit,
            )

            candidate_score = (
                matrix[row_index][column_index]
                + remaining_score
            )

            candidate_pairs = (
                (row_index, column_index),
                *remaining_pairs,
            )

            if candidate_score > best_score:
                best_score = candidate_score
                best_pairs = candidate_pairs

        return best_score, best_pairs

    total_similarity, pairs = solve(0, 0)

    matches = tuple(
        FragmentMatch(
            left_index=row,
            right_index=column,
            similarity=matrix[row][column],
        )
        for row, column in pairs
    )

    return FragmentAssignment(
        matches=matches,
        total_similarity=total_similarity,
    )
