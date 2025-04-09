"""
Main GVAS file implementation
Python port of lib.rs

Key differences from Rust version:
- Uses Python's IO system
- Simplified compression handling
- Uses dataclasses for structured data
"""

import os
import zlib
from dataclasses import dataclass, asdict
from typing import Dict, Optional, BinaryIO, List

from io import BytesIO

from .error import DeserializeError, SerializeError
from .engine_versions import EngineVersion, FEngineVersion
from .game_version import GameVersion, CompressionType, GVAS_MAGIC, PLZ_MAGIC
from .gvas_types import HashableIndexMap
from .properties import Property
from .utils import *


# Stores CustomVersions serialized by UE4
@dataclass
class FCustomVersion:
    # Key
    key: str = None
    # Value
    version: int = 0

    # Read FCustomVersion from a binary file
    def read(self, stream: BinaryIO) -> None:
        self.key = guid_to_str(read_guid(stream))
        self.version = read_uint32(stream)

    # Write FCustomVersion to a binary file
    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        guid = uuid.UUID(self.key)
        bytes_written += write_guid(stream, guid)
        bytes_written += write_int32(stream, self.version)
        return bytes_written


# ============================================
#
def is_zlib_compressed(data):
    """
    Checks if the data is likely zlib compressed based on the initial bytes.

    Args:
        data: The bytes-like object to check.

    Returns:
        True if the data is likely zlib compressed, False otherwise.
    """
    if len(data) < 2:
        return False
    return data[:2] in (b"\x78\x01", b"\x78\x9c", b"\x78\xda")


def is_definitely_zlib_compressed(data):
    """
    Checks if the data is definitely zlib compressed by attempting decompression.

    Args:
        data: The bytes-like object to check.

    Returns:
        True if the data is definitely zlib compressed, False otherwise.
    """
    try:
        zlib.decompress(data)
        return True
    except zlib.error:
        return False


# ============================================
#
def looks_like_gvas(stream: BinaryIO) -> bool:
    peeked_bytes = peek(stream, 4)
    return peeked_bytes == GVAS_MAGIC


# ============================================
#
def looks_like_palworld(stream: BinaryIO) -> bool:

    current_position = stream.tell()
    # grab the elements
    decompressed_size = read_uint32(stream)
    compressed_size = read_uint32(stream)
    plz_bytes = read_bytes(stream, len(PLZ_MAGIC))
    enum_value = read_uint8(stream)
    stream.seek(current_position)

    # tests:
    sizes_ok = compressed_size <= decompressed_size < 1_000_000_000
    magic_ok = plz_bytes == PLZ_MAGIC
    enum_ok = enum_value in [member.value for member in CompressionType]
    return sizes_ok and magic_ok and enum_ok


@dataclass
class GvasHeader:
    """Header information for GVAS files"""

    type: str = "Unknown"
    package_file_version: int = None
    package_file_version_ue5: Optional[int] = None
    engine_version: FEngineVersion = None
    custom_version_format: int = None
    custom_versions: HashableIndexMap[str, int] = None
    save_game_class_name: str = None

    @classmethod
    def read(cls, stream: BinaryIO) -> "GvasHeader":
        """Read header from stream"""
        # Check magic number
        magic = stream.read(4)
        if magic != GVAS_MAGIC:
            raise DeserializeError.invalid_header("Invalid magic number")

        # Read versions
        save_game_version = read_uint32(stream)
        package_file_version = read_uint32(stream)

        # Read UE5 version if present
        package_file_version_ue5 = None
        format_version = "Version2"
        if save_game_version >= 3:  # SaveGameVersion::PackageFileSummaryVersionChange
            package_file_version_ue5 = read_uint32(stream)
            format_version = "Version3"

        # Read engine version
        engine_version: FEngineVersion = FEngineVersion.read(stream)

        # Read custom versions
        custom_version_format = read_uint32(stream)
        custom_version_count = read_uint32(stream)

        custom_version_reader = FCustomVersion()
        custom_versions = HashableIndexMap()
        for _ in range(custom_version_count):
            custom_version_reader.read(stream)
            custom_versions[custom_version_reader.key] = custom_version_reader.version

        # Read save game class type_name
        save_game_class_name = read_string(stream)

        return cls(
            type=format_version,
            package_file_version=package_file_version,
            package_file_version_ue5=package_file_version_ue5,
            engine_version=engine_version,
            custom_version_format=custom_version_format,
            custom_versions=custom_versions,
            save_game_class_name=save_game_class_name,
        )

    def write(self, stream: BinaryIO) -> int:
        """Write header to stream"""
        bytes_written = 0

        # Write magic number
        bytes_written += stream.write(GVAS_MAGIC)

        # Write versions
        bytes_written += write_uint32(stream, 3 if self.package_file_version_ue5 else 2)
        bytes_written += write_uint32(stream, self.package_file_version)

        # Write UE5 version if present
        if self.package_file_version_ue5 is not None:
            bytes_written += write_uint32(stream, self.package_file_version_ue5)

        # Write engine version data
        bytes_written += self.engine_version.write(stream)

        # Write custom version GUIDs
        bytes_written += write_uint32(stream, self.custom_version_format)
        bytes_written += write_uint32(stream, len(self.custom_versions))

        for guid, version in self.custom_versions.items():
            bytes_written += FCustomVersion(guid, version).write(stream)

        bytes_written += write_string(stream, self.save_game_class_name)

        return bytes_written


