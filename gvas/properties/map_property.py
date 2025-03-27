"""
Map property implementation for GVAS
Python port of map_property.rs

Key differences from Rust version:
- Uses Python's dict instead of HashMap
- Simplified type handling
"""

from dataclasses import dataclass
from typing import Dict, Optional, BinaryIO, Any
import struct

from .property_base import Property, PropertyTrait, SerializationHints
from ..error import *
from ..utils import *


@dataclass
class MapProperty(PropertyTrait):
    """A property that holds a key-value mapping"""

    key_type: str = ""
    value_type: str = ""
    allocation_flags: int = 0
    values: Dict[Any, Any] = None

    def __post_init__(self):
        if self.values is None:
            self.values = {}

    @classmethod
    def new(cls, key_type: str, value_type: str) -> "MapProperty":
        """Create a new map property"""
        return cls(key_type=key_type, value_type=value_type)

    def read_header(self, stream: BinaryIO) -> (int, str):
        # Read length and array index
        length = read_uint32(stream)
        _array_index = read_uint32(stream, 0)
        self.key_type = read_string(stream)
        self.value_type = read_string(stream)
        _header_terminator = read_uint8(stream, 0)

        # END OF HEADER FOR ARRAY PROPERTY
        return length

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read map from stream"""

        if include_header:
            content_length = self.read_header(stream)

        # Read number of entries
        self.allocation_flags = read_uint32(stream)
        element_count = read_uint32(stream)

        # Read entries
        self.values = {}
        for _ in range(element_count):
            # Read key
            key_prop = Property.new(stream, self.key_type, include_header=False)

            # Read value
            value_prop = Property.new(stream, self.value_type, include_header=False)

            self.values[key_prop.value.value] = value_prop.value.value

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write map to stream"""
        bytes_written = 0

        # Write key type
        bytes_written += write_string(stream, self.key_type)

        # Write value type
        bytes_written += write_string(stream, self.value_type)

        # Write number of entries
        stream.write(struct.pack("<I", len(self.values)))
        bytes_written += 4

        # Write entries
        for key, value in self.values.items():
            # Write key
            key_prop = Property(self.key_type, key)
            bytes_written += key_prop.write(stream)

            # Write value
            value_prop = Property(self.value_type, value)
            bytes_written += value_prop.write(stream)

        return bytes_written
