"""
Array property implementation for GVAS
Python port of array_property.rs

Key differences from Rust version:
- Uses Python lists instead of Vec
- Simplified type handling
"""

from dataclasses import dataclass
from typing import List, Optional, Any, BinaryIO
import struct
from io import BytesIO

from .property_base import Property, PropertyTrait, PropertyOptions
from ..error import DeserializeError, SerializeError
from ..gvas_types import Guid
from ..utils import read_string, write_string


@dataclass
class ArrayProperty(PropertyTrait):
    """A property that holds an array of values"""

    property_type: str = ""
    field_name: Optional[str] = None
    type_name: Optional[str] = None
    guid: Optional[Guid] = None
    values: List[Any] = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.guid is None:
            self.guid = Guid()

    @classmethod
    def new(
        cls,
        property_type: str,
        field_name: Optional[str] = None,
        type_name: Optional[str] = None,
        guid: Optional[Guid] = None,
    ) -> "ArrayProperty":
        """Create a new array property"""
        return cls(
            property_type=property_type,
            field_name=field_name,
            type_name=type_name,
            guid=guid or Guid(),
        )

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read array from stream"""

        property_length_to_check = 0
        if include_header:
            # Read length and array index
            length = struct.unpack("<I", stream.read(4))[0]
            print(f"read array {length=}")

            property_length_to_check = length
            array_index = struct.unpack("<I", stream.read(4))[0]
            if array_index != 0:
                position = stream.tell() - 4
                raise DeserializeError.invalid_array_index(array_index, position)

            # Read property type
            self.property_type = read_string(stream)
            print(f"read array {self.property_type=}")

            # Read terminator
            terminator = stream.read(1)[0]
            if terminator != 0:
                position = stream.tell() - 1
                raise DeserializeError.invalid_terminator(terminator, position)

            # Read number of elements in the array
            array_member_count = struct.unpack("<I", stream.read(4))[0]
            print(f"Found array member {array_member_count=}")

            # Handle struct properties
            if self.property_type == "StructProperty":
                # Read field name
                self.field_name = read_string(stream)
                print(f"Found StructProperty {self.field_name=}")

                # Read structure sub/generic type
                prop_type = read_string(stream)

                print(f"Found StructProperty {prop_type=}")
                if prop_type != self.property_type:
                    raise DeserializeError(
                        f"Property type mismatch: {prop_type} != {self.property_type}"
                    )

                # Read properties size
                prop_size = struct.unpack("<Q", stream.read(8))[0]
                property_length_to_check = prop_size

                print(f"Found StructProperty {prop_size=}")

                # Read struct type name
                self.type_name = read_string(stream)

                # Read GUID
                guid_bytes = stream.read(16)
                self.guid = Guid.from_bytes(guid_bytes)

                print(f"Found StructProperty {self.guid=}")

                # Read terminator
                terminator = stream.read(1)[0]
                if terminator != 0:
                    raise DeserializeError.invalid_terminator(
                        terminator, stream.tell() - 1
                    )

                # now we are supposed to read structs bodies, NO HEADER
                # Read array elements
                self.values = []
                print(f"Reading StructProperty members")
                for idx in range(array_member_count):
                    print(f"Reading StructProperty member {idx=}")
                    prop = Property.new(
                        stream, self.property_type, include_header=False, options=None
                    )
                    self.values.append(prop.value)
            else:

                # REF: length validation may not be correct
                # Record start position for length validation
                start = stream.tell()

                # Read array elements
                self.values = []
                print(f"Reading StructProperty members")
                for idx in range(array_member_count):
                    print(f"Reading StructProperty member {idx=}")
                    prop = Property.new(
                        stream, self.property_type, include_header=True, options=None
                    )
                    self.values.append(prop.value)

                # Validate length
                end = stream.tell()
                actual_size = end - start
                if actual_size != property_length_to_check:
                    raise DeserializeError.invalid_value_size(
                        property_length_to_check, actual_size, start
                    )
        else:
            raise DeserializeError.invalid_property(
                "ArrayProperty is not supported in arrays", stream
            )

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write array to stream"""
        if not include_header:
            raise SerializeError.invalid_property(
                "ArrayProperty is not supported in arrays"
            )

        # First write to a temporary buffer to get the length
        buffer = BytesIO()
        buffer_bytes = 0

        # Write property type
        type_bytes = (self.property_type + "\0").encode("utf-8")
        buffer.write(struct.pack("<I", len(type_bytes)))
        buffer.write(type_bytes)
        buffer_bytes += 4 + len(type_bytes)

        # Write terminator
        buffer.write(bytes([0]))
        buffer_bytes += 1

        # Handle struct properties
        if self.property_type == "StructProperty":
            # Write field name
            field_bytes = (self.field_name + "\0").encode("utf-8")
            buffer.write(struct.pack("<I", len(field_bytes)))
            buffer.write(field_bytes)
            buffer_bytes += 4 + len(field_bytes)

            # Write property type again
            buffer.write(struct.pack("<I", len(type_bytes)))
            buffer.write(type_bytes)
            buffer_bytes += 4 + len(type_bytes)

            # Create buffer for properties
            prop_buffer = BytesIO()
            prop_bytes = 0

            # Create options for nested properties
            nested_options = PropertyOptions(
                hints=options.hints if options else None,
                property_path=(
                    f"{options.property_path}.ArrayProperty"
                    if options
                    else "ArrayProperty"
                ),
            )

            # Write properties to buffer
            for value in self.values:
                prop = Property(self.property_type, value)
                prop_bytes += prop.write(prop_buffer, options=nested_options)

            # Write properties size
            buffer.write(struct.pack("<Q", prop_bytes))
            buffer_bytes += 8

            # Write struct type name
            type_bytes = (self.type_name + "\0").encode("utf-8")
            buffer.write(struct.pack("<I", len(type_bytes)))
            buffer.write(type_bytes)
            buffer_bytes += 4 + len(type_bytes)

            # Write GUID
            buffer.write(self.guid.to_bytes())
            buffer_bytes += 16

            # Write terminator
            buffer.write(bytes([0]))
            buffer_bytes += 1

            # Write properties from buffer
            buffer_data = prop_buffer.getvalue()
            buffer.write(buffer_data)
            buffer_bytes += len(buffer_data)

        # Write number of elements
        buffer.write(struct.pack("<I", len(self.values)))
        buffer_bytes += 4

        # Create options for nested properties
        nested_options = PropertyOptions(
            hints=options.hints if options else None,
            property_path=(
                f"{options.property_path}.ArrayProperty" if options else "ArrayProperty"
            ),
        )

        # Write array elements
        for value in self.values:
            prop = Property(self.property_type, value)
            buffer_bytes += prop.write(buffer, options=nested_options)

        # Write header
        bytes_written = 0
        stream.write(struct.pack("<I", buffer_bytes))  # length
        stream.write(struct.pack("<I", 0))  # array_index
        bytes_written += 8

        # Write buffer contents
        buffer_data = buffer.getvalue()
        stream.write(buffer_data)
        bytes_written += len(buffer_data)

        return bytes_written
