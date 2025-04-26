# Array Property Documentation

## Overview
This document describes the `ArrayProperty` class within the GVAS format. This property type stores an ordered sequence (list) of elements, all of which must be of the same GVAS property type. It handles serialization differently depending on whether the elements are simple ("bare") types or complex types like `StructProperty`.

## Class and Function Definitions

### `ArrayProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding an ordered list of elements of the same type.

```python
import uuid
from typing import ClassVar, Callable, Any
from gvas.properties.aggregator_properties import UNREAL_ENGINE_PROPERTIES

@dataclass
class ArrayProperty(PropertyTrait):
    # Class variables defining optimized readers/writers for simple types
    bare_readers: ClassVar[dict[str, Callable[[BinaryIO], Any]]] = { ... }
    bare_writers: ClassVar[dict[str, Callable[[BinaryIO, Any], int]]] = { ... }

    type: Literal["ArrayProperty"] = "ArrayProperty"
    field_name: Optional[str] = None # Only used for Array<StructProperty>
    type_name: Optional[str] = None  # Only used for Array<StructProperty>
    property_type: Optional[str] = None # GVAS type name string for elements
    guid: Optional[uuid.UUID] = None  # Only used for Array<StructProperty>
    values: Union[
        str, # Hex string if property_type is ByteProperty and values are bytes
        bytes, # Raw bytes if property_type is ByteProperty
        list[
            Union[
                UNREAL_ENGINE_PROPERTIES, # Property instances
                # Bare types allowed by bare_readers/writers
                str, int, float, bool, bytes, uuid.UUID, None,
            ],
        ],
    ] = None

    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID): ...

    @field_serializer("values")
    def serialize_values(self, values: [str, bytes, list, PropertyTrait, StandardStructTrait], field_info): ...

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def read_body(self, stream: BinaryIO, length: int) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**.

### `ArrayProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Required, `include_header` must be true for reading):
    *   Property Type Name (`String`): "ArrayProperty"
    *   Length (Int64): Size in bytes of the array data body (Step 2).
    *   Element Type Name (`String`): The GVAS property type name for all elements in the array (e.g., "IntProperty", "StructProperty", "NameProperty").
    *   Padding (UInt8): Typically 0.
2.  Array Data Body: The format depends heavily on the `Element Type Name`.
    *   Element Count (UInt32): The number of elements in the array.
    *   Element Data: The sequence of element data.

        *   **If Element Type is `StructProperty`:**
            *   Field Name (`String`): The name associated with this array (often the name of the field holding the array).
            *   Member Type Name (`String`): Must match the `Element Type Name` from the main header ("StructProperty").
            *   Struct Header (Embedded Standard Header):
                *   Property Type Name (`String`): Again, "StructProperty".
                *   Struct Body Length (Int64): Total size in bytes of *all* serialized struct bodies combined.
                *   Struct Type Name (`String`): The specific type of struct within the array (e.g., "Vector", "MyCustomStruct").
                *   Struct GUID (16 Bytes): GUID associated with the struct type.
                *   Padding (UInt8): Typically 0.
            *   Struct Bodies (Concatenated): `Element Count` instances of the serialized struct data, concatenated together. **Crucially, these structs are written *without* their individual `StructProperty` headers**. For standard structs, it's just their raw binary data (e.g., 3 floats for a Vector). For custom structs, it's the sequence of their internal properties terminated by "None".

        *   **If Element Type is `ByteProperty` AND the data represents a raw byte sequence:**
            *   Raw Bytes: The `Element Count` bytes are read/written directly as a single block.

        *   **If Element Type is a "Bare" Type (Int32, Float, Bool, Name, Str, Enum, Guid, etc.):**
            *   Bare Values (Array): `Element Count` instances of the bare value, read/written using optimized functions (e.g., `read_int32`, `write_string`) without any property headers.

        *   **If Element Type is any other complex Property Type (e.g., `ObjectProperty`, `TextProperty`, etc.):**
            *   Property Values (Array): `Element Count` instances of the property data, read/written **without** their individual headers (`include_header=False`).

