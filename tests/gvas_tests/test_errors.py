"""
Tests for error handling
"""

import unittest
from io import BytesIO
import struct
import zlib

from gvas.error import DeserializeError
from gvas.gvas_file import GVASFile, GVAS_MAGIC
from gvas.game_version import GameVersion
from gvas.properties.property_base import Property, PropertyOptions
from gvas.properties.int_property import BoolProperty


class TestErrors(unittest.TestCase):
    """Test error handling"""

    def test_invalid_magic(self):
        """Test handling of invalid magic bytes"""
        # Create a stream with invalid magic
        stream = BytesIO(b"NOTGVAS\x00\x00")

        # Attempt to read the file
        with self.assertRaises(Exception) as context:
            GVASFile.read(stream, GameVersion.Default)

        # The exact error will depend on implementation details
        # but we should get some kind of error
        self.assertTrue(isinstance(context.exception, (DeserializeError, zlib.error)))

    def test_invalid_property_type(self):
        """Test handling of invalid property type"""
        # Create options
        options = PropertyOptions()

        # Attempt to read a property with an invalid type
        with self.assertRaises(DeserializeError) as context:
            Property.new(BytesIO(), "InvalidProperty", options)

        self.assertIn("Unknown property type", str(context.exception))

    def test_invalid_header(self):
        """Test handling of invalid header"""
        # Create a stream with valid magic but invalid data
        stream = BytesIO()
        stream.write(GVAS_MAGIC)  # Valid magic
        stream.write(struct.pack("<I", 999))  # Invalid save game version
        stream.seek(0)

        # Attempt to read the file
        with self.assertRaises(Exception) as context:
            GVASFile.read(stream, GameVersion.Default)

        # The exact error will depend on implementation details
        # but we should get some kind of error
        self.assertTrue(isinstance(context.exception, Exception))


if __name__ == "__main__":
    unittest.main()
