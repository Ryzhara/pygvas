# Integer PropertyFactory Binary Format

## Overview
Integer properties in GVAS files store various numeric values, including boolean, byte, floating-point, and integer values of different sizes and signedness. The format supports multiple numeric types with specific size and encoding requirements.

## Binary Structure

### Common Header (when include_header is true)
```
[property_type: string]      // Type of numeric property
[length: uint32]            // Size of the value in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

### Boolean PropertyFactory
```
[property_type: "BoolProperty"]
[length: 0]                 // Always 0 for boolean
[array_index: 0]
[terminator: 0]
[value: uint8]             // 0 or 1
```

### Byte PropertyFactory
```
[property_type: "ByteProperty"]
[length: uint32]           // 1 for byte value, >1 for type_name
[array_index: 0]
[name: string]            // Optional name field
[terminator: 0]
[value: uint8]           // For byte value
[value: bytes]           // For type_name (FString with length prefix)
```

### Float PropertyFactory (32-bit)
```
[property_type: "FloatProperty"]
[length: 4]               // Always 4 bytes
[array_index: 0]
[terminator: 0]
[value: float32]         // 32-bit floating point value
```

### Double PropertyFactory (64-bit)
```
[property_type: "DoubleProperty"]
[length: 8]               // Always 8 bytes
[array_index: 0]
[terminator: 0]
[value: float64]         // 64-bit floating point value
```

### Integer Properties
The following integer types are supported:
- Int8Property (8-bit signed)
- Int16Property (16-bit signed)
- Int32Property (32-bit signed)
- Int64Property (64-bit signed)
- UInt8Property (8-bit unsigned)
- UInt16Property (16-bit unsigned)
- UInt32Property (32-bit unsigned)
- UInt64Property (64-bit unsigned)

Format for all integer properties:
```
[property_type: string]      // e.g., "Int32Property"
[length: uint32]            // Size in bytes (1, 2, 4, or 8)
[array_index: 0]
[terminator: 0]
[value: int]               // Integer value of specified size
```

## Examples

### Boolean PropertyFactory
```
[property_type: "BoolProperty"]
[length: 0]
[array_index: 0]
[terminator: 0]
[value: 1]                // true
```

### Byte PropertyFactory (as byte)
```
[property_type: "ByteProperty"]
[length: 1]
[array_index: 0]
[name: "MyByte"]
[terminator: 0]
[value: 42]               // Byte value
```

### Byte PropertyFactory (as type_name)
```
[property_type: "ByteProperty"]
[length: 12]
[array_index: 0]
[name: "MyType"]
[terminator: 0]
[value: "CustomType"]     // Type name as FString
```

### 32-bit Integer
```
[property_type: "Int32Property"]
[length: 4]
[array_index: 0]
[terminator: 0]
[value: 12345]           // 32-bit integer value
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the size of the value in bytes
- The array_index field is reserved for future use and is always 0
- Boolean properties have a length of 0
- Byte properties can store either a single byte or a type name
- Float and Double properties use IEEE 754 floating-point format
- Integer properties support both signed and unsigned values
- The terminator byte is always 0
- Byte properties with type names use FString format with length prefix
- All numeric values are stored in little-endian format 