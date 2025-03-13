"""
Map property implementation for GVAS
Python port of map_property.rs

Key differences from Rust version:
- Uses Python's dict instead of HashMap
- Simplified type handling
"""

from dataclasses import dataclass
from typing import Dict, Optional, BinaryIO, Any
import struct

from .property import Property, PropertyTrait, PropertyOptions
from ..error import DeserializeError
from ..utils import read_string, write_string

@dataclass
class MapProperty(PropertyTrait):
    """A property that holds a key-value mapping"""
    key_type: str = ""
    value_type: str = ""
    values: Dict[Any, Any] = None
    
    def __post_init__(self):
        if self.values is None:
            self.values = {}
    
    @classmethod
    def new(cls, key_type: str, value_type: str) -> 'MapProperty':
        """Create a new map property"""
        return cls(key_type=key_type, value_type=value_type)
    
    def read(self, stream: BinaryIO, options: Optional[PropertyOptions] = None) -> None:
        """Read map from stream"""
        # Read key type
        self.key_type = read_string(stream)
        
        # Read value type
        self.value_type = read_string(stream)
        
        # Read number of entries
        num_entries = struct.unpack('<I', stream.read(4))[0]
        
        # Create options for nested properties
        nested_options = PropertyOptions(
            hints=options.hints if options else None,
            property_path=f"{options.property_path}.MapProperty" if options else "MapProperty"
        )
        
        # Read entries
        self.values = {}
        for _ in range(num_entries):
            # Read key
            key_prop = Property.new(
                stream,
                self.key_type,
                options=nested_options
            )
            
            # Read value
            value_prop = Property.new(
                stream,
                self.value_type,
                options=nested_options
            )
            
            self.values[key_prop.value] = value_prop.value
            
    def write(self, stream: BinaryIO, options: Optional[PropertyOptions] = None) -> int:
        """Write map to stream"""
        bytes_written = 0
        
        # Write key type
        bytes_written += write_string(stream, self.key_type)
        
        # Write value type
        bytes_written += write_string(stream, self.value_type)
        
        # Write number of entries
        stream.write(struct.pack('<I', len(self.values)))
        bytes_written += 4
        
        # Create options for nested properties
        nested_options = PropertyOptions(
            hints=options.hints if options else None,
            property_path=f"{options.property_path}.MapProperty" if options else "MapProperty"
        )
        
        # Write entries
        for key, value in self.values.items():
            # Write key
            key_prop = Property(self.key_type, key)
            bytes_written += key_prop.write(stream, options=nested_options)
            
            # Write value
            value_prop = Property(self.value_type, value)
            bytes_written += value_prop.write(stream, options=nested_options)
            
        return bytes_written