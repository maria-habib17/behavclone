from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MethodFragment:
    """One method or constructor extracted from a Java source file.

    BehavClone v0.1 defines a structural fragment as a complete Java
    method_declaration or constructor_declaration.
    """

    file_path: Path
    kind: str
    name: str
    start_line: int
    end_line: int
    source: str

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1
