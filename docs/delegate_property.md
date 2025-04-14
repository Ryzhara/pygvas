# Delegate PropertyFactory Binary Format

## Overview
Delegate properties in GVAS files store function references that can be used for event handling and callbacks. The format supports both single delegates and multicast delegates (which can have multiple function references).

## Binary Structure

### Single Delegate PropertyFactory
#### Header (when include_header is true)
```
[property_type: string]      // "DelegateProperty"
[length: uint32]            // Size of the delegate data in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

#### Delegate Data
```
[object: string]            // Object containing the function
[function_name: string]     // Name of the function to call
```

### Multicast Delegate PropertyFactory
#### Header (when include_header is true)
```
[property_type: string]      // "MulticastInlineDelegateProperty"
[length: uint32]            // Size of the delegate data in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

#### Multicast Delegate Data
```
[delegate_count: uint32]    // Number of delegates in the multicast
[delegate_1: Delegate]      // First delegate
[delegate_2: Delegate]      // Second delegate
...                        // Additional delegates
```

## Example

### Single Delegate
```
[property_type: "DelegateProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[object: "PlayerCharacter"]
[function_name: "OnDamageTaken"]
```

### Multicast Delegate
```
[property_type: "MulticastInlineDelegateProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[delegate_count: 2]
[delegate_1: {
    object: "PlayerCharacter",
    function_name: "OnDamageTaken"
}]
[delegate_2: {
    object: "GameManager",
    function_name: "HandlePlayerDamage"
}]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the delegate data section
- The array_index field is reserved for future use and is always 0
- Single delegates can only reference one function
- Multicast delegates can reference multiple functions
- The object field specifies which object contains the function
- The function_name field specifies which function to call
- The terminator byte is always 0
- Multicast delegates maintain a list of multiple function references
- The delegate_count field specifies how many functions are referenced 