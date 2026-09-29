from dataclasses import dataclass
from pathlib import Path

TokenNgram = tuple[str, ...]


@dataclass(frozen=True)
class CohortFeatureEvidence:
    """Cohort-relative evidence for one normalized token n-gram."""

    feature: TokenNgram
    document_frequency: int
    cohort_size: int
    rarity: float

    @property
    def document_proportion(self) -> float:
        if self.cohort_size == 0:
            return 0.0

        return self.document_frequency / self.cohort_size


@dataclass(frozen=True)
class CohortProfile:
    """Document-frequency profile for one assignment cohort."""

    cohort_size: int
    ngram_size: int
    document_frequencies: dict[TokenNgram, int]


@dataclass(frozen=True)
class FragmentCohortEvidence:
    """Cohort context for one selected fragment correspondence."""

    left_file: Path
    left_name: str
    left_start_line: int
    right_file: Path
    right_name: str
    right_start_line: int
    shared_features: tuple[CohortFeatureEvidence, ...]

    @property
    def shared_feature_count(self) -> int:
        return len(self.shared_features)

    @property
    def max_rarity(self) -> float:
        if not self.shared_features:
            return 0.0

        return max(
            feature.rarity
            for feature in self.shared_features
        )

    @property
    def mean_rarity(self) -> float:
        if not self.shared_features:
            return 0.0

        return sum(
            feature.rarity
            for feature in self.shared_features
        ) / self.shared_feature_count


@dataclass(frozen=True)
class SubmissionCohortEvidence:
    """Cohort evidence attached to one pairwise submission comparison."""

    cohort_size: int
    ngram_size: int
    matches: tuple[FragmentCohortEvidence, ...]
