"""Controlled comparison between BehavClone and external JPlag."""

import argparse
import csv
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from behavclone.baselines.jplag_runner import (
    JPlagProvenance,
    run_jplag,
)
from behavclone.ingestion.assignment import load_assignment
from experiments.controlled import controlled_pairs
from experiments.runner import run_structural_benchmark
from experiments.synthetic import (
    controlled_submissions,
    write_synthetic_assignment,
)

JPLAG_VERSION = "6.3.0"
JPLAG_SHA256 = (
    "5f2c21e8b88ed77134effcb3a5a3ab13"
    "d188f6a3e16d401387f7479e92db9aa2"
)


@dataclass(frozen=True)
class BaselineComparisonRow:
    """Side-by-side measurements for one controlled pair."""

    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: str
    behavclone_raw_similarity: float
    behavclone_normalized_similarity: float
    behavclone_structural_similarity: float
    jplag_average_similarity: float
    jplag_max_similarity: float


def _write_json(
    path: Path,
    payload: object,
) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_csv(
    path: Path,
    rows: tuple[BaselineComparisonRow, ...],
) -> None:
    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "related",
        "transformation",
        "behavclone_raw_similarity",
        "behavclone_normalized_similarity",
        "behavclone_structural_similarity",
        "jplag_average_similarity",
        "jplag_max_similarity",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field: getattr(row, field)
                    for field in fieldnames
                }
            )


def _portable_provenance(
    provenance: JPlagProvenance,
) -> dict[str, object]:
    return {
        "version": provenance.version,
        "jar_sha256": provenance.jar_sha256,
        "normalized": provenance.normalized,
        "frequency_analysis": provenance.frequency_analysis,
    }


def run_baseline_comparison(
    output_root: str | Path,
    *,
    java_executable: str | Path,
    jplag_jar: str | Path,
) -> Path:
    """Run both systems over the same deterministic controlled corpus."""
    output_root = Path(output_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        assignment_root = temporary_root / "assignment"
        jplag_output = temporary_root / "jplag"

        write_synthetic_assignment(
            assignment_root,
            controlled_submissions(),
        )

        assignment = load_assignment(
            assignment_root
        )

        pairs = controlled_pairs()

        behavclone_result = run_structural_benchmark(
            assignment,
            pairs,
            assignment_metric="normalized",
        )

        jplag_run = run_jplag(
            assignment_root / "submissions",
            jplag_output,
            java_executable=java_executable,
            jar_path=jplag_jar,
            version=JPLAG_VERSION,
            expected_jar_sha256=JPLAG_SHA256,
        )

        rows = []

        for pair_metrics in behavclone_result.pairs:
            jplag_pair = jplag_run.results.find_pair(
                pair_metrics.left_submission_id,
                pair_metrics.right_submission_id,
            )

            rows.append(
                BaselineComparisonRow(
                    left_submission_id=(
                        pair_metrics.left_submission_id
                    ),
                    right_submission_id=(
                        pair_metrics.right_submission_id
                    ),
                    related=pair_metrics.related,
                    transformation=(
                        pair_metrics.transformation.value
                        if pair_metrics.transformation is not None
                        else "control"
                    ),
                    behavclone_raw_similarity=(
                        pair_metrics.mean_raw_similarity
                    ),
                    behavclone_normalized_similarity=(
                        pair_metrics.mean_normalized_similarity
                    ),
                    behavclone_structural_similarity=(
                        pair_metrics.mean_structural_similarity
                    ),
                    jplag_average_similarity=(
                        jplag_pair.average_similarity
                    ),
                    jplag_max_similarity=(
                        jplag_pair.max_similarity
                    ),
                )
            )

        rows_tuple = tuple(rows)

        payload = {
            "experiment": "controlled-behavclone-jplag-comparison",
            "interpretation": (
                "Side-by-side measurements on a small synthetic "
                "controlled corpus. These results do not establish "
                "general superiority or plagiarism-detection accuracy."
            ),
            "behavclone_assignment_metric": "normalized",
            "jplag": _portable_provenance(
                jplag_run.provenance
            ),
            "pair_count": len(rows_tuple),
            "pairs": [
                asdict(row)
                for row in rows_tuple
            ],
        }

    json_path = output_root / "comparison.json"

    _write_json(
        json_path,
        payload,
    )

    _write_csv(
        output_root / "comparison.csv",
        rows_tuple,
    )

    return json_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare BehavClone with pinned JPlag "
            "on the controlled corpus."
        )
    )
    parser.add_argument(
        "--java",
        default=os.environ.get(
            "BEHAVCLONE_JAVA25"
        ),
        help=(
            "Path to a Java 25 executable. "
            "Can also use BEHAVCLONE_JAVA25."
        ),
    )
    parser.add_argument(
        "--jplag-jar",
        default=os.environ.get(
            "BEHAVCLONE_JPLAG_JAR"
        ),
        help=(
            "Path to the pinned JPlag 6.3.0 JAR. "
            "Can also use BEHAVCLONE_JPLAG_JAR."
        ),
    )
    parser.add_argument(
        "--output",
        default="results/baselines/jplag",
    )

    args = parser.parse_args()

    if not args.java:
        parser.error(
            "--java or BEHAVCLONE_JAVA25 is required"
        )

    if not args.jplag_jar:
        parser.error(
            "--jplag-jar or BEHAVCLONE_JPLAG_JAR is required"
        )

    output = run_baseline_comparison(
        args.output,
        java_executable=args.java,
        jplag_jar=args.jplag_jar,
    )

    print(
        "Wrote BehavClone/JPlag comparison to "
        f"{output}"
    )


if __name__ == "__main__":
    main()
