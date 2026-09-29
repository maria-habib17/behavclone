import csv
from pathlib import Path

from behavclone.behavior.models import (
    BehavioralDataset,
    TestObservation,
    TestStatus,
)

REQUIRED_COLUMNS = {
    "submission",
    "test",
    "status",
    "expected",
    "actual",
}


def _required_value(
    row: dict[str, str | None],
    column: str,
    row_number: int,
) -> str:
    value = row.get(column)

    if value is None or not value.strip():
        raise ValueError(
            f"Row {row_number}: missing value for '{column}'."
        )

    return value.strip()


def _parse_status(
    value: str,
    row_number: int,
) -> TestStatus:
    normalized = value.strip().upper()

    try:
        return TestStatus(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_number}: unsupported test status '{value}'."
        ) from exc


def load_behavioral_results(
    path: str | Path,
) -> BehavioralDataset:
    """Load externally generated test observations from CSV."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Behavioral results file does not exist: {path}"
        )

    observations: list[TestObservation] = []
    seen: set[tuple[str, str]] = set()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(
                "Behavioral results CSV must contain a header."
            )

        fieldnames = {
            field.strip()
            for field in reader.fieldnames
            if field is not None
        }

        missing_columns = (
            REQUIRED_COLUMNS - fieldnames
        )

        if missing_columns:
            missing = ", ".join(
                sorted(missing_columns)
            )
            raise ValueError(
                "Behavioral results CSV is missing required "
                f"columns: {missing}"
            )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
            submission_id = _required_value(
                row,
                "submission",
                row_number,
            )
            test_id = _required_value(
                row,
                "test",
                row_number,
            )
            status_text = _required_value(
                row,
                "status",
                row_number,
            )

            expected = row.get("expected")
            actual = row.get("actual")

            if expected is None:
                expected = ""

            if actual is None:
                actual = ""

            key = (
                submission_id,
                test_id,
            )

            if key in seen:
                raise ValueError(
                    "Duplicate behavioral observation for "
                    f"submission '{submission_id}' and "
                    f"test '{test_id}'."
                )

            seen.add(key)

            observations.append(
                TestObservation(
                    submission_id=submission_id,
                    test_id=test_id,
                    status=_parse_status(
                        status_text,
                        row_number,
                    ),
                    expected=expected,
                    actual=actual,
                )
            )

    return BehavioralDataset(
        observations=tuple(observations)
    )
