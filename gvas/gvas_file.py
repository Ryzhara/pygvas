"""
Main GVAS file implementation
Python port of lib.rs

Key differences from Rust version:
- Uses Python's IO system
- Simplified compression handling
- Uses dataclasses for structured data
"""

import zlib
from io import BytesIO
from typing import Annotated

from pydantic import BaseModel
from pydantic import field_serializer, field_validator, Discriminator
from pydantic.dataclasses import dataclass

from gvas.engine_tools import (
    FEngineVersion,
    GameVersion,
    CompressionType,
    EngineVersionTool,
)
from gvas.gvas_utils import *
from gvas.properties.aggregators import (
    SetProperty,
    MapProperty,
    ArrayProperty,
    StructProperty,
)
from gvas.properties.delegate_property import (
    MulticastInlineDelegateProperty,
    MulticastSparseDelegateProperty,
    DelegateProperty,
)
from gvas.properties.enum_property import EnumProperty
from gvas.properties.field_path_property import FieldPathProperty, FieldPath
from gvas.properties.name_property import NameProperty
from gvas.properties.numerical_property import (
    BoolProperty,
    ByteProperty,
    Int8Property,
    UInt8Property,
    Int16Property,
    UInt16Property,
    Int32Property,
    UInt32Property,
    IntProperty,
    Int64Property,
    UInt64Property,
    FloatProperty,
    DoubleProperty,
)
from gvas.properties.object_property import ObjectProperty
from gvas.properties.property_base import PropertyFactory
from gvas.properties.standard_structs import (
    DateTimeStruct,
    GuidStruct,
    TimespanStruct,
    IntPointStruct,
    LinearColorStruct,
    RotatorStruct,
    QuatStruct,
    VectorStruct,
    Vector2DStruct,
)
from gvas.properties.str_property import StrProperty
from gvas.properties.text_property import TextProperty

UNREAL_ENGINE_PROPERTIES = Annotated[
    Union[
        # numerical types
        BoolProperty,
        ByteProperty,
        FloatProperty,
        DoubleProperty,
        IntProperty,
        Int8Property,
        UInt8Property,
        Int16Property,
        UInt16Property,
        Int32Property,
        UInt32Property,
        Int64Property,
        UInt64Property,
        FloatProperty,
        DoubleProperty,
        # standard types
        DateTimeStruct,
        GuidStruct,
        TimespanStruct,
        IntPointStruct,
        LinearColorStruct,
        RotatorStruct,
        QuatStruct,
        VectorStruct,
        Vector2DStruct,
        # aggregator property types
        SetProperty,
        MapProperty,
        StructProperty,
        ArrayProperty,
        # terminal property types
        EnumProperty,
        TextProperty,
        NameProperty,
        StrProperty,
        ObjectProperty,
        FieldPath,
        FieldPathProperty,
        MulticastInlineDelegateProperty,
        MulticastSparseDelegateProperty,
        DelegateProperty,
    ],
    Discriminator("type"),
]


@dataclass
class GvasHeader:
    type: str = "Unknown"
    package_file_version: int = None
    package_file_version_ue5: Optional[int] = None
    engine_version: FEngineVersion = None
    custom_version_format: int = None
    custom_versions: dict[str, int] = None
    save_game_class_name: str = None

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

    @classmethod
    def read(cls, stream: BinaryIO) -> "GvasHeader":
        """Read header from stream"""
        # Check magic number
        magic = stream.read(4)
        if magic != MagicConstants.GVAS_MAGIC:
            raise DeserializeError.invalid_header("Invalid magic number")

        # Read versions
        save_game_version = read_uint32(stream)
        if not 2 <= save_game_version <= 3:
            raise DeserializeError.invalid_header("Invalid save_game_version")

        package_file_version = read_uint32(stream)

        # Read UE5 version if present
        package_file_version_ue5 = None
        format_version = "Version2"
        if save_game_version >= 3:  # SaveGameVersion::PackageFileSummaryVersionChange
            package_file_version_ue5 = read_uint32(stream)
            format_version = "Version3"

        # Read engine version
        engine_version: FEngineVersion = FEngineVersion()
        engine_version.read(stream)

        # Read custom versions
        custom_version_format = read_uint32(stream)
        custom_version_count = read_uint32(stream)

        custom_version_reader = cls.FCustomVersion()
        custom_versions = {}
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
        bytes_written += stream.write(MagicConstants.GVAS_MAGIC)

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
            bytes_written += self.FCustomVersion(guid, version).write(stream)

        bytes_written += write_string(stream, self.save_game_class_name)

        return bytes_written


