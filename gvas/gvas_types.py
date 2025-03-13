"""
Basic types for GVAS
Python port of types.rs

Key differences from Rust version:
- Uses Python's UUID for Guid implementation
- Simplified implementations using Python built-ins
"""

from dataclasses import dataclass
from typing import Dict, TypeVar, Generic
import uuid
import struct

K = TypeVar('K')
V = TypeVar('V')


class Guid:
    """
    Represents a GUID/UUID.
    Equivalent to Rust's Guid implementation but using Python's uuid module.
    """

    def __init__(self, value: uuid.UUID = None):
        self._value = value or uuid.UUID(int=0)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Guid':
        """Create a Guid from bytes in little-endian format"""
        # Unreal Engine uses different byte order than Python's UUID
        # Need to reorder bytes to match UE format
        b = bytearray(data)
        b[0:4] = reversed(b[0:4])
        b[4:6] = reversed(b[4:6])
        b[6:8] = reversed(b[6:8])
        return cls(uuid.UUID(bytes=bytes(b)))

    def to_bytes(self) -> bytes:
        """Convert to bytes in little-endian format"""
        # Reverse the byte order again for UE format
        b = bytearray(self._value.bytes)
        b[0:4] = reversed(b[0:4])
        b[4:6] = reversed(b[4:6])
        b[6:8] = reversed(b[6:8])
        return bytes(b)

    def is_zero(self) -> bool:
        """Check if this is a zero GUID"""
        return self._value.int == 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Guid):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"Guid({self._value})"


class HashableIndexMap(Dict[K, V]):
    """
    A dictionary that maintains insertion order and can be hashed.
    Python equivalent of Rust's HashableIndexMap.
    """

    def __hash__(self) -> int:
        # Hash based on sorted items to ensure consistent hash values
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashableIndexMap):
            return NotImplemented
        return dict(self) == dict(other)
