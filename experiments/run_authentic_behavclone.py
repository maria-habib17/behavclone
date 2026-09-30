"""First frozen authentic BehavClone measurement.

The selected IR-Plag case and authentic evaluation protocol were
committed before this runner was created or executed.

Raw external source code and the private source-to-anonymous-ID mapping
remain outside the BehavClone repository.
"""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from itertools import combinations
from pathlib import Path

from behavclone.cohort.assignment import (
    build_assignment_cohort_profile,
    compare_fragment_cohort_evidence,
)
from behavclone.ingestion.assignment import load_assignment
from behavclone.matching.submission import compare_submissions
from experiments.authentic_protocol import (
    AUTHENTIC_EVALUATION_PROTOCOL,
)

EXPECTED_SUBMISSION_COUNT = 15
EXPECTED_PAIR_COUNT = 105


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _write_json(
    path: Path,
    payload: object,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _cohort_summary(evidence) -> dict[str, float | int]:
    features = [
        feature
        for match in evidence.matches
        for feature in match.shared_features
    ]

    if not features:
        return {
            "shared_feature_count": 0,
            "pair_specific_feature_count": 0,
            "max_rarity": 0.0,
            "mean_rarity": 0.0,
        }

    rarities = [
        feature.rarity
        for feature in features
    ]

    return {
        "shared_feature_count": len(features),
        "pair_specific_feature_count": sum(
            1
            for feature in features
            if feature.document_frequency == 2
        ),
        "max_rarity": max(rarities),
        "mean_rarity": (
            sum(rarities) / len(rarities)
        ),
    }


def _load_private_manifest(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    if len(rows) != EXPECTED_SUBMISSION_COUNT:
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_SUBMISSION_COUNT} "
            "manifest rows."
        )

    ids = [
        row["anonymous_id"]
        for row in rows
    ]

    expected_ids = [
        f"A{index:03d}"
        for index in range(
            1,
            EXPECTED_SUBMISSION_COUNT + 1,
        )
    ]

    if ids != expected_ids:
        raise ValueError(
            "Private manifest anonymous IDs "
            "do not match the frozen sequence."
        )

    return rows


def _verify_sources(
    rows: list[dict[str, str]],
) -> None:
    seen_hashes: set[str] = set()

    for row in rows:
        source = Path(
            row["original_path"]
        )

        if not source.is_file():
            raise FileNotFoundError(
                f"Missing private source for "
                f"{row['anonymous_id']}."
            )

        actual = _sha256(source)
        expected = row[
            "sha256"
        ].lower()

        if actual != expected:
            raise ValueError(
                "Source hash changed for "
                f"{row['anonymous_id']}."
            )

        if actual in seen_hashes:
            raise ValueError(
                "Duplicate source content "
                "detected."
            )

        seen_hashes.add(actual)


def _write_assignment(
    root: Path,
    rows: list[dict[str, str]],
) -> None:
    submissions_root = (
        root / "submissions"
    )
    submissions_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    for row in rows:
        anonymous_id = row[
            "anonymous_id"
        ]

        source = Path(
            row["original_path"]
        )

        target_dir = (
            submissions_root
            / anonymous_id
        )
        target_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copyfile(
            source,
            target_dir / "Submission.java",
        )

    config = (
        'assignment:\n'
        '  name: IR-Plag case-01 authentic evaluation\n'
        '  language: java\n'
        '  submissions_dir: submissions\n'
    )

    (
        root / "assignment.yaml"
    ).write_text(
        config,
        encoding="utf-8",
    )


