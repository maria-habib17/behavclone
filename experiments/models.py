from dataclasses import dataclass
from enum import Enum

from behavclone.matching.models import MatchingMetric


class TransformationKind(str, Enum):
    IDENTIFIER_RENAME = "identifier_rename"
    METHOD_REORDER = "method_reorder"
    CLASS_RENAME = "class_rename"
    FILE_RENAME = "file_rename"
    DEAD_CODE = "dead_code"
    CLASS_SPLIT = "class_split"


@dataclass(frozen=True)
class BenchmarkPair:
    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: TransformationKind | None = None

    def __post_init__(self) -> None:
        if not self.related and self.transformation is not None:
            raise ValueError(
                "Unrelated benchmark pairs cannot declare a transformation."
            )


@dataclass(frozen=True)
class PairMetrics:
    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: TransformationKind | None
    matched_count: int
    left_coverage: float
    right_coverage: float
    mean_raw_similarity: float
    mean_normalized_similarity: float
    mean_structural_similarity: float


@dataclass(frozen=True)
class BenchmarkResult:
    pairs: tuple[PairMetrics, ...]
    assignment_metric: MatchingMetric = "normalized"

    @property
    def related_pairs(self) -> tuple[PairMetrics, ...]:
        return tuple(
            pair
            for pair in self.pairs
            if pair.related
        )

    @property
    def unrelated_pairs(self) -> tuple[PairMetrics, ...]:
        return tuple(
            pair
            for pair in self.pairs
            if not pair.related
        )
