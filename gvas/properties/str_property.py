"""
String property implementations for GVAS
Python port of str_property.rs
"""

from io import BytesIO
from typing import Literal

from pydantic.dataclasses import dataclass

from gvas.gvas_utils import *
from gvas.properties.property_base import PropertyTrait


@dataclass
class StrProperty(PropertyTrait):

    type: Literal["StrProperty"] = "StrProperty"
    value: Optional[str] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read string from stream"""
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value = read_string(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
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
