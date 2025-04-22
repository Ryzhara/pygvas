# Numerical Property Binary Format Documentation

## Overview
This document describes the binary format for numerical properties in the GVAS (Game Save) format. These properties handle various numeric data types, from booleans to 64-bit integers and floating-point numbers. The file contains several related classes:

1. `BoolProperty` - Boolean values
2. `ByteProperty` - Byte values or type names
3. `Int8Property` - 8-bit signed integers
4. `UInt8Property` - 8-bit unsigned integers
5. `Int16Property` - 16-bit signed integers
6. `UInt16Property` - 16-bit unsigned integers
7. `Int32Property` - 32-bit signed integers
8. `UInt32Property` - 32-bit unsigned integers
9. `Int64Property` - 64-bit signed integers
10. `UInt64Property` - 64-bit unsigned integers
11. `FloatProperty` - 32-bit floating-point numbers
12. `DoubleProperty` - 64-bit floating-point numbers

## Common Structure
All numerical properties follow a similar pattern with a standard header and value data. The main differences are in the size and type of the value data.

### Standard Header Format (include_header=True)
- Property Type (String): Property type name encoded as a string
- Length (UInt32): Size of the value data in bytes
- Array Index (UInt32): Always 0 for numerical properties
- Terminator (UInt8): Always 0x00

## Individual Property Formats

### BoolProperty
**Value Size:** 1 byte
**Special Header:** BoolProperty has a unique header format:
- 4 bytes of zeros (length)
- 4 bytes of zeros (array index)
- No terminator

**Example:**
```
[Header]
00 00 00 00  // Length (0)
00 00 00 00  // Array Index (0)

[Value]
01           // true
00           // Terminator
```

### ByteProperty
**Value Size:** 1 byte or variable (for type names)
**Special Features:**
- Can store either a byte value or a type name
- Includes an additional name field in the header

**Example (Byte Value):**
```
[Header]
00 00 00 0C  "ByteProperty" (12 bytes)
00 00 00 01  Length (1 byte)
00 00 00 00  Array Index (0)
00 00 00 05  Name Length (5)
54 79 70 65 31  "Type1" in UTF-8
00           Terminator

[Value]
FF           // Byte value
```

### Int8Property
**Value Size:** 1 byte
**Example:**
```
[Header]
00 00 00 0B  "Int8Property" (11 bytes)
00 00 00 01  Length (1 byte)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
7F           // 127
```

### UInt8Property
**Value Size:** 1 byte
**Example:**
```
[Header]
00 00 00 0C  "UInt8Property" (12 bytes)
00 00 00 01  Length (1 byte)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF           // 255
```

### Int16Property
**Value Size:** 2 bytes
**Example:**
```
[Header]
00 00 00 0C  "Int16Property" (12 bytes)
00 00 00 02  Length (2 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF 7F        // 32767
```

### UInt16Property
**Value Size:** 2 bytes
**Example:**
```
[Header]
00 00 00 0D  "UInt16Property" (13 bytes)
00 00 00 02  Length (2 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF FF        // 65535
```

### Int32Property
**Value Size:** 4 bytes
**Example:**
```
[Header]
00 00 00 0C  "Int32Property" (12 bytes)
00 00 00 04  Length (4 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF FF FF 7F  // 2147483647
```

### UInt32Property
**Value Size:** 4 bytes
**Example:**
```
[Header]
00 00 00 0D  "UInt32Property" (13 bytes)
00 00 00 04  Length (4 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF FF FF FF  // 4294967295
```

### Int64Property
**Value Size:** 8 bytes
**Example:**
```
[Header]
00 00 00 0C  "Int64Property" (12 bytes)
00 00 00 08  Length (8 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF FF FF FF FF FF FF 7F  // 9223372036854775807
```

### UInt64Property
**Value Size:** 8 bytes
**Example:**
```
[Header]
00 00 00 0D  "UInt64Property" (13 bytes)
00 00 00 08  Length (8 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
FF FF FF FF FF FF FF FF  // 18446744073709551615
```

### FloatProperty
**Value Size:** 4 bytes
**Format:** IEEE 754 single-precision
**Example:**
```
[Header]
00 00 00 0C  "FloatProperty" (12 bytes)
00 00 00 04  Length (4 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
40 49 0F DB  // 3.14159
```

### DoubleProperty
**Value Size:** 8 bytes
**Format:** IEEE 754 double-precision
**Example:**
```
[Header]
00 00 00 0D  "DoubleProperty" (13 bytes)
00 00 00 08  Length (8 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Value]
40 09 21 FB 54 44 2D 18  // 3.141592653589793
```

## Implementation Notes
- All numeric values are stored in little-endian format
- Float values are stored in IEEE 754 format
- BoolProperty has a unique header format with no terminator
- ByteProperty can store either a byte value or a type name
- The format is compatible with Unreal Engine's native serialization format
- All properties use the standard header format except BoolProperty 