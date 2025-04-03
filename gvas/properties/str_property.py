"""
String property implementations for GVAS
Python port of str_property.rs and name_property.rs

Contains implementations for:
- StrProperty
- NameProperty
"""

from dataclasses import dataclass
from typing import Optional, BinaryIO
import struct
from io import BytesIO

from .property_base import PropertyTrait, SerializationHints
from ..error import DeserializeError
from ..utils import *


@dataclass
class StrProperty(PropertyTrait):
    """A property that holds a string value"""

    value: Optional[str] = None

    @classmethod
    def new(cls, value: Optional[str] = None) -> "StrProperty":
        """Create a new string property"""
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read string from stream"""
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        with ByteCountValidator(stream, length, do_validation=include_header):
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write string to stream"""
        bytes_written = 0

        # Write to temporary buffer first to get length
        buffer = BytesIO()
        if self.value is None:
            write_uint32(buffer, 0)  # empty string
        else:
            write_string(buffer, self.value)

        if include_header:
            bytes_written += write_standard_header(
                stream, "StrProperty", length=len(buffer.getvalue())
            )

        # Write buffer contents
        bytes_written += stream.write(buffer.getvalue())

        return bytes_written
