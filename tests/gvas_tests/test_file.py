"""
Tests for GVASFile functionality
"""

import unittest
from io import BytesIO
import struct
from typing import Dict, List

from gvas.gvas_file import GVASFile, GvasHeader
from gvas.game_version import GameVersion
from gvas.properties.property_base import Property
from gvas.properties.int_property import Int32Property, BoolProperty
from gvas.properties.str_property import StrProperty
from gvas.gvas_types import HashableIndexMap


class TestGvasFile(unittest.TestCase):
    """Test GVASFile functionality"""

    def test_create_file(self):
        """Test creating a GVASFile from scratch"""
        # Create a header
        header = GvasHeader(
            package_file_version=522,
            package_file_version_ue5=None,
            engine_version_major=4,
            engine_version_minor=27,
            engine_version_patch=2,
            engine_version_build=0,
            engine_version_branch="UE4",
            custom_version_format=0,
            custom_versions=HashableIndexMap(),
            save_game_class_name="TestSaveGame",
        )

        # Create a new GVASFile
        file = GVASFile(header=header, properties={})

        # Set some properties
        file.properties["IntProperty"] = Property(
            type_name="Int32Property", value=Int32Property(42)
        )
        file.properties["StringProperty"] = Property(
            type_name="StrProperty", value=StrProperty("Hello, world!")
        )
        file.properties["BoolProperty"] = Property(
            type_name="BoolProperty", value=BoolProperty(True)
        )

        # Serialize the file
        stream = BytesIO()
        file.write(stream, GameVersion.Default)

        # Deserialize the file
        stream.seek(0)
        loaded_file = GVASFile.read(stream, GameVersion.Default)

        # Check that the properties match
        self.assertEqual(len(loaded_file.properties), 3)
        self.assertEqual(loaded_file.properties["IntProperty"].value.value, 42)
        self.assertEqual(
            loaded_file.properties["StringProperty"].value.value, "Hello, world!"
        )
        self.assertEqual(loaded_file.properties["BoolProperty"].value.value, True)

    def test_file_header(self):
        """Test GVASFile header serialization"""
        # Create a header with custom values
        header = GvasHeader(
            package_file_version=123,
            package_file_version_ue5=None,
            engine_version_major=4,
            engine_version_minor=27,
            engine_version_patch=2,
            engine_version_build=12345,
            engine_version_branch="UE4",
            custom_version_format=5,
            custom_versions=HashableIndexMap(),
            save_game_class_name="TestSaveGame",
        )

        # Create a new GVASFile
        file = GVASFile(header=header, properties={})

        # Add custom format data if needed
        # Note: This would need to be added to the actual implementation

        # Serialize the file
        stream = BytesIO()
        file.write(stream, GameVersion.Default)

        # Deserialize the file
        stream.seek(0)
        loaded_file = GVASFile.read(stream, GameVersion.Default)

        # Check that the header values match
        self.assertEqual(loaded_file.header.package_file_version, 123)
        self.assertEqual(loaded_file.header.engine_version_major, 4)
        self.assertEqual(loaded_file.header.engine_version_minor, 27)
        self.assertEqual(loaded_file.header.engine_version_patch, 2)
        self.assertEqual(loaded_file.header.engine_version_build, 12345)
        self.assertEqual(loaded_file.header.engine_version_branch, "UE4")
        self.assertEqual(loaded_file.header.custom_version_format, 5)

    def test_game_version_handling(self):
        """Test handling different game versions"""
        # Create a header
        header = GvasHeader(
            package_file_version=522,
            package_file_version_ue5=None,
            engine_version_major=4,
            engine_version_minor=27,
            engine_version_patch=2,
            engine_version_build=0,
            engine_version_branch="UE4",
            custom_version_format=0,
            custom_versions=HashableIndexMap(),
            save_game_class_name="TestSaveGame",
        )

        # Create a file with default game version
        file = GVASFile(header=header, properties={})
        file.properties["TestProperty"] = Property(
            type_name="Int32Property", value=Int32Property(42)
        )

        # Serialize with default game version
        default_stream = BytesIO()
        file.write(default_stream, GameVersion.Default)

        # Deserialize with default game version
        default_stream.seek(0)
        default_file = GVASFile.read(default_stream, GameVersion.Default)

        # Check that the property was loaded correctly
        self.assertEqual(default_file.properties["TestProperty"].value.value, 42)


if __name__ == "__main__":
    unittest.main()
