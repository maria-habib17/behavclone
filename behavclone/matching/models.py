from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True)
class SubmissionFragmentMatch:
    """Interpretable correspondence between methods in two submissions."""

    left_file: Path
    left_name: str
    left_start_line: int
    right_file: Path
    right_name: str
    right_start_line: int
    similarity: FragmentSimilarity


@dataclass(frozen=True)
class SubmissionComparison:
    """Evidence produced when comparing two complete submissions."""

    left_fragment_count: int
    right_fragment_count: int
    matches: tuple[SubmissionFragmentMatch, ...]

    @property
    def matched_count(self) -> int:
        return len(self.matches)

    @property
    def left_coverage(self) -> float:
        if self.left_fragment_count == 0:
            return 0.0

        return self.matched_count / self.left_fragment_count

    @property
    def right_coverage(self) -> float:
        if self.right_fragment_count == 0:
            return 0.0

        return self.matched_count / self.right_fragment_count

    @property
    def mean_normalized_similarity(self) -> float:
        if not self.matches:
            return 0.0

        return sum(
            match.similarity.normalized
            for match in self.matches
        ) / self.matched_count

    @property
    def mean_structural_similarity(self) -> float:
        if not self.matches:
            return 0.0

        return sum(
            match.similarity.structural
            for match in self.matches
        ) / self.matched_count
