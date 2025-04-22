# Set Property Binary Format Documentation

## Overview
The `SetProperty` class implements a property type that holds a set of unique values in the GVAS format. It supports various element types and includes allocation flags for memory management.

## Binary Structure

### Standard Header (include_header=True)
```
[Property Type] (String)    // "SetProperty"
[Length] (UInt32)          // Size of the set data in bytes
[Array Index] (UInt32)     // Always 0
[Terminator] (UInt8)       // Always 0x00
[Property Type] (String)   // Type of elements in the set
```

### Set Data
```
[Allocation Flags] (UInt32) // Memory allocation flags
[Element Count] (UInt32)   // Number of elements in the set
[Elements] (Array)         // Array of elements
```

### Element Format
```
[Element Data] (Varies)    // Element data, format depends on property type
```

## Supported Element Types
- Any property type that can be used as a set element
- Elements are written without property headers
- Each element must be unique within the set

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the set data section
- The array_index field is reserved for future use and is always 0
- Elements are written sequentially without property headers
- The format is compatible with Unreal Engine's native serialization format
- Allocation flags control memory management behavior
- Set elements must be unique (duplicates are not allowed)
- The property type determines how elements are compared for uniqueness 