"""Deterministic cohort-wide benchmark pair construction."""

from collections.abc import Iterable
from itertools import combinations

from experiments.models import BenchmarkPair


def all_cohort_pairs(
    submission_ids: Iterable[str],
    related_pairs: Iterable[BenchmarkPair],
) -> tuple[BenchmarkPair, ...]:
    """Label every unordered cohort pair from predeclared positives."""
    ids = tuple(sorted(submission_ids))

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Submission IDs must be unique."
        )

    known_ids = set(ids)
    related_by_key: dict[
        tuple[str, str],
        BenchmarkPair,
    ] = {}

    for pair in related_pairs:
        if not pair.related:
            raise ValueError(
                "Seeded related pairs must be labeled related."
            )

        if (
            pair.left_submission_id not in known_ids
            or pair.right_submission_id not in known_ids
        ):
            raise ValueError(
                "Seeded related pair references an unknown "
                "submission."
            )

        if (
            pair.left_submission_id
            == pair.right_submission_id
        ):
            raise ValueError(
                "A submission cannot be paired with itself."
            )

        key = tuple(
            sorted(
                (
                    pair.left_submission_id,
                    pair.right_submission_id,
                )
            )
        )

        if key in related_by_key:
            raise ValueError(
                "Duplicate seeded related pair: "
                f"{key[0]} / {key[1]}"
            )

        related_by_key[key] = pair

    pairs: list[BenchmarkPair] = []

    for left_id, right_id in combinations(ids, 2):
        key = (left_id, right_id)
        seeded = related_by_key.get(key)

        if seeded is None:
            pairs.append(
                BenchmarkPair(
                    left_submission_id=left_id,
                    right_submission_id=right_id,
                    related=False,
                )
            )
            continue

        pairs.append(
            BenchmarkPair(
                left_submission_id=left_id,
                right_submission_id=right_id,
                related=True,
                transformation=seeded.transformation,
            )
        )

    return tuple(pairs)
