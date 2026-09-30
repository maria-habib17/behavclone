"""Tests for the predeclared scaled behavioral fixture."""

import csv
import io
from collections import Counter

from behavclone.behavior.importer import (
    load_behavioral_results,
)
from experiments.scaled_behavior import (
    TEST_IDS,
    scaled_behavioral_results,
)
from experiments.scaled_synthetic import (
    scaled_cohort,
)


def _rows():
    return list(
        csv.DictReader(
            io.StringIO(
                scaled_behavioral_results()
            )
        )
    )


def test_scaled_behavior_covers_every_submission_and_test():
    rows = _rows()

    submission_ids = {
        submission.submission_id
        for submission in scaled_cohort().submissions
    }

    assert len(rows) == 16 * len(TEST_IDS)

    assert {
        row["submission"]
        for row in rows
    } == submission_ids

    counts = Counter(
        row["submission"]
        for row in rows
    )

    assert set(counts.values()) == {
        len(TEST_IDS)
    }


def test_scaled_behavior_has_unique_submission_test_pairs():
    rows = _rows()

    keys = {
        (
            row["submission"],
            row["test"],
        )
        for row in rows
    }

    assert len(keys) == len(rows)


def test_common_sanity_is_correct_for_every_submission():
    rows = _rows()

    common = [
        row
        for row in rows
        if row["test"] == "COMMON_SANITY"
    ]

    assert len(common) == 16

    assert {
        row["status"]
        for row in common
    } == {"PASS"}


def test_price_fixture_contains_same_and_different_wrong_outputs():
    rows = _rows()

    failures = {
        row["submission"]: row["actual"]
        for row in rows
        if (
            row["test"] == "PRICE_EDGE"
            and row["status"] == "FAIL"
        )
    }

    assert failures == {
        "PRICE_BASE": "106",
        "PRICE_RENAMED": "106",
        "PRICE_REORDERED": "105",
    }


def test_not_every_provenance_member_is_forced_to_fail():
    rows = _rows()

    price_split = next(
        row
        for row in rows
        if (
            row["submission"]
            == "PRICE_SPLIT"
            and row["test"]
            == "PRICE_EDGE"
        )
    )

    score_renamed = next(
        row
        for row in rows
        if (
            row["submission"]
            == "SCORE_RENAMED"
            and row["test"]
            == "SCORE_EDGE"
        )
    )

    assert price_split["status"] == "PASS"
    assert score_renamed["status"] == "PASS"


def test_failures_are_not_shared_across_families():
    rows = _rows()

    family_by_test = {
        "PRICE_EDGE": "PRICE_",
        "SCORE_EDGE": "SCORE_",
        "STOCK_EDGE": "STOCK_",
        "TEMP_EDGE": "TEMP_",
    }

    for row in rows:
        if row["status"] != "FAIL":
            continue

        assert row["submission"].startswith(
            family_by_test[row["test"]]
        )


def test_fixture_is_accepted_by_real_importer(tmp_path):
    path = (
        tmp_path
        / "test-results.csv"
    )

    path.write_text(
        scaled_behavioral_results()
        + "\n",
        encoding="utf-8",
    )

    dataset = load_behavioral_results(
        path
    )

    assert len(
        dataset.submission_ids
    ) == 16

    assert dataset.test_ids == set(
        TEST_IDS
    )

    assert len(
        dataset.observations
    ) == 80
