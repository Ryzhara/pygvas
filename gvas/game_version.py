"""
Game version information for GVAS
Python port of game_version.rs

Key differences from Rust version:
- Uses Python enums instead of Rust enums
- Simplified version handling
"""

from enum import Enum, auto
from typing import Optional

# Magic number that appears at the start of every GVAS file
GVAS_MAGIC = b"GVAS"
PLZ_MAGIC = b"PlZ"  # not sure why RUST uses a null byte terminator


class CompressionType(Enum):
    """
    Compression types used in Palworld custom file format
    """

    # None
    NONE = 0x30
    # Zlib
    ZLIB = 0x31
    # Zlib twice
    ZLIB_TWICE = 0x32
    # Palworld specific compression type; NOT IMPLEMENTED
    PLZ = 0xFF


class GameVersion(Enum):
    """Supported game versions"""

    DEFAULT = 1
    PALWORLD = 2

    def get_compression_type(self) -> CompressionType:
        """Get the compression type for this game version"""
        if self == GameVersion.PALWORLD:
            return CompressionType.ZLIB_TWICE
        return CompressionType.NONE


class DeserializedGameVersion:
    """
    Holds information about the deserialized game version

    This is used to track what game version was used during deserialization,
    which may affect how the file is handled.
    """

    def __init__(self, version: GameVersion):
        self.version = version
        self._compression_type: Optional[CompressionType] = None

    @property
    def compression_type(self) -> CompressionType:
        """Get the compression type, defaulting to the game version's default"""
        if self._compression_type is None:
            return self.version.get_compression_type()
        return self._compression_type

    @compression_type.setter
    def compression_type(self, value: CompressionType):
        """Set a specific compression type"""
        self._compression_type = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeserializedGameVersion):
            return NotImplemented
        return (
            self.version == other.version
            and self._compression_type == other._compression_type
        )
