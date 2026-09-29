"""Reporting helpers for multi-signal evidence experiments."""

import csv
from dataclasses import dataclass
from pathlib import Path

from behavclone.evidence.models import MultiSignalEvidence


@dataclass(frozen=True)
class MultiSignalRow:
    """Flat, interpretable evidence-channel measurements for one pair."""

    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: str
    raw_similarity: float
    normalized_similarity: float
    structural_similarity: float
    shared_cohort_feature_count: int
    pair_specific_cohort_feature_count: int
    max_cohort_rarity: float
    mean_cohort_rarity: float
    shared_failure_count: int
    identical_wrong_output_count: int
    max_failure_rarity: float
    max_wrong_output_rarity: float


def build_multisignal_row(
    evidence: MultiSignalEvidence,
    *,
    related: bool,
    transformation: str,
) -> MultiSignalRow:
    """Flatten separate evidence channels without combining their scores."""
    behavioral = evidence.behavioral

    return MultiSignalRow(
        left_submission_id=evidence.left_submission_id,
        right_submission_id=evidence.right_submission_id,
        related=related,
        transformation=transformation,
        raw_similarity=evidence.structural.mean_raw_similarity,
        normalized_similarity=(
            evidence.structural.mean_normalized_similarity
        ),
        structural_similarity=(
            evidence.structural.mean_structural_similarity
        ),
        shared_cohort_feature_count=(
            evidence.cohort.shared_feature_count
        ),
        pair_specific_cohort_feature_count=(
            evidence.cohort.pair_specific_feature_count
        ),
        max_cohort_rarity=evidence.cohort.max_rarity,
        mean_cohort_rarity=evidence.cohort.mean_rarity,
        shared_failure_count=(
            behavioral.shared_failure_count
            if behavioral is not None
            else 0
        ),
        identical_wrong_output_count=(
            behavioral.identical_wrong_output_count
            if behavioral is not None
            else 0
        ),
        max_failure_rarity=(
            behavioral.max_failure_rarity
            if behavioral is not None
            else 0.0
        ),
        max_wrong_output_rarity=(
            behavioral.max_wrong_output_rarity
            if behavioral is not None
            else 0.0
        ),
    )


def write_multisignal_csv(
    path: Path,
    rows: tuple[MultiSignalRow, ...],
) -> None:
    """Write deterministic evidence-channel measurements."""
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "related",
        "transformation",
        "raw_similarity",
        "normalized_similarity",
        "structural_similarity",
        "shared_cohort_feature_count",
        "pair_specific_cohort_feature_count",
        "max_cohort_rarity",
        "mean_cohort_rarity",
        "shared_failure_count",
        "identical_wrong_output_count",
        "max_failure_rarity",
        "max_wrong_output_rarity",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field: getattr(row, field)
                    for field in fieldnames
                }
            )
