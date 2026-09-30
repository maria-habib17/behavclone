"""Provenance-family labels for the scaled cohort."""

from itertools import combinations

from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)


def _base_transformation(
    left_id: str,
    right_id: str,
) -> TransformationKind | None:
    """Return metadata for a known isolated base-to-variant edge."""
    suffixes = {
        left_id.rsplit("_", 1)[-1],
        right_id.rsplit("_", 1)[-1],
    }

    if "BASE" not in suffixes:
        return None

    if "RENAMED" in suffixes:
        return TransformationKind.IDENTIFIER_RENAME

    if "REORDERED" in suffixes:
        return TransformationKind.METHOD_REORDER

    if "SPLIT" in suffixes:
        return TransformationKind.CLASS_SPLIT

    return None


def provenance_family_pairs(
    family_members: dict[str, tuple[str, ...]],
) -> tuple[BenchmarkPair, ...]:
    """Label all within-family pairs related and cross-family pairs controls."""
    if not family_members:
        raise ValueError(
            "At least one provenance family is required."
        )

    all_ids = tuple(
        sorted(
            submission_id
            for members in family_members.values()
            for submission_id in members
        )
    )

    if any(
        not members
        for members in family_members.values()
    ):
        raise ValueError(
            "Provenance families cannot be empty."
        )

    if len(all_ids) != len(set(all_ids)):
        raise ValueError(
            "Submission IDs must belong to exactly one family."
        )

    family_by_id = {
        submission_id: family
        for family, members in family_members.items()
        for submission_id in members
    }

    pairs: list[BenchmarkPair] = []

    for left_id, right_id in combinations(all_ids, 2):
        same_family = (
            family_by_id[left_id]
            == family_by_id[right_id]
        )

        pairs.append(
            BenchmarkPair(
                left_submission_id=left_id,
                right_submission_id=right_id,
                related=same_family,
                transformation=(
                    _base_transformation(
                        left_id,
                        right_id,
                    )
                    if same_family
                    else None
                ),
            )
        )

    return tuple(pairs)
