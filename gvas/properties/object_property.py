"""
Object property implementation for GVAS
Python port of object_property.rs
"""

from io import BytesIO
from typing import Optional, Literal

from pydantic.dataclasses import dataclass

from .property_base import PropertyTrait
from ..engine_tools import ByteCountValidator
from ..gvas_utils import *


@dataclass
class ObjectProperty(PropertyTrait):
    """A property that holds an object value"""

    type: Literal["ObjectProperty"] = "ObjectProperty"
    value: Optional[str] = None

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

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

        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = write_string(body_buffer, self.value)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written = write_standard_header(
                stream, "ObjectProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
