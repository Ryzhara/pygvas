"""
FieldPath property implementation for GVAS
Python port of field_path_property.rs
"""

from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional, Dict, Any, BinaryIO, List
from .property_base import PropertyTrait
from ..utils import *


@dataclass
class FieldPath:
    type: str = "FieldPath"
    path: list[str] = field(default_factory=list)
    resolved_owner: str = None

    def read(self, stream: BinaryIO):
        path_element_count: int = read_uint32(stream)

        for _ in range(path_element_count):
            self.path.append(read_string(stream))
        self.resolved_owner = read_string(stream)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_uint32(stream, len(self.path))
        for path_element in self.path:
            bytes_written += write_string(stream, path_element)
        bytes_written += write_string(stream, self.resolved_owner)
        return bytes_written


@dataclass
class FieldPathProperty(PropertyTrait):
    """A property that holds an FieldPath value"""

    type: str = "FieldPathProperty"
    value: FieldPath = None

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        self.value = FieldPath(path=[], resolved_owner="")
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value.read(stream)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write enum value to stream"""

        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = self.value.write(body_buffer)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "FieldPathProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
