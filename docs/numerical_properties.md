# Numerical Properties Documentation

## Overview
This document describes the various GVAS property classes used to store numerical data, ranging from booleans and bytes to 64-bit integers and double-precision floating-point numbers.

## Class and Function Definitions

All numerical property classes inherit from `PropertyTrait`.

### `BoolProperty` (inherits `PropertyTrait`)
Stores a boolean value (`True` or `False`). Has a unique binary format compared to other numerical properties.

```python
@dataclass
class BoolProperty(PropertyTrait):
    type: Literal["BoolProperty"] = "BoolProperty"
    value: bool = False

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `ByteProperty` (inherits `PropertyTrait`)
Stores either a single byte (UInt8) or a string representing an enum value name. The distinction is made based on the `length` field in the header (1 for byte, >1 for string).

```python
@dataclass
class ByteProperty(PropertyTrait):
    type: Literal["ByteProperty"] = "ByteProperty"
    name: Optional[str] = "" # Corresponds to the enum type name if value is a string
    value: Union[int, str] = 0 # Either UInt8 or String

    def read(self, stream: BinaryIO, include_header: bool = True, suggested_length: int = 0) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `Int8Property` (inherits `PropertyTrait`)
Stores a signed 8-bit integer.

```python
@dataclass
class Int8Property(PropertyTrait):
    type: Literal["Int8Property"] = "Int8Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `UInt8Property` (inherits `PropertyTrait`)
Stores an unsigned 8-bit integer (byte).

```python
@dataclass
class UInt8Property(PropertyTrait):
    type: Literal["UInt8Property"] = "UInt8Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `Int16Property` (inherits `PropertyTrait`)
Stores a signed 16-bit integer.

```python
@dataclass
class Int16Property(PropertyTrait):
    type: Literal["Int16Property"] = "Int16Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `UInt16Property` (inherits `PropertyTrait`)
Stores an unsigned 16-bit integer.

```python
@dataclass
class UInt16Property(PropertyTrait):
    type: Literal["UInt16Property"] = "UInt16Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `Int32Property` (inherits `PropertyTrait`)
Stores a signed 32-bit integer.

```python
@dataclass
class Int32Property(PropertyTrait):
    type: Literal["Int32Property"] = "Int32Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `IntProperty` (inherits `PropertyTrait`)
An alias for `Int32Property` for backward compatibility.

```python
@dataclass
class IntProperty(PropertyTrait):
    type: Literal["IntProperty"] = "IntProperty"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `UInt32Property` (inherits `PropertyTrait`)
Stores an unsigned 32-bit integer.

```python
@dataclass
class UInt32Property(PropertyTrait):
    type: Literal["UInt32Property"] = "UInt32Property"
    value: int = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `Int64Property` (inherits `PropertyTrait`)
Stores a signed 64-bit integer.

```python
@dataclass
class Int64Property(PropertyTrait):
    type: Literal["Int64Property"] = "Int64Property"
    value: Union[int, float] = 0 # Python int can handle large numbers

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `UInt64Property` (inherits `PropertyTrait`)
Stores an unsigned 64-bit integer.

```python
@dataclass
class UInt64Property(PropertyTrait):
    type: Literal["UInt64Property"] = "UInt64Property"
    value: Union[int, float] = 0 # Python int can handle large numbers

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `FloatProperty` (inherits `PropertyTrait`)
Stores a 32-bit single-precision floating-point number.

```python
@dataclass
class FloatProperty(PropertyTrait):
    type: Literal["FloatProperty"] = "FloatProperty"
    value: float = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

### `DoubleProperty` (inherits `PropertyTrait`)
Stores a 64-bit double-precision floating-point number.

```python
@dataclass
class DoubleProperty(PropertyTrait):
    type: Literal["DoubleProperty"] = "DoubleProperty"
    value: float = 0

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. String handling uses standard `read_string`/`write_string`.

### Common Format (Most Numerical Types)
Most numerical properties (`Int8` through `Double`) follow this pattern if `include_header` is true:
1.  Standard Property Header:
    *   Property Type Name (`String`): e.g., "Int32Property"
    *   Length (Int64): Fixed size of the numerical value (1, 2, 4, or 8 bytes).
    *   Padding (UInt8): Typically 0.
2.  Value: The numerical value itself, with the size specified by `Length`.

```
[Standard Header]
  [Property Type Name: String]
  [Length: Int64 (1, 2, 4, or 8)]
  [Padding: UInt8]
