import math
from collections import Counter
from collections.abc import Iterable, Sequence

from behavclone.cohort.models import (
    CohortFeatureEvidence,
    CohortProfile,
    TokenNgram,
)
from behavclone.fragments.models import MethodFragment
from behavclone.normalization.java import normalized_tokens


def token_ngrams(
    tokens: Sequence[str],
    n: int,
) -> frozenset[TokenNgram]:
    """Return distinct contiguous token n-grams.

    Features are returned as a set because cohort frequency is measured
    per submission, not by the number of repeated occurrences within one
    submission.
    """
    if n <= 0:
        raise ValueError("n must be greater than zero.")

    if len(tokens) < n:
        return frozenset()

    return frozenset(
        tuple(tokens[index : index + n])
        for index in range(len(tokens) - n + 1)
    )


def fragment_features(
    fragment: MethodFragment,
    n: int,
) -> frozenset[TokenNgram]:
    """Extract normalized token n-grams from one method fragment."""
    return token_ngrams(
        normalized_tokens(fragment.source),
        n,
    )


def submission_features(
    fragments: Iterable[MethodFragment],
    n: int,
) -> frozenset[TokenNgram]:
    """Return distinct normalized features appearing in one submission."""
    features: set[TokenNgram] = set()

    for fragment in fragments:
        features.update(
            fragment_features(fragment, n)
        )

    return frozenset(features)


def build_cohort_profile(
    submissions: Iterable[Iterable[MethodFragment]],
    n: int,
) -> CohortProfile:
    """Build submission-level document frequencies for a cohort."""
    if n <= 0:
        raise ValueError("n must be greater than zero.")

    frequencies: Counter[TokenNgram] = Counter()
    cohort_size = 0

    for fragments in submissions:
        cohort_size += 1

        for feature in submission_features(fragments, n):
            frequencies[feature] += 1

    return CohortProfile(
        cohort_size=cohort_size,
        ngram_size=n,
        document_frequencies=dict(frequencies),
    )


def feature_rarity(
    profile: CohortProfile,
    feature: TokenNgram,
) -> CohortFeatureEvidence:
    """Return smoothed inverse-document-frequency evidence."""
    document_frequency = profile.document_frequencies.get(
        feature,
        0,
    )

    rarity = math.log(
        (profile.cohort_size + 1)
        / (document_frequency + 1)
    ) + 1.0

    return CohortFeatureEvidence(
        feature=feature,
        document_frequency=document_frequency,
        cohort_size=profile.cohort_size,
        rarity=rarity,
    )


def shared_feature_evidence(
    left: MethodFragment,
    right: MethodFragment,
    profile: CohortProfile,
) -> tuple[CohortFeatureEvidence, ...]:
    """Return cohort evidence for normalized features shared by a pair."""
    left_features = fragment_features(
        left,
        profile.ngram_size,
    )
    right_features = fragment_features(
        right,
        profile.ngram_size,
    )

    shared = left_features & right_features

    evidence = [
        feature_rarity(profile, feature)
        for feature in shared
    ]

    return tuple(
        sorted(
            evidence,
            key=lambda item: (
                -item.rarity,
                item.feature,
            ),
        )
    )
