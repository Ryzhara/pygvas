"""
Numeric property implementations for GVAS
Python port of int_property.rs
"""

from typing import Literal

from pydantic.dataclasses import dataclass

from gvas.properties.property_base import PropertyTrait
from gvas.gvas_utils import *


@dataclass
class BoolProperty(PropertyTrait):
    """A property that holds a boolean value"""

    type: Literal["BoolProperty"] = "BoolProperty"
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

    type: Literal["ByteProperty"] = "ByteProperty"
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
    type: Literal["Int8Property"] = "Int8Property"
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
    type: Literal["UInt8Property"] = "UInt8Property"
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
    type: Literal["Int16Property"] = "Int16Property"
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
    type: Literal["UInt16Property"] = "UInt16Property"
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
    type: Literal["Int32Property"] = "Int32Property"
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
    type: Literal["IntProperty"] = "IntProperty"
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
    type: Literal["UInt32Property"] = "UInt32Property"
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
    type: Literal["Int64Property"] = "Int64Property"
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
    type: Literal["UInt64Property"] = "UInt64Property"
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
    type: Literal["FloatProperty"] = "FloatProperty"
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
    type: Literal["DoubleProperty"] = "DoubleProperty"
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
