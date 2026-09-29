"""Interpretable multi-signal evidence summaries.

This module keeps structural similarity, cohort-relative structural rarity,
and behavioral evidence as separate channels. It intentionally does not
produce a combined plagiarism score or automated verdict.
"""

from dataclasses import dataclass

from behavclone.behavior.models import SubmissionBehavioralEvidence
from behavclone.cohort.models import SubmissionCohortEvidence
from behavclone.matching.models import SubmissionComparison


@dataclass(frozen=True)
class StructuralEvidenceSummary:
    """Submission-level structural similarity measurements."""

    matched_count: int
    left_coverage: float
    right_coverage: float
    mean_raw_similarity: float
    mean_normalized_similarity: float
    mean_structural_similarity: float


@dataclass(frozen=True)
class CohortEvidenceSummary:
    """Summary of cohort-relative features shared by selected matches."""

    ngram_size: int
    cohort_size: int
    shared_feature_count: int
    pair_specific_feature_count: int
    max_rarity: float
    mean_rarity: float


@dataclass(frozen=True)
class BehavioralEvidenceSummary:
    """Summary of shared incorrect externally observed behavior."""

    cohort_size: int
    shared_failure_count: int
    identical_wrong_output_count: int
    max_failure_rarity: float
    max_wrong_output_rarity: float


@dataclass(frozen=True)
class MultiSignalEvidence:
    """Separate evidence channels for one submission pair."""

    left_submission_id: str
    right_submission_id: str
    structural: StructuralEvidenceSummary
    cohort: CohortEvidenceSummary
    behavioral: BehavioralEvidenceSummary | None


def summarize_structural_evidence(
    comparison: SubmissionComparison,
) -> StructuralEvidenceSummary:
    """Convert a submission comparison into structural evidence."""
    return StructuralEvidenceSummary(
        matched_count=comparison.matched_count,
        left_coverage=comparison.left_coverage,
        right_coverage=comparison.right_coverage,
        mean_raw_similarity=comparison.mean_raw_similarity,
        mean_normalized_similarity=comparison.mean_normalized_similarity,
        mean_structural_similarity=comparison.mean_structural_similarity,
    )


def summarize_cohort_evidence(
    evidence: SubmissionCohortEvidence,
) -> CohortEvidenceSummary:
    """Summarize shared cohort-relative structural features."""
    features = tuple(
        feature
        for match in evidence.matches
        for feature in match.shared_features
    )

    pair_specific = tuple(
        feature
        for feature in features
        if feature.document_frequency == 2
    )

    if features:
        max_rarity = max(
            feature.rarity
            for feature in features
        )
        mean_rarity = sum(
            feature.rarity
            for feature in features
        ) / len(features)
    else:
        max_rarity = 0.0
        mean_rarity = 0.0

    return CohortEvidenceSummary(
        ngram_size=evidence.ngram_size,
        cohort_size=evidence.cohort_size,
        shared_feature_count=len(features),
        pair_specific_feature_count=len(pair_specific),
        max_rarity=max_rarity,
        mean_rarity=mean_rarity,
    )


def summarize_behavioral_evidence(
    evidence: SubmissionBehavioralEvidence,
) -> BehavioralEvidenceSummary:
    """Summarize shared incorrect behavioral evidence."""
    if evidence.shared_failures:
        max_failure_rarity = max(
            item.failure_rarity
            for item in evidence.shared_failures
        )
    else:
        max_failure_rarity = 0.0

    wrong_output_rarities = tuple(
        item.wrong_output_rarity
        for item in evidence.shared_failures
        if item.wrong_output_rarity is not None
    )

    max_wrong_output_rarity = (
        max(wrong_output_rarities)
        if wrong_output_rarities
        else 0.0
    )

    return BehavioralEvidenceSummary(
        cohort_size=evidence.cohort_size,
        shared_failure_count=evidence.shared_failure_count,
        identical_wrong_output_count=(
            evidence.identical_wrong_output_count
        ),
        max_failure_rarity=max_failure_rarity,
        max_wrong_output_rarity=max_wrong_output_rarity,
    )
