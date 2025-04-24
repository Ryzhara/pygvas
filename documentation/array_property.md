# Array Property Binary Format Documentation

## Overview
The `ArrayProperty` class implements a property type that holds an array of values in the GVAS format. It supports various element types and includes special handling for different property types.

## Binary Structure

### Standard Header (include_header=True)
```
[Property Type] (String)    // "ArrayProperty"
[Length] (UInt32)          // Size of the array data in bytes
[Array Index] (UInt32)     // Always 0
[Terminator] (UInt8)       // Always 0x00
[Property Type] (String)   // Type of elements in the array
```

### Array Data
```
[Element Count] (UInt32)   // Number of elements in the array
[Elements] (Array)         // Array of elements, format depends on property type
```

## Element Types

### StructProperty Elements
```
[Field Name] (String)      // Field name for struct
[Member Type] (String)     // Must match property type
[Type Name] (String)       // Struct type name
[GUID] (UUID)             // Optional GUID
[Struct Data] (Varies)     // Struct-specific data
```

### ByteProperty Elements
```
[Byte Data] (Bytes)        // Raw byte data
```

### Bare Type Elements
For simple types, the elements are written directly without headers:
- StrProperty: String
- NameProperty: String
- EnumProperty: String
- GuidStruct: UUID
- BoolProperty: Bool
- Int8Property: Int8
- UInt8Property: UInt8
- Int16Property: Int16
- UInt16Property: UInt16
- Int32Property: Int32
- UInt32Property: UInt32
- IntProperty: Int32 (backward compatibility)
- Int64Property: Int64
- UInt64Property: UInt64
- FloatProperty: Float32
- DoubleProperty: Float64

### Other Property Types
```
[Element Data] (Varies)    // Property-specific data without header
```

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the array data section
- The array_index field is reserved for future use and is always 0
- StructProperty elements include additional header information
- ByteProperty can store either raw bytes or a single ByteProperty
- Simple types are written directly without property headers
- The format is compatible with Unreal Engine's native serialization format
- Special handling for different property types to optimize storage 