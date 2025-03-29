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


#
# @dataclass
# class NameProperty(PropertyTrait):
#     """A property that holds a type_name value with an array index"""
#
#     value: Optional[str] = None
#     array_index: int = 0
#
#     @classmethod
#     def from_str(cls, value: Optional[str]) -> "NameProperty":
#         """Create a NameProperty from a string"""
#         return cls(value=value)
#
#     def read(
#         self,
#         stream: BinaryIO,
#         include_header: bool = True,
#     ) -> None:
#         """Read type_name value from stream"""
#         if include_header:
#             # Read length and array index
#             length = struct.unpack("<I", stream.read(4))[0]
#             array_index = struct.unpack("<I", stream.read(4))[0]
#             if array_index != 0:
#                 position = stream.tell() - 4
#                 raise DeserializeError.invalid_array_index(array_index, position)
#
#             # Read terminator
#             terminator = stream.read(1)[0]
#             if terminator != 0:
#                 position = stream.tell() - 1
#                 raise DeserializeError.invalid_terminator(terminator, position)
#
#             # Record start position for length validation
#             start = stream.tell()
#
#         # Read string value and array index
#         str_len = struct.unpack("<I", stream.read(4))[0]
#         self.value = stream.read(str_len).decode("utf-8")[:-1] if str_len > 0 else None
#         self.array_index = struct.unpack("<I", stream.read(4))[0]
#
#         # Validate length if header was included
#         if include_header:
#             end = stream.tell()
#             actual_size = end - start
#             if actual_size != length:
#                 raise DeserializeError.invalid_value_size(length, actual_size, start)
#
#     def write(
#         self,
#         stream: BinaryIO,
#         include_header: bool = True,
#     ) -> int:
#         """Write type_name value to stream"""
#         bytes_written = 0
#
#         if include_header:
#             # Write to temporary buffer first to get length
#             buffer = BytesIO()
#             buffer_bytes = 0
#
#             # Write string value and array index
#             if self.value is not None:
#                 str_bytes = (self.value + "\0").encode("utf-8")
#                 buffer.write(struct.pack("<I", len(str_bytes)))
#                 buffer.write(str_bytes)
#                 buffer_bytes += 4 + len(str_bytes)
#             else:
#                 buffer.write(struct.pack("<I", 0))
#                 buffer_bytes += 4
#
#             buffer.write(struct.pack("<I", self.array_index))
#             buffer_bytes += 4
#
#             # Write length and array index
#             stream.write(struct.pack("<I", buffer_bytes))  # Total length
#             stream.write(struct.pack("<I", 0))  # Array index
#             bytes_written += 8
#
#             # Write terminator
#             stream.write(bytes([0]))
#             bytes_written += 1
#
#             # Write buffer contents
#             buffer_data = buffer.getvalue()
#             stream.write(buffer_data)
#             bytes_written += len(buffer_data)
#         else:
#             # Write string value and array index directly
#             if self.value is not None:
#                 str_bytes = (self.value + "\0").encode("utf-8")
#                 stream.write(struct.pack("<I", len(str_bytes)))
#                 stream.write(str_bytes)
#                 bytes_written += 4 + len(str_bytes)
#             else:
#                 stream.write(struct.pack("<I", 0))
#                 bytes_written += 4
#
#             stream.write(struct.pack("<I", self.array_index))
#             bytes_written += 4
#
#         return bytes_written
