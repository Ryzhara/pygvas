# GVAS Utilities Documentation

## Overview
This module provides common utility functions for working with the GVAS format, including functions for reading and writing various data types, handling strings, GUIDs, and standard headers. These utilities are essential for serialization and deserialization operations in the GVAS format.

## Constants

### ZERO_GUID
- A UUID instance representing a zero GUID (all bytes set to 0)
- Used as a default or null value for GUID fields

## Data Type Conversion Functions

### timespan_to_str(tspan: int) -> str
Converts a timespan value (in milliseconds) to a human-readable string format.

#### Parameters
- `tspan`: Integer representing timespan in milliseconds

#### Returns
- String in the format "HH:MM:SS.mmm" representing the timespan

#### Example
```python
timespan_to_str(3661000)  # Returns "1:01:01.000"
```

### datetime_to_str
```python
def datetime_to_str(dt: int) -> str
```
Converts a timestamp in ticks (0.1 microseconds since January 1, 0001) to a human-readable string.
- Handles conversion from Unreal Engine's FDateTime format
- Returns a formatted string in the format "DD/MM/YYYY HH:MM:SS.microseconds"
- Falls back to string representation of the input if conversion fails

## Atomic Data Reading/Writing

### read_atomic_data
```python
def read_atomic_data(
    stream: BinaryIO,
    format_str: str,
    width: int,
    assert_value=None,
    error_msg: str = None,
) -> int
```
Base function for reading atomic data types from a binary stream.
- Uses struct.unpack with the specified format string
- Validates the read value against an optional expected value
- Returns the unpacked value
- Raises DeserializeError if the read fails or validation fails

## Integer Reading/Writing Functions

### 8-bit Integers
- `read_int8`: Reads a signed 8-bit integer
- `write_int8`: Writes a signed 8-bit integer
- `read_uint8`: Reads an unsigned 8-bit integer
- `write_uint8`: Writes an unsigned 8-bit integer

### 16-bit Integers
- `read_int16`: Reads a signed 16-bit integer
- `write_int16`: Writes a signed 16-bit integer
- `read_uint16`: Reads an unsigned 16-bit integer
- `write_uint16`: Writes an unsigned 16-bit integer

### 32-bit Integers
- `read_int32`: Reads a signed 32-bit integer
- `write_int32`: Writes a signed 32-bit integer
- `read_uint32`: Reads an unsigned 32-bit integer
- `write_uint32`: Writes an unsigned 32-bit integer

### 64-bit Integers
- `read_int64`: Reads a signed 64-bit integer
- `write_int64`: Writes a signed 64-bit integer
- `read_uint64`: Reads an unsigned 64-bit integer
- `write_uint64`: Writes an unsigned 64-bit integer

## Floating Point Reading/Writing

### Single Precision
- `read_float`: Reads a 32-bit floating point number
- `write_float`: Writes a 32-bit floating point number

### Double Precision
- `read_double`: Reads a 64-bit floating point number
- `write_double`: Writes a 64-bit floating point number

## Boolean Reading/Writing

### Standard Boolean
- `read_bool`: Reads a single byte boolean
- `write_bool`: Writes a single byte boolean

### 32-bit Boolean
- `read_bool32bit`: Reads a 32-bit boolean (0 or 1)
- `write_bool32bit`: Writes a 32-bit boolean (0 or 1)

## String Handling

### read_string
```python
def read_string(stream: BinaryIO) -> str | None
```
Reads a string from a binary stream.
- Handles both UTF-8 and UTF-16 encoding
- Supports ASCII and non-ASCII strings
- Returns None for empty strings
- Validates string length and encoding
- Handles null terminators appropriately

### write_string
```python
def write_string(stream: BinaryIO, value: str) -> int
```
Writes a string to a binary stream.
- Automatically chooses between UTF-8 and UTF-16 encoding
- Handles None values as empty strings
- Adds appropriate null terminators
- Returns the number of bytes written

## GUID Handling

### GUID Conversion
- `guid_from_uint32x4`: Creates a GUID from four 32-bit integers
- `guid_to_str`: Converts a GUID to its string representation
- `str_to_guid`: Converts a string to a GUID

### GUID Reading/Writing
- `read_guid`: Reads a GUID from a binary stream
- `write_guid`: Writes a GUID to a binary stream

## Stream Operations

### peek
```python
def peek(stream, count: int) -> bytes
```
Reads bytes from a stream without advancing the position.
- Returns the specified number of bytes
- Restores the stream position after reading

### read_bytes
```python
def read_bytes(stream: BinaryIO, byte_count: int) -> bytes
```
Reads a specified number of bytes from a stream.
- Returns the bytes read
- Advances the stream position

### write_bytes
```python
def write_bytes(stream: BinaryIO, value_bytes: bytes) -> int
```
Writes bytes to a stream.
- Returns the number of bytes written
- Advances the stream position

## Header Handling

### read_standard_header
```python
def read_standard_header(
    stream: BinaryIO,
    *,
    assert_length: int = None,
    assert_array_index: int = 0,
    stream_readers: list[Callable[[BinaryIO], Any]] = None,
) -> list[Any]
```
Reads a standard GVAS header from a stream.
- Validates length and array index
- Supports custom data readers
- Handles null terminator
- Returns a list containing length, array index, and any additional data

### write_standard_header
```python
def write_standard_header(
    stream: BinaryIO,
    property_type,
    *,
    length: int = None,
    array_index: int = 0,
    data_to_write: list[Union[str, uuid.UUID]] = None,
) -> int
```
Writes a standard GVAS header to a stream.
- Writes property type, length, and array index
- Supports additional string and GUID data
- Adds null terminator
- Returns the number of bytes written

## Implementation Notes
- All numeric values are read/written in little-endian format
- String handling supports both ASCII and Unicode
- Error handling uses custom DeserializeError and SerializeError classes
- Stream operations maintain proper position tracking
- Header operations follow the GVAS format specification
- GUID operations support both binary and string representations 