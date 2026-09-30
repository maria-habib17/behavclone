"""Frozen JPlag baseline for the authentic IR-Plag cohort."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from dataclasses import asdict
from itertools import combinations
from pathlib import Path

from behavclone.baselines.jplag_runner import (
    JPlagProvenance,
    run_jplag,
)
from experiments.authentic_protocol import (
    AUTHENTIC_EVALUATION_PROTOCOL,
)
from experiments.run_jplag_comparison import (
    JPLAG_SHA256,
    JPLAG_VERSION,
)

EXPECTED_SUBMISSION_COUNT = 15
EXPECTED_PAIR_COUNT = 105
EXPECTED_IDS = tuple(
    f"A{index:03d}"
    for index in range(1, EXPECTED_SUBMISSION_COUNT + 1)
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _write_json(
    path: Path,
    payload: object,
) -> None:
    serialized = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    path.write_bytes(
        serialized.encode("utf-8")
    )


def _write_csv(
    path: Path,
    rows: list[dict[str, object]],
) -> None:
    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "average_similarity",
        "max_similarity",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)


def _load_private_manifest(
    path: Path,
) -> dict[str, tuple[Path, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if len(rows) != EXPECTED_SUBMISSION_COUNT:
        raise ValueError(
            "Authentic manifest must contain exactly "
            f"{EXPECTED_SUBMISSION_COUNT} submissions."
        )

    required = {
        "anonymous_id",
        "original_path",
        "sha256",
    }

    if not required.issubset(
        set(reader.fieldnames or ())
    ):
        raise ValueError(
            "Authentic manifest is missing required columns."
        )

    manifest: dict[str, tuple[Path, str]] = {}

    for row in rows:
        anonymous_id = row["anonymous_id"].strip()
        source = Path(row["original_path"])
        digest = row["sha256"].strip().lower()

        if anonymous_id in manifest:
            raise ValueError(
                "Duplicate anonymous ID in manifest: "
                f"{anonymous_id}"
            )

        manifest[anonymous_id] = (
            source,
            digest,
        )

    if tuple(sorted(manifest)) != EXPECTED_IDS:
        raise ValueError(
            "Authentic manifest must contain exactly "
            "A001 through A015."
        )

    return manifest


def _verify_sources(
    manifest: dict[str, tuple[Path, str]],
) -> None:
    observed_hashes: set[str] = set()

    for anonymous_id in EXPECTED_IDS:
        source, expected_hash = manifest[
            anonymous_id
        ]

        if not source.is_file():
            raise ValueError(
                "Authentic source does not exist for "
                f"{anonymous_id}: {source}"
            )

        actual_hash = _sha256(source)

        if actual_hash != expected_hash:
            raise ValueError(
                "Authentic source SHA-256 mismatch for "
                f"{anonymous_id}."
            )

        if actual_hash in observed_hashes:
            raise ValueError(
                "Duplicate authentic source content detected."
            )

        observed_hashes.add(actual_hash)


def _prepare_submissions(
    root: Path,
    manifest: dict[str, tuple[Path, str]],
) -> Path:
    submissions = root / "submissions"
    submissions.mkdir(
        parents=True,
        exist_ok=False,
    )

    for anonymous_id in EXPECTED_IDS:
        source, _ = manifest[anonymous_id]

        destination = (
            submissions
            / anonymous_id
            / "Submission.java"
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=False,
        )

        shutil.copyfile(
            source,
            destination,
        )

    return submissions


def _portable_provenance(
    provenance: JPlagProvenance,
) -> dict[str, object]:
    payload = asdict(provenance)

    # Machine-specific paths are not part of the
    # portable frozen result artifact.
    payload.pop("java_executable")
    payload.pop("jar_path")

    return payload


def run_authentic_jplag(
    manifest_path: str | Path,
    output_root: str | Path,
    *,
    java_executable: str | Path,
    jplag_jar: str | Path,
) -> Path:
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    if protocol.jplag_normalized:
        raise ValueError(
            "Frozen primary JPlag protocol must use "
            "normalized=False."
        )

    if protocol.jplag_frequency_analysis:
        raise ValueError(
            "Frozen primary JPlag protocol must use "
            "frequency_analysis=False."
        )

    if protocol.jplag_similarity_fields != (
        "averageSimilarity",
        "maxSimilarity",
    ):
        raise ValueError(
            "Unexpected frozen JPlag similarity fields."
        )

    manifest_path = Path(manifest_path)
    output_root = Path(output_root)

    if output_root.exists():
        raise ValueError(
            "Authentic JPlag output already exists: "
            f"{output_root}"
        )

    manifest = _load_private_manifest(
        manifest_path
    )
    _verify_sources(manifest)

    expected_pairs = tuple(
        combinations(EXPECTED_IDS, 2)
    )

    if len(expected_pairs) != EXPECTED_PAIR_COUNT:
        raise AssertionError(
            "Unexpected authentic pair count."
        )

    with tempfile.TemporaryDirectory(
        prefix="behavclone-authentic-jplag-"
    ) as temporary:
        temporary_root = Path(temporary)

        submissions = _prepare_submissions(
            temporary_root,
            manifest,
        )

        run = run_jplag(
            submissions,
            temporary_root / "jplag",
            java_executable=java_executable,
            jar_path=jplag_jar,
            version=JPLAG_VERSION,
            expected_jar_sha256=JPLAG_SHA256,
            normalize=False,
            frequency=False,
        )

        if len(run.results.pairs) != EXPECTED_PAIR_COUNT:
            raise ValueError(
                "JPlag did not return exactly "
                f"{EXPECTED_PAIR_COUNT} comparisons; got "
                f"{len(run.results.pairs)}."
            )

        rows: list[dict[str, object]] = []

        for left, right in expected_pairs:
            pair = run.results.find_pair(
                left,
                right,
            )

            rows.append(
                {
                    "left_submission_id": left,
                    "right_submission_id": right,
                    "average_similarity": (
                        pair.average_similarity
                    ),
                    "max_similarity": (
                        pair.max_similarity
                    ),
                }
            )

        output_root.mkdir(
            parents=True,
            exist_ok=False,
        )

        pairs_csv = output_root / "pairs.csv"
        pairs_json = output_root / "pairs.json"
        summary_json = output_root / "summary.json"

        _write_csv(
            pairs_csv,
            rows,
        )

        _write_json(
            pairs_json,
            rows,
        )

        summary = {
            "experiment": (
                "authentic-false-positive-jplag"
            ),
            "dataset": "IR-Plag",
            "case": "case-01",
            "cohort": "non-plagiarized",
            "language": "Java",
            "submission_count": (
                EXPECTED_SUBMISSION_COUNT
            ),
            "pair_count": EXPECTED_PAIR_COUNT,
            "dataset_label": (
                "dataset-provided non-plagiarized"
            ),
            "jplag": _portable_provenance(
                run.provenance
            ),
            "similarity_fields": [
                "averageSimilarity",
                "maxSimilarity",
            ],
            "similarity_threshold": 0.0,
            "normalized": False,
            "frequency_analysis": False,
            "behavioral_evidence": "unavailable",
            "combined_score": False,
            "plagiarism_verdict": False,
            "interpretation_boundary": (
                "Dataset-provided labels are used for "
                "authentic false-positive and similarity-"
                "ambiguity analysis; they do not establish "
                "author intent or prove absence of copying."
            ),
        }

        summary["artifact_sha256"] = {
            "pairs.csv": _sha256(pairs_csv),
            "pairs.json": _sha256(pairs_json),
        }

        _write_json(
            summary_json,
            summary,
        )

    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        required=True,
    )
    parser.add_argument(
        "--output",
        required=True,
    )
    parser.add_argument(
        "--java",
        required=True,
    )
    parser.add_argument(
        "--jplag-jar",
        required=True,
    )

    args = parser.parse_args()

    output = run_authentic_jplag(
        args.manifest,
        args.output,
        java_executable=args.java,
        jplag_jar=args.jplag_jar,
    )

    print(
        "Wrote frozen authentic JPlag baseline to "
        f"{output}"
    )


if __name__ == "__main__":
    main()
