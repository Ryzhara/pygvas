"""
Base Property implementation for GVAS
Python port of properties/mod.rs

Key differences from Rust version:
- Uses Python abstract base classes
- Implements property interface using Python protocols
- Uses dataclasses for property options
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, BinaryIO
from ..error import DeserializeError


@dataclass
class PropertyOptions:
    """Options for property reading/writing"""

    hints: Dict[str, str] = None
    # property_path: str = ""

    def get_hint(self, path: str) -> Optional[str]:
        """Get a type hint for a property path"""
        if not self.hints:
            return None
        return self.hints.get(path)


class PropertyTrait(ABC):
    """Base trait/interface for all property types"""

    @abstractmethod
    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
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
        options: Optional[PropertyOptions] = None,
        suggested_length: Optional[int] = None,
    ) -> "Property":
        """Create a new property instance from a binary stream"""
        from . import (
            ArrayProperty,
            BoolProperty,
            ByteProperty,
            EnumProperty,
            FloatProperty,
            IntProperty,
            MapProperty,
            NameProperty,
            SetProperty,
            StrProperty,
            StructProperty,
        )
        from .int_property import (
            Int8Property,
            Int16Property,
            Int32Property,
            Int64Property,
            UInt16Property,
            UInt32Property,
            UInt64Property,
            DoubleProperty,
        )
        from .graphical_types import (
            DateTimeProperty,
            IntPointProperty,
            LinearColorProperty,
            QuatProperty,
            RotatorProperty,
            Vector2Property,
            VectorProperty,
        )

        # Map property types to their classes
        type_map = {
            "ArrayProperty": ArrayProperty,
            "BoolProperty": BoolProperty,
            "ByteProperty": ByteProperty,
            "EnumProperty": EnumProperty,
            "FloatProperty": FloatProperty,
            "IntProperty": IntProperty,
            "Int8Property": Int8Property,
            "Int16Property": Int16Property,
            "Int32Property": Int32Property,
            "Int64Property": Int64Property,
            "UInt16Property": UInt16Property,
            "UInt32Property": UInt32Property,
            "UInt64Property": UInt64Property,
            "DoubleProperty": DoubleProperty,
            "MapProperty": MapProperty,
            "NameProperty": NameProperty,
            "SetProperty": SetProperty,
            "StrProperty": StrProperty,
            "StructProperty": StructProperty,
        }

        # Map property types to their classes
        graphical_type_map = {
            "Vector": VectorProperty,
            "VectorF": VectorProperty,
            "VectorD": VectorProperty,
            "Vector2": Vector2Property,
            "Vector2F": Vector2Property,
            "Vector2D": Vector2Property,
            "Rotator": RotatorProperty,
            "RotatorF": RotatorProperty,
            "RotatorD": RotatorProperty,
            "Quat": QuatProperty,
            "QuatF": QuatProperty,
            "QuatD": QuatProperty,
            "LinearColor": LinearColorProperty,
            "IntPoint": IntPointProperty,
            "DateTime": DateTimeProperty,
        }

        # Get the appropriate property class
        if property_type in type_map.keys():
            prop_class = type_map.get(property_type)
            prop = prop_class(property_type)

        elif property_type in graphical_type_map.keys():
            prop_class = graphical_type_map.get(property_type)
            if property_type in ["DateTIme", "IntPoint", "LinearColor"]:
                prop = prop_class(property_type)
            else:
                use_lwc = False
                if lwc := options.get_hint("LargeWorldCoordinates"):
                    assert type(lwc) is bool, "Invalid LargeWorldCoordinates hint"
                    use_lwc = lwc
                prop = prop_class(property_type, use_lwc)

        else:
            print(f"Unknown property type: {property_type}")
            raise DeserializeError(f"Unknown property type: {property_type}")

        # Handle special cases for properties that need suggested_length
        if (
            property_type == "ByteProperty"
            and hasattr(prop, "read")
            and callable(getattr(prop, "read"))
        ):
            if suggested_length is not None:
                prop.read(stream, include_header, suggested_length, options)
            else:
                prop.read(stream, include_header, options)
        else:
            # Standard case
            prop.read(stream, include_header, options)

        # print(f"Property read: {asdict(prop)}")
        return cls(property_type, prop)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write property value to stream"""
        return self.value.write(stream, include_header, options)

    def __repr__(self) -> str:
        return f"Property({self.type}, {self.value})"
