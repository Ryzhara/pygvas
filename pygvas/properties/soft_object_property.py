from io import BytesIO
from typing import Literal

from pydantic.dataclasses import dataclass

from pygvas.properties.property_base import PropertyTrait
from pygvas.gvas_utils import *


@dataclass
class SoftObjectProperty(PropertyTrait):
    """A property that holds a SOFT object value with a trailing UINT32 suffix"""

    type: Literal["SoftObjectProperty"] = "SoftObjectProperty"
    value: Optional[str] = None
    suffix: Optional[int] = 0  # some form of standard terminator?

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        # Read value
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value = read_string(stream)
            # not certain what this value is, but carry it through
            self.suffix = read_uint32(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = write_string(body_buffer, self.value)
        # carried-through value
        body_bytes += write_uint32(body_buffer, self.suffix)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written = write_standard_header(
                stream, "SoftObjectProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
