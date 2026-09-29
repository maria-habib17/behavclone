import csv
import json
from pathlib import Path

import pytest

RESULT_ROOT = Path(
    "results/baselines/jplag"
)


def load_rows():
    with (
        RESULT_ROOT / "comparison.csv"
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
    right_submission_id,
):
    matches = [
        row
        for row in rows
        if (
            row["left_submission_id"] == "BASE"
            and row["right_submission_id"]
            == right_submission_id
        )
    ]

    assert len(matches) == 1
    return matches[0]


def test_controlled_jplag_artifacts_exist():
    assert (
        RESULT_ROOT / "comparison.csv"
    ).is_file()

    assert (
        RESULT_ROOT / "comparison.json"
    ).is_file()


def test_controlled_jplag_provenance_is_pinned():
    payload = json.loads(
        (
            RESULT_ROOT / "comparison.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert payload["jplag"] == {
        "frequency_analysis": False,
        "jar_sha256": (
            "5f2c21e8b88ed77134effcb3a5a3ab13"
            "d188f6a3e16d401387f7479e92db9aa2"
        ),
        "normalized": False,
        "version": "6.3.0",
    }


def test_controlled_comparison_contains_nine_pairs():
    rows = load_rows()

    assert len(rows) == 9


def test_identifier_rename_is_detected_by_both():
    row = find_pair(
        load_rows(),
        "ID_RENAME",
    )

    assert float(
        row["behavclone_normalized_similarity"]
    ) == pytest.approx(1.0)

    assert float(
        row["jplag_average_similarity"]
    ) == pytest.approx(1.0)


def test_dead_code_exposes_measured_difference():
    row = find_pair(
        load_rows(),
        "DEAD_CODE",
    )

    assert float(
        row["behavclone_normalized_similarity"]
    ) == pytest.approx(
        0.8372093023255814
    )

    assert float(
        row["jplag_average_similarity"]
    ) == pytest.approx(0.0)


def test_class_split_exposes_measured_difference():
    row = find_pair(
        load_rows(),
        "CLASS_SPLIT",
    )

    assert float(
        row["behavclone_normalized_similarity"]
    ) == pytest.approx(1.0)

    assert float(
        row["jplag_average_similarity"]
    ) == pytest.approx(0.0)


def test_lookalike_is_high_similarity_for_both():
    row = find_pair(
        load_rows(),
        "LOOKALIKE",
    )

    assert row["related"] == "False"

    assert float(
        row["behavclone_normalized_similarity"]
    ) == pytest.approx(1.0)

    assert float(
        row["jplag_average_similarity"]
    ) == pytest.approx(1.0)


def test_artifact_avoids_general_superiority_claim():
    payload = json.loads(
        (
            RESULT_ROOT / "comparison.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    interpretation = (
        payload["interpretation"].lower()
    )

    assert "do not establish" in interpretation
    assert "general superiority" in interpretation
    assert "plagiarism-detection accuracy" in interpretation
