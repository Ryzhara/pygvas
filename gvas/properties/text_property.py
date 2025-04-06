from typing import Optional
from enum import IntEnum, auto
from dataclasses import dataclass

from .property_base import PropertyTrait, SerializationTools
from ..utils import *


@dataclass
class TextProperty(PropertyTrait):
    """A property that holds FText data"""

    actual_property_count: int = (
        0  # needed for parent property writing this to a stream
    )
    type_name: str = "TextProperty"
    flags: int = 0
    byte_data: Optional[bytes] = None  # just scarf the bytes

    @classmethod
    def new(cls, actual_property_count) -> "TextProperty":
        """Create a new text property"""
        return cls(actual_property_count=actual_property_count)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read text from stream"""
        # body_start, body_end = SerializationTools.get_byte_block_to_be_read()
        text_property_blob = SerializationTools.text_property_blob
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.flags = read_uint32(stream)
            bytes_remaining = text_property_blob - 4
            self.byte_data = read_bytes(stream, bytes_remaining)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write text to stream"""
        length = 4 + len(self.byte_data)
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "TextProperty", length=length
            )

        bytes_written += write_uint32(stream, self.flags)
        bytes_written += write_bytes(stream, self.byte_data)
        return bytes_written


@dataclass
class TextProperty_GENERATED(PropertyTrait):
    """A property that holds text data"""

    value: "FText" = None

    @classmethod
    def new(cls, value: "FText") -> "TextProperty":
        """Create a new text property"""
        return cls(value=value)

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read text from stream"""
        self.value = FText.read(stream, include_header=include_header)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write text to stream"""
        return self.value.write(stream, include_header=include_header)


@dataclass
class FText:
    """Unreal Engine FText structure"""

    flags: int = 0
    history: "FTextHistory" = None

    @classmethod
    def new_none(
        cls, flags: int = 0, culture_invariant_string: Optional[str] = None
    ) -> "FText":
        """Create a new None text"""
        return cls(flags=flags, history=FTextHistory.none(culture_invariant_string))

    @classmethod
    def new_base(
        cls,
        flags: int = 0,
        namespace: Optional[str] = None,
        key: Optional[str] = None,
        source_string: Optional[str] = None,
    ) -> "FText":
        """Create a new base text"""
        return cls(
            flags=flags, history=FTextHistory.base(namespace, key, source_string)
        )

    @classmethod
    def read(cls, stream: BinaryIO) -> "FText":
        """Read FText from stream"""
        flags = read_uint32(stream)
        history = FTextHistory.read(stream)
        return cls(flags=flags, history=history)

    def write(self, stream: BinaryIO) -> int:
        """Write FText to stream"""
        bytes_written = 0
        bytes_written += write_uint32(stream, self.flags)
        bytes_written += 4
        bytes_written += self.history.write(stream)
        return bytes_written


class TextHistoryType(IntEnum):
    """Types of text history"""

    NONE = -1
    BASE = 0
    NAMED_FORMAT = auto()
    ORDERED_FORMAT = auto()
    ARGUMENT_FORMAT = auto()
    AS_NUMBER = auto()
    AS_PERCENT = auto()
    AS_CURRENCY = auto()
    AS_DATE = auto()
    AS_TIME = auto()
    AS_DATETIME = auto()
    TRANSFORM = auto()
    STRING_TABLE_ENTRY = auto()
    TEXT_GENERATOR = auto()
    RAW_TEXT = auto()


@dataclass
class FTextHistory:
    """Text history data"""

    type: TextHistoryType
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}

    @classmethod
    def none(cls, culture_invariant_string: Optional[str] = None) -> "FTextHistory":
        """Create None history"""
        return cls(
            type=TextHistoryType.NONE,
            data={"culture_invariant_string": culture_invariant_string},
        )

    @classmethod
    def base(
        cls, namespace: Optional[str], key: Optional[str], source_string: Optional[str]
    ) -> "FTextHistory":
        """Create Base history"""
        return cls(
            type=TextHistoryType.BASE,
            data={"namespace": namespace, "key": key, "source_string": source_string},
        )

    @classmethod
    def read(cls, stream: BinaryIO) -> "FTextHistory":
        """Read history from stream"""
        history_type = TextHistoryType(struct.unpack("<i", stream.read(4))[0])

        if history_type == TextHistoryType.NONE:
            culture_invariant_string = read_string(stream)
            return cls.none(culture_invariant_string)

        elif history_type == TextHistoryType.BASE:
            namespace = read_string(stream)
            key = read_string(stream)
            source_string = read_string(stream)
            return cls.base(namespace, key, source_string)

        else:
            # Add other history types as needed
            raise DeserializeError.invalid_value(
                f"Unsupported text history type: {history_type}"
            )

    def write(self, stream: BinaryIO) -> int:
        """Write history to stream"""
        bytes_written = 0
        stream.write(struct.pack("<i", self.type))
        bytes_written += 4

        if self.type == TextHistoryType.NONE:
            bytes_written += write_string(
                stream, self.data.get("culture_invariant_string")
            )

        elif self.type == TextHistoryType.BASE:
            bytes_written += write_string(stream, self.data.get("namespace"))
            bytes_written += write_string(stream, self.data.get("key"))
            bytes_written += write_string(stream, self.data.get("source_string"))

        else:
            # Add other history types as needed
            raise ValueError(f"Unsupported text history type: {self.type}")

        return bytes_written
