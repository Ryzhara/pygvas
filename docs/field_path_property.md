# Field Path PropertyFactory Binary Format

## Overview
Field path properties in GVAS files store references to object fields or properties in the game's object hierarchy. The format includes a list of path elements that describe how to navigate to a specific field, along with the resolved owner of the field.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "FieldPathProperty"
[length: uint32]            // Size of the field path data in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

### Field Path Data
```
[path_element_count: uint32] // Number of elements in the path
[path_element_1: string]    // First path element
[path_element_2: string]    // Second path element
...                        // Additional path elements
[resolved_owner: string]    // Owner of the field
```

## Example

### Simple Field Path
```
[property_type: "FieldPathProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[path_element_count: 2]
[path_element_1: "PlayerCharacter"]
[path_element_2: "Inventory"]
[resolved_owner: "GameWorld"]
```

### Complex Field Path
```
[property_type: "FieldPathProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[path_element_count: 4]
[path_element_1: "GameWorld"]
[path_element_2: "Players"]
[path_element_3: "Player1"]
[path_element_4: "Equipment"]
[resolved_owner: "GameWorld"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the field path data section
- The array_index field is reserved for future use and is always 0
- The path_element_count field specifies how many elements are in the path
- Each path element is a string that represents a step in the object hierarchy
- The resolved_owner field specifies the owner of the field being referenced
- Path elements are stored in order from root to target
- The terminator byte is always 0
- Field paths can be used to reference nested properties in complex object hierarchies 