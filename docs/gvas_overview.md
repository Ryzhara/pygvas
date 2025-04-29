# GVAS Library Overview

## Introduction

The GVAS (Game Version Agnostic Save) library is a Python implementation for reading, writing, and manipulating Unreal Engine save game files. It provides a comprehensive set of tools for working with the serialized format used by Unreal Engine games to store save game data, with a focus on flexibility and support for various game versions.

This library is a Python port of an original Rust implementation, designed to maintain compatibility while leveraging Python's strengths for ease of use and integration with other Python tools and libraries.

## Purpose

The primary purposes of the GVAS library are:

1. **Save File Parsing**: Read and interpret Unreal Engine save files (.sav) from various games
2. **Save File Generation**: Create and modify save files for Unreal Engine games
3. **Game Version Support**: Handle differences in save file formats across various Unreal Engine versions and games
4. **Data Manipulation**: Provide a clean API for inspecting and modifying save game data
5. **Format Conversion**: Convert between binary save files and human-readable formats (e.g., JSON)

## Core Components

The GVAS library is organized into several key components, each handling different aspects of the save file format:

### Main Module Components

- **gvas_file.py**: The central module that ties everything together, providing high-level functions for reading and writing save files
- **gvas_utils.py**: Utility functions for binary operations, common across the library
- **engine_tools.py**: Tools for working with engine versions, game versions, and compression methods
- **gvas_types.py**: Specialized data types (mostly unused in the Python version)
- **error.py**: Custom exception types for detailed error reporting

### Property Types

The `properties/` directory contains implementations of various property types supported by the GVAS format:

- **property_base.py**: Base classes and the property factory for creating property instances
- **numerical_properties.py**: Integer, floating-point, and boolean property types
- **text_property.py**: Complex text handling with localization support
- **aggregator_properties.py**: Container properties (arrays, maps, sets, structs)
- **standard_structs.py**: Implementations of common Unreal Engine data structures
- **str_property.py**, **name_property.py**, **enum_property.py**: Various string-based property types
- **object_property.py**, **field_path_property.py**: Reference property types
- **delegate_property.py**: Function reference property types

## Architecture

The GVAS library follows a modular architecture with clean separation of concerns:

```
GVAS Library
│
├── Core Components
│   ├── GVASFile (High-level container)
│   ├── Serialization/Deserialization Logic
│   ├── Utility Functions
│   └── Error Handling
│
├── Property System
│   ├── PropertyTrait (Base interface)
│   ├── PropertyFactory (Factory pattern)
│   └── Property Types (Implementation)
│
└── Engine Compatibility
    ├── Version Detection
    ├── Game-specific Handling
    └── Compression Support
```

### Data Flow

The typical data flow when using the library:

1. **Reading**: Binary file → Decompression (if needed) → Header parsing → Property deserialization → Property objects
2. **Manipulation**: Property access/modification through Python objects
3. **Writing**: Property objects → Property serialization → Header generation → Compression (if needed) → Binary file

## Key Features

### Property System

The property system is the heart of the GVAS library, with the following features:

- **Extensible**: New property types can be added by implementing the `PropertyTrait` interface
- **Type-safe**: Properties maintain their correct types and validate data during serialization
- **Factory Pattern**: The `PropertyFactory` creates appropriate property instances based on type names
- **Binary Format**: Each property type knows how to read/write its specific binary format

### Compression Support

The library supports various compression methods used by Unreal Engine games:

- **None**: Uncompressed data
- **ZLIB**: Standard ZLIB compression
- **ZLIB_TWICE**: Double compression (used by games like Palworld)

### Game Version Support

The library adapts to different game versions:

- **Engine Version Detection**: Automatically detects the Unreal Engine version from the file
- **Custom Versions**: Tracks game-specific custom version GUIDs
- **Game-specific Features**: Special handling for known games like Palworld

### JSON Conversion

For debugging and easier manipulation, the library provides:

- **Serialization to JSON**: Convert binary save files to human-readable JSON
- **Deserialization from JSON**: Recreate binary save files from edited JSON
- **Schema Validation**: Ensure the JSON structure matches expected property types

## Usage Patterns

### Basic Usage

```python
from gvas.gvas_file import GVASFile

# Load a save file
save_data = GVASFile.deserialize_gvas_file("save.sav")

# Access properties
player_name = save_data.properties["PlayerName"].value

# Modify properties
save_data.properties["PlayerLevel"].value = 50

# Save the modified file
save_data.serialize_to_gvas_file("modified_save.sav")
```

### JSON Conversion

```python
# Convert to JSON for inspection or editing
save_data.serialize_to_json_file("save.json")

# Later, load the JSON back
from_json = GVASFile.deserialize_from_json_file("save.json")
```

### Deserialization Hints

For complex save files where property types may be ambiguous:

```python
hints = {
    "PlayerInventory": "ArrayProperty",
    "PlayerStats.Details": "StructProperty"
}
save_data = GVASFile.deserialize_gvas_file("save.sav", deserialization_hints=hints)
```

## Performance Considerations

- **Streaming**: Uses Python's IO system for efficient file handling
- **Lazy Loading**: Certain property types support deferred loading of large data
- **Memory Usage**: Balances between memory usage and performance

## Documentation Structure

The documentation for the GVAS library is organized by module:

1. **Core Documentation**: Overview, architecture, and general usage
2. **Module Documentation**: Detailed documentation for each module
3. **Property Type Documentation**: Specifications for each property type
4. **Binary Format Documentation**: Details of the binary format for each component

## Implementation Notes

- **Python vs. Rust**: This library is a Python port of a Rust implementation, with adaptations for Python's features
- **Pydantic Integration**: Uses Pydantic for data validation and serialization
- **Type Annotations**: Extensive use of Python type hints for better IDE support
- **Error Handling**: Detailed error messages with binary positions for debugging

## Resources

- **Version Compatibility**: Information about Unreal Engine version compatibility
- **Binary Format Reference**: Details of the GVAS binary format
- **Property Type Reference**: Complete list of supported property types and their formats

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 