# Text Property Documentation

## Overview
This document describes the `TextProperty` and its associated structures within the GVAS format. `TextProperty` represents Unreal Engine's `FText`, a complex type used for localized and formatted text. It involves various "history types" that determine how the text is constructed and formatted.

## Class and Function Definitions

### Enums and Helpers

#### `IntEnumHelper`
Base class providing helper methods for reading and writing `IntEnum` values from/to a byte stream as `Int8`.

#### `DateTimeStyle(IntEnumHelper)`
Enum defining styles for formatting dates and times (e.g., `Short`, `Medium`, `Long`, `Full`).

#### `TransformType(IntEnumHelper)`
Enum defining text transformations (`ToLower`, `ToUpper`).

#### `RoundingMode(IntEnumHelper)`
Enum defining various modes for rounding numbers (e.g., `HalfToEven`, `FromZero`, `ToNegativeInfinity`).

#### `FormatArgumentType(IntEnumHelper)`
Enum defining the types of arguments that can be used in formatted text (e.g., `Int`, `Float`, `Text`). This is the type read/written from the stream.

#### `FormatArgumentValue(IntEnumHelper)`
Enum used *internally* to represent argument values, accommodating potential 64-bit integers based on engine version. There's an impedance mismatch handled during read/write between this and `FormatArgumentType`.

#### `TextHistoryType(IntEnumHelper)`
Enum defining the different ways an `FText` object can be represented or constructed (e.g., `Base`, `NamedFormat`, `AsNumber`, `StringTableEntry`). This determines the structure of the data following the `FText` flags.

### Core Data Structures

#### `TextPropertyHelper`
Base class providing static methods to check engine version support for features like 64-bit arguments (`supports_64bit`) and culture invariance (`supports_culture_invariance`). Many history type classes inherit from this.

#### `NumberFormattingOptions`
Stores options for formatting numbers (e.g., sign display, grouping, rounding mode, digit counts).

```python
@dataclass
class NumberFormattingOptions:
    always_include_sign: bool = False
    use_grouping: bool = False
    rounding_mode: str = RoundingMode.HalfToEven.name
    minimum_integral_digits: int = 1
    maximum_integral_digits: int = 324
    minimum_fractional_digits: int = 0
    maximum_fractional_digits: int = 3

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `LightWeightDateTime`
Represents a date and time value using ticks (UInt64).

```python
@dataclass
class LightWeightDateTime:
    ticks: int = 0
    comment: str = None # Not serialized, just for debugging

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO): ... # Returns bytes_written (int)
```

#### `FormatArgument` (inherits `TextPropertyHelper`)
Represents a single argument used in formatted text. It reads a `FormatArgumentType` but stores its value based on `FormatArgumentValue`, handling potential 32/64-bit integer differences.

```python
@dataclass
class FormatArgument(TextPropertyHelper):
    type: str = FormatArgumentValue.Unknown.name
    value: Optional[Union[int, float, "FText"]] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `FText`
Represents the core `FText` structure, containing flags and a specific history object.

```python
UNREAL_ENGINE_TEXT_PROPERTY_TYPES = Annotated[
    Union[
        "Empty", "NoType", "Base", "NamedFormat", "OrderedFormat",
        "ArgumentFormat", "AsNumber", "AsPercent", "AsCurrency", "AsDate",
        "AsTime", "AsDateTime", "Transform", "StringTableEntry",
    ],
    Discriminator("type"),
]

@dataclass
class FText:
    flags: int = 0
    history: Optional[UNREAL_ENGINE_TEXT_PROPERTY_TYPES] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO): ... # Returns bytes_written (int)
```

### Text History Types
These classes represent the different structures determined by `TextHistoryType`.

#### `Empty` (inherits `TextPropertyHelper`)
Represents an empty or non-existent text entry, especially when culture invariance is supported but no invariant string is present.

```python
@dataclass
class Empty(TextPropertyHelper):
    type: Literal[TextHistoryType.Empty.name] = TextHistoryType.Empty.name

    # Note: write() outputs TextHistoryType.NoType marker based on engine version
    def write(self, stream: BinaryIO) -> int: ...
```

#### `NoType` (inherits `TextPropertyHelper`)
Represents a culture-invariant string when supported by the engine version.

```python
@dataclass
class NoType(TextPropertyHelper):
    type: Literal[TextHistoryType.NoType.name] = TextHistoryType.NoType.name
    culture_invariant_string: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ... # May return Empty() instance
    def write(self, stream: BinaryIO): ...
```

#### `Base`
Represents basic localized text with a namespace, key, and source string.

