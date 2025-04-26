# String Property Documentation

## Overview
This document covers the `StrProperty` class used in the GVAS format. This is a straightforward property type for storing standard character strings.

## Class and Function Definitions

### `StrProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding a standard string value.

```python
@dataclass
class StrProperty(PropertyTrait):

    type: Literal["StrProperty"] = "StrProperty"
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read/written using `read_string`/`write_string`, which handle length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `StrProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "StrProperty"
    *   Length (Int64): Size in bytes of the `Value` string data.
    *   Padding (UInt8): Typically 0.
2.  Value (`String`): The actual string content.

```
[Standard Header (Optional)]
  [Property Type Name: String = "StrProperty"]
  [Length: Int64]
  [Padding: UInt8]
[Value: String]
```

## Examples

### Example `StrProperty` Binary Data
Let's assume `value = "Hello World!"`.

```
# Header (assuming include_header=True)
# Property Type Name: "StrProperty" (UTF-8)
0C 00 00 00        # Length = 12 (11 chars + null terminator)
53 74 72 50 72 6F 70 65 72 74 79 # "StrProperty"
00                 # Null terminator

# Length: (Size of Value string data: "Hello World!" -> 13 bytes + null = 14)
0E 00 00 00 00 00 00 00 # Length = 14

# Padding
00                 # Padding = 0

# Value: "Hello World!" (UTF-8)
0D 00 00 00        # String Length = 13
48 65 6C 6C 6F 20 57 6F 72 6C 64 21 # "Hello World!"
00                 # Null terminator
```

### Example `StrProperty` with Empty Value
If `value = ""` or `value = None`:

```
# Header (assuming include_header=True)
# Property Type Name: "StrProperty" (UTF-8)
0C 00 00 00 53 74 72 50 72 6F 70 65 72 74 79 00

# Length: (Size of Value string data: Empty String -> 1 byte null terminator)
01 00 00 00 00 00 00 00 # Length = 1

# Padding
00                 # Padding = 0

# Value: Empty String (UTF-8)
00 00 00 00        # String Length = 0
00                 # Null terminator
```

## Implementation Notes
- Handles `None` value during writing by serializing an empty string.
- String serialization/deserialization uses `gvas.gvas_utils` functions.
- The `ByteCountValidator` ensures correct length consumption during reading if the header is included.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 