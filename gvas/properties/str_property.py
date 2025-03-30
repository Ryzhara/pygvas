"""
String property implementations for GVAS
Python port of str_property.rs and name_property.rs

Contains implementations for:
- StrProperty
- NameProperty
"""

from dataclasses import dataclass
from typing import Optional, BinaryIO
import struct
from io import BytesIO

from .property_base import PropertyTrait, SerializationHints
from ..error import DeserializeError
from ..utils import *


@dataclass
class StrProperty(PropertyTrait):
    """A property that holds a string value"""

    value: Optional[str] = None

    @classmethod
    def new(cls, value: Optional[str] = None) -> "StrProperty":
        """Create a new string property"""
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read string from stream"""
        length = 0
        if include_header:
            length = read_uint32(stream)
            _array_index = read_uint32(stream, 0)
            read_null_byte_terminator(stream)

        # Record start position for length validation
        start = stream.tell()
        self.value = read_string(stream)
        end = stream.tell()

        # Validate length if header was included
        if include_header:
            assert (
                end - start == length
            ), f"Invalid string size: {end-start} != {length}"

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write string to stream"""
        bytes_written = 0

        # Write to temporary buffer first to get length
        buffer = BytesIO()
        content_length = (
            write_string(buffer, self.value)
            if self.value is not None
            else write_uint32(buffer, 0)
        )

        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "StrProperty")

            # Write length and array index
            bytes_written += write_uint32(stream, content_length)
            bytes_written += write_uint32(stream, 0)  # Array index
            bytes_written += write_uint8(stream, 0)  # null byte terminator

        # Write buffer contents
        bytes_written += stream.write(buffer.getvalue())

        return bytes_written
