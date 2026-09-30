import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(
    "results/authentic/behavclone"
)

EXPECTED_HASHES = {
    "pairs.csv": (
        "0d063996f6249ff5f8fcf28816fb4f7eb"
        "1f73d228d256cf6c0e7f04c37c323d4"
    ),
    "pairs.json": (
        "4f423eabfb7449c78c5853155b44b3eb4"
        "6c94e5510bbbaF143b506e6bbaa2ee7"
    ).lower(),
    "summary.json": (
        "74a163a180c6eb0cecb538d73028946c1c"
        "efa258a5da41d7df790d57cab3be82"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_authentic_behavclone_artifact_hashes():
    for name, expected in EXPECTED_HASHES.items():
        assert digest(ROOT / name) == expected


def test_authentic_behavclone_pair_count():
    with (
        ROOT / "pairs.csv"
    ).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    assert len(rows) == 105


def test_authentic_behavclone_anonymous_ids():
    rows = json.loads(
        (
            ROOT / "pairs.json"
        ).read_text(
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
        (
            ROOT / "summary.json"
        ).read_text(
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

    assert (
        summary["behavioral_evidence"]
        == "unavailable"
    )

    assert summary["combined_score"] is False
    assert summary["plagiarism_verdict"] is False
