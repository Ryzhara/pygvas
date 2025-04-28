# Enum Property Documentation

## Overview
This document describes the `EnumProperty` class used within the GVAS format. This property type stores a value representing a member of a specific Unreal Engine enumeration.

## Class and Function Definitions

### `EnumProperty` (inherits `PropertyTrait`)
Represents a GVAS property that holds an enumeration value as a string.

```python
@dataclass
class EnumProperty(PropertyTrait):
    """A property that holds an enumeration value"""

    type: Literal["EnumProperty"] = "EnumProperty"
    enum_type: Optional[str] = None
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read/written using `read_string`/`write_string`, which handle length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `EnumProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "EnumProperty"
    *   Length (Int64): Size in bytes of the `Value` string data.
    *   Enum Type Name (`String`): The name of the enumeration type (e.g., "EColorPalette").
    *   Padding (UInt8): Typically 0.
2.  Value (`String`): The name of the specific enumeration member (e.g., "PrimaryColor").

```
[Standard Header (Optional)]
  [Property Type Name: String = "EnumProperty"]
  [Length: Int64]
  [Enum Type Name: String]
  [Padding: UInt8]
[Value: String]
```

## Examples

### Example `EnumProperty` Binary Data
Let's assume `enum_type = "EMyEnum"` and `value = "EnumValueB"`.

```
# Header (assuming include_header=True)
# Property Type Name: "EnumProperty" (UTF-8)
0D 00 00 00        # Length = 13 (12 chars + null terminator)
45 6E 75 6D 50 72 6F 70 65 72 74 79 # "EnumProperty"
00                 # Null terminator

# Length: (Size of Value string data: "EnumValueB" -> 11 bytes + null = 12)
0C 00 00 00 00 00 00 00 # Length = 12

# Enum Type Name: "EMyEnum" (UTF-8)
08 00 00 00        # Length = 8 (7 chars + null terminator)
45 4D 79 45 6E 75 6D # "EMyEnum"
00                 # Null terminator

# Padding
00                 # Padding = 0

# Value: "EnumValueB" (UTF-8)
0B 00 00 00        # Length = 11 (10 chars + null terminator)
45 6E 75 6D 56 61 6C 75 65 42 # "EnumValueB"
00                 # Null terminator
```

## Implementation Notes
- The `enum_type` is read/written as part of the extended standard header.
- The actual `value` (the enum member name) is read/written as the property's body data.
- String handling is done via `gvas.gvas_utils` functions.
- The `ByteCountValidator` ensures the value data read matches the length specified in the header.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 