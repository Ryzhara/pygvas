import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from .property_base import SerializationHints
from ..utils import *


class SpecialStructTrait(ABC):
    """Base trait/interface for all special struct types"""

    @abstractmethod
    def read(self, stream: BinaryIO) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(self, stream: BinaryIO) -> int:
        """Write property data to a binary stream and return byte count written"""
        pass

    @classmethod
    def uses_large_world_coordinates(cls):
        return SerializationHints.get_engine_version().major >= 5


# ============================================
#
@dataclass
class GuidProperty(SpecialStructTrait):
    type_name: str = "Guid"
    guid: uuid = None
    comment: str = ""

    @classmethod
    def new(cls) -> "GuidProperty":
        return cls()

    def read(self, stream: BinaryIO) -> None:
        guid_bytes = stream.read(16)
        self.guid = uuid.UUID(bytes_le=guid_bytes)
        try:
            self.comment = str(self.guid)
        except Exception as e:
            print(f"Cant process {self.guid=} : {e}")
            self.comment = str(self.guid)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = write_bytes(stream, self.guid.bytes_le)
        assert bytes_written == 16
        return bytes_written


# ============================================
#
@dataclass
class DateTimeProperty(SpecialStructTrait):
    type_name: str = "DateTime"
    datetime: int = 0  # uint64
    comment: str = ""

    @classmethod
    def new(cls) -> "DateTimeProperty":
        return cls()

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<Q", 8)
        self.datetime = struct.unpack(format_str, stream.read(size))[0]
        try:
            # datetime.datetime.fromtimestamp takes time in seconds since January 1, 1970, 00:00:00 (UTC) as a floating-point number
            # FDateTime type represents dates and times as ticks (0.1 microseconds) since January 1, 0001
            seconds_since_1_1_00001 = 6_392_264_799_600
            ticks_per_second = 10_000_000.0
            seconds = self.datetime / ticks_per_second
            self.comment = (
                datetime.datetime.min + datetime.timedelta(seconds=seconds)
            ).strftime("%d/%m/%Y %H:%M:%S.%f")
            # print(f"Found DateTime: {self.comment}")
            # self.comment = str(datetime.datetime.fromtimestamp(self.datetime / 1000.0))
        except Exception as e:
            print(f"Cant process {self.datetime=} : {e}")
            self.comment = str(self.datetime)

    def write(self, stream: BinaryIO) -> int:
        format_str, size = ("<Q", 8)
        # bytes_written = stream.write(struct.pack(format_str, self.datetime))
        bytes_written = write_uint64(stream, self.datetime)
        assert bytes_written == size
        return bytes_written


# ============================================
#
@dataclass
class TimespanProperty(SpecialStructTrait):
    type_name: str = "Timespan"
    timespan: int = 0  # uint64
    comment: str = ""

    @classmethod
    def new(cls) -> "TimespanProperty":
        return cls()

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<Q", 8)
        self.timespan = struct.unpack(format_str, stream.read(size))[0]
        self.comment = str(datetime.timedelta(milliseconds=(self.timespan / 1000.0)))

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<Q", 8)
        bytes_written = stream.write(struct.pack(format_str, self.timespan))
        return bytes_written


# ============================================
#
@dataclass
class IntPointProperty(SpecialStructTrait):
    type_name: str = "IntPoint"
    x: int = 0
    y: int = 0

    @classmethod
    def new(cls) -> "IntPointProperty":
        return cls()

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<i", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<i", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        return bytes_written


# ============================================
#
@dataclass
class LinearColorProperty(SpecialStructTrait):
    type_name: str = "LinearColor"
    a: float = 0
    b: float = 0
    g: float = 0
    r: float = 0

    @classmethod
    def new(cls) -> "LinearColorProperty":
        return cls()

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<f", 4)
        self.a = struct.unpack(format_str, stream.read(size))[0]
        self.b = struct.unpack(format_str, stream.read(size))[0]
        self.g = struct.unpack(format_str, stream.read(size))[0]
        self.r = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.a))
        bytes_written += stream.write(struct.pack(format_str, self.b))
        bytes_written += stream.write(struct.pack(format_str, self.g))
        bytes_written += stream.write(struct.pack(format_str, self.r))
        return bytes_written


