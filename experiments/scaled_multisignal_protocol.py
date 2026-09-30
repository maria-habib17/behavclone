"""Predeclared protocol for scaled multi-signal evaluation.

This module freezes the analysis choices before scaled behavioral
measurements are generated. Evidence channels remain separate and are
not combined into a plagiarism score or automated verdict.
"""

from dataclasses import dataclass

SCALED_MULTISIGNAL_NGRAM_SIZE = 4

STRUCTURAL_COLLISION_VALUE = 1.0


@dataclass(frozen=True)
class ScaledMultiSignalProtocol:
    """Frozen analysis choices for the scaled multi-signal experiment."""

    ngram_size: int
    structural_collision_value: float
    cohort_fields: tuple[str, ...]
    behavioral_fields: tuple[str, ...]
    label_view: str
    interpretation: str


SCALED_MULTISIGNAL_PROTOCOL = ScaledMultiSignalProtocol(
    ngram_size=SCALED_MULTISIGNAL_NGRAM_SIZE,
    structural_collision_value=STRUCTURAL_COLLISION_VALUE,
    cohort_fields=(
        "shared_feature_count",
        "pair_specific_feature_count",
        "max_rarity",
        "mean_rarity",
    ),
    behavioral_fields=(
        "shared_failure_count",
        "identical_wrong_output_count",
        "max_failure_rarity",
        "max_wrong_output_rarity",
    ),
    label_view="provenance_families",
    interpretation=(
        "Structural, cohort-relative, and behavioral evidence are "
        "reported as separate channels. The primary label view treats "
        "within-family pairs as related and cross-family pairs as "
        "controls. Normalized and structural similarity collisions are "
        "analyzed without introducing a combined score, plagiarism "
        "threshold, automated verdict, or post-hoc relabeling."
    ),
)
