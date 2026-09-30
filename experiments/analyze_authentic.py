from __future__ import annotations

import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_PAIR_COUNT = 105


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pair_key(row: dict[str, Any]) -> tuple[str, str]:
    left = row["left_submission_id"]
    right = row["right_submission_id"]
    return tuple(sorted((left, right)))


def _index_pairs(
    rows: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    indexed = {
        _pair_key(row): row
        for row in rows
    }

    if len(rows) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PAIR_COUNT} rows, "
            f"found {len(rows)}."
        )

    if len(indexed) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            "Expected 105 unique unordered pairs."
        )

    return indexed


def _describe(
    values: list[float],
) -> dict[str, float | int]:
    return {
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "max": max(values),
        "zero_count": sum(
            value == 0.0
            for value in values
        ),
        "one_count": sum(
            value == 1.0
            for value in values
        ),
        "unique_values": len(set(values)),
    }


def _average_ranks(
    rows: dict[tuple[str, str], dict[str, Any]],
    field: str,
) -> dict[tuple[str, str], float]:
    ordered = sorted(
        (
            row[field],
            pair,
        )
        for pair, row in rows.items()
    )

    ranks: dict[tuple[str, str], float] = {}
    index = 0

    while index < len(ordered):
        value = ordered[index][0]
        end = index

        while (
            end + 1 < len(ordered)
            and ordered[end + 1][0] == value
        ):
            end += 1

        high_rank = len(ordered) - end
        low_rank = len(ordered) - index
        average_rank = (
            high_rank + low_rank
        ) / 2.0

        for position in range(index, end + 1):
            ranks[ordered[position][1]] = average_rank

        index = end + 1

    return ranks


def _pearson(
    left: list[float],
    right: list[float],
) -> float:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)

    numerator = sum(
        (x - left_mean) * (y - right_mean)
        for x, y in zip(left, right, strict=True)
    )

    left_denominator = math.sqrt(
        sum(
            (x - left_mean) ** 2
            for x in left
        )
    )

    right_denominator = math.sqrt(
        sum(
            (y - right_mean) ** 2
            for y in right
        )
    )

    if (
        left_denominator == 0.0
        or right_denominator == 0.0
    ):
        raise ValueError(
            "Rank correlation is undefined."
        )

    return numerator / (
        left_denominator
        * right_denominator
    )


def _spearman(
    left_rows: dict[
        tuple[str, str],
        dict[str, Any],
    ],
    left_field: str,
    right_rows: dict[
        tuple[str, str],
        dict[str, Any],
    ],
    right_field: str,
) -> float:
    pairs = sorted(left_rows)

    left_ranks = _average_ranks(
        left_rows,
        left_field,
    )

    right_ranks = _average_ranks(
        right_rows,
        right_field,
    )

    return _pearson(
        [
            left_ranks[pair]
            for pair in pairs
        ],
        [
            right_ranks[pair]
            for pair in pairs
        ],
    )


def _tie_summary(
    rows: dict[
        tuple[str, str],
        dict[str, Any],
    ],
    field: str,
) -> dict[str, Any]:
    counts = Counter(
        row[field]
        for row in rows.values()
    )

    groups = [
        {
            "score": score,
            "pair_count": count,
        }
        for score, count in sorted(
            counts.items(),
            reverse=True,
        )
    ]

    return {
        "distinct_score_count": len(groups),
        "largest_tie_group": max(
            counts.values()
        ),
        "groups": groups,
    }


