from typing import Optional
from enum import IntEnum, auto
from dataclasses import dataclass
from unittest import case

from .property_base import PropertyTrait
from ..utils import *


class DateTimeStyle(IntEnum):
    # Default
    Default = 0
    # Short
    Short = auto()
    # Medium
    Medium = auto()
    # Long
    Long = auto()
    # Full
    Full = auto()


class TransformType(IntEnum):
    # To lowercase
    ToLower = 0
    # To uppercase
    ToUpper = auto()


class RoundingMode(IntEnum):
    # Rounds to the nearest place, equidistant ties go to the value which is closest to an even value: 1.5 becomes 2, 0.5 becomes 0
    HalfToEven = 0
    # Rounds to nearest place, equidistant ties go to the value which is further from zero: -0.5 becomes -1.0, 0.5 becomes 1.0
    HalfFromZero = auto()
    # Rounds to nearest place, equidistant ties go to the value which is closer to zero: -0.5 becomes 0, 0.5 becomes 0.
    HalfToZero = auto()
    # Rounds to the value which is further from zero, "larger" in absolute value: 0.1 becomes 1, -0.1 becomes -1
    FromZero = auto()
    # Rounds to the value which is closer to zero, "smaller" in absolute value: 0.1 becomes 0, -0.1 becomes 0
    ToZero = auto()
    # Rounds to the value which is more negative: 0.1 becomes 0, -0.1 becomes -1
    ToNegativeInfinity = auto()
    # Rounds to the value which is more positive: 0.1 becomes 1, -0.1 becomes 0
    ToPositiveInfinity = auto()

    @classmethod
    def read_type(cls, stream: BinaryIO) -> "RoundingMode":
        rounding_mode: int = read_int8(stream)
        try:
            rounding_mode: RoundingMode = RoundingMode(rounding_mode)
        except ValueError:
            raise ValueError(f"Unimplemented RoundingMode type {rounding_mode}")
        return rounding_mode


# Number formatting options
class NumberFormattingOptions:
    # Always include sign
    always_include_sign: bool
    # Use grouping
    use_grouping: bool
    # Rounding mode
    # [cfg_attr(feature = "serde", serde(flatten))]
    rounding_mode: RoundingMode
    # Minimum integral digits
    minimum_integral_digits: int
    # Maximum integral digits
    maximum_integral_digits: int
    # Minimum fractional digits
    minimum_fractional_digits: int
    # Maximum fractional digits
    maximum_fractional_digits: int

    def read(self, stream: BinaryIO):
        self.always_include_sign = read_bool32bit(stream)
        self.use_grouping = read_bool32bit(stream)
        self.rounding_mode = RoundingMode.read_type(stream)
        self.minimum_integral_digits = read_int32(stream)
        self.maximum_integral_digits = read_int32(stream)
        self.minimum_fractional_digits = read_int32(stream)
        self.maximum_fractional_digits = read_int32(stream)

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_uint32(stream, 1 if self.always_include_sign else 0)
        bytes_written += write_uint32(stream, 1 if self.use_grouping else 0)
        bytes_written += write_uint32(stream, 1 if self.rounding_mode else 0)
        bytes_written += write_int32(stream, self.minimum_integral_digits)
        bytes_written += write_int32(stream, self.maximum_integral_digits)
        bytes_written += write_int32(stream, self.minimum_fractional_digits)
        bytes_written += write_int32(stream, self.maximum_fractional_digits)
        return bytes_written


class FormatArgumentValue(IntEnum):
    # Integer
    Int = 0
    # Unsigned integer
    UInt = auto()
    # Float
    Float = auto()
    # Double
    Double = auto()
    # FText
    Text = auto()
    # 64-bit integer
    Int64 = auto()
    # 64-bit unsigned integer
    UInt64 = auto()

    @classmethod
    def read_type(cls, stream: BinaryIO):
        format_argument_type = read_int8(stream)
        try:
            format_argument_type = FormatArgumentValue(format_argument_type)
        except ValueError:
            raise ValueError(
                f"Unimplemented FormatArgumentValue type {format_argument_type}"
            )
        return format_argument_type

    @classmethod
    def read(cls, stream: BinaryIO):
        format_argument_type = cls.read_type(stream)
        supports_64bit = SerializationTools.supports_version(
            FUE5ReleaseStreamObjectVersion.TextFormatArgumentData64bitSupport
        )

        match format_argument_type:
            case FormatArgumentValue.Int:
                return read_int64(stream) if supports_64bit else read_int32(stream)

            case FormatArgumentValue.UInt:
                return read_uint64(stream) if supports_64bit else read_uint32(stream)

            case FormatArgumentValue.Float:
                return read_float(stream)

            case FormatArgumentValue.Double:
                return read_double(stream)

            case FormatArgumentValue.Text:
                ftext = FText()
                ftext.read(stream)
                return ftext

            case FormatArgumentValue.Int64:
                return read_int64(stream)

            case FormatArgumentValue.UInt64:
                return read_uint64(stream)

            case FormatArgumentValue.Gender:
                raise NotImplementedError()


