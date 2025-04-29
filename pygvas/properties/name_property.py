"""
Name property implementation for GVAS
Python port of name_property.rs
"""

from io import BytesIO
from typing import Literal

from pydantic.dataclasses import dataclass

from pygvas.properties.property_base import PropertyTrait
from pygvas.gvas_utils import *


@dataclass
class NameProperty(PropertyTrait):
    """A property that holds a name"""

    type: Literal["NameProperty"] = "NameProperty"
    array_index: int = 0
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read name from stream"""
        length, start, end = 0, 0, 0
        if include_header:
            length, self.array_index = read_standard_header(
                stream, assert_array_index=None
            )

        # Record start position for length validation
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value = read_string(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write name to stream"""
        # Write to temporary buffer first to get length
        body_buffer = BytesIO()
        length = write_string(body_buffer, self.value)

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "NameProperty", length=length, array_index=self.array_index
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
