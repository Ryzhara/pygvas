# Struct Property Binary Format

## Overview
Struct properties in GVAS files store structured data that can be either a special graphical structure type or a custom structure with arbitrary properties. The format supports both predefined special structs and fully custom structs.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "StructProperty"
[length: uint32]            // Size of the struct data in bytes
[array_index: uint32]       // Always 0
[type_name: string]         // Name of the struct type
[guid: uuid]                // GUID of the struct type
[terminator: uint8]         // Always 0
```

### Body Structure

#### Special Struct Types
When `type_name` matches a special struct type, the body is read using the special struct's own reading method.

#### Custom Struct Types
For custom struct types, the body contains a series of properties until a "None" terminator:

```
[property_name: string]
[property_type: string]
[property_value: Property]  // Varies by property type
...                        // Additional properties
[terminator: "None"]       // End of properties
```

## Special Struct Types
Special struct types are predefined graphical structures that have their own specific binary format. These are handled by the `SpecialStructTrait` interface.

## Custom Struct Types
Custom struct types can contain any combination of GVAS properties:
- String properties
- Integer properties
- Float properties
- Array properties
- Nested struct properties
- And other property types

## Example

### Custom Struct with Multiple Properties
```
[property_type: "StructProperty"]
[length: uint32]
[array_index: 0]
[type_name: "CustomStruct"]
[guid: uuid]
[terminator: 0]
[property_name: "name"]
[property_type: "StrProperty"]
[property_value: "Example"]
[property_name: "count"]
[property_type: "IntProperty"]
[property_value: 42]
[property_name: "items"]
[property_type: "ArrayProperty"]
[property_value: [...]]
[terminator: "None"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field in the header represents the total size of the struct body
- The array_index field is reserved for future use and is always 0
- Custom structs can contain nested properties of any type
- Special structs have their own specific binary format
- The GUID field is used to uniquely identify struct types
- Property names and types are strings
- The "None" terminator indicates the end of property list in custom structs 