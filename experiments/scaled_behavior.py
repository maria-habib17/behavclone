"""Predeclared behavioral fixture for the scaled synthetic cohort.

The observations are synthetic imported test results. They are defined
before pairwise multi-signal measurements are generated.

The fixture intentionally contains:
- common correct observations, which are not behavioral pair evidence;
- family-local shared failures with identical wrong outputs;
- family-local shared failures with different wrong outputs;
- passing submissions within the same provenance family.

This prevents provenance labels from being copied directly into the
behavioral evidence channel.
"""

from experiments.scaled_synthetic import (
    scaled_cohort,
)

TEST_IDS = (
    "COMMON_SANITY",
    "PRICE_EDGE",
    "SCORE_EDGE",
    "STOCK_EDGE",
    "TEMP_EDGE",
)


def _observation(
    submission_id: str,
    test_id: str,
    status: str,
    expected: str,
    actual: str,
) -> str:
    return (
        f"{submission_id},"
        f"{test_id},"
        f"{status},"
        f"{expected},"
        f"{actual}"
    )


def scaled_behavioral_results() -> str:
    """Return deterministic imported behavior for the scaled cohort."""
    submission_ids = tuple(
        submission.submission_id
        for submission in scaled_cohort().submissions
    )

    lines = [
        "submission,test,status,expected,actual",
    ]

    failures = {
        (
            "PRICE_BASE",
            "PRICE_EDGE",
        ): ("107", "106"),
        (
            "PRICE_RENAMED",
            "PRICE_EDGE",
        ): ("107", "106"),
        (
            "PRICE_REORDERED",
            "PRICE_EDGE",
        ): ("107", "105"),
        (
            "SCORE_BASE",
            "SCORE_EDGE",
        ): ("24", "23"),
        (
            "SCORE_SPLIT",
            "SCORE_EDGE",
        ): ("24", "23"),
        (
            "STOCK_RENAMED",
            "STOCK_EDGE",
        ): ("30", "29"),
        (
            "STOCK_REORDERED",
            "STOCK_EDGE",
        ): ("30", "29"),
        (
            "TEMP_BASE",
            "TEMP_EDGE",
        ): ("10", "9"),
        (
            "TEMP_RENAMED",
            "TEMP_EDGE",
        ): ("10", "9"),
        (
            "TEMP_SPLIT",
            "TEMP_EDGE",
        ): ("10", "8"),
    }

    expected_by_test = {
        "COMMON_SANITY": "1",
        "PRICE_EDGE": "107",
        "SCORE_EDGE": "24",
        "STOCK_EDGE": "30",
        "TEMP_EDGE": "10",
    }

    for submission_id in submission_ids:
        for test_id in TEST_IDS:
            failure = failures.get(
                (
                    submission_id,
                    test_id,
                )
            )

            if failure is not None:
                expected, actual = failure

                lines.append(
                    _observation(
                        submission_id,
                        test_id,
                        "FAIL",
                        expected,
                        actual,
                    )
                )
                continue

            expected = expected_by_test[
                test_id
            ]

            lines.append(
                _observation(
                    submission_id,
                    test_id,
                    "PASS",
                    expected,
                    expected,
                )
            )

    return "\n".join(lines)
