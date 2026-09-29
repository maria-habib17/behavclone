"""Reproducible entry point for the controlled BehavClone benchmark."""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from behavclone.ingestion.assignment import load_assignment
from behavclone.matching.models import MatchingMetric
from experiments.controlled import controlled_pairs
from experiments.evaluation import SimilarityMetric, rank_benchmark
from experiments.reporting import build_ablation_rows, write_ablation_csv, write_ablation_json
from experiments.runner import run_structural_benchmark
from experiments.synthetic import controlled_submissions, write_synthetic_assignment

ASSIGNMENT_METRICS: tuple[MatchingMetric, ...] = (
    "raw",
    "normalized",
    "structural",
)

SIMILARITY_METRICS: tuple[SimilarityMetric, ...] = (
    "raw",
    "normalized",
    "structural",
)


def _write_json(path: Path, payload: object) -> None:
    """Write deterministic UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _ranking_payload(evaluation) -> dict:
    """Serialize one ranking evaluation without hiding false positives."""
    return {
        "metric": evaluation.metric,
        "mean_related_rank": evaluation.mean_related_rank,
        "best_unrelated_rank": evaluation.best_unrelated_rank,
        "ranked_pairs": [
            {
                "rank": item.rank,
                "score": item.score,
                "left_submission_id": item.pair.left_submission_id,
                "right_submission_id": item.pair.right_submission_id,
                "related": item.pair.related,
                "transformation": (
                    item.pair.transformation.value
                    if item.pair.transformation
                    else "control"
                ),
            }
            for item in evaluation.ranked_pairs
        ],
    }


def _result_digest(path: Path) -> str:
    """Return a stable SHA-256 digest for one generated artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_controlled_experiment(output_root: Path) -> None:
    """Run every assignment-metric variant and write deterministic artifacts."""
    output_root = output_root.resolve()

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="behavclone-controlled-") as temp_dir:
        assignment_root = Path(temp_dir) / "assignment"

        write_synthetic_assignment(
            assignment_root,
            controlled_submissions(),
        )

        assignment = load_assignment(assignment_root)
        pairs = controlled_pairs()

        summary: dict[str, object] = {
            "experiment": "controlled-transformations",
            "assignment_metrics": list(ASSIGNMENT_METRICS),
            "similarity_metrics": list(SIMILARITY_METRICS),
            "submission_count": len(assignment.submissions),
            "pair_count": len(pairs),
            "runs": {},
        }

        for assignment_metric in ASSIGNMENT_METRICS:
            result = run_structural_benchmark(
                assignment,
                pairs,
                assignment_metric=assignment_metric,
            )

            run_root = output_root / assignment_metric
            rows = build_ablation_rows(result)

            pairs_csv = run_root / "pairs.csv"
            pairs_json = run_root / "pairs.json"

            write_ablation_csv(rows, pairs_csv)
            write_ablation_json(rows, pairs_json)

            rankings: dict[str, object] = {}

            for similarity_metric in SIMILARITY_METRICS:
                evaluation = rank_benchmark(
                    result,
                    similarity_metric,
                )
                rankings[similarity_metric] = _ranking_payload(evaluation)

            _write_json(
                run_root / "ranking.json",
                rankings,
            )

            metadata = {
                "experiment": "controlled-transformations",
                "assignment_metric": result.assignment_metric,
                "submission_count": len(assignment.submissions),
                "pair_count": len(result.pairs),
                "related_pair_count": len(result.related_pairs),
                "unrelated_pair_count": len(result.unrelated_pairs),
                "artifacts": {
                    "pairs.csv": _result_digest(pairs_csv),
                    "pairs.json": _result_digest(pairs_json),
                },
            }

            _write_json(
                run_root / "metadata.json",
                metadata,
            )

            summary["runs"][assignment_metric] = {
                "assignment_metric": assignment_metric,
                "related_pair_count": len(result.related_pairs),
                "unrelated_pair_count": len(result.unrelated_pairs),
                "rankings": {
                    metric: {
                        "mean_related_rank": rankings[metric][
                            "mean_related_rank"
                        ],
                        "best_unrelated_rank": rankings[metric][
                            "best_unrelated_rank"
                        ],
                    }
                    for metric in SIMILARITY_METRICS
                },
            }

        _write_json(
            output_root / "summary.json",
            summary,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the reproducible BehavClone controlled benchmark."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results") / "controlled",
        help="Directory for generated benchmark artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    run_controlled_experiment(args.output)
    print(f"Wrote controlled benchmark artifacts to {args.output}")


if __name__ == "__main__":
    main()
