from pathlib import Path

import pytest

from behavclone.baselines.jplag_csv import (
    load_jplag_csv,
)


def write_csv(
    path: Path,
    content: str,
) -> None:
    path.write_text(
        content,
        encoding="utf-8",
    )


def test_loads_observed_jplag_csv_schema(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "BASE,ID_RENAME,1.0,1.0\n"
            "BASE,LOOKALIKE,1.0,1.0\n"
            "BASE,DEAD_CODE,0.0,0.0\n"
        ),
    )

    results = load_jplag_csv(path)

    assert len(results.pairs) == 3

    renamed = results.find_pair(
        "BASE",
        "ID_RENAME",
    )

    assert renamed.average_similarity == 1.0
    assert renamed.max_similarity == 1.0


def test_pair_lookup_is_order_independent(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "FILE_RENAME,ID_RENAME,1.0,1.0\n"
        ),
    )

    results = load_jplag_csv(path)

    pair = results.find_pair(
        "ID_RENAME",
        "FILE_RENAME",
    )

    assert pair.average_similarity == 1.0


def test_rejects_missing_required_column(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity\n"
            "BASE,ID_RENAME,1.0\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        load_jplag_csv(path)


def test_rejects_out_of_range_similarity(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "BASE,ID_RENAME,1.2,1.0\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="average similarity",
    ):
        load_jplag_csv(path)


def test_rejects_non_numeric_similarity(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "BASE,ID_RENAME,high,1.0\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="non-numeric",
    ):
        load_jplag_csv(path)


def test_rejects_duplicate_pair_on_lookup(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "BASE,ID_RENAME,1.0,1.0\n"
            "ID_RENAME,BASE,1.0,1.0\n"
        ),
    )

    results = load_jplag_csv(path)

    with pytest.raises(
        ValueError,
        match="duplicate pair",
    ):
        results.find_pair(
            "BASE",
            "ID_RENAME",
        )


def test_missing_pair_has_clear_error(
    tmp_path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submissionName1,submissionName2,"
            "averageSimilarity,maxSimilarity\n"
            "BASE,ID_RENAME,1.0,1.0\n"
        ),
    )

    results = load_jplag_csv(path)

    with pytest.raises(
        ValueError,
        match="does not contain pair",
    ):
        results.find_pair(
            "BASE",
            "LOOKALIKE",
        )
