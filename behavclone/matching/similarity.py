from collections.abc import Sequence

from behavclone.matching.models import FragmentSimilarity
from behavclone.normalization.java import represent_fragment


def longest_common_subsequence_length(
    first: Sequence[str],
    second: Sequence[str],
) -> int:
    """Return the length of the longest common subsequence."""

    if len(first) < len(second):
        shorter = first
        longer = second
    else:
        shorter = second
        longer = first

    previous = [0] * (len(shorter) + 1)

    for longer_token in longer:
        current = [0]

        for index, shorter_token in enumerate(shorter, start=1):
            if longer_token == shorter_token:
                current.append(previous[index - 1] + 1)
            else:
                current.append(
                    max(
                        previous[index],
                        current[index - 1],
                    )
                )

        previous = current

    return previous[-1]


def sequence_similarity(
    first: Sequence[str],
    second: Sequence[str],
) -> float:
    """Return symmetric LCS similarity in the range [0, 1].

    Similarity is:

        2 * LCS(A, B) / (len(A) + len(B))

    Both empty sequences are treated as identical.
    """

    if not first and not second:
        return 1.0

    if not first or not second:
        return 0.0

    lcs = longest_common_subsequence_length(first, second)

    return (2.0 * lcs) / (len(first) + len(second))


def compare_fragments(
    first_source: str,
    second_source: str,
) -> FragmentSimilarity:
    """Compare two Java fragments across all representations."""

    first = represent_fragment(first_source)
    second = represent_fragment(second_source)

    return FragmentSimilarity(
        raw=sequence_similarity(
            first.raw_tokens,
            second.raw_tokens,
        ),
        normalized=sequence_similarity(
            first.normalized_tokens,
            second.normalized_tokens,
        ),
        structural=sequence_similarity(
            first.structural_tokens,
            second.structural_tokens,
        ),
    )
