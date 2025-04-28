# GVAS Utilities Documentation

## Overview
This document describes the utility functions and helper classes provided in `gvas_utils.py`. These utilities handle low-level binary read/write operations, context tracking during deserialization, validation, and common data conversions required for processing GVAS files.

## Class and Function Definitions

### Constants

#### `MagicConstants`
A class holding important constant values:
- `ZERO_GUID`: A `uuid.UUID` instance representing all zeros.
- `GVAS_MAGIC`: The byte sequence `b"GVAS"` expected at the beginning of GVAS files.
- `PLZ_MAGIC`: The byte sequence `b"PlZ"` associated with Palworld files.
- `MIN_STRING_LENGTH`: The (negated) maximum number of bytes for UTF-16 strings.
- `MAX_STRING_LENGTH`: The maximum number of bytes for UTF-8 strings.

### Helper Classes

#### `UnitTestGlobals`
A class to manage/suppress verbose messages during unit testing.

```python
class UnitTestGlobals:
    _unit_tests_running: bool = False

    @classmethod
    def set_inside_unit_tests(cls) -> None: ...
    @classmethod
    def inside_unit_tests(cls) -> bool: ...
```

#### `ContextScopeTracker`
A class (used statically and as a context manager) to track the hierarchical structure being processed during deserialization (e.g., "SaveGameData.MyCharacter.Inventory.Item0.Name"). It also manages deserialization hints needed for ambiguous types (like structs within arrays).

```python
class ContextScopeTracker:
    _context_stack: list[str] = []
    _deserialization_hints: dict[str, Union[str, dict[str, Any]]] = {}
    _hint_context: dict[str, Any] = {}

    # --- Static Methods ---
    @classmethod
    def push_context_step(cls, step: str) -> None: ...
    @classmethod
    def pop_context_step(cls) -> None: ...
    @classmethod
    def get_context_path(cls) -> str: ...
    @classmethod
    def set_deserialization_hints(cls, hints: dict) -> None: ...
    @classmethod
    def get_hint_for_context(cls) -> Union[str, dict, None]: ...
    @classmethod
    def set_hint_context(cls, context: dict) -> None: ...
    @classmethod
    def get_hint_context(cls) -> dict: ...

    # --- Context Manager Implementation ---
    def __init__(self, context: str): ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...
```
- Used via `with ContextScopeTracker("MyProperty") as tracker:`.
- `set_deserialization_hints` is called by the user to provide necessary type information for ambiguous structures.
- `get_hint_for_context` is used internally (e.g., by `StructProperty`) to retrieve hints.

#### `ByteCountValidator`
A context manager used to verify that a specific number of bytes were read within its scope, raising a `DeserializeError` if the count mismatches.

```python
class ByteCountValidator:
    def __init__(self, stream: BinaryIO, expected_byte_count: int, do_validation: bool):
        # ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...
```
- Used via `with ByteCountValidator(stream, length, validate) as validator:`.
- Compares `stream.tell()` before and after the `with` block.

### Read/Write Functions for Primitive Types
These functions handle reading and writing specific data types from/to a `BinaryIO` stream using Python's `struct` module with little-endian format (`<`). Many include optional `assert_value` and `error_msg` parameters for validation during reads.

- `read_int8(stream, ...)` / `write_int8(stream, value)`: Signed 8-bit integer.
- `read_uint8(stream, ...)` / `write_uint8(stream, value)`: Unsigned 8-bit integer.
- `read_bool(stream, ...)` / `write_bool(stream, value)`: Boolean (1 byte, 0x00 or 0x01).
- `read_bool32bit(stream)` / `write_bool32bit(stream, value)`: Boolean stored as a 32-bit integer (0 or 1).
- `read_int16(stream, ...)` / `write_int16(stream, value)`: Signed 16-bit integer.
- `read_uint16(stream, ...)` / `write_uint16(stream, value)`: Unsigned 16-bit integer.
- `read_int32(stream, ...)` / `write_int32(stream, value)`: Signed 32-bit integer.
- `read_uint32(stream, ...)` / `write_uint32(stream, value)`: Unsigned 32-bit integer.
- `read_int64(stream, ...)` / `write_int64(stream, value)`: Signed 64-bit integer.
- `read_uint64(stream, ...)` / `write_uint64(stream, value)`: Unsigned 64-bit integer.
- `read_float(stream, ...)` / `write_float(stream, value)`: 32-bit float.
- `read_double(stream, ...)` / `write_double(stream, value)`: 64-bit float (double).
- `read_bytes(stream, byte_count)` / `write_bytes(stream, value_bytes)`: Raw byte sequences.
- `read_guid(stream)` / `write_guid(stream, guid)`: 16-byte GUID (accepts/returns `uuid.UUID` or string).
- `read_string(stream)` / `write_string(stream, value)`: Length-prefixed string (handles UTF-8/UTF-16 encoding based on sign of length).

