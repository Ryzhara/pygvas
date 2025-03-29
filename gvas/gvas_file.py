"""
Main GVAS file implementation
Python port of lib.rs

Key differences from Rust version:
- Uses Python's IO system
- Simplified compression handling
- Uses dataclasses for structured data
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, BinaryIO, List
import struct
import zlib
from io import BytesIO

from .error import DeserializeError, SerializeError
from .game_version import (
    GameVersion,
    DeserializedGameVersion,
    CompressionType,
    PLZ_MAGIC,
)
from .gvas_types import Guid, HashableIndexMap
from .properties import Property, SerializationHints
from .utils import *

# Magic number that appears at the start of every GVAS file
GVAS_MAGIC = b"GVAS"


@dataclass
class GvasHeader:
    """Header information for GVAS files"""

    package_file_version: int
    package_file_version_ue5: Optional[int]
    engine_version_major: int
    engine_version_minor: int
    engine_version_patch: int
    engine_version_build: int
    engine_version_branch: str
    custom_version_format: int
    custom_versions: HashableIndexMap[Guid, int]
    save_game_class_name: str

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
        if save_game_version >= 3:  # SaveGameVersion::PackageFileSummaryVersionChange
            package_file_version_ue5 = read_uint32(stream)

        # Read engine version
        engine_version_major = read_uint16(stream)
        engine_version_minor = read_uint16(stream)
        engine_version_patch = read_uint16(stream)
        engine_version_build = read_uint32(stream)

        # Read branch type_name
        engine_version_branch = read_string(stream)

        # Read custom versions
        custom_version_format = read_uint32(stream)
        custom_version_count = read_uint32(stream)

        custom_versions = HashableIndexMap()
        for _ in range(custom_version_count):
            guid_bytes = stream.read(16)
            version = read_uint32(stream)
            custom_versions[Guid.from_bytes(guid_bytes)] = version

        # Read save game class type_name
        save_game_class_name = read_string(stream)

        return cls(
            package_file_version=package_file_version,
            package_file_version_ue5=package_file_version_ue5,
            engine_version_major=engine_version_major,
            engine_version_minor=engine_version_minor,
            engine_version_patch=engine_version_patch,
            engine_version_build=engine_version_build,
            engine_version_branch=engine_version_branch,
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
        bytes_written += write_uint16(stream, self.engine_version_major)
        bytes_written += write_uint16(stream, self.engine_version_minor)
        bytes_written += write_uint16(stream, self.engine_version_patch)
        bytes_written += write_uint32(stream, self.engine_version_build)
        bytes_written += write_string(stream, self.engine_version_branch)

        # Write custom version GUIDs
        bytes_written += write_uint32(stream, self.custom_version_format)
        bytes_written += write_uint32(stream, len(self.custom_versions))

        for guid, version in self.custom_versions.items():
            bytes_written += write_bytes(stream, guid.to_bytes())
            bytes_written += write_uint32(stream, version)

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
    ) -> "GVASFile":

        # print(f"Now inside read()")

        """Read GVAS file from stream"""
        if game_version == GameVersion.PALWORLD:
            magic = stream.read(4)
            if magic == PLZ_MAGIC:
                print("Found PLZ MAGIC")
                compression_type = CompressionType.PLZ
            else:
                print(f"Tested MAGIC {magic=}")
                stream.seek(-4, 1)  # Rewind

        # Handle compression
        if compression_type == CompressionType.PLZ:
            # TODO: Implement PLZ decompression
            raise NotImplementedError("PLZ compression not yet supported")
        elif compression_type == CompressionType.ZLIB:
            raise NotImplementedError("PLZ compression not yet supported")
            # Read compressed size
            compressed_size = struct.unpack("<Q", stream.read(8))[0]

            # Read and decompress data
            compressed_data = stream.read(compressed_size)
            decompressed_data = zlib.decompress(compressed_data)

            # Create new stream from decompressed data
            stream = BytesIO(decompressed_data)

        # Read header
        header = GvasHeader.read(stream)
        # set up hints for use during serialization
        SerializationHints.set_engine_version(
            header.engine_version_major,
            header.engine_version_minor,
            header.engine_version_patch,
            header.engine_version_build,
        )

        # Read properties
        properties = {}
        while True:
            # Read property type_name
            name = read_string(stream)
            if name in ["", "None"]:
                # print(f"No more properties to read")
                break

            # Read property type
            prop_type = read_string(stream)

            # print(f"Reading {name=} and {prop_type=}")

            # Read property
            prop = Property.new(stream, prop_type, include_header=True)
            properties[name] = prop

        # print(f"Read header and {len(properties)=} from stream")
        return cls(header=header, properties=properties)

    def write(self, stream: BinaryIO, game_version: GameVersion) -> None:
        """Write GVAS file to stream"""
        # Create temporary buffer for compression
        buffer = BytesIO()

        # Write header
        bytes_written = self.header.write(buffer)
        # print(f"Header {bytes_written=}")

        # Write properties
        # print(f"Writing property count: {len(self.properties.items())}")
        for name, prop in self.properties.items():
            # Write property type_name
            bytes_written += write_string(buffer, name)

            # Write property
            prop.write(buffer, include_header=True)

        # Write None + NULL byte terminator for file
        write_string(buffer, "None")
        buffer.write(struct.pack("<I", 0))

        # Get buffer contents
        data = buffer.getvalue()

        print(f"Total bytes written: {len(data)}")

        # Handle compression
        compression_type = game_version.get_compression_type()
        if compression_type == CompressionType.PLZ:
            # TODO: Implement PLZ compression
            raise NotImplementedError("PLZ compression not yet supported")
        elif compression_type == CompressionType.ZLIB:
            assert False, "ZLIB is not tested!"
            # Write PLZ magic if needed
            if game_version == GameVersion.PALWORLD:
                assert False, "PALWORLD is not tested!"
                stream.write(PLZ_MAGIC)

            # Compress data
            compressed_data = zlib.compress(data)

            # Write compressed size and data
            stream.write(struct.pack("<Q", len(compressed_data)))
            stream.write(compressed_data)
        else:
            # Write uncompressed
            print(f"Writing data")
            stream.write(data)
