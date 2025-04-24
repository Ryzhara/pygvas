# Struct Property Binary Format Documentation

## Overview
The `StructProperty` class implements a property type that holds structured data in the GVAS format. It supports both custom structures and special built-in types, with optional GUIDs for type identification.

## Binary Structure

### Standard Header (include_header=True)
```
[Property Type] (String)    // "StructProperty"
[Length] (UInt32)          // Size of the struct data in bytes
[Array Index] (UInt32)     // Always 0
[Terminator] (UInt8)       // Always 0x00
[Type Name] (String)       // Name of the struct type
[GUID] (UUID)             // Optional GUID for type identification
```

### Struct Data
For custom structures:
```
[Property Name] (String)   // Name of the property
[Property Type] (String)   // Type of the property
[Property Data] (Varies)   // Property-specific data
...                       // Repeat for each property
[None] (String)           // "None" terminator
```

For special built-in types:
```
[Type-Specific Data] (Varies) // Data specific to the struct type
```

## Special Built-in Types
The following special struct types are supported:
- DateTimeStruct
- GuidStruct
- TimespanStruct
- IntPointStruct
- LinearColorStruct
- RotatorStruct
- QuatStruct
- VectorStruct
- Vector2DStruct

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the struct data section
- The array_index field is reserved for future use and is always 0
- Custom structures are written as a series of named properties
- Special types have their own optimized serialization format
- The format is compatible with Unreal Engine's native serialization format
- GUIDs are optional and used for type identification
- Properties are written with their full headers
- The "None" terminator marks the end of custom structure data 