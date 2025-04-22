# GVAS File Documentation

## Overview
This module provides the core implementation for reading and writing GVAS files, including header handling, compression support, and property management. It supports both standard GVAS format and Palworld's custom format.

## Constants

### UNREAL_ENGINE_PROPERTIES
A union type representing all supported Unreal Engine property types, including:
- Numerical types (Bool, Byte, Int, Float, etc.)
- Standard types (DateTime, Guid, Timespan, etc.)
- Aggregator types (Set, Map, Struct, Array)
- Terminal types (Enum, Text, Name, Str, Object, etc.)

## Classes

### GvasHeader
Represents the header of a GVAS file.

#### Fields
- `type`: Format version string ("Version2" or "Version3")
- `package_file_version`: Package file version number
- `package_file_version_ue5`: Optional UE5 package file version
- `engine_version`: FEngineVersion instance
- `custom_version_format`: Custom version format number
- `custom_versions`: Dictionary of custom version GUIDs to version numbers
- `save_game_class_name`: Name of the save game class

#### Binary Format
```
GVAS_MAGIC (4 bytes)
save_game_version (u32)
package_file_version (u32)
[if save_game_version >= 3]
    package_file_version_ue5 (u32)
engine_version (FEngineVersion)
custom_version_format (u32)
custom_version_count (u32)
[custom_version_count * FCustomVersion]
save_game_class_name (string)
```

#### FCustomVersion (Inner Class)
Represents a custom version entry in the header.

##### Fields
- `key`: GUID string
- `version`: Version number

##### Binary Format
```
guid (16 bytes)
version (u32)
```

### GameFileFormat
Holds information about the deserialized game version and compression type.

#### Fields
- `game_version`: GameVersion enum value
- `compression_type`: CompressionType enum value

#### Methods
- `has_gvas_header`: Checks for GVAS magic number
- `has_palworld_header`: Checks for Palworld magic number
- `has_zlib_header`: Checks for zlib magic number
- `is_definitely_zlib_compressed`: Tests if data is zlib compressed
- `check_for_palworld`: Validates Palworld file format
- `deserialize_game_version`: Determines game version and compression type

### GVASFile
Main class for handling GVAS files.

#### Fields
- `game_file_format`: GameFileFormat instance
- `header`: GvasHeader instance
- `properties`: Dictionary of property names to property values

#### Binary Format
For standard GVAS:
```
[GvasHeader]
[properties]
    property_name (string)
    property_type (string)
    property_value (varies)
    ...
"None" (string)
0 (u32)
```

For Palworld format:
```
decompressed_size (u32)
compressed_size (u32)
PLZ_MAGIC (3 bytes)
compression_type (u8)
[compressed data]
```

#### Methods
- `print_game_file_format`: Prints file format information
- `read_file`: Reads a GVAS file from disk
- `read`: Reads GVAS data from a stream
- `write_file`: Writes a GVAS file to disk
- `write`: Writes GVAS data to a stream

## Compression Types

### None
- No compression
- Data is written as-is

### ZLIB
- Single zlib compression
- Uses standard zlib format
- Magic bytes: 0x78 0x01, 0x78 0x9c, or 0x78 0xda

### ZLIB_TWICE
- Double zlib compression
- Data is compressed twice
- Used in Palworld format

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- Compression is handled transparently during read/write
- Property types are determined by hints and context
- Custom versions allow for backward compatibility
- The module supports both standard GVAS and Palworld formats
- Error handling uses custom DeserializeError and SerializeError classes
- Stream operations maintain proper position tracking
- The implementation is designed to be compatible with Unreal Engine's native serialization format 