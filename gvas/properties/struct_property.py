"""
Struct property implementation for GVAS
Python port of struct_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, BinaryIO, List
from io import BytesIO
import struct

from .property import Property, PropertyTrait, PropertyOptions
from ..types import Guid
from ..error import DeserializeError
from ..utils import read_string, write_string

@dataclass
class StructPropertyValue:
    """Value stored in a struct property"""
    type_name: str
    properties: Dict[str, Property]
    
    @classmethod
    def new(cls, type_name: str) -> 'StructPropertyValue':
        """Create a new struct property value"""
        return cls(type_name=type_name, properties={})

@dataclass
class StructProperty(PropertyTrait):
    """A property that holds structured data"""
    type_name: str = ""
    guid: Guid = None
    value: Optional[StructPropertyValue] = None
    
    def __post_init__(self):
        if self.guid is None:
            self.guid = Guid()
    
    @classmethod
    def new(cls, type_name: str, guid: Optional[Guid] = None) -> 'StructProperty':
        """Create a new struct property"""
        return cls(type_name=type_name, guid=guid or Guid())
    
    def read(self, stream: BinaryIO, include_header: bool = True,
             options: Optional[PropertyOptions] = None) -> None:
        """Read struct from stream"""
        if include_header:
            # Read length and array index
            length = struct.unpack('<I', stream.read(4))[0]
            array_index = struct.unpack('<I', stream.read(4))[0]
            if array_index != 0:
                position = stream.tell() - 4
                raise DeserializeError.invalid_array_index(array_index, position)
            
            # Read struct type name
            self.type_name = read_string(stream)
            
            # Read terminator
            terminator = stream.read(1)[0]
            if terminator != 0:
                position = stream.tell() - 1
                raise DeserializeError.invalid_terminator(terminator, position)
            
            # Record start position for length validation
            start = stream.tell()
            
            # Read struct size
            struct_size = struct.unpack('<Q', stream.read(8))[0]
            
            # Read GUID
            guid_bytes = stream.read(16)
            self.guid = Guid.from_bytes(guid_bytes)
            
            # Read terminator
            terminator = stream.read(1)[0]
            if terminator != 0:
                position = stream.tell() - 1
                raise DeserializeError.invalid_terminator(terminator, position)
                
        # Create options for nested properties
        nested_options = PropertyOptions(
            hints=options.hints if options else None,
            property_path=f"{options.property_path}.StructProperty" if options else "StructProperty"
        )
        
        # Get type hint if available
        type_hint = nested_options.get_hint(nested_options.property_path)
        actual_type = type_hint or self.type_name
        
        # Create struct value
        self.value = StructPropertyValue(actual_type, {})
        
        # Read properties until we hit None
        while True:
            # Read property name
            name = read_string(stream)
            if not name:
                break
                
            # Read property type
            prop_type = read_string(stream)
            if not prop_type:
                break
                
            # Read property
            prop = Property.new(
                stream,
                prop_type,
                include_header=True,
                options=nested_options
            )
            
            self.value.properties[name] = prop
            
        # Validate length if header was included
        if include_header:
            end = stream.tell()
            actual_size = end - start
            if actual_size != length:
                raise DeserializeError.invalid_value_size(length, actual_size, start)
            
    def write(self, stream: BinaryIO, include_header: bool = True,
              options: Optional[PropertyOptions] = None) -> int:
        """Write struct to stream"""
        bytes_written = 0
        
        if include_header:
            # Write to a temporary buffer first to get the length
            buffer = BytesIO()
            buffer_bytes = 0
            
            # Write struct type name
            buffer_bytes += write_string(buffer, self.type_name)
            
            # Write terminator
            buffer.write(bytes([0]))
            buffer_bytes += 1
            
            # Write struct size (placeholder)
            size_pos = buffer.tell()
            buffer.write(struct.pack('<Q', 0))
            buffer_bytes += 8
            
            # Write GUID
            buffer.write(self.guid.to_bytes())
            buffer_bytes += 16
            
            # Write terminator
            buffer.write(bytes([0]))
            buffer_bytes += 1
            
            # Create options for nested properties
            nested_options = PropertyOptions(
                hints=options.hints if options else None,
                property_path=f"{options.property_path}.StructProperty" if options else "StructProperty"
            )
            
            # Write properties
            if self.value:
                for name, prop in self.value.properties.items():
                    # Write property name
                    buffer_bytes += write_string(buffer, name)
                    
                    # Write property type
                    buffer_bytes += write_string(buffer, prop.type)
                    
                    # Write property
                    buffer_bytes += prop.write(buffer, options=nested_options)
                    
            # Write None terminator
            buffer.write(struct.pack('<I', 0))
            buffer_bytes += 4
            
            # Update struct size
            current_pos = buffer.tell()
            buffer.seek(size_pos)
            buffer.write(struct.pack('<Q', buffer_bytes - 30))  # 30 = header size
            buffer.seek(0)
            
            # Write length and array index
            stream.write(struct.pack('<I', buffer_bytes))  # Total length
            stream.write(struct.pack('<I', 0))  # Array index
            bytes_written += 8
            
            # Write buffer contents
            buffer_data = buffer.getvalue()
            stream.write(buffer_data)
            bytes_written += len(buffer_data)
        else:
            # Create options for nested properties
            nested_options = PropertyOptions(
                hints=options.hints if options else None,
                property_path=f"{options.property_path}.StructProperty" if options else "StructProperty"
            )
            
            # Write properties
            if self.value:
                for name, prop in self.value.properties.items():
                    # Write property name
                    bytes_written += write_string(stream, name)
                    
                    # Write property type
                    bytes_written += write_string(stream, prop.type)
                    
                    # Write property
                    bytes_written += prop.write(stream, include_header=True, options=nested_options)
                    
            # Write None terminator
            stream.write(struct.pack('<I', 0))
            bytes_written += 4
            
        return bytes_written 