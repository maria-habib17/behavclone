import csv
import json
from pathlib import Path

from experiments.models import (
    BenchmarkResult,
    PairMetrics,
    TransformationKind,
)
from experiments.reporting import (
    build_ablation_rows,
    write_ablation_csv,
    write_ablation_json,
)


def result_fixture() -> BenchmarkResult:
    return BenchmarkResult(
        pairs=(
            PairMetrics(
                left_submission_id="BASE",
                right_submission_id="RENAMED",
                related=True,
                transformation=(
                    TransformationKind.IDENTIFIER_RENAME
                ),
                matched_count=2,
                left_coverage=1.0,
                right_coverage=1.0,
                mean_raw_similarity=0.7,
                mean_normalized_similarity=1.0,
                mean_structural_similarity=1.0,
            ),
            PairMetrics(
                left_submission_id="BASE",
                right_submission_id="CONTROL",
                related=False,
                transformation=None,
                matched_count=2,
                left_coverage=1.0,
                right_coverage=1.0,
                mean_raw_similarity=0.3,
                mean_normalized_similarity=0.5,
                mean_structural_similarity=0.6,
            ),
        )
    )


def test_ablation_rows_preserve_representations():
    rows = build_ablation_rows(
        result_fixture()
    )

    assert len(rows) == 2
    assert rows[0].transformation == "identifier_rename"
    assert rows[0].raw_similarity == 0.7
    assert rows[0].normalized_similarity == 1.0
    assert rows[0].structural_similarity == 1.0
    assert rows[1].transformation == "control"


def test_csv_export_is_readable(
    tmp_path: Path,
):
    rows = build_ablation_rows(
        result_fixture()
    )
    path = tmp_path / "results.csv"

    write_ablation_csv(rows, path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        exported = list(
            csv.DictReader(handle)
        )

    assert len(exported) == 2
    assert exported[0]["right_submission_id"] == "RENAMED"
    assert exported[0]["raw_similarity"] == "0.7"
    assert exported[0]["normalized_similarity"] == "1.0"


def test_json_export_is_readable(
    tmp_path: Path,
):
    rows = build_ablation_rows(
        result_fixture()
    )
    path = tmp_path / "results.json"

    write_ablation_json(rows, path)

    exported = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert len(exported) == 2
    assert exported[0]["transformation"] == (
        "identifier_rename"
    )
    assert exported[1]["related"] is False


def test_json_export_is_deterministic(
    tmp_path: Path,
):
    rows = build_ablation_rows(
        result_fixture()
    )

    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    write_ablation_json(rows, first)
    write_ablation_json(rows, second)

    assert first.read_bytes() == second.read_bytes()