```
[Standard Header]
  [Property Type Name: String = "ArrayProperty"]
  [Length: Int64]
  [Element Type Name: String]
  [Padding: UInt8]

[Array Data Body]
  [Element Count: UInt32]

  # ---- Element Data Starts ----

  # IF Element Type == "StructProperty":
  [Field Name: String]
  [Member Type Name: String = "StructProperty"]
  [Struct Header]
    [Property Type Name: String = "StructProperty"]
    [Struct Body Length: Int64]
    [Struct Type Name: String]
    [Struct GUID: 16 Bytes]
    [Padding: UInt8]
  [Struct Body 1 (No Header)]
  [Struct Body 2 (No Header)]
  ...
  [Struct Body N (No Header)]

  # IF Element Type == "ByteProperty" (Raw Bytes):
  [Raw Bytes (Element Count bytes)]

  # IF Element Type is Bare (e.g., "Int32Property"):
  [Bare Value 1]
  [Bare Value 2]
  ...
  [Bare Value N]

  # IF Element Type is Complex (e.g., "ObjectProperty"):
  [Property Data 1 (No Header)]
  [Property Data 2 (No Header)]
  ...
  [Property Data N (No Header)]
```

## Examples

### Example: Array of Bare Type (`Int32Property`)
Values: `[10, 20, 30]`

```
# Header
# Property Type Name: "ArrayProperty" (UTF-8)
0E 00 00 00 41 72 72 61 79 50 72 6F 70 65 72 74 79 00

# Length: (Calculated size of array body: Count(4) + 3*Int32(4) = 16 bytes)
10 00 00 00 00 00 00 00 # Length = 16

# Element Type Name: "Int32Property" (UTF-8)
0E 00 00 00 49 6E 74 33 32 50 72 6F 70 65 72 74 79 00

# Padding
00

# -- Array Data Body Starts --
# Element Count
03 00 00 00          # Count = 3

# Element Data (Bare Int32 values)
0A 00 00 00          # Value = 10
14 00 00 00          # Value = 20
1E 00 00 00          # Value = 30
```

### Example: Array of Struct Type (`VectorStruct`, LWC Disabled)
Values: `[Vector(x=1,y=2,z=3), Vector(x=4,y=5,z=6)]`, Field Name: "Positions"

```
# Header
# Property Type Name: "ArrayProperty" (UTF-8)
0E 00 00 00 41 72 72 61 79 50 72 6F 70 65 72 74 79 00

# Length: (Calculated size of array body)
#   Count(4) + FieldName("Positions" 10B+null=11) +
#   MemberType("StructProperty" 15B+null=16) +
#   StructHeader(Name(16B)+Len(8B)+TypeName(7B+null=8)+GUID(16B)+Pad(1B) = 49) +
#   StructBody1(Vector 12B) + StructBody2(Vector 12B)
#   Total Body = 4 + 11 + 16 + 49 + 12 + 12 = 104 bytes
68 00 00 00 00 00 00 00 # Length = 104 (0x68)

# Element Type Name: "StructProperty" (UTF-8)
0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00

# Padding
00

# -- Array Data Body Starts --
# Element Count
02 00 00 00          # Count = 2

# Field Name: "Positions" (UTF-8)
0A 00 00 00 50 6F 73 69 74 69 6F 6E 73 00

# Member Type Name: "StructProperty" (UTF-8)
0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00

# Struct Header (Embedded)
#   Property Type Name: "StructProperty" (UTF-8)
0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00
#   Struct Body Length: (2 vectors * 12 bytes/vector = 24 bytes)
18 00 00 00 00 00 00 00 # Length = 24
#   Struct Type Name: "Vector" (UTF-8)
07 00 00 00 56 65 63 74 6F 72 00
#   Struct GUID: (Zero GUID)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#   Padding:
00

# Struct Body 1 (Vector(1,2,3) - No Header)
00 00 80 3F # X=1.0f
00 00 00 40 # Y=2.0f
00 00 40 40 # Z=3.0f

# Struct Body 2 (Vector(4,5,6) - No Header)
00 00 80 40 # X=4.0f
00 00 A0 40 # Y=5.0f
00 00 C0 40 # Z=6.0f
```

## Implementation Notes
- `ArrayProperty` cannot be nested directly within other container types (`SetProperty`, `MapProperty`) for reading.
- The serialization format varies significantly based on the `property_type` specified in the header.
- **Bare Types**: Simple types like integers, floats, bools, strings, names, enums, GUIDs are written directly one after another without individual property headers.
- **StructProperty Arrays**: These have a unique, complex structure involving an extra embedded header that specifies the type of struct *within* the array. The struct bodies themselves are then written sequentially **without** their `StructProperty` headers.
- **ByteProperty Arrays**: Can represent either an array of enum strings (like other complex types) or a single block of raw bytes.
- **Other Complex Types**: Properties like `ObjectProperty`, `TextProperty` are written sequentially **without** their individual headers.
- The `bare_readers` and `bare_writers` class variables provide optimized handling for simple types.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 