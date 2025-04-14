# String PropertyFactory Binary Format

## Overview
String properties in GVAS files store text values. The format supports both null and non-null string values with proper length tracking.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "StrProperty"
[length: uint32]            // Size of the string data in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

### Value Data
```
[value: string]             // The actual string value (UTF-8 encoded)
```

For null values:
```
[length: uint32]            // 0 for null strings
```

## Example

### Non-Null String PropertyFactory
```
[property_type: "StrProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[value: "Hello, World!"]
```

### Null String PropertyFactory
```
[property_type: "StrProperty"]
[length: 0]
[array_index: 0]
[terminator: 0]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the size of the string in bytes
- Null strings are represented by a length of 0
- The array_index field is reserved for future use and is always 0
- The terminator byte is always 0
- String values can contain any valid UTF-8 characters 