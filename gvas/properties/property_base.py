"""
Base Property implementation for GVAS
Python port of properties/mod.rs

Key differences from Rust version:
- Uses Python abstract base classes
- Implements property interface using Python protocols
- Uses dataclasses for property options
"""

import enum
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO, List, Tuple
from xml.sax.handler import property_encoding, property_dom_node

from ..custom_versions import FEditorObjectVersion, FUE5ReleaseStreamObjectVersion
from ..error import DeserializeError
from ..engine_versions import FEngineVersion, EngineVersion
from ..gvas_types import HashableIndexMap


# ============================================


class SerializationTools:
    """
    This class corresponds to the Rust package use of "options" and scoped property stacks.
    It is never instantiated and avoids cluttering signatures with mostly unused parameters.

    If your file fails while parsing with a DeserializeError::MissingHint error you need hints.
    When a struct is stored inside ArrayProperty/SetProperty/MapProperty in GvasFile it does not
    contain type annotations. This means that a library parsing the file must know the type
    beforehand. That’s why you need hints.
    """

    # Hack for TextProperty;
    body_bytes: Tuple[int, int] = (0, 0)  # tell child reader how big their blob is
    engine_version: FEngineVersion
    custom_versions: HashableIndexMap[uuid, int]
    hints: Dict[str, str] = {}
    properties_stack: List[str] = []
    text_property_blob: int = 0  # temp hack for TextProperty as blob

    # initialization requirements
    @classmethod
    def set_header_and_custom_versions(
        cls,
        engine_version: FEngineVersion,
        custom_versions: HashableIndexMap[uuid, int],
    ) -> None:
        cls.engine_version = engine_version
        cls.custom_versions = custom_versions

    # used for processing hints
    @classmethod
    def push_path(cls, step: str) -> None:
        cls.properties_stack.append(step)

    @classmethod
    def pop_path(cls) -> None:
        cls.properties_stack.pop()

    @classmethod
    def get_path(cls) -> str:
        return ".".join(cls.properties_stack)

    # hack for getting around unknown object byte count
    @classmethod
    def set_byte_block_to_be_read(cls, start: int, end: int) -> None:
        cls.body_bytes = (start, end)

    @classmethod
    def get_byte_block_to_be_read(cls) -> Tuple[int, int]:
        return cls.body_bytes

    @classmethod
    def supports_version(
        cls, required_version: FEditorObjectVersion | FUE5ReleaseStreamObjectVersion
    ) -> bool:
        guid_key = required_version.custom_version_guid
        supported_version = cls.custom_versions.get(guid_key, 0)
        return supported_version >= required_version.value


# ============================================
#
class ContextScopeTracker:
    parent_context = "unknown"
    context = "unknown"

    def __init__(self, context: str):
        self.parent_context = SerializationTools.get_path()
        self.context = context

    def __enter__(self):
        SerializationTools.push_path(self.context)
        # print(f"Entering scope: {SerializationTools.get_path()}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(
                f"An exception of type {exc_type} occurred: {exc_val} with context\n\t{SerializationTools.get_path()}"
            )
            import traceback
            import sys

            traceback.print_exception(exc_type, exc_val, exc_tb, file=sys.stdout)
            return False
        # Don't pop so we can have deepest context for debugging
        SerializationTools.pop_path()
        return True


# ============================================
#
class PropertyTrait(ABC):
    """
    Base trait/interface for Unreal specific property types
    """

    @abstractmethod
    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write property data to a binary stream"""
        pass

    @classmethod
    def from_json(cls, json_dict):
        # Create a new instance without calling the constructor
        instance = cls.__new__(cls)
        # Update the instance attributes with the JSON dictionary
        instance.__dict__.update(json_dict)
        return instance


class Property:
    """
    Base property class that holds a property value
    Python equivalent of the Property enum in Rust
    """

    def __init__(self):
        pass

    @staticmethod
    def property_class_from_type(property_type: str) -> Any:
        from . import (
            ArrayProperty,
            BoolProperty,
            ByteProperty,
            EnumProperty,
            IntProperty,
            TextProperty,
            MapProperty,
            NameProperty,
            SetProperty,
            StrProperty,
            StructProperty,
            ObjectProperty,
            FieldPathProperty,
            MulticastInlineDelegateProperty,
        )
        from .int_property import (
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
    ) -> "Property":
        """Create a new property instance from a binary stream"""

        with ContextScopeTracker(property_type) as _scope_tracker:
            # Get the appropriate property class instance
            property_instance = Property.property_class_from_type(property_type)

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

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write property value to stream"""
        return self.value.write(stream, include_header)

    def __repr__(self) -> str:
        return f"Property({self.type}, {self.value})"
