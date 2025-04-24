"""
FieldPath property implementation for GVAS
Python port of field_path_property.rs
"""

from pydantic.dataclasses import dataclass
from io import BytesIO
from typing import Optional, Literal

from .property_base import PropertyTrait
from ..engine_tools import ByteCountValidator
from ..gvas_utils import *


@dataclass
class Delegate:
    type: Literal["Delegate"] = "Delegate"
    object: Optional[str] = None
    function_name: Optional[str] = None

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
    type: Literal["DelegateProperty"] = "DelegateProperty"
    value: Optional[Delegate] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        self.value = Delegate(object="", function_name="")
        # Read value
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value.read(stream)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write enum value to stream"""

        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = self.value.write(body_buffer)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "DelegateProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written


@dataclass
class MulticastScriptDelegate:
    type: Literal["MulticastScriptDelegate"] = "MulticastScriptDelegate"
    delegates: Optional[list[Delegate]] = None

    def read(self, stream: BinaryIO) -> None:
        delegate_count = read_uint32(stream)
        self.delegates = []
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


@dataclass
class MulticastInlineDelegateProperty(PropertyTrait):
    type: Literal["MulticastInlineDelegateProperty"] = "MulticastInlineDelegateProperty"
    value: Optional[MulticastScriptDelegate] = None

    def read(self, stream: BinaryIO, include_header=True) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        self.value = MulticastScriptDelegate()
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value.read(stream)

    def write(self, stream: BinaryIO, include_header=True) -> int:
        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = self.value.write(body_buffer)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "MulticastInlineDelegateProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written


@dataclass
class MulticastSparseDelegateProperty(PropertyTrait):
    type: Literal["MulticastSparseDelegateProperty"] = "MulticastSparseDelegateProperty"
    value: Optional[MulticastScriptDelegate] = None

    def read(self, stream: BinaryIO, include_header=True) -> None:
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        self.value = MulticastScriptDelegate()
        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.value.read(stream)

    def write(self, stream: BinaryIO, include_header=True) -> int:
        # create temporary buffer for body
        body_buffer = BytesIO()
        body_bytes = self.value.write(body_buffer)
        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "MulticastSparseDelegateProperty", length=body_bytes
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
