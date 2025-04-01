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
class Delegate:
    object: str
    function_name: str

    def read(self, stream: BinaryIO):
        self.object = read_string(stream)
        self.function_name = read_string(stream)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_string(stream, self.object)
        bytes_written += write_string(stream, self.function_name)
        return bytes_written


@dataclass
class DelegateProperty(PropertyTrait):
    value: Delegate

    @classmethod
    def new(cls, value: Delegate) -> "DelegateProperty":
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        length = 0
        if include_header:
            length = read_uint32(stream)
            _array_index = read_uint32(stream, 0)
            # if there were strings, they'd go here
            _terminator = read_uint8(stream, 0)

        self.value = Delegate(object="", function_name="")
        # Read value
        start = stream.tell()
        self.value.read(stream)
        end = stream.tell()

        # Verify length
        if include_header:
            if end - start != length:
                raise DeserializeError.invalid_value_size(length, end - start, start)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write enum value to stream"""

        # create temporary buffer for body
        temp_body_buffer = BytesIO()
        body_bytes = self.value.write(temp_body_buffer)
        assert body_bytes == len(temp_body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "DelegateProperty")
            bytes_written += write_uint32(stream, body_bytes)
            bytes_written += write_uint32(stream, 0)  # array_index
            # if there were strings, they'd go here
            bytes_written += write_uint8(stream, 0)  # terminator

        # Write enum value
        bytes_written += write_bytes(stream, temp_body_buffer.getvalue())

        return bytes_written


@dataclass()
class MulticastScriptDelegate:
    delegates: list[Delegate] = field(default_factory=list)

    def read(self, stream: BinaryIO) -> None:
        delegate_count = read_uint32(stream)
        for _ in range(delegate_count):
            delegate = Delegate(object="", function_name="")
            delegate.read(stream)
            self.delegates.append(delegate)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        delegate_count = len(self.delegates)
        bytes_written += write_uint32(stream, delegate_count)
        for delegate in self.delegates:
            bytes_written += delegate.write(stream)
        return bytes_written


@dataclass()
class MulticastInlineDelegateProperty(PropertyTrait):

    value: MulticastScriptDelegate = None

    @classmethod
    def new(cls, value: MulticastScriptDelegate) -> "MulticastInlineDelegateProperty":
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header=True,
    ) -> None:
        length = 0
        if include_header:
            length = read_uint32(stream)
            _array_index = read_uint32(stream, 0)
            # if there were strings, they'd go here
            _terminator = read_uint8(stream, 0)

        self.value = MulticastScriptDelegate()
        # Read value
        start = stream.tell()
        self.value.read(stream)
        end = stream.tell()

        # Verify length
        if include_header:
            if end - start != length:
                raise DeserializeError.invalid_value_size(length, end - start, start)

    def write(
        self,
        stream: BinaryIO,
        include_header=True,
    ) -> int:
        # create temporary buffer for body
        temp_body_buffer = BytesIO()
        body_bytes = self.value.write(temp_body_buffer)
        assert body_bytes == len(temp_body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            # Write property type needs to be written by the object
            bytes_written += write_string(stream, "MulticastInlineDelegateProperty")
            bytes_written += write_uint32(stream, body_bytes)
            bytes_written += write_uint32(stream, 0)  # array_index
            # if there were strings, they'd go here
            bytes_written += write_uint8(stream, 0)  # terminator

        # Write enum value
        bytes_written += write_bytes(stream, temp_body_buffer.getvalue())

        return bytes_written
