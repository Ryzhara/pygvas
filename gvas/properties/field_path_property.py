"""
FieldPath property implementation for GVAS
Python port of field_path_property.rs
"""

from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Dict, Any, BinaryIO, List
from .property_base import PropertyTrait
from ..utils import *


@dataclass
class FieldPath:
    path: list[str]
    resolved_owner: str

    def read(self, stream: BinaryIO):
        path_element_count: int = read_uint32(stream)
        self.path = []
        for _ in range(path_element_count):
            self.path.append(read_string(stream))
        self.resolved_owner = read_string(stream)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_uint32(stream, len(self.path))
        for path_element in self.path:
            bytes_written += write_string(stream, path_element)
        bytes_written += write_string(stream, self.resolved_owner)
        return bytes_written


@dataclass
class FieldPathProperty(PropertyTrait):
    """A property that holds an FieldPath value"""

    value: FieldPath

    @classmethod
    def new(cls, value: FieldPath) -> "FieldPathProperty":
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

        self.value = FieldPath(path=[], resolved_owner="")
        # Read value
        start = stream.tell()
        self.value.read(stream)
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
        body_bytes = self.value.write(temp_body_buffer)
        assert body_bytes == len(temp_body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "FieldPathProperty")
            bytes_written += write_uint32(stream, body_bytes)
            bytes_written += write_uint32(stream, 0)  # array_index
            # if there were strings, they'd go here
            bytes_written += write_uint8(stream, 0)  # terminator

        # Write enum value
        bytes_written += write_bytes(stream, temp_body_buffer.getvalue())

        return bytes_written
