# Name Property Binary Format

## Overview
Name properties in GVAS files store string values that represent names. The format is similar to string properties but with specific handling for name values.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "NameProperty"
[length: uint32]            // Size of the name data in bytes
[array_index: uint32]       // Index in array (if part of an array)
[terminator: uint8]         // Always 0
```

### Value Data
```
[name: string]              // The actual name value
```

## Example

### Simple Name Property
```
[property_type: "NameProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[name: "PlayerName"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the size of the name string in bytes
- The array_index field is used when the property is part of an array
- The terminator byte is always 0
- Name values are stored as strings but have special semantic meaning in the game engine 