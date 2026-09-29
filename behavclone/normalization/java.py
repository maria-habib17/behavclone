import tree_sitter_java as tsjava
from tree_sitter import Language, Node, Parser

from behavclone.normalization.models import FragmentRepresentation

JAVA_LANGUAGE = Language(tsjava.language())

IDENTIFIER_TYPES = {
    "identifier",
    "type_identifier",
}

LITERAL_TYPES = {
    "decimal_integer_literal": "<INT>",
    "hex_integer_literal": "<INT>",
    "octal_integer_literal": "<INT>",
    "binary_integer_literal": "<INT>",
    "decimal_floating_point_literal": "<FLOAT>",
    "hex_floating_point_literal": "<FLOAT>",
    "string_literal": "<STRING>",
    "character_literal": "<CHAR>",
}


def _parser() -> Parser:
    return Parser(JAVA_LANGUAGE)


def _text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode(
        "utf-8",
        errors="replace",
    )


def _leaf_nodes(node: Node) -> list[Node]:
    """Return syntax-tree leaves in source order."""

    if node.child_count == 0:
        return [node]

    leaves: list[Node] = []

    for child in node.children:
        leaves.extend(_leaf_nodes(child))

    return leaves


def lexical_tokens(source_text: str) -> tuple[str, ...]:
    """Return concrete Java leaf tokens, excluding comments."""

    source = source_text.encode("utf-8")
    tree = _parser().parse(source)

    return tuple(
        _text(node, source)
        for node in _leaf_nodes(tree.root_node)
        if node.type not in {
            "line_comment",
            "block_comment",
        }
    )


def normalized_tokens(source_text: str) -> tuple[str, ...]:
    """Normalize identifiers and literals while preserving syntax."""

    source = source_text.encode("utf-8")
    tree = _parser().parse(source)

    result: list[str] = []

    for node in _leaf_nodes(tree.root_node):
        if node.type in {
            "line_comment",
            "block_comment",
        }:
            continue

        if node.type in IDENTIFIER_TYPES:
            result.append("<ID>")
            continue

        if node.type in LITERAL_TYPES:
            result.append(LITERAL_TYPES[node.type])
            continue

        result.append(_text(node, source))

    return tuple(result)


def structural_tokens(source_text: str) -> tuple[str, ...]:
    """Represent syntax using named Tree-sitter node types.

    Identifier spelling is deliberately absent from this representation.
    Operators remain represented by their concrete symbols.
    """

    source = source_text.encode("utf-8")
    tree = _parser().parse(source)

    result: list[str] = []

    def visit(node: Node) -> None:
        if node.type in {
            "line_comment",
            "block_comment",
        }:
            return

        if node.is_named:
            if node.type in IDENTIFIER_TYPES:
                result.append("identifier")
            elif node.type in LITERAL_TYPES:
                result.append("literal")
            else:
                result.append(node.type)

        elif node.child_count == 0:
            result.append(_text(node, source))

        for child in node.children:
            visit(child)

    visit(tree.root_node)

    return tuple(result)


def represent_fragment(
    source_text: str,
) -> FragmentRepresentation:
    """Build all currently supported representations."""

    return FragmentRepresentation(
        raw_tokens=lexical_tokens(source_text),
        normalized_tokens=normalized_tokens(source_text),
        structural_tokens=structural_tokens(source_text),
    )
