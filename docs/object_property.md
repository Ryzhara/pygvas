# Object PropertyFactory Binary Format

## Overview
Object properties in GVAS files store references to game objects using string identifiers. The format includes a header with length information and a string value that represents the object reference.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "ObjectProperty"
[length: uint32]            // Size of the object reference string in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

### Object Reference Data
```
[value: string]             // The object reference string (UTF-8 encoded)
```

## Example

### Simple Object Reference
```
[property_type: "ObjectProperty"]
[length: 15]
[array_index: 0]
[terminator: 0]
[value: "PlayerCharacter"]
```

### Complex Object Reference
```
[property_type: "ObjectProperty"]
[length: 32]
[array_index: 0]
[terminator: 0]
[value: "GameWorld.Players.Player1"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the size of the object reference string in bytes
- The array_index field is reserved for future use and is always 0
- The terminator byte is always 0
- Object references can be simple identifiers or dot-separated paths
- The value string represents the object's identifier in the game world
- The length field is verified during deserialization to ensure data integrity
- Object properties are used to reference other objects in the game's object hierarchy 