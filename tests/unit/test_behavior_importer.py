from pathlib import Path

import pytest

from behavclone.behavior.importer import (
    load_behavioral_results,
)
from behavclone.behavior.models import TestStatus as BehaviorTestStatus


def write_csv(
    path: Path,
    content: str,
) -> None:
    path.write_text(
        content,
        encoding="utf-8",
    )


def test_loads_behavioral_results(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            "S001,T01,PASS,10,10\n"
            "S001,T02,FAIL,20,19\n"
            "S002,T01,pass,10,10\n"
        ),
    )

    dataset = load_behavioral_results(path)

    assert len(dataset.observations) == 3
    assert dataset.submission_ids == frozenset({
        "S001",
        "S002",
    })
    assert dataset.test_ids == frozenset({
        "T01",
        "T02",
    })

    first = dataset.observations[0]

    assert first.submission_id == "S001"
    assert first.test_id == "T01"
    assert first.status is BehaviorTestStatus.PASS
    assert first.passed
    assert not first.failed


def test_filters_observations_by_submission(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            "S001,T01,PASS,10,10\n"
            "S002,T01,FAIL,10,9\n"
            "S001,T02,FAIL,20,19\n"
        ),
    )

    dataset = load_behavioral_results(path)

    observations = dataset.for_submission(
        "S001"
    )

    assert [
        observation.test_id
        for observation in observations
    ] == [
        "T01",
        "T02",
    ]


def test_preserves_expected_and_actual_output_exactly(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            'S001,T01,FAIL," expected "," actual "\n'
        ),
    )

    dataset = load_behavioral_results(path)
    observation = dataset.observations[0]

    assert observation.expected == " expected "
    assert observation.actual == " actual "


def test_rejects_missing_required_column(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected\n"
            "S001,T01,PASS,10\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="missing required columns: actual",
    ):
        load_behavioral_results(path)


def test_rejects_missing_submission_value(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            ",T01,PASS,10,10\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="missing value for 'submission'",
    ):
        load_behavioral_results(path)


def test_rejects_missing_test_value(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            "S001,,PASS,10,10\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="missing value for 'test'",
    ):
        load_behavioral_results(path)


def test_rejects_unsupported_status(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            "S001,T01,UNKNOWN,10,10\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="unsupported test status 'UNKNOWN'",
    ):
        load_behavioral_results(path)


def test_rejects_duplicate_submission_test_observation(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        (
            "submission,test,status,expected,actual\n"
            "S001,T01,PASS,10,10\n"
            "S001,T01,FAIL,10,9\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="Duplicate behavioral observation",
    ):
        load_behavioral_results(path)


def test_rejects_missing_file(
    tmp_path: Path,
):
    path = tmp_path / "missing.csv"

    with pytest.raises(
        FileNotFoundError,
        match="Behavioral results file does not exist",
    ):
        load_behavioral_results(path)


def test_empty_data_file_produces_empty_dataset(
    tmp_path: Path,
):
    path = tmp_path / "results.csv"

    write_csv(
        path,
        "submission,test,status,expected,actual\n",
    )

    dataset = load_behavioral_results(path)

    assert dataset.observations == ()
    assert dataset.submission_ids == frozenset()
    assert dataset.test_ids == frozenset()
