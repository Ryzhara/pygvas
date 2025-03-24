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
from .struct_property import StructProperty
from ..error import DeserializeError, SerializeError
from ..gvas_types import Guid
from ..utils import (
    read_string,
    write_string,
    read_guid_with_terminator,
    write_guid_with_terminator,
)


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
        if not include_header:
            raise DeserializeError.invalid_property(
                "ArrayProperty is not supported in arrays", stream.tell()
            )

        length = self.read_header(stream)
        print(f"array property: {length=}")
        # self.property_type should be populated
        start = stream.tell()
        self.read_body(stream)
        end = stream.tell()
        if end - start != length:
            raise DeserializeError.invalid_value_size(length, end - start, start)

    def read_header(self, stream: BinaryIO) -> (int, str):
        # Read length and array index
        length = struct.unpack("<I", stream.read(4))[0]
        # print(f"Read ArrayProperty {length=}")

        array_index = struct.unpack("<I", stream.read(4))[0]
        if array_index != 0:
            position = stream.tell() - 4
            raise DeserializeError.invalid_array_index(array_index, position)

        # Read property type
        self.property_type = read_string(stream)
        # print(f"Read ArrayProperty: {self.property_type=}")

        # Read string? terminator
        terminator = stream.read(1)[0]
        if terminator != 0:
            position = stream.tell() - 1
            raise DeserializeError.invalid_terminator(terminator, position)

        # END OF HEADER FOR ARRAY PROPERTY
        return length

    def read_body(self, stream: BinaryIO) -> None:

        # Read number of elements in the array
        property_count = struct.unpack("<I", stream.read(4))[0]
        # print(f"Found {property_count=}")

        self.values = []  # prepare storage

        match self.property_type:
            case "StructProperty":
                # Read field type_name
                self.field_name = read_string(stream)

                # Read structure sub/generic type
                array_member_property_type = read_string(stream)

                # print(f"Found StructProperty {array_member_property_type=}")
                assert (
                    array_member_property_type == self.property_type
                ), f"Property array member type mismatch: {array_member_property_type} != {self.property_type}"

                # Read properties size
                # TODO: add check for byte count
                properties_size = struct.unpack("<Q", stream.read(8))[0]

                self.type_name = read_string(stream)

                self.guid = read_guid_with_terminator(stream)

                # now we are supposed to read structs bodies, NO HEADER
                # Read array elements
                # print(f"Reading StructProperty members")
                for idx in range(property_count):
                    # print(f"Reading StructProperty member {idx=}")
                    new_array_property = StructProperty(self.property_type)
                    # print(f"Reading StructProperty member {new_array_property=}")
                    # have to key the READ from the subtype type_name! aka STRUCT_NAME
                    new_array_property.read_body(stream)
                    self.values.append(new_array_property)

            # we probably  need to handle more things in detail? read the code
            # case "Guid", "DateTime", "Quat", "Vector", "Rotator", etc:
            #     pass
            case "StrProperty":
                for _ in range(property_count):
                    string_element = read_string(stream)
                    self.values.append(string_element)
            case _:

                # Read array elements
                for _ in range(property_count):
                    new_array_property = Property.new(
                        stream, self.property_type, include_header=False, options=None
                    )
                    self.values.append(new_array_property.value)

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

        # First write to a temporary array_buffer to get the length
        array_buffer = BytesIO()
        array_bytes = 0

        # Write property type
        array_bytes += write_string(array_buffer, "ArrayProperty")

        # ====== START OF HEADER ==============
        ap_byte_count_location = array_bytes
        array_bytes += array_buffer.write(struct.pack("<I", 0))  # TBD total byte count
        array_bytes += array_buffer.write(struct.pack("<I", 0))  # index

        array_bytes += write_string(array_buffer, self.property_type)

        # header terminator null byte
        array_bytes += array_buffer.write(struct.pack("<B", 0))
        # ====== END OF HEADER ==============

        # property_count, or number of elements in the array
        property_count = len(self.values)
        array_bytes += array_buffer.write(struct.pack("<I", property_count))
        print(f"\tWriting array: {property_count=}")
        # Handle struct properties
        match self.property_type:
            case "StructProperty":

                array_bytes += write_string(array_buffer, self.field_name)

                # Write property type again
                array_bytes += write_string(array_buffer, self.property_type)

                properties_byte_count_position = array_buffer.tell()
                array_bytes += array_buffer.write(struct.pack("<I", 0))
                array_bytes += array_buffer.write(struct.pack("<I", 0))

                array_bytes += write_string(array_buffer, self.type_name)
                array_bytes += write_guid_with_terminator(array_buffer, self.guid)

                # Write properties to array_buffer
                struct_properties_start = array_buffer.tell()
                for struct_property in self.values:
                    array_bytes += struct_property.write(
                        array_buffer, include_header=False
                    )
                struct_properties_end = array_buffer.tell()

                # write total bytes in structs
                struct_properties_bytes = (
                    struct_properties_end - struct_properties_start
                )
                array_buffer.seek(properties_byte_count_position)
                array_buffer.write(struct.pack("<I", struct_properties_bytes))

            case "StrProperty":
                for string_value in self.values:
                    array_bytes += write_string(array_buffer, string_value)

            case _:
                # Write array elements
                for array_property in self.values:
                    array_bytes += array_property.write(
                        array_buffer, include_header=False
                    )

        # Write total byte count size
        array_buffer.seek(ap_byte_count_location)
        array_buffer.write(struct.pack("<I", array_bytes))

        # now write the whole thing
        stream.write(array_buffer.getvalue())

        return array_bytes
