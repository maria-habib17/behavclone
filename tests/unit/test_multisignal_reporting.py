import csv

from behavclone.evidence.assignment import (
    compare_assignment_pair_evidence,
)
from behavclone.ingestion.assignment import load_assignment
from experiments.multisignal_reporting import (
    build_multisignal_row,
)
from experiments.run_multisignal import (
    run_multisignal_experiment,
)
from experiments.synthetic import (
    controlled_behavioral_results,
    controlled_submissions,
    write_synthetic_assignment,
)


def test_multisignal_csv_is_generated(
    tmp_path,
):
    output = tmp_path / "results"

    run_multisignal_experiment(output)

    assert (output / "evidence.json").is_file()
    assert (output / "evidence.csv").is_file()


def test_multisignal_csv_contains_all_pairs(
    tmp_path,
):
    output = tmp_path / "results"

    run_multisignal_experiment(output)

    with (output / "evidence.csv").open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 9


def test_flat_row_keeps_channels_separate(
    tmp_path,
):
    assignment_root = tmp_path / "assignment"

    write_synthetic_assignment(
        assignment_root,
        controlled_submissions(),
        behavioral_results=controlled_behavioral_results(),
    )

    assignment = load_assignment(
        assignment_root
    )

    evidence = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "ID_RENAME",
    )

    row = build_multisignal_row(
        evidence,
        related=True,
        transformation="identifier_rename",
    )

    assert row.normalized_similarity == 1.0
    assert row.structural_similarity == 1.0

    assert row.shared_cohort_feature_count == 30
    assert row.pair_specific_cohort_feature_count == 0

    assert row.shared_failure_count == 1
    assert row.identical_wrong_output_count == 1


def test_csv_exposes_lookalike_disagreement(
    tmp_path,
):
    output = tmp_path / "results"

    run_multisignal_experiment(output)

    with (output / "evidence.csv").open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    lookalike = next(
        row
        for row in rows
        if row["right_submission_id"] == "LOOKALIKE"
    )

    assert float(
        lookalike["normalized_similarity"]
    ) == 1.0

    assert float(
        lookalike["structural_similarity"]
    ) == 1.0

    assert int(
        lookalike["shared_failure_count"]
    ) == 0

    assert int(
        lookalike["identical_wrong_output_count"]
    ) == 0
