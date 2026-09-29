import math
from collections import Counter

from behavclone.behavior.models import (
    BehavioralCohortProfile,
    BehavioralDataset,
    SharedFailureEvidence,
    SubmissionBehavioralEvidence,
    TestObservation,
)


def _rarity(
    cohort_size: int,
    document_frequency: int,
) -> float:
    return math.log(
        (cohort_size + 1) / (document_frequency + 1)
    ) + 1.0


def _index_submission(
    dataset: BehavioralDataset,
    submission_id: str,
) -> dict[str, TestObservation]:
    return {
        observation.test_id: observation
        for observation in dataset.for_submission(submission_id)
    }


def build_behavioral_cohort_profile(
    dataset: BehavioralDataset,
) -> BehavioralCohortProfile:
    """Build submission-level failure and wrong-output frequencies."""
    failure_counts: Counter[str] = Counter()
    wrong_output_counts: Counter[tuple[str, str]] = Counter()

    for observation in dataset.observations:
        if not observation.failed:
            continue

        failure_counts[observation.test_id] += 1
        wrong_output_counts[
            (observation.test_id, observation.actual)
        ] += 1

    return BehavioralCohortProfile(
        cohort_size=len(dataset.submission_ids),
        failure_counts=dict(failure_counts),
        wrong_output_counts=dict(wrong_output_counts),
    )


def failure_rarity(
    profile: BehavioralCohortProfile,
    test_id: str,
) -> float:
    """Return cohort rarity for failure of one test."""
    return _rarity(
        profile.cohort_size,
        profile.failure_count(test_id),
    )


def wrong_output_rarity(
    profile: BehavioralCohortProfile,
    test_id: str,
    actual: str,
) -> float:
    """Return cohort rarity for one exact failed-test output."""
    return _rarity(
        profile.cohort_size,
        profile.wrong_output_count(test_id, actual),
    )


def compare_submission_behavior(
    dataset: BehavioralDataset,
    left_submission_id: str,
    right_submission_id: str,
) -> SubmissionBehavioralEvidence:
    """Compare two submissions using shared externally observed failures."""
    if left_submission_id not in dataset.submission_ids:
        raise ValueError(
            f"Unknown submission: {left_submission_id}"
        )

    if right_submission_id not in dataset.submission_ids:
        raise ValueError(
            f"Unknown submission: {right_submission_id}"
        )

    profile = build_behavioral_cohort_profile(dataset)

    left = _index_submission(
        dataset,
        left_submission_id,
    )
    right = _index_submission(
        dataset,
        right_submission_id,
    )

    shared_failures: list[SharedFailureEvidence] = []

    for test_id in sorted(left.keys() & right.keys()):
        left_observation = left[test_id]
        right_observation = right[test_id]

        if (
            not left_observation.failed
            or not right_observation.failed
        ):
            continue

        identical_wrong_output = (
            left_observation.actual
            == right_observation.actual
        )

        wrong_count: int | None = None
        wrong_rarity: float | None = None

        if identical_wrong_output:
            wrong_count = profile.wrong_output_count(
                test_id,
                left_observation.actual,
            )
            wrong_rarity = wrong_output_rarity(
                profile,
                test_id,
                left_observation.actual,
            )

        shared_failures.append(
            SharedFailureEvidence(
                test_id=test_id,
                expected=left_observation.expected,
                left_actual=left_observation.actual,
                right_actual=right_observation.actual,
                failure_count=profile.failure_count(test_id),
                cohort_size=profile.cohort_size,
                failure_rarity=failure_rarity(
                    profile,
                    test_id,
                ),
                identical_wrong_output=identical_wrong_output,
                wrong_output_count=wrong_count,
                wrong_output_rarity=wrong_rarity,
            )
        )

    return SubmissionBehavioralEvidence(
        left_submission_id=left_submission_id,
        right_submission_id=right_submission_id,
        cohort_size=profile.cohort_size,
        shared_failures=tuple(shared_failures),
    )
