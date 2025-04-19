"""
Base PropertyFactory implementation for GVAS
Python port of properties/mod.rs
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO, List, Tuple
from pydantic.dataclasses import dataclass

from ..utils import *


# ============================================
#
class PropertyTrait(ABC):
    """
    Base trait/interface for Unreal specific property types
    """

    @abstractmethod
    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write property data to a binary stream"""
        pass


@dataclass
class PropertyFactory:
    """
    Base property class that holds a property value
    Python equivalent of the PropertyFactory enum in Rust
    """

    @staticmethod
    def property_class_from_type(property_type: str) -> PropertyTrait:

        from gvas.properties.enum_property import EnumProperty
        from gvas.properties.text_property import TextProperty
        from gvas.properties.str_property import StrProperty
        from gvas.properties.name_property import NameProperty
        from gvas.properties.object_property import ObjectProperty
        from gvas.properties.field_path_property import FieldPathProperty
        from gvas.properties.delegate_property import (
            MulticastInlineDelegateProperty,
            MulticastSparseDelegateProperty,
            DelegateProperty,
        )

        from gvas.properties.aggregators import (
            SetProperty,
            MapProperty,
            ArrayProperty,
            StructProperty,
        )
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

        # Map property types to their classes
        type_map = {
            "ArrayProperty": ArrayProperty,
            "StructProperty": StructProperty,
            "TextProperty": TextProperty,
            "MapProperty": MapProperty,
            "NameProperty": NameProperty,
            "SetProperty": SetProperty,
            "StrProperty": StrProperty,
            "ByteProperty": ByteProperty,
            "EnumProperty": EnumProperty,
            "ObjectProperty": ObjectProperty,
            "FieldPathProperty": FieldPathProperty,
            "MulticastInlineDelegateProperty": MulticastInlineDelegateProperty,
            "MulticastSparseDelegateProperty": MulticastSparseDelegateProperty,
            "DelegateProperty": DelegateProperty,
            # numerical stuff
            "BoolProperty": BoolProperty,
            "Int8Property": Int8Property,
            "UInt8Property": UInt8Property,
            "Int16Property": Int16Property,
            "UInt16Property": UInt16Property,
            "Int32Property": Int32Property,
            "UInt32Property": UInt32Property,
            "IntProperty": IntProperty,
            "Int64Property": Int64Property,
            "UInt64Property": UInt64Property,
            "FloatProperty": FloatProperty,
            "DoubleProperty": DoubleProperty,
        }

        if property_type in type_map.keys():
            property_instance = type_map[property_type]()
            return property_instance
        # else:
        print(f"Unknown property type: {property_type}")
        raise DeserializeError(f"Unknown property type: {property_type}")

    @classmethod
    def new(
        cls,
        stream: BinaryIO,
        property_type: str,
        include_header: bool = True,
        suggested_length: Optional[int] = None,
    ) -> PropertyTrait:
        """Create a new property instance from a binary stream"""

        with ContextScopeTracker(property_type) as _scope_tracker:
            # Get the appropriate property class instance
            property_instance = PropertyFactory.property_class_from_type(property_type)

            # Handle special cases for properties that need suggested_length
            if (
                property_type == "ByteProperty"
                and hasattr(property_instance, "read")
                and callable(getattr(property_instance, "read"))
            ):
                property_instance.read(stream, include_header, suggested_length)
            else:
                # Standard case
                property_instance.read(stream, include_header)

        return property_instance
