# Text Property Binary Format Documentation

## Overview
The `TextProperty` class implements a property type that holds FText data in the GVAS format. FText is Unreal Engine's text system that supports localization and various text formatting options. The format includes both raw text data and structured FText history information.

## Binary Structure

### Standard Header (include_header=True)
```
[Property Type] (String)    // "TextProperty"
[Length] (UInt32)          // Size of the text data in bytes
[Array Index] (UInt32)     // Always 0
[Terminator] (UInt8)       // Always 0x00
```

### FText Data
```
[Flags] (UInt32)           // Text formatting flags
[History Type] (Int32)     // Type of text history
[History Data] (Varies)    // History-specific data
```

## Text History Types

### Empty (-2)
```
[Type] (Int32)            // TextHistoryType.Empty (-2)
[NoType] (Int32)          // TextHistoryType.NoType (-1)
[Has Culture String] (Bool32) // False
```

### NoType (-1)
```
[Type] (Int32)            // TextHistoryType.NoType (-1)
[Has Culture String] (Bool32) // True
[Culture Invariant String] (String) // The actual text content
```

### Base (0)
```
[Type] (Int32)            // TextHistoryType.Base (0)
[Namespace] (String)      // Text namespace
[Key] (String)           // Text key
[Source String] (String) // Original text
```

### NamedFormat
```
[Type] (Int32)            // TextHistoryType.NamedFormat
[Source Format] (FText)   // Base format text
[Argument Count] (Int32)  // Number of named arguments
[Arguments] (Array)       // Array of named arguments:
  [Key] (String)         // Argument name
  [Value] (FormatArgument) // Argument value
```

### OrderedFormat
```
[Type] (Int32)            // TextHistoryType.OrderedFormat
[Source Format] (FText)   // Base format text
[Argument Count] (Int32)  // Number of ordered arguments
[Arguments] (Array)       // Array of FormatArgument values
```

### ArgumentFormat
```
[Type] (Int32)            // TextHistoryType.ArgumentFormat
[Source Format] (FText)   // Base format text
[Argument Count] (Int32)  // Number of named arguments
[Arguments] (Array)       // Array of named arguments:
  [Key] (String)         // Argument name
  [Value] (FormatArgument) // Argument value
```

### AsNumber
```
[Type] (Int32)            // TextHistoryType.AsNumber
[Source Value] (FormatArgument) // Number to format
[Has Format Options] (Bool32)  // Whether format options are present
[Format Options] (Optional)    // NumberFormattingOptions if present
[Target Culture] (String)     // Culture for formatting
```

### AsPercent
```
[Type] (Int32)            // TextHistoryType.AsPercent
[Source Value] (FormatArgument) // Number to format as percentage
[Has Format Options] (Bool32)  // Whether format options are present
[Format Options] (Optional)    // NumberFormattingOptions if present
[Target Culture] (String)     // Culture for formatting
```

### AsCurrency
```
[Type] (Int32)            // TextHistoryType.AsCurrency
[Currency Code] (String)  // Currency identifier
[Source Value] (FormatArgument) // Amount to format
[Has Format Options] (Bool32)  // Whether format options are present
[Format Options] (Optional)    // NumberFormattingOptions if present
[Target Culture] (String)     // Culture for formatting
```

### AsDate
```
[Type] (Int32)            // TextHistoryType.AsDate
[LightWeightDateTime] (LightWeightDateTime)     // Date to format
[Date Style] (DateTimeStyle) // Style for date formatting
[Target Culture] (String) // Culture for formatting
```

### Transform
```
[Type] (Int32)            // TextHistoryType.Transform
[Source Text] (FText)     // Text to transform
[Transform Type] (TransformType) // Type of transformation
```

### StringTableEntry
```
[Type] (Int32)            // TextHistoryType.StringTableEntry
[Table ID] (FText)        // String table identifier
[Key] (String)           // Entry key in the table
```

## FormatArgument Structure
```
[Type] (Int32)           // FormatArgumentType
[Value] (Varies)         // Value based on type:
  - Int: Int32
  - UInt: UInt32
  - Float: Float32
  - Double: Float64
  - Text: FText
  - Gender: Int32
```

## Implementation Notes
- All integers are stored in little-endian format
- Strings are length-prefixed UTF-8 encoded
- The length field represents the total size of the text data section
- The array_index field is reserved for future use and is always 0
- Text properties support both raw text and structured FText data
- FText history types determine how the text is formatted and localized
- The flags field controls text formatting options
- Byte data is stored as-is without modification
- The format is compatible with Unreal Engine's native serialization format 