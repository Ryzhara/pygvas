"""
Tests for StructProperty functionality
"""
import unittest
from io import BytesIO
import struct
from typing import Dict, Optional

from gvas.properties.property import Property, PropertyTrait, PropertyOptions
from gvas.properties.struct_property import StructProperty, StructPropertyValue
from gvas.properties.int_property import Int32Property, BoolProperty
from gvas.properties.str_property import StrProperty
from gvas.types import Guid
from gvas.utils import read_string, write_string

class TestStructProperty(unittest.TestCase):
    """Test StructProperty serialization and deserialization"""
    
    def test_create_struct_property(self):
        """Test creating a StructProperty"""
        # Create a new StructProperty
        struct_prop = StructProperty.new("TestStruct")
        
        # Check default values
        self.assertEqual(struct_prop.type_name, "TestStruct")
        self.assertIsNotNone(struct_prop.guid)
        self.assertTrue(struct_prop.guid.is_zero())
        self.assertIsNone(struct_prop.value)
        
        # Create a StructProperty with a custom GUID
        custom_guid = Guid(bytes.fromhex("12345678123456789ABC123456789ABC"))
        struct_prop = StructProperty.new("TestStruct", custom_guid)
        
        # Check custom values
        self.assertEqual(struct_prop.type_name, "TestStruct")
        self.assertEqual(struct_prop.guid, custom_guid)
        self.assertIsNone(struct_prop.value)
    
    def test_struct_property_with_values(self):
        """Test StructProperty with nested values"""
        # Create a StructProperty
        struct_prop = StructProperty.new("TestStruct")
        
        # Create a StructPropertyValue
        struct_value = StructPropertyValue.new("TestStruct")
        
        # Add some properties to the struct value
        struct_value.properties["IntValue"] = Property(
            type_name="Int32Property",
            value=Int32Property(value=42)
        )
        struct_value.properties["BoolValue"] = Property(
            type_name="BoolProperty",
            value=BoolProperty(value=True)
        )
        struct_value.properties["StringValue"] = Property(
            type_name="StrProperty",
            value=StrProperty(value="Hello, world!")
        )
        
        # Set the value on the struct property
        struct_prop.value = struct_value
        
        # Check the values
        self.assertEqual(struct_prop.value.type_name, "TestStruct")
        self.assertEqual(len(struct_prop.value.properties), 3)
        self.assertEqual(struct_prop.value.properties["IntValue"].value.value, 42)
        self.assertEqual(struct_prop.value.properties["BoolValue"].value.value, True)
        self.assertEqual(struct_prop.value.properties["StringValue"].value.value, "Hello, world!")
    
    def test_struct_property_roundtrip(self):
        """Test StructProperty serialization and deserialization"""
        # Create a StructProperty
        struct_prop = StructProperty.new("TestStruct")
        
        # Create a StructPropertyValue
        struct_value = StructPropertyValue.new("TestStruct")
        
        # Add some properties to the struct value
        struct_value.properties["IntValue"] = Property(
            type_name="Int32Property",
            value=Int32Property(value=42)
        )
        struct_value.properties["BoolValue"] = Property(
            type_name="BoolProperty",
            value=BoolProperty(value=True)
        )
        struct_value.properties["StringValue"] = Property(
            type_name="StrProperty",
            value=StrProperty(value="Hello, world!")
        )
        
        # Set the value on the struct property
        struct_prop.value = struct_value
        
        # Create options for serialization
        options = PropertyOptions()
        
        # Serialize the struct property
        stream = BytesIO()
        bytes_written = struct_prop.write(stream, options=options)
        
        # Reset the stream position
        stream.seek(0)
        
        # Deserialize the struct property
        deserialized_prop = StructProperty()
        deserialized_prop.read(stream, options=options)
        
        # Check the deserialized values
        self.assertEqual(deserialized_prop.type_name, "TestStruct")
        self.assertEqual(deserialized_prop.guid, struct_prop.guid)
        self.assertEqual(deserialized_prop.value.type_name, "TestStruct")
        self.assertEqual(len(deserialized_prop.value.properties), 3)
        self.assertEqual(deserialized_prop.value.properties["IntValue"].value.value, 42)
        self.assertEqual(deserialized_prop.value.properties["BoolValue"].value.value, True)
        self.assertEqual(deserialized_prop.value.properties["StringValue"].value.value, "Hello, world!")
    
    def test_nested_struct_property(self):
        """Test StructProperty with nested StructProperty"""
        # Create outer StructProperty
        outer_struct = StructProperty.new("OuterStruct")
        outer_value = StructPropertyValue.new("OuterStruct")
        
        # Create inner StructProperty
        inner_struct = StructProperty.new("InnerStruct")
        inner_value = StructPropertyValue.new("InnerStruct")
        
        # Add a property to the inner struct
        inner_value.properties["Value"] = Property(
            type_name="Int32Property",
            value=Int32Property(value=42)
        )
        
        # Set the inner struct value
        inner_struct.value = inner_value
        
        # Add the inner struct to the outer struct
        outer_value.properties["InnerStruct"] = Property(
            type_name="StructProperty",
            value=inner_struct
        )
        
        # Add a simple property to the outer struct
        outer_value.properties["Name"] = Property(
            type_name="StrProperty",
            value=StrProperty(value="Test")
        )
        
        # Set the outer struct value
        outer_struct.value = outer_value
        
        # Create options for serialization
        options = PropertyOptions()
        
        # Serialize the outer struct
        stream = BytesIO()
        bytes_written = outer_struct.write(stream, options=options)
        
        # Reset the stream position
        stream.seek(0)
        
        # Deserialize the outer struct
        deserialized_struct = StructProperty()
        deserialized_struct.read(stream, options=options)
        
        # Check the deserialized values
        self.assertEqual(deserialized_struct.type_name, "OuterStruct")
        self.assertEqual(len(deserialized_struct.value.properties), 2)
        self.assertEqual(deserialized_struct.value.properties["Name"].value.value, "Test")
        
        # Check the inner struct
        inner_prop = deserialized_struct.value.properties["InnerStruct"]
        self.assertEqual(inner_prop.type, "StructProperty")
        inner_struct = inner_prop.value
        self.assertEqual(inner_struct.type_name, "InnerStruct")
        self.assertEqual(len(inner_struct.value.properties), 1)
        self.assertEqual(inner_struct.value.properties["Value"].value.value, 42)

if __name__ == "__main__":
    unittest.main() 