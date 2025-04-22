# Property Base Documentation

## Overview
This document describes the base classes and functionality for handling properties in the GVAS (Game Save) format. The `property_base.py` file contains two main classes:

1. `PropertyTrait` - Abstract base class defining the interface for all property types
2. `PropertyFactory` - Factory class for creating and managing property instances

## PropertyTrait

### Class Definition
```python
class PropertyTrait(ABC):
    """
    Base trait/interface for Unreal specific property types
    """
```

### Abstract Methods

#### read
```python
@abstractmethod
def read(self, stream: BinaryIO, include_header: bool = True) -> None:
    """Read property data from a binary stream"""
```

**Parameters:**
- `stream` (BinaryIO): Binary stream to read from
- `include_header` (bool): Whether to read the property header (default: True)

**Description:**
- Abstract method that must be implemented by all property types
- Reads property data from a binary stream
- Handles both header and value data reading based on `include_header` parameter

#### write
```python
@abstractmethod
def write(self, stream: BinaryIO, include_header: bool = True) -> int:
    """Write property data to a binary stream"""
```

**Parameters:**
- `stream` (BinaryIO): Binary stream to write to
- `include_header` (bool): Whether to write the property header (default: True)

**Returns:**
- `int`: Number of bytes written

**Description:**
- Abstract method that must be implemented by all property types
- Writes property data to a binary stream
- Handles both header and value data writing based on `include_header` parameter

## PropertyFactory

### Class Definition
```python
@dataclass
class PropertyFactory:
    """
    Base property class that holds a property value
    Python equivalent of the PropertyFactory enum in Rust
    """
```

### Static Methods

#### property_class_from_type
```python
@staticmethod
def property_class_from_type(property_type: str) -> PropertyTrait:
```

**Parameters:**
- `property_type` (str): String identifier of the property type

**Returns:**
- `PropertyTrait`: Instance of the appropriate property class

**Description:**
- Maps property type strings to their corresponding property classes
- Creates and returns a new instance of the appropriate property class
- Raises `DeserializeError` for unknown property types
- Handles all property types including:
  - Array, Struct, Text, Map, Name, Set, Str properties
  - Byte, Enum, Object, FieldPath properties
  - Delegate properties (MulticastInline, MulticastSparse, Delegate)
  - All numerical properties (Bool, Int8-64, UInt8-64, Float, Double)

### Class Methods

#### new
```python
@classmethod
def new(
    cls,
    stream: BinaryIO,
    property_type: str,
    include_header: bool = True,
    suggested_length: Optional[int] = None,
) -> PropertyTrait:
```

**Parameters:**
- `stream` (BinaryIO): Binary stream to read from
- `property_type` (str): String identifier of the property type
- `include_header` (bool): Whether to read the property header (default: True)
- `suggested_length` (Optional[int]): Suggested length for certain property types (default: None)

**Returns:**
- `PropertyTrait`: New property instance with data read from stream

**Description:**
- Creates a new property instance from a binary stream
- Uses `property_class_from_type` to get the appropriate property class
- Handles special cases for properties that need `suggested_length` (e.g., ByteProperty)
- Uses `ContextScopeTracker` for tracking property type during deserialization
- Returns a fully initialized property instance with data read from the stream

## Implementation Notes

### Property Type Mapping
The `PropertyFactory` maintains a comprehensive mapping of property type strings to their corresponding classes:

```python
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
    # Numerical properties
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
```

### Error Handling
- Unknown property types raise a `DeserializeError`
- Error messages are only printed when not inside unit tests
- The factory pattern ensures type safety and proper initialization

### Context Tracking
- Uses `ContextScopeTracker` to maintain context during property deserialization
- Helps with debugging and error tracking by maintaining the property type context

### Special Cases
- `ByteProperty` requires special handling with `suggested_length`
- All property types must implement the `PropertyTrait` interface
- The factory ensures consistent property creation and initialization 