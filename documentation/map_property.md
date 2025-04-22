# Map Property Binary Format Documentation

## Overview
The `MapProperty` class implements a property type that holds a key-value mapping in the GVAS format. It supports various key and value types and includes allocation flags for memory management.

## Binary Structure

### Standard Header (include_header=True)
```
[Property Type] (String)    // "MapProperty"
[Length] (UInt32)          // Size of the map data in bytes
[Array Index] (UInt32)     // Always 0
[Terminator] (UInt8)       // Always 0x00
[Key Type] (String)        // Type of keys in the map
[Value Type] (String)      // Type of values in the map
```

### Map Data
```
[Allocation Flags] (UInt32) // Memory allocation flags
[Entry Count] (UInt32)     // Number of key-value pairs
[Entries] (Array)          // Array of key-value pairs
```

### Key-Value Pair Format
```
[Key] (Varies)            // Key data, format depends on key type
[Value] (Varies)          // Value data, format depends on value type
```

## Supported Key Types
- String
- Any property type that can be used as a key

## Supported Value Types
- Boolean
- Integer
- String
- Any property type that can be used as a value

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the map data section
- The array_index field is reserved for future use and is always 0
- Keys and values are written without property headers
- The format is compatible with Unreal Engine's native serialization format
- Allocation flags control memory management behavior
- Each key-value pair is written sequentially 