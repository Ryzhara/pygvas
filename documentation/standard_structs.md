# Standard Structs Documentation

## Overview
This document describes the common, predefined struct types frequently encountered within GVAS files, such as vectors, colors, GUIDs, and date/time representations. These are typically used as values within `StructProperty` or `ArrayProperty`.

## Class and Function Definitions

### `StandardStructTrait`(ABC)
An abstract base class defining the interface for standard struct types. It includes `read` and `write` abstract methods and a static method `uses_lwc()` to check if Large World Coordinates (LWC) are enabled based on the engine version. LWC typically means using `double` (64-bit float) instead of `float` (32-bit float) for vector/rotator types.

```python
from abc import ABC, abstractmethod

@dataclass
class StandardStructTrait(ABC):
    @abstractmethod
    def read(self, stream: BinaryIO) -> None: ...

    @abstractmethod
    def write(self, stream: BinaryIO) -> int: ...

    @staticmethod
    def uses_lwc() -> bool: ...
```

### `GuidStruct` (inherits `StandardStructTrait`)
Represents a Globally Unique Identifier (GUID).

```python
@dataclass
class GuidStruct(StandardStructTrait):
    type: Literal["Guid"] = "Guid"
    guid: Optional[str] = None # Stored as string representation

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `DateTimeStruct` (inherits `StandardStructTrait`)
Represents a specific point in time, stored as ticks (UInt64).

```python
@dataclass
class DateTimeStruct(StandardStructTrait):
    type: Literal["DateTime"] = "DateTime"
    datetime: int = 0  # uint64 ticks
    comment: str = None # Not serialized, just for debugging

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `TimespanStruct` (inherits `StandardStructTrait`)
Represents a duration of time, stored as ticks (UInt64).

```python
@dataclass
class TimespanStruct(StandardStructTrait):
    type: Literal["Timespan"] = "Timespan"
    timespan: int = 0  # uint64 ticks
    comment: str = None # Not serialized, just for debugging

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `IntPointStruct` (inherits `StandardStructTrait`)
Represents a 2D point using integer coordinates.

```python
@dataclass
class IntPointStruct(StandardStructTrait):
    type: Literal["IntPoint"] = "IntPoint"
    x: int = 0 # Int32
    y: int = 0 # Int32

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `LinearColorStruct` (inherits `StandardStructTrait`)
Represents a color with Red, Green, Blue, and Alpha components using floating-point values.

```python
@dataclass
class LinearColorStruct(StandardStructTrait):
    type: Literal["LinearColor"] = "LinearColor"
    a: float = 0 # Float32
    b: float = 0 # Float32
    g: float = 0 # Float32
    r: float = 0 # Float32

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `RotatorStruct` (inherits `StandardStructTrait`)
Represents a rotation in 3D space using Pitch, Yaw, and Roll angles. Uses `double` if LWC is enabled, otherwise `float`.

```python
@dataclass
class RotatorStruct(StandardStructTrait):
    type: Literal["Rotator"] = "Rotator"
    pitch: float = 0 # Float32 or Float64 (Double)
    yaw: float = 0   # Float32 or Float64 (Double)
    roll: float = 0  # Float32 or Float64 (Double)

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `QuatStruct` (inherits `StandardStructTrait`)
Represents a rotation using a Quaternion (x, y, z, w). Uses `double` if LWC is enabled, otherwise `float`.

```python
@dataclass
class QuatStruct(StandardStructTrait):
    type: Literal["Quat"] = "Quat"
    x: float = 0 # Float32 or Float64 (Double)
    y: float = 0 # Float32 or Float64 (Double)
    z: float = 0 # Float32 or Float64 (Double)
    w: float = 0 # Float32 or Float64 (Double)

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `VectorStruct` (inherits `StandardStructTrait`)
Represents a 3D vector (x, y, z). Uses `double` if LWC is enabled, otherwise `float`.

```python
@dataclass
class VectorStruct(StandardStructTrait):
    type: Literal["Vector"] = "Vector"
    x: float = 0 # Float32 or Float64 (Double)
    y: float = 0 # Float32 or Float64 (Double)
    z: float = 0 # Float32 or Float64 (Double)

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `Vector2DStruct` (inherits `StandardStructTrait`)
Represents a 2D vector (x, y). Uses `double` if LWC is enabled, otherwise `float`.

