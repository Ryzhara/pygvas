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

from .property_base import PropertyTrait, SerializationHints
from ..error import DeserializeError, SerializeError
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
        """Read boolean value from stream -- these should both be zero?"""
        if include_header:
            # type string was read by caller
            # Read length and array index
            _length = read_uint32(stream, 0)  # length must be zero
            _array_index = read_uint32(stream, 0)  # array index must be zero

        self.value = read_bool(stream)

        if include_header:
            read_uint8(stream, 0)  # Read bool specific null byte

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write boolean value to stream"""
        bytes_written = 0

        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "BoolProperty")
            bytes_written += write_uint32(stream, 0)  # Write length (0 for bool)
            bytes_written += write_uint32(stream, 0)  # Write array index

        bytes_written += write_bool(stream, self.value)

        if include_header:
            bytes_written += write_uint8(stream, 0)  # Write bool specific null byte

        return bytes_written


@dataclass
class ByteProperty(PropertyTrait):
    """A property that holds a byte value or type_name"""

    name: Optional[str] = None
    value: Union[int, bytes] = 0

    @classmethod
    def new_byte(cls, name: Optional[str], value: int) -> "ByteProperty":
        """Create a new byte-type property"""
        return cls(name=name, value=value)

    @classmethod
    def new_name(cls, name: Optional[str], value: str) -> "ByteProperty":
        """Create a new type_name-type property"""
        return cls(name=name, value=value)

    def read(
        self, stream: BinaryIO, include_header: bool = True, suggested_length: int = 0
    ) -> None:
        """Read byte property from stream"""
        if include_header:
            suggested_length = read_uint32(stream, 1)  # expect value 1
            _array_index = read_uint32(stream, 0)  # require zero array_index
            self.name = read_string(stream)
            _null_byte = read_uint8(stream, 0)  # enforce null terminator

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
            # Write the BODY to temporary buffer first to get length

            # now write all the things
            bytes_written += write_string(stream, "ByteProperty")
            total_bytes = 1 if type(self.value) is int else len(self.value)
            bytes_written += write_uint32(stream, total_bytes)  # Total length
            bytes_written += write_uint32(stream, 0)  # Array index
            bytes_written += write_string(stream, self.name)
            bytes_written += write_uint8(stream, 0)  # null byte terminator

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

    value: float = 0.0

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read float value from stream"""
        if include_header:
            _length = read_uint32(stream, 4)
            _array_index = read_uint32(stream, 0)
            read_null_byte_terminator(stream)

        self.value = read_float(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write float value to stream"""
        bytes_written = 0

        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "FloatProperty")
            bytes_written += write_uint32(stream, 4)  # length
            bytes_written += write_uint32(stream, 0)  # Write array index
            bytes_written += write_uint8(stream, 0)  # Write terminator

        bytes_written += write_float(stream, self.value)
        # bytes_written += 4

        return bytes_written


@dataclass
class DoubleProperty(PropertyTrait):
    """A property that holds a 64-bit floating point value"""

    value: float = 0.0

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read double value from stream"""
        if include_header:
            _length = read_uint32(stream, 8)
            _array_index = read_uint32(stream, 0)
            read_null_byte_terminator(stream)

        self.value = struct.unpack("<d", stream.read(8))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write double value to stream"""
        bytes_written = 0

        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "DoubleProperty")
            bytes_written += write_uint32(stream, 8)  # length
            bytes_written += write_uint32(stream, 0)  # Write array index
            bytes_written += write_uint8(stream, 0)  # Write terminator

        bytes_written += write_double(stream, self.value)

        return bytes_written


def create_int_property_class(type_name: str, size: int, signed: bool = True):
    """Create an integer property class with the specified size and signedness"""
    # tuple of (unsigned-str, signed-str)
    parameter_map = {1: ("B", "b"), 2: ("<H", "<h"), 4: ("<I", "<i"), 8: ("<q", "<Q")}
    assert size in parameter_map.keys()
    encoding_string = parameter_map[size][1 if signed else 0]

    @dataclass
    class IntPropertyClass(PropertyTrait):
        """A property that holds a {size}-bit {signedness} integer value"""

        value: int = 0

        def read(
            self,
            stream: BinaryIO,
            include_header: bool = True,
        ) -> None:
            """Read integer value from stream"""
            if include_header:
                # Read length and array index
                _length = read_uint32(stream, size)
                _array_index = read_uint32(stream, 0)
                read_null_byte_terminator(stream)

            # Read value based on size and signedness
            self.value = struct.unpack(encoding_string, stream.read(size))[0]

        def write(
            self,
            stream: BinaryIO,
            include_header: bool = True,
        ) -> int:
            """Write integer value to stream"""
            bytes_written = 0

            if include_header:
                # Write property type needs to be written by the object
                bytes_written += write_string(stream, type_name)

                bytes_written += write_uint32(stream, size)  # Write length
                bytes_written += write_uint32(stream, 0)  # Write array index
                bytes_written += write_uint8(stream, 0)  # null byte terminator

            bytes_written += stream.write(struct.pack(encoding_string, self.value))

            return bytes_written

    IntPropertyClass.__name__ = type_name
    IntPropertyClass.__doc__ = f"A property that holds a {size}-bit {'signed' if signed else 'unsigned'} integer value"
    return IntPropertyClass


# Create all integer property classes
Int8Property = create_int_property_class("Int8Property", 1, True)
Int16Property = create_int_property_class("Int16Property", 2, True)
Int32Property = create_int_property_class("Int32Property", 4, True)
Int64Property = create_int_property_class("Int64Property", 8, True)
UInt8Property = create_int_property_class("UInt8Property", 1, False)
UInt16Property = create_int_property_class("UInt16Property", 2, False)
UInt32Property = create_int_property_class("UInt32Property", 4, False)
UInt64Property = create_int_property_class("UInt64Property", 8, False)

# For backward compatibility
IntProperty = create_int_property_class("IntProperty", 4, True)
