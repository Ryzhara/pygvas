# Map Property Documentation

## Overview
This document describes the `MapProperty` class within the GVAS format. This property type stores a collection of key-value pairs, similar to a dictionary or hash map. Both keys and values are themselves GVAS properties.

## Class and Function Definitions

### `MapProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding key-value pairs.

```python
from gvas.properties.aggregator_properties import UNREAL_ENGINE_PROPERTIES

@dataclass
class MapProperty(PropertyTrait):
    KEY_TYPE = Union[str, UNREAL_ENGINE_PROPERTIES] # Actual Key Property Instance
    VALUE_TYPE = Union[bool, int, str, UNREAL_ENGINE_PROPERTIES] # Actual Value Property Instance

    type: Literal["MapProperty"] = "MapProperty"
    key_type: str = None   # Property type name string for keys
    value_type: str = None # Property type name string for values
    allocation_flags: int = 0 # Typically 0, potentially related to memory allocation
    values: list[tuple[KEY_TYPE, VALUE_TYPE]] = None # List of (key_prop, value_prop) tuples

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**.

### `MapProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "MapProperty"
    *   Length (Int64): Size in bytes of the map data body (Steps 2-4).
    *   Key Type Name (`String`): The GVAS property type name for the map keys (e.g., "NameProperty", "IntProperty").
    *   Value Type Name (`String`): The GVAS property type name for the map values (e.g., "StructProperty", "FloatProperty").
    *   Padding (UInt8): Typically 0.
2.  Allocation Flags (UInt32): Currently observed to be 0.
3.  Entry Count (UInt32): The number of key-value pairs in the map.
4.  Entries (Array): `Entry Count` instances of the following pair:
    *   Key Property Data: The binary data for the key property, read/written **without** its own header (using `include_header=False`). The specific format depends on the `Key Type Name`.
    *   Value Property Data: The binary data for the value property, read/written **without** its own header (using `include_header=False`). The specific format depends on the `Value Type Name`.

```
[Standard Header (Optional)]
  [Property Type Name: String = "MapProperty"]
  [Length: Int64]
  [Key Type Name: String]
  [Value Type Name: String]
  [Padding: UInt8]
[Allocation Flags: UInt32]
[Entry Count: UInt32]
[Key 1 Data (No Header)]
[Value 1 Data (No Header)]
[Key 2 Data (No Header)]
[Value 2 Data (No Header)]
...
[Key N Data (No Header)]
[Value N Data (No Header)]
```

## Examples

### Example MapProperty (Key: NameProperty, Value: Int32Property)
Map: `{"EntryA": 10, "EntryB": -5}`

```
# Header (assuming include_header=True)
# Property Type Name: "MapProperty" (UTF-8)
0C 00 00 00 4D 61 70 50 72 6F 70 65 72 74 79 00

# Length: (Calculated size of map data body)
#   AllocFlags(4) + EntryCount(4) +
#   Key1(Name "EntryA" no header: 7B+null=8) + Val1(Int32 no header: 4) +
#   Key2(Name "EntryB" no header: 7B+null=8) + Val2(Int32 no header: 4)
#   Total Body = 4 + 4 + 8 + 4 + 8 + 4 = 32 bytes
20 00 00 00 00 00 00 00 # Length = 32 (0x20)

# Key Type Name: "NameProperty" (UTF-8)
0D 00 00 00 4E 61 6D 65 50 72 6F 70 65 72 74 79 00

# Value Type Name: "Int32Property" (UTF-8)
0E 00 00 00 49 6E 74 33 32 50 72 6F 70 65 72 74 79 00

# Padding
00

# -- Map Data Body Starts --
# Allocation Flags
00 00 00 00

# Entry Count
02 00 00 00       # Count = 2

# Entry 1: Key ("EntryA" - NameProperty, no header)
07 00 00 00       # String Length = 7
45 6E 74 72 79 41 # "EntryA"
00                # Null terminator

# Entry 1: Value (10 - Int32Property, no header)
0A 00 00 00       # Value = 10

# Entry 2: Key ("EntryB" - NameProperty, no header)
07 00 00 00       # String Length = 7
45 6E 74 72 79 42 # "EntryB"
00                # Null terminator

# Entry 2: Value (-5 - Int32Property, no header)
FB FF FF FF       # Value = -5
```

## Implementation Notes
- The key and value property types are specified as strings in the header.
- When reading/writing the individual key and value properties within the map body, the `include_header` flag is set to `False`. This means only the core data of the key/value properties is stored, not their full headers.
- The `PropertyFactory` is used internally to instantiate and manage the deserialization/serialization of the key and value properties based on their type names.
- The actual Python representation stores `(key_property_instance, value_property_instance)` tuples in the `values` list.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 