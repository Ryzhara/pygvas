# NameProperty Binary Format Documentation

## Overview
The `NameProperty` class implements a property type that holds a name value in the GVAS (Game Save) format. It handles reading and writing name values to/from binary streams. Unlike other string-based properties, NameProperty includes an array index in its header.

## Binary Format Structure

### With Header (include_header=True)
When a header is included, the format consists of two parts:

1. **Standard Header**
   - Property Type (String): "NameProperty" encoded as a string
   - Length (UInt32): Total length of the string data
   - Array Index (UInt32): Index value for the name (can be non-zero)
   - Terminator (UInt8): Always 0x00

2. **String Data**
   - String Length (Int32): 
     - If positive: Length of UTF-8 string + 1 (for terminator)
     - If negative: Length of UTF-16-LE string + 1 (for terminator)
   - String Content:
     - For ASCII strings: UTF-8 encoded bytes
     - For non-ASCII strings: UTF-16-LE encoded bytes
   - Terminator:
     - For ASCII strings: UInt8 (0x00)
     - For non-ASCII strings: UInt16 (0x0000)

### Without Header (include_header=False)
When no header is included, only the String Data portion is written/read.

## String Encoding Rules
- If the string contains only ASCII characters:
  - Encoded as UTF-8
  - Length prefix is positive
  - Terminated with a single null byte (0x00)
- If the string contains non-ASCII characters:
  - Encoded as UTF-16-LE
  - Length prefix is negative
  - Terminated with a null word (0x0000)

## Special Cases
- Null/None values:
  - When writing: Treated as an empty string with length 0
  - When reading: Returns None if length is 0
- Array Index:
  - Unlike other properties, NameProperty can have a non-zero array index
  - The array index is preserved during serialization/deserialization

## Example Binary Layout

### ASCII Name "PlayerName" with Array Index 1
```
[Header]
00 00 00 0B  "NameProperty" (11 bytes)
00 00 00 0A  Length (10 bytes)
00 00 00 01  Array Index (1)
00           Terminator

[String Data]
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 4E 61 6D 65  "PlayerName" in UTF-8
00           Terminator
```

### Non-ASCII Name "プレイヤー" with Array Index 0
```
[Header]
00 00 00 0B  "NameProperty" (11 bytes)
00 00 00 0C  Length (12 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[String Data]
00 00 00 F6  Length (-10 = -5 chars - 1 terminator)
83 7C 83 8C 83 43 83 8B 83 45  "プレイヤー" in UTF-16-LE
00 00        Terminator
```

## Implementation Notes
- The class uses a `ByteCountValidator` to ensure the correct number of bytes are read
- When writing, it first writes to a temporary buffer to calculate the total length
- The implementation handles both ASCII and non-ASCII strings automatically
- The format is compatible with the original Rust implementation (name_property.rs)
- The array index is a distinguishing feature of NameProperty compared to other string-based properties 