"""
Basic types for GVAS
Python port of types.rs

This is currently unused, as the Python dictionary preserves order already.

Also, for MapProperty, I created tuples of (key, value) to avoid complexity of
trying to boil things down to immutable types and then reverse that.
"""

"""
from pydantic.dataclasses import dataclass
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")

@dataclass
class HashableIndexMap(dict[K, V]):
    # A dictionary that maintains insertion order and can be hashed.
    # Python equivalent of Rust's HashableIndexMap.


    def __hash__(self) -> int:
        # Hash based on sorted items to ensure consistent hash values
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, "HashableIndexMap"):
            return NotImplemented
        return dict(self) == dict(other)
"""
# ==================================================================
""" And maybe we really want something more like this?

This allows for a non-nested dictionary as a key, but I think we have 
too much nesting in StructProperty to make this worthwhile.

class DictKeyDict:
    def __init__(self):
        self._store = {}

    def _freeze(self, key):
        if isinstance(key, dict):
            try:
                # Convert dict to a frozenset of sorted items for consistent ordering
                return frozenset(sorted(key.items()))
            except TypeError:
                raise TypeError(f"Unhashable items in dict key: {key}")
        raise TypeError(f"Unsupported key type: {type(key).__name__}")

    def __setitem__(self, key, value):
        frozen_key = self._freeze(key)
        self._store[frozen_key] = value

    def __getitem__(self, key):
        frozen_key = self._freeze(key)
        return self._store[frozen_key]

    def __delitem__(self, key):
        frozen_key = self._freeze(key)
        del self._store[frozen_key]

    def __contains__(self, key):
        return self._freeze(key) in self._store

    def items(self):
        return self._store.items()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._store})"

"""
