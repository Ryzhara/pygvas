"""
Map property implementation for GVAS
Python port of map_property.rs

Key differences from Rust version:
- Uses Python's dict instead of HashMap
- Simplified type handling
"""

from dataclasses import dataclass
from io import BytesIO
from typing import Dict, Optional, BinaryIO, Any
import struct

from .property_base import Property, PropertyTrait, SerializationHints
from ..error import *
from ..gvas_types import HashableIndexMap
from ..utils import *


@dataclass
class MapProperty(PropertyTrait):
    """A property that holds a key-value mapping"""

    key_type: str = ""
    value_type: str = ""
    allocation_flags: int = 0
    values: HashableIndexMap | None = None

    def __post_init__(self):
        if self.values is None:
            self.values = HashableIndexMap()

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
        # END OF HEADER FOR MAP PROPERTY
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
            key_prop = Property.new(stream, self.key_type, include_header=False)
            value_prop = Property.new(stream, self.value_type, include_header=False)
            self.values[key_prop] = value_prop

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write map to stream"""

        buffer = BytesIO()
        buffer_bytes_written = 0
        length_location = 0
        if include_header:
            # START OF HEADER
            buffer_bytes_written += write_string(buffer, "MapProperty")
            length_location = buffer.tell()
            buffer_bytes_written += write_uint32(buffer, 0)  # placeholder value
            buffer_bytes_written += write_uint32(buffer, 0)  # zero value array_index
            buffer_bytes_written += write_string(buffer, self.key_type)
            buffer_bytes_written += write_string(buffer, self.value_type)
            buffer_bytes_written += write_uint8(buffer, 0)  # null byte terminator

        # START OF BODY
        start = buffer.tell()
        buffer_bytes_written += write_uint32(buffer, self.allocation_flags)
        element_count = len(self.values.keys())
        buffer_bytes_written += write_uint32(buffer, element_count)

        # Write entries
        for key, value in self.values.items():

            key_prop = Property(self.key_type, key)
            buffer_bytes_written += key_prop.write(buffer, include_header=False)

            # Write value
            value_prop = Property(self.value_type, value)
            buffer_bytes_written += value_prop.write(buffer, include_header=False)
        end = buffer.tell()

        if include_header:
            buffer.seek(length_location)
            total_bytes_written = end - start
            write_uint32(buffer, total_bytes_written)

        # now write the temp buffer to the stream
        return write_bytes(stream, buffer.getvalue())
