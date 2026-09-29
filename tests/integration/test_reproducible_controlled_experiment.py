import json
from pathlib import Path

from experiments.run_controlled import run_controlled_experiment


def _artifact_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_controlled_experiment_writes_expected_artifacts(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "results"

    run_controlled_experiment(output_root)

    expected_common = {
        "pairs.csv",
        "pairs.json",
        "ranking.json",
        "metadata.json",
    }

    assert (output_root / "summary.json").is_file()

    for metric in ("raw", "normalized", "structural"):
        metric_root = output_root / metric

        assert metric_root.is_dir()
        assert {
            path.name
            for path in metric_root.iterdir()
            if path.is_file()
        } == expected_common


def test_controlled_experiment_is_byte_reproducible(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    run_controlled_experiment(first)
    run_controlled_experiment(second)

    assert _artifact_bytes(first) == _artifact_bytes(second)


def test_summary_preserves_assignment_metric_provenance(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "results"

    run_controlled_experiment(output_root)

    summary = json.loads(
        (output_root / "summary.json").read_text(encoding="utf-8")
    )

    assert summary["assignment_metrics"] == [
        "raw",
        "normalized",
        "structural",
    ]

    assert summary["submission_count"] == 10
    assert summary["pair_count"] == 9

    for metric in ("raw", "normalized", "structural"):
        assert summary["runs"][metric]["assignment_metric"] == metric


def test_controlled_experiment_exposes_lookalike_false_positive_pressure(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "results"

    run_controlled_experiment(output_root)

    ranking = json.loads(
        (
            output_root
            / "normalized"
            / "ranking.json"
        ).read_text(encoding="utf-8")
    )

    normalized_pairs = ranking["normalized"]["ranked_pairs"]

    lookalike = next(
        pair
        for pair in normalized_pairs
        if pair["right_submission_id"] == "LOOKALIKE"
    )

    assert lookalike["related"] is False
    assert lookalike["score"] == 1.0
    assert lookalike["rank"] == 5


def test_assignment_metrics_currently_produce_same_pair_measurements(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "results"

    run_controlled_experiment(output_root)

    measurements = []

    for metric in ("raw", "normalized", "structural"):
        measurements.append(
            (
                output_root
                / metric
                / "pairs.json"
            ).read_bytes()
        )

    assert measurements[0] == measurements[1] == measurements[2]
