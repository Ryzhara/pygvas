# Standard Types Binary Format Documentation

## Overview
This document describes the binary format for various standard types used in the GVAS (Game Save) format. These types are implemented as classes that inherit from `StandardStructTrait` and provide serialization/deserialization functionality.

## Common Structure
All standard types follow a common pattern:
- They implement the `StandardStructTrait` interface
- They provide `read()` and `write()` methods for binary serialization
- They use consistent byte ordering (little-endian)

## Individual Type Formats

### GuidProperty
Represents a GUID/UUID value.

**Binary Format:**
- 16 bytes of raw GUID data
- No header or terminator

**Example:**
```
01 23 45 67 89 AB CD EF FE DC BA 98 76 54 32 10  // 16-byte GUID
```

### DateTimeProperty
Represents a date and time value.

**Binary Format:**
- 8 bytes (UInt64): Number of ticks since Unix epoch
- No header or terminator

**Example:**
```
00 00 00 00 00 00 00 00  // 8-byte timestamp
```

### TimespanProperty
Represents a time duration.

**Binary Format:**
- 8 bytes (UInt64): Duration in milliseconds
- No header or terminator

**Example:**
```
00 00 00 00 00 00 00 00  // 8-byte duration
```

### IntPointProperty
Represents a 2D integer point.

**Binary Format:**
- 4 bytes (Int32): X coordinate
- 4 bytes (Int32): Y coordinate
- No header or terminator

**Example:**
```
00 00 00 00  // X coordinate
00 00 00 00  // Y coordinate
```

### LinearColorProperty
Represents a color with alpha channel.

**Binary Format:**
- 4 bytes (Float32): Alpha component
- 4 bytes (Float32): Blue component
- 4 bytes (Float32): Green component
- 4 bytes (Float32): Red component
- No header or terminator

**Example:**
```
00 00 00 00  // Alpha
00 00 00 00  // Blue
00 00 00 00  // Green
00 00 00 00  // Red
```

### RotatorProperty
Represents a 3D rotation.

**Binary Format:**
- 4 or 8 bytes (Float32 or Float64): Pitch
- 4 or 8 bytes (Float32 or Float64): Yaw
- 4 or 8 bytes (Float32 or Float64): Roll
- No header or terminator

**Note:** The size of each component depends on the `is_double` flag:
- If `is_double` is False: Uses Float32 (4 bytes per component)
- If `is_double` is True: Uses Float64 (8 bytes per component)

**Example (Float32):**
```
00 00 00 00  // Pitch
00 00 00 00  // Yaw
00 00 00 00  // Roll
```

### QuatProperty
Represents a quaternion.

**Binary Format:**
- 4 or 8 bytes (Float32 or Float64): X component
- 4 or 8 bytes (Float32 or Float64): Y component
- 4 or 8 bytes (Float32 or Float64): Z component
- 4 or 8 bytes (Float32 or Float64): W component
- No header or terminator

**Note:** The size of each component depends on the `is_double` flag:
- If `is_double` is False: Uses Float32 (4 bytes per component)
- If `is_double` is True: Uses Float64 (8 bytes per component)

**Example (Float32):**
```
00 00 00 00  // X
00 00 00 00  // Y
00 00 00 00  // Z
00 00 00 00  // W
```

### VectorProperty
Represents a 3D vector.

**Binary Format:**
- 4 or 8 bytes (Float32 or Float64): X component
- 4 or 8 bytes (Float32 or Float64): Y component
- 4 or 8 bytes (Float32 or Float64): Z component
- No header or terminator

**Note:** The size of each component depends on the `is_double` flag:
- If `is_double` is False: Uses Float32 (4 bytes per component)
- If `is_double` is True: Uses Float64 (8 bytes per component)

**Example (Float32):**
```
00 00 00 00  // X
00 00 00 00  // Y
00 00 00 00  // Z
```

### Vector2DProperty
Represents a 2D vector.

**Binary Format:**
- 4 or 8 bytes (Float32 or Float64): X component
- 4 or 8 bytes (Float32 or Float64): Y component
- No header or terminator

**Note:** The size of each component depends on the `is_double` flag:
- If `is_double` is False: Uses Float32 (4 bytes per component)
- If `is_double` is True: Uses Float64 (8 bytes per component)

**Example (Float32):**
```
00 00 00 00  // X
00 00 00 00  // Y
```

## Implementation Notes
- All numeric values are stored in little-endian format
- Float values are stored in IEEE 754 format
- The `is_double` flag in vector and rotation types is determined by the UE5 Large World Coordinates feature
- All types implement the `StandardStructTrait` interface for consistent serialization behavior
- The format is compatible with Unreal Engine's native serialization format 