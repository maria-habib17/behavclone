from dataclasses import dataclass


@dataclass(frozen=True)
class FragmentSimilarity:
    """Measured similarity between two source fragments."""

    raw: float
    normalized: float
    structural: float


@dataclass(frozen=True)
class FragmentMatch:
    """One selected one-to-one correspondence between fragments."""

    left_index: int
    right_index: int
    similarity: float


@dataclass(frozen=True)
class FragmentAssignment:
    """Maximum-weight one-to-one fragment assignment."""

    matches: tuple[FragmentMatch, ...]
    total_similarity: float

    @property
    def matched_count(self) -> int:
        return len(self.matches)
