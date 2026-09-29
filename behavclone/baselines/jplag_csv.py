"""Import JPlag pairwise CSV exports."""

import csv
from pathlib import Path

from behavclone.baselines.jplag_models import (
    JPlagPairResult,
    JPlagResults,
)

_REQUIRED_COLUMNS = {
    "submissionName1",
    "submissionName2",
    "averageSimilarity",
    "maxSimilarity",
}


def load_jplag_csv(
    path: str | Path,
) -> JPlagResults:
    """Load the non-anonymized pairwise CSV exported by JPlag."""
    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        fieldnames = set(reader.fieldnames or ())

        missing = _REQUIRED_COLUMNS - fieldnames

        if missing:
            raise ValueError(
                "JPlag CSV is missing required columns: "
                + ", ".join(sorted(missing))
            )

        pairs = []

        for row in reader:
            left = row["submissionName1"].strip()
            right = row["submissionName2"].strip()

            if not left or not right:
                raise ValueError(
                    "JPlag CSV contains a blank submission name."
                )

            try:
                average = float(
                    row["averageSimilarity"]
                )
                maximum = float(
                    row["maxSimilarity"]
                )
            except ValueError as error:
                raise ValueError(
                    "JPlag CSV contains a non-numeric "
                    "similarity value."
                ) from error

            if not 0.0 <= average <= 1.0:
                raise ValueError(
                    "JPlag average similarity must be "
                    "between 0 and 1."
                )

            if not 0.0 <= maximum <= 1.0:
                raise ValueError(
                    "JPlag max similarity must be "
                    "between 0 and 1."
                )

            pairs.append(
                JPlagPairResult(
                    left_submission_id=left,
                    right_submission_id=right,
                    average_similarity=average,
                    max_similarity=maximum,
                )
            )

    return JPlagResults(
        pairs=tuple(pairs)
    )
