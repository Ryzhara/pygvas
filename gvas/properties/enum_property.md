# Enum Property Binary Format

## Overview
Enum properties in GVAS files store enumeration values with their associated type. The format includes both the enum type name and the specific enum value.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "EnumProperty"
[length: uint32]            // Size of the enum value in bytes
[array_index: uint32]       // Always 0
[enum_type: string]         // Name of the enum type
[terminator: uint8]         // Always 0
```

### Value Data
```
[value: string]             // The actual enum value
```

## Example

### Enum Property
```
[property_type: "EnumProperty"]
[length: uint32]
[array_index: 0]
[enum_type: "GameDifficulty"]
[terminator: 0]
[value: "Hard"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the size of the enum value string in bytes
- The array_index field is reserved for future use and is always 0
- The enum_type field specifies the type of enumeration
- The terminator byte is always 0
- Enum values are stored as strings but represent specific enumerated values
- The enum_type can be empty but the value must be a valid string 