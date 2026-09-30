"""Scaled multi-signal evidence experiment.

This experiment applies the predeclared multi-signal protocol and
behavioral fixture to the frozen scaled synthetic cohort. Evidence
channels remain separate; no combined plagiarism score is produced.
"""

import argparse
import csv
import json
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path

from behavclone.evidence.assignment import compare_assignment_pair_evidence
from behavclone.ingestion.assignment import load_assignment
from experiments.provenance_pairs import provenance_family_pairs
from experiments.scaled_behavior import scaled_behavioral_results
from experiments.scaled_multisignal_protocol import (
    SCALED_MULTISIGNAL_PROTOCOL,
)
from experiments.scaled_synthetic import (
    SCALED_FAMILIES,
    scaled_cohort,
)
from experiments.synthetic import write_synthetic_assignment


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
    rows: list[dict[str, object]],
) -> None:
    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "related",
        "transformation",
        "mean_raw_similarity",
        "mean_normalized_similarity",
        "mean_structural_similarity",
        "cohort_shared_feature_count",
        "cohort_pair_specific_feature_count",
        "cohort_max_rarity",
        "cohort_mean_rarity",
        "behavior_shared_failure_count",
        "behavior_identical_wrong_output_count",
        "behavior_max_failure_rarity",
        "behavior_max_wrong_output_rarity",
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
        writer.writerows(rows)


def _pair_row(
    pair,
    evidence,
) -> dict[str, object]:
    behavioral = evidence.behavioral

    if behavioral is None:
        raise ValueError(
            "Scaled multi-signal experiment requires behavioral evidence."
        )

    transformation = (
        pair.transformation.value
        if pair.transformation is not None
        else ""
    )

    return {
        "left_submission_id": pair.left_submission_id,
        "right_submission_id": pair.right_submission_id,
        "related": pair.related,
        "transformation": transformation,
        "mean_raw_similarity": (
            evidence.structural.mean_raw_similarity
        ),
        "mean_normalized_similarity": (
            evidence.structural.mean_normalized_similarity
        ),
        "mean_structural_similarity": (
            evidence.structural.mean_structural_similarity
        ),
        "cohort_shared_feature_count": (
            evidence.cohort.shared_feature_count
        ),
        "cohort_pair_specific_feature_count": (
            evidence.cohort.pair_specific_feature_count
        ),
        "cohort_max_rarity": (
            evidence.cohort.max_rarity
        ),
        "cohort_mean_rarity": (
            evidence.cohort.mean_rarity
        ),
        "behavior_shared_failure_count": (
            behavioral.shared_failure_count
        ),
        "behavior_identical_wrong_output_count": (
            behavioral.identical_wrong_output_count
        ),
        "behavior_max_failure_rarity": (
            behavioral.max_failure_rarity
        ),
        "behavior_max_wrong_output_rarity": (
            behavioral.max_wrong_output_rarity
        ),
    }


def _channel_summary(
    rows: list[dict[str, object]],
    *,
    related: bool,
) -> dict[str, object]:
    selected = [
        row
        for row in rows
        if row["related"] is related
    ]

    behavioral_positive = [
        row
        for row in selected
        if int(
            row[
                "behavior_shared_failure_count"
            ]
        )
        > 0
    ]

    identical_positive = [
        row
        for row in selected
        if int(
            row[
                "behavior_identical_wrong_output_count"
            ]
        )
        > 0
    ]

    collisions = [
        row
        for row in selected
        if (
            float(
                row[
                    "mean_normalized_similarity"
                ]
            )
            == SCALED_MULTISIGNAL_PROTOCOL.structural_collision_value
        )
    ]

    collision_behavioral_positive = [
        row
        for row in collisions
        if int(
            row[
                "behavior_shared_failure_count"
            ]
        )
        > 0
    ]

    collision_identical_positive = [
        row
        for row in collisions
        if int(
            row[
                "behavior_identical_wrong_output_count"
            ]
        )
        > 0
    ]

    return {
        "pair_count": len(selected),
        "behavior_shared_failure_pairs": len(
            behavioral_positive
        ),
        "behavior_identical_wrong_output_pairs": len(
            identical_positive
        ),
        "normalized_collision_pairs": len(
            collisions
        ),
        "normalized_collision_pairs_with_shared_failure": len(
            collision_behavioral_positive
        ),
        "normalized_collision_pairs_with_identical_wrong_output": len(
            collision_identical_positive
        ),
    }


