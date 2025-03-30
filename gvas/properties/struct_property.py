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

from .standard_types import (
    is_special_struct,
    get_special_struct_instance,
    SpecialStructTrait,
)
from .property_base import Property, PropertyTrait, SerializationHints
from ..utils import *


@dataclass
class StructPropertyValue:
    """Value stored in a struct property"""

    type_name: str
    properties: Dict[str, Property] | SpecialStructTrait

    @classmethod
    def new(cls, type_name: str, properties=None) -> "StructPropertyValue":
        """Create a new struct property value"""
        return cls(type_name=type_name, properties=properties or {})


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
        if include_header:
            length = self.read_header(stream)

        # Record start position for length validation
        start = stream.tell()
        self.read_body(stream)
        # Validate length if header was included
        end = stream.tell()

        if include_header:
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

    def read_body(self, stream: BinaryIO) -> None:
        """we must check for type_name in the special (graphical) structure types and
        then invoke reading that, vs reading a custom, arbitrary body as below"""

        if is_special_struct(self.type_name):
            property_value = get_special_struct_instance(self.type_name)
            property_value.read(stream)
            self.value = StructPropertyValue(self.type_name, property_value)
            # print(f"Struct: Reading instance of {self.type_name} {self.value=}")

        else:  # fully custom
            self.value = StructPropertyValue(self.type_name, {})
            # Read properties until we hit None. Or is it "None" ?
            while True:
                # Read property property_name
                property_name = read_string(stream)
                if property_name == "None":
                    break

                # Read property type
                property_type = read_string(stream)
                if not property_type:
                    print(f"property_type NONE; break!!!!!")
                    break

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
            if is_special_struct(self.type_name):
                # print(f"Struct: Writing instance of {self.type_name}")
                buffer_bytes += self.value.properties.write(buffer)

            else:  # fully custom
                for property_name, property_value in self.value.properties.items():
                    buffer_bytes += write_string(buffer, property_name)
                    buffer_bytes += property_value.write(buffer, include_header=True)
                # Write "None" terminator for the struct
                buffer_bytes += write_string(buffer, "None")

        end_child_bytes = buffer_bytes

        # Update total child byte count in the header
        if include_header:
            buffer.seek(header_length_position)
            write_uint32(buffer, end_child_bytes - start_child_bytes)

        # Write buffer contents with optional header
        buffer_data = buffer.getvalue()
        stream.write(buffer_data)
        total_bytes_written = len(buffer_data)

        return total_bytes_written

    def write_header(self, stream: BinaryIO) -> (int, int):
        bytes_written = 0

        # Write property type
        bytes_written += write_string(stream, "StructProperty")

        header_length_position = stream.tell()
        bytes_written += write_uint32(stream, 0)  # placeholder for length
        bytes_written += write_uint32(stream, 0)  # array_index zero

        # Write property subtype, aka type_name
        bytes_written += write_string(stream, self.type_name)

        bytes_written += write_guid_with_terminator(stream, self.guid)
        return bytes_written, header_length_position
