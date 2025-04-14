# Standard Types Binary Format

## Overview
Standard types in GVAS files represent common data structures used in Unreal Engine, including GUIDs, dates, times, colors, vectors, and other geometric types. These types are implemented as special structs with specific binary formats. Some types can use either single-precision (float32) or double-precision (float64) values based on the engine version.

## Binary Structure

### Common Header (when used as a property)
```
Unlike the classes derived from PropertyTrait, classes derived from StandardStructTrait do not have any common header. They are serialized and deserialized as "bare types" because they have deterministic structure.
```

### Guid PropertyFactory
```
[guid: bytes]              // 16 bytes, little-endian UUID
```

### DateTime PropertyFactory
```
[datetime: uint64]         // Ticks since January 1, 0001 (0.1 microseconds)
```

### Timespan PropertyFactory
```
[timespan: uint64]         // Duration in milliseconds
```

### IntPoint PropertyFactory
```
[x: int32]                // X coordinate
[y: int32]                // Y coordinate
```

### LinearColor PropertyFactory
```
[a: float32]              // Alpha component (0.0 to 1.0)
[b: float32]              // Blue component (0.0 to 1.0)
[g: float32]              // Green component (0.0 to 1.0)
[r: float32]              // Red component (0.0 to 1.0)
```

### Rotator PropertyFactory
```
[pitch: float32/float64]  // Pitch angle in degrees (float32 for UE4, float64 for UE5+)
[yaw: float32/float64]    // Yaw angle in degrees (float32 for UE4, float64 for UE5+)
[roll: float32/float64]   // Roll angle in degrees (float32 for UE4, float64 for UE5+)
```

### Quat PropertyFactory
```
[x: float32/float64]      // X component of quaternion (float32 for UE4, float64 for UE5+)
[y: float32/float64]      // Y component of quaternion (float32 for UE4, float64 for UE5+)
[z: float32/float64]      // Z component of quaternion (float32 for UE4, float64 for UE5+)
[w: float32/float64]      // W component of quaternion (float32 for UE4, float64 for UE5+)
```

### Vector PropertyFactory
```
[x: float32/float64]      // X coordinate (float32 for UE4, float64 for UE5+)
[y: float32/float64]      // Y coordinate (float32 for UE4, float64 for UE5+)
[z: float32/float64]      // Z coordinate (float32 for UE4, float64 for UE5+)
```

### Vector2D PropertyFactory
```
[x: float32/float64]      // X coordinate (float32 for UE4, float64 for UE5+)
[y: float32/float64]      // Y coordinate (float32 for UE4, float64 for UE5+)
```

## Examples

### Guid PropertyFactory
```
[property_type: "Guid"]
[length: 16]
[array_index: 0]
[terminator: 0]
[guid: 16 bytes]          // e.g., "550e8400-e29b-41d4-a716-446655440000"
```

### DateTime PropertyFactory
```
[property_type: "DateTime"]
[length: 8]
[array_index: 0]
[terminator: 0]
[datetime: 63822647996000] // Example: "2024-03-15 12:34:56.789"
```

### LinearColor PropertyFactory
```
[property_type: "LinearColor"]
[length: 16]
[array_index: 0]
[terminator: 0]
[a: 1.0]                  // Alpha
[b: 0.0]                  // Blue
[g: 0.5]                  // Green
[r: 1.0]                  // Red
```

### Vector PropertyFactory (UE4)
```
[property_type: "Vector"]
[length: 12]
[array_index: 0]
[terminator: 0]
[x: 100.0]                // X coordinate (float32)
[y: 200.0]                // Y coordinate (float32)
[z: 300.0]                // Z coordinate (float32)
```

### Vector PropertyFactory (UE5+)
```
[property_type: "Vector"]
[length: 24]
[array_index: 0]
[terminator: 0]
[x: 100.0]                // X coordinate (float64)
[y: 200.0]                // Y coordinate (float64)
[z: 300.0]                // Z coordinate (float64)
```

## Notes
- All integers are stored in little-endian format
- All floating-point values are stored in little-endian format
- DateTime values are stored as ticks (0.1 microseconds) since January 1, 0001
- Timespan values are stored in milliseconds
- The following types use float32 in UE4 and float64 in UE5+:
  - Vector
  - Vector2D
  - Rotator
  - Quat
- LinearColor always uses float32 regardless of engine version
- The length field represents the total size of the struct data in bytes
- The array_index field is reserved for future use and is always 0
- The terminator byte is always 0
- Guid values are stored as 16-byte little-endian UUIDs
- IntPoint values are stored as 32-bit signed integers
- The precision of floating-point values is determined by the engine version (UE4 vs UE5+)
- Large World Coordinates (LWC) mode uses double precision (float64) for better precision
- LinearColor components are stored in ABGR order
- The length field represents the total size of the struct data in bytes
- The array_index field is reserved for future use and is always 0
- The terminator byte is always 0
- Guid values are stored as 16-byte little-endian UUIDs
- IntPoint values are stored as 32-bit signed integers 