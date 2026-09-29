from pathlib import Path

from behavclone.fragments.models import MethodFragment
from behavclone.fragments.starter import (
    StarterSignature,
    filter_starter_fragments,
)
from behavclone.matching.assignment import maximum_weight_assignment
from behavclone.matching.models import (
    FragmentSimilarity,
    SubmissionComparison,
    SubmissionFragmentMatch,
)
from behavclone.matching.similarity import compare_fragments
from behavclone.parsing.java import extract_method_fragments


def extract_submission_fragments(
    source_files: list[Path],
    starter_signatures: frozenset[StarterSignature] | None = None,
) -> list[MethodFragment]:
    """Extract comparable fragments from every Java file in a submission.

    File names and class names do not define correspondence. They are
    retained only as evidence metadata.

    When starter signatures are supplied, fragments with an equal
    conservative starter signature are excluded before matching.
    """
    fragments: list[MethodFragment] = []

    for source_file in sorted(source_files):
        fragments.extend(
            extract_method_fragments(source_file)
        )

    if starter_signatures is None:
        return fragments

    return filter_starter_fragments(
        fragments,
        starter_signatures,
    )


def build_similarity_matrix(
    left: list[MethodFragment],
    right: list[MethodFragment],
) -> tuple[
    list[list[float]],
    list[list[FragmentSimilarity]],
]:
    """Build all-pairs normalized similarity evidence."""
    score_matrix: list[list[float]] = []
    evidence_matrix: list[list[FragmentSimilarity]] = []

    for left_fragment in left:
        score_row: list[float] = []
        evidence_row: list[FragmentSimilarity] = []

        for right_fragment in right:
            similarity = compare_fragments(
                left_fragment.source,
                right_fragment.source,
            )

            score_row.append(similarity.normalized)
            evidence_row.append(similarity)

        score_matrix.append(score_row)
        evidence_matrix.append(evidence_row)

    return score_matrix, evidence_matrix


def compare_submissions(
    left_files: list[Path],
    right_files: list[Path],
    starter_signatures: frozenset[StarterSignature] | None = None,
) -> SubmissionComparison:
    """Compare two submissions without positional file/method matching."""
    left = extract_submission_fragments(
        left_files,
        starter_signatures,
    )
    right = extract_submission_fragments(
        right_files,
        starter_signatures,
    )

    if not left or not right:
        return SubmissionComparison(
            left_fragment_count=len(left),
            right_fragment_count=len(right),
            matches=(),
        )

    score_matrix, evidence_matrix = build_similarity_matrix(
        left,
        right,
    )

    assignment = maximum_weight_assignment(score_matrix)

    matches = tuple(
        SubmissionFragmentMatch(
            left_file=left[match.left_index].file_path,
            left_name=left[match.left_index].name,
            left_start_line=left[match.left_index].start_line,
            right_file=right[match.right_index].file_path,
            right_name=right[match.right_index].name,
            right_start_line=right[match.right_index].start_line,
            similarity=evidence_matrix[
                match.left_index
            ][
                match.right_index
            ],
        )
        for match in assignment.matches
    )

    return SubmissionComparison(
        left_fragment_count=len(left),
        right_fragment_count=len(right),
        matches=matches,
    )


def compare_assignment_submissions(
    left_files: list[Path],
    right_files: list[Path],
    starter_files: list[Path],
) -> SubmissionComparison:
    """Compare submissions after excluding configured starter fragments."""
    from behavclone.fragments.starter import build_starter_signatures

    starter_signatures = build_starter_signatures(
        starter_files
    )

    return compare_submissions(
        left_files,
        right_files,
        starter_signatures=starter_signatures,
    )
