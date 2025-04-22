import unittest
from io import BytesIO
from typing import Union, Callable

from typing_extensions import override

from gvas.engine_tools import SerializationTools
from gvas.gvas_utils import ZERO_GUID

from gvas.properties.standard_types import (
    DateTimeProperty,
    GuidProperty,
    IntPointProperty,
    LinearColorProperty,
    QuatProperty,
    RotatorProperty,
    TimespanProperty,
    VectorProperty,
    Vector2DProperty,
)

STANDARD_TYPE_UNION = Union[
    DateTimeProperty,
    GuidProperty,
    IntPointProperty,
    LinearColorProperty,
    QuatProperty,
    RotatorProperty,
    TimespanProperty,
    VectorProperty,
    Vector2DProperty,
]


class TestTextPropertyTypes(unittest.TestCase):
    fn_storage: Callable = None

    @classmethod
    @override
    def setUpClass(cls) -> None:
        SerializationTools.set_inside_unit_tests()
        SerializationTools.hints = {}

    def write_and_read_standard_type(
        self,
        test_value: STANDARD_TYPE_UNION,
        deserializer: STANDARD_TYPE_UNION,
        supports_version: bool,
    ) -> None:
        fn_restore = SerializationTools.supports_version
        try:
            SerializationTools.supports_version = lambda x: supports_version
            # object is initialized. We only do testing for serialize and deserialize and compare
            write_buffer = BytesIO()
            _bytes_written = test_value.write(write_buffer)
            write_buffer.seek(0)

            # only one object type does not return themselves, but have to handle that
            deserializer.read(write_buffer)
        except Exception:
            raise
        finally:
            SerializationTools.supports_version = fn_restore

    def perform_roundtrip_standard_type_roundtrip_test(
        self,
        test_value: STANDARD_TYPE_UNION,
        deserializer: STANDARD_TYPE_UNION,
        supports_version: bool,
        msg: str,
    ):

        # have to do this, as construction occurs after this by parent
        self.write_and_read_standard_type(test_value, deserializer, supports_version)
        self.assertEqual(test_value, deserializer, msg)

    def test_10_datetime_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            GuidProperty(guid=ZERO_GUID), GuidProperty(), supports_version=False
        )
