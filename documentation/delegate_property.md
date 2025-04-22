# Delegate Property Binary Format Documentation

## Overview
This document describes the binary format for delegate-related properties in the GVAS (Game Save) format. These properties are used to represent function delegates and multicast delegates in the game's object system. The file contains several related classes:

1. `Delegate` - Represents a single function delegate
2. `DelegateProperty` - Property wrapper for a single delegate
3. `MulticastScriptDelegate` - Represents a collection of delegates
4. `MulticastInlineDelegateProperty` - Property wrapper for inline multicast delegates
5. `MulticastSparseDelegateProperty` - Property wrapper for sparse multicast delegates

## Delegate Class Format

### Binary Format
- Object Name (String):
  - String Length (Int32)
  - String Content (UTF-8 or UTF-16-LE)
  - Terminator (UInt8 or UInt16)
- Function Name (String):
  - String Length (Int32)
  - String Content (UTF-8 or UTF-16-LE)
  - Terminator (UInt8 or UInt16)

### Example
```
[Object Name]
00 00 00 0A  Length (10 = 9 chars + 1 terminator)
50 6C 61 79 65 72 43 68 61 72  "PlayerChar" in UTF-8
00           Terminator

[Function Name]
00 00 00 0C  Length (12 = 11 chars + 1 terminator)
4F 6E 44 61 6D 61 67 65 54 61 6B 65  "OnDamageTake" in UTF-8
00           Terminator
```

## DelegateProperty Class Format

### With Header (include_header=True)
1. **Standard Header**
   - Property Type (String): "DelegateProperty" encoded as a string
   - Length (UInt32): Total length of the delegate data
   - Array Index (UInt32): Always 0 for DelegateProperty
   - Terminator (UInt8): Always 0x00

2. **Delegate Data**
   - Object Name (String)
   - Function Name (String)

### Without Header (include_header=False)
When no header is included, only the Delegate Data portion is written/read.

## MulticastScriptDelegate Class Format

### Binary Format
- Delegate Count (UInt32): Number of delegates in the collection
- Delegate Array: Array of Delegate objects, each containing:
  - Object Name (String)
  - Function Name (String)

### Example
```
00 00 00 02  Delegate Count (2)

[Delegate 1]
00 00 00 0A  Object Name Length (10)
50 6C 61 79 65 72 43 68 61 72  "PlayerChar" in UTF-8
00           Terminator
00 00 00 0C  Function Name Length (12)
4F 6E 44 61 6D 61 67 65 54 61 6B 65  "OnDamageTake" in UTF-8
00           Terminator

[Delegate 2]
00 00 00 0A  Object Name Length (10)
45 6E 65 6D 79 43 68 61 72 20  "EnemyChar" in UTF-8
00           Terminator
00 00 00 0C  Function Name Length (12)
4F 6E 44 61 6D 61 67 65 44 65 61 6C  "OnDamageDeal" in UTF-8
00           Terminator
```

## MulticastInlineDelegateProperty Class Format

### With Header (include_header=True)
1. **Standard Header**
   - Property Type (String): "MulticastInlineDelegateProperty" encoded as a string
   - Length (UInt32): Total length of the multicast delegate data
   - Array Index (UInt32): Always 0
   - Terminator (UInt8): Always 0x00

2. **Multicast Delegate Data**
   - Delegate Count (UInt32)
   - Delegate Array

### Without Header (include_header=False)
When no header is included, only the Multicast Delegate Data portion is written/read.

## MulticastSparseDelegateProperty Class Format

### With Header (include_header=True)
1. **Standard Header**
   - Property Type (String): "MulticastSparseDelegateProperty" encoded as a string
   - Length (UInt32): Total length of the multicast delegate data
   - Array Index (UInt32): Always 0
   - Terminator (UInt8): Always 0x00

2. **Multicast Delegate Data**
   - Delegate Count (UInt32)
   - Delegate Array

### Without Header (include_header=False)
When no header is included, only the Multicast Delegate Data portion is written/read.

## String Encoding Rules
For all string values (object names and function names):
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
  - When writing: Treated as empty strings
  - When reading: Returns empty strings if length is 0
- Empty Delegate Collections:
  - When writing: Delegate count is 0
  - When reading: Creates empty list if count is 0

## Implementation Notes
- All classes use `ByteCountValidator` to ensure the correct number of bytes are read
- When writing, they first write to a temporary buffer to calculate the total length
- The implementation handles both ASCII and non-ASCII strings automatically
- The format is compatible with the original Rust implementation
- Delegates are used to implement event handling and callback systems in the game 