### Header Read/Write Functions

-   **`read_standard_header(stream, *, assert_length, assert_array_index, stream_readers)`**
    -   Reads the common header structure preceding many property types.
    -   Always reads Length (UInt32) and Array Index (UInt32).
    -   Optionally reads additional fields using functions provided in `stream_readers` (e.g., type names for MapProperty).
    -   Always reads and discards a final null byte terminator (UInt8).
    -   Returns a list containing `[length, optional_array_index, optional_reader_results...]`.
    -   Can assert specific values for length and array index.

-   **`write_standard_header(stream, property_type, *, length, array_index, data_to_write)`**
    -   Writes the common header structure.
    -   Always writes Property Type Name (String), Length (UInt32), and Array Index (UInt32).
    -   Optionally writes additional data (strings or GUIDs) provided in `data_to_write`.
    -   Always writes a final null byte terminator (UInt8).
    -   Returns the total number of bytes written for the header.

### Miscellaneous Utilities

- `peek(stream, count)`: Reads `count` bytes without advancing the stream position.
- `peek_valid_string(stream: BinaryIO)`: Used internally to detect that guessing custom struct will fail.
- `datetime_to_str(ticks)`: Converts UInt64 ticks (from `DateTimeStruct`) to a human-readable string (approximate).
- `timespan_to_str(ticks)`: Converts UInt64 ticks (from `TimespanStruct`) to a human-readable timedelta string.
- `guid_to_str(guid_uuid)` / `str_to_guid(guid_str)`: Convert between `uuid.UUID` objects and uppercase string representations.
- `guid_from_uint32x4(...)`: Creates a `uuid.UUID` from four UInt32 values (used for custom version GUIDs).
- `read_atomic_data(stream, format_str, width, ...)`: Internal helper for reading fixed-width primitive types using `struct.unpack`.

## Binary Format

This module defines the functions that implement the binary formats for primitive types and standard headers.

### String Format (`read_string`/`write_string`)
1.  Length (Int32): Number of characters + 1 (for terminator). Negative if UTF-16, positive if UTF-8.
2.  String Content (Bytes): `abs(Length)-1` characters encoded in UTF-8 or UTF-16LE.
3.  Terminator (UInt8 or UInt16): Single null byte (0x00) for UTF-8, or two null bytes (0x0000) for UTF-16LE.

### Standard Header Format (`read_standard_header`/`write_standard_header`)
Structure written/read when `include_header=True` for most properties:
1.  Property Type Name (`String`): e.g., "IntProperty"
2.  Length (UInt32): Byte size of the property data *following* this header.
3.  Array Index (UInt32): Index if the property is part of an array (usually 0).
4.  Optional Data Fields (`Any...`): Depending on the property type (e.g., Key/Value types for MapProperty), additional fields (like Strings or GUIDs) might be read/written here.
5.  Terminator (UInt8): Always 0x00.

### Primitive Types
Refer to Python's `struct` module documentation for standard sizes and formats (e.g., `<i` for little-endian signed 32-bit int, `?` for bool, `<f` for float, `<d` for double).

## Implementation Notes

-   Provides the fundamental building blocks for reading and writing GVAS data structures.
-   Uses Python's `struct` module for efficient packing/unpacking of binary data.
-   Handles little-endian byte order consistently.
-   String serialization handles both ASCII/UTF-8 and UTF-16LE based on content and length prefix sign.
-   `ContextScopeTracker` is essential for debugging and handling complex deserialization scenarios requiring hints.
-   `ByteCountValidator` helps ensure data integrity by verifying expected data lengths.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 