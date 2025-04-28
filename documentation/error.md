# Error Types Documentation

## Overview
This document describes the custom exception types used by the `pygvas` library to report errors during GVAS file processing.

## Class and Function Definitions

### `DeserializeError` (inherits `Exception`)
Represents an error that occurs during the deserialization (reading) of a GVAS file or its components.

```python
class DeserializeError(Exception):
    """Error that occurs during deserialization"""

    def __init__(self, message: str, position: int = None):
        # ... (adds position to message if provided)

    @classmethod
    def invalid_header(cls, message: str) -> "DeserializeError":
        # Creates error for header issues
        ...

    @classmethod
    def invalid_property(cls, message: str, position: int) -> "DeserializeError":
        # Creates error for property structure issues
        ...

    @classmethod
    def invalid_value(cls, value: int, position: int, message: str) -> "DeserializeError":
        # Creates error for unexpected values read
        ...

    @classmethod
    def missing_hint(cls, property_type: str, property_path: str, position: int) -> "DeserializeError":
        # Creates error when a required deserialization hint is missing
        ...

    @classmethod
    def invalid_hint(cls, hint_type: str, property_path: str, position: int) -> "DeserializeError":
        # Creates error when an unknown hint type is encountered
        ...

    @classmethod
    def invalid_value_size(cls, length: int, param: int, position: int):
        # Creates error when read size doesn't match expected size
        ...

    @classmethod
    def invalid_read_count(cls, expected: int, found: int, position: int):
        # Creates error for mismatches in expected vs actual bytes read (e.g., by ByteCountValidator)
        ...
```

-   Includes the stream `position` in the error message when available.
-   Provides several class methods (`invalid_header`, `invalid_property`, etc.) as constructors for specific common error scenarios.

### `SerializeError` (inherits `BaseException`)
Represents an error that occurs during the serialization (writing) of GVAS data.

```python
class SerializeError(BaseException):
    """Error that occurs during serialization"""

    @classmethod
    def invalid_value(cls, message: str) -> "SerializeError":
        """Create an invalid value error"""
        # ... (creates error for invalid values during serialization)
        ...
```

-   Provides a class method `invalid_value` for creating serialization errors related to invalid data.

## Binary Format

These are exception classes and do not have a direct binary format.

## Examples

```python
# Example usage (conceptual)
try:
    # ... attempt to read GVAS data ...
    if some_condition_fails:
        raise DeserializeError.invalid_property("Missing terminator", stream.tell())
except DeserializeError as e:
    print(f"Failed to deserialize: {e}")

try:
    # ... attempt to write GVAS data ...
    if some_value_is_bad:
        raise SerializeError.invalid_value("Cannot serialize negative count")
except SerializeError as e:
    print(f"Failed to serialize: {e}")
```

## Implementation Notes
-   These classes provide more specific error types than standard Python exceptions, aiding in debugging GVAS processing issues.
-   `DeserializeError` often includes the stream position where the error was detected.
-   The factory class methods simplify the creation of common error types.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 