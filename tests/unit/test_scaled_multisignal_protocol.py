"""Tests for the frozen scaled multi-signal evaluation protocol."""

from experiments.scaled_multisignal_protocol import (
    SCALED_MULTISIGNAL_PROTOCOL,
)


def test_scaled_multisignal_protocol_uses_four_grams():
    assert (
        SCALED_MULTISIGNAL_PROTOCOL.ngram_size
        == 4
    )


def test_scaled_multisignal_protocol_uses_provenance_labels():
    assert (
        SCALED_MULTISIGNAL_PROTOCOL.label_view
        == "provenance_families"
    )


def test_scaled_multisignal_protocol_freezes_cohort_fields():
    assert (
        SCALED_MULTISIGNAL_PROTOCOL.cohort_fields
        == (
            "shared_feature_count",
            "pair_specific_feature_count",
            "max_rarity",
            "mean_rarity",
        )
    )


def test_scaled_multisignal_protocol_freezes_behavior_fields():
    assert (
        SCALED_MULTISIGNAL_PROTOCOL.behavioral_fields
        == (
            "shared_failure_count",
            "identical_wrong_output_count",
            "max_failure_rarity",
            "max_wrong_output_rarity",
        )
    )


def test_scaled_multisignal_protocol_has_no_combined_score():
    protocol = SCALED_MULTISIGNAL_PROTOCOL

    assert not hasattr(
        protocol,
        "combined_score",
    )

    interpretation = (
        protocol.interpretation.lower()
    )

    assert "separate channels" in interpretation
    assert "combined score" in interpretation
    assert "automated verdict" in interpretation


def test_scaled_multisignal_protocol_freezes_collision_value():
    assert (
        SCALED_MULTISIGNAL_PROTOCOL
        .structural_collision_value
        == 1.0
    )
