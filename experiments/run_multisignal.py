"""Reproducible multi-signal evidence experiment."""

import argparse
import json
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path

from behavclone.evidence.assignment import compare_assignment_pair_evidence
from behavclone.ingestion.assignment import load_assignment
from experiments.controlled import controlled_pairs
from experiments.multisignal_reporting import (
    build_multisignal_row,
    write_multisignal_csv,
)
from experiments.synthetic import (
    controlled_behavioral_results,
    controlled_submissions,
    write_synthetic_assignment,
)


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


def run_multisignal_experiment(
    output_root: str | Path,
    *,
    ngram_size: int = 4,
) -> Path:
    """Generate deterministic evidence profiles for controlled pairs."""
    output_root = Path(output_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory() as temporary:
        assignment_root = Path(temporary) / "assignment"

        write_synthetic_assignment(
            assignment_root,
            controlled_submissions(),
            behavioral_results=controlled_behavioral_results(),
        )

        assignment = load_assignment(assignment_root)

        rows = []
        csv_rows = []

        for pair in controlled_pairs():
            evidence = compare_assignment_pair_evidence(
                assignment,
                pair.left_submission_id,
                pair.right_submission_id,
                ngram_size=ngram_size,
            )

            transformation = (
                pair.transformation.value
                if pair.transformation is not None
                else "control"
            )

            rows.append(
                {
                    "left_submission_id": pair.left_submission_id,
                    "right_submission_id": pair.right_submission_id,
                    "related": pair.related,
                    "transformation": transformation,
                    "evidence": asdict(evidence),
                }
            )

            csv_rows.append(
                build_multisignal_row(
                    evidence,
                    related=pair.related,
                    transformation=transformation,
                )
            )

    payload = {
        "experiment": "controlled-multisignal-evidence",
        "interpretation": (
            "Evidence channels are reported separately. "
            "No combined plagiarism score or automated verdict is produced."
        ),
        "ngram_size": ngram_size,
        "pair_count": len(rows),
        "pairs": rows,
    }

    output_path = output_root / "evidence.json"

    _write_json(
        output_path,
        payload,
    )

    write_multisignal_csv(
        output_root / "evidence.csv",
        tuple(csv_rows),
    )

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the controlled BehavClone multi-signal "
            "evidence experiment."
        )
    )
    parser.add_argument(
        "--output",
        default="results/multisignal",
        help="Output directory for deterministic artifacts.",
    )
    parser.add_argument(
        "--ngram-size",
        type=int,
        default=4,
        help="Normalized token n-gram size for cohort evidence.",
    )

    args = parser.parse_args()

    output_path = run_multisignal_experiment(
        args.output,
        ngram_size=args.ngram_size,
    )

    print(
        "Wrote controlled multi-signal artifact to "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()
