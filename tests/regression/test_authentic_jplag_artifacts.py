import csv
import hashlib
import json
from pathlib import Path

ROOT = Path("results/authentic/jplag")

EXPECTED_HASHES = {
    "pairs.csv": (
        "9f34dd1d16afc0268e1b0e1d8bc969d3"
        "db24d38040d12249feba5676155ff1dd"
    ),
    "pairs.json": (
        "60f454dbee02b4ab341793073701e033"
        "61bb6fb7de37efd9c0a00126dd937c23"
    ),
    "summary.json": (
        "c3b1a08df483c4e9953a7f55f2d21a87"
        "c48cda2f76e9f96f8fc24999f545a76d"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_authentic_jplag_artifact_hashes():
    for name, expected in EXPECTED_HASHES.items():
        assert _sha256(ROOT / name) == expected


def test_authentic_jplag_pair_dimensions():
    with (ROOT / "pairs.csv").open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        csv_rows = list(csv.DictReader(handle))

    json_rows = json.loads(
        (ROOT / "pairs.json").read_text(
            encoding="utf-8"
        )
    )

    assert len(csv_rows) == 105
    assert len(json_rows) == 105

    expected_ids = {
        f"A{index:03d}"
        for index in range(1, 16)
    }

    observed = set()

    for row in json_rows:
        left = row["left_submission_id"]
        right = row["right_submission_id"]

        assert left in expected_ids
        assert right in expected_ids
        assert left < right

        pair = (left, right)

        assert pair not in observed
        observed.add(pair)

        assert 0.0 <= row["average_similarity"] <= 1.0
        assert 0.0 <= row["max_similarity"] <= 1.0

    assert len(observed) == 105


def test_authentic_jplag_summary_protocol():
    summary = json.loads(
        (ROOT / "summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["dataset"] == "IR-Plag"
    assert summary["case"] == "case-01"
    assert summary["cohort"] == "non-plagiarized"
    assert summary["language"] == "Java"

    assert summary["submission_count"] == 15
    assert summary["pair_count"] == 105

    assert summary["normalized"] is False
    assert summary["frequency_analysis"] is False
    assert summary["similarity_threshold"] == 0.0

    assert summary["similarity_fields"] == [
        "averageSimilarity",
        "maxSimilarity",
    ]

    assert summary["jplag"]["version"] == "6.3.0"

    assert summary["jplag"]["jar_sha256"] == (
        "5f2c21e8b88ed77134effcb3a5a3ab13"
        "d188f6a3e16d401387f7479e92db9aa2"
    )

    assert summary["behavioral_evidence"] == "unavailable"
    assert summary["combined_score"] is False
    assert summary["plagiarism_verdict"] is False


def test_authentic_jplag_artifacts_use_lf():
    for name in (
        "pairs.csv",
        "pairs.json",
        "summary.json",
    ):
        payload = (ROOT / name).read_bytes()

        assert b"\r\n" not in payload
