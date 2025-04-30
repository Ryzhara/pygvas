# Delegate Properties Documentation

## Overview
This document details the GVAS property types related to delegates, including `DelegateProperty`, `MulticastInlineDelegateProperty`, and `MulticastSparseDelegateProperty`. These properties are used to store references to functions or events within Unreal Engine objects.

## Class and Function Definitions

### `Delegate`
Represents a single delegate, binding an object name to a function name.

```python
@dataclass
class Delegate:
    type: Literal["Delegate"] = "Delegate"
    object: Optional[str] = None
    function_name: Optional[str] = None

    def read(self, stream: BinaryIO): ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `DelegateProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding a single `Delegate`.

```python
@dataclass
class DelegateProperty(PropertyTrait):
    type: Literal["DelegateProperty"] = "DelegateProperty"
    value: Optional[Delegate] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `MulticastScriptDelegate`
Represents a collection of `Delegate` objects, used by multicast delegate properties.

```python
@dataclass
class MulticastScriptDelegate:
    type: Literal["MulticastScriptDelegate"] = "MulticastScriptDelegate"
    delegates: Optional[list[Delegate]] = None

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `MulticastInlineDelegateProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding a `MulticastScriptDelegate` (a list of delegates). Often used for event dispatchers.

```python
@dataclass
class MulticastInlineDelegateProperty(PropertyTrait):
    type: Literal["MulticastInlineDelegateProperty"] = "MulticastInlineDelegateProperty"
    value: Optional[MulticastScriptDelegate] = None

    def read(self, stream: BinaryIO, include_header=True) -> None: ...
    def write(self, stream: BinaryIO, include_header=True) -> int: ...
```

### `MulticastSparseDelegateProperty` (inherits `PropertyTrait`)
Similar to `MulticastInlineDelegateProperty`, also holds a `MulticastScriptDelegate`. The distinction between "Inline" and "Sparse" might relate to engine-level optimizations or usage patterns, but the serialized format is the same based on this code.

```python
@dataclass
class MulticastSparseDelegateProperty(PropertyTrait):
    type: Literal["MulticastSparseDelegateProperty"] = "MulticastSparseDelegateProperty"
    value: Optional[MulticastScriptDelegate] = None

    def read(self, stream: BinaryIO, include_header=True) -> None: ...
    def write(self, stream: BinaryIO, include_header=True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are read using `read_string`, which handles length prefixing (Int32) and potential UTF-8/UTF-16 encoding.

### `Delegate`
Reads/writes the following sequence:
1.  Object Name (`String`): The name of the object containing the function.
2.  Function Name (`String`): The name of the function being delegated.

```
[Object Name: String]
[Function Name: String]
```

### `DelegateProperty`
Reads/writes the standard property header followed by the `Delegate` data if `include_header` is true. Otherwise, reads/writes only the `Delegate` data.
1.  Standard Property Header (Optional):
    *   Property Type Name (`String`): "DelegateProperty"
    *   Length (Int64): Size in bytes of the `Delegate` data.
    *   Padding (UInt8): Typically 0.
2.  `Delegate` Data: (See `Delegate` binary format above)

```
[Standard Header (Optional)]
[Delegate Data]
```

### `MulticastScriptDelegate`
Reads/writes the following sequence:
1.  Delegate Count (UInt32): Number of `Delegate` entries that follow.
2.  Delegates (Array of `Delegate`): `Delegate Count` instances of `Delegate` data.

```
[Delegate Count: UInt32]
[Delegate 1 Data]
[Delegate 2 Data]
...
[Delegate N Data]
```

### `MulticastInlineDelegateProperty` / `MulticastSparseDelegateProperty`
Reads/writes the standard property header followed by the `MulticastScriptDelegate` data if `include_header` is true. Otherwise, reads/writes only the `MulticastScriptDelegate` data.
1.  Standard Property Header (Optional):
    *   Property Type Name (`String`): "MulticastInlineDelegateProperty" or "MulticastSparseDelegateProperty"
    *   Length (Int64): Size in bytes of the `MulticastScriptDelegate` data.
    *   Padding (UInt8): Typically 0.
2.  `MulticastScriptDelegate` Data: (See `MulticastScriptDelegate` binary format above)

```
[Standard Header (Optional)]
[MulticastScriptDelegate Data]
```

## Examples

### Example `Delegate` Binary Data
Let's assume `object = "MyActor"` and `function_name = "OnBeginPlay"`.

```
# Object Name: "MyActor" (UTF-8)
08 00 00 00        # Length = 8 (7 chars + null terminator)
4D 79 41 63 74 6F 72 # "MyActor"
00                 # Null terminator

# Function Name: "OnBeginPlay" (UTF-8)
0C 00 00 00        # Length = 12 (11 chars + null terminator)
4F 6E 42 65 67 69 6E 50 6C 61 79 # "OnBeginPlay"
00                 # Null terminator
```

### Example `MulticastScriptDelegate` Binary Data
Contains two delegates:
1.  `object = "MyActor"`, `function_name = "OnBeginPlay"`
2.  `object = "AnotherComp"`, `function_name = "HandleEvent"`

```
# Delegate Count
02 00 00 00        # Count = 2

# Delegate 1: "MyActor", "OnBeginPlay" (UTF-8)
08 00 00 00 4D 79 41 63 74 6F 72 00 # Object Name
0C 00 00 00 4F 6E 42 65 67 69 6E 50 6C 61 79 00 # Function Name

# Delegate 2: "AnotherComp", "HandleEvent" (UTF-8)
0C 00 00 00 41 6E 6F 74 68 65 72 43 6F 6D 70 00 # Object Name
0C 00 00 00 48 61 6E 64 6C 65 45 76 65 6E 74 00 # Function Name
```

## Implementation Notes
- The actual serialization/deserialization of strings (`read_string`, `write_string`) and the standard property header (`read_standard_header`, `write_standard_header`) are handled by functions imported from `gvas.gvas_utils` and `gvas.properties.property_base` (implicitly via `PropertyTrait`).
- The `ByteCountValidator` is used during reading to ensure the correct number of bytes specified in the header's length field is consumed.
- The difference between `MulticastInlineDelegateProperty` and `MulticastSparseDelegateProperty` is not apparent from the serialization code alone; it likely reflects different underlying engine implementations or use cases.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 