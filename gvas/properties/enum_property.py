"""
Enum property implementation for GVAS
Python port of enum_property.rs
"""

from dataclasses import dataclass
from typing import Optional, BinaryIO
import struct

from .property_base import PropertyTrait, SerializationHints
from ..error import DeserializeError
from ..utils import read_string, write_string


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
        if include_header:
            # Read length and array index
            length = struct.unpack("<I", stream.read(4))[0]
            array_index = struct.unpack("<I", stream.read(4))[0]
            if array_index != 0:
                position = stream.tell() - 4
                raise DeserializeError.invalid_array_index(array_index, position)

            # Read enum type type_name if present
            self.enum_type = read_string(stream)

            # Read terminator
            terminator = stream.read(1)[0]
            if terminator != 0:
                position = stream.tell() - 1
                raise DeserializeError.invalid_terminator(terminator, position)

            # Read value
            start = stream.tell()
            self.value = read_string(stream)
            end = stream.tell()

            # Verify length
            if end - start != length:
                raise DeserializeError.invalid_value_size(length, end - start, start)
        else:
            # Just read the value when not reading header
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write enum value to stream"""
        bytes_written = 0

        if include_header:
            # First write to a temporary buffer to get the length
            value_bytes = (self.value + "\0").encode("utf-8")
            value_len_bytes = struct.pack("<I", len(value_bytes))
            value_size = len(value_len_bytes) + len(value_bytes)

            # Write length and array index
            stream.write(struct.pack("<I", value_size))
            stream.write(struct.pack("<I", 0))  # array_index
            bytes_written += 8

            # Write enum type type_name if present
            if self.enum_type:
                bytes_written += write_string(stream, self.enum_type)
            else:
                stream.write(struct.pack("<I", 0))
                bytes_written += 4

            # Write terminator
            stream.write(b"\0")
            bytes_written += 1

        # Write enum value
        bytes_written += write_string(stream, self.value)

        return bytes_written
