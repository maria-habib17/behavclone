import csv
import hashlib
from pathlib import Path

import pytest

from experiments.run_authentic_jplag import (
    EXPECTED_IDS,
    EXPECTED_PAIR_COUNT,
    EXPECTED_SUBMISSION_COUNT,
    _load_private_manifest,
    _write_csv,
    _write_json,
)


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_authentic_jplag_frozen_dimensions():
    assert EXPECTED_SUBMISSION_COUNT == 15
    assert EXPECTED_PAIR_COUNT == 105
    assert EXPECTED_IDS == tuple(
        f"A{index:03d}"
        for index in range(1, 16)
    )


def test_authentic_jplag_manifest_requires_all_ids(
    tmp_path,
):
    manifest = tmp_path / "manifest.csv"

    with manifest.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "anonymous_id",
                "original_path",
                "sha256",
            ],
            lineterminator="\n",
        )

        writer.writeheader()

        for index in range(1, 15):
            writer.writerow(
                {
                    "anonymous_id": (
                        f"A{index:03d}"
                    ),
                    "original_path": "unused.java",
                    "sha256": "0" * 64,
                }
            )

    with pytest.raises(
        ValueError,
        match="exactly 15 submissions",
    ):
        _load_private_manifest(manifest)


def test_authentic_jplag_json_is_lf_deterministic(
    tmp_path,
):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    payload = {
        "z": 1,
        "a": [2, 3],
    }

    _write_json(first, payload)
    _write_json(second, payload)

    assert first.read_bytes() == second.read_bytes()
    assert b"\r\n" not in first.read_bytes()
    assert digest(first) == digest(second)


def test_authentic_jplag_csv_is_lf_deterministic(
    tmp_path,
):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"

    rows = [
        {
            "left_submission_id": "A001",
            "right_submission_id": "A002",
            "average_similarity": 0.5,
            "max_similarity": 0.75,
        }
    ]

    _write_csv(first, rows)
    _write_csv(second, rows)

    assert first.read_bytes() == second.read_bytes()
    assert b"\r\n" not in first.read_bytes()
    assert digest(first) == digest(second)
