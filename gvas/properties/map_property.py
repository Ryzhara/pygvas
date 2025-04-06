"""
Map property implementation for GVAS
Python port of map_property.rs

Key differences from Rust version:
- Uses Python's dict instead of HashMap
- Simplified type handling
"""

from dataclasses import dataclass
from email.base64mime import body_decode
from io import BytesIO
from typing import Dict, Optional, BinaryIO, Any

from .property_base import Property, PropertyTrait, ContextScopeTracker
from ..gvas_types import HashableIndexMap
from ..utils import *


@dataclass
class MapProperty(PropertyTrait):
    """A property that holds a key-value mapping"""

    key_type: str = ""
    value_type: str = ""
    allocation_flags: int = 0
    values: HashableIndexMap | None = None

    def __post_init__(self):
        if self.values is None:
            self.values = HashableIndexMap()

    @classmethod
    def new(cls, key_type: str, value_type: str) -> "MapProperty":
        """Create a new map property"""
        return cls(key_type=key_type, value_type=value_type)

    def read_header(self, stream: BinaryIO) -> (int, str):

        # Read length and array index
        length = read_uint32(stream)
        _array_index = read_uint32(stream, 0)
        self.key_type = read_string(stream)
        self.value_type = read_string(stream)
        _header_terminator = read_uint8(stream, 0)
        # END OF HEADER FOR MAP PROPERTY
        return length

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read map from stream"""

        if include_header:
            # content_length = self.read_header(stream)
            length, self.key_type, self.value_type = read_standard_header(
                stream, stream_readers=[read_string, read_string]
            )

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            # Read number of entries
            self.allocation_flags = read_uint32(stream)
            element_count = read_uint32(stream)

            # Read entries
            self.values = {}
            for _ in range(element_count):
                with ContextScopeTracker("Key") as _scope_tracker:
                    key_prop = Property.new(stream, self.key_type, include_header=False)
                with ContextScopeTracker("Value") as _scope_tracker:
                    value_prop = Property.new(
                        stream, self.value_type, include_header=False
                    )
                self.values[key_prop] = value_prop

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write map to stream"""

        body_buffer = BytesIO()
        buffer_bytes_written = 0

        # START OF BODY
        body_start = body_buffer.tell()
        buffer_bytes_written += write_uint32(body_buffer, self.allocation_flags)
        element_count = len(self.values.keys())
        buffer_bytes_written += write_uint32(body_buffer, element_count)

        # Write entries
        for key, value in self.values.items():
            # wrap them with correct type, then write
            key_property = Property(self.key_type, key)
            buffer_bytes_written += key_property.write(
                body_buffer, include_header=False
            )

            value_property = Property(self.value_type, value)
            buffer_bytes_written += value_property.write(
                body_buffer, include_header=False
            )
        body_end = body_buffer.tell()
        body_bytes = body_end - body_start
        assert body_bytes == buffer_bytes_written

        stream_bytes_written = 0
        if include_header:
            stream_bytes_written += write_standard_header(
                stream,
                "MapProperty",
                length=body_bytes,
                data_to_write=[self.key_type, self.value_type],
            )

        stream_bytes_written += write_bytes(stream, body_buffer.getvalue())

        # now write the temp buffer to the stream
        return stream_bytes_written
