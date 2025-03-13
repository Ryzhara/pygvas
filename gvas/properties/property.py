"""
Base Property implementation for GVAS
Python port of properties/mod.rs

Key differences from Rust version:
- Uses Python abstract base classes
- Implements property interface using Python protocols
- Uses dataclasses for property options
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, BinaryIO
from ..error import DeserializeError

@dataclass
class PropertyOptions:
    """Options for property reading/writing"""
    hints: Dict[str, str] = None
    property_path: str = ""
    
    def get_hint(self, path: str) -> Optional[str]:
        """Get a type hint for a property path"""
        if not self.hints:
            return None
        return self.hints.get(path)

class PropertyTrait(ABC):
    """Base trait/interface for all property types"""
    
    @abstractmethod
    def read(self, stream: BinaryIO, include_header: bool = True, options: Optional[PropertyOptions] = None) -> None:
        """Read property data from a binary stream"""
        pass
    
    @abstractmethod
    def write(self, stream: BinaryIO, include_header: bool = True, options: Optional[PropertyOptions] = None) -> int:
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
    def new(cls, stream: BinaryIO, property_type: str, include_header: bool = True,
            options: Optional[PropertyOptions] = None, suggested_length: Optional[int] = None) -> 'Property':
        """Create a new property instance from a binary stream"""
        from . import (ArrayProperty, BoolProperty, ByteProperty, EnumProperty,
                      FloatProperty, IntProperty, MapProperty, NameProperty,
                      SetProperty, StrProperty, StructProperty)
        from .int_property import (Int8Property, Int16Property, Int32Property, Int64Property,
                                  UInt16Property, UInt32Property, UInt64Property, DoubleProperty)
        
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
        
        # Get the appropriate property class
        print(f"Looking for property type: {property_type}")
        prop_class = type_map.get(property_type)
        if not prop_class:
            print(f"Available property types: {list(type_map.keys())}")
            raise DeserializeError(f"Unknown property type: {property_type}")
            
        # Create and read the property
        prop = prop_class()
        
        # Handle special cases for properties that need suggested_length
        if property_type == "ByteProperty" and hasattr(prop, "read") and callable(getattr(prop, "read")):
            if suggested_length is not None:
                prop.read(stream, include_header, suggested_length, options)
            else:
                prop.read(stream, include_header, options)
        elif property_type in ["ArrayProperty", "MapProperty", "SetProperty"] and hasattr(prop, "read") and callable(getattr(prop, "read")):
            prop.read(stream, include_header, options)
        else:
            # Standard case
            prop.read(stream, include_header, options)
        
        return cls(property_type, prop)
    
    def write(self, stream: BinaryIO, include_header: bool = True, options: Optional[PropertyOptions] = None) -> int:
        """Write property value to stream"""
        return self.value.write(stream, include_header, options)
        
    def __repr__(self) -> str:
        return f"Property({self.type}, {self.value})"