def run_scaled_multisignal(
    output_root: str | Path,
) -> Path:
    """Generate deterministic scaled multi-signal evidence artifacts."""
    output_root = Path(output_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    cohort = scaled_cohort()

    pairs = provenance_family_pairs(
        SCALED_FAMILIES
    )

    with tempfile.TemporaryDirectory() as temporary:
        assignment_root = (
            Path(temporary)
            / "assignment"
        )

        write_synthetic_assignment(
            assignment_root,
            cohort.submissions,
            behavioral_results=(
                scaled_behavioral_results()
            ),
        )

        assignment = load_assignment(
            assignment_root
        )

        evidence_rows = []
        csv_rows = []

        for pair in pairs:
            evidence = compare_assignment_pair_evidence(
                assignment,
                pair.left_submission_id,
                pair.right_submission_id,
                ngram_size=(
                    SCALED_MULTISIGNAL_PROTOCOL.ngram_size
                ),
                matching_metric="normalized",
            )

            evidence_rows.append(
                {
                    "left_submission_id": (
                        pair.left_submission_id
                    ),
                    "right_submission_id": (
                        pair.right_submission_id
                    ),
                    "related": pair.related,
                    "transformation": (
                        pair.transformation.value
                        if pair.transformation is not None
                        else None
                    ),
                    "evidence": asdict(
                        evidence
                    ),
                }
            )

            csv_rows.append(
                _pair_row(
                    pair,
                    evidence,
                )
            )

    summary = {
        "experiment": (
            "scaled-controlled-multisignal-evidence"
        ),
        "submission_count": len(
            cohort.submissions
        ),
        "family_count": len(
            SCALED_FAMILIES
        ),
        "pair_count": len(
            pairs
        ),
        "related_pair_count": sum(
            pair.related
            for pair in pairs
        ),
        "control_pair_count": sum(
            not pair.related
            for pair in pairs
        ),
        "protocol": asdict(
            SCALED_MULTISIGNAL_PROTOCOL
        ),
        "related_summary": _channel_summary(
            csv_rows,
            related=True,
        ),
        "control_summary": _channel_summary(
            csv_rows,
            related=False,
        ),
        "interpretation": (
            "Controlled synthetic evidence-channel analysis. "
            "Structural, cohort-relative, and behavioral evidence "
            "are reported separately. Behavioral observations were "
            "predeclared before pairwise measurement and do not force "
            "every provenance-related pair to share a failure. "
            "Results characterize this synthetic cohort only and do "
            "not establish plagiarism-detection accuracy, causal "
            "provenance, or general superiority."
        ),
    }

    _write_json(
        output_root / "summary.json",
        summary,
    )

    _write_json(
        output_root / "evidence.json",
        {
            "experiment": summary[
                "experiment"
            ],
            "pairs": evidence_rows,
        },
    )

    _write_csv(
        output_root / "evidence.csv",
        csv_rows,
    )

    return output_root


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the frozen scaled multi-signal evidence experiment."
        )
    )
    parser.add_argument(
        "--output",
        default="results/scaled-multisignal",
        help="Output directory for deterministic artifacts.",
    )

    args = parser.parse_args()

    output_root = run_scaled_multisignal(
        args.output
    )

    print(
        "Wrote scaled multi-signal artifacts to "
        f"{output_root}"
    )


if __name__ == "__main__":
    main()
