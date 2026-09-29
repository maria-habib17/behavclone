from behavclone.evidence.assignment import (
    compare_assignment_pair_evidence,
)
from behavclone.ingestion.assignment import load_assignment
from experiments.synthetic import (
    controlled_behavioral_results,
    controlled_submissions,
    write_synthetic_assignment,
)


def controlled_assignment(tmp_path):
    write_synthetic_assignment(
        tmp_path,
        controlled_submissions(),
        behavioral_results=controlled_behavioral_results(),
    )
    return load_assignment(tmp_path)


def test_controlled_assignment_imports_behavioral_results(
    tmp_path,
):
    assignment = controlled_assignment(tmp_path)

    assert assignment.config.test_results == "test-results.csv"
    assert (
        assignment.root / "test-results.csv"
    ).is_file()


def test_related_identifier_rename_has_three_evidence_channels(
    tmp_path,
):
    assignment = controlled_assignment(tmp_path)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "ID_RENAME",
        ngram_size=4,
    )

    assert (
        evidence.structural.mean_normalized_similarity
        == 1.0
    )
    assert evidence.cohort.shared_feature_count > 0

    assert evidence.behavioral is not None
    assert evidence.behavioral.shared_failure_count == 1
    assert evidence.behavioral.identical_wrong_output_count == 1


def test_lookalike_structural_false_positive_has_no_behavioral_evidence(
    tmp_path,
):
    assignment = controlled_assignment(tmp_path)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "LOOKALIKE",
        ngram_size=4,
    )

    assert (
        evidence.structural.mean_normalized_similarity
        == 1.0
    )
    assert (
        evidence.structural.mean_structural_similarity
        == 1.0
    )

    assert evidence.behavioral is not None
    assert evidence.behavioral.shared_failure_count == 0
    assert evidence.behavioral.identical_wrong_output_count == 0


def test_structurally_identical_pairs_can_have_different_behavioral_evidence(
    tmp_path,
):
    assignment = controlled_assignment(tmp_path)

    related = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "ID_RENAME",
        ngram_size=4,
    )

    lookalike = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "LOOKALIKE",
        ngram_size=4,
    )

    assert (
        related.structural.mean_normalized_similarity
        == lookalike.structural.mean_normalized_similarity
        == 1.0
    )

    assert related.behavioral is not None
    assert lookalike.behavioral is not None

    assert related.behavioral.identical_wrong_output_count == 1
    assert lookalike.behavioral.identical_wrong_output_count == 0


def test_behavioral_frequency_is_reported_not_interpreted_as_verdict(
    tmp_path,
):
    assignment = controlled_assignment(tmp_path)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "BASE",
        "ID_RENAME",
    )

    assert evidence.behavioral is not None
    assert evidence.behavioral.cohort_size == 10
    assert evidence.behavioral.shared_failure_count == 1
    assert evidence.behavioral.max_failure_rarity > 1.0
    assert evidence.behavioral.max_wrong_output_rarity > 1.0
