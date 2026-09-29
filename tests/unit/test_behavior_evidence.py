import math

import pytest

from behavclone.behavior.evidence import (
    build_behavioral_cohort_profile,
    compare_submission_behavior,
    failure_rarity,
    wrong_output_rarity,
)
from behavclone.behavior.models import (
    BehavioralDataset,
)
from behavclone.behavior.models import TestObservation as BehaviorTestObservation
from behavclone.behavior.models import (
    TestStatus as BehaviorTestStatus,
)


def observation(
    submission: str,
    test: str,
    status: BehaviorTestStatus,
    expected: str,
    actual: str,
) -> BehaviorTestObservation:
    return BehaviorTestObservation(
        submission_id=submission,
        test_id=test,
        status=status,
        expected=expected,
        actual=actual,
    )


def dataset(
    *observations: BehaviorTestObservation,
) -> BehavioralDataset:
    return BehavioralDataset(
        observations=observations
    )


def test_profile_counts_failures_by_test():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    profile = build_behavioral_cohort_profile(results)

    assert profile.cohort_size == 3
    assert profile.failure_count("T01") == 2


def test_profile_counts_exact_wrong_outputs_separately():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
        observation(
            "S004",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    profile = build_behavioral_cohort_profile(results)

    assert profile.failure_count("T01") == 3
    assert profile.wrong_output_count(
        "T01",
        "9",
    ) == 2
    assert profile.wrong_output_count(
        "T01",
        "8",
    ) == 1


def test_rarer_failure_has_larger_rarity():
    results = dataset(
        observation(
            "S001",
            "COMMON",
            BehaviorTestStatus.FAIL,
            "x",
            "a",
        ),
        observation(
            "S002",
            "COMMON",
            BehaviorTestStatus.FAIL,
            "x",
            "b",
        ),
        observation(
            "S003",
            "COMMON",
            BehaviorTestStatus.FAIL,
            "x",
            "c",
        ),
        observation(
            "S001",
            "RARE",
            BehaviorTestStatus.FAIL,
            "x",
            "z",
        ),
        observation(
            "S004",
            "COMMON",
            BehaviorTestStatus.PASS,
            "x",
            "x",
        ),
    )

    profile = build_behavioral_cohort_profile(results)

    assert (
        failure_rarity(profile, "RARE")
        > failure_rarity(profile, "COMMON")
    )


def test_rarity_formula_is_explicit_and_reproducible():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    profile = build_behavioral_cohort_profile(results)

    expected = math.log((3 + 1) / (2 + 1)) + 1

    assert failure_rarity(
        profile,
        "T01",
    ) == pytest.approx(expected)


def test_shared_correct_passes_produce_no_evidence():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    assert evidence.shared_failures == ()
    assert evidence.shared_failure_count == 0
    assert evidence.identical_wrong_output_count == 0


def test_fail_and_pass_produce_no_shared_failure():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    assert evidence.shared_failures == ()


def test_shared_failure_with_different_outputs_is_preserved():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    assert evidence.shared_failure_count == 1

    shared = evidence.shared_failures[0]

    assert shared.test_id == "T01"
    assert shared.failure_count == 2
    assert not shared.identical_wrong_output
    assert shared.wrong_output_count is None
    assert shared.wrong_output_rarity is None
    assert shared.wrong_output_proportion is None


def test_identical_wrong_output_is_separate_evidence():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
        observation(
            "S004",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    shared = evidence.shared_failures[0]

    assert shared.identical_wrong_output
    assert shared.failure_count == 3
    assert shared.wrong_output_count == 2
    assert shared.failure_proportion == pytest.approx(
        3 / 4
    )
    assert shared.wrong_output_proportion == pytest.approx(
        2 / 4
    )
    assert evidence.identical_wrong_output_count == 1


def test_wrong_output_rarity_uses_exact_output_frequency():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S003",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
        observation(
            "S004",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "7",
        ),
    )

    profile = build_behavioral_cohort_profile(results)

    assert wrong_output_rarity(
        profile,
        "T01",
        "8",
    ) > wrong_output_rarity(
        profile,
        "T01",
        "9",
    )


def test_shared_failures_are_sorted_by_test_id():
    results = dataset(
        observation(
            "S001",
            "T02",
            BehaviorTestStatus.FAIL,
            "20",
            "19",
        ),
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "9",
        ),
        observation(
            "S002",
            "T02",
            BehaviorTestStatus.FAIL,
            "20",
            "18",
        ),
        observation(
            "S002",
            "T01",
            BehaviorTestStatus.FAIL,
            "10",
            "8",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    assert [
        item.test_id
        for item in evidence.shared_failures
    ] == [
        "T01",
        "T02",
    ]


def test_comparison_rejects_unknown_left_submission():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    with pytest.raises(
        ValueError,
        match="Unknown submission: S999",
    ):
        compare_submission_behavior(
            results,
            "S999",
            "S001",
        )


def test_comparison_rejects_unknown_right_submission():
    results = dataset(
        observation(
            "S001",
            "T01",
            BehaviorTestStatus.PASS,
            "10",
            "10",
        ),
    )

    with pytest.raises(
        ValueError,
        match="Unknown submission: S999",
    ):
        compare_submission_behavior(
            results,
            "S001",
            "S999",
        )


def test_identical_wrong_output_can_be_rarer_than_shared_failure():
    results = dataset(
        observation(
            "S001",
            "T_EDGE",
            BehaviorTestStatus.FAIL,
            "100",
            "99",
        ),
        observation(
            "S002",
            "T_EDGE",
            BehaviorTestStatus.FAIL,
            "100",
            "99",
        ),
        observation(
            "S003",
            "T_EDGE",
            BehaviorTestStatus.FAIL,
            "100",
            "98",
        ),
        observation(
            "S004",
            "T_EDGE",
            BehaviorTestStatus.FAIL,
            "100",
            "97",
        ),
        observation(
            "S005",
            "T_EDGE",
            BehaviorTestStatus.PASS,
            "100",
            "100",
        ),
    )

    evidence = compare_submission_behavior(
        results,
        "S001",
        "S002",
    )

    assert evidence.shared_failure_count == 1

    shared = evidence.shared_failures[0]

    assert shared.failure_count == 4
    assert shared.wrong_output_count == 2
    assert shared.identical_wrong_output

    assert shared.wrong_output_rarity is not None
    assert (
        shared.wrong_output_rarity
        > shared.failure_rarity
    )
