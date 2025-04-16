"""
Numeric property implementations for GVAS
Python port of int_property.rs
"""

from typing import Optional

from pydantic.dataclasses import dataclass

from .property_base import PropertyTrait
from ..utils import *


@dataclass
class BoolProperty(PropertyTrait):
    """A property that holds a boolean value"""

    type: str = "BoolProperty"
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

    type: str = "ByteProperty"
    name: Optional[str] = ""
    value: Union[int, str] = 0

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
            # according to the RUST code, this is an FSTRING, with  int32 prefix of length. Not BYTES.
            self.value = read_string(stream)

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
                stream,
                "ByteProperty",
                length=total_bytes,
                data_to_write=[self.name or ""],
            )

        # Write value
        if type(self.value) is int:
            bytes_written += write_uint8(stream, self.value)
        elif type(self.value) is str:
            # according to the RUST code, this is an FSTRING, with  int32 prefix of length. Not BYTES.
            bytes_written += write_string(stream, self.value)
        else:
            raise TypeError(f"Invalid type in ByteProperty: {type(self.value)}")

        return bytes_written


@dataclass
class Int8Property(PropertyTrait):
    type: str = "Int8Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=1)
        self.value = read_int8(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=1)
        bytes_written += write_int8(stream, self.value)
        return bytes_written


@dataclass
class UInt8Property(PropertyTrait):
    type: str = "UInt8Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=1)
        self.value = read_uint8(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=1)
        bytes_written += write_uint8(stream, self.value)
        return bytes_written


@dataclass
class Int16Property(PropertyTrait):
    type: str = "Int16Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=2)
        self.value = read_int16(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=2)
        bytes_written += write_int16(stream, self.value)
        return bytes_written


@dataclass
class UInt16Property(PropertyTrait):
    type: str = "UInt16Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=2)
        self.value = read_uint16(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=2)
        bytes_written += write_uint16(stream, self.value)
        return bytes_written


# For backward compatibility
@dataclass
class Int32Property(PropertyTrait):
    type: str = "Int32Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=4)
        self.value = read_int32(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=4)
        bytes_written += write_int32(stream, self.value)
        return bytes_written


# for backward compatibility
@dataclass
class IntProperty(PropertyTrait):
    type: str = "IntProperty"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=4)
        self.value = read_int32(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=4)
        bytes_written += write_int32(stream, self.value)
        return bytes_written


@dataclass
class UInt32Property(PropertyTrait):
    type: str = "UInt32Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=4)
        self.value = read_uint32(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=4)
        bytes_written += write_uint32(stream, self.value)
        return bytes_written


@dataclass
class Int64Property(PropertyTrait):
    type: str = "Int64Property"
    value: Union[int, float] = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=8)
        self.value = read_int64(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=8)
        bytes_written += write_int64(stream, self.value)
        return bytes_written


@dataclass
class UInt64Property(PropertyTrait):
    type: str = "UInt64Property"
    value: Union[int, float] = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=8)
        self.value = read_uint64(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=8)
        bytes_written += write_uint64(stream, self.value)
        return bytes_written


@dataclass
class FloatProperty(PropertyTrait):
    type: str = "FloatProperty"
    value: float = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=4)
        self.value = read_float(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=4)
        bytes_written += write_float(stream, self.value)
        return bytes_written


@dataclass
class DoubleProperty(PropertyTrait):
    type: str = "DoubleProperty"
    value: float = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        if include_header:
            read_standard_header(stream, assert_length=8)
        self.value = read_double(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(stream, self.type, length=8)
        bytes_written += write_double(stream, self.value)
        return bytes_written


#
#
# def create_numerical_property_class(
#     type_name: str,
#     storage_type,
#     size: int,
#     read_function: Callable[[BinaryIO], Any],
#     write_function: Callable[[BinaryIO, Any], int],
# ):
#     """
#     Create a property class to read/write number type with the specified size and type
#     """
#
#     @dataclass
#     class NumericalPropertyClass(PropertyTrait):
#         """A property that holds a {size}-bit {signedness} integer value"""
#
#         type: str = type_name
#         value: storage_type = 0
#
#         def read(self, stream: BinaryIO, include_header: bool = True) -> None:
#             if include_header:
#                 read_standard_header(stream, assert_length=size)
#             self.value = read_function(stream)
#
#         def write(self, stream: BinaryIO, include_header: bool = True) -> int:
#             bytes_written = 0
#
#             if include_header:
#                 bytes_written += write_standard_header(stream, type_name, length=size)
#             bytes_written += write_function(stream, self.value)
#             return bytes_written
#
#     NumericalPropertyClass.__name__ = type_name
#     NumericalPropertyClass.__doc__ = (
#         f"A property that holds a {size}-bit numerical value of type {storage_type}"
#     )
#     return NumericalPropertyClass
#

# Create all integer property classes
# fmt: off
# Int8Property = create_numerical_property_class("Int8Property", int, 1, read_int8, write_int8)
# UInt8Property = create_numerical_property_class("UInt8Property", int, 1, read_uint8, write_uint8)
# Int16Property = create_numerical_property_class("Int16Property", int, 2, read_int16, write_int16)
# UInt16Property = create_numerical_property_class("UInt16Property", int, 2, read_uint16, write_uint16)
# Int32Property = create_numerical_property_class("Int32Property", int, 4, read_int32, write_int32)
# UInt32Property = create_numerical_property_class("UInt32Property", int, 4, read_uint32, write_uint32)
# Int64Property = create_numerical_property_class("Int64Property", int, 8, read_int64, write_int64)
# UInt64Property = create_numerical_property_class("UInt64Property", int, 8, read_uint64, write_uint64)

# # For backward compatibility
# IntProperty = create_numerical_property_class("IntProperty", int, 4, read_int32, write_int32)

# FloatProperty = create_numerical_property_class("FloatProperty", float, 4, read_float, write_float)
# DoubleProperty = create_numerical_property_class("DoubleProperty", float, 8, read_double, write_double)