```python
@dataclass
class Vector2DStruct(StandardStructTrait):
    type: Literal["Vector2D"] = "Vector2D"
    x: float = 0 # Float32 or Float64 (Double)
    y: float = 0 # Float32 or Float64 (Double)

    def read(self, stream: BinaryIO) -> None: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### `ByteBlobStruct` (inherits `StandardStructTrait`)
A special struct used primarily via `deserialization_hints` to read a specified number of bytes as a raw hexadecimal string, allowing bypass of unknown custom struct types.

```python
@dataclass
class ByteBlobStruct(StandardStructTrait):
    type: Literal["ByteBlobStruct"] = "ByteBlobStruct"
    byte_blob: str = "" # Hex representation of the raw bytes

    def read(self, stream: BinaryIO) -> None: ... # Reads context["byte_count"] bytes
    def write(self, stream: BinaryIO) -> int: ...
```

### Helper Functions

#### `is_standard_struct(type_name: str) -> bool`
Checks if a given type name corresponds to one of the known standard struct types.

#### `get_standard_struct_instance(type_name: str) -> StandardStructTrait`
Factory function that returns an instance of the appropriate `StandardStructTrait` subclass based on the provided `type_name`.

## Binary Format

All multi-byte values are **little-endian**.

### `GuidStruct`
-   guid (16 bytes): Raw bytes of the GUID.

### `DateTimeStruct`
-   ticks (`UInt64`): 8 bytes representing the date/time.

### `TimespanStruct`
-   ticks (`UInt64`): 8 bytes representing the timespan.

### `IntPointStruct`
-   x (`Int32`): 4 bytes.
-   y (`Int32`): 4 bytes.

### `LinearColorStruct`
-   a (`Float32`): 4 bytes.
-   b (`Float32`): 4 bytes.
-   g (`Float32`): 4 bytes.
-   r (`Float32`): 4 bytes.

### `RotatorStruct`
Size depends on LWC:
-   pitch (`Float32` or `Double`): 4 or 8 bytes.
-   yaw (`Float32` or `Double`): 4 or 8 bytes.
-   roll (`Float32` or `Double`): 4 or 8 bytes.

### `QuatStruct`
Size depends on LWC:
-   x (`Float32` or `Double`): 4 or 8 bytes.
-   y (`Float32` or `Double`): 4 or 8 bytes.
-   z (`Float32` or `Double`): 4 or 8 bytes.
-   w (`Float32` or `Double`): 4 or 8 bytes.

### `VectorStruct`
Size depends on LWC:
-   x (`Float32` or `Double`): 4 or 8 bytes.
-   y (`Float32` or `Double`): 4 or 8 bytes.
-   z (`Float32` or `Double`): 4 or 8 bytes.

### `Vector2DStruct`
Size depends on LWC:
-   x (`Float32` or `Double`): 4 or 8 bytes.
-   y (`Float32` or `Double`): 4 or 8 bytes.

### `ByteBlobStruct`
-   raw_bytes: A sequence of bytes whose length is determined externally (typically via context from `StructProperty` length field when used with hints).

## Examples

### Example `GuidStruct`
GUID: `00112233-4455-6677-8899-AABBCCDDEEFF`
```
# Little-endian representation as seen in hex editor
# 00112233 -> 33 22 11 00
# 4455     -> 55 44
# 6677     -> 77 66
# 8899     -> 99 88
# AABBCCDDEEFF -> FF EE DD CC BB AA
33 22 11 00  55 44  77 66  99 88  FF EE DD CC BB AA
```

### Example `VectorStruct` (LWC Disabled - Float32)
X=1.0, Y=2.0, Z=3.0
```
# X=1.0f (0x3F800000) Y=2.0f (0x40000000) Z=3.0f (0x40400000)
# Little-Endian Hex Editor View:
3F 80 00 00  00 00 00 40  00 00 40 40
```

### Example `VectorStruct` (LWC Enabled - Double)
X=1.0, Y=2.0, Z=3.0
```
# X=1.0 (0x3FF0000000000000) Y=2.0 (0x4000000000000000) Z=3.0 (0x4008000000000000)
# Little-Endian Hex Editor View:
00 00 00 00 00 00 F0 3F  00 00 00 00 00 00 00 40  00 00 00 00 00 00 08 40
```

## Implementation Notes
- These structs represent fixed binary layouts.
- Vector, Rotator, and Quat structs adapt their read/write operations based on the engine version's support for Large World Coordinates (`uses_lwc()`).
- The `ByteBlobStruct` is a utility for handling unknown raw struct data and relies on external context (like the byte count from a `StructProperty` header) for reading.
- These classes are typically instantiated and used by `StructProperty` when it encounters a struct with a matching `struct_type` name.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 