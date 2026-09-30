import csv
import hashlib
import json
from pathlib import Path

ROOT = Path("results/authentic/behavclone")

EXPECTED_HASHES = {
    "pairs.csv": (
        "0d063996f6249ff5f8fcf28816fb4f7e"
        "b1f73d228d256cf6c0e7f04c37c323d4"
    ),
    "pairs.json": (
        "16583c07e239ccfd241414768b8c1858"
        "c0408e7c0fc14110dfdfcc9184ce7a6a"
    ),
    "summary.json": (
        "44289f5fafe094abaa0521d5372354f23"
        "6362062c5e88a622bdd923199baf126"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_authentic_behavclone_artifact_hashes():
    for name, expected in EXPECTED_HASHES.items():
        assert digest(ROOT / name) == expected


def test_authentic_behavclone_pair_count():
    with (ROOT / "pairs.csv").open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 105


def test_authentic_behavclone_anonymous_ids():
    rows = json.loads(
        (ROOT / "pairs.json").read_text(
            encoding="utf-8"
        )
    )

    ids = {
        submission_id
        for row in rows
        for submission_id in (
            row["left_submission_id"],
            row["right_submission_id"],
        )
    }

    assert ids == {
        f"A{i:03d}"
        for i in range(1, 16)
    }


def test_authentic_behavclone_summary_boundary():
    summary = json.loads(
        (ROOT / "summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["dataset"] == "IR-Plag"
    assert summary["selected_case"] == "case-01"
    assert summary["cohort"] == "non-plagiarized"
    assert summary["submission_count"] == 15
    assert summary["pair_count"] == 105
    assert summary["matching_metric"] == "normalized"
    assert summary["cohort_ngram_size"] == 4
    assert summary["behavioral_evidence"] == "unavailable"
    assert summary["combined_score"] is False
    assert summary["plagiarism_verdict"] is False
