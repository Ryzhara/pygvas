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

from .property_base import PropertyTrait, PropertyOptions
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
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read boolean value from stream -- these should both be zero?"""
        if include_header:
            # Read length and array index
            length = struct.unpack("<I", stream.read(4))[0]
            # print(f"Found bool {length=}")
            array_index = struct.unpack("<I", stream.read(4))[0]
            # print(f"Found bool {array_index=}")
            assert length == 0, f"Invalid boolean length {length=}"
            assert array_index == 0, f"Invalid boolean array index {array_index=}"

        self.value = bool(stream.read(1)[0])

        if include_header:
            # Read terminator
            terminator = stream.read(1)[0]
            if terminator != 0:
                position = stream.tell() - 1
                raise DeserializeError.invalid_terminator(terminator, position)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write boolean value to stream"""
        bytes_written = 0

        # Write property type needs to be written by the object
        bytes_written += write_string(stream, "BoolProperty")

        if include_header:
            # Write length (0 for bool)
            bytes_written += stream.write(struct.pack("<I", 0))
            # Write array index
            bytes_written += stream.write(struct.pack("<I", 0))
            # Write terminator

        bytes_written += stream.write(bytes([int(self.value)]))
        # bytes_written += 1 ???

        if include_header:
            bytes_written += stream.write(bytes([0]))
            # bytes_written += 9

        return bytes_written


class BytePropertyValue(Enum):
    """Type of byte property value"""

    Byte = 0
    Name = 1


@dataclass
class ByteProperty(PropertyTrait):
    """A property that holds a byte value or type_name"""

    name: Optional[str] = None
    value: Union[int, str] = 0

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
            _length, _array_index = read_length_and_array_index(
                stream, assert_length=1, assert_index=0
            )
            read_null_byte_terminator_and_validate(stream)

        # Read type_name if present
        self.name = read_string(stream) if suggested_length > 1 else None

        # Read value based on length
        if suggested_length <= 1:  # indicates a byte value
            self.value = stream.read(1)[0]
        else:  # indicates a type_name value
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write byte property to stream"""
        bytes_written = 0

        if include_header:
            # Write to temporary buffer first to get length
            buffer = BytesIO()
            buffer_bytes = 0

            # Write type_name if present
            if self.name:
                buffer_bytes += write_string(buffer, self.name)
            else:
                buffer.write(struct.pack("<I", 0))
                buffer_bytes += 4

            # Write value
            if isinstance(self.value, int):
                buffer.write(bytes([self.value]))
                buffer_bytes += 1
            else:
                buffer_bytes += write_string(buffer, self.value)

            # Write length and array index
            stream.write(struct.pack("<I", buffer_bytes))  # Total length
            stream.write(struct.pack("<I", 0))  # Array index
            bytes_written += 8

            # Write terminator
            stream.write(bytes([0]))
            bytes_written += 1

            # Write buffer contents
            buffer_data = buffer.getvalue()
            stream.write(buffer_data)
            bytes_written += len(buffer_data)
        else:
            # Write type_name if present
            if self.name:
                bytes_written += write_string(stream, self.name)
            else:
                stream.write(struct.pack("<I", 0))
                bytes_written += 4

            # Write value
            if isinstance(self.value, int):
                stream.write(bytes([self.value]))
                bytes_written += 1
            else:
                bytes_written += write_string(stream, self.value)

        return bytes_written


@dataclass
class FloatProperty(PropertyTrait):
    """A property that holds a 32-bit floating point value"""

    value: float = 0.0

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read float value from stream"""
        if include_header:
            _length, _array_index = read_length_and_array_index(
                stream, assert_length=4, assert_index=0
            )

            read_null_byte_terminator_and_validate()

        self.value = struct.unpack("<f", stream.read(4))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write float value to stream"""
        bytes_written = 0

        # Write property type needs to be written by the object
        bytes_written += write_string(stream, "FloatProperty")

        if include_header:
            # Write length (4 for float)
            bytes_written += stream.write(struct.pack("<I", 4))
            # Write array index
            bytes_written += stream.write(struct.pack("<I", 0))
            # Write terminator
            bytes_written += stream.write(bytes([0]))
            # bytes_written += 9

        bytes_written += stream.write(struct.pack("<f", self.value))
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
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read double value from stream"""
        if include_header:
            _length, _array_index = read_length_and_array_index(
                stream, assert_length=8, assert_index=0
            )

            read_null_byte_terminator_and_validate()

        self.value = struct.unpack("<d", stream.read(8))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write double value to stream"""
        bytes_written = 0

        # Write property type needs to be written by the object
        bytes_written += write_string(stream, "DoubleProperty")

        if include_header:
            # Write length (8 for double)
            bytes_written += stream.write(struct.pack("<I", 8))
            # Write array index
            bytes_written += stream.write(struct.pack("<I", 0))
            # Write terminator
            bytes_written += stream.write(bytes([0]))
            # bytes_written += 9

        bytes_written += stream.write(struct.pack("<d", self.value))
        # bytes_written += 8

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
            options: Optional[PropertyOptions] = None,
        ) -> None:
            """Read integer value from stream"""
            if include_header:
                # Read length and array index
                _length, _array_index = read_length_and_array_index(
                    stream, assert_length=size, assert_index=0
                )

                read_null_byte_terminator_and_validate()

            # Read value based on size and signedness
            self.value = struct.unpack(encoding_string, stream.read(size))[0]

        def write(
            self,
            stream: BinaryIO,
            include_header: bool = True,
            options: Optional[PropertyOptions] = None,
        ) -> int:
            """Write integer value to stream"""
            bytes_written = 0

            # Write property type needs to be written by the object
            bytes_written += write_string(stream, type_name)

            if include_header:
                # Write length
                bytes_written += stream.write(struct.pack("<I", size))
                # Write array index
                bytes_written += stream.write(struct.pack("<I", 0))
                # Write terminator
                bytes_written += stream.write(bytes([0]))
                # bytes_written += 9

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
