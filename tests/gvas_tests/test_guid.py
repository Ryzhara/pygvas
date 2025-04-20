"""
Tests for GUID functionality
"""

import unittest
from io import BytesIO
import uuid

from gvas.gvas_utils import ZERO_GUID, write_guid, read_guid


class TestGuid(unittest.TestCase):
    """Test GUID functionality"""

    def test_guid_creation(self):
        """Test creating GUIDs"""
        # Create a zero GUID
        guid = ZERO_GUID
        self.assertEqual(str(guid), "00000000-0000-0000-0000-000000000000")
        self.assertTrue(guid == ZERO_GUID)

        # Create a GUID from UUID
        test_uuid = uuid.UUID("12345678-1234-5678-9ABC-123456789ABC")
        guid = uuid.UUID(test_uuid)
        self.assertEqual(str(guid).lower(), "12345678-1234-5678-9abc-123456789abc")
        self.assertFalse(guid == ZERO_GUID)

        # Create a GUID from bytes
        # Note: The byte order is different in UE format
        guid_bytes = bytes.fromhex("78563412341278569ABC123456789ABC")
        guid = uuid.UUID(bytes=guid_bytes)
        self.assertEqual(str(guid).lower(), "12345678-1234-5678-9abc-123456789abc")

    def test_guid_equality(self):
        """Test GUID equality"""
        guid1 = uuid.UUID("12345678-1234-5678-9ABC-123456789ABC")
        guid2 = uuid.UUID("12345678-1234-5678-9ABC-123456789ABC")
        guid3 = uuid.UUID("87654321-4321-8765-CBA9-CBA987654321")

        self.assertEqual(guid1, guid2)
        self.assertNotEqual(guid1, guid3)

        # Test hash equality
        guid_dict = {guid1: "value1", guid3: "value3"}
        self.assertEqual(guid_dict[guid1], "value1")

    def test_guid_serialization(self):
        """Test GUID serialization and deserialization"""
        original_guid = uuid.UUID("12345678-1234-5678-9ABC-123456789ABC")

        # Serialize to bytes
        bytes_data = original_guid.bytes
        self.assertEqual(len(bytes_data), 16)

        # Deserialize from bytes
        deserialized_guid = uuid.UUID(bytes=bytes_data)
        self.assertEqual(original_guid, deserialized_guid)

        # Test stream serialization
        stream = BytesIO()
        write_guid(stream, original_guid)
        stream.seek(0)

        # bytes_read = stream.read(16)
        deserialized_guid = read_guid(stream)
        self.assertEqual(original_guid, deserialized_guid)


if __name__ == "__main__":
    unittest.main()
