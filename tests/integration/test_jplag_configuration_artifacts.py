import csv
import json
from pathlib import Path

import pytest

RESULT_ROOT = Path(
    "results/baselines/jplag-configurations"
)


def load_rows():
    with (
        RESULT_ROOT / "configurations.csv"
    ).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def find_pair(
    rows,
    configuration,
    right_submission_id,
):
    matches = [
        row
        for row in rows
        if (
            row["configuration"] == configuration
            and row["left_submission_id"] == "BASE"
            and row["right_submission_id"]
            == right_submission_id
        )
    ]

    assert len(matches) == 1
    return matches[0]


def test_jplag_configuration_artifacts_exist():
    assert (
        RESULT_ROOT / "configurations.csv"
    ).is_file()

    assert (
        RESULT_ROOT / "configurations.json"
    ).is_file()


def test_jplag_configuration_provenance_is_pinned():
    payload = json.loads(
        (
            RESULT_ROOT / "configurations.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert payload["version"] == "6.3.0"

    assert payload["jar_sha256"] == (
        "5f2c21e8b88ed77134effcb3a5a3ab13"
        "d188f6a3e16d401387f7479e92db9aa2"
    )

    assert payload["configuration_count"] == 3
    assert payload["pair_count_per_configuration"] == 9


def test_configuration_flags_are_explicit():
    payload = json.loads(
        (
            RESULT_ROOT / "configurations.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    configurations = payload["configurations"]

    assert configurations["standard"] == {
        "frequency_analysis": False,
        "jar_sha256": (
            "5f2c21e8b88ed77134effcb3a5a3ab13"
            "d188f6a3e16d401387f7479e92db9aa2"
        ),
        "normalized": False,
        "version": "6.3.0",
    }

    assert configurations["normalized"] == {
        "frequency_analysis": False,
        "jar_sha256": (
            "5f2c21e8b88ed77134effcb3a5a3ab13"
            "d188f6a3e16d401387f7479e92db9aa2"
        ),
        "normalized": True,
        "version": "6.3.0",
    }

    assert configurations["frequency"] == {
        "frequency_analysis": True,
        "jar_sha256": (
            "5f2c21e8b88ed77134effcb3a5a3ab13"
            "d188f6a3e16d401387f7479e92db9aa2"
        ),
        "normalized": False,
        "version": "6.3.0",
    }


def test_each_configuration_contains_nine_pairs():
    rows = load_rows()

    assert len(rows) == 27

    for configuration in (
        "standard",
        "normalized",
        "frequency",
    ):
        assert sum(
            row["configuration"] == configuration
            for row in rows
        ) == 9


def test_normalization_recovers_dead_code_pair():
    rows = load_rows()

    standard = find_pair(
        rows,
        "standard",
        "DEAD_CODE",
    )

    normalized = find_pair(
        rows,
        "normalized",
        "DEAD_CODE",
    )

    assert float(
        standard["average_similarity"]
    ) == pytest.approx(0.0)

    assert float(
        normalized["average_similarity"]
    ) == pytest.approx(1.0)


def test_class_split_remains_zero_in_all_configurations():
    rows = load_rows()

    for configuration in (
        "standard",
        "normalized",
        "frequency",
    ):
        row = find_pair(
            rows,
            configuration,
            "CLASS_SPLIT",
        )

        assert float(
            row["average_similarity"]
        ) == pytest.approx(0.0)


def test_lookalike_remains_maximal_in_all_configurations():
    rows = load_rows()

    for configuration in (
        "standard",
        "normalized",
        "frequency",
    ):
        row = find_pair(
            rows,
            configuration,
            "LOOKALIKE",
        )

        assert row["related"] == "False"

        assert float(
            row["average_similarity"]
        ) == pytest.approx(1.0)


def test_frequency_does_not_change_exported_pair_values():
    rows = load_rows()

    standard_rows = {
        (
            row["left_submission_id"],
            row["right_submission_id"],
        ): (
            float(row["average_similarity"]),
            float(row["max_similarity"]),
        )
        for row in rows
        if row["configuration"] == "standard"
    }

    frequency_rows = {
        (
            row["left_submission_id"],
            row["right_submission_id"],
        ): (
            float(row["average_similarity"]),
            float(row["max_similarity"]),
        )
        for row in rows
        if row["configuration"] == "frequency"
    }

    assert frequency_rows == standard_rows


def test_interpretation_limits_frequency_claim():
    payload = json.loads(
        (
            RESULT_ROOT / "configurations.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    interpretation = (
        payload["interpretation"].lower()
    )

    assert "unchanged csv values" in interpretation
    assert "no effect elsewhere" in interpretation
    assert "do not establish" in interpretation
    assert "general superiority" in interpretation
    assert "plagiarism-detection accuracy" in interpretation
