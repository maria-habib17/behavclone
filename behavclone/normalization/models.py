from dataclasses import dataclass


@dataclass(frozen=True)
class FragmentRepresentation:
    """Multiple representations of one Java fragment.

    Keeping representations separate allows BehavClone experiments to
    measure the contribution of each normalization strategy.
    """

    raw_tokens: tuple[str, ...]
    normalized_tokens: tuple[str, ...]
    structural_tokens: tuple[str, ...]
