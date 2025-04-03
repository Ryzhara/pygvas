"""
Name property implementation for GVAS
Python port of name_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from dataclasses import dataclass
from io import BytesIO
from typing import Optional, BinaryIO
from .property_base import PropertyTrait, SerializationHints
from ..utils import *


@dataclass
class NameProperty(PropertyTrait):
    """A property that holds a name"""

    array_index: int = 0
    value: Optional[str] = None

    @classmethod
    def new(cls, value: Optional[str] = None, array_index: int = 0) -> "NameProperty":
        """Create a new name property"""
        return cls(array_index=array_index, value=value)

    @classmethod
    def from_str(cls, value: str) -> "NameProperty":
        """Create a name property from a string"""
        return cls.new(value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read name from stream"""
        length, start, end = 0, 0, 0
        if include_header:
            # Read length and array index
            length = read_uint32(stream)
            self.array_index = read_uint32(stream)  # actually use this for once?
            read_uint8(stream, 0)  # ensure null byte terminator

        # Record start position for length validation
        start = stream.tell()
        self.value = read_string(stream)
        end = stream.tell()

        if start and end and length:
            actual_size = end - start
            if actual_size != length:
                DeserializeError.invalid_value_size(length, actual_size, start)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write name to stream"""
        # Write to temporary buffer first to get length
        buffer = BytesIO()
        length = write_string(buffer, self.value)

        bytes_written = 0
        if include_header:
            bytes_written += write_string(stream, "NameProperty")
            bytes_written += write_uint32(stream, length)
            bytes_written += write_uint32(stream, self.array_index)
            bytes_written += write_uint8(stream, 0)

        bytes_written += write_bytes(stream, buffer.getvalue())

        return bytes_written
