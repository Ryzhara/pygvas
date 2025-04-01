"""
Object property implementation for GVAS
Python port of object_property.rs
"""

from dataclasses import dataclass
from io import BytesIO
from typing import Optional, BinaryIO
from .property_base import PropertyTrait
from ..utils import *


@dataclass
class ObjectProperty(PropertyTrait):
    """A property that holds an object value"""

    value: str = ""

    @classmethod
    def new(cls, value: str) -> "ObjectProperty":
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        length = 0
        if include_header:
            length = read_uint32(stream)
            _array_index = read_uint32(stream, 0)
            # if there were strings, they'd go here
            _terminator = read_uint8(stream, 0)

        # Read value
        start = stream.tell()
        self.value = read_string(stream)
        end = stream.tell()

        # Verify length
        if include_header:
            if end - start != length:
                raise DeserializeError.invalid_value_size(length, end - start, start)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write enum value to stream"""

        # create temporary buffer for body
        temp_body_buffer = BytesIO()
        body_bytes = write_string(temp_body_buffer, self.value)
        assert body_bytes == len(temp_body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "ObjectProperty")
            bytes_written += write_uint32(stream, body_bytes)
            bytes_written += write_uint32(stream, 0)  # array_index
            # if there were strings, they'd go here
            bytes_written += write_uint8(stream, 0)  # terminator

        # Write enum value
        bytes_written += write_bytes(stream, temp_body_buffer.getvalue())

        return bytes_written
