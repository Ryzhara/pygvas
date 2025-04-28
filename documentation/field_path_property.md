# Field Path Property Documentation

## Overview
This document explains the `FieldPathProperty` used in the GVAS format. This property type stores a path to a specific field or property within an Unreal Engine object structure, potentially referencing nested objects or components.

## Class and Function Definitions

### `FieldPath`
Represents the actual path data, consisting of a list of string names forming the path and the name of the resolved owner object.

```python
@dataclass
class FieldPath:
    type: Literal["FieldPath"] = "FieldPath"
    path: Optional[list[str]] = None
    resolved_owner: Optional[str] = None

    def __post_init__(self):
        if self.path is None:
            self.path = []

    def read(self, stream: BinaryIO): ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `FieldPathProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding a `FieldPath` object.

```python
@dataclass
class FieldPathProperty(PropertyTrait):
    """A property that holds an FieldPath value"""

    type: Literal["FieldPathProperty"] = "FieldPathProperty"
    value: FieldPath = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read/written using `read_string`/`write_string`, which handle length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `FieldPath`
Reads/writes the following sequence:
1.  Path Element Count (UInt32): Number of string elements in the `Path` list.
2.  Path Elements (Array of `String`): `Path Element Count` instances of string data, representing each step in the path.
3.  Resolved Owner (`String`): The name of the object ultimately owning the field targeted by the path.

```
[Path Element Count: UInt32]
[Path Element 1: String]
[Path Element 2: String]
...
[Path Element N: String]
[Resolved Owner: String]
```

### `FieldPathProperty`
Reads/writes the standard property header followed by the `FieldPath` data if `include_header` is true. Otherwise, reads/writes only the `FieldPath` data.
1.  Standard Property Header (Optional):
    *   Property Type Name (`String`): "FieldPathProperty"
    *   Length (Int64): Size in bytes of the `FieldPath` data.
    *   Padding (UInt8): Typically 0.
2.  `FieldPath` Data: (See `FieldPath` binary format above)

```
[Standard Header (Optional)]
[FieldPath Data]
```

## Examples

### Example `FieldPath` Binary Data
Let's assume `path = ["MyComponent", "NestedObject", "TargetField"]` and `resolved_owner = "OwningActor"`.

```
# Path Element Count
03 00 00 00        # Count = 3

# Path Element 1: "MyComponent" (UTF-8)
0C 00 00 00        # Length = 12 (11 chars + null terminator)
4D 79 43 6F 6D 70 6F 6E 65 6E 74 # "MyComponent"
00                 # Null terminator

# Path Element 2: "NestedObject" (UTF-8)
0D 00 00 00        # Length = 13 (12 chars + null terminator)
4E 65 73 74 65 64 4F 62 6A 65 63 74 # "NestedObject"
00                 # Null terminator

# Path Element 3: "TargetField" (UTF-8)
0C 00 00 00        # Length = 12 (11 chars + null terminator)
54 61 72 67 65 74 46 69 65 6C 64 # "TargetField"
00                 # Null terminator

# Resolved Owner: "OwningActor" (UTF-8)
0C 00 00 00        # Length = 12 (11 chars + null terminator)
4F 77 6E 69 6E 67 41 63 74 6F 72 # "OwningActor"
00                 # Null terminator
```

## Implementation Notes
- The `FieldPath` structure is read/written as the body of the `FieldPathProperty`.
- String handling relies on `gvas.gvas_utils`.
- The `ByteCountValidator` ensures the data read matches the length specified in the optional header.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 