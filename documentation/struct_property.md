# Struct Property Documentation

## Overview
This document describes the `StructProperty` class within the GVAS format. This is a versatile property type used to store structured data. It can represent either one of the predefined "Standard Structs" (like `Vector`, `Guid`, `LinearColor`) or a custom structure containing an arbitrary collection of named GVAS properties.

## Class and Function Definitions

### `StructProperty` (inherits `PropertyTrait`)
Represents a GVAS property holding structured data. The `value` can be either an instance of a `StandardStructTrait` subclass or a dictionary mapping property names (strings) to other GVAS property instances (`UNREAL_ENGINE_PROPERTIES`).

```python
import uuid
from gvas.properties.aggregator_properties import UNREAL_ENGINE_PROPERTIES
from gvas.properties.standard_structs import (
    StandardStructTrait,
    DateTimeStruct,
    GuidStruct,
    TimespanStruct,
    IntPointStruct,
    LinearColorStruct,
    RotatorStruct,
    QuatStruct,
    VectorStruct,
    Vector2DStruct,
)

@dataclass
class StructProperty(PropertyTrait):
    type: Literal["StructProperty"] = "StructProperty"
    guid: Optional[uuid.UUID] = None # Often zero, significant for certain engine types
    type_name: Optional[str] = None  # Name of the struct type (e.g., "Vector", "MyCustomStruct")
    value: Union[
        dict[str, UNREAL_ENGINE_PROPERTIES], # For custom structs
        DateTimeStruct, GuidStruct, TimespanStruct, # Standard structs
        IntPointStruct, LinearColorStruct, RotatorStruct,
        QuatStruct, VectorStruct, Vector2DStruct,
    ] = None

    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID): ...

    def read(self, stream: BinaryIO, include_header: bool = True) -> None: ...
    def read_body(self, stream: BinaryIO, standard_struct_override: StandardStructTrait = None) -> None: ...
    def write(self, stream: BinaryIO, include_header: bool = True) -> int: ...
```

## Binary Format

All multi-byte values are **little-endian**.

### `StructProperty`
Reads/writes the following sequence:
1.  Standard Property Header (Optional, if `include_header` is true):
    *   Property Type Name (`String`): "StructProperty"
    *   Length (Int64): Size in bytes of the struct data body (Step 2).
    *   Type Name (`String`): The name identifying the struct type (e.g., "Vector", "MyCustomStruct").
    *   GUID (16 Bytes): A GUID associated with the struct type. Often zero (`0000...0000`), but can be significant for specific engine types.
    *   Padding (UInt8): Typically 0.
2.  Struct Data Body: The format depends on whether the `Type Name` corresponds to a Standard Struct or a Custom Struct.

    *   **If Standard Struct (`Type Name` matches a known standard type like "Vector", "Guid", etc.):**
        *   The body contains the fixed binary layout specific to that standard struct type (see `standard_structs.md` documentation for details).

    *   **If Custom Struct (`Type Name` is not a standard type):**
        *   The body contains a sequence of GVAS properties, terminated by a "None" string.
        *   Property Sequence (Array): Zero or more instances of:
            *   Property Name (`String`): Name of the property within the struct.
            *   Property Type (`String`): GVAS type name of the property.
            *   Full Property Data: The complete binary data for the property, **including** its own header (`include_header=True`).
        *   Terminator (`String`): The literal string "None" indicating the end of the properties.

```
[Standard Header (Optional)]
  [Property Type Name: String = "StructProperty"]
  [Length: Int64]
  [Type Name: String]
  [GUID: 16 Bytes]
  [Padding: UInt8]

[Struct Data Body]
  # IF Standard Struct:
  [Standard Struct Specific Binary Data]

  # IF Custom Struct:
  [Property 1 Name: String]
  [Property 1 Type: String]
  [Property 1 Data (Full Header + Body)]

  [Property 2 Name: String]
  [Property 2 Type: String]
  [Property 2 Data (Full Header + Body)]

  ...

  [Property N Name: String]
  [Property N Type: String]
  [Property N Data (Full Header + Body)]

  [Terminator: String = "None"]
```

## Examples

