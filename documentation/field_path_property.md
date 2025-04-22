# FieldPathProperty Binary Format Documentation

## Overview
The `FieldPathProperty` class implements a property type that holds a field path value in the GVAS (Game Save) format. It handles reading and writing field paths, which consist of a list of path elements and a resolved owner. This is used to reference specific fields or properties within the game's object system.

## Binary Format Structure

### With Header (include_header=True)
When a header is included, the format consists of two parts:

1. **Standard Header**
   - Property Type (String): "FieldPathProperty" encoded as a string
   - Length (UInt32): Total length of the field path data
   - Array Index (UInt32): Always 0 for FieldPathProperty
   - Terminator (UInt8): Always 0x00

2. **Field Path Data**
   - Path Element Count (UInt32): Number of path elements
   - Path Elements (String[]): Array of strings, each encoded as:
     - String Length (Int32): 
       - If positive: Length of UTF-8 string + 1
       - If negative: Length of UTF-16-LE string + 1
     - String Content:
       - For ASCII strings: UTF-8 encoded bytes
       - For non-ASCII strings: UTF-16-LE encoded bytes
     - Terminator:
       - For ASCII strings: UInt8 (0x00)
       - For non-ASCII strings: UInt16 (0x0000)
   - Resolved Owner (String): Encoded using the same string format as path elements

### Without Header (include_header=False)
When no header is included, only the Field Path Data portion is written/read.

## String Encoding Rules
For each string in the path elements and resolved owner:
- If the string contains only ASCII characters:
  - Encoded as UTF-8
  - Length prefix is positive
  - Terminated with a single null byte (0x00)
- If the string contains non-ASCII characters:
  - Encoded as UTF-16-LE
  - Length prefix is negative
  - Terminated with a null word (0x0000)

## Special Cases
- Empty Path:
  - When writing: Path element count is 0
  - When reading: Creates an empty list
- Null/None values:
  - When writing: Treated as an empty path with empty resolved owner
  - When reading: Returns empty path and resolved owner if length is 0

## Example Binary Layout

### Simple Field Path with ASCII Elements
```
[Header]
00 00 00 0F  "FieldPathProperty" (15 bytes)
00 00 00 1A  Length (26 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Field Path Data]
00 00 00 02  Path Element Count (2)
00 00 00 05  Length (5 = 4 chars + 1 terminator)
47 61 6D 65  "Game" in UTF-8
00           Terminator
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 53 74 61 74  "PlayerStat" in UTF-8
00           Terminator
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 43 68 61 72  "PlayerChar" in UTF-8
00           Terminator
```

### Field Path with Non-ASCII Elements
```
[Header]
00 00 00 0F  "FieldPathProperty" (15 bytes)
00 00 00 1C  Length (28 bytes)
00 00 00 00  Array Index (0)
00           Terminator

[Field Path Data]
00 00 00 01  Path Element Count (1)
00 00 00 F6  Length (-10 = -5 chars - 1 terminator)
83 7C 83 8C 83 43 83 8B 83 45  "プレイヤー" in UTF-16-LE
00 00        Terminator
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 43 68 61 72  "PlayerChar" in UTF-8
00           Terminator
```

## Implementation Notes
- The class uses a `ByteCountValidator` to ensure the correct number of bytes are read
- When writing, it first writes to a temporary buffer to calculate the total length
- The implementation handles both ASCII and non-ASCII strings automatically
- The format is compatible with the original Rust implementation (field_path_property.rs)
- Field paths are used to reference specific properties or fields within the game's object hierarchy 