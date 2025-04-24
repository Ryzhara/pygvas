import enum
from enum import IntEnum, auto
from io import BytesIO
from typing import Self, TypeVar, Type, Annotated

from pydantic import Discriminator

from gvas.properties.numerical_property import *
from gvas.properties.property_base import PropertyTrait
from gvas.engine_tools import (
    EngineVersionTool,
    FEditorObjectVersion,
    FUE5ReleaseStreamObjectVersion,
)
from gvas.gvas_utils import *


EnumT = TypeVar("EnumT", bound=IntEnum)


class IntEnumHelper(enum.IntEnum):
    @staticmethod
    def cast_to_type(enum_class: Type[EnumT], value: int) -> Any:
        try:
            return enum_class(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid member of {enum_class.__name__}")

    @staticmethod
    def read_intenum_type(stream: BinaryIO, enum_class: Type[EnumT]) -> Any:
        enum_value: int = read_int8(stream)
        return IntEnumHelper.cast_to_type(enum_class, enum_value)

    @staticmethod
    def write_intenum_type(stream: BinaryIO, enum_value: IntEnum) -> int:
        return write_int8(stream, enum_value.value)


class DateTimeStyle(IntEnumHelper):
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

    @classmethod
    def read_type(cls, stream: BinaryIO) -> "DateTimeStyle":
        return IntEnumHelper.read_intenum_type(stream, DateTimeStyle)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


class TransformType(IntEnumHelper):
    # To lowercase
    ToLower = 0
    # To uppercase
    ToUpper = auto()

    @classmethod
    def read_type(cls, stream: BinaryIO) -> "TransformType":
        return IntEnumHelper.read_intenum_type(stream, TransformType)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


class RoundingMode(IntEnumHelper):
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
        return IntEnumHelper.read_intenum_type(stream, RoundingMode)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


# Number formatting options
@dataclass
class NumberFormattingOptions:
    # HAD TO INCLUDE DEFAULTS FOR default __init__
    always_include_sign: bool = False
    use_grouping: bool = False
    rounding_mode: str = RoundingMode.HalfToEven.name
    minimum_integral_digits: int = 1
    maximum_integral_digits: int = 324
    minimum_fractional_digits: int = 0
    maximum_fractional_digits: int = 3

    def __post_init__(self):
        if self.rounding_mode is not None:
            pass

    def read(self, stream: BinaryIO) -> Self:
        self.always_include_sign = read_bool32bit(stream)
        self.use_grouping = read_bool32bit(stream)
        self.rounding_mode = RoundingMode.read_type(stream).name
        self.minimum_integral_digits = read_int32(stream)
        self.maximum_integral_digits = read_int32(stream)
        self.minimum_fractional_digits = read_int32(stream)
        self.maximum_fractional_digits = read_int32(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_bool32bit(stream, self.always_include_sign)
        bytes_written += write_bool32bit(stream, self.use_grouping)
        bytes_written += RoundingMode[self.rounding_mode].write_type(stream)
        bytes_written += write_int32(stream, self.minimum_integral_digits)
        bytes_written += write_int32(stream, self.maximum_integral_digits)
        bytes_written += write_int32(stream, self.minimum_fractional_digits)
        bytes_written += write_int32(stream, self.maximum_fractional_digits)
        return bytes_written


class FormatArgumentType(IntEnumHelper):
    # Integer (32 bit in most games, 64 bit in Hogwarts Legacy)
    Int = 0
    # Unsigned integer (32 bit)
    UInt = auto()
    # Floating point number (32 bit)
    Float = auto()
    # Floating point number (64 bit)
    Double = auto()
    # FText
    Text = auto()
    # ?
    Gender = auto()

    @classmethod
    def read_type(cls, stream: BinaryIO) -> "FormatArgumentType":
        return IntEnumHelper.read_intenum_type(stream, FormatArgumentType)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


# Argh. We are impedance matching FormatArgumentType to FormatArgumentValue so
# we can accommodate an implicit type conversion on 64-bit support. :(
class FormatArgumentValue(IntEnumHelper):
    Unknown = -1
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
    def read_type(cls, stream: BinaryIO) -> "FormatArgumentValue":
        return IntEnumHelper.read_intenum_type(stream, FormatArgumentValue)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


class TextPropertyHelper:

    @staticmethod
    def supports_64bit():
        return EngineVersionTool.supports_version(
            FUE5ReleaseStreamObjectVersion.TextFormatArgumentData64bitSupport
        )

    @staticmethod
    def supports_culture_invariance():
        return EngineVersionTool.supports_version(
            FEditorObjectVersion.CultureInvariantTextSerializationKeyStability
        )


# this is actually a factory for all the format argument types listed in the enum
@dataclass
class FormatArgument(TextPropertyHelper):
    type: str = FormatArgumentValue.Unknown.name
    value: Optional[Union[int, float, "FText"]] = None

    def read(self, stream: BinaryIO) -> Self:

        format_argument_type = FormatArgumentType.read_type(stream)

        supports_64bit = self.supports_64bit()

        # Argh. We are impedance matching FormatArgumentType to FormatArgumentValue so
        # we can accommodate an implicit type conversion on 64-bit support. :(
        # We read one type, use a different type internally, then write the original type back out
        match format_argument_type:
            case FormatArgumentType.Int:
                if supports_64bit:
                    self.type = FormatArgumentValue.Int64.name
                    self.value = read_int64(stream)
                else:
                    self.type = FormatArgumentValue.Int.name
                    self.value = read_int32(stream)

            case FormatArgumentType.UInt:
                if supports_64bit:
                    self.type = FormatArgumentValue.UInt64.name
                    self.value = read_uint64(stream)
                else:
                    self.type = FormatArgumentValue.UInt.name
                    self.value = read_uint32(stream)

            case FormatArgumentType.Float:
                self.type = FormatArgumentValue.Float.name
                self.value = read_float(stream)

            case FormatArgumentType.Double:
                self.type = FormatArgumentValue.Double.name
                self.value = read_double(stream)

            case FormatArgumentType.Text:
                self.type = FormatArgumentValue.Text.name
                self.value = FText().read(stream)

            case FormatArgumentType.Gender:
                raise DeserializeError.invalid_value(
                    format_argument_type, stream.tell(), "Gender is not implemented"
                )

            case _:
                raise NotImplementedError()

        return self

    def assert_64bit_support(self, *, expected: bool):
        if expected != self.supports_64bit():
            raise SerializeError.invalid_value(
                f"{self.type} support {'required' if expected else 'prohibited'} with TextFormatArgumentData64bitSupport"
            )

    def write(self, stream: BinaryIO) -> int:
        # Argh. We are impedance matching FormatArgumentType to FormatArgumentValue so
        # we can accommodate an implicit type conversion on 64-bit support. :(
        # We read one type, use a different type internally, then write the original type back out
        bytes_written = 0
        match self.type:
            case FormatArgumentValue.Int.name:
                self.assert_64bit_support(expected=False)
                # *sigh* convert back to other type
                bytes_written += FormatArgumentType.Int.write_type(stream)
                bytes_written += write_int32(stream, self.value)

            case FormatArgumentValue.Int64.name:
                self.assert_64bit_support(expected=True)
                # *sigh* convert back to other type
                bytes_written += FormatArgumentType.Int.write_type(stream)
                bytes_written += write_int64(stream, self.value)

            case FormatArgumentValue.UInt.name:
                self.assert_64bit_support(expected=False)
                # *sigh* convert back to other type
                bytes_written += FormatArgumentType.UInt.write_type(stream)
                bytes_written += write_uint32(stream, self.value)

            case FormatArgumentValue.UInt64.name:
                self.assert_64bit_support(expected=True)
                # *sigh* convert back to other type
                bytes_written += FormatArgumentType.UInt.write_type(stream)
                bytes_written += write_uint64(stream, self.value)

            case FormatArgumentValue.Float.name:
                bytes_written += FormatArgumentType.Float.write_type(stream)
                bytes_written += write_float(stream, self.value)

            case FormatArgumentValue.Double.name:
                bytes_written += FormatArgumentType.Double.write_type(stream)
                bytes_written += write_double(stream, self.value)

            case FormatArgumentValue.Text.name:
                bytes_written += FormatArgumentType.Text.write_type(stream)
                bytes_written += self.value.write(stream)

            case _:
                raise NotImplementedError()
        return bytes_written


class TextHistoryType(IntEnumHelper):
    Empty = -2
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
    def read_type(cls, stream: BinaryIO) -> "TextHistoryType":
        return IntEnumHelper.read_intenum_type(stream, TextHistoryType)

    def write_type(self, stream: BinaryIO) -> int:
        return IntEnumHelper.write_intenum_type(stream, self)


UNREAL_ENGINE_TEXT_PROPERTY_TYPES = Annotated[
    Union[
        "Empty",
        "NoType",
        "Base",
        "NamedFormat",
        "OrderedFormat",
        "ArgumentFormat",
        "AsNumber",
        "AsPercent",
        "AsCurrency",
        "AsDate",
        "AsTime",
        "AsDateTime",
        "Transform",
        "StringTableEntry",
    ],
    Discriminator("type"),
]


@dataclass
class FText:
    flags: int = 0
    history: Optional[UNREAL_ENGINE_TEXT_PROPERTY_TYPES] = None

    def read(self, stream: BinaryIO) -> Self:
        self.flags = read_uint32(stream)
        self.history = FTextHistoryFactory.read(stream)
        return self

    def write(self, stream: BinaryIO):
        bytes_written = 0
        bytes_written += write_uint32(stream, self.flags)
        bytes_written += self.history.write(stream)
        return bytes_written


# Lightweight version of LightWeightDateTime
@dataclass
class LightWeightDateTime:
    ticks: int = 0
    comment: str = None

    def read(self, stream: BinaryIO) -> Self:
        self.ticks = read_uint64(stream)
        self.comment = datetime_to_str(self.ticks)
        return self

    def write(self, stream: BinaryIO):
        return write_uint64(stream, self.ticks)


@dataclass
class Empty(TextPropertyHelper):
    type: Literal[TextHistoryType.Empty.name] = TextHistoryType.Empty.name

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.NoType.write_type(stream)

        if self.supports_culture_invariance():
            bytes_written += write_bool32bit(stream, False)
        return bytes_written


@dataclass
class NoType(TextPropertyHelper):

    type: Literal[TextHistoryType.NoType.name] = TextHistoryType.NoType.name
    culture_invariant_string: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        if self.supports_culture_invariance():
            has_culture_invariant_string = read_bool32bit(stream)
            if has_culture_invariant_string:
                self.culture_invariant_string = read_string(stream)
                return self
            else:
                return Empty()
        else:
            return Empty()

    def write(self, stream: BinaryIO):
        bytes_written = 0
        bytes_written += TextHistoryType.NoType.write_type(stream)

        if self.supports_culture_invariance():
            bytes_written += write_bool32bit(stream, True)
            bytes_written += write_string(stream, self.culture_invariant_string)
        return bytes_written


@dataclass
class Base:
    type: Literal[TextHistoryType.Base.name] = TextHistoryType.Base.name
    namespace: Optional[str] = None
    key: Optional[str] = None
    source_string: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.namespace = read_string(stream)
        self.key = read_string(stream)
        self.source_string = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.Base.write_type(stream)

        bytes_written += write_string(stream, self.namespace)
        bytes_written += write_string(stream, self.key)
        bytes_written += write_string(stream, self.source_string)
        return bytes_written


@dataclass
class NamedFormat:
    type: Literal[TextHistoryType.NamedFormat.name] = TextHistoryType.NamedFormat.name
    source_format: Optional[FText] = None
    arguments: Optional[dict[str, FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_format = FText().read(stream)
        argument_count = read_int32(stream)
        self.arguments: dict = {}
        for _ in range(argument_count):
            key = read_string(stream)
            value = FormatArgument().read(stream)
            self.arguments[key] = value
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.NamedFormat.write_type(stream)

        bytes_written += self.source_format.write(stream)
        bytes_written += write_int32(stream, len(self.arguments))
        for key, value in self.arguments.items():
            bytes_written += write_string(stream, key)
            bytes_written += value.write(stream)
        return bytes_written


@dataclass
class OrderedFormat:
    type: Literal[TextHistoryType.OrderedFormat.name] = (
        TextHistoryType.OrderedFormat.name
    )
    source_format: Optional[FText] = None
    arguments: Optional[list[FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_format = FText().read(stream)
        argument_count = read_int32(stream)
        self.arguments: list = []
        for _ in range(argument_count):
            value = FormatArgument().read(stream)
            self.arguments.append(value)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.OrderedFormat.write_type(stream)

        bytes_written += self.source_format.write(stream)
        bytes_written += write_int32(stream, len(self.arguments))
        for argument in self.arguments:
            bytes_written += argument.write(stream)
        return bytes_written


@dataclass
class ArgumentFormat:
    type: Literal[TextHistoryType.ArgumentFormat.name] = (
        TextHistoryType.ArgumentFormat.name
    )
    source_format: Optional[FText] = None
    arguments: Optional[dict[str, FormatArgument]] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_format = FText().read(stream)
        argument_count = read_int32(stream)
        self.arguments: dict = {}
        for _ in range(argument_count):
            key = read_string(stream)
            value = FormatArgument().read(stream)
            self.arguments[key] = value
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.ArgumentFormat.write_type(stream)

        bytes_written += self.source_format.write(stream)
        bytes_written += write_int32(stream, len(self.arguments))
        for key, value in self.arguments.items():
            bytes_written += write_string(stream, key)
            bytes_written += value.write(stream)
        return bytes_written


@dataclass
class AsNumber:
    type: Literal[TextHistoryType.AsNumber.name] = TextHistoryType.AsNumber.name
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_value = FormatArgument().read(stream)
        has_format_options = read_bool32bit(stream)
        if has_format_options:
            self.format_options = NumberFormattingOptions().read(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsNumber.write_type(stream)

        bytes_written += self.source_value.write(stream)
        bytes_written += write_bool32bit(stream, True if self.format_options else False)
        if self.format_options:
            bytes_written += self.format_options.write(stream)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class AsPercent:
    type: Literal[TextHistoryType.AsPercent.name] = TextHistoryType.AsPercent.name
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_value = FormatArgument().read(stream)
        has_format_options = read_bool32bit(stream)
        if has_format_options:
            self.format_options = NumberFormattingOptions().read(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsPercent.write_type(stream)

        bytes_written += self.source_value.write(stream)
        bytes_written += write_bool32bit(stream, True if self.format_options else False)
        if self.format_options:
            bytes_written += self.format_options.write(stream)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class AsCurrency:
    type: Literal[TextHistoryType.AsCurrency.name] = TextHistoryType.AsCurrency.name
    currency_code: Optional[str] = None
    source_value: Optional[FormatArgument] = None
    format_options: Optional[NumberFormattingOptions] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.currency_code = read_string(stream)
        self.source_value = FormatArgument().read(stream)
        has_format_options = read_bool32bit(stream)
        if has_format_options:
            self.format_options = NumberFormattingOptions().read(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsCurrency.write_type(stream)

        bytes_written += write_string(stream, self.currency_code)
        bytes_written += self.source_value.write(stream)
        bytes_written += write_bool32bit(stream, True if self.format_options else False)
        if self.format_options:
            bytes_written += self.format_options.write(stream)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class AsDate:
    type: Literal[TextHistoryType.AsDate.name] = TextHistoryType.AsDate.name
    date_time: Optional[LightWeightDateTime] = None
    date_style: Optional[DateTimeStyle] = None
    # todo: FTEXT_HISTORY_DATE_TIMEZONE support (needs object version)
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.date_time = LightWeightDateTime().read(stream)
        self.date_style = DateTimeStyle.read_type(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsDate.write_type(stream)

        bytes_written += self.date_time.write(stream)
        bytes_written += self.date_style.write_type(stream)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class AsTime:
    type: Literal[TextHistoryType.AsTime.name] = TextHistoryType.AsTime.name
    source_date_time: Optional[LightWeightDateTime] = None
    time_style: Optional[DateTimeStyle] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_date_time = LightWeightDateTime().read(stream)
        self.time_style = DateTimeStyle.read_type(stream)
        self.time_zone = read_string(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsTime.write_type(stream)

        bytes_written += self.source_date_time.write(stream)
        bytes_written += self.time_style.write_type(stream)
        bytes_written += write_string(stream, self.time_zone)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class AsDateTime:
    type: Literal[TextHistoryType.AsDateTime.name] = TextHistoryType.AsDateTime.name
    source_date_time: Optional[LightWeightDateTime] = None
    date_style: Optional[DateTimeStyle] = None
    time_style: Optional[DateTimeStyle] = None
    time_zone: Optional[str] = None
    target_culture: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_date_time = LightWeightDateTime().read(stream)
        self.date_style = DateTimeStyle.read_type(stream)
        self.time_style = DateTimeStyle.read_type(stream)
        self.time_zone = read_string(stream)
        self.target_culture = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.AsDateTime.write_type(stream)

        bytes_written += self.source_date_time.write(stream)
        bytes_written += self.date_style.write_type(stream)
        bytes_written += self.time_style.write_type(stream)
        bytes_written += write_string(stream, self.time_zone)
        bytes_written += write_string(stream, self.target_culture)
        return bytes_written


@dataclass
class Transform:
    type: Literal[TextHistoryType.Transform.name] = TextHistoryType.Transform.name
    source_text: Optional[FText] = None
    transform_type: Optional[TransformType] = None

    def read(self, stream: BinaryIO) -> Self:
        self.source_text = FText().read(stream)
        self.transform_type = TransformType.read_type(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.Transform.write_type(stream)

        bytes_written += self.source_text.write(stream)
        bytes_written += self.transform_type.write_type(stream)
        return bytes_written


@dataclass
class StringTableEntry:
    type: Literal[TextHistoryType.StringTableEntry.name] = (
        TextHistoryType.StringTableEntry.name
    )
    table_id: Optional[FText] = None
    key: Optional[str] = None

    def read(self, stream: BinaryIO) -> Self:
        self.table_id = FText().read(stream)
        self.key = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += TextHistoryType.StringTableEntry.write_type(stream)

        bytes_written += self.table_id.write(stream)
        bytes_written += write_string(stream, self.key)
        return bytes_written


@dataclass
class FTextHistoryFactory:
    @classmethod
    def read(cls, stream: BinaryIO) -> UNREAL_ENGINE_TEXT_PROPERTY_TYPES:

        text_history_type = TextHistoryType.read_type(stream)

        match text_history_type:
            case TextHistoryType.NoType:
                return NoType().read(stream)

            case TextHistoryType.Base:
                return Base().read(stream)

            case TextHistoryType.NamedFormat:
                return NamedFormat().read(stream)

            case TextHistoryType.OrderedFormat:
                return OrderedFormat().read(stream)

            # other than type, this is identical to NamedFormat :/
            case TextHistoryType.ArgumentFormat:
                return ArgumentFormat().read(stream)

            case TextHistoryType.AsNumber:
                return AsNumber().read(stream)

            case TextHistoryType.AsPercent:
                return AsPercent().read(stream)

            case TextHistoryType.AsCurrency:
                return AsCurrency().read(stream)

            case TextHistoryType.AsDate:
                return AsDate().read(stream)

            case TextHistoryType.AsTime:
                return AsTime().read(stream)

            case TextHistoryType.AsDateTime:
                return AsDateTime().read(stream)

            case TextHistoryType.Transform:
                return Transform().read(stream)

            case TextHistoryType.StringTableEntry:
                return StringTableEntry().read(stream)

            case _:
                raise DeserializeError.invalid_value(
                    text_history_type.value,
                    stream.tell(),
                    f"Read unexpected type {text_history_type}",
                )


@dataclass
class TextProperty(PropertyTrait):
    """A property that holds FText data"""

    type: Literal["TextProperty"] = "TextProperty"
    flags: int = 0
    history: Optional[UNREAL_ENGINE_TEXT_PROPERTY_TYPES] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read text from stream"""
        length = 0
        if include_header:
            length, *_ = read_standard_header(stream)

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            ftext = FText().read(stream)
            self.flags = ftext.flags
            self.history = ftext.history

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write text to stream"""
        body_buffer = BytesIO()
        ftext = FText(flags=self.flags, history=self.history)
        # ftext.flags = self.flags
        # ftext.history = self.history
        ftext.write(body_buffer)

        length = len(body_buffer.getvalue())
        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream, "TextProperty", length=length
            )

        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written
