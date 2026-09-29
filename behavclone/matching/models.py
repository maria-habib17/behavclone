from dataclasses import dataclass


@dataclass(frozen=True)
class FragmentSimilarity:
    """Measured similarity between two source fragments."""

    raw: float
    normalized: float
    structural: float
