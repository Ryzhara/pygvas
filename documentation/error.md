# Error Handling Documentation

## Overview
This module provides error handling classes for the GVAS format, specifically for deserialization and serialization operations. These error classes are designed to provide detailed information about errors that occur during the reading and writing of GVAS files.

## Error Classes

### DeserializeError
Exception class for errors that occur during deserialization (reading) of GVAS files.

#### Constructor
```python
def __init__(self, message: str, position: int = None)
```
- `message`: Error message describing the issue
- `position`: Optional byte position in the stream where the error occurred

#### Class Methods
- `invalid_header(message: str) -> "DeserializeError"`
  - Creates an error for invalid header data
  - Example: `DeserializeError.invalid_header("Invalid magic number")`

- `invalid_property(message: str, position: int) -> "DeserializeError"`
  - Creates an error for invalid property data
  - Example: `DeserializeError.invalid_property("Unknown property type", 0x100)`

- `invalid_value(value: int, position: int, message: str) -> "DeserializeError"`
  - Creates an error for invalid value data
  - Example: `DeserializeError.invalid_value(0xFF, 0x200, "Value out of range")`

- `missing_hint(property_type: str, property_path: str, position: int) -> "DeserializeError"`
  - Creates an error when a required type hint is missing
  - Example: `DeserializeError.missing_hint("StructProperty", "PlayerData.Stats", 0x300)`

- `invalid_value_size(length: int, param: int, position: int) -> "DeserializeError"`
  - Creates an error for invalid size values
  - Example: `DeserializeError.invalid_value_size(4, 8, 0x400)`

- `invalid_read_count(expected: int, found: int, position: int) -> "DeserializeError"`
  - Creates an error when the number of bytes read doesn't match expectations
  - Example: `DeserializeError.invalid_read_count(16, 12, 0x500)`

### SerializeError
Exception class for errors that occur during serialization (writing) of GVAS files.

#### Class Methods
- `invalid_value(message: str) -> "SerializeError"`
  - Creates an error for invalid values during serialization
  - Example: `SerializeError.invalid_value("Invalid enum value")`

## Error Handling Patterns

### Position Tracking
- Both error classes support position tracking to help identify where in the file an error occurred
- Positions are typically byte offsets from the start of the file
- When a position is provided, it's automatically included in the error message

### Error Context
- Error messages are designed to be descriptive and include relevant context
- For deserialization errors, the position is often crucial for debugging
- Serialization errors focus on the invalid value or condition that caused the error

### Usage Examples

#### Deserialization Error
```python
try:
    # Attempt to read data
    data = read_from_stream(stream)
except DeserializeError as e:
    print(f"Error reading data: {e}")
    if e.position is not None:
        print(f"Error occurred at position: {e.position}")
```

#### Serialization Error
```python
try:
    # Attempt to write data
    write_to_stream(stream, data)
except SerializeError as e:
    print(f"Error writing data: {e}")
```

## Implementation Notes
- Errors are designed to be caught and handled at appropriate levels
- Position information is crucial for debugging deserialization issues
- Error messages should be descriptive and include relevant context
- The error system is designed to be compatible with Python's exception handling
- Error classes extend from standard Python exception classes for compatibility 