"""
Name property implementation for GVAS
Python port of name_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from dataclasses import dataclass
from email.base64mime import body_decode
from io import BytesIO
from typing import Optional, BinaryIO
from .property_base import PropertyTrait
from ..utils import *


@dataclass
class NameProperty(PropertyTrait):
    """A property that holds a name"""

    array_index: int = 0
    value: Optional[str] = None

    @classmethod
    def new(cls, value: Optional[str] = None, array_index: int = 0) -> "NameProperty":
        """Create a new name property"""
        return cls(array_index=array_index, value=value)

    @classmethod
    def from_str(cls, value: str) -> "NameProperty":
        """Create a name property from a string"""
        return cls.new(value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read name from stream"""
        length, start, end = 0, 0, 0
        if include_header:
            length, self.array_index = read_standard_header(
                stream, assert_array_index=None
            )

        # Record start position for length validation
        with ByteCountValidator(stream, length, do_validation=include_header):
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
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
