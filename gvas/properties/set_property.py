"""
Set property implementation for GVAS
Python port of set_property.rs

Key differences from Rust version:
- Uses Python's set instead of HashSet
- Simplified type handling
"""

from io import BytesIO
from typing import Optional

from pydantic.dataclasses import dataclass

from .property_base import PropertyFactory, PropertyTrait
from ..utils import *


@dataclass
class SetProperty(PropertyTrait):
    """A property that stores a set of properties"""

    type: str = "SetProperty"
    property_type: Optional[str] = None
    allocation_flags: int = 0
    properties: Optional[List[PropertyFactory]] = None

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read set from stream"""
        if not include_header:
            raise DeserializeError.invalid_property(
                "SetProperty is not supported in arrays", stream.tell()
            )

        length, self.property_type = read_standard_header(
            stream, stream_readers=[read_string]
        )

        with ByteCountValidator(stream, length, do_validation=True) as _validator:
            self.allocation_flags = read_uint32(stream)
            element_count = read_uint32(stream)

            self.properties = []
            if element_count > 0:
                total_bytes_per_property = (length - 8) // element_count
                for _ in range(element_count):
                    prop = PropertyFactory.new(
                        stream,
                        self.property_type,
                        include_header=False,
                        suggested_length=total_bytes_per_property,
                    )
                    self.properties.append(prop)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write set to stream"""

        # Create the body in a temporary buffer
        body_buffer = BytesIO()
        body_bytes = 0

        # Write allocation flags and element count
        body_bytes += write_uint32(body_buffer, self.allocation_flags)
        body_bytes += write_uint32(body_buffer, len(self.properties))

        # Write properties
        for set_property in self.properties:
            body_bytes += set_property.write(body_buffer, include_header=False)

        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream,
                self.property_type,
                length=body_bytes,
                data_to_write=[self.property_type],
            )

        # Write buffer contents
        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
