from pathlib import Path

import pytest

from behavclone.baselines.jplag_runner import (
    sha256_file,
)


def test_sha256_file_is_deterministic(
    tmp_path: Path,
):
    path = tmp_path / "artifact.jar"
    path.write_bytes(b"behavclone-jplag")

    first = sha256_file(path)
    second = sha256_file(path)

    assert first == second
    assert len(first) == 64


def test_sha256_file_matches_known_digest(
    tmp_path: Path,
):
    path = tmp_path / "artifact.jar"
    path.write_bytes(b"abc")

    assert sha256_file(path) == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_sha256_file_rejects_missing_file(
    tmp_path: Path,
):
    with pytest.raises(FileNotFoundError):
        sha256_file(
            tmp_path / "missing.jar"
        )
