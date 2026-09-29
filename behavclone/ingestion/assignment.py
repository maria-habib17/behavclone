from pathlib import Path

import yaml

from behavclone.ingestion.models import (
    Assignment,
    AssignmentConfig,
    Submission,
)


def discover_java_files(root: Path) -> list[Path]:
    """Recursively discover Java source files."""

    return sorted(
        path
        for path in root.rglob("*.java")
        if path.is_file()
    )


def load_assignment(root: str | Path) -> Assignment:
    """Load an assignment and discover its submissions."""

    root = Path(root).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Assignment directory does not exist: {root}"
        )

    config_path = root / "assignment.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Missing assignment configuration: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle)

    if not isinstance(raw_config, dict) or "assignment" not in raw_config:
        raise ValueError(
            "assignment.yaml must contain an 'assignment' section."
        )

    config = AssignmentConfig.model_validate(
        raw_config["assignment"]
    )

    if config.language.lower() != "java":
        raise ValueError(
            "BehavClone v0.1 currently supports Java assignments only."
        )

    submissions_root = root / config.submissions_directory

    if not submissions_root.exists():
        raise FileNotFoundError(
            f"Missing submissions directory: {submissions_root}"
        )

    submissions: list[Submission] = []

    for directory in sorted(submissions_root.iterdir()):
        if not directory.is_dir():
            continue

        submissions.append(
            Submission(
                submission_id=directory.name,
                root=directory,
                source_files=discover_java_files(directory),
            )
        )

    return Assignment(
        root=root,
        config=config,
        submissions=submissions,
    )
