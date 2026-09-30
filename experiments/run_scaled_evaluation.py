"""Reproducible scaled-cohort evaluation."""

import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

from behavclone.ingestion.assignment import load_assignment
from experiments.cohort_pairs import all_cohort_pairs
from experiments.evaluation import SimilarityMetric, rank_benchmark
from experiments.provenance_pairs import provenance_family_pairs
from experiments.retrieval import evaluate_retrieval
from experiments.runner import run_structural_benchmark
from experiments.scaled_synthetic import (
    SCALED_FAMILIES,
    scaled_cohort,
)
from experiments.synthetic import write_synthetic_assignment

METRICS: tuple[SimilarityMetric, ...] = (
    "raw",
    "normalized",
    "structural",
)

K_VALUES = (5, 10, 20)


def _pair_key(
    left_id: str,
    right_id: str,
) -> tuple[str, str]:
    return tuple(sorted((left_id, right_id)))


def _metric_payload(
    result,
    metric: SimilarityMetric,
) -> dict[str, object]:
    evaluation = evaluate_retrieval(
        result,
        metric,
        k_values=K_VALUES,
    )

    return {
        "average_precision": evaluation.average_precision,
        "first_control_rank": evaluation.first_unrelated_rank,
        "precision_at_k": {
            str(k): evaluation.precision_at_k[k]
            for k in K_VALUES
        },
        "recall_at_k": {
            str(k): evaluation.recall_at_k[k]
            for k in K_VALUES
        },
    }


def _label_payload(
    result,
) -> dict[str, object]:
    return {
        "pair_count": len(result.pairs),
        "related_count": len(result.related_pairs),
        "control_count": len(result.unrelated_pairs),
        "metrics": {
            metric: _metric_payload(
                result,
                metric,
            )
            for metric in METRICS
        },
    }


def _score_lookup(
    result,
) -> dict[tuple[str, str], object]:
    return {
        _pair_key(
            item.left_submission_id,
            item.right_submission_id,
        ): item
        for item in result.pairs
    }


def _rank_lookup(
    result,
    metric: SimilarityMetric,
) -> dict[tuple[str, str], int]:
    ranking = rank_benchmark(
        result,
        metric,
    )

    return {
        _pair_key(
            item.pair.left_submission_id,
            item.pair.right_submission_id,
        ): item.rank
        for item in ranking.ranked_pairs
    }


def run_scaled_evaluation(
    output_root: Path,
) -> None:
    """Run both scaled-cohort labeling views and write artifacts."""
    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    cohort = scaled_cohort()

    submission_ids = tuple(
        submission.submission_id
        for submission in cohort.submissions
    )

    seeded_pairs = all_cohort_pairs(
        submission_ids,
        cohort.related_pairs,
    )

    provenance_pairs = provenance_family_pairs(
        SCALED_FAMILIES
    )

    with tempfile.TemporaryDirectory() as directory:
        assignment_root = (
            Path(directory)
            / "assignment"
        )

        write_synthetic_assignment(
            assignment_root,
            cohort.submissions,
        )

        assignment = load_assignment(
            assignment_root
        )

        seeded_result = run_structural_benchmark(
            assignment,
            seeded_pairs,
            assignment_metric="normalized",
        )

        provenance_result = run_structural_benchmark(
            assignment,
            provenance_pairs,
            assignment_metric="normalized",
        )

    summary = {
        "experiment": "scaled-controlled-cohort",
        "submission_count": len(cohort.submissions),
        "family_count": len(SCALED_FAMILIES),
        "assignment_metric": "normalized",
        "k_values": list(K_VALUES),
        "label_views": {
            "seeded_edges": _label_payload(
                seeded_result
            ),
            "provenance_families": _label_payload(
                provenance_result
            ),
        },
        "interpretation": (
            "Controlled synthetic evaluation with two explicit "
            "labeling views. Seeded-edge retrieval treats only "
            "declared base-to-transformation edges as targets. "
            "Provenance-family retrieval treats every within-family "
            "pair as related and cross-family pairs as controls. "
            "Results characterize this synthetic cohort only and do "
            "not establish plagiarism-detection accuracy or general "
            "superiority."
        ),
    }

    summary_path = output_root / "summary.json"

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    seeded_lookup = _score_lookup(
        seeded_result
    )

    provenance_lookup = _score_lookup(
        provenance_result
    )

    rank_lookups = {
        metric: _rank_lookup(
            provenance_result,
            metric,
        )
        for metric in METRICS
    }

    csv_path = output_root / "pairs.csv"

    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "seeded_related",
        "provenance_related",
        "transformation",
        "raw_similarity",
        "normalized_similarity",
        "structural_similarity",
        "raw_rank",
        "normalized_rank",
        "structural_rank",
    ]

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

        for key in sorted(
            provenance_lookup
        ):
            provenance_item = (
                provenance_lookup[key]
            )
            seeded_item = seeded_lookup[key]

            transformation = (
                seeded_item.transformation.value
                if (
                    seeded_item.transformation
                    is not None
                )
                else ""
            )

            writer.writerow(
                {
                    "left_submission_id": key[0],
                    "right_submission_id": key[1],
                    "seeded_related": (
                        seeded_item.related
                    ),
                    "provenance_related": (
                        provenance_item.related
                    ),
                    "transformation": transformation,
                    "raw_similarity": (
                        provenance_item.mean_raw_similarity
                    ),
                    "normalized_similarity": (
                        provenance_item.mean_normalized_similarity
                    ),
                    "structural_similarity": (
                        provenance_item.mean_structural_similarity
                    ),
                    "raw_rank": (
                        rank_lookups["raw"][key]
                    ),
                    "normalized_rank": (
                        rank_lookups["normalized"][key]
                    ),
                    "structural_rank": (
                        rank_lookups["structural"][key]
                    ),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the reproducible scaled "
            "BehavClone evaluation."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/scaled"),
    )

    args = parser.parse_args()

    run_scaled_evaluation(
        args.output
    )


if __name__ == "__main__":
    main()
