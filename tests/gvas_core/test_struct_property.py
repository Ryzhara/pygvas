"""
Tests for StructProperty functionality
"""

import unittest
import uuid
from io import BytesIO
from typing import override

from gvas.engine_tools import SerializationTools
from gvas.gvas_utils import ZERO_GUID, read_string
from gvas.properties.aggregators import StructProperty
from gvas.properties.numerical_property import Int32Property, BoolProperty
from gvas.properties.str_property import StrProperty


class TestStructProperty(unittest.TestCase):
    """Test StructProperty serialization and deserialization"""

    @classmethod
    @override
    def setUpClass(cls) -> None:
        SerializationTools.set_inside_unit_tests()
        SerializationTools.hints = {}

    def test_create_struct_property(self):
        """Test creating a StructProperty"""
        # Create a new StructProperty
        struct_prop = StructProperty(type_name="TestStruct", guid=ZERO_GUID)

        # Check default values
        self.assertEqual(struct_prop.type_name, "TestStruct")
        self.assertIsNotNone(struct_prop.guid)
        self.assertTrue(struct_prop.guid == ZERO_GUID)
        self.assertIsNone(struct_prop.value)

        # Create a StructProperty with a custom GUID
        custom_guid = uuid.UUID(
            bytes_le=bytes.fromhex("12345678123456789ABC123456789ABC")
        )
        struct_prop = StructProperty(type_name="TestStruct", guid=custom_guid)

        # Check custom values
        self.assertEqual(struct_prop.type_name, "TestStruct")
        self.assertEqual(struct_prop.guid, custom_guid)
        self.assertIsNone(struct_prop.value)

    def test_struct_property_with_values(self):
        """Test StructProperty with nested values"""
        # Create a StructProperty
        struct_prop = StructProperty(type_name="TestStruct", value={})

        # Add some properties to the struct value
        struct_prop.value["IntValue"] = Int32Property(value=42)
        struct_prop.value["BoolValue"] = BoolProperty(value=True)
        struct_prop.value["StringValue"] = StrProperty(value="Hello, world!")

        # Check the values
        self.assertEqual(struct_prop.type_name, "TestStruct")
        self.assertEqual(len(struct_prop.value), 3)
        self.assertEqual(struct_prop.value["IntValue"].value, 42)
        self.assertEqual(struct_prop.value["BoolValue"].value, True)
        self.assertEqual(struct_prop.value["StringValue"].value, "Hello, world!")

    def test_struct_property_roundtrip(self):
        """Test StructProperty serialization and deserialization"""
        # Create a StructProperty
        struct_prop = StructProperty(type_name="TestStruct", guid=ZERO_GUID, value={})

        # Add some properties to the struct value
        struct_prop.value["IntValue"] = Int32Property(value=42)
        struct_prop.value["BoolValue"] = BoolProperty(value=True)
        struct_prop.value["StringValue"] = StrProperty(value="Hello, world!")

        # Serialize the struct property with and without a standard header
        for include_header in [False, True]:
            stream = BytesIO()
            bytes_written = struct_prop.write(stream, include_header=include_header)
            stream.seek(0)  # Reset the stream position

            # Deserialize the struct property
            deserialized_prop = StructProperty()
            if include_header:
                property_type = read_string(stream)
                self.assertEqual(property_type, struct_prop.type)

            deserialized_prop.read(stream, include_header=include_header)

            # Check the deserialized values
            self.assertEqual(
                deserialized_prop.type_name,
                "TestStruct" if include_header else None,
                "Testing with standard header",
            )

            self.assertEqual(
                deserialized_prop.guid,
                None,
                f"Testing with {include_header=}. We drop ZERO guids on reads because it saves space.",
            )

            self.assertEqual(len(deserialized_prop.value), 3)
            self.assertEqual(deserialized_prop.value["IntValue"].value, 42)
            self.assertEqual(deserialized_prop.value["BoolValue"].value, True)
            self.assertEqual(
                deserialized_prop.value["StringValue"].value,
                "Hello, world!",
            )

    def test_nested_struct_property(self):
        """Test StructProperty with nested StructProperty"""
        # Create outer StructProperty
        outer_struct = StructProperty(type_name="OuterStruct", value={})

        # Create inner StructProperty
        inner_struct = StructProperty(type_name="InnerStruct", value={})

        # Add a property to the inner struct
        inner_struct.value["Value"] = Int32Property(value=42)

        # Add the inner struct to the outer struct
        outer_struct.value["InnerStruct"] = inner_struct

        # Add a simple property to the outer struct
        outer_struct.value["Name"] = StrProperty(value="Test")

        for include_header in [False, True]:
            # Serialize the outer struct
            stream = BytesIO()
            bytes_written = outer_struct.write(stream, include_header=include_header)
            stream.seek(0)  # Reset the stream position

            # Deserialize the outer struct
            deserialized_struct = StructProperty(type_name="OuterStruct")
            if include_header:
                property_type = read_string(stream)
                self.assertEqual(property_type, deserialized_struct.type)

            deserialized_struct.read(stream, include_header=include_header)

            # Check the deserialized values
            self.assertEqual(deserialized_struct.type_name, "OuterStruct")
            self.assertEqual(len(deserialized_struct.value), 2)
            self.assertEqual(deserialized_struct.value["Name"].value, "Test")

            # Check the inner struct
            inner_struct = deserialized_struct.value["InnerStruct"]
            self.assertEqual(inner_struct.type, "StructProperty")
            self.assertEqual(inner_struct.type_name, "InnerStruct")
            self.assertEqual(len(inner_struct.value), 1)
            self.assertEqual(inner_struct.value["Value"].value, 42)


if __name__ == "__main__":
    unittest.main()