def run_authentic_behavclone(
    private_manifest: Path,
    output_root: Path,
) -> Path:
    protocol = (
        AUTHENTIC_EVALUATION_PROTOCOL
    )

    rows = _load_private_manifest(
        private_manifest
    )

    _verify_sources(rows)

    if output_root.exists():
        shutil.rmtree(
            output_root
        )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory(
        prefix="behavclone-authentic-"
    ) as temp_dir:
        assignment_root = (
            Path(temp_dir)
            / "assignment"
        )

        _write_assignment(
            assignment_root,
            rows,
        )

        assignment = load_assignment(
            assignment_root
        )

        if (
            len(assignment.submissions)
            != EXPECTED_SUBMISSION_COUNT
        ):
            raise ValueError(
                "Loaded assignment does not "
                "contain 15 submissions."
            )

        profile, fragments = (
            build_assignment_cohort_profile(
                assignment,
                protocol.cohort_ngram_size,
            )
        )

        submission_ids = sorted(
            fragments
        )

        pair_rows: list[
            dict[str, object]
        ] = []

        for left_id, right_id in combinations(
            submission_ids,
            2,
        ):
            left_submission = next(
                submission
                for submission
                in assignment.submissions
                if (
                    submission.submission_id
                    == left_id
                )
            )

            right_submission = next(
                submission
                for submission
                in assignment.submissions
                if (
                    submission.submission_id
                    == right_id
                )
            )

            comparison = compare_submissions(
                left_submission.source_files,
                right_submission.source_files,
                metric=(
                    protocol
                    .behavclone_matching_metric
                ),
            )

            cohort_evidence = (
                compare_fragment_cohort_evidence(
                    fragments[left_id],
                    fragments[right_id],
                    profile,
                )
            )

            cohort = _cohort_summary(
                cohort_evidence
            )

            pair_rows.append(
                {
                    "left_submission_id": (
                        left_id
                    ),
                    "right_submission_id": (
                        right_id
                    ),
                    "left_fragment_count": (
                        comparison
                        .left_fragment_count
                    ),
                    "right_fragment_count": (
                        comparison
                        .right_fragment_count
                    ),
                    "matched_count": (
                        comparison
                        .matched_count
                    ),
                    "left_coverage": (
                        comparison
                        .left_coverage
                    ),
                    "right_coverage": (
                        comparison
                        .right_coverage
                    ),
                    "mean_raw_similarity": (
                        comparison
                        .mean_raw_similarity
                    ),
                    "mean_normalized_similarity": (
                        comparison
                        .mean_normalized_similarity
                    ),
                    "mean_structural_similarity": (
                        comparison
                        .mean_structural_similarity
                    ),
                    **cohort,
                }
            )

    if len(pair_rows) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            "Expected exactly "
            f"{EXPECTED_PAIR_COUNT} "
            "pairwise measurements."
        )

    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "left_fragment_count",
        "right_fragment_count",
        "matched_count",
        "left_coverage",
        "right_coverage",
        "mean_raw_similarity",
        "mean_normalized_similarity",
        "mean_structural_similarity",
        "shared_feature_count",
        "pair_specific_feature_count",
        "max_rarity",
        "mean_rarity",
    ]

    csv_path = (
        output_root / "pairs.csv"
    )

    with csv_path.open(
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
        writer.writerows(pair_rows)

    _write_json(
        output_root / "pairs.json",
        pair_rows,
    )

    summary = {
        "experiment": (
            "authentic-false-positive"
        ),
        "dataset": "IR-Plag",
        "selected_case": "case-01",
        "cohort": "non-plagiarized",
        "language": "java",
        "submission_count": (
            EXPECTED_SUBMISSION_COUNT
        ),
        "pair_count": (
            EXPECTED_PAIR_COUNT
        ),
        "matching_metric": (
            protocol
            .behavclone_matching_metric
        ),
        "cohort_ngram_size": (
            protocol.cohort_ngram_size
        ),
        "behavioral_evidence": (
            "unavailable"
        ),
        "combined_score": False,
        "plagiarism_verdict": False,
        "interpretation": (
            "All pairs belong to the "
            "dataset-provided non-plagiarized "
            "cohort. Similarity and cohort "
            "evidence characterize surfacing "
            "and ambiguity; they do not infer "
            "plagiarism, authorship, or intent."
        ),
        "artifacts": {
            "pairs.csv": _sha256(
                csv_path
            ),
            "pairs.json": _sha256(
                output_root
                / "pairs.json"
            ),
        },
    }

    _write_json(
        output_root / "summary.json",
        summary,
    )

    return output_root


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the frozen authentic "
            "BehavClone measurement."
        )
    )
    parser.add_argument(
        "--private-manifest",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            Path("results")
            / "authentic"
            / "behavclone"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    output = run_authentic_behavclone(
        args.private_manifest,
        args.output,
    )

    print(
        "Wrote authentic BehavClone "
        f"artifacts to {output}"
    )


if __name__ == "__main__":
    main()