class TextHistoryType(IntEnum):
    # None
    # [default]
    NoType = -1
    # Base
    Base = 0
    # Named format
    NamedFormat = auto()
    # Ordered format
    OrderedFormat = auto()
    # Argument format
    ArgumentFormat = auto()
    # As number
    AsNumber = auto()
    # As percentage
    AsPercent = auto()
    # As currency
    AsCurrency = auto()
    # As date
    AsDate = auto()
    # As time
    AsTime = auto()
    # As datetime
    AsDateTime = auto()
    # Transform
    Transform = auto()
    # String table entry
    StringTableEntry = auto()
    # Text generator
    TextGenerator = auto()
    # Uncertain, Back 4 Blood specific serialization
    RawText = auto()

    @classmethod
    def read_type(cls, stream: BinaryIO):
        history_type = read_int8(stream)
        try:
            history_type = TextHistoryType(history_type)
        except ValueError:
            raise ValueError(f"Unimplemented FTextHistory type {history_type}")
        return history_type


class FTextHistory:
    @classmethod
    def read(cls, stream: BinaryIO):

        result = {"history_type": TextHistoryType.read_type(stream)}

        match result["history_type"]:
            case TextHistoryType.NoType:
                if SerializationTools.supports_version(
                    FEditorObjectVersion.CultureInvariantTextSerializationKeyStability
                ):
                    has_culture_invariant_string = read_bool32bit
                    result.update({"culture_invariant_string": read_string(stream)})
                    return result

            case TextHistoryType.Base:
                result.update(
                    {
                        "namespace": read_string(stream),
                        "key": read_string(stream),
                        "source_string": read_string(stream),
                    }
                )
                return result

            case TextHistoryType.NamedFormat:
                source_format = FText()
                source_format.read(stream)
                argument_count = read_int32(stream)
                arguments: dict[str, Any] = {}
                for _ in range(argument_count):
                    key = read_string(stream)
                    value = FormatArgumentValue.read(stream)
                    arguments[key] = value
                return {"source_format": source_format, "arguments": arguments}

            case TextHistoryType.OrderedFormat:
                source_format = FText()
                source_format.read(stream)
                argument_count = read_int32(stream)
                arguments: list = []
                for _ in range(argument_count):
                    arguments.append(FormatArgumentValue.read(stream))
                return {"source_format": source_format, "arguments": arguments}

            # other than type, this is identical to NamedFormat :/
            case TextHistoryType.ArgumentFormat:
                source_format = FText()
                source_format.read(stream)
                argument_count = read_int32(stream)
                arguments: dict[str, Any] = {}
                for _ in range(argument_count):
                    key = read_string(stream)
                    value = FormatArgumentValue.read(stream)
                    arguments[key] = value
                return {"source_format": source_format, "arguments": arguments}

            case TextHistoryType.AsNumber:
                source_value = FormatArgumentValue.read(stream)
                has_format_options = read_bool32bit(stream)
                format_options = None
                if has_format_options:
                    format_options = NumberFormattingOptions()
                    format_options.read(stream)
                target_culture = read_string(stream)
                return {
                    "source_value": source_value,
                    "format_options": format_options,
                    "target_culture": target_culture,
                }

            case TextHistoryType.AsPercent:
                pass

            case TextHistoryType.AsCurrency:
                pass

            case TextHistoryType.AsDate:
                pass

            case TextHistoryType.AsTime:
                pass

            case TextHistoryType.AsDateTime:
                pass

            case TextHistoryType.Transform:
                pass

            case TextHistoryType.StringTableEntry:
                pass

            case TextHistoryType.TextGenerator:
                pass

            case TextHistoryType.RawText:
                pass


class FText:
    flags: int = 0
    history: FTextHistory = None

    def read(self, stream: BinaryIO):
        self.flags = read_uint32(stream)
        self.history = FTextHistory.read(stream)


@dataclass
class TextProperty(PropertyTrait):
    """A property that holds FText data"""

    type: str = "TextProperty"
    actual_property_count: int = 0  # for correctly writing object during hack
    flags: int = 0
    byte_data: Optional[bytes] = None  # just scarf the bytes

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read text from stream"""
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
