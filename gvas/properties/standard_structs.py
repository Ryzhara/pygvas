from abc import ABC, abstractmethod
from typing import Literal

from pydantic.dataclasses import dataclass

from gvas.engine_tools import FUE5ReleaseStreamObjectVersion, EngineVersionTool
from gvas.gvas_utils import *


# ============================================
#
@dataclass
class StandardStructTrait(ABC):
    """
    Base trait/interface for all structure types that could be in any environment
    """

    @abstractmethod
    def read(self, stream: BinaryIO) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(self, stream: BinaryIO) -> int:
        """Write property data to a binary stream and return byte count written"""
        pass

    @staticmethod
    def uses_lwc():
        uses_lwc = EngineVersionTool.supports_version(
            FUE5ReleaseStreamObjectVersion.LargeWorldCoordinates
        )
        return uses_lwc


# ============================================
#
@dataclass
class GuidStruct(StandardStructTrait):
    type: Literal["Guid"] = "Guid"
    guid: Optional[str] = None

    def read(self, stream: BinaryIO) -> None:
        position = stream.tell()
        self.guid = guid_to_str(read_guid(stream))

    def write(self, stream: BinaryIO) -> int:
        bytes_written = write_guid(stream, self.guid)
        assert bytes_written == 16
        return bytes_written


# ============================================
#
@dataclass
class DateTimeStruct(StandardStructTrait):
    type: Literal["DateTime"] = "DateTime"
    datetime: int = 0  # uint64
    comment: str = None

    def read(self, stream: BinaryIO) -> None:
        self.datetime = read_uint64(stream)
        self.comment = datetime_to_str(self.datetime)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = write_uint64(stream, self.datetime)
        return bytes_written


# ============================================
#
@dataclass
class TimespanStruct(StandardStructTrait):
    type: Literal["Timespan"] = "Timespan"
    timespan: int = 0  # uint64
    comment: str = None

    def read(self, stream: BinaryIO) -> None:
        format_str, size = ("<Q", 8)
        self.timespan = struct.unpack(format_str, stream.read(size))[0]
        self.comment = timespan_to_str(self.timespan)

    def write(self, stream: BinaryIO) -> int:
        format_str, _size = ("<Q", 8)
        bytes_written = stream.write(struct.pack(format_str, self.timespan))
        return bytes_written


# ============================================
#
@dataclass
class IntPointStruct(StandardStructTrait):
    type: Literal["IntPoint"] = "IntPoint"
    x: int = 0
    y: int = 0

    def read(self, stream: BinaryIO) -> None:
        # always int32
        self.x = read_int32(stream)
        self.y = read_int32(stream)

    def write(self, stream: BinaryIO) -> int:
        # always int32
        bytes_written = 0
        bytes_written += write_int32(stream, self.x)
        bytes_written += write_int32(stream, self.y)
        return bytes_written


# ============================================
#
@dataclass
class LinearColorStruct(StandardStructTrait):
    type: Literal["LinearColor"] = "LinearColor"
    a: float = 0
    b: float = 0
    g: float = 0
    r: float = 0

    def read(self, stream: BinaryIO) -> None:
        # always float32
        self.a = read_float(stream)
        self.b = read_float(stream)
        self.g = read_float(stream)
        self.r = read_float(stream)

    def write(self, stream: BinaryIO) -> int:
        # always float32
        bytes_written = 0
        bytes_written += write_float(stream, self.a)
        bytes_written += write_float(stream, self.b)
        bytes_written += write_float(stream, self.g)
        bytes_written += write_float(stream, self.r)
        return bytes_written


# ============================================
#
@dataclass
class RotatorStruct(StandardStructTrait):
    type: Literal["Rotator"] = "Rotator"
    pitch: float = 0
    yaw: float = 0
    roll: float = 0

    def read(self, stream: BinaryIO) -> None:

        read_fn = read_double if self.uses_lwc() else read_float

        self.pitch = read_fn(stream)
        self.yaw = read_fn(stream)
        self.roll = read_fn(stream)

    def write(self, stream: BinaryIO) -> int:

        write_fn = write_double if self.uses_lwc() else write_float

        bytes_written = 0
        bytes_written += write_fn(stream, self.pitch)
        bytes_written += write_fn(stream, self.yaw)
        bytes_written += write_fn(stream, self.roll)
        return bytes_written


