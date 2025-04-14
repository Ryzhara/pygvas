"""
Enum property implementation for GVAS
Python port of enum_property.rs
"""

from io import BytesIO
from typing import Optional

from pydantic.dataclasses import dataclass

from .property_base import PropertyTrait
from ..utils import *


@dataclass
class EnumProperty(PropertyTrait):
    """A property that holds an enumeration value"""

    type: str = "EnumProperty"
    enum_type: Optional[str] = None
    value: Optional[str] = None

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read enum value from stream"""
        length = 0
        if include_header:
            length, self.enum_type = read_standard_header(
                stream, stream_readers=[read_string]
            )

        # Read value
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value = read_string(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write enum value to stream"""

        body_buffer = BytesIO()
        body_bytes = write_string(body_buffer, self.value)

        bytes_written = 0
        if include_header:
            bytes_written = write_standard_header(
                stream,
                "EnumProperty",
                length=body_bytes,
                data_to_write=[self.enum_type],
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
