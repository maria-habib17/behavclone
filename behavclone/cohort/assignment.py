from collections.abc import Iterable

from behavclone.cohort.models import (
    CohortProfile,
    FragmentCohortEvidence,
    SubmissionCohortEvidence,
)
from behavclone.cohort.rarity import (
    build_cohort_profile,
    shared_feature_evidence,
)
from behavclone.fragments.models import MethodFragment
from behavclone.fragments.starter import (
    StarterSignature,
    build_starter_signatures,
)
from behavclone.ingestion.models import Assignment, Submission
from behavclone.matching.assignment import maximum_weight_assignment
from behavclone.matching.submission import (
    build_similarity_matrix,
    extract_submission_fragments,
)


def extract_cohort_fragments(
    submissions: Iterable[Submission],
    starter_signatures: frozenset[StarterSignature] | None = None,
) -> dict[str, list[MethodFragment]]:
    """Extract comparable fragments for every submission in a cohort."""
    return {
        submission.submission_id: extract_submission_fragments(
            submission.source_files,
            starter_signatures,
        )
        for submission in submissions
    }


def build_assignment_cohort_profile(
    assignment: Assignment,
    n: int,
) -> tuple[
    CohortProfile,
    dict[str, list[MethodFragment]],
]:
    """Build a cohort profile after configured starter exclusion."""
    starter_signatures = build_starter_signatures(
        assignment.starter_files
    )

    fragments_by_submission = extract_cohort_fragments(
        assignment.submissions,
        starter_signatures,
    )

    profile = build_cohort_profile(
        fragments_by_submission.values(),
        n,
    )

    return profile, fragments_by_submission


def compare_fragment_cohort_evidence(
    left: list[MethodFragment],
    right: list[MethodFragment],
    profile: CohortProfile,
) -> SubmissionCohortEvidence:
    """Attach cohort rarity evidence to selected fragment matches."""
    if not left or not right:
        return SubmissionCohortEvidence(
            cohort_size=profile.cohort_size,
            ngram_size=profile.ngram_size,
            matches=(),
        )

    score_matrix, _ = build_similarity_matrix(
        left,
        right,
    )

    assignment = maximum_weight_assignment(
        score_matrix
    )

    matches = tuple(
        FragmentCohortEvidence(
            left_file=left[match.left_index].file_path,
            left_name=left[match.left_index].name,
            left_start_line=left[match.left_index].start_line,
            right_file=right[match.right_index].file_path,
            right_name=right[match.right_index].name,
            right_start_line=right[match.right_index].start_line,
            shared_features=shared_feature_evidence(
                left[match.left_index],
                right[match.right_index],
                profile,
            ),
        )
        for match in assignment.matches
    )

    return SubmissionCohortEvidence(
        cohort_size=profile.cohort_size,
        ngram_size=profile.ngram_size,
        matches=matches,
    )


def compare_assignment_pair_with_cohort(
    assignment: Assignment,
    left_submission_id: str,
    right_submission_id: str,
    n: int,
) -> SubmissionCohortEvidence:
    """Produce cohort-relative evidence for two assignment submissions."""
    profile, fragments_by_submission = (
        build_assignment_cohort_profile(
            assignment,
            n,
        )
    )

    if left_submission_id not in fragments_by_submission:
        raise ValueError(
            f"Unknown submission: {left_submission_id}"
        )

    if right_submission_id not in fragments_by_submission:
        raise ValueError(
            f"Unknown submission: {right_submission_id}"
        )

    return compare_fragment_cohort_evidence(
        fragments_by_submission[left_submission_id],
        fragments_by_submission[right_submission_id],
        profile,
    )
