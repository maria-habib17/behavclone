from dataclasses import dataclass
from enum import Enum


class TestStatus(str, Enum):
    """Observed outcome of one externally executed test."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class TestObservation:
    """Imported behavioral observation for one submission and test."""

    submission_id: str
    test_id: str
    status: TestStatus
    expected: str
    actual: str

    @property
    def passed(self) -> bool:
        return self.status is TestStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status is TestStatus.FAIL


@dataclass(frozen=True)
class BehavioralDataset:
    """Validated externally supplied behavioral observations."""

    observations: tuple[TestObservation, ...]

    @property
    def submission_ids(self) -> frozenset[str]:
        return frozenset(
            observation.submission_id
            for observation in self.observations
        )

    @property
    def test_ids(self) -> frozenset[str]:
        return frozenset(
            observation.test_id
            for observation in self.observations
        )

    def for_submission(
        self,
        submission_id: str,
    ) -> tuple[TestObservation, ...]:
        return tuple(
            observation
            for observation in self.observations
            if observation.submission_id == submission_id
        )


@dataclass(frozen=True)
class BehavioralCohortProfile:
    """Cohort frequencies derived from imported test observations."""

    cohort_size: int
    failure_counts: dict[str, int]
    wrong_output_counts: dict[tuple[str, str], int]

    def failure_count(self, test_id: str) -> int:
        return self.failure_counts.get(test_id, 0)

    def wrong_output_count(
        self,
        test_id: str,
        actual: str,
    ) -> int:
        return self.wrong_output_counts.get(
            (test_id, actual),
            0,
        )


@dataclass(frozen=True)
class SharedFailureEvidence:
    """Evidence for one test failed by both compared submissions."""

    test_id: str
    expected: str
    left_actual: str
    right_actual: str
    failure_count: int
    cohort_size: int
    failure_rarity: float
    identical_wrong_output: bool
    wrong_output_count: int | None
    wrong_output_rarity: float | None

    @property
    def failure_proportion(self) -> float:
        if self.cohort_size == 0:
            return 0.0
        return self.failure_count / self.cohort_size

    @property
    def wrong_output_proportion(self) -> float | None:
        if self.wrong_output_count is None:
            return None
        if self.cohort_size == 0:
            return 0.0
        return self.wrong_output_count / self.cohort_size


@dataclass(frozen=True)
class SubmissionBehavioralEvidence:
    """Behavioral evidence for one submission pair."""

    left_submission_id: str
    right_submission_id: str
    cohort_size: int
    shared_failures: tuple[SharedFailureEvidence, ...]

    @property
    def shared_failure_count(self) -> int:
        return len(self.shared_failures)

    @property
    def identical_wrong_output_count(self) -> int:
        return sum(
            evidence.identical_wrong_output
            for evidence in self.shared_failures
        )
