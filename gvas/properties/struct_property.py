"""
Struct property implementation for GVAS
Python port of struct_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, BinaryIO, List
from io import BytesIO

from .graphical_types import is_special_struct, get_special_struct_instance
from .property_base import Property, PropertyTrait, SerializationHints
from ..error import DeserializeError
from ..utils import *


@dataclass
class StructPropertyValue:
    """Value stored in a struct property"""

    type_name: str
    properties: Dict[str, Property]

    @classmethod
    def new(cls, type_name: str) -> "StructPropertyValue":
        """Create a new struct property value"""
        return cls(type_name=type_name, properties={})


@dataclass
class StructProperty(PropertyTrait):
    """A property that holds structured data"""

    type_name: str = ""
    guid: Guid = None
    value: Optional[StructPropertyValue] = None

    def __post_init__(self):
        if self.guid is None:
            self.guid = Guid()

    @classmethod
    def new(cls, type_name: str, guid: Optional[Guid] = None) -> "StructProperty":
        """Create a new struct property"""
        return cls(type_name=type_name, guid=guid or Guid())

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read struct from stream"""
        if not include_header:
            raise DeserializeError()

        length = self.read_header(stream)
        # this is BODY
        # Record start position for length validation
        start = stream.tell()
        _result = self.read_body(stream)
        # Validate length if header was included
        end = stream.tell()
        actual_size = end - start
        assert (
            actual_size == length
        ), f"Invalid value size: {length} != {actual_size} at {start}"

    def read_header(self, stream) -> int:
        length = read_uint32(stream, None)
        _array_index = read_uint32(stream, 0)
        self.type_name = read_string(stream)
        self.guid = read_guid_with_terminator(stream)

        return length

    def read_body(self, stream: BinaryIO) -> bytes:

        # Create struct value
        self.value = StructPropertyValue(self.type_name, {})

        # Read properties until we hit None. Or is it "None" ?
        while True:
            # Read property property_name
            property_name = read_string(stream)
            # print(f"Found struct {property_name=}")
            if property_name == "None":
                # print(f"property reading NONE; break")
                break

            # Read property type
            property_type = read_string(stream)
            # print(f"found struct {property_type=}")
            if not property_type:
                print(f"property_type NONE; break!!!!!")
                break

            # Read property
            if is_special_struct(self.type_name):
                print(f"Struct: Reading instance of {self.type_name}")
                property_value = get_special_struct_instance(self.type_name)
                property_value.read(stream)
                self.value.properties[property_name] = Property(
                    self.type_name, property_value
                )
            else:
                property_value = Property.new(
                    stream, property_type, include_header=True
                )
                self.value.properties[property_name] = property_value

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write struct to stream"""
        # REF: Write to a temporary buffer first to get the length of the body
        buffer = BytesIO()
        buffer_bytes = 0
        header_length_position = 0
        header_length = 0

        if include_header:
            header_length, header_length_position = self.write_header(buffer)
            buffer_bytes += header_length

        # Write property children
        start_child_bytes = buffer_bytes
        if self.value:
            for name, prop in self.value.properties.items():
                # Write property type_name
                buffer_bytes += write_string(buffer, name)

                # # Write property type needs to be written by the object
                # buffer_bytes += write_string(buffer, prop.type)

                # Write property
                buffer_bytes += prop.write(buffer, include_header=True)

        # Write "None" terminator for the struct
        buffer_bytes += write_string(buffer, "None")
        # buffer_bytes == len("None")+1+4

        end_child_bytes = buffer_bytes

        # Update total child byte count in the header
        if include_header:
            buffer.seek(header_length_position)
            buffer.write(struct.pack("<I", end_child_bytes - start_child_bytes))

        # Write buffer contents with optional header
        buffer.seek(0)
        buffer_data = buffer.getvalue()
        stream.write(buffer_data)
        total_bytes_written = len(buffer_data)

        return total_bytes_written

    def write_header(self, stream: BinaryIO) -> (int, int):
        bytes_written = 0

        # Write property type
        bytes_written += write_string(stream, "StructProperty")

        # Write placeholder for struct size (4b) and index (4b), which must be zero
        header_length_position = stream.tell()
        bytes_written += stream.write(struct.pack("<I", 0))
        bytes_written += stream.write(struct.pack("<I", 0))
        # buffer_bytes += 8

        # Write property subtype, aka type_name
        bytes_written += write_string(stream, self.type_name)

        bytes_written += write_guid_with_terminator(stream, self.guid)
        return bytes_written, header_length_position
