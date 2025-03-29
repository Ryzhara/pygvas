"""
Enum property implementation for GVAS
Python port of enum_property.rs
"""

from dataclasses import dataclass
from io import BytesIO
from typing import Optional, BinaryIO
from .property_base import PropertyTrait
from ..utils import *


@dataclass
class EnumProperty(PropertyTrait):
    """A property that holds an enumeration value"""

    enum_type: Optional[str] = None
    value: str = ""

    @classmethod
    def new(cls, enum_type: Optional[str], value: str) -> "EnumProperty":
        """Create a new enum property"""
        return cls(enum_type=enum_type, value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read enum value from stream"""
        length = 0
        if include_header:
            # Read length and array index
            length = read_uint32(stream)
            _array_index = read_uint32(stream, 0)
            self.enum_type = read_string(stream)
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

        temp_body_buffer = BytesIO()
        body_bytes = write_string(temp_body_buffer, self.value)

        bytes_written = 0
        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "EnumProperty")

            # Write length and array index
            bytes_written += write_uint32(stream, body_bytes)
            bytes_written += write_uint32(stream, 0)  # array_index
            bytes_written += write_string(
                stream, self.enum_type
            )  # write_string handles ""

        # Write enum value
        bytes_written += write_string(stream, self.value)

        return bytes_written
