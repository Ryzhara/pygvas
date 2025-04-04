# Map Property Binary Format

## Overview
Map properties in GVAS files store key-value pairs where both keys and values can be of any GVAS property type. The format supports dynamic key and value types specified in the header.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "MapProperty"
[length: uint32]            // Size of the map data in bytes
[array_index: uint32]       // Always 0
[key_type: string]          // Type of property used for keys
[value_type: string]        // Type of property used for values
[terminator: uint8]         // Always 0
```

### Map Data
```
[allocation_flags: uint32]  // Map allocation flags
[element_count: uint32]     // Number of key-value pairs
[key_1: Property]          // First key (type specified by key_type)
[value_1: Property]        // First value (type specified by value_type)
[key_2: Property]          // Second key
[value_2: Property]        // Second value
...                        // Additional key-value pairs
```

## Example

### Map of String to Integer
```
[property_type: "MapProperty"]
[length: uint32]
[array_index: 0]
[key_type: "StrProperty"]
[value_type: "IntProperty"]
[terminator: 0]
[allocation_flags: 0]
[element_count: 2]
[key_1: "first"]
[value_1: 42]
[key_2: "second"]
[value_2: 100]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the map data section
- The array_index field is reserved for future use and is always 0
- Key and value types can be any valid GVAS property type
- Keys and values are stored without their property headers
- The allocation_flags field is used for map-specific flags
- The element_count field specifies the number of key-value pairs
- Keys must be unique within the map
- The HashableIndexMap type is used to store the key-value pairs 