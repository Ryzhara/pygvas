# Set Property Documentation

## Overview
This document describes the `SetProperty` class within the GVAS format. This property type stores an unordered collection of unique elements, similar to a mathematical set. All elements within the set must be of the same GVAS property type.

## Class and Function Definitions

### `SetProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding a set of unique property instances of the same type.

```python
from gvas.properties.aggregator_properties import UNREAL_ENGINE_PROPERTIES

@dataclass
class SetProperty(PropertyTrait):
    type: Literal["SetProperty"] = "SetProperty"
    property_type: Optional[str] = None # Property type name string for elements
    allocation_flags: int = 0 # Typically 0
    properties: Optional[list[UNREAL_ENGINE_PROPERTIES]] = None # List of element property instances

    def __post_init__(self):
        if self.properties is None:
            self.properties = []

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**.

### `SetProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Required, `include_header` must be true for reading):
    *   Property Type Name (`String`): "SetProperty"
    *   Length (Int64): Size in bytes of the set data body (Steps 2-4).
    *   Element Type Name (`String`): The GVAS property type name for all elements in the set (e.g., "NameProperty", "ObjectProperty").
    *   Padding (UInt8): Typically 0.
2.  Allocation Flags (UInt32): Currently observed to be 0.
3.  Element Count (UInt32): The number of elements in the set.
4.  Elements (Array): `Element Count` instances of the element property data.
    *   Element Property Data: The binary data for the element property, read/written **without** its own header (using `include_header=False`). The specific format depends on the `Element Type Name`.

```
[Standard Header]
  [Property Type Name: String = "SetProperty"]
  [Length: Int64]
  [Element Type Name: String]
  [Padding: UInt8]
[Allocation Flags: UInt32]
[Element Count: UInt32]
[Element 1 Data (No Header)]
[Element 2 Data (No Header)]
...
[Element N Data (No Header)]
```

## Examples

### Example SetProperty (Element Type: NameProperty)
Set: `{"Apple", "Banana"}`

```
# Header
# Property Type Name: "SetProperty" (UTF-8)
0C 00 00 00 53 65 74 50 72 6F 70 65 72 74 79 00

# Length: (Calculated size of set data body)
#   AllocFlags(4) + ElemCount(4) +
#   Elem1(Name "Apple" no header: 6B+null=7) +
#   Elem2(Name "Banana" no header: 7B+null=8)
#   Total Body = 4 + 4 + 7 + 8 = 23 bytes
17 00 00 00 00 00 00 00 # Length = 23 (0x17)

# Element Type Name: "NameProperty" (UTF-8)
0D 00 00 00 4E 61 6D 65 50 72 6F 70 65 72 74 79 00

# Padding
00

# -- Set Data Body Starts --
# Allocation Flags
00 00 00 00

# Element Count
02 00 00 00       # Count = 2

# Element 1 Data ("Apple" - NameProperty, no header)
06 00 00 00       # String Length = 6
41 70 70 6C 65    # "Apple"
00                # Null terminator

# Element 2 Data ("Banana" - NameProperty, no header)
07 00 00 00       # String Length = 7
42 61 6E 61 6E 61 # "Banana"
00                # Null terminator
```

## Implementation Notes
- `SetProperty` cannot be nested directly within other container types like `ArrayProperty` or `MapProperty` when reading (due to the requirement for `include_header=True`).
- The type of all elements in the set is specified by the `property_type` string in the header.
- When reading/writing the individual element properties within the set body, `include_header` is set to `False`.
- The `PropertyFactory` is used to handle the elements based on the `property_type`.
- While GVAS represents this as a sequence, the underlying concept is a set, implying uniqueness of elements (though this implementation stores them in a list `properties`).

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 