# Engine Tools Documentation

## Overview
This module provides essential tools and utilities for handling Unreal Engine version information, compression types, and serialization in the GVAS format. It includes classes for managing engine versions, custom serialization versions, and validation of binary data.

## Constants

### Magic Numbers
- `GVAS_MAGIC`: The magic number that appears at the start of every GVAS file
- `PLZ_MAGIC`: A special magic number used in Rust implementation

## Enums

### CompressionType
Defines the compression types used in Palworld custom file format:
- `UNKNOWN`: Unknown compression type (0x00)
- `NONE`: No compression (0x30)
- `ZLIB`: Zlib compression (0x31)
- `ZLIB_TWICE`: Double Zlib compression (0x32)
- `PLZ`: Palworld specific compression type (0xFF)

### GameVersion
Defines supported game versions:
- `UNKNOWN`: Unknown version (0)
- `DEFAULT`: Default version (1)
- `PALWORLD`: Palworld version (2)

### EngineVersion
Defines Unreal Engine versions from UE4 to UE5:
- Versions range from `VER_UE4_0` to `VER_UE4_27`
- UE5 versions from `VER_UE5_0` to `VER_UE5_2`
- Special versions:
  - `VER_UE4_AUTOMATIC_VERSION`: Newest specified version (4.27)
  - `VER_UE4_AUTOMATIC_VERSION_PLUS_ONE`: Version plus one (4.28)

## Classes

### FEngineVersion
Represents the Unreal Engine version in which a GVAS file was saved.

#### Fields
- `major`: Major version number (u16)
- `minor`: Minor version number (u16)
- `patch`: Patch version number (u16)
- `change_list`: Build ID (u32)
- `branch`: Build ID string

#### Methods
- `new(major, minor, patch, change_list, branch)`: Creates a new FEngineVersion instance
- `format()`: Returns a formatted version string
- `read(stream)`: Reads version information from a binary stream
- `write(stream)`: Writes version information to a binary stream
- `get_version()`: Returns the corresponding EngineVersion enum value

### FEditorObjectVersion
Custom serialization version for changes made in Dev-Editor stream.

#### Properties
- `friendly_name`: Returns the class name
- `custom_version_guid`: Returns a UUID for version identification
- `version_mappings`: Maps engine versions to object versions

#### Version Constants
Defines various version changes and their introduction points, including:
- Text formatting changes
- Material system updates
- Mesh description modifications
- Animation system improvements
- And many more specialized changes

### FUE5ReleaseStreamObjectVersion
Custom serialization version for changes made in UE5/Release-* stream.

#### Properties
- `friendly_name`: Returns the class name
- `custom_version_guid`: Returns a UUID for version identification
- `version_mappings`: Maps engine versions to object versions

#### Version Constants
Defines UE5-specific version changes, including:
- Lumen reflections
- World partition updates
- Material system changes
- Animation system improvements
- And other UE5-specific features

### ByteCountValidator
Validates the number of bytes read from a stream.

#### Fields
- `stream`: The binary stream to validate
- `expected_byte_count`: Expected number of bytes to read
- `do_validation`: Whether to perform validation
- `start_byte`: Starting position in stream
- `end_byte`: Ending position in stream

#### Methods
- `__enter__()`: Records starting position
- `__exit__()`: Validates bytes read and handles exceptions

### EngineVersionTool
Provides tools for serialization and version management.

#### Class Fields
- `custom_versions`: Dictionary of custom version GUIDs to version numbers
- `hints`: Dictionary of parsing hints
- `context_stack`: Stack of context strings
- `engine_major`: Major engine version
- `engine_minor`: Minor engine version
- `unit_tests_running`: Whether unit tests are running

#### Methods
- `set_inside_unit_tests()`: Marks that unit tests are running
- `inside_unit_tests()`: Checks if unit tests are running
- `set_engine_version(major, minor)`: Sets the engine version
- `version_is_at_least(major, minor)`: Checks if current version is at least specified version
- `version_is_less_than(major, minor)`: Checks if current version is less than specified version
- `set_custom_versions(versions)`: Sets custom version mappings
- `push_context_step(step)`: Pushes a context step onto the stack
- `pop_context_step()`: Pops a context step from the stack
- `get_context_path()`: Returns the current context path
- `supports_version(version)`: Checks if a custom version is supported

### ContextScopeTracker
Manages context tracking during serialization.

#### Fields
- `parent_context`: Parent context string
- `context`: Current context string

#### Methods
- `__enter__()`: Pushes context onto the stack
- `__exit__()`: Pops context from the stack and handles exceptions

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- Version information is crucial for proper serialization
- Context tracking helps with debugging and error reporting
- Custom versions allow for backward compatibility
- Byte count validation ensures data integrity
- The module is designed to be compatible with Unreal Engine's native serialization format 