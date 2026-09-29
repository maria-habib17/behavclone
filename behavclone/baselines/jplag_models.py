"""Models for externally produced JPlag baseline results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JPlagPairResult:
    """One pairwise similarity result exported by JPlag."""

    left_submission_id: str
    right_submission_id: str
    average_similarity: float
    max_similarity: float

    def involves(self, submission_id: str) -> bool:
        return submission_id in {
            self.left_submission_id,
            self.right_submission_id,
        }

    def matches_pair(
        self,
        left_submission_id: str,
        right_submission_id: str,
    ) -> bool:
        return {
            self.left_submission_id,
            self.right_submission_id,
        } == {
            left_submission_id,
            right_submission_id,
        }


@dataclass(frozen=True)
class JPlagResults:
    """Parsed pairwise results from one JPlag execution."""

    pairs: tuple[JPlagPairResult, ...]

    def find_pair(
        self,
        left_submission_id: str,
        right_submission_id: str,
    ) -> JPlagPairResult:
        matches = tuple(
            pair
            for pair in self.pairs
            if pair.matches_pair(
                left_submission_id,
                right_submission_id,
            )
        )

        if not matches:
            raise ValueError(
                "JPlag result does not contain pair: "
                f"{left_submission_id}, {right_submission_id}"
            )

        if len(matches) > 1:
            raise ValueError(
                "JPlag result contains duplicate pair: "
                f"{left_submission_id}, {right_submission_id}"
            )

        return matches[0]
