import json
from pathlib import Path

DATASET_METADATA = Path(
    "experiments/authentic_dataset.json"
)


def load_metadata():
    return json.loads(
        DATASET_METADATA.read_text(
            encoding="utf-8"
        )
    )


def test_authentic_dataset_is_ir_plag():
    data = load_metadata()

    assert data["dataset"] == "IR-Plag"
    assert (
        data["dataset_repository"]
        == "oscarkarnalim/sourcecodeplagiarismdataset"
    )


def test_authentic_dataset_freezes_case_before_measurement():
    data = load_metadata()

    assert data["selected_case"] == "case-01"

    assert (
        data["cohort"]
        == "non-plagiarized"
    )

    assert (
        "before similarity measurement"
        in data["selection_rule"]
    )


def test_authentic_dataset_meets_frozen_minimum():
    data = load_metadata()

    assert data["language"] == "java"
    assert data["submission_count"] == 15
    assert data["submission_count"] >= 10


def test_authentic_dataset_uses_complete_submission():
    data = load_metadata()

    assert (
        data["unit_of_analysis"]
        == "complete submission"
    )


def test_authentic_dataset_keeps_behavior_unavailable():
    data = load_metadata()

    assert (
        data["behavioral_evidence"]
        == (
            "unavailable unless common test "
            "observations are independently established"
        )
    )


def test_authentic_dataset_has_no_verdict():
    data = load_metadata()

    assert data["combined_score"] is False
    assert data["plagiarism_verdict"] is False


def test_authentic_dataset_records_interpretation_boundary():
    data = load_metadata()

    boundary = data[
        "interpretation_boundary"
    ].lower()

    assert "benchmark provenance" in boundary
    assert "not independently verified" in boundary
    assert "author intent" in boundary
