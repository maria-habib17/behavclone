"""Tests freezing the authentic-evaluation protocol."""

from experiments.authentic_protocol import (
    AUTHENTIC_EVALUATION_PROTOCOL,
)


def test_authentic_protocol_uses_complete_submissions():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    assert (
        protocol.unit_of_analysis
        == "complete_submission"
    )

    assert protocol.language == "java"


def test_authentic_protocol_has_minimum_cohort_size():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    assert protocol.minimum_submissions == 10


def test_authentic_protocol_freezes_behavclone_configuration():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    assert (
        protocol.behavclone_matching_metric
        == "normalized"
    )

    assert protocol.cohort_ngram_size == 4

    assert protocol.structural_metrics == (
        "mean_raw_similarity",
        "mean_normalized_similarity",
        "mean_structural_similarity",
    )


def test_authentic_protocol_keeps_evidence_channels_separate():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    assert protocol.cohort_fields == (
        "shared_feature_count",
        "pair_specific_feature_count",
        "max_rarity",
        "mean_rarity",
    )

    assert protocol.behavioral_fields == (
        "shared_failure_count",
        "identical_wrong_output_count",
        "max_failure_rarity",
        "max_wrong_output_rarity",
    )


def test_authentic_protocol_freezes_standard_jplag_baseline():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    assert protocol.jplag_similarity_fields == (
        "averageSimilarity",
        "maxSimilarity",
    )

    assert protocol.jplag_normalized is False
    assert (
        protocol.jplag_frequency_analysis
        is False
    )


def test_authentic_protocol_requires_anonymization_and_provenance():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    requirements = " ".join(
        protocol.inclusion_requirements
    ).lower()

    assert "anonymized" in requirements
    assert "provenance" in requirements
    assert "ethically" in requirements
    assert "starter code" in requirements


def test_authentic_protocol_excludes_unclear_or_artificial_data():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    exclusions = " ".join(
        protocol.exclusion_requirements
    ).lower()

    assert "personally identifying" in exclusions
    assert "permission" in exclusions
    assert "generated duplicates" in exclusions
    assert "known copied pairs" in exclusions


def test_authentic_protocol_preserves_negative_results():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    reporting = " ".join(
        protocol.reporting_requirements
    ).lower()

    assert "unfavorable" in reporting
    assert "null findings" in reporting
    assert "missing evidence" in reporting


def test_authentic_protocol_prohibits_overclaiming():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    claims = {
        claim.lower()
        for claim in protocol.prohibited_claims
    }

    assert "plagiarism verdict" in claims
    assert "authorship inference" in claims
    assert "intent inference" in claims

    assert (
        "plagiarism detection accuracy from an unlabeled cohort"
        in claims
    )

    assert (
        "general superiority over jplag"
        in claims
    )

    assert (
        "universal similarity threshold"
        in claims
    )


def test_protocol_has_no_combined_score_or_verdict_field():
    protocol = AUTHENTIC_EVALUATION_PROTOCOL

    fields = set(
        protocol.__dataclass_fields__
    )

    assert "combined_score" not in fields
    assert "verdict" not in fields
    assert "threshold" not in fields
