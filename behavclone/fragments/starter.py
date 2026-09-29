from collections.abc import Iterable
from pathlib import Path

import tree_sitter_java as tsjava
from tree_sitter import Language, Node, Parser

from behavclone.fragments.models import MethodFragment
from behavclone.parsing.java import extract_method_fragments

StarterSignature = tuple[str, ...]

JAVA_LANGUAGE = Language(tsjava.language())

IDENTIFIER_TYPES = {
    "identifier",
    "type_identifier",
}

COMMENT_TYPES = {
    "line_comment",
    "block_comment",
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


def starter_tokens(source_text: str) -> tuple[str, ...]:
    """Build a conservative token representation for starter exclusion.

    Identifier spelling is normalized so unchanged starter code remains
    recognizable after identifier renaming.

    Literal values, operators, keywords, and punctuation are preserved so
    modified logic is not discarded merely because it has the same broad
    normalized shape.
    """
    source = source_text.encode("utf-8")
    tree = _parser().parse(source)

    result: list[str] = []

    for node in _leaf_nodes(tree.root_node):
        if node.type in COMMENT_TYPES:
            continue

        if node.type in IDENTIFIER_TYPES:
            result.append("<ID>")
            continue

        result.append(_text(node, source))

    return tuple(result)


def fragment_signature(
    fragment: MethodFragment,
) -> StarterSignature:
    """Return the conservative starter signature of a fragment."""
    return starter_tokens(fragment.source)


def build_starter_signatures(
    starter_files: Iterable[Path],
) -> frozenset[StarterSignature]:
    """Build signatures for instructor-provided starter fragments."""
    signatures: set[StarterSignature] = set()

    for source_file in sorted(starter_files):
        for fragment in extract_method_fragments(source_file):
            signatures.add(fragment_signature(fragment))

    return frozenset(signatures)


def filter_starter_fragments(
    fragments: Iterable[MethodFragment],
    starter_signatures: frozenset[StarterSignature],
) -> list[MethodFragment]:
    """Remove fragments equivalent to instructor starter fragments.

    Equality is exact after identifier normalization. Literal values,
    operators, keywords, and punctuation must still match exactly.

    No fuzzy starter-code threshold is used.
    """
    if not starter_signatures:
        return list(fragments)

    return [
        fragment
        for fragment in fragments
        if fragment_signature(fragment) not in starter_signatures
    ]


def discover_starter_signatures(
    starter_root: str | Path | None,
) -> frozenset[StarterSignature]:
    """Discover Java starter files and build their fragment signatures.

    A missing, unset, or non-directory starter location contributes no
    exclusions.
    """
    if starter_root is None:
        return frozenset()

    root = Path(starter_root)

    if not root.is_dir():
        return frozenset()

    starter_files = sorted(
        path
        for path in root.rglob("*.java")
        if path.is_file()
    )

    return build_starter_signatures(starter_files)
