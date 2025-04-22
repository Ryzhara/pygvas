# EnumProperty Binary Format Documentation

## Overview
The `EnumProperty` class implements a property type that holds an enumeration value in the GVAS (Game Save) format. It handles reading and writing enum values, which consist of an enum type and a specific enum value. This is used to represent enumerated types within the game's object system.

## Binary Format Structure

### With Header (include_header=True)
When a header is included, the format consists of two parts:

1. **Standard Header**
   - Property Type (String): "EnumProperty" encoded as a string
   - Length (UInt32): Total length of the enum value data
   - Array Index (UInt32): Always 0 for EnumProperty
   - Enum Type (String): The type of the enumeration
   - Terminator (UInt8): Always 0x00

2. **Enum Value Data**
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
When no header is included, only the Enum Value Data portion is written/read.

## String Encoding Rules
For both the enum type and value:
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
- Empty Enum Type:
  - When writing: Uses empty string if enum_type is None
  - When reading: Stores None if enum_type is empty string

## Example Binary Layout

### ASCII Enum Value
```
[Header]
00 00 00 0C  "EnumProperty" (12 bytes)
00 00 00 0A  Length (10 bytes)
00 00 00 00  Array Index (0)
00 00 00 0A  Enum Type Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 54 79 70 65  "PlayerType" in UTF-8
00           Terminator

[Enum Value Data]
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 4F 6E 65  "PlayerOne" in UTF-8
00           Terminator
```

### Non-ASCII Enum Value
```
[Header]
00 00 00 0C  "EnumProperty" (12 bytes)
00 00 00 0C  Length (12 bytes)
00 00 00 00  Array Index (0)
00 00 00 0A  Enum Type Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 54 79 70 65  "PlayerType" in UTF-8
00           Terminator

[Enum Value Data]
00 00 00 F6  Length (-10 = -5 chars - 1 terminator)
83 7C 83 8C 83 43 83 8B 83 45  "プレイヤー" in UTF-16-LE
00 00        Terminator
```

## Implementation Notes
- The class uses a `ByteCountValidator` to ensure the correct number of bytes are read
- When writing, it first writes to a temporary buffer to calculate the total length
- The implementation handles both ASCII and non-ASCII strings automatically
- The format is compatible with the original Rust implementation (enum_property.rs)
- Enum properties are used to represent fixed sets of named values within the game's object system 