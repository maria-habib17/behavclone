from pathlib import Path

from pydantic import BaseModel, Field


class AssignmentConfig(BaseModel):
    """Configuration for one programming assignment."""

    name: str
    language: str = "java"
    submissions_directory: str = "submissions"
    starter_directory: str | None = "starter"
    test_results: str | None = "test-results.csv"


class Submission(BaseModel):
    """A pseudonymous programming submission."""

    submission_id: str
    root: Path
    source_files: list[Path] = Field(default_factory=list)


class Assignment(BaseModel):
    """An assignment together with its discovered submissions."""

    root: Path
    config: AssignmentConfig
    submissions: list[Submission] = Field(default_factory=list)
