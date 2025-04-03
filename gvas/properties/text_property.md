# Text Property Binary Format

## Overview
Text properties in GVAS files store Unreal Engine FText data, which supports localization and various text formatting options. The format includes both raw text data and structured FText history information.

## Binary Structure

### Header (when include_header is true)
```
[property_type: string]      // "TextProperty"
[length: uint32]            // Size of the text data in bytes
[array_index: uint32]       // Always 0
[terminator: uint8]         // Always 0
```

### Text Data
```
[flags: uint32]             // Text formatting flags
[byte_data: bytes]          // Raw text data
```

### FText Structure (for TextProperty_GENERATED)
```
[flags: uint32]             // Text formatting flags
[history_type: int32]       // Type of text history
[history_data: varies]      // History-specific data
```

### Text History Types

#### None History
```
[type: int32]              // TextHistoryType.NONE (-1)
[culture_invariant_string: string]
```

#### Base History
```
[type: int32]              // TextHistoryType.BASE (0)
[namespace: string]        // Text namespace
[key: string]              // Text key
[source_string: string]    // Original text
```

## Text History Types
The format supports various text history types:
- NONE (-1): Basic text without localization
- BASE (0): Localized text with namespace and key
- NAMED_FORMAT: Named format text
- ORDERED_FORMAT: Ordered format text
- ARGUMENT_FORMAT: Argument format text
- AS_NUMBER: Number formatting
- AS_PERCENT: Percentage formatting
- AS_CURRENCY: Currency formatting
- AS_DATE: Date formatting
- AS_TIME: Time formatting
- AS_DATETIME: DateTime formatting
- TRANSFORM: Text transformation
- STRING_TABLE_ENTRY: String table entry
- TEXT_GENERATOR: Generated text
- RAW_TEXT: Raw text data

## Example

### Simple Text Property
```
[property_type: "TextProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[flags: 0]
[byte_data: "Hello, World!"]
```

### Localized Text Property
```
[property_type: "TextProperty"]
[length: uint32]
[array_index: 0]
[terminator: 0]
[flags: 0]
[history_type: 0]  // BASE
[namespace: "GameUI"]
[key: "WelcomeMessage"]
[source_string: "Welcome to the game!"]
```

## Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the text data section
- The array_index field is reserved for future use and is always 0
- Text properties support both raw text and structured FText data
- FText history types determine how the text is formatted and localized
- The flags field controls text formatting options
- Byte data is stored as-is without modification
- The actual_text_count field is used by parent properties 