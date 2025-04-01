"""
Base Property implementation for GVAS
Python port of properties/mod.rs

Key differences from Rust version:
- Uses Python abstract base classes
- Implements property interface using Python protocols
- Uses dataclasses for property options
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, BinaryIO, Tuple
from ..error import DeserializeError


class SerializationHints:
    # one class variable to rule them all. This class is never instantiated.
    # We just set some data and
    meta_info: Dict[str, Any] = {
        "engine_version": (4, 0, 0, 0),
        "body_bytes": 0,  # tell child reader how big their blob is
    }

    @classmethod
    def set_engine_version(
        cls, major: int, minor: int, patch: int, build: int = 0
    ) -> None:
        cls.meta_info["engine_version"] = (major, minor, patch, build)

    @classmethod
    def get_engine_version(cls) -> Tuple[int, int, int, int]:
        return cls.meta_info.get("engine_version", (4, 0, 0, 0))

    @classmethod
    def set_body_bytes(cls, start: int, end: int) -> None:
        cls.meta_info["body_bytes"] = (start, end)

    @classmethod
    def get_body_bytes(cls) -> int:
        return cls.meta_info["body_bytes"]

    @classmethod
    def get(cls, key_name: str, default_value: Any = None):
        return cls.meta_info.get(key_name, default_value)


class PropertyTrait(ABC):
    """Base trait/interface for all property types"""

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


class Property:
    """
    Base property class that holds a property value
    Python equivalent of the Property enum in Rust
    """

    def __init__(self, type_name: str, value: Any):
        self.type = type_name
        self.value = value

    @classmethod
    def new(
        cls,
        stream: BinaryIO,
        property_type: str,
        include_header: bool = True,
        suggested_length: Optional[int] = None,
    ) -> "Property":
        """Create a new property instance from a binary stream"""
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

        # Get the appropriate property class
        if property_type in type_map.keys():
            prop_class = type_map.get(property_type)
            prop = prop_class(property_type)

        else:
            print(f"Unknown property type: {property_type}")
            raise DeserializeError(f"Unknown property type: {property_type}")

        # Handle special cases for properties that need suggested_length
        if (
            property_type == "ByteProperty"
            and hasattr(prop, "read")
            and callable(getattr(prop, "read"))
        ):
            # assert (
            #     suggested_length is not None
            # ), f"Unexpected missing suggested length: for Byte Property {prop=}"
            prop.read(stream, include_header, suggested_length)
            # if suggested_length is not None:
            #     prop.read(stream, include_header, suggested_length)
            # else:
            #     prop.read(stream, include_header)
        else:
            # Standard case
            try:
                prop.read(stream, include_header)
            except Exception as e:
                print(e)

        # print(f"Property read: {asdict(prop)}")
        return cls(property_type, prop)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write property value to stream"""
        return self.value.write(stream, include_header)

    def __repr__(self) -> str:
        return f"Property({self.type}, {self.value})"