### Example: Standard Struct (`VectorStruct`, LWC Disabled)
Value: `VectorStruct(x=1.0, y=2.0, z=3.0)`

```
# Header (assuming include_header=True)
# Property Type Name: "StructProperty" (UTF-8)
0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00

# Length: (Size of VectorStruct body: 3 * float32 = 12 bytes)
0C 00 00 00 00 00 00 00 # Length = 12

# Type Name: "Vector" (UTF-8)
07 00 00 00 56 65 63 74 6F 72 00

# GUID: (Zero GUID)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

# Padding
00

# -- Struct Data Body Starts --
# VectorStruct Data (x=1.0, y=2.0, z=3.0)
00 00 80 3F  # X = 1.0f
00 00 00 40  # Y = 2.0f
00 00 40 40  # Z = 3.0f
```

### Example: Custom Struct
Value: `{"Health": FloatProperty(value=100.0), "Ammo": Int32Property(value=30)}`

```
# Header (assuming include_header=True)
# Property Type Name: "StructProperty" (UTF-8)
0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00

# Length: (Calculated size of custom struct body)
#   Prop1 Name("Health"): 7B+null=8
#   Prop1 Type("FloatProperty"): 14B+null=15
#   Prop1 Data(Full FloatProperty): Header(15+8+1=24) + Body(4) = 28
#   Prop2 Name("Ammo"): 5B+null=6
#   Prop2 Type("Int32Property"): 13B+null=14
#   Prop2 Data(Full Int32Property): Header(14+8+1=23) + Body(4) = 27
#   Terminator("None"): 5B+null=6
#   Total Body = 8 + 15 + 28 + 6 + 14 + 27 + 6 = 104 bytes
68 00 00 00 00 00 00 00 # Length = 104 (0x68)

# Type Name: "MyCustomStruct" (UTF-8) - Example
0F 00 00 00 4D 79 43 75 73 74 6F 6D 53 74 72 75 63 74 00

# GUID: (Zero GUID)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

# Padding
00

# -- Struct Data Body Starts --
# Property 1 Name: "Health" (UTF-8)
07 00 00 00 48 65 61 6C 74 68 00

# Property 1 Type: "FloatProperty" (UTF-8)
0E 00 00 00 46 6C 6F 61 74 50 72 6F 70 65 72 74 79 00

# Property 1 Data (Full FloatProperty Header + Body)
#   Header: Name("FloatProperty" 15B) + Len(4 -> 8B) + Pad(1B) = 24 Bytes
#   Body: Value(100.0 -> 4B)
0E 00 00 00 46 6C 6F 61 74 50 72 6F 70 65 72 74 79 00 # Header Name
04 00 00 00 00 00 00 00 # Header Length = 4
00                      # Header Padding
00 00 C8 42             # Body Value = 100.0f

# Property 2 Name: "Ammo" (UTF-8)
05 00 00 00 41 6D 6D 6F 00

# Property 2 Type: "Int32Property" (UTF-8)
0E 00 00 00 49 6E 74 33 32 50 72 6F 70 65 72 74 79 00

# Property 2 Data (Full Int32Property Header + Body)
#   Header: Name("Int32Property" 14B) + Len(4 -> 8B) + Pad(1B) = 23 Bytes
#   Body: Value(30 -> 4B)
0E 00 00 00 49 6E 74 33 32 50 72 6F 70 65 72 74 79 00 # Header Name
04 00 00 00 00 00 00 00 # Header Length = 4
00                      # Header Padding
1E 00 00 00             # Body Value = 30

# Terminator: "None" (UTF-8)
05 00 00 00 4E 6F 6E 65 00
```

## Implementation Notes
- The distinction between a standard struct and a custom struct is determined by checking if the `type_name` read from the header exists in the predefined list of standard struct types (`is_standard_struct`).
- `deserialization_hints` can be used to override the `type_name` or provide context (like byte count for `ByteBlobStruct`).
- For custom structs, properties are read/written sequentially, including their full headers, until the "None" string terminator is encountered.
- Standard structs have fixed binary layouts handled by their respective classes (e.g., `VectorStruct.read/write`).
- The `guid` field is serialized/deserialized but often contains only zeros.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 