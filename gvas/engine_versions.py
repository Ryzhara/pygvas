# Engine version information
import enum
from dataclasses import dataclass

from .utils import *


# UE4 Engine version enum
class EngineVersion(enum.Enum):
    # Unknown
    UNKNOWN = (-1, -1)
    # Oldest loadable package
    VER_UE4_OLDEST_LOADABLE_PACKAGE = (4, 0)

    VER_UE4_0 = (4, 0)
    VER_UE4_1 = (4, 1)
    VER_UE4_2 = (4, 2)
    VER_UE4_3 = (4, 3)
    VER_UE4_4 = (4, 4)
    VER_UE4_5 = (4, 5)
    VER_UE4_6 = (4, 6)
    VER_UE4_7 = (4, 7)
    VER_UE4_8 = (4, 8)
    VER_UE4_9 = (4, 9)
    VER_UE4_10 = (4, 10)
    VER_UE4_11 = (4, 11)
    VER_UE4_12 = (4, 12)
    VER_UE4_13 = (4, 13)
    VER_UE4_14 = (4, 14)
    VER_UE4_15 = (4, 15)
    VER_UE4_16 = (4, 16)
    VER_UE4_17 = (4, 17)
    VER_UE4_18 = (4, 18)
    VER_UE4_19 = (4, 19)
    VER_UE4_20 = (4, 20)
    VER_UE4_21 = (4, 21)
    VER_UE4_22 = (4, 22)
    VER_UE4_23 = (4, 23)
    VER_UE4_24 = (4, 24)
    VER_UE4_25 = (4, 25)
    VER_UE4_26 = (4, 26)
    VER_UE4_27 = (4, 27)

    VER_UE5_0 = (5, 0)
    VER_UE5_1 = (5, 1)
    VER_UE5_2 = (5, 2)

    # The newest specified version of the Unreal Engine.
    VER_UE4_AUTOMATIC_VERSION = (4, 27)
    # Version plus one
    VER_UE4_AUTOMATIC_VERSION_PLUS_ONE = (4, 28)


# Stores UE4 version in which the GVAS file was saved
@dataclass
class FEngineVersion:
    # Major version number.
    major: int  # u16
    # Minor version number.
    minor: int  # u16
    # Patch version number.
    patch: int  # u16
    # Build id.
    change_list: int  # u32
    # Build id string.
    branch: str  # String

    @classmethod
    def new(
        cls, major: int, minor: int, patch: int, change_list: int, branch: str
    ) -> "FEngineVersion":
        return FEngineVersion(major, minor, patch, change_list, branch)

    def format(self):
        return (
            f"{self.major}.{self.minor}.{self.patch}-{self.change_list}+++{self.branch}"
        )

    @classmethod
    def read(cls, stream: BinaryIO) -> "FEngineVersion":
        major = read_uint16(stream)
        minor = read_uint16(stream)
        patch = read_uint16(stream)
        change_list = read_uint32(stream)
        branch = read_string(stream)
        return cls.new(major, minor, patch, change_list, branch)

    # Write FEngineVersion to a binary file
    # [inline]
    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_uint16(stream, self.major)
        bytes_written += write_uint16(stream, self.minor)
        bytes_written += write_uint16(stream, self.patch)
        bytes_written += write_uint32(stream, self.change_list)
        bytes_written += write_string(stream, self.branch)
        return bytes_written

    # Get [`EngineVersion`]
    def get_version(self) -> EngineVersion:
        try:
            result = EngineVersion((self.major, self.minor))
        except ValueError:
            result = EngineVersion.UNKNOWN
        return result