@dataclass
class GVASFile:
    """Main GVAS file class"""

    header: GvasHeader
    properties: Dict[str, Property]

    @classmethod
    def read(
        cls,
        stream: BinaryIO,
        game_version: GameVersion,
        compression_type: CompressionType,
    ) -> ("GVASFile", BinaryIO):

        if game_version == GameVersion.PALWORLD:
            # we have to peek through custom file format. *sigh*
            decompressed_size = read_uint32(stream)
            compressed_size = read_uint32(stream)
            print(f"Found: {decompressed_size=} and {compressed_size=}")
            magic_bytes = stream.read(3)
            if magic_bytes == PLZ_MAGIC:
                print(
                    f"Found PLZ MAGIC for PalWorld with {decompressed_size=} and {compressed_size=}"
                )
                enum_value = read_int8(stream)
                match enum_value:
                    case CompressionType.NONE.value:
                        compression_type = CompressionType.NONE
                    case CompressionType.ZLIB.value:
                        compression_type = CompressionType.ZLIB
                    case CompressionType.ZLIB_TWICE.value:
                        compression_type = CompressionType.ZLIB_TWICE
                    case _:
                        raise ValueError("Unknown compression type")

        # Handle compression options
        if compression_type == CompressionType.ZLIB_TWICE:
            compressed_data = stream.read()
            print(f"Found compressed data: {len(compressed_data)=}")
            decompressed_data = zlib.decompress(compressed_data)  # once
            first_compressed_size = len(decompressed_data)
            print(f"Found: {first_compressed_size=}")
            decompressed_data = zlib.decompress(decompressed_data)  # twice
            second_compressed_size = len(decompressed_data)
            print(f"Found: {second_compressed_size=}")

            assert decompressed_size == len(
                decompressed_data
            ), f"{decompressed_size=} != {len(decompressed_data)=}"

            # Create new stream from decompressed data
            stream = BytesIO(decompressed_data)

        elif compression_type == CompressionType.ZLIB:
            compressed_data = stream.read()
            decompressed_data = zlib.decompress(compressed_data)
            assert decompressed_size == len(
                decompressed_data
            ), f"{decompressed_size=} != {len(decompressed_data)=}"

            # Create new stream from decompressed data
            stream = BytesIO(decompressed_data)

        elif compression_type == CompressionType.NONE:
            pass

        else:
            raise ValueError("Unknown compression type")

        # Read header
        header = GvasHeader.read(stream)
        # print(header.engine_version)

        # set up hints for use during deserialization
        SerializationTools.set_custom_versions(header.custom_versions)

        # Read all the top level file properties
        properties = {}
        while True:
            if (property_name := read_string(stream)) == "None":
                break
            with ContextScopeTracker(property_name):
                property_type = read_string(stream)
                property_value = Property.new(
                    stream, property_type, include_header=True
                )
                properties[property_name] = property_value

        stream.seek(0)
        return cls(header=header, properties=properties), stream

    def write(
        self,
        stream: BinaryIO,
        game_version: GameVersion,
        compression_type: CompressionType,
        ucompressed_file_name: str = None,
    ) -> None:
        """Write GVAS file to stream"""

        # First we serialize the content to UE format
        buffer = BytesIO()
        bytes_written = self.header.write(buffer)
        for name, prop in self.properties.items():
            bytes_written += write_string(buffer, name)
            prop.write(buffer, include_header=True)

        # Write None + NULL byte terminator for file end
        write_string(buffer, "None")
        buffer.write(struct.pack("<I", 0))

        # Get buffer contents
        data_to_write = buffer.getvalue()

        decompressed_size = len(data_to_write)
        compressed_size = decompressed_size  # for no compression

        # ====================================
        # Handle compression options
        if compression_type == CompressionType.ZLIB_TWICE:
            # hack to save uncompressed
            if ucompressed_file_name:
                print(f"Writing {ucompressed_file_name}")
                with open(ucompressed_file_name, "wb") as f:
                    f.write(data_to_write)

            data_to_write = zlib.compress(data_to_write)  # once
            first_compressed_size = len(data_to_write)
            print(f"We have: {first_compressed_size=}")

            data_to_write = zlib.compress(data_to_write)  # twice
            second_compressed_size = len(data_to_write)
            print(f"We have: {second_compressed_size=}")

            # tricky folks; they store the first compressed size, not the final
            compressed_size = first_compressed_size

        elif compression_type == CompressionType.ZLIB:
            print(f"Writing {ucompressed_file_name}")
            with open(ucompressed_file_name, "wb") as f:
                f.write(data_to_write)
            data_to_write = zlib.compress(data_to_write)  # once
            compressed_size = len(data_to_write)

        elif compression_type == CompressionType.NONE:
            compressed_size = decompressed_size

        else:
            raise ValueError("Unknown compression type")

        # ====================================
        # Handle PalWorld special prefix
        if game_version == GameVersion.PALWORLD:
            print(
                f"Writing PalWorld file with {decompressed_size=} and {compressed_size=}"
            )
            write_uint32(stream, decompressed_size)
            write_uint32(stream, compressed_size)
            write_bytes(stream, PLZ_MAGIC)
            write_uint8(stream, compression_type.value)

        stream.write(data_to_write)