```python
@dataclass
class Base:
    type: Literal[TextHistoryType.Base.name] = TextHistoryType.Base.name
    namespace: Optional[str] = None
    key: Optional[str] = None
    source_string: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `NamedFormat`
Represents text formatted with named arguments (like Python's f-strings or `.format`).

```python
@dataclass
class NamedFormat:
    type: Literal[TextHistoryType.NamedFormat.name] = TextHistoryType.NamedFormat.name
    source_format: Optional[FText] = None
    arguments: Optional[dict[str, FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `OrderedFormat`
Represents text formatted with ordered arguments (like C's `printf`).

```python
@dataclass
class OrderedFormat:
    type: Literal[TextHistoryType.OrderedFormat.name] = TextHistoryType.OrderedFormat.name
    source_format: Optional[FText] = None
    arguments: Optional[list[FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `ArgumentFormat`
Similar to `NamedFormat`, used for formatting arguments within text.

```python
@dataclass
class ArgumentFormat:
    type: Literal[TextHistoryType.ArgumentFormat.name] = TextHistoryType.ArgumentFormat.name
    source_format: Optional[FText] = None
    arguments: Optional[dict[str, FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsNumber`
Represents text generated by formatting a numerical value.

```python
@dataclass
class AsNumber:
    type: Literal[TextHistoryType.AsNumber.name] = TextHistoryType.AsNumber.name
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsPercent`
Represents text generated by formatting a numerical value as a percentage.

```python
@dataclass
class AsPercent:
    type: Literal[TextHistoryType.AsPercent.name] = TextHistoryType.AsPercent.name
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsCurrency`
Represents text generated by formatting a numerical value as currency.

```python
@dataclass
class AsCurrency:
    type: Literal[TextHistoryType.AsCurrency.name] = TextHistoryType.AsCurrency.name
    currency_code: Optional[str] = None
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsDate`
Represents text generated by formatting a date/time value as a date.

```python
@dataclass
class AsDate:
    type: Literal[TextHistoryType.AsDate.name] = TextHistoryType.AsDate.name
    date_time: Optional[LightWeightDateTime] = None
    date_style: Optional[DateTimeStyle] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsTime`
Represents text generated by formatting a date/time value as a time.

```python
@dataclass
class AsTime:
    type: Literal[TextHistoryType.AsTime.name] = TextHistoryType.AsTime.name
    source_date_time: Optional[LightWeightDateTime] = None
    time_style: Optional[DateTimeStyle] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `AsDateTime`
Represents text generated by formatting a date/time value as both date and time.

```python
@dataclass
class AsDateTime:
    type: Literal[TextHistoryType.AsDateTime.name] = TextHistoryType.AsDateTime.name
    source_date_time: Optional[LightWeightDateTime] = None
    date_style: Optional[DateTimeStyle] = None
    time_style: Optional[DateTimeStyle] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `Transform`
Represents text generated by applying a transformation (ToUpper, ToLower) to another `FText`.

```python
@dataclass
class Transform:
    type: Literal[TextHistoryType.Transform.name] = TextHistoryType.Transform.name
    source_text: Optional[FText] = None
    transform_type: Optional[TransformType] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

#### `StringTableEntry`
Represents text sourced from a String Table asset using a table ID and key.

```python
@dataclass
class StringTableEntry:
    type: Literal[TextHistoryType.StringTableEntry.name] = TextHistoryType.StringTableEntry.name
    table_id: Optional[FText] = None # Yes, the Table ID can itself be an FText
    key: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self: ...
    def write(self, stream: BinaryIO) -> int: ...
```

### Factory and Main Property Class

#### `FTextHistoryFactory`
Class with a static `read` method that reads the `TextHistoryType` byte and then reads and returns the corresponding history type object.

```python
@dataclass
class FTextHistoryFactory:
    @classmethod
    def read(cls, stream: BinaryIO) -> UNREAL_ENGINE_TEXT_PROPERTY_TYPES: ...
```

#### `TextProperty` (inherits `PropertyTrait`)
The main GVAS property class for `FText`.

```python
@dataclass
class TextProperty(PropertyTrait):
    """A property that holds FText data"""

    type: Literal["TextProperty"] = "TextProperty"
    flags: int = 0
    history: Optional[UNREAL_ENGINE_TEXT_PROPERTY_TYPES] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**. Strings are standard length-prefixed strings (`read_string`/`write_string`). Enums are generally written as `Int8`.

### `TextProperty`
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "TextProperty"
    *   Length (Int64): Size in bytes of the `FText` data.
    *   Padding (UInt8): Typically 0.
2.  `FText` Data (See below).

```
[Standard Header (Optional)]
[FText Data]
```

### `FText`
1.  Flags (UInt32): Bitmask controlling text properties (e.g., localization, culture invariance).
2.  History Type (`Int8`): A value from `TextHistoryType` enum determining the subsequent structure.
3.  History Data: The data corresponding to the `History Type` read in step 2 (See specific history types below).

```
[Flags: UInt32]
[History Type: Int8]
[History Data]
```

### `FormatArgument`
1.  Argument Type (`Int8`): Value from `FormatArgumentType`.
2.  Argument Value: The actual value, type and size depend on `Argument Type` and engine version (potential 64-bit ints).
    *   `Int`: `Int32` or `Int64`
    *   `UInt`: `UInt32` or `UInt64`
    *   `Float`: `Float` (4 bytes)
    *   `Double`: `Double` (8 bytes)
    *   `Text`: `FText` Data (recursive)

```
[Argument Type: Int8]
[Argument Value: (variable type/size)]
```

### History Type Details (Following `History Type: Int8`)

*   **`NoType` / `Empty` (-1/-2):**
    *   has_culture_invariant_string (`Bool32`): Only if `supports_culture_invariance()` is true. (This boolean is read but not stored directly in `NoType`)
    *   culture_invariant_string (`String`): Only if previous bool is true.
*   **`Base` (0):**
    *   namespace (`String`)
    *   key (`String`)
    *   source_string (`String`)
*   **`NamedFormat` (1):**
    *   source_format (`FText`)
    *   Argument Count (`Int32`)
    *   arguments (Array): `Argument Count` entries of:
        *   key (`String`)
        *   value (`FormatArgument`)
*   **`OrderedFormat` (2):**
    *   source_format (`FText`)
    *   Argument Count (`Int32`)
    *   arguments (Array): `Argument Count` entries of `FormatArgument`.
*   **`ArgumentFormat` (3):** (Identical structure to `NamedFormat`)
    *   source_format (`FText`)
    *   Argument Count (`Int32`)
    *   arguments (Array): `Argument Count` entries of:
        *   key (`String`)
        *   value (`FormatArgument`)
*   **`AsNumber` (4):**
    *   source_value (`FormatArgument`)
    *   Has Format Options (`Bool32`): (Read but not stored directly)
    *   format_options (`NumberFormattingOptions`): Only if previous bool is true.
    *   target_culture (`String`)
*   **`AsPercent` (5):** (Identical structure to `AsNumber`)
    *   source_value (`FormatArgument`)
    *   Has Format Options (`Bool32`): (Read but not stored directly)
    *   format_options (`NumberFormattingOptions`): Only if previous bool is true.
    *   target_culture (`String`)
*   **`AsCurrency` (6):**
    *   currency_code (`String`)
    *   source_value (`FormatArgument`)
    *   Has Format Options (`Bool32`): (Read but not stored directly)
    *   format_options (`NumberFormattingOptions`): Only if previous bool is true.
    *   target_culture (`String`)
*   **`AsDate` (7):**
    *   date_time (`LightWeightDateTime` -> `UInt64` Ticks)
    *   date_style (`Int8`)
    *   target_culture (`String`)
*   **`AsTime` (8):**
    *   source_date_time (`LightWeightDateTime` -> `UInt64` Ticks)
    *   time_style (`Int8`)
    *   time_zone (`String`)
    *   target_culture (`String`)
*   **`AsDateTime` (9):**
    *   source_date_time (`LightWeightDateTime` -> `UInt64` Ticks)
    *   date_style (`Int8`)
    *   time_style (`Int8`)
    *   time_zone (`String`)
    *   target_culture (`String`)
*   **`Transform` (10):**
    *   source_text (`FText`)
    *   transform_type (`Int8`)
*   **`StringTableEntry` (11):**
    *   table_id (`FText`)
    *   key (`String`)

### `NumberFormattingOptions`
1.  always_include_sign (`Bool32`)
2.  use_grouping (`Bool32`)
3.  rounding_mode (`Int8`)
4.  minimum_integral_digits (`Int32`)
5.  maximum_integral_digits (`Int32`)
6.  minimum_fractional_digits (`Int32`)
7.  maximum_fractional_digits (`Int32`)

## Examples

### Example: `Base` History Type
`FText` with flags=0, history type=`Base`, namespace="", key="ABC", source="Hello"

```
# FText
00 00 00 00  # Flags = 0
00           # History Type = Base (0)

# Base History Data
# Namespace: "" (empty string)
00 00 00 00  # Length = 0
00           # Null terminator

# Key: "ABC" (UTF-8)
04 00 00 00  # Length = 4 (3 chars + null)
41 42 43     # "ABC"
00           # Null terminator

# Source String: "Hello" (UTF-8)
06 00 00 00  # Length = 6 (5 chars + null)
48 65 6C 6C 6F # "Hello"
00           # Null terminator
```

### Example: `AsNumber` History Type (Simplified, pre-64bit support)
`FText` with flags=0, history type=`AsNumber`, source value=int 123, no format options, culture="en"

```
# FText
00 00 00 00  # Flags = 0
04           # History Type = AsNumber (4)

# AsNumber History Data
# Source Value (FormatArgument: Int)
00           # Argument Type = Int (0)
7B 00 00 00  # Argument Value = 123 (Int32)

# Has Format Options
00 00 00 00  # False (Bool32)

# Target Culture: "en" (UTF-8)
03 00 00 00  # Length = 3 (2 chars + null)
65 6E        # "en"
00           # Null terminator
```

## Implementation Notes
- The complexity arises from the numerous history types and the conditional logic based on engine versions (`supports_64bit()`, `supports_culture_invariance()`).
- The `FTextHistoryFactory` is crucial for dispatching reads to the correct history type class.
- Pay close attention to the impedance mismatch between `FormatArgumentType` (serialized) and `FormatArgumentValue` (internal representation for 64-bit support).
- `FText` can be recursive (e.g., in `NamedFormat`, `OrderedFormat`, `Transform`, `StringTableEntry`).

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 