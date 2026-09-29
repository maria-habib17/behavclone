from pathlib import Path

from behavclone.behavior.evidence import compare_submission_behavior
from behavclone.behavior.importer import load_behavioral_results
from behavclone.behavior.models import (
    BehavioralDataset,
    SubmissionBehavioralEvidence,
)
from behavclone.ingestion.models import Assignment


def behavioral_results_path(
    assignment: Assignment,
) -> Path | None:
    """Resolve the configured external test-results file."""
    configured = assignment.config.test_results

    if configured is None:
        return None

    return assignment.root / configured


def load_assignment_behavior(
    assignment: Assignment,
) -> BehavioralDataset:
    """Load externally generated behavioral results for an assignment."""
    path = behavioral_results_path(assignment)

    if path is None:
        raise ValueError(
            "Assignment does not configure behavioral test results."
        )

    return load_behavioral_results(path)


def compare_assignment_behavior(
    assignment: Assignment,
    left_submission_id: str,
    right_submission_id: str,
) -> SubmissionBehavioralEvidence:
    """Compare a submission pair using configured external test results."""
    known_submissions = {
        submission.submission_id
        for submission in assignment.submissions
    }

    if left_submission_id not in known_submissions:
        raise ValueError(
            f"Unknown assignment submission: {left_submission_id}"
        )

    if right_submission_id not in known_submissions:
        raise ValueError(
            f"Unknown assignment submission: {right_submission_id}"
        )

    dataset = load_assignment_behavior(assignment)

    return compare_submission_behavior(
        dataset,
        left_submission_id,
        right_submission_id,
    )