# ============================================
#
@dataclass
class RotatorProperty(SpecialStructTrait):
    type_name = "Rotator"
    is_double: bool = False
    pitch: float = 0
    yaw: float = 0
    roll: float = 0

    @classmethod
    def new(cls) -> "RotatorProperty":
        return cls(is_double=SpecialStructTrait.uses_large_world_coordinates())

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.pitch = struct.unpack(format_str, stream.read(size))[0]
        self.yaw = struct.unpack(format_str, stream.read(size))[0]
        self.roll = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.pitch))
        bytes_written += stream.write(struct.pack(format_str, self.yaw))
        bytes_written += stream.write(struct.pack(format_str, self.roll))
        return bytes_written


# ============================================
#
@dataclass
class QuatProperty(SpecialStructTrait):
    type_name = "Quat"
    is_double: bool = False
    x: float = 0
    y: float = 0
    z: float = 0
    w: float = 0

    @classmethod
    def new(cls, use_lwc=False) -> "QuatProperty":
        return cls(is_double=SpecialStructTrait.uses_large_world_coordinates())

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]
        self.z = struct.unpack(format_str, stream.read(size))[0]
        self.w = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        bytes_written += stream.write(struct.pack(format_str, self.z))
        bytes_written += stream.write(struct.pack(format_str, self.w))
        return bytes_written


# ============================================
#
@dataclass
class VectorProperty(SpecialStructTrait):
    type_name: str = "Vector"
    is_double: bool = False
    x: float = 0
    y: float = 0
    z: float = 0

    @classmethod
    def new(cls, use_lwc=False) -> "VectorProperty":
        return cls(is_double=SpecialStructTrait.uses_large_world_coordinates())

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]
        self.z = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<d", 8) if self.is_double else ("<f", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        bytes_written += stream.write(struct.pack(format_str, self.z))
        return bytes_written


# ============================================
#
@dataclass
class Vector2DProperty(SpecialStructTrait):
    type_name: str = "Vector2D"
    is_double: bool = False
    x: float = 0
    y: float = 0

    @classmethod
    def new(cls, use_lwc=False) -> "Vector2DProperty":
        return cls(is_double=SpecialStructTrait.uses_large_world_coordinates())

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<d", 8) if self.is_double else ("<f", 4)
        self.x = struct.unpack(format_str, stream.read(size))[0]
        self.y = struct.unpack(format_str, stream.read(size))[0]

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<d", 8) if self.is_double else ("<", 4)
        bytes_written = 0
        bytes_written += stream.write(struct.pack(format_str, self.x))
        bytes_written += stream.write(struct.pack(format_str, self.y))
        return bytes_written


_special_struct_type_map = {
    "Vector": VectorProperty,
    "Vector2D": Vector2DProperty,
    "Rotator": RotatorProperty,
    "Quat": QuatProperty,
    "LinearColor": LinearColorProperty,
    "IntPoint": IntPointProperty,
    "DateTime": DateTimeProperty,
    "Timespan": TimespanProperty,
    "Guid": GuidProperty,
}


# ============================================
#
def is_special_struct(type_name: str) -> bool:
    return type_name in _special_struct_type_map.keys()


# ============================================
#
def get_special_struct_instance(
    type_name: str, use_lwc: bool = False
) -> SpecialStructTrait:
    # Map property types to their classes

    if type_name in _special_struct_type_map.keys():
        prop_class = _special_struct_type_map.get(type_name)
        prop = prop_class.new()
    else:
        print(f"Unknown special struc type: {type_name}")
        raise DeserializeError(f"Unknown special struc type: {type_name}")

    return prop
