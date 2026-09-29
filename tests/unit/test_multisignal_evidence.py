from pathlib import Path

import pytest

from behavclone.behavior.models import (
    SharedFailureEvidence,
    SubmissionBehavioralEvidence,
)
from behavclone.cohort.models import (
    CohortFeatureEvidence,
    FragmentCohortEvidence,
    SubmissionCohortEvidence,
)
from behavclone.evidence.models import (
    summarize_behavioral_evidence,
    summarize_cohort_evidence,
)


def cohort_feature(
    name: str,
    document_frequency: int,
    cohort_size: int,
    rarity: float,
) -> CohortFeatureEvidence:
    return CohortFeatureEvidence(
        feature=(name,),
        document_frequency=document_frequency,
        cohort_size=cohort_size,
        rarity=rarity,
    )


def test_cohort_summary_preserves_frequency_and_rarity_evidence():
    evidence = SubmissionCohortEvidence(
        cohort_size=10,
        ngram_size=4,
        matches=(
            FragmentCohortEvidence(
                left_file=Path("A.java"),
                left_name="first",
                left_start_line=1,
                right_file=Path("B.java"),
                right_name="second",
                right_start_line=1,
                shared_features=(
                    cohort_feature("rare", 2, 10, 2.2),
                    cohort_feature("common", 10, 10, 1.0),
                ),
            ),
        ),
    )

    summary = summarize_cohort_evidence(evidence)

    assert summary.cohort_size == 10
    assert summary.ngram_size == 4
    assert summary.shared_feature_count == 2
    assert summary.pair_specific_feature_count == 1
    assert summary.max_rarity == pytest.approx(2.2)
    assert summary.mean_rarity == pytest.approx(1.6)


def test_empty_cohort_evidence_has_zero_summary_values():
    evidence = SubmissionCohortEvidence(
        cohort_size=5,
        ngram_size=4,
        matches=(),
    )

    summary = summarize_cohort_evidence(evidence)

    assert summary.shared_feature_count == 0
    assert summary.pair_specific_feature_count == 0
    assert summary.max_rarity == 0.0
    assert summary.mean_rarity == 0.0


def test_behavior_summary_keeps_shared_failures_and_wrong_outputs_separate():
    evidence = SubmissionBehavioralEvidence(
        left_submission_id="S001",
        right_submission_id="S002",
        cohort_size=8,
        shared_failures=(
            SharedFailureEvidence(
                test_id="T01",
                expected="100",
                left_actual="99",
                right_actual="99",
                failure_count=3,
                cohort_size=8,
                failure_rarity=1.8,
                identical_wrong_output=True,
                wrong_output_count=2,
                wrong_output_rarity=2.1,
            ),
            SharedFailureEvidence(
                test_id="T02",
                expected="20",
                left_actual="18",
                right_actual="17",
                failure_count=4,
                cohort_size=8,
                failure_rarity=1.5,
                identical_wrong_output=False,
                wrong_output_count=None,
                wrong_output_rarity=None,
            ),
        ),
    )

    summary = summarize_behavioral_evidence(evidence)

    assert summary.shared_failure_count == 2
    assert summary.identical_wrong_output_count == 1
    assert summary.max_failure_rarity == pytest.approx(1.8)
    assert summary.max_wrong_output_rarity == pytest.approx(2.1)


def test_no_behavioral_failures_produce_zero_rarity_summary():
    evidence = SubmissionBehavioralEvidence(
        left_submission_id="S001",
        right_submission_id="S002",
        cohort_size=4,
        shared_failures=(),
    )

    summary = summarize_behavioral_evidence(evidence)

    assert summary.shared_failure_count == 0
    assert summary.identical_wrong_output_count == 0
    assert summary.max_failure_rarity == 0.0
    assert summary.max_wrong_output_rarity == 0.0
