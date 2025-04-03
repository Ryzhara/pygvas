# Set Property Binary Format

## Overview
Set properties in GVAS files store collections of unique values of the same type. Unlike arrays, sets ensure uniqueness of elements and are not supported in arrays themselves.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "SetProperty"
[length: uint32]            // Size of the set data in bytes
[array_index: uint32]       // Always 0
[element_type: string]      // Type of elements in the set
[terminator: uint8]         // Always 0
```

### Set Data
```
[allocation_flags: uint32]  // Set allocation flags
[element_count: uint32]     // Number of elements in the set
[element_1: Property]       // First element (type specified by element_type)
[element_2: Property]       // Second element
...                        // Additional elements
```

## Example

### Set of Integers
```
[property_type: "SetProperty"]
[length: uint32]
[array_index: 0]
[element_type: "IntProperty"]
[terminator: 0]
[allocation_flags: 0]
[element_count: 3]
[element_1: 42]
[element_2: 100]
[element_3: 42]  // Duplicate value (will be stored only once)
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the set data section
- The array_index field is reserved for future use and is always 0
- Set properties are not supported in arrays (include_header must be true)
- Elements are stored without their property headers
- The allocation_flags field is used for set-specific flags
- The element_count field specifies the number of unique elements
- Duplicate values are automatically removed
- Each element must be of the type specified by element_type
- The total_bytes_per_property is calculated as (length - 8) / element_count 