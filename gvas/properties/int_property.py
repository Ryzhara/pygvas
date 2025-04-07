"""
Numeric property implementations for GVAS
Python port of int_property.rs

Contains implementations for:
- BoolProperty
- ByteProperty
- FloatProperty
- DoubleProperty
- Int8Property
- Int16Property
- Int32Property
- Int64Property
- UInt8Property
- UInt16Property
- UInt32Property
- UInt64Property
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, BinaryIO
import struct
from io import BytesIO

from .property_base import PropertyTrait
from ..utils import *


@dataclass
class BoolProperty(PropertyTrait):
    """A property that holds a boolean value"""

    value: bool = False

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read boolean value from stream -- length and array_index should both be zero"""
        if include_header:
            # BoolProperty header is just 8 bytes of zeros! No terminator
            _length = read_uint32(stream, 0)  # length must be zero
            _array_index = read_uint32(stream, 0)  # array index must be zero

        # Could conceivably be just embedding the value in the header, but only if header was ALWAYS required.
        self.value = read_bool(stream)

        if include_header:
            # And then ends in a terminator
            read_uint8(stream, 0)  # Read bool specific null byte

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write boolean value to stream"""
        bytes_written = 0

        if include_header:
            bytes_written += write_string(stream, "BoolProperty")
            # BoolProperty header is just 8 bytes of zeros! No terminator
            bytes_written += write_uint32(stream, 0)  # Write length (0 for bool)
            bytes_written += write_uint32(stream, 0)  # Write array index

        bytes_written += write_bool(stream, self.value)

        if include_header:
            # And then ends in a terminator
            bytes_written += write_uint8(stream, 0)  # Write bool specific null byte

        return bytes_written


@dataclass
class ByteProperty(PropertyTrait):
    """A property that holds a byte value or type_name"""

    type = "ByteProperty"
    name: Optional[str] = None
    value: Union[int, bytes] = 0

    def __init__(self, name: Optional[str] = None, value: Union[int, bytes] = None):
        self.name = name
        self.value = value

    def read(
        self, stream: BinaryIO, include_header: bool = True, suggested_length: int = 0
    ) -> None:
        """Read byte property from stream"""
        if include_header:
            suggested_length, self.name = read_standard_header(
                stream, stream_readers=[read_string]
            )

        # Read value based on length
        if suggested_length <= 1:  # indicates a byte value
            self.value = read_uint8(stream)
        else:  # indicates a type_name value
            # according to the RUST code, this is actually an FSTRING, with  int32 prefix of length. NOT raw bytes
            self.value = read_bytes(stream, suggested_length)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write byte property to stream"""
        bytes_written = 0

        if include_header:
            total_bytes = 1 if type(self.value) is int else len(self.value)
            bytes_written += write_standard_header(
                stream, "ByteProperty", length=total_bytes, data_to_write=[self.name]
            )

        # Write value
        if type(self.value) is int:
            bytes_written += write_uint8(stream, self.value)
        elif type(self.value) is bytes:
            # according to the RUST code, this is actually an FSTRING, with  int32 prefix of length. NOT raw bytes
            bytes_written += write_bytes(stream, self.value)
        else:
            raise TypeError(f"Invalid type in ByteProperty: {type(self.value)}")

        return bytes_written


@dataclass
class FloatProperty(PropertyTrait):
    """A property that holds a 32-bit floating point value"""

    type = "FloatProperty"
    value: float = 0.0

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read float value from stream"""
        if include_header:
            read_standard_header(stream, assert_length=4)

        self.value = read_float(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write float value to stream"""
        bytes_written = 0

        if include_header:
            bytes_written += write_standard_header(stream, "FloatProperty", length=4)

        bytes_written += write_float(stream, self.value)

        return bytes_written


@dataclass
class DoubleProperty(PropertyTrait):
    """A property that holds a 64-bit floating point value"""

    type = "DoubleProperty"
    value: float = 0.0

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read double value from stream"""
        if include_header:
            read_standard_header(stream, assert_length=8)

        self.value = read_double(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write double value to stream"""
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, "DoubleProperty", length=8)

        bytes_written += write_double(stream, self.value)

        return bytes_written


def create_int_property_class(type_name: str, size: int, signed: bool = True):
    """
    Create an integer property class with the specified size and signedness
    """
    # It is cleaner to use struct functions rather than read/write wrappers
    # tuple of (unsigned-str, signed-str)
    parameter_map = {1: ("B", "b"), 2: ("<H", "<h"), 4: ("<I", "<i"), 8: ("<Q", "<q")}
    assert size in parameter_map.keys()
    encoding_string = parameter_map[size][1 if signed else 0]

    @dataclass
    class IntPropertyClass(PropertyTrait):
        """A property that holds a {size}-bit {signedness} integer value"""

        type: str = type_name
        value: int = 0

        def read(
            self,
            stream: BinaryIO,
            include_header: bool = True,
        ) -> None:
            """
            Read integer value from stream
            """
            if include_header:
                read_standard_header(stream, assert_length=size)

            self.value = struct.unpack(encoding_string, stream.read(size))[0]

        def write(
            self,
            stream: BinaryIO,
            include_header: bool = True,
        ) -> int:
            """
            Write integer value to stream
            """
            bytes_written = 0

            if include_header:
                bytes_written += write_standard_header(stream, type_name, length=size)

            bytes_written += stream.write(struct.pack(encoding_string, self.value))

            return bytes_written

    IntPropertyClass.__name__ = type_name
    IntPropertyClass.__doc__ = f"A property that holds a {size}-bit {'signed' if signed else 'unsigned'} integer value"
    return IntPropertyClass


# Create all integer property classes
Int8Property = create_int_property_class("Int8Property", 1, True)
UInt8Property = create_int_property_class("UInt8Property", 1, False)
Int16Property = create_int_property_class("Int16Property", 2, True)
UInt16Property = create_int_property_class("UInt16Property", 2, False)
Int32Property = create_int_property_class("Int32Property", 4, True)
UInt32Property = create_int_property_class("UInt32Property", 4, False)
Int64Property = create_int_property_class("Int64Property", 8, True)
UInt64Property = create_int_property_class("UInt64Property", 8, False)

# For backward compatibility
IntProperty = create_int_property_class("IntProperty", 4, True)