[Value: (Fixed Size Numeric Type)]
```

If `include_header` is false, only the `Value` is read/written.

### `BoolProperty` Format
`BoolProperty` has a unique structure if `include_header` is true:
1.  Property Type Name (`String`): "BoolProperty"
2.  Length (UInt32): Always 0.
3.  Array Index (UInt32): Always 0.
4.  Value (Bool - 1 Byte): The boolean value (0x00 for False, 0x01 for True).
5.  Terminator (UInt8): Always 0.

```
[Property Type Name: String = "BoolProperty"]
[Length: UInt32 = 0]
[Array Index: UInt32 = 0]
[Value: UInt8 (0 or 1)]
[Terminator: UInt8 = 0]
```

If `include_header` is false, only the `Value` (1 byte) is read/written.

### `ByteProperty` Format
`ByteProperty` uses an extended header if `include_header` is true:
1.  Standard Property Header:
    *   Property Type Name (`String`): "ByteProperty"
    *   Length (Int64): Size of the value data (1 if `value` is Int, length of string data if `value` is String).
    *   Name (`String`): Often the Enum type name if the value is a string, otherwise potentially empty or "None".
    *   Padding (UInt8): Typically 0.
2.  Value: EITHER
    *   Byte Value (UInt8): If `Length` was 1.
    *   OR String Value (`String`): If `Length` was > 1.

```
[Standard Header]
  [Property Type Name: String = "ByteProperty"]
  [Length: Int64 (1 or >1)]
  [Name: String]
  [Padding: UInt8]
[Value: (UInt8 OR String)]
```

If `include_header` is false, only the `Value` is read/written, and the caller must know whether to expect a byte or a string based on context (e.g., the `suggested_length` passed to `read`).

## Examples

### Example `Int32Property` (Value = -10)
```
# Header (assuming include_header=True)
# Property Type Name: "Int32Property" (UTF-8)
0E 00 00 00        # Length = 14 (13 chars + null)
49 6E 74 33 32 50 72 6F 70 65 72 74 79 # "Int32Property"
00                 # Null terminator

# Length:
04 00 00 00 00 00 00 00 # Length = 4

# Padding
00                 # Padding = 0

# Value: -10 (Int32)
F6 FF FF FF        # -10 in little-endian two's complement
```

### Example `BoolProperty` (Value = True)
```
# Header (assuming include_header=True)
# Property Type Name: "BoolProperty" (UTF-8)
0D 00 00 00        # Length = 13 (12 chars + null)
42 6F 6F 6C 50 72 6F 70 65 72 74 79 # "BoolProperty"
00                 # Null terminator

# Length:
00 00 00 00        # Length = 0

# Array Index:
00 00 00 00        # Array Index = 0

# Value:
01                 # True (UInt8)

# Terminator:
00                 # Terminator = 0
```

### Example `ByteProperty` (Value = 5, Name = "MyByteEnum")
```
# Header (assuming include_header=True)
# Property Type Name: "ByteProperty" (UTF-8)
0D 00 00 00        # Length = 13 (12 chars + null)
42 79 74 65 50 72 6F 70 65 72 74 79 # "ByteProperty"
00                 # Null terminator

# Length:
01 00 00 00 00 00 00 00 # Length = 1 (indicates byte value)

# Name: "MyByteEnum" (UTF-8)
0B 00 00 00        # Length = 11 (10 chars + null)
4D 79 42 79 74 65 45 6E 75 6D # "MyByteEnum"
00                 # Null terminator

# Padding
00                 # Padding = 0

# Value: 5 (UInt8)
05
```

### Example `ByteProperty` (Value = "EnumValueC", Name = "MyByteEnum")
```
# Header (assuming include_header=True)
# Property Type Name: "ByteProperty" (UTF-8)
0D 00 00 00 42 79 74 65 50 72 6F 70 65 72 74 79 00

# Length: (Size of "EnumValueC" string data: 11 chars + null = 12)
0C 00 00 00 00 00 00 00 # Length = 12

# Name: "MyByteEnum" (UTF-8)
0B 00 00 00 4D 79 42 79 74 65 45 6E 75 6D 00

# Padding
00                 # Padding = 0

# Value: "EnumValueC" (String, UTF-8)
0B 00 00 00        # String Length = 11
45 6E 75 6D 56 61 6C 75 65 43 # "EnumValueC"
00                 # Null terminator
```

## Implementation Notes
- Most numerical types use a standard header indicating a fixed data length (1, 2, 4, or 8 bytes) followed by the raw numerical value.
- `BoolProperty` has a specific, non-standard header structure.
- `ByteProperty` is special as its value can be either a single byte (UInt8) or a string, determined by the `length` field in its header.
The `name` field in the `ByteProperty` header often holds the Enum type when the value is a string.
- `IntProperty` is maintained as an alias for `Int32Property`.
- Integer types (`Int8`-`Int64`, `UInt8`-`UInt64`) and floating-point types (`Float`, `Double`) map directly to corresponding binary representations.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 