@dataclass
class GameFileFormat:
    """
    Holds information about the deserialized game version

    This is used to track what game version was used during deserialization,
    which may affect how the file is handled.
    """

    game_version: GameVersion = GameVersion.UNKNOWN
    compression_type: CompressionType = CompressionType.UNKNOWN

    @field_serializer("game_version")
    def serialize_game_version(self, game_version: GameVersion):
        return game_version.name

    @field_validator("game_version", mode="before")
    def validate_game_version(cls, value: GameVersion):
        if type(value) is str:
            return GameVersion.__getitem__(value)
        return value

    @field_serializer("compression_type")
    def serialize_compression_type(self, compression_type: CompressionType):
        return compression_type.name

    @field_validator("compression_type", mode="before")
    def validate_compression_type(cls, value: CompressionType):
        if type(value) is str:
            return CompressionType.__getitem__(value)
        return value

    @classmethod
    def has_gvas_header(cls, stream: BinaryIO) -> bool:
        peeked_bytes = peek(stream, 4)
        return peeked_bytes == MagicConstants.GVAS_MAGIC

    @classmethod
    def has_palworld_header(cls, stream: BinaryIO) -> bool:
        peeked_bytes = peek(stream, 4)
        return peeked_bytes == MagicConstants.PLZ_MAGIC

    @classmethod
    def has_zlib_header(cls, stream: BinaryIO) -> bool:
        magic_bytes: bytes = peek(stream, 2)
        return magic_bytes in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]

    @classmethod
    def is_definitely_zlib_compressed(cls, stream: BinaryIO):
        position = stream.tell()
        try:
            zlib.decompress(stream.read())
            return True
        except zlib.error:
            return False
        finally:
            stream.seek(position)

    def check_for_palworld(self, stream: BinaryIO) -> bool:

        current_position = stream.tell()
        try:
            # grab the elements
            decompressed_size = read_uint32(stream)
            compressed_size = read_uint32(stream)

            # sanity test
            sizes_ok = compressed_size <= decompressed_size < 1_000_000_000
            if not sizes_ok:
                return False

            if (
                _plz_bytes := read_bytes(stream, len(MagicConstants.PLZ_MAGIC))
            ) != MagicConstants.PLZ_MAGIC:
                return False

            self.game_version = GameVersion.PALWORLD

            # read the compression indicator
            compression_enum = read_int8(stream)
            try:
                self.compression_type = CompressionType(compression_enum)
                if self.compression_type not in [
                    CompressionType.NONE,
                    CompressionType.ZLIB,
                    CompressionType.ZLIB_TWICE,
                ]:
                    return False

            except ValueError:
                raise DeserializeError.invalid_value(
                    compression_enum,
                    current_position,
                    f"Unknown compression type found for file with Palworld MAGIC.",
                )

            if (
                self.compression_type == CompressionType.ZLIB
                and not self.has_zlib_header(stream)
            ):
                return False

            # NONE is fine, and ZLIP_TWICE will be caught later

            return True

        except zlib.error:
            return False

        finally:
            stream.seek(current_position)

    def deserialize_game_version(self, stream: BinaryIO, verbose: bool = False):
        is_palworld = False
        if self.has_gvas_header(stream):
            self.game_version = GameVersion.DEFAULT
            self.compression_type = CompressionType.NONE
        else:
            is_palworld = self.check_for_palworld(stream)

        if verbose:
            print(
                f"Found a {'PALWORLD' if is_palworld else 'GVAS'} file with compression type of '{self.compression_type.name}'."
            )


# @dataclass
class GVASFile(BaseModel):

    game_file_format: GameFileFormat
    header: GvasHeader
    properties: dict[str, UNREAL_ENGINE_PROPERTIES]

    @classmethod
    def print_game_file_format(cls, file_path: str):
        with open(file_path, "rb") as stream:
            game_file_format = GameFileFormat()
            game_file_format.deserialize_game_version(stream)
            print(
                f"Found {file_path=} has version={game_file_format.game_version} and compression={game_file_format.compression_type}"
            )

    @classmethod
    def read_file(cls, file_path: str) -> ("GVASFile", BinaryIO):
        with open(file_path, "rb") as stream:
            game_file_format = GameFileFormat()
            game_file_format.deserialize_game_version(stream)
            return cls.read(
                stream, game_file_format.game_version, game_file_format.compression_type
            )

    @classmethod
    def read(
        cls,
        stream: BinaryIO,
        game_version: GameVersion,
        compression_type: CompressionType,
    ) -> ("GVASFile", BinaryIO):

        decompressed_size = 0
        compressed_size = 0
        if game_version == GameVersion.PALWORLD:
            # we have to peek through custom file format. *sigh*
            decompressed_size = read_uint32(stream)
            compressed_size = read_uint32(stream)
            magic_bytes = stream.read(3)
            if magic_bytes == MagicConstants.PLZ_MAGIC:
                if not ContextScopeTracker.inside_unit_tests():
                    print(
                        f"Found PalWorld file with {decompressed_size=} and {compressed_size=}"
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
            decompressed_data = zlib.decompress(compressed_data)  # once
            decompressed_data = zlib.decompress(decompressed_data)  # twice

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

        # Set up version information for using during deserialization
        EngineVersionTool.set_engine_version(
            engine_major=header.engine_version.major,
            engine_minor=header.engine_version.minor,
        )
        EngineVersionTool.set_custom_versions(header.custom_versions)

        # Read all the top level file properties
        properties = {}
        while True:
            if (property_name := read_string(stream)) == "None":
                break
            with ContextScopeTracker(property_name):
                property_type = read_string(stream)
                property_value = PropertyFactory.create_and_deserialize(
                    stream, property_type, include_header=True
                )
                properties[property_name] = property_value

        read_uint32(stream, 0)

        stream.seek(0)
        return (
            cls(
                game_file_format=GameFileFormat(game_version, compression_type),
                header=header,
                properties=properties,
            ),
            stream,
        )

    def write_file(self, output_file, uncompressed_output_file) -> None:
        with open(output_file, "wb") as f:
            self.write(f, uncompressed_output_file)

    def write(
        self,
        stream: BinaryIO,
        uncompressed_file_name: str = None,
    ) -> None:
        """Write GVAS file to stream"""

        # First we serialize the content to UE format
        buffer = BytesIO()
        bytes_written = self.header.write(buffer)
        for name, property_instance in self.properties.items():
            bytes_written += write_string(buffer, name)
            property_instance.write(buffer, include_header=True)

        # Write None + NULL byte terminator for file end
        write_string(buffer, "None")
        write_uint32(buffer, 0)

        # Get buffer contents
        data_to_write = buffer.getvalue()

        decompressed_size = len(data_to_write)
        compressed_size = decompressed_size  # for no compression

        # ====================================
        # Handle compression options
        if self.game_file_format.compression_type == CompressionType.ZLIB_TWICE:
            # hack to save uncompressed
            if uncompressed_file_name:
                with open(uncompressed_file_name, "wb") as f:
                    f.write(data_to_write)

            data_to_write = zlib.compress(data_to_write)  # once
            first_compressed_size = len(data_to_write)

            data_to_write = zlib.compress(data_to_write)  # twice
            second_compressed_size = len(data_to_write)

            # tricky folks; they store the first compressed size, not the final
            compressed_size = first_compressed_size

        elif self.game_file_format.compression_type == CompressionType.ZLIB:
            if uncompressed_file_name:
                with open(uncompressed_file_name, "wb") as f:
                    f.write(data_to_write)
            data_to_write = zlib.compress(data_to_write)  # once
            compressed_size = len(data_to_write)

        elif self.game_file_format.compression_type == CompressionType.NONE:
            compressed_size = decompressed_size

        else:
            raise ValueError("Unknown compression type")

        # ====================================
        # Handle PalWorld special prefix
        if self.game_file_format.game_version == GameVersion.PALWORLD:
            if not ContextScopeTracker.inside_unit_tests():
                print(
                    f"Writing PalWorld file with {decompressed_size=} and {compressed_size=}"
                )
            write_uint32(stream, decompressed_size)
            write_uint32(stream, compressed_size)
            write_bytes(stream, MagicConstants.PLZ_MAGIC)
            write_int8(stream, self.game_file_format.compression_type.value)

        stream.write(data_to_write)
