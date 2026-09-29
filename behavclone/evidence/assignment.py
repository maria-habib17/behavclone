"""Pair-level orchestration for interpretable multi-signal evidence."""

from behavclone.behavior.assignment import (
    behavioral_results_path,
    compare_assignment_behavior,
)
from behavclone.cohort.assignment import (
    build_assignment_cohort_profile,
    compare_fragment_cohort_evidence,
)
from behavclone.evidence.models import (
    MultiSignalEvidence,
    summarize_behavioral_evidence,
    summarize_cohort_evidence,
    summarize_structural_evidence,
)
from behavclone.fragments.starter import build_starter_signatures
from behavclone.ingestion.models import Assignment, Submission
from behavclone.matching.models import MatchingMetric
from behavclone.matching.submission import compare_submissions


def _submission_by_id(
    assignment: Assignment,
    submission_id: str,
) -> Submission:
    for submission in assignment.submissions:
        if submission.submission_id == submission_id:
            return submission

    raise ValueError(
        f"Unknown assignment submission: {submission_id}"
    )


def compare_assignment_pair_evidence(
    assignment: Assignment,
    left_submission_id: str,
    right_submission_id: str,
    *,
    ngram_size: int = 4,
    matching_metric: MatchingMetric = "normalized",
) -> MultiSignalEvidence:
    """Produce separate structural, cohort, and behavioral evidence channels."""
    left = _submission_by_id(
        assignment,
        left_submission_id,
    )
    right = _submission_by_id(
        assignment,
        right_submission_id,
    )

    starter_signatures = build_starter_signatures(
        assignment.starter_files
    )

    structural_comparison = compare_submissions(
        left.source_files,
        right.source_files,
        starter_signatures=starter_signatures,
        metric=matching_metric,
    )

    profile, fragments_by_submission = (
        build_assignment_cohort_profile(
            assignment,
            n=ngram_size,
        )
    )

    cohort_evidence = compare_fragment_cohort_evidence(
        fragments_by_submission[left_submission_id],
        fragments_by_submission[right_submission_id],
        profile,
    )

    behavioral_summary = None

    results_path = behavioral_results_path(assignment)

    if results_path is not None:
        behavioral_evidence = compare_assignment_behavior(
            assignment,
            left_submission_id,
            right_submission_id,
        )
        behavioral_summary = summarize_behavioral_evidence(
            behavioral_evidence
        )

    return MultiSignalEvidence(
        left_submission_id=left_submission_id,
        right_submission_id=right_submission_id,
        structural=summarize_structural_evidence(
            structural_comparison
        ),
        cohort=summarize_cohort_evidence(
            cohort_evidence
        ),
        behavioral=behavioral_summary,
    )
