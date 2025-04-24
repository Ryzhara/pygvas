"""
Tests for GVASFile functionality
"""

import unittest
from io import BytesIO
from typing import Union, override

from gvas.engine_tools import (
    FEngineVersion,
    CompressionType,
    GameVersion,
)
from gvas.gvas_file import GVASFile, GvasHeader, GameFileFormat
from gvas.gvas_utils import ContextScopeTracker
from gvas.properties.property_base import PropertyFactory, PropertyTrait
from gvas.properties.numerical_property import (
    Int32Property,
    BoolProperty,
    IntProperty,
    DoubleProperty,
)
from gvas.properties.str_property import StrProperty


class TestGvasFile(unittest.TestCase):
    """Test GVASFile functionality"""

    @classmethod
    @override
    def setUpClass(cls) -> None:
        ContextScopeTracker.set_inside_unit_tests()
        ContextScopeTracker.set_hints({})

    def test_10_create_file(self):
        # Test creating a GVASFile from scratch

        # create a game file format
        game_file_format = GameFileFormat(
            game_version=GameVersion.DEFAULT, compression_type=CompressionType.NONE
        )

        # Create a header
        header = GvasHeader(
            package_file_version=522,
            package_file_version_ue5=None,
            engine_version=FEngineVersion(
                major=4, minor=27, patch=2, change_list=0, branch="UE4"
            ),
            custom_version_format=0,
            custom_versions={},
            save_game_class_name="TestSaveGame",
        )

        # Create a new GVASFile
        file = GVASFile(game_file_format=game_file_format, header=header, properties={})

        # Set some properties
        int_property: Union[IntProperty, PropertyTrait] = (
            PropertyFactory.property_class_from_type("IntProperty")
        )
        int_property.value = 42
        file.properties["IntProperty"] = int_property

        file.properties["DoubleProperty"] = DoubleProperty(value=3.14)

        str_property: Union[StrProperty, PropertyTrait] = (
            PropertyFactory.property_class_from_type("StrProperty")
        )
        str_property.value = "Hello, world!"
        file.properties["StringProperty"] = str_property

        bool_property: Union[BoolProperty, PropertyTrait] = (
            PropertyFactory.property_class_from_type("BoolProperty")
        )
        bool_property.value = True
        file.properties["BoolProperty"] = bool_property

        expected_property_count = len(file.properties)

        # Serialize the file
        stream = BytesIO()
        file.write(stream)

        # Deserialize the file
        stream.seek(0)
        loaded_file, _original_stream = GVASFile.read(
            stream,
            game_version=GameVersion.DEFAULT,
            compression_type=CompressionType.NONE,
        )

        # Check that the properties match
        self.assertEqual(len(loaded_file.properties), expected_property_count)
        self.assertEqual(
            loaded_file.properties["IntProperty"].value,
            file.properties["IntProperty"].value,
        )
        self.assertEqual(
            loaded_file.properties["DoubleProperty"].value,
            file.properties["DoubleProperty"].value,
        )
        self.assertEqual(
            loaded_file.properties["StringProperty"].value,
            file.properties["StringProperty"].value,
        )
        self.assertEqual(
            loaded_file.properties["BoolProperty"].value,
            file.properties["BoolProperty"].value,
        )

    def test_20_file_header(self):
        # Test GVASFile header serialization

        # create a game file format
        game_file_format = GameFileFormat(
            game_version=GameVersion.DEFAULT, compression_type=CompressionType.NONE
        )

        # Create a header with custom values
        header = GvasHeader(
            package_file_version=123,
            package_file_version_ue5=None,
            engine_version=FEngineVersion(
                major=4, minor=27, patch=2, change_list=12345, branch="UE4"
            ),
            custom_version_format=5,
            custom_versions={},
            save_game_class_name="TestSaveGame",
        )

        # Create a new GVASFile
        file = GVASFile(game_file_format=game_file_format, header=header, properties={})

        # Add custom format data if needed
        # Note: This would need to be added to the actual implementation

        # Serialize the file
        stream = BytesIO()
        file.write(stream)

        # Deserialize the file
        stream.seek(0)
        loaded_file, _original_stream = GVASFile.read(
            stream, GameVersion.DEFAULT, CompressionType.NONE
        )

        # Check that the header values match
        self.assertEqual(
            loaded_file.header.package_file_version, header.package_file_version
        )
        self.assertEqual(
            loaded_file.header.engine_version.major, header.engine_version.major
        )
        self.assertEqual(
            loaded_file.header.engine_version.minor, header.engine_version.minor
        )
        self.assertEqual(
            loaded_file.header.engine_version.patch, header.engine_version.patch
        )
        self.assertEqual(
            loaded_file.header.engine_version.change_list,
            header.engine_version.change_list,
        )
        self.assertEqual(
            loaded_file.header.engine_version.branch, header.engine_version.branch
        )
        self.assertEqual(
            loaded_file.header.custom_version_format, header.custom_version_format
        )
        self.assertEqual(
            loaded_file.header.save_game_class_name, header.save_game_class_name
        )

    def test_30_game_version_handling(self):
        # Test handling different game versions
        # create a game file format
        game_file_format = GameFileFormat(
            game_version=GameVersion.DEFAULT, compression_type=CompressionType.NONE
        )

        # Create a header with custom values
        header = GvasHeader(
            package_file_version=522,
            package_file_version_ue5=None,
            engine_version=FEngineVersion(
                major=4, minor=27, patch=2, change_list=0, branch="UE4"
            ),
            custom_version_format=0,
            custom_versions={},
            save_game_class_name="TestSaveGame",
        )

        # Create a file with default game version
        file = GVASFile(game_file_format=game_file_format, header=header, properties={})

        file.properties["TestProperty"] = Int32Property(value=42)

        # Serialize with default game version
        default_stream = BytesIO()
        file.write(default_stream)

        # Deserialize with default game version
        default_stream.seek(0)
        default_file, _original_stream = GVASFile.read(
            default_stream, GameVersion.DEFAULT, CompressionType.NONE
        )

        # Check that the property was loaded correctly
        self.assertEqual(default_file.properties["TestProperty"].value, 42)


if __name__ == "__main__":
    unittest.main()
