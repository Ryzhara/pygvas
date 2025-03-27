import struct
from dataclasses import dataclass
from .property_base import Property, PropertyTrait, PropertyOptions

from enum import Enum
from typing import Optional, BinaryIO
import datetime


""" These might be structs or unitary properties.
    "DateTime",
    "Timespan",
"""


@dataclass
class DateTimeProperty(PropertyTrait):
    type_name: str = "DateTime"
    datetime: int = 0  # uint64
    comment: str = ""

    @classmethod
    def new(cls, type_name: str) -> "DateTimeProperty":
        assert type_name == "DateTime"
        return cls(type_name=type_name)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"DateTimeProperty never has a header!"
        format_str, size = ("<Q", 8)
        self.datetime = struct.unpack(format_str, stream.read(size))[0]
        self.comment = str(datetime.datetime.fromtimestamp(self.datetime / 1000.0))

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"DateTimeProperty never has a header!"
        format_str, _size = ("<Q", 8)
        bytes_written = stream.write(struct.pack(format_str, self.datetime))
        return bytes_written


@dataclass
class TimespanProperty(PropertyTrait):
    type_name: str = "Timespan"
    timespan: int = 0  # uint64
    comment: str = ""

    @classmethod
    def new(cls, type_name: str) -> "TimespanProperty":
        assert type_name == "Timespan"
        return cls(type_name=type_name)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"DateTimeProperty never has a header!"
        format_str, size = ("<Q", 8)
        self.timespan = struct.unpack(format_str, stream.read(size))[0]
        self.comment = str(datetime.timedelta(milliseconds=(self.timespan / 1000.0)))

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"DateTimeProperty never has a header!"
        format_str, _size = ("<Q", 8)
        bytes_written = stream.write(struct.pack(format_str, self.timespan))
        return bytes_written


@dataclass
class IntPointProperty(PropertyTrait):
    type_name: str = "IntPoint"
    x: int = 0
    y: int = 0

    @classmethod
    def new(cls, type_name: str) -> "IntPointProperty":
        assert type_name == "IntPoint"
        return cls(type_name=type_name)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"IntPointProperty never has a header!"
        format_str, size = ("<i", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"IntPointProperty never has a header!"
        format_str, _size = ("<i", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        return bytes_written


@dataclass
class LinearColorProperty(PropertyTrait):
    type_name: str = "LinearColor"
    a: float = 0
    b: float = 0
    g: float = 0
    r: float = 0

    @classmethod
    def new(cls, type_name: str) -> "LinearColorProperty":
        assert type_name == "LinearColor"
        return cls(type_name=type_name)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, size = ("<f", 4)
        self.a = struct.unpack(format_str, stream.read(size))[0]
        self.b = struct.unpack(format_str, stream.read(size))[0]
        self.g = struct.unpack(format_str, stream.read(size))[0]
        self.r = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str = "<f"
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.a))
        bytes_written += stream.write(struct.pack(format_str, self.b))
        bytes_written += stream.write(struct.pack(format_str, self.g))
        bytes_written += stream.write(struct.pack(format_str, self.r))
        return bytes_written


@dataclass
class RotatorProperty(PropertyTrait):
    type_name = ""  # Rotator, RotatorF, RotatorD
    is_double: bool = False
    pitch: float = 0
    yaw: float = 0
    roll: float = 0

    @classmethod
    def new(cls, type_name: str, use_lwc=False) -> "RotatorProperty":
        # assert type_name in ["Rotator", "RotatorF", "RotatorD"]
        # is_double = type_name == "RotatorD" or (type_name == "Rotator" and use_lwc)
        assert type_name == "Rotator"
        is_double = use_lwc
        return cls(is_double=is_double)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.pitch = struct.unpack(format_str, stream.read(size))[0]
        self.yaw = struct.unpack(format_str, stream.read(size))[0]
        self.roll = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.pitch))
        bytes_written += stream.write(struct.pack(format_str, self.yaw))
        bytes_written += stream.write(struct.pack(format_str, self.roll))
        return bytes_written


@dataclass
class QuatProperty(PropertyTrait):
    type_name = ""  # Quat, QuatF, QuatD
    is_double: bool = False
    x: float = 0
    z: float = 0
    w: float = 0
    y: float = 0

    @classmethod
    def new(cls, type_name: str, use_lwc=False) -> "QuatProperty":
        # assert type_name in ["Quat", "QuatF", "QuatD"]
        # is_double = type_name == "QuatD" or (type_name == "Quat" and use_lwc)
        assert type_name == "Quat"
        is_double = use_lwc
        return cls(is_double=is_double)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]
        self.z = struct.unpack(format_str, stream.read(size))[0]
        self.w = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        bytes_written += stream.write(struct.pack(format_str, self.z))
        bytes_written += stream.write(struct.pack(format_str, self.w))
        return bytes_written


@dataclass
class VectorProperty(PropertyTrait):
    type_name: str = ""
    is_double: bool = False
    x: float = 0
    y: float = 0
    z: float = 0

    @classmethod
    def new(cls, type_name: str, use_lwc=False) -> "VectorProperty":
        # assert type_name in ["Vector", "VectorF", "VectorD"]
        # is_double = type_name == "VectorD" or (type_name == "Vector" and use_lwc)
        assert type_name == "Vector"
        is_double = use_lwc
        return cls(type_name=type_name, is_double=is_double)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]
        self.z = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        bytes_written += stream.write(struct.pack(format_str, self.z))
        return bytes_written


# In Python, floats are actually doubles
@dataclass
class Vector2Property(PropertyTrait):
    type_name: str = ""  # Vector2, Vector2F, Vector2D
    is_double: bool = False
    x: float = 0
    y: float = 0

    @classmethod
    def new(cls, type_name: str, use_lwc=False) -> "Vector2Property":
        # assert type_name in ["Vector2", "Vector2F", "Vector2D"]
        # is_double = type_name == "Vector2D" or (type_name == "Vector2" and use_lwc)
        assert type_name == "Vector2"
        is_double = use_lwc
        return cls(type_name=type_name, is_double=is_double)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = False,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        assert include_header == False, f"{self.type_name} never has a header!"
        format_str, _size = ("<d", 8) if self.is_double else ("<", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        return bytes_written
