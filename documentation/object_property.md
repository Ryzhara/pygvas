# ObjectProperty Binary Format Documentation

## Overview
The `ObjectProperty` class implements a property type that holds an object reference in the GVAS (Game Save) format. It handles reading and writing object references to/from binary streams.

## Binary Format Structure

### With Header (include_header=True)
When a header is included, the format consists of two parts:

1. **Standard Header**
   - Property Type (String): "ObjectProperty" encoded as a string
   - Length (UInt32): Total length of the string data
   - Array Index (UInt32): Always 0 for ObjectProperty
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

## Example Binary Layout

### ASCII Object Reference "PlayerCharacter"
```
[Header]
00 00 00 0E  "ObjectProperty" (14 bytes)
00 00 00 10  Length (16 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[String Data]
00 00 00 10  Length (16 = 15 chars + 1 terminator)
50 6C 61 79 65 72 43 68 61 72 61 63 74 65 72  "PlayerCharacter" in UTF-8
00           Terminator
```

### Non-ASCII Object Reference "プレイヤー"
```
[Header]
00 00 00 0E  "ObjectProperty" (14 bytes)
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
- The format is compatible with the original Rust implementation (object_property.rs)
- Object references are stored as strings that identify the object in the game's object system 