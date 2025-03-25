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
import struct

from .property_base import Property, PropertyTrait, PropertyOptions
from ..gvas_types import Guid
from ..error import DeserializeError
from ..utils import (
    read_string,
    write_string,
    read_guid_with_terminator,
    write_guid_with_terminator,
)


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
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read struct from stream"""
        if not include_header:
            raise DeserializeError()

        length = self.read_header(stream)
        # this is BODY
        # Record start position for length validation
        start = stream.tell()
        result_ = self.read_body(stream)
        # Validate length if header was included
        end = stream.tell()
        actual_size = end - start
        if actual_size != length:
            raise DeserializeError.invalid_value_size(length, actual_size, start)

    def read_header(self, stream) -> int:
        # Read length and array index
        length = struct.unpack("<I", stream.read(4))[0]
        array_index = struct.unpack("<I", stream.read(4))[0]
        # print(f"found {length=} {array_index=}")
        if array_index != 0:
            print(f"found non-zero index! {array_index}")

        # Read struct type type_name
        self.type_name = read_string(stream)
        # print(f"Struct length {length=} for {self.type_name}")

        self.guid = read_guid_with_terminator(stream)

        return length

    def read_body(self, stream: BinaryIO) -> bytes:

        # Create struct value
        self.value = StructPropertyValue(self.type_name, {})

        """ We should have a match self.type_name: here with
        Vector
        Vector2D
        Rotator
        Quat
        Datetime
        Timespan
        LinearColor
        IntPoint
        Guid
        and then the catchall?
        """

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

            property_value = Property.new(stream, property_type, include_header=True)
            # print(f"found struct {property_value=}")
            self.value.properties[property_name] = property_value

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write struct to stream"""
        # REF: Write to a temporary buffer first to get the length of the body
        buffer = BytesIO()
        buffer_bytes = 0
        header_length_and_index_position = 0
        header_length = 0

        if self.type_name == "JsonObjectWrapper":
            kludge = 314159

        if include_header:
            # Write property type
            buffer_bytes += write_string(buffer, "StructProperty")

            header_length, header_length_and_index_position = self.write_header(buffer)
            buffer_bytes += header_length

        # Write property children
        if self.value:
            for name, prop in self.value.properties.items():
                # Write property type_name
                buffer_bytes += write_string(buffer, name)

                # # Write property type needs to be written by the object
                # buffer_bytes += write_string(buffer, prop.type)

                # Write property
                buffer_bytes += prop.write(buffer, include_header=True)

        # Write None terminator for the struct
        # This needs to be "None" as a string
        buffer_bytes += write_string(buffer, "None")
        # buffer_bytes == len("None")+1+4

        # Update total child size in the header
        if include_header:
            buffer.seek(header_length_and_index_position)
            # print(f"Update struct header length {buffer_bytes - header_length=}")
            buffer.write(struct.pack("<I", buffer_bytes - header_length))
            # buffer.write(struct.pack("<I", 0))

        # Write buffer contents with optional header
        buffer.seek(0)
        buffer_data = buffer.getvalue()
        stream.write(buffer_data)
        total_bytes_written = len(buffer_data)

        return total_bytes_written

    def write_header(self, stream: BinaryIO) -> (int, int):
        bytes_written = 0

        # Write placeholder for struct size (4b) and index (4b), which must be zero
        length_and_index_position = stream.tell()
        bytes_written += stream.write(struct.pack("<I", 0))
        bytes_written += stream.write(struct.pack("<I", 0))
        # buffer_bytes += 8

        # Write property subtype, aka type_name
        bytes_written += write_string(stream, self.type_name)

        bytes_written += write_guid_with_terminator(stream, self.guid)
        return bytes_written, length_and_index_position
