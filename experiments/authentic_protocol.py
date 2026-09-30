"""Predeclared protocol for authentic false-positive evaluation.

This protocol is frozen before authentic submissions are measured.

The experiment evaluates similarity surfacing among independently
produced solutions to a common assignment specification. It does not
infer plagiarism, authorship, intent, or academic misconduct.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticEvaluationProtocol:
    unit_of_analysis: str
    minimum_submissions: int
    language: str
    behavclone_matching_metric: str
    cohort_ngram_size: int
    structural_metrics: tuple[str, ...]
    cohort_fields: tuple[str, ...]
    behavioral_fields: tuple[str, ...]
    jplag_similarity_fields: tuple[str, ...]
    jplag_normalized: bool
    jplag_frequency_analysis: bool
    inclusion_requirements: tuple[str, ...]
    exclusion_requirements: tuple[str, ...]
    reporting_requirements: tuple[str, ...]
    prohibited_claims: tuple[str, ...]


AUTHENTIC_EVALUATION_PROTOCOL = AuthenticEvaluationProtocol(
    unit_of_analysis="complete_submission",
    minimum_submissions=10,
    language="java",
    behavclone_matching_metric="normalized",
    cohort_ngram_size=4,
    structural_metrics=(
        "mean_raw_similarity",
        "mean_normalized_similarity",
        "mean_structural_similarity",
    ),
    cohort_fields=(
        "shared_feature_count",
        "pair_specific_feature_count",
        "max_rarity",
        "mean_rarity",
    ),
    behavioral_fields=(
        "shared_failure_count",
        "identical_wrong_output_count",
        "max_failure_rarity",
        "max_wrong_output_rarity",
    ),
    jplag_similarity_fields=(
        "averageSimilarity",
        "maxSimilarity",
    ),
    jplag_normalized=False,
    jplag_frequency_analysis=False,
    inclusion_requirements=(
        "all submissions answer the same assignment specification",
        "each submission is analyzed as a complete submission",
        "submission identifiers are anonymized before repository use",
        "the provenance of the dataset is documented",
        "use of the submissions is ethically and legally permitted",
        "starter code is identified when the assignment provides it",
    ),
    exclusion_requirements=(
        "exclude personally identifying student information",
        "exclude submissions whose permission or provenance is unclear",
        "exclude generated duplicates created only to inflate cohort size",
        "exclude known copied pairs from the primary false-positive cohort",
    ),
    reporting_requirements=(
        "report cohort size and submission size characteristics",
        "report all pairwise BehavClone structural evidence",
        "report cohort-relative evidence separately",
        "report behavioral evidence only when common imported test results exist",
        "report JPlag results separately when the baseline can be run",
        "inspect highest-similarity independently produced pairs",
        "preserve unfavorable and null findings",
        "distinguish measurements from interpretation",
        "document missing evidence channels explicitly",
    ),
    prohibited_claims=(
        "plagiarism verdict",
        "authorship inference",
        "intent inference",
        "plagiarism detection accuracy from an unlabeled cohort",
        "general superiority over JPlag",
        "universal similarity threshold",
    ),
)
