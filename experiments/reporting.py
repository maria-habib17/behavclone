import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from experiments.models import BenchmarkResult


@dataclass(frozen=True)
class AblationRow:
    """Representation-specific measurements for one benchmark pair."""

    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: str
    raw_similarity: float
    normalized_similarity: float
    structural_similarity: float


def build_ablation_rows(
    result: BenchmarkResult,
) -> tuple[AblationRow, ...]:
    """Convert benchmark measurements into representation-ablation rows."""
    return tuple(
        AblationRow(
            left_submission_id=pair.left_submission_id,
            right_submission_id=pair.right_submission_id,
            related=pair.related,
            transformation=(
                pair.transformation.value
                if pair.transformation
                else "control"
            ),
            raw_similarity=pair.mean_raw_similarity,
            normalized_similarity=(
                pair.mean_normalized_similarity
            ),
            structural_similarity=(
                pair.mean_structural_similarity
            ),
        )
        for pair in result.pairs
    )


def write_ablation_csv(
    rows: tuple[AblationRow, ...],
    path: Path,
) -> None:
    """Write deterministic CSV experiment output."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "left_submission_id",
        "right_submission_id",
        "related",
        "transformation",
        "raw_similarity",
        "normalized_similarity",
        "structural_similarity",
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
            writer.writerow(asdict(row))


def write_ablation_json(
    rows: tuple[AblationRow, ...],
    path: Path,
) -> None:
    """Write deterministic JSON experiment output."""
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        asdict(row)
        for row in rows
    ]

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
