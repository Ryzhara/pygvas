"""
Basic types for GVAS
Python port of types.rs
"""

from pydantic.dataclasses import dataclass
from typing import Dict, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class HashableIndexMap(Dict[K, V]):
    """
    A dictionary that maintains insertion order and can be hashed.
    Python equivalent of Rust's HashableIndexMap.
    """

    def __hash__(self) -> int:
        # Hash based on sorted items to ensure consistent hash values
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, "HashableIndexMap"):
            return NotImplemented
        return dict(self) == dict(other)
