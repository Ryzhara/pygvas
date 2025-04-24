# GVAS File Documentation

## Overview
This module provides the core implementation for reading and writing GVAS files, including header handling, compression support, and property management. It supports both standard GVAS format and Palworld's custom format.

## Type Definitions

### UNREAL_ENGINE_PROPERTIES
A union type representing all supported Unreal Engine property types, including:
- Numerical types:
  - BoolProperty
  - ByteProperty
  - Int8Property, UInt8Property
  - Int16Property, UInt16Property
  - Int32Property, UInt32Property
  - Int64Property, UInt64Property
  - FloatProperty, DoubleProperty
- Standard types:
  - DateTimeStruct
  - GuidStruct
  - TimespanStruct
  - IntPointStruct
  - LinearColorStruct
  - RotatorStruct
  - QuatStruct
  - VectorStruct
  - Vector2DStruct
- Aggregator types:
  - SetProperty
  - MapProperty
  - StructProperty
  - ArrayProperty
- Terminal types:
  - EnumProperty
  - TextProperty
  - NameProperty
  - StrProperty
  - ObjectProperty
  - FieldPathProperty
  - DelegateProperty types

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
GVAS_MAGIC (4 bytes) - "GVAS"
save_game_version (u32) - Must be 2 or 3
package_file_version (u32) - Package version number
[if save_game_version >= 3]
    package_file_version_ue5 (u32) - UE5 package version
engine_version (FEngineVersion) - Engine version info
custom_version_format (u32) - Format of custom versions
custom_version_count (u32) - Number of custom versions
[custom_version_count * FCustomVersion] - Custom version entries
save_game_class_name (string) - Class name with null terminator
```

#### FCustomVersion (Inner Class)
Represents a custom version entry in the header.

##### Fields
- `key`: GUID string
- `version`: Version number

##### Binary Format
```
guid (16 bytes) - UUID in little-endian format
version (u32) - Version number
```

### GameFileFormat
Holds information about the deserialized game version and compression type.

#### Fields
- `game_version`: GameVersion enum value
- `compression_type`: CompressionType enum value

#### Methods
- `has_gvas_header`: Checks for GVAS magic number (0x47564153)
- `has_palworld_header`: Checks for Palworld magic number (0x506C5A00)
- `has_zlib_header`: Checks for zlib magic bytes (0x7801, 0x789c, or 0x78da)
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
    property_name (string) - Length-prefixed UTF-8
    property_type (string) - Length-prefixed UTF-8
    property_value (varies) - Depends on property type
    ...
"None" (string) - End marker
0 (u32) - Null terminator
```

For Palworld format:
```
decompressed_size (u32) - Size before compression
compressed_size (u32) - Size after compression
PLZ_MAGIC (3 bytes) - 0x506C5A
compression_type (u8) - Compression type enum
[compressed data] - Compressed GVAS content
```

#### Methods
- `print_game_file_format`: Prints file format information
- `read_file`: Reads a GVAS file from disk
- `read`: Reads GVAS data from a stream
- `write_file`: Writes a GVAS file to disk
- `write`: Writes GVAS data to a stream

## Compression Types

### None (0x30)
- No compression
- Data is written as-is
- Used for uncompressed files

### ZLIB (0x31)
- Single zlib compression
- Uses standard zlib format
- Magic bytes: 0x78 0x01, 0x78 0x9c, or 0x78 0xda
- Used for standard compressed files

### ZLIB_TWICE (0x32)
- Double zlib compression
- Data is compressed twice
- Used in Palworld format
- First compression size is stored in header

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
- Property values are read/written using the appropriate property type handlers
- Context tracking is used for debugging and error reporting
- Custom version support allows for engine-specific features 