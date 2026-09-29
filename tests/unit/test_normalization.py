from behavclone.normalization.java import represent_fragment

FIRST = """
int calculate(int price, int discount) {
    int result = price - discount;

    if (result < 0) {
        return 0;
    }

    return result;
}
"""


RENAMED = """
int compute(int amount, int reduction) {
    int finalValue = amount - reduction;

    if (finalValue < 0) {
        return 0;
    }

    return finalValue;
}
"""


DIFFERENT_OPERATOR = """
int calculate(int price, int discount) {
    int result = price + discount;

    if (result < 0) {
        return 0;
    }

    return result;
}
"""


def test_raw_tokens_preserve_identifier_differences():
    first = represent_fragment(FIRST)
    renamed = represent_fragment(RENAMED)

    assert first.raw_tokens != renamed.raw_tokens

    assert "calculate" in first.raw_tokens
    assert "compute" in renamed.raw_tokens


def test_identifier_renaming_normalizes_equivalently():
    first = represent_fragment(FIRST)
    renamed = represent_fragment(RENAMED)

    assert first.normalized_tokens == renamed.normalized_tokens


def test_structural_representation_ignores_identifier_spelling():
    first = represent_fragment(FIRST)
    renamed = represent_fragment(RENAMED)

    assert first.structural_tokens == renamed.structural_tokens


def test_normalization_preserves_operator_difference():
    first = represent_fragment(FIRST)
    changed = represent_fragment(DIFFERENT_OPERATOR)

    assert first.normalized_tokens != changed.normalized_tokens
    assert "-" in first.normalized_tokens
    assert "+" in changed.normalized_tokens


def test_structural_representation_preserves_operator_difference():
    first = represent_fragment(FIRST)
    changed = represent_fragment(DIFFERENT_OPERATOR)

    assert first.structural_tokens != changed.structural_tokens
    assert "-" in first.structural_tokens
    assert "+" in changed.structural_tokens


def test_comments_do_not_change_normalized_representation():
    without_comment = """
    int add(int left, int right) {
        return left + right;
    }
    """

    with_comment = """
    int add(int left, int right) {
        // Add the two values.
        return left + right;
    }
    """

    first = represent_fragment(without_comment)
    second = represent_fragment(with_comment)

    assert first.normalized_tokens == second.normalized_tokens


def test_literal_values_are_normalized():
    first = represent_fragment(
        """
        int threshold() {
            return 10;
        }
        """
    )

    second = represent_fragment(
        """
        int threshold() {
            return 500;
        }
        """
    )

    assert first.raw_tokens != second.raw_tokens
    assert first.normalized_tokens == second.normalized_tokens