# ============================================
#
@dataclass
class QuatStruct(StandardStructTrait):
    type: Literal["Quat"] = "Quat"
    x: float = 0
    y: float = 0
    z: float = 0
    w: float = 0

    def read(self, stream: BinaryIO) -> None:

        read_fn = read_double if self.uses_lwc() else read_float

        self.x = read_fn(stream)
        self.y = read_fn(stream)
        self.z = read_fn(stream)
        self.w = read_fn(stream)

    def write(self, stream: BinaryIO) -> int:

        write_fn = write_double if self.uses_lwc() else write_float

        bytes_written = 0
        bytes_written += write_fn(stream, self.x)
        bytes_written += write_fn(stream, self.y)
        bytes_written += write_fn(stream, self.z)
        bytes_written += write_fn(stream, self.w)
        return bytes_written


# ============================================
#
@dataclass
class VectorStruct(StandardStructTrait):
    type: Literal["Vector"] = "Vector"
    x: float = 0
    y: float = 0
    z: float = 0

    def read(self, stream: BinaryIO) -> None:

        read_fn = read_double if self.uses_lwc() else read_float

        self.x = read_fn(stream)
        self.y = read_fn(stream)
        self.z = read_fn(stream)

    def write(self, stream: BinaryIO) -> int:

        write_fn = write_double if self.uses_lwc() else write_float

        bytes_written = 0
        bytes_written += write_fn(stream, self.x)
        bytes_written += write_fn(stream, self.y)
        bytes_written += write_fn(stream, self.z)
        return bytes_written


# ============================================
#
@dataclass
# from pydantic import BaseModel
class Vector2DStruct(StandardStructTrait):
    type: Literal["Vector2D"] = "Vector2D"
    x: float = 0
    y: float = 0

    def read(self, stream: BinaryIO) -> None:

        read_fn = read_double if self.uses_lwc() else read_float

        self.x = read_fn(stream)
        self.y = read_fn(stream)

    def write(self, stream: BinaryIO) -> int:

        write_fn = write_double if self.uses_lwc() else write_float

        bytes_written = 0
        bytes_written += write_fn(stream, self.x)
        bytes_written += write_fn(stream, self.y)
        return bytes_written


# ============================================
# .
@dataclass
class ByteBlobStruct(StandardStructTrait):
    """Intended for deserialization_hints to allow circumventing unknown custom types in GVAS files."""

    type: Literal["ByteBlobStruct"] = "ByteBlobStruct"
    byte_blob: str = ""

    def read(self, stream: BinaryIO) -> None:

        # expect length in context
        context = ContextScopeTracker.get_hint_context()
        byte_count = context["byte_count"]
        self.byte_blob = read_bytes(stream, byte_count).hex()

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_bytes(stream, bytes.fromhex(self.byte_blob))
        return bytes_written


STANDARD_STRUCT_UNION = Union[
    DateTimeStruct,
    GuidStruct,
    IntPointStruct,
    LinearColorStruct,
    QuatStruct,
    RotatorStruct,
    TimespanStruct,
    VectorStruct,
    Vector2DStruct,
    ByteBlobStruct,
]

# ============================================
#
_standard_struct_type_map: dict[str, STANDARD_STRUCT_UNION] = {
    "Vector": VectorStruct,
    "Vector2D": Vector2DStruct,
    "Rotator": RotatorStruct,
    "Quat": QuatStruct,
    "LinearColor": LinearColorStruct,
    "IntPoint": IntPointStruct,
    "DateTime": DateTimeStruct,
    "Timespan": TimespanStruct,
    "Guid": GuidStruct,
    "ByteBlobStruct": ByteBlobStruct,
}


# ============================================
#
def is_standard_struct(type_name: str) -> bool:
    return type_name in _standard_struct_type_map.keys()


# ============================================
#
def get_standard_struct_instance(
    type_name: str, use_lwc: bool = False
) -> StandardStructTrait:
    # Map property types to their classes

    if type_name in _standard_struct_type_map.keys():
        property_encoding_class: STANDARD_STRUCT_UNION = _standard_struct_type_map.get(
            type_name
        )
        property_instance = property_encoding_class()
    else:
        print(f"Unknown special struct type: {type_name}")
        raise DeserializeError(f"Unknown special struct type: {type_name}")

    return property_instance
