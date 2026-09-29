import pytest

from behavclone.matching.similarity import (
    compare_fragments,
    longest_common_subsequence_length,
    sequence_similarity,
)


def test_lcs_identical_sequences():
    tokens = ("a", "b", "c")

    assert longest_common_subsequence_length(tokens, tokens) == 3


def test_lcs_handles_reordering():
    first = ("a", "b", "c")
    second = ("a", "c", "b")

    assert longest_common_subsequence_length(first, second) == 2


def test_sequence_similarity_identical_is_one():
    tokens = ("a", "b", "c")

    assert sequence_similarity(tokens, tokens) == 1.0


def test_sequence_similarity_is_symmetric():
    first = ("a", "b", "c")
    second = ("a", "c")

    assert sequence_similarity(first, second) == pytest.approx(
        sequence_similarity(second, first)
    )


def test_sequence_similarity_empty_cases():
    assert sequence_similarity((), ()) == 1.0
    assert sequence_similarity(("a",), ()) == 0.0
    assert sequence_similarity((), ("a",)) == 0.0


def test_identical_fragments_score_one():
    source = """
    int add(int left, int right) {
        return left + right;
    }
    """

    result = compare_fragments(source, source)

    assert result.raw == pytest.approx(1.0)
    assert result.normalized == pytest.approx(1.0)
    assert result.structural == pytest.approx(1.0)


def test_identifier_renaming_affects_raw_but_not_normalized():
    first = """
    int calculate(int price, int discount) {
        return price - discount;
    }
    """

    renamed = """
    int compute(int amount, int reduction) {
        return amount - reduction;
    }
    """

    result = compare_fragments(first, renamed)

    assert result.raw < 1.0
    assert result.normalized == pytest.approx(1.0)
    assert result.structural == pytest.approx(1.0)


def test_operator_change_reduces_normalized_similarity():
    subtract = """
    int calculate(int price, int discount) {
        return price - discount;
    }
    """

    add = """
    int calculate(int price, int discount) {
        return price + discount;
    }
    """

    result = compare_fragments(subtract, add)

    assert result.normalized < 1.0
    assert result.structural < 1.0


def test_extra_statement_reduces_similarity():
    first = """
    int calculate(int price, int discount) {
        return price - discount;
    }
    """

    second = """
    int calculate(int price, int discount) {
        int result = price - discount;
        return result;
    }
    """

    result = compare_fragments(first, second)

    assert result.raw < 1.0
    assert result.normalized < 1.0
    assert result.structural < 1.0
