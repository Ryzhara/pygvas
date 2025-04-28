"""
Tests for property functionality
"""

import unittest
from io import BytesIO
from typing import override

from gvas.gvas_utils import read_string, ContextScopeTracker, UnitTestGlobals
from gvas.properties.enum_property import EnumProperty
from gvas.properties.numerical_properties import (
    BoolProperty,
    ByteProperty,
    Int8Property,
    Int16Property,
    Int32Property,
    IntProperty,
    Int64Property,
    UInt8Property,
    UInt16Property,
    UInt32Property,
    UInt64Property,
    FloatProperty,
    DoubleProperty,
)
from gvas.properties.property_base import PropertyFactory, PropertyTrait
from gvas.properties.str_property import StrProperty


class TestProperty(unittest.TestCase):
    """Test property serialization and deserialization"""

    @classmethod
    @override
    def setUpClass(cls) -> None:
        UnitTestGlobals.set_inside_unit_tests()
        ContextScopeTracker.set_deserialization_hints({})

    def perform_property_roundtrip_test(
        self, test_property: PropertyTrait, property_type: str, places: int = 7
    ):
        """
        Test that a property can be serialized and deserialized correctly

        Args:
            test_property: The property to test
            property_type: The type type_name of the property
        """

        # Export the property to a byte array
        buffer = BytesIO()
        bytes_written = test_property.write(buffer, include_header=True)

        buffer.seek(0)  # start at beginning
        imported_type = read_string(buffer)  # Normally done by GVAS file
        self.assertEqual(
            imported_type,
            property_type,
            f"Expected {property_type}, got {imported_type}",
        )
        # read the rest of the property
        imported_property = PropertyFactory.create_and_deserialize(
            buffer, imported_type, include_header=True
        )
        # this works for all properties that store in "value", as opposed to "values" or "delegates
        error_msg = (
            f"Properties don't match: {test_property.value} != {imported_property.value}",
        )
        if type(test_property.value) == float:
            self.assertAlmostEqual(
                test_property.value,
                imported_property.value,
                places=places,
                msg=error_msg,
            )
        else:
            self.assertEqual(test_property.value, imported_property.value, error_msg)

    def test_010_bool_property(self):
        # Test BoolProperty serialization/deserialization
        self.perform_property_roundtrip_test(BoolProperty(value=True), "BoolProperty")
        self.perform_property_roundtrip_test(BoolProperty(value=False), "BoolProperty")

    def test_020_byte_property(self):
        # Test ByteProperty serialization/deserialization
        # Test with byte value
        byte_property = ByteProperty()
        byte_property.name = None
        # Use BytePropertyValue.Byte.value instead of calling it
        byte_property.value = 1
        self.perform_property_roundtrip_test(byte_property, "ByteProperty")

        # Test with namespaced value
        namespaced_property = ByteProperty()
        namespaced_property.name = "TestName"
        # Use a string value for namespaced value
        namespaced_property.value = "TestValue"
        self.perform_property_roundtrip_test(namespaced_property, "ByteProperty")

    def test_030_int_properties(self):
        # Test integer property serialization/deserialization
        self.perform_property_roundtrip_test(Int8Property(value=42), "Int8Property")
        self.perform_property_roundtrip_test(Int8Property(value=-42), "Int8Property")
        self.perform_property_roundtrip_test(Int16Property(value=1000), "Int16Property")
        self.perform_property_roundtrip_test(
            Int16Property(value=-1000), "Int16Property"
        )
        self.perform_property_roundtrip_test(
            Int32Property(value=100000), "Int32Property"
        )
        self.perform_property_roundtrip_test(IntProperty(value=-100000), "IntProperty")
        self.perform_property_roundtrip_test(
            Int64Property(value=-10000000000), "Int64Property"
        )
        self.perform_property_roundtrip_test(
            Int64Property(value=-10000000000), "Int64Property"
        )

        self.perform_property_roundtrip_test(UInt8Property(value=200), "UInt8Property")
        self.perform_property_roundtrip_test(
            UInt16Property(value=60000), "UInt16Property"
        )
        self.perform_property_roundtrip_test(
            UInt32Property(value=4000000000), "UInt32Property"
        )
        self.perform_property_roundtrip_test(
            UInt64Property(value=10000000000000000000), "UInt64Property"
        )

    def test_040__float_property(self):
        # Test FloatProperty serialization/deserialization"
        self.perform_property_roundtrip_test(
            FloatProperty(value=3.14159), "FloatProperty", places=5
        )
        self.perform_property_roundtrip_test(
            FloatProperty(value=31.4159), "FloatProperty", places=4
        )
        self.perform_property_roundtrip_test(
            FloatProperty(value=31415.9), "FloatProperty", places=1
        )
        self.perform_property_roundtrip_test(
            FloatProperty(value=314159.0), "FloatProperty", places=1
        )
        self.perform_property_roundtrip_test(
            FloatProperty(value=-2.71828), "FloatProperty", places=5
        )

    def test_050__double_property(self):
        # Test FloatProperty serialization/deserialization
        self.perform_property_roundtrip_test(
            DoubleProperty(value=3.141592653589793), "DoubleProperty", places=16
        )
        self.perform_property_roundtrip_test(
            DoubleProperty(value=-2.718281828459045), "DoubleProperty", places=16
        )

    def test_060__str_property(self):
        # Test StrProperty serialization/deserialization
        self.perform_property_roundtrip_test(
            StrProperty(value="Hello, world!"), "StrProperty"
        )
        self.perform_property_roundtrip_test(StrProperty(value=None), "StrProperty")

    def test_070_enum_property(self):
        # Test EnumProperty serialization/deserialization
        enum_property = EnumProperty()
        enum_property.enum_type = "TestEnum"
        enum_property.value = "TestValue"
        self.perform_property_roundtrip_test(enum_property, "EnumProperty")

        enum_prop2 = EnumProperty()
        enum_prop2.enum_type = None
        enum_prop2.value = "TestValue"
        self.perform_property_roundtrip_test(enum_prop2, "EnumProperty")


if __name__ == "__main__":
    unittest.main()
