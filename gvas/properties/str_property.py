"""
String property implementations for GVAS
Python port of str_property.rs and name_property.rs

Contains implementations for:
- StrProperty
- NameProperty
"""

from dataclasses import dataclass
from email.base64mime import body_decode
from typing import Optional, BinaryIO
import struct
from io import BytesIO

from .property_base import PropertyTrait
from ..error import DeserializeError
from ..utils import *


@dataclass
class StrProperty(PropertyTrait):

    def __init__(self, type_name: str, value: Optional[str] = None):
        """Create a new string property"""
        self.type = type_name
        self.value = value

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read string from stream"""
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write string to stream"""
        bytes_written = 0

        # Write to temporary body_buffer first to get length
        body_buffer = BytesIO()
        body_bytes = 0
        if self.value is None:
            body_bytes += write_uint32(body_buffer, 0)  # empty string
        else:
            body_bytes += write_string(body_buffer, self.value)
        assert body_bytes == len(body_buffer.getvalue())

        if include_header:
            bytes_written += write_standard_header(
                stream, "StrProperty", length=body_bytes
            )

        bytes_written += stream.write(body_buffer.getvalue())
        return bytes_written
