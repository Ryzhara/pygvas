"""
Set property implementation for GVAS
Python port of set_property.rs

Key differences from Rust version:
- Uses Python's set instead of HashSet
- Simplified type handling
"""

from dataclasses import dataclass
from typing import List, Optional, BinaryIO, Any
from io import BytesIO
import struct

from .property_base import Property, PropertyTrait, PropertyOptions
from ..error import DeserializeError
from ..utils import read_string, write_string


@dataclass
class SetProperty(PropertyTrait):
    """A property that stores a set of properties"""

    property_type: str = ""
    allocation_flags: int = 0
    properties: List[Property] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = []

    @classmethod
    def new(
        cls,
        property_type: str,
        allocation_flags: int = 0,
        properties: Optional[List[Property]] = None,
    ) -> "SetProperty":
        """Create a new set property"""
        return cls(
            property_type=property_type,
            allocation_flags=allocation_flags,
            properties=properties or [],
        )

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> None:
        """Read set from stream"""
        if not include_header:
            raise DeserializeError.invalid_property(
                "SetProperty is not supported in arrays", stream.tell()
            )

        # Read length and array index
        length = struct.unpack("<I", stream.read(4))[0]
        array_index = struct.unpack("<I", stream.read(4))[0]
        if array_index != 0:
            position = stream.tell() - 4
            raise DeserializeError.invalid_array_index(array_index, position)

        # Read property type
        self.property_type = read_string(stream)

        # Read terminator
        terminator = stream.read(1)[0]
        if terminator != 0:
            position = stream.tell() - 1
            raise DeserializeError.invalid_terminator(terminator, position)

        # Record start position for length validation
        start = stream.tell()

        # Read allocation flags and element count
        self.allocation_flags = struct.unpack("<I", stream.read(4))[0]
        element_count = struct.unpack("<I", stream.read(4))[0]

        # Read properties
        self.properties = []
        if element_count > 0:
            total_bytes_per_property = (length - 8) // element_count
            for _ in range(element_count):
                prop = Property.new(
                    stream,
                    self.property_type,
                    include_header=False,
                    options=options,
                    suggested_length=total_bytes_per_property,
                )
                self.properties.append(prop)

        # Validate length
        end = stream.tell()
        actual_size = end - start
        if actual_size != length:
            raise DeserializeError.invalid_value_size(length, actual_size, start)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
        options: Optional[PropertyOptions] = None,
    ) -> int:
        """Write set to stream"""
        bytes_written = 0

        if include_header:
            # Write to temporary buffer first to get length
            buffer = BytesIO()
            buffer_bytes = 0

            # Write allocation flags and element count
            buffer.write(struct.pack("<I", self.allocation_flags))
            buffer.write(struct.pack("<I", len(self.properties)))
            buffer_bytes += 8

            # Write properties
            for prop in self.properties:
                buffer_bytes += prop.write(
                    buffer, include_header=False, options=options
                )

            # Write length and array index
            stream.write(struct.pack("<I", buffer_bytes))  # Total length
            stream.write(struct.pack("<I", 0))  # Array index
            bytes_written += 8

            # Write property type
            bytes_written += write_string(stream, self.property_type)

            # Write terminator
            stream.write(bytes([0]))
            bytes_written += 1

            # Write buffer contents
            buffer_data = buffer.getvalue()
            stream.write(buffer_data)
            bytes_written += len(buffer_data)
        else:
            # Write allocation flags and element count
            stream.write(struct.pack("<I", self.allocation_flags))
            stream.write(struct.pack("<I", len(self.properties)))
            bytes_written += 8

            # Write properties
            for prop in self.properties:
                bytes_written += prop.write(
                    stream, include_header=False, options=options
                )

        return bytes_written
