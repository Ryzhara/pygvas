# GVAS File Format Specification

## Overview
GVAS (Game Versioned Archive System) is a binary file format designed for game save files, particularly used in Unreal Engine games. The format supports versioning, compression, and property-based data storage.

## File Structure

### 1. PalWorld-Specific Header
*(Only present for PalWorld game version)*

| Field | Type | Description |
|-------|------|-------------|
| decompressed_size | uint32 | Size of decompressed data |
| compressed_size | uint32 | Size of compressed data |
| magic | 3 bytes | PLZ_MAGIC identifier |
| compression_type | int8 | Compression method (0x30=NONE, 0x31=ZLIB, 0x32=ZLIB_TWICE) |

### 2. Compressed Data Section
*(If compression is enabled)*

| Compression Type | Description |
|-----------------|-------------|
| ZLIB | Single zlib compression |
| ZLIB_TWICE | Double zlib compression |
| NONE | No compression |

### 3. Main GVAS Header

| Field | Type | Description |
|-------|------|-------------|
| magic | 4 bytes | "GVAS" identifier |
| save_game_version | uint32 | Version number (2 or 3) |
| package_file_version | uint32 | Package file version |
| package_file_version_ue5 | uint32 | UE5 version (only if save_game_version >= 3) |
| engine_version_major | uint16 | Major engine version |
| engine_version_minor | uint16 | Minor engine version |
| engine_version_patch | uint16 | Patch version |
| engine_version_build | uint32 | Build number |
| engine_version_branch | string | Engine branch name |
| custom_version_format | uint32 | Custom version format identifier |
| custom_version_count | uint32 | Number of custom versions |
| custom_versions | array | Array of (GUID, version) pairs |
| save_game_class_name | string | Name of save game class |

### 4. Properties Section

The properties section contains a series of property entries until a "None" property is encountered:

```
[property_name: string]
[property_type: string]
[property_value: Property]  // Varies by property type
... (repeats until property_name == "None")
[NULL: uint32]  // 0 byte terminator
```

## Technical Details

### Endianness
- All integers are stored in little-endian format

### String Format
- Strings are length-prefixed
- String encoding is UTF-8

### Compression Types
1. **NONE**
   - No compression applied
   - Data is stored as-is

2. **ZLIB**
   - Single zlib compression
   - Standard zlib algorithm

3. **ZLIB_TWICE**
   - Double zlib compression
   - Data is compressed twice using zlib

### Version Support
- Supports multiple engine versions
- Special handling for UE5 versions
- Custom versioning system through GUID-version pairs

### Game-Specific Extensions
- PalWorld includes additional header information
- Format maintains extensibility for game-specific needs

## File Termination
The file ends with:
1. A property named "None"
2. A NULL terminator (uint32 with value 0)

## Notes
- The format is designed for backward compatibility
- Property values can vary in structure based on their type
- The format supports both compressed and uncompressed data
- Game-specific extensions (like PalWorld's header) are handled transparently 