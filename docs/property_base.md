# Property Base and Factory Documentation

## Overview
This document describes the core components for handling GVAS properties: the abstract base class `PropertyTrait` and the factory class `PropertyFactory`. The factory is responsible for identifying and instantiating the correct property type based on strings read from the GVAS file.

## Class and Function Definitions

### `PropertyTrait` (ABC)
An abstract base class defining the fundamental interface required for all GVAS property types. Any class representing a GVAS property (like `IntProperty`, `StructProperty`, `ArrayProperty`, etc.) must inherit from this and implement its abstract methods.

```python
from abc import ABC, abstractmethod
from io import BinaryIO

class PropertyTrait(ABC):
    """
    Base trait/interface for Unreal specific property types
    """

    @abstractmethod
    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read property data from a binary stream"""
        pass

    @abstractmethod
    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write property data to a binary stream and return byte count written"""
        pass
```

-   **`read(stream, include_header)`**: Abstract method to deserialize the property's data from the `stream`. `include_header` indicates whether the standard GVAS property header should be expected and read first.
-   **`write(stream, include_header)`**: Abstract method to serialize the property's data to the `stream`. `include_header` indicates whether the standard GVAS property header should be written first. Returns the number of bytes written.

### `PropertyFactory`
A factory class responsible for creating instances of specific `PropertyTrait` subclasses based on a type name string.

```python
from typing import Optional
from io import BinaryIO
from gvas.properties.property_base import PropertyTrait

@dataclass
class PropertyFactory:

    @staticmethod
    def property_class_from_type(property_type: str) -> PropertyTrait:
        """Returns an uninitialized instance of the property class for the given type name."""
        # ... (implementation uses a large type_map dictionary)
        pass

    @classmethod
    def create_and_deserialize(
        cls,
        stream: BinaryIO,
        property_type: str,
        include_header: bool = True,
        suggested_length: Optional[int] = None,
    ) -> PropertyTrait:
        """Creates, deserializes, and returns a property instance from the stream."""
        # ... (implementation uses property_class_from_type and calls read())
        pass
```

-   **`property_class_from_type(property_type)`**: (Static Method) Takes a property type string (e.g., "IntProperty", "StructProperty") and returns an *uninitialized* instance of the corresponding `PropertyTrait` subclass. It uses an internal mapping (`type_map`) to find the correct class.
-   **`create_and_deserialize(cls, stream, property_type, include_header, suggested_length)`**: (Class Method) This is the primary method used for reading properties. It takes the `stream` and the `property_type` string, uses `property_class_from_type` to get an instance, and then calls the instance's `read` method to deserialize its data from the stream. It handles the `include_header` flag and passes `suggested_length` specifically for `ByteProperty` which needs it.

### FText History Type Classes (Definitions for Documentation)

These classes represent the different formats (`TextHistoryType`) an `FText` property can take. They are defined in `gvas.properties.text_property` but are included here as they are fundamental to understanding `TextProperty` deserialization handled via the factory.

```python
# NOTE: These are simplified definitions for docs purposes.
# See text_property.py for full implementation details.

@dataclass
class Empty: # HistoryType -2 or implicitly from NoType
    type: Literal["Empty"] = "Empty"
    # ... (No significant data serialized directly under this type)

@dataclass
class NoType: # HistoryType -1
    type: Literal["NoType"] = "NoType"
    culture_invariant_string: Optional[str] = None
    # ... read/write handle culture invariance support

@dataclass
class Base: # HistoryType 0
    type: Literal["Base"] = "Base"
    namespace: Optional[str] = None
    key: Optional[str] = None
    source_string: Optional[str] = None
    # ... read/write methods

@dataclass
class NamedFormat: # HistoryType 1
    type: Literal["NamedFormat"] = "NamedFormat"
    source_format: Optional["FText"] = None
    arguments: Optional[dict[str, "FormatArgument"]] = None
    # ... read/write methods

@dataclass
class OrderedFormat: # HistoryType 2
    type: Literal["OrderedFormat"] = "OrderedFormat"
    source_format: Optional["FText"] = None
    arguments: Optional[list["FormatArgument"]] = None
    # ... read/write methods

@dataclass
class ArgumentFormat: # HistoryType 3
    type: Literal["ArgumentFormat"] = "ArgumentFormat"
    source_format: Optional["FText"] = None
    arguments: Optional[dict[str, "FormatArgument"]] = None
    # ... read/write methods

@dataclass
class AsNumber: # HistoryType 4
    type: Literal["AsNumber"] = "AsNumber"
    source_value: Optional["FormatArgument"] = None
    format_options: Optional["NumberFormattingOptions"] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class AsPercent: # HistoryType 5
    type: Literal["AsPercent"] = "AsPercent"
    source_value: Optional["FormatArgument"] = None
    format_options: Optional["NumberFormattingOptions"] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class AsCurrency: # HistoryType 6
    type: Literal["AsCurrency"] = "AsCurrency"
    currency_code: Optional[str] = None
    source_value: Optional["FormatArgument"] = None
    format_options: Optional["NumberFormattingOptions"] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class AsDate: # HistoryType 7
    type: Literal["AsDate"] = "AsDate"
    date_time: Optional["LightWeightDateTime"] = None
    date_style: Optional["DateTimeStyle"] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class AsTime: # HistoryType 8
    type: Literal["AsTime"] = "AsTime"
    source_date_time: Optional["LightWeightDateTime"] = None
    time_style: Optional["DateTimeStyle"] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class AsDateTime: # HistoryType 9
    type: Literal["AsDateTime"] = "AsDateTime"
    source_date_time: Optional["LightWeightDateTime"] = None
    date_style: Optional["DateTimeStyle"] = None
    time_style: Optional["DateTimeStyle"] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None
    # ... read/write methods

@dataclass
class Transform: # HistoryType 10
    type: Literal["Transform"] = "Transform"
    source_text: Optional["FText"] = None
    transform_type: Optional["TransformType"] = None
    # ... read/write methods

@dataclass
class StringTableEntry: # HistoryType 11
    type: Literal["StringTableEntry"] = "StringTableEntry"
    table_id: Optional["FText"] = None
    key: Optional[str] = None
    # ... read/write methods
```

## Binary Format

This file defines base classes and factories, not specific binary formats itself. The binary format is determined by the concrete `PropertyTrait` subclasses (e.g., `IntProperty`, `StructProperty`).

-   `PropertyTrait` defines the `read`/`write` interface that subclasses use to interact with the binary stream.
-   `PropertyFactory.create_and_deserialize` orchestrates the reading process: it reads the necessary headers (if `include_header` is true), determines the property type, instantiates the correct class, and calls its `read` method.

## Implementation Notes

-   `PropertyTrait` serves as the cornerstone interface for all property types, ensuring a consistent API for reading and writing.
-   `PropertyFactory` centralizes the logic for mapping type names (strings read from the GVAS file) to the corresponding Python classes.
-   The `create_and_deserialize` method is the main entry point for reading properties dynamically based on their type encountered in the stream.
-   Error handling for unknown property types is included within the factory.
-   Context tracking (`ContextScopeTracker`, `gvas_utils.py`) is used internally to provide better error messages and handle deserialization hints.
-   The FText History Types listed represent the complex, varied ways localized and formatted text can be stored within a `TextProperty`.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 