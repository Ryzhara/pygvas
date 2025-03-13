"""
Game version information for GVAS
Python port of game_version.rs

Key differences from Rust version:
- Uses Python enums instead of Rust enums
- Simplified version handling
"""

from enum import Enum, auto
from typing import Optional

# Magic number for PLZ compression
PLZ_MAGIC = b'PLZ\x00'

class PalworldCompressionType(Enum):
    """Compression types used in Palworld saves"""
    NONE = 0
    ZLIB = 1
    PLZ = 2

class GameVersion(Enum):
    """Supported game versions"""
    Default = auto()
    Palworld = auto()
    
    def get_compression_type(self) -> PalworldCompressionType:
        """Get the compression type for this game version"""
        if self == GameVersion.Palworld:
            return PalworldCompressionType.PLZ
        return PalworldCompressionType.ZLIB

class DeserializedGameVersion:
    """
    Holds information about the deserialized game version
    
    This is used to track what game version was used during deserialization,
    which may affect how the file is handled.
    """
    
    def __init__(self, version: GameVersion):
        self.version = version
        self._compression_type: Optional[PalworldCompressionType] = None
        
    @property
    def compression_type(self) -> PalworldCompressionType:
        """Get the compression type, defaulting to the game version's default"""
        if self._compression_type is None:
            return self.version.get_compression_type()
        return self._compression_type
    
    @compression_type.setter 
    def compression_type(self, value: PalworldCompressionType):
        """Set a specific compression type"""
        self._compression_type = value
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeserializedGameVersion):
            return NotImplemented
        return (self.version == other.version and 
                self._compression_type == other._compression_type) 