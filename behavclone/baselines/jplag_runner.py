"""External JPlag execution with explicit, reproducible provenance."""

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

from behavclone.baselines.jplag_csv import load_jplag_csv
from behavclone.baselines.jplag_models import JPlagResults


@dataclass(frozen=True)
class JPlagProvenance:
    """Pinned external-tool provenance for one JPlag run."""

    version: str
    jar_sha256: str
    java_executable: str
    jar_path: str
    normalized: bool
    frequency_analysis: bool


@dataclass(frozen=True)
class JPlagRun:
    """Results and provenance from one external JPlag execution."""

    results: JPlagResults
    provenance: JPlagProvenance
    report_path: Path
    csv_path: Path


def sha256_file(path: str | Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def run_jplag(
    submissions_directory: str | Path,
    output_directory: str | Path,
    *,
    java_executable: str | Path,
    jar_path: str | Path,
    version: str,
    expected_jar_sha256: str,
    normalize: bool = False,
    frequency: bool = False,
) -> JPlagRun:
    """Run pinned JPlag and import its non-anonymized CSV results."""
    submissions_directory = Path(submissions_directory)
    output_directory = Path(output_directory)
    java_executable = Path(java_executable)
    jar_path = Path(jar_path)

    if not submissions_directory.is_dir():
        raise ValueError(
            "JPlag submissions directory does not exist: "
            f"{submissions_directory}"
        )

    if not java_executable.is_file():
        raise ValueError(
            "Java executable does not exist: "
            f"{java_executable}"
        )

    if not jar_path.is_file():
        raise ValueError(
            f"JPlag JAR does not exist: {jar_path}"
        )

    actual_hash = sha256_file(jar_path)
    expected_hash = expected_jar_sha256.lower()

    if actual_hash != expected_hash:
        raise ValueError(
            "JPlag JAR SHA-256 mismatch: "
            f"expected {expected_hash}, got {actual_hash}"
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_base = output_directory / "results"

    command = [
        str(java_executable),
        "-jar",
        str(jar_path),
        str(submissions_directory),
        "--language",
        "java",
        "--mode",
        "RUN",
        "--shown-comparisons",
        "-1",
        "--similarity-threshold",
        "0.0",
        "--csv-export",
        "--cluster-skip",
        "--overwrite",
        "--result-file",
        str(result_base),
    ]

    if normalize:
        command.append("--normalize")

    if frequency:
        command.append("--frequency")

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "JPlag execution failed with exit code "
            f"{completed.returncode}.\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )

    report_path = result_base.with_suffix(".jplag")
    csv_path = result_base / "results.csv"

    if not report_path.is_file():
        raise RuntimeError(
            "JPlag completed without producing its report: "
            f"{report_path}"
        )

    if not csv_path.is_file():
        raise RuntimeError(
            "JPlag completed without producing results.csv: "
            f"{csv_path}"
        )

    provenance = JPlagProvenance(
        version=version,
        jar_sha256=actual_hash,
        java_executable=str(java_executable),
        jar_path=str(jar_path),
        normalized=normalize,
        frequency_analysis=frequency,
    )

    return JPlagRun(
        results=load_jplag_csv(csv_path),
        provenance=provenance,
        report_path=report_path,
        csv_path=csv_path,
    )
