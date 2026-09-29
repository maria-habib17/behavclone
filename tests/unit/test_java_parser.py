from pathlib import Path

from behavclone.parsing.java import extract_method_fragments


def write_java(
    tmp_path: Path,
    filename: str,
    source: str,
) -> Path:
    path = tmp_path / filename
    path.write_text(source, encoding="utf-8")
    return path


def test_extracts_method(tmp_path):
    path = write_java(
        tmp_path,
        "Calculator.java",
        """
        class Calculator {
            int add(int a, int b) {
                return a + b;
            }
        }
        """,
    )

    fragments = extract_method_fragments(path)

    assert len(fragments) == 1
    assert fragments[0].kind == "method_declaration"
    assert fragments[0].name == "add"
    assert "return a + b;" in fragments[0].source


def test_extracts_constructor_and_method(tmp_path):
    path = write_java(
        tmp_path,
        "Account.java",
        """
        class Account {
            Account() {
            }

            int balance() {
                return 0;
            }
        }
        """,
    )

    fragments = extract_method_fragments(path)

    assert {
        (fragment.kind, fragment.name)
        for fragment in fragments
    } == {
        ("constructor_declaration", "Account"),
        ("method_declaration", "balance"),
    }


def test_extracts_multiple_methods(tmp_path):
    path = write_java(
        tmp_path,
        "MathService.java",
        """
        class MathService {
            int add(int a, int b) {
                return a + b;
            }

            int subtract(int a, int b) {
                return a - b;
            }

            int multiply(int a, int b) {
                return a * b;
            }
        }
        """,
    )

    fragments = extract_method_fragments(path)

    assert [fragment.name for fragment in fragments] == [
        "add",
        "subtract",
        "multiply",
    ]


def test_extracts_methods_from_nested_classes(tmp_path):
    path = write_java(
        tmp_path,
        "Outer.java",
        """
        class Outer {
            void outerMethod() {
            }

            class Inner {
                void innerMethod() {
                }
            }
        }
        """,
    )

    fragments = extract_method_fragments(path)

    assert {
        fragment.name
        for fragment in fragments
    } == {
        "outerMethod",
        "innerMethod",
    }


def test_different_filenames_and_names_are_supported(tmp_path):
    first = write_java(
        tmp_path,
        "Calculator.java",
        """
        class Calculator {
            int calculate(int price, int discount) {
                return price - discount;
            }
        }
        """,
    )

    second = write_java(
        tmp_path,
        "PricingEngine.java",
        """
        class PricingEngine {
            int compute(int amount, int reduction) {
                return amount - reduction;
            }
        }
        """,
    )

    first_fragments = extract_method_fragments(first)
    second_fragments = extract_method_fragments(second)

    assert len(first_fragments) == 1
    assert len(second_fragments) == 1

    assert first_fragments[0].name == "calculate"
    assert second_fragments[0].name == "compute"


def test_extraction_preserves_method_order(tmp_path):
    path = write_java(
        tmp_path,
        "First.java",
        """
        class First {
            int add(int a, int b) {
                return a + b;
            }

            int subtract(int a, int b) {
                return a - b;
            }
        }
        """,
    )

    fragments = extract_method_fragments(path)

    assert [fragment.name for fragment in fragments] == [
        "add",
        "subtract",
    ]


def test_permuted_methods_are_still_all_extracted(tmp_path):
    first = write_java(
        tmp_path,
        "First.java",
        """
        class First {
            int add(int a, int b) {
                return a + b;
            }

            int subtract(int a, int b) {
                return a - b;
            }
        }
        """,
    )

    second = write_java(
        tmp_path,
        "Second.java",
        """
        class Second {
            int subtract(int a, int b) {
                return a - b;
            }

            int add(int a, int b) {
                return a + b;
            }
        }
        """,
    )

    first_names = [
        fragment.name
        for fragment in extract_method_fragments(first)
    ]

    second_names = [
        fragment.name
        for fragment in extract_method_fragments(second)
    ]

    assert first_names == ["add", "subtract"]
    assert second_names == ["subtract", "add"]
    assert set(first_names) == set(second_names)
