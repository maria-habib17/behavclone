import json

from experiments.run_multisignal import (
    run_multisignal_experiment,
)


def load_artifact(path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def pair_by_right(payload, right_submission_id):
    return next(
        pair
        for pair in payload["pairs"]
        if pair["right_submission_id"]
        == right_submission_id
    )


def test_multisignal_artifact_is_byte_reproducible(
    tmp_path,
):
    first = run_multisignal_experiment(
        tmp_path / "first"
    )
    second = run_multisignal_experiment(
        tmp_path / "second"
    )

    assert first.read_bytes() == second.read_bytes()


def test_multisignal_artifact_contains_all_controlled_pairs(
    tmp_path,
):
    path = run_multisignal_experiment(
        tmp_path / "results"
    )

    payload = load_artifact(path)

    assert payload["pair_count"] == 9
    assert len(payload["pairs"]) == 9
    assert payload["ngram_size"] == 4


def test_artifact_explicitly_avoids_combined_verdict(
    tmp_path,
):
    path = run_multisignal_experiment(
        tmp_path / "results"
    )

    payload = load_artifact(path)

    assert "No combined plagiarism score" in (
        payload["interpretation"]
    )

    serialized = json.dumps(payload)

    assert '"plagiarism_score"' not in serialized
    assert '"verdict"' not in serialized


def test_identifier_rename_and_lookalike_share_structural_pressure(
    tmp_path,
):
    path = run_multisignal_experiment(
        tmp_path / "results"
    )

    payload = load_artifact(path)

    renamed = pair_by_right(
        payload,
        "ID_RENAME",
    )
    lookalike = pair_by_right(
        payload,
        "LOOKALIKE",
    )

    renamed_structural = renamed["evidence"]["structural"]
    lookalike_structural = lookalike["evidence"]["structural"]

    assert (
        renamed_structural["mean_normalized_similarity"]
        == 1.0
    )
    assert (
        lookalike_structural["mean_normalized_similarity"]
        == 1.0
    )

    assert (
        renamed_structural["mean_structural_similarity"]
        == 1.0
    )
    assert (
        lookalike_structural["mean_structural_similarity"]
        == 1.0
    )


def test_behavior_channel_distinguishes_structurally_identical_case(
    tmp_path,
):
    path = run_multisignal_experiment(
        tmp_path / "results"
    )

    payload = load_artifact(path)

    renamed = pair_by_right(
        payload,
        "ID_RENAME",
    )
    lookalike = pair_by_right(
        payload,
        "LOOKALIKE",
    )

    renamed_behavior = renamed["evidence"]["behavioral"]
    lookalike_behavior = lookalike["evidence"]["behavioral"]

    assert renamed_behavior["shared_failure_count"] == 1
    assert (
        renamed_behavior["identical_wrong_output_count"]
        == 1
    )

    assert lookalike_behavior["shared_failure_count"] == 0
    assert (
        lookalike_behavior["identical_wrong_output_count"]
        == 0
    )


def test_artifact_preserves_cohort_evidence_as_separate_channel(
    tmp_path,
):
    path = run_multisignal_experiment(
        tmp_path / "results"
    )

    payload = load_artifact(path)

    renamed = pair_by_right(
        payload,
        "ID_RENAME",
    )

    cohort = renamed["evidence"]["cohort"]

    assert cohort["cohort_size"] == 10
    assert cohort["ngram_size"] == 4
    assert cohort["shared_feature_count"] > 0
    assert cohort["max_rarity"] >= 1.0
