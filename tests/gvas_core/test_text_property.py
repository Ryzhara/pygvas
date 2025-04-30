import unittest
from io import BytesIO
from typing import Union, Callable

from typing_extensions import override

from pygvas.engine_tools import EngineVersionTool
from pygvas.error import SerializeError
from pygvas.gvas_utils import datetime_to_str, ContextScopeTracker, UnitTestGlobals
from pygvas.properties.text_property import (
    FText,
    ArgumentFormat,
    FormatArgument,
    LightWeightDateTime,
    NumberFormattingOptions,
    TextHistoryType,
    FormatArgumentValue,
    TransformType,
    Empty,
    NoType,
    Base,
    AsCurrency,
    AsDate,
    AsDateTime,
    AsTime,
    AsNumber,
    AsPercent,
    NamedFormat,
    OrderedFormat,
    Transform,
    StringTableEntry,
    DateTimeStyle,
)

HISTORY_TYPE_UNION = Union[
    Empty,
    NoType,
    Base,
    NamedFormat,
    OrderedFormat,
    ArgumentFormat,
    AsNumber,
    AsPercent,
    AsCurrency,
    AsDate,
    AsTime,
    AsDateTime,
    Transform,
    StringTableEntry,
]


class TestTextPropertyTypes(unittest.TestCase):
    fn_storage: Callable = None

    @classmethod
    @override
    def setUpClass(cls) -> None:
        UnitTestGlobals.set_inside_unit_tests()
        ContextScopeTracker.set_deserialization_hints({})

    def perform_text_format_argument_roundtrip_test(
        self, *, format_argument_value: FormatArgumentValue, supports_64bit: bool
    ):
        # duck type this baby for the test
        fn_restore = EngineVersionTool.supports_version
        try:
            EngineVersionTool.supports_version = lambda x: supports_64bit

            # it is easier to write then read, except for FText
            self.assertEqual(format_argument_value, FormatArgumentValue.Text)

            ftext = FText(flags=0x0F, history=None)
            ftext.history = Empty()
            test_value: FormatArgument = FormatArgument(
                type=format_argument_value.name, value=ftext
            )

            write_buffer = BytesIO()
            test_value.write(write_buffer)
            write_buffer.seek(0)

            deserialized_value = FormatArgument().read(write_buffer)

            self.assertEqual(test_value.type, deserialized_value.type)
            self.assertEqual(test_value.value.flags, deserialized_value.value.flags)
            self.assertEqual(test_value.value.history, deserialized_value.value.history)
        except Exception:
            raise
        finally:
            # get our ducks in a row
            EngineVersionTool.supports_version = fn_restore

    def perform_numerical_format_argument_roundtrip_test(
        self,
        *,
        format_argument_value: FormatArgumentValue,
        supports_64bit: bool,
        numerical_value: Union[float, int],
        places: int = 7,
    ):
        # duck type this baby for the test
        fn_restore = EngineVersionTool.supports_version
        try:
            EngineVersionTool.supports_version = lambda x: supports_64bit

            test_value: FormatArgument = FormatArgument(
                type=format_argument_value.name, value=numerical_value
            )

            write_buffer = BytesIO()
            test_value.write(write_buffer)
            write_buffer.seek(0)

            deserialized_value = FormatArgument().read(write_buffer)

            self.assertEqual(test_value.type, deserialized_value.type)
            if format_argument_value in [
                FormatArgumentValue.Float,
                FormatArgumentValue.Double,
            ]:
                self.assertAlmostEqual(
                    test_value.value,
                    deserialized_value.value,
                    places=places,
                    msg=f"Failure testing type {format_argument_value.name}",
                )
            else:
                self.assertEqual(
                    test_value.value,
                    deserialized_value.value,
                    msg=f"Failure testing type {format_argument_value.name}",
                )

        except Exception:
            raise
        finally:
            # get our ducks in a row
            EngineVersionTool.supports_version = fn_restore

    def write_and_read_text_history(
        self,
        test_value: HISTORY_TYPE_UNION,
        deserializer: HISTORY_TYPE_UNION,
        supports_version: bool,
    ) -> (TextHistoryType, HISTORY_TYPE_UNION):
        fn_restore = EngineVersionTool.supports_version
        try:
            EngineVersionTool.supports_version = lambda x: supports_version
            # object is initialized. We only do testing for serialize and deserialize and compare
            write_buffer = BytesIO()
            _bytes_written = test_value.write(write_buffer)
            write_buffer.seek(0)

            # have to do this, as construction occurs after this by parent
            text_history_type: TextHistoryType = TextHistoryType.read_type(write_buffer)
            # only one object type does not return themselves, but have to handle that
            result = deserializer.read(write_buffer)
        except Exception:
            raise
        finally:
            EngineVersionTool.supports_version = fn_restore

        return text_history_type, result

    def perform_roundtrip_text_history_roundtrip_test(
        self,
        test_value: HISTORY_TYPE_UNION,
        deserializer: HISTORY_TYPE_UNION,
        supports_version: bool,
        msg: str,
    ):

        # have to do this, as construction occurs after this by parent
        text_history_type, deserializer = self.write_and_read_text_history(
            test_value, deserializer, supports_version
        )
        self.assertEqual(test_value.type, text_history_type.name, msg)
        self.assertEqual(test_value, deserializer, msg)

    def test_010_format_value_float_double(self):
        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Float,
            supports_64bit=False,
            numerical_value=3.141592,
            places=7,
        )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Float,
            supports_64bit=True,
            numerical_value=3.14,
            places=2,
        )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Double,
            supports_64bit=False,
            numerical_value=3.141592653,
            places=9,
        )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Double,
            supports_64bit=True,
            numerical_value=3.141592653,
            places=9,
        )

    def test_020_format_value_32bit_integers(self):

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Int,
            supports_64bit=False,
            numerical_value=-314159265,
        )

        with self.assertRaises(SerializeError):
            self.perform_numerical_format_argument_roundtrip_test(
                format_argument_value=FormatArgumentValue.Int,
                supports_64bit=True,
                numerical_value=-314159265,
            )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.UInt,
            supports_64bit=False,
            numerical_value=314159265,
        )

        with self.assertRaises(SerializeError):
            self.perform_numerical_format_argument_roundtrip_test(
                format_argument_value=FormatArgumentValue.UInt,
                supports_64bit=True,
                numerical_value=314159265,
            )

    def test_030_format_value_64bit_integers(self):

        with self.assertRaises(SerializeError):
            self.perform_numerical_format_argument_roundtrip_test(
                format_argument_value=FormatArgumentValue.Int64,
                supports_64bit=False,
                numerical_value=-314159265,
            )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Int64,
            supports_64bit=True,
            numerical_value=-314159265,
        )

        with self.assertRaises(SerializeError):
            self.perform_numerical_format_argument_roundtrip_test(
                format_argument_value=FormatArgumentValue.UInt64,
                supports_64bit=False,
                numerical_value=314159265,
            )

        self.perform_numerical_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.UInt64,
            supports_64bit=True,
            numerical_value=314159265,
        )

    def test_040_format_value_text(self):
        self.perform_text_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Text, supports_64bit=False
        )
        self.perform_text_format_argument_roundtrip_test(
            format_argument_value=FormatArgumentValue.Text, supports_64bit=True
        )

    def test_050_text_history_empty(self):
        # this one is a special case for handling "Empty". The read/write is not symmetric. :/
        test_value = Empty()
        deserializer = NoType()
        # have to do this, as construction occurs after this by parent
        text_history_type, result = self.write_and_read_text_history(
            test_value, deserializer, False
        )
        self.assertEqual(
            text_history_type.name, TextHistoryType.NoType.name, msg=f"Testing Empty"
        )
        self.assertEqual(test_value.type, result.type, msg=f"Testing Empty")
        self.assertEqual(test_value, result, msg=f"Testing Empty")

    def test_060_text_history_notype(self):
        test_value = NoType(culture_invariant_string="culture_invariant_string")
        deserializer = NoType()
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            deserializer,
            supports_version=True,
            msg=f"Testing NoType with culture_invariant_string",
        )

    def test_070_text_history_base(self):
        test_value = Base(
            namespace="namespace", key="keyname", source_string="source_string"
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value, Base(), supports_version=False, msg=f"Testing Base"
        )

    def test_080_text_history_named_format(self):
        test_value = NamedFormat(
            source_format=FText(flags=0x0F, history=Empty()),
            arguments=dict(),
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            NamedFormat(),
            supports_version=False,
            msg=f"Testing NamedFormat",
        )

    def test_090_text_history_ordered_format(self):
        test_value = OrderedFormat(
            source_format=FText(flags=0x0F, history=Empty()),
            arguments=list(),
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            OrderedFormat(),
            supports_version=False,
            msg=f"Testing OrderedFormat",
        )

    def test_100_text_history_argument_format(self):
        test_value = ArgumentFormat(
            source_format=FText(flags=0x0F, history=Empty()),
            arguments=dict(),
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            ArgumentFormat(),
            supports_version=False,
            msg=f"Testing ArgumentFormat",
        )

    def test_110_text_history_as_number(self):
        test_value = AsNumber(
            source_value=FormatArgument(type=FormatArgumentValue.Int.name, value=314),
            format_options=NumberFormattingOptions(),
            target_culture="Enlightened AsNumber",
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            AsNumber(),
            supports_version=False,
            msg=f"Testing AsNumber",
        )

    def test_120_text_history_as_percent(self):
        test_value = AsPercent(
            source_value=FormatArgument(type=FormatArgumentValue.Int.name, value=50),
            format_options=NumberFormattingOptions(),
            target_culture="Enlightened AsPercent",
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            AsPercent(),
            supports_version=False,
            msg=f"Testing AsPercent",
        )

    def test_130_text_history_as_currency(self):
        test_value = AsCurrency(
            currency_code="$",
            source_value=FormatArgument(type=FormatArgumentValue.Int.name, value=50),
            format_options=NumberFormattingOptions(),
            target_culture="Enlightened AsCurrency",
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            AsCurrency(),
            supports_version=False,
            msg=f"Testing AsCurrency",
        )

    def test_140_text_history_as_date(self):
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        test_value = AsDate(
            date_time=LightWeightDateTime(ticks=ticks, comment=datetime_to_str(ticks)),
            date_style=DateTimeStyle.Default,
            target_culture="Enlightened AsDate",
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            AsDate(),
            supports_version=False,
            msg=f"Testing AsDate",
        )

    def test_150_text_history_as_datetime(self):
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        test_value = AsDateTime(
            source_date_time=LightWeightDateTime(
                ticks=ticks, comment=datetime_to_str(ticks)
            ),
            date_style=DateTimeStyle.Default,
            time_style=DateTimeStyle.Default,
            time_zone="CST",
            target_culture="Enlightened AsDateTime",
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            AsDateTime(),
            supports_version=False,
            msg=f"Testing AsDateTime",
        )

    def test_160_text_history_transform(self):
        test_value = Transform(
            source_text=FText(flags=0x07, history=Empty()),
            transform_type=TransformType.ToUpper,
        )
        self.perform_roundtrip_text_history_roundtrip_test(
            test_value,
            Transform(),
            supports_version=False,
            msg=f"Testing Transform",
        )