def build_authentic_analysis(
    behavclone_path: Path,
    jplag_path: Path,
) -> dict[str, Any]:
    behavclone_rows = _load_json(
        behavclone_path
    )

    jplag_rows = _load_json(
        jplag_path
    )

    behavclone = _index_pairs(
        behavclone_rows
    )

    jplag = _index_pairs(
        jplag_rows
    )

    if set(behavclone) != set(jplag):
        raise ValueError(
            "BehavClone and JPlag pair sets differ."
        )

    pairs = sorted(behavclone)

    distributions = {}

    for label, rows, field in (
        (
            "behavclone_raw",
            behavclone,
            "mean_raw_similarity",
        ),
        (
            "behavclone_normalized",
            behavclone,
            "mean_normalized_similarity",
        ),
        (
            "behavclone_structural",
            behavclone,
            "mean_structural_similarity",
        ),
        (
            "jplag_average",
            jplag,
            "average_similarity",
        ),
        (
            "jplag_max",
            jplag,
            "max_similarity",
        ),
    ):
        distributions[label] = _describe(
            [
                rows[pair][field]
                for pair in pairs
            ]
        )

    rank_association = {
        "behavclone_raw_vs_jplag_average": (
            _spearman(
                behavclone,
                "mean_raw_similarity",
                jplag,
                "average_similarity",
            )
        ),
        "behavclone_raw_vs_jplag_max": (
            _spearman(
                behavclone,
                "mean_raw_similarity",
                jplag,
                "max_similarity",
            )
        ),
        "behavclone_normalized_vs_jplag_average": (
            _spearman(
                behavclone,
                "mean_normalized_similarity",
                jplag,
                "average_similarity",
            )
        ),
        "behavclone_normalized_vs_jplag_max": (
            _spearman(
                behavclone,
                "mean_normalized_similarity",
                jplag,
                "max_similarity",
            )
        ),
        "behavclone_structural_vs_jplag_average": (
            _spearman(
                behavclone,
                "mean_structural_similarity",
                jplag,
                "average_similarity",
            )
        ),
        "behavclone_structural_vs_jplag_max": (
            _spearman(
                behavclone,
                "mean_structural_similarity",
                jplag,
                "max_similarity",
            )
        ),
    }

    tie_structure = {}

    for label, rows, field in (
        (
            "behavclone_raw",
            behavclone,
            "mean_raw_similarity",
        ),
        (
            "behavclone_normalized",
            behavclone,
            "mean_normalized_similarity",
        ),
        (
            "behavclone_structural",
            behavclone,
            "mean_structural_similarity",
        ),
        (
            "jplag_average",
            jplag,
            "average_similarity",
        ),
        (
            "jplag_max",
            jplag,
            "max_similarity",
        ),
    ):
        tie_structure[label] = _tie_summary(
            rows,
            field,
        )

    behavclone_maximal = {
        pair
        for pair in pairs
        if behavclone[pair][
            "mean_normalized_similarity"
        ] == 1.0
    }

    jplag_average_maximal = {
        pair
        for pair in pairs
        if jplag[pair][
            "average_similarity"
        ] == 1.0
    }

    maximal_overlap = {
        "behavclone_normalized_count": len(
            behavclone_maximal
        ),
        "jplag_average_count": len(
            jplag_average_maximal
        ),
        "intersection_count": len(
            behavclone_maximal
            & jplag_average_maximal
        ),
        "behavclone_only_count": len(
            behavclone_maximal
            - jplag_average_maximal
        ),
        "jplag_only_count": len(
            jplag_average_maximal
            - behavclone_maximal
        ),
    }

    cohort_fields = (
        "shared_feature_count",
        "pair_specific_feature_count",
        "max_rarity",
        "mean_rarity",
    )

    cohort_all_pairs = {
        field: _describe(
            [
                behavclone[pair][field]
                for pair in pairs
            ]
        )
        for field in cohort_fields
    }

    cohort_within_maximal = {
        field: _describe(
            [
                behavclone[pair][field]
                for pair in sorted(
                    behavclone_maximal
                )
            ]
        )
        for field in cohort_fields
    }

    pair_specific_nonzero = [
        {
            "left_submission_id": pair[0],
            "right_submission_id": pair[1],
            "pair_specific_feature_count": (
                behavclone[pair][
                    "pair_specific_feature_count"
                ]
            ),
        }
        for pair in pairs
        if behavclone[pair][
            "pair_specific_feature_count"
        ] > 0
    ]

    coverage = {
        field: _describe(
            [
                behavclone[pair][field]
                for pair in pairs
            ]
        )
        for field in (
            "left_fragment_count",
            "right_fragment_count",
            "matched_count",
            "left_coverage",
            "right_coverage",
        )
    }

    return {
        "experiment": (
            "authentic-false-positive-analysis"
        ),
        "dataset": "IR-Plag",
        "case": "case-01",
        "cohort": "non-plagiarized",
        "language": "Java",
        "submission_count": 15,
        "pair_count": EXPECTED_PAIR_COUNT,
        "dataset_label": (
            "dataset-provided non-plagiarized"
        ),
        "distributions": distributions,
        "rank_association_spearman": (
            rank_association
        ),
        "tie_structure": tie_structure,
        "maximal_similarity_overlap": (
            maximal_overlap
        ),
        "behavclone_cohort_all_pairs": (
            cohort_all_pairs
        ),
        "behavclone_cohort_within_"
        "normalized_maximal_pairs": (
            cohort_within_maximal
        ),
        "pair_specific_nonzero_pairs": (
            pair_specific_nonzero
        ),
        "fragment_coverage": coverage,
        "behavioral_evidence": "unavailable",
        "combined_score": False,
        "plagiarism_verdict": False,
        "interpretation_boundaries": [
            (
                "Dataset-provided labels are used "
                "for false-positive and similarity-"
                "ambiguity analysis; they do not "
                "establish author intent."
            ),
            (
                "BehavClone and JPlag similarity "
                "values are not mathematically "
                "equivalent scores."
            ),
            (
                "Large exact-score ties make "
                "lexically tie-broken top-K order "
                "unsuitable as unique rank evidence."
            ),
            (
                "The authentic cohort contains one "
                "extracted fragment per submission, "
                "so it does not validate "
                "architecture-flexible multi-fragment "
                "matching."
            ),
            (
                "Behavioral evidence is unavailable "
                "for this authentic cohort."
            ),
            (
                "No universal plagiarism threshold, "
                "plagiarism verdict, or general "
                "superiority claim is supported."
            ),
        ],
    }


def write_authentic_analysis(
    analysis: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = (
        json.dumps(
            analysis,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    output_path.write_bytes(
        serialized.encode("utf-8")
    )


def main() -> None:
    analysis = build_authentic_analysis(
        Path(
            "results/authentic/behavclone/"
            "pairs.json"
        ),
        Path(
            "results/authentic/jplag/"
            "pairs.json"
        ),
    )

    write_authentic_analysis(
        analysis,
        Path(
            "results/authentic/analysis/"
            "summary.json"
        ),
    )

    print(
        "Wrote authentic analysis to "
        "results/authentic/analysis/summary.json"
    )


if __name__ == "__main__":
    main()
