from pathlib import Path

import tree_sitter_java as tsjava
from tree_sitter import Language, Node, Parser

from behavclone.fragments.models import MethodFragment

JAVA_LANGUAGE = Language(tsjava.language())


def create_java_parser() -> Parser:
    """Create a Tree-sitter parser configured for Java."""

    return Parser(JAVA_LANGUAGE)


def _node_text(node: Node, source: bytes) -> str:
    """Decode the source represented by one syntax-tree node."""

    return source[node.start_byte : node.end_byte].decode(
        "utf-8",
        errors="replace",
    )


def _fragment_name(node: Node, source: bytes) -> str:
    """Extract the declared method or constructor name."""

    name_node = node.child_by_field_name("name")

    if name_node is None:
        return "<anonymous>"

    return _node_text(name_node, source)


def extract_method_fragments(
    file_path: str | Path,
) -> list[MethodFragment]:
    """Extract complete methods and constructors from a Java file."""

    file_path = Path(file_path)
    source = file_path.read_bytes()

    parser = create_java_parser()
    tree = parser.parse(source)

    fragments: list[MethodFragment] = []
    stack = [tree.root_node]

    while stack:
        node = stack.pop()

        if node.type in {
            "method_declaration",
            "constructor_declaration",
        }:
            fragments.append(
                MethodFragment(
                    file_path=file_path,
                    kind=node.type,
                    name=_fragment_name(node, source),
                    start_line=node.start_point.row + 1,
                    end_line=node.end_point.row + 1,
                    source=_node_text(node, source),
                )
            )

        stack.extend(reversed(node.children))

    return sorted(
        fragments,
        key=lambda fragment: (
            fragment.start_line,
            fragment.end_line,
            fragment.name,
        ),
    )
