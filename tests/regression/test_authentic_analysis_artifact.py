import hashlib
import json
from pathlib import Path

SUMMARY = Path(
    "results/authentic/analysis/summary.json"
)

EXPECTED_SHA256 = (
    "e48cf0f9a8a5c2a50ea4f78b6de408e9"
    "c492e727ab5ba62754b927a382e249a0"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_authentic_analysis_artifact_hash():
    assert _sha256(SUMMARY) == EXPECTED_SHA256


def test_authentic_analysis_core_findings():
    analysis = json.loads(
        SUMMARY.read_text(encoding="utf-8")
    )

    assert analysis["submission_count"] == 15
    assert analysis["pair_count"] == 105

    distributions = analysis["distributions"]

    assert (
        distributions[
            "behavclone_normalized"
        ]["one_count"]
        == 55
    )

    assert (
        distributions[
            "jplag_average"
        ]["one_count"]
        == 66
    )

    assert (
        distributions[
            "jplag_max"
        ]["one_count"]
        == 78
    )

    overlap = analysis[
        "maximal_similarity_overlap"
    ]

    assert overlap == {
        "behavclone_normalized_count": 55,
        "intersection_count": 55,
        "jplag_average_count": 66,
        "behavclone_only_count": 0,
        "jplag_only_count": 11,
    }

    rho = analysis[
        "rank_association_spearman"
    ][
        "behavclone_normalized_vs_jplag_average"
    ]

    assert abs(rho - 0.927817) < 0.000001


def test_authentic_analysis_negative_findings():
    analysis = json.loads(
        SUMMARY.read_text(encoding="utf-8")
    )

    cohort = analysis[
        "behavclone_cohort_within_"
        "normalized_maximal_pairs"
    ]

    assert (
        cohort[
            "pair_specific_feature_count"
        ]["max"]
        == 0
    )

    assert len(
        analysis["pair_specific_nonzero_pairs"]
    ) == 2

    coverage = analysis["fragment_coverage"]

    for field in (
        "left_fragment_count",
        "right_fragment_count",
        "matched_count",
        "left_coverage",
        "right_coverage",
    ):
        assert coverage[field]["min"] == 1.0
        assert coverage[field]["max"] == 1.0


def test_authentic_analysis_interpretation_guards():
    analysis = json.loads(
        SUMMARY.read_text(encoding="utf-8")
    )

    assert (
        analysis["behavioral_evidence"]
        == "unavailable"
    )
    assert analysis["combined_score"] is False
    assert analysis["plagiarism_verdict"] is False

    boundaries = analysis[
        "interpretation_boundaries"
    ]

    assert any(
        "not mathematically equivalent"
        in boundary
        for boundary in boundaries
    )

    assert any(
        "Large exact-score ties"
        in boundary
        for boundary in boundaries
    )

    assert any(
        "does not validate"
        in boundary
        for boundary in boundaries
    )

    assert any(
        "No universal plagiarism threshold"
        in boundary
        for boundary in boundaries
    )


def test_authentic_analysis_uses_canonical_lf():
    payload = SUMMARY.read_bytes()

    assert b"\r\n" not in payload
    assert payload.endswith(b"\n")
