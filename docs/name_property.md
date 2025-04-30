# Name Property Documentation

## Overview
This document details the `NameProperty` class within the GVAS format. This property type is used to store Unreal Engine's `FName` type, which is typically an optimized string often used for identifiers like object names, bone names, material parameter names, etc.

## Class and Function Definitions

### `NameProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding an `FName` value, serialized simply as a string.

```python
@dataclass
class NameProperty(PropertyTrait):
    """A property that holds a name"""

    type: Literal["NameProperty"] = "NameProperty"
    array_index: int = 0
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read/written using `read_string`/`write_string`, which handle length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `NameProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "NameProperty"
    *   Length (Int64): Size in bytes of the `Value` string data.
    *   Array Index (UInt32): Index if this property is part of an array (usually 0 if not).
    *   Padding (UInt8): Typically 0.
2.  Value (`String`): The actual FName string content.

```
[Standard Header (Optional)]
  [Property Type Name: String = "NameProperty"]
  [Length: Int64]
  [Array Index: UInt32]
  [Padding: UInt8]
[Value: String]
```

## Examples

### Example `NameProperty` Binary Data
Let's assume `value = "CharacterMesh0"` and `array_index = 0`.

```
# Header (assuming include_header=True)
# Property Type Name: "NameProperty" (UTF-8)
0D 00 00 00        # Length = 13 (12 chars + null terminator)
4E 61 6D 65 50 72 6F 70 65 72 74 79 # "NameProperty"
00                 # Null terminator

# Length: (Size of Value string data: "CharacterMesh0" -> 15 bytes + null = 16)
10 00 00 00 00 00 00 00 # Length = 16

# Array Index
00 00 00 00        # Array Index = 0

# Padding
00                 # Padding = 0

# Value: "CharacterMesh0" (UTF-8)
0F 00 00 00        # Length = 15 (14 chars + null terminator)
43 68 61 72 61 63 74 65 72 4D 65 73 68 30 # "CharacterMesh0"
00                 # Null terminator
```

## Implementation Notes
- The `array_index` is read/written as part of the standard header.
- The `value` (the FName string) is read/written as the property's body data.
- String handling uses `gvas.gvas_utils` functions (`read_string`, `write_string`).
- The `ByteCountValidator` ensures the value data read matches the length specified in the header.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 