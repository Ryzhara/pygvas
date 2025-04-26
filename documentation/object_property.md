# Object Property Documentation

## Overview
This document describes the `ObjectProperty` class within the GVAS format. This property type stores a reference to another Unreal Engine object, typically by its path name.

## Class and Function Definitions

### `ObjectProperty` (inherits `PropertyTrait`)
Represents a GVAS property that holds an object reference, serialized as a string containing the object's path.

```python
@dataclass
class ObjectProperty(PropertyTrait):
    """A property that holds an object value"""

    type: Literal["ObjectProperty"] = "ObjectProperty"
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read/written using `read_string`/`write_string`, which handle length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `ObjectProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "ObjectProperty"
    *   Length (Int64): Size in bytes of the `Value` string data (the object path).
    *   Padding (UInt8): Typically 0.
2.  Value (`String`): The path name string identifying the referenced object (e.g., "/Game/Blueprints/MyCharacterBP.MyCharacterBP_C").

```
[Standard Header (Optional)]
  [Property Type Name: String = "ObjectProperty"]
  [Length: Int64]
  [Padding: UInt8]
[Value: String]
```

## Examples

### Example `ObjectProperty` Binary Data
Let's assume `value = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C"`.

```
# Header (assuming include_header=True)
# Property Type Name: "ObjectProperty" (UTF-8)
0F 00 00 00        # Length = 15 (14 chars + null terminator)
4F 62 6A 65 63 74 50 72 6F 70 65 72 74 79 # "ObjectProperty"
00                 # Null terminator

# Length: (Size of Value string data)
# Value string: "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C"
# Length = 83 chars + null terminator = 84
54 00 00 00 00 00 00 00 # Length = 84 (0x54)

# Padding
00                 # Padding = 0

# Value: Object Path (UTF-8)
53 00 00 00        # String Length = 83
2F 47 61 6D 65 2F 54 68 69 72 64 50 65 72 73 6F 6E 2F 42 6C 75 65 70 72 69 6E 74 73 2F 42 50 5F 54 68 69 72 64 50 65 72 73 6F 6E 43 68 61 72 61 63 74 65 72 2E 42 50 5F 54 68 69 72 64 50 65 72 73 6F 6E 43 68 61 72 61 63 74 65 72 5F 43 # "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C"
00                 # Null terminator
```

## Implementation Notes
- The object reference is stored solely as its path string.
- String handling uses `gvas.gvas_utils` functions.
- The `ByteCountValidator` verifies the length during reading if the header is present.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 