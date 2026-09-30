"""Reproducible configuration ablation for pinned JPlag."""

import argparse
import csv
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from behavclone.baselines.jplag_runner import (
    JPlagProvenance,
    run_jplag,
)
from experiments.controlled import controlled_pairs
from experiments.run_jplag_comparison import (
    JPLAG_SHA256,
    JPLAG_VERSION,
)
from experiments.synthetic import (
    controlled_submissions,
    write_synthetic_assignment,
)


@dataclass(frozen=True)
class JPlagConfiguration:
    """One explicit JPlag configuration."""

    name: str
    normalize: bool
    frequency: bool


@dataclass(frozen=True)
class JPlagAblationRow:
    """Pairwise result for one JPlag configuration."""

    configuration: str
    normalized: bool
    frequency_analysis: bool
    left_submission_id: str
    right_submission_id: str
    related: bool
    transformation: str
    average_similarity: float
    max_similarity: float


CONFIGURATIONS = (
    JPlagConfiguration(
        name="standard",
        normalize=False,
        frequency=False,
    ),
    JPlagConfiguration(
        name="normalized",
        normalize=True,
        frequency=False,
    ),
    JPlagConfiguration(
        name="frequency",
        normalize=False,
        frequency=True,
    ),
)


def _portable_provenance(
    provenance: JPlagProvenance,
) -> dict[str, object]:
    return {
        "version": provenance.version,
        "jar_sha256": provenance.jar_sha256,
        "normalized": provenance.normalized,
        "frequency_analysis": provenance.frequency_analysis,
    }


def _write_json(
    path: Path,
    payload: object,
) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_csv(
    path: Path,
    rows: tuple[JPlagAblationRow, ...],
) -> None:
    fieldnames = [
        "configuration",
        "normalized",
        "frequency_analysis",
        "left_submission_id",
        "right_submission_id",
        "related",
        "transformation",
        "average_similarity",
        "max_similarity",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field: getattr(row, field)
                    for field in fieldnames
                }
            )


def run_jplag_configuration_ablation(
    output_root: str | Path,
    *,
    java_executable: str | Path,
    jplag_jar: str | Path,
) -> Path:
    """Run explicit JPlag configurations on one controlled corpus."""
    output_root = Path(output_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    pairs = controlled_pairs()
    rows: list[JPlagAblationRow] = []
    provenance_by_configuration: dict[
        str,
        dict[str, object],
    ] = {}

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        assignment_root = temporary_root / "assignment"

        write_synthetic_assignment(
            assignment_root,
            controlled_submissions(),
        )

        submissions_directory = (
            assignment_root / "submissions"
        )

        for configuration in CONFIGURATIONS:
            jplag_output = (
                temporary_root
                / f"jplag-{configuration.name}"
            )

            run = run_jplag(
                submissions_directory,
                jplag_output,
                java_executable=java_executable,
                jar_path=jplag_jar,
                version=JPLAG_VERSION,
                expected_jar_sha256=JPLAG_SHA256,
                normalize=configuration.normalize,
                frequency=configuration.frequency,
            )

            provenance_by_configuration[
                configuration.name
            ] = _portable_provenance(
                run.provenance
            )

            for pair in pairs:
                result = run.results.find_pair(
                    pair.left_submission_id,
                    pair.right_submission_id,
                )

                rows.append(
                    JPlagAblationRow(
                        configuration=configuration.name,
                        normalized=configuration.normalize,
                        frequency_analysis=(
                            configuration.frequency
                        ),
                        left_submission_id=(
                            pair.left_submission_id
                        ),
                        right_submission_id=(
                            pair.right_submission_id
                        ),
                        related=pair.related,
                        transformation=(
                            pair.transformation.value
                            if pair.transformation is not None
                            else "control"
                        ),
                        average_similarity=(
                            result.average_similarity
                        ),
                        max_similarity=(
                            result.max_similarity
                        ),
                    )
                )

    rows_tuple = tuple(rows)

    payload = {
        "experiment": "controlled-jplag-configuration-ablation",
        "interpretation": (
            "JPlag configuration sensitivity on a small synthetic "
            "controlled corpus. Pairwise CSV similarities are reported "
            "as exported by JPlag. Unchanged CSV values do not imply "
            "that an option has no effect elsewhere in JPlag's analysis "
            "or report. These results do not establish general "
            "superiority or plagiarism-detection accuracy."
        ),
        "version": JPLAG_VERSION,
        "jar_sha256": JPLAG_SHA256,
        "configuration_count": len(CONFIGURATIONS),
        "pair_count_per_configuration": len(pairs),
        "configurations": provenance_by_configuration,
        "rows": [
            asdict(row)
            for row in rows_tuple
        ],
    }

    json_path = output_root / "configurations.json"

    _write_json(
        json_path,
        payload,
    )

    _write_csv(
        output_root / "configurations.csv",
        rows_tuple,
    )

    return json_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run pinned JPlag configuration ablations "
            "on the controlled corpus."
        )
    )
    parser.add_argument(
        "--java",
        default=os.environ.get(
            "BEHAVCLONE_JAVA25"
        ),
        help=(
            "Path to a Java 25 executable. "
            "Can also use BEHAVCLONE_JAVA25."
        ),
    )
    parser.add_argument(
        "--jplag-jar",
        default=os.environ.get(
            "BEHAVCLONE_JPLAG_JAR"
        ),
        help=(
            "Path to the pinned JPlag 6.3.0 JAR. "
            "Can also use BEHAVCLONE_JPLAG_JAR."
        ),
    )
    parser.add_argument(
        "--output",
        default=(
            "results/baselines/"
            "jplag-configurations"
        ),
    )

    args = parser.parse_args()

    if not args.java:
        parser.error(
            "--java or BEHAVCLONE_JAVA25 is required"
        )

    if not args.jplag_jar:
        parser.error(
            "--jplag-jar or BEHAVCLONE_JPLAG_JAR is required"
        )

    output = run_jplag_configuration_ablation(
        args.output,
        java_executable=args.java,
        jplag_jar=args.jplag_jar,
    )

    print(
        "Wrote JPlag configuration ablation to "
        f"{output}"
    )


if __name__ == "__main__":
    main()
