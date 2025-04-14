"""
Game version information for GVAS
Python port of game_version.rs

Key differences from Rust version:
- Uses Python enums instead of Rust enums
- Simplified version handling
"""

from enum import Enum

# Magic number that appears at the start of every GVAS file
GVAS_MAGIC = b"GVAS"
PLZ_MAGIC = b"PlZ"  # not sure why RUST uses a null byte terminator


class CompressionType(Enum):
    """
    Compression types used in Palworld custom file format
    """

    UNKNOWN = 0x00
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

    UNKNOWN = 0
    DEFAULT = 1
    PALWORLD = 2
