from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)


def controlled_pairs() -> tuple[BenchmarkPair, ...]:
    """Return labeled pairs for the controlled transformation benchmark."""
    return (
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="ID_RENAME",
            related=True,
            transformation=TransformationKind.IDENTIFIER_RENAME,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="METHOD_REORDER",
            related=True,
            transformation=TransformationKind.METHOD_REORDER,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="CLASS_RENAME",
            related=True,
            transformation=TransformationKind.CLASS_RENAME,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="FILE_RENAME",
            related=True,
            transformation=TransformationKind.FILE_RENAME,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="DEAD_CODE",
            related=True,
            transformation=TransformationKind.DEAD_CODE,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="CLASS_SPLIT",
            related=True,
            transformation=TransformationKind.CLASS_SPLIT,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="UNRELATED_A",
            related=False,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="UNRELATED_B",
            related=False,
        ),
        BenchmarkPair(
            left_submission_id="BASE",
            right_submission_id="LOOKALIKE",
            related=False,
        ),
    )
