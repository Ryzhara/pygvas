# Array Property Binary Format

## Overview
Array properties in GVAS files store collections of values of the same type. The format supports both primitive types and complex property types.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "ArrayProperty"
[length: uint32]            // Size of the array data in bytes
[array_index: uint32]       // Always 0
[array_type: string]        // Type of elements in the array
[terminator: uint8]         // Always 0
```

### Array Data
```
[array_length: uint32]      // Number of elements in the array
[element_1: Property]       // First element (type depends on array_type)
[element_2: Property]       // Second element
...                        // Additional elements
```

## Element Types

### Primitive Types
When `array_type` is a primitive type, elements are stored directly:

| Type | Binary Format |
|------|---------------|
| Bool | 1 byte (0 or 1) |
| Int8 | 1 byte signed integer |
| Int16 | 2 bytes signed integer (little-endian) |
| Int32 | 4 bytes signed integer (little-endian) |
| Int64 | 8 bytes signed integer (little-endian) |
| UInt8 | 1 byte unsigned integer |
| UInt16 | 2 bytes unsigned integer (little-endian) |
| UInt32 | 4 bytes unsigned integer (little-endian) |
| UInt64 | 8 bytes unsigned integer (little-endian) |
| Float | 4 bytes IEEE 754 float (little-endian) |
| Double | 8 bytes IEEE 754 double (little-endian) |
| String | [length: uint32][utf8_bytes: bytes] |

### Complex Types
When `array_type` is a complex property type, each element is stored as a complete property with its own header and data.

## Example

### Array of Strings
```
[property_type: "ArrayProperty"]
[length: uint32]
[array_index: 0]
[array_type: "StrProperty"]
[terminator: 0]
[array_length: 3]
[element_1: "First string"]
[element_2: "Second string"]
[element_3: "Third string"]
```

### Array of Integers
```
[property_type: "ArrayProperty"]
[length: uint32]
[array_index: 0]
[array_type: "IntProperty"]
[terminator: 0]
[array_length: 4]
[element_1: 42]
[element_2: -17]
[element_3: 0]
[element_4: 100]
```

## Notes
- All integers are stored in little-endian format
- String elements are length-prefixed UTF-8 encoded
- Complex property elements include their own headers
- The array_index field is reserved for future use and is always 0
- The length field in the header represents the total size of the array data section
- The array_length field represents the number of elements in the array 