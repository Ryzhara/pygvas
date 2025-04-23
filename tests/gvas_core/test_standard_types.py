import unittest
from io import BytesIO
from typing import Union, Callable

from typing_extensions import override

from gvas.engine_tools import SerializationTools
from gvas.gvas_utils import ZERO_GUID, guid_to_str, datetime_to_str, timespan_to_str

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
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        self.perform_roundtrip_standard_type_roundtrip_test(
            DateTimeProperty(datetime=ticks, comment=datetime_to_str(ticks)),
            DateTimeProperty(),
            supports_version=False,
            msg=f"Testing standard type DateTimeProperty",
        )

    def test_20_guid_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            GuidProperty(guid=guid_to_str(ZERO_GUID)),
            GuidProperty(),
            supports_version=False,
            msg=f"Testing standard type GUIDProperty",
        )

    def test_30_int_point_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            IntPointProperty(x=3, y=-3),
            IntPointProperty(),
            supports_version=False,
            msg=f"Testing standard type IntPointProperty",
        )

    # this one will likely have the double/float issue because we're using doubles internally
    def test_40_linear_color_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            LinearColorProperty(a=1.0, b=1.0, g=1.0, r=1.0),
            LinearColorProperty(),
            supports_version=False,
            msg=f"Testing standard type LinearColorProperty",
        )

    # this one will likely have the double/float issue because we're using doubles internally
    def test_50_quat_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            QuatProperty(x=1.0, y=1.0, z=1.0, w=1.0),
            QuatProperty(),
            supports_version=False,
            msg=f"Testing standard type QuatProperty",
        )

    def test_60_rotator_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            RotatorProperty(is_double=False, pitch=1.0, yaw=1.0, roll=1.0),
            RotatorProperty(is_double=False),
            supports_version=False,
            msg=f"Testing standard type RotatorProperty (float)",
        )

    def test_61_rotator_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            RotatorProperty(is_double=True, pitch=1.0, yaw=1.0, roll=1.0),
            RotatorProperty(is_double=True),
            supports_version=True,
            msg=f"Testing standard type RotatorProperty (double)",
        )

    def test_70_timespan_property(self):
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        self.perform_roundtrip_standard_type_roundtrip_test(
            TimespanProperty(timespan=ticks, comment=timespan_to_str(ticks)),
            TimespanProperty(),
            supports_version=False,
            msg=f"Testing standard type TimespanProperty",
        )

    def test_80_vector2d_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            Vector2DProperty(is_double=False, x=1.0, y=1.0),
            Vector2DProperty(is_double=False),
            supports_version=False,
            msg=f"Testing standard type Vector2DProperty",
        )

    def test_81_vector2d_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            Vector2DProperty(is_double=True, x=1.0, y=1.0),
            Vector2DProperty(is_double=True),
            supports_version=True,
            msg=f"Testing standard type Vector2DProperty",
        )

    def test_80_vector_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            VectorProperty(is_double=False, x=1.0, y=1.0, z=1.0),
            VectorProperty(is_double=False),
            supports_version=False,
            msg=f"Testing standard type VectorProperty",
        )

    def test_81_vector_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            VectorProperty(is_double=True, x=3.14159, y=3.14159, z=3.14159),
            VectorProperty(is_double=True),
            supports_version=True,
            msg=f"Testing standard type VectorProperty",
        )

    def test_90_ensure_support_version_works(self):
        fn_restore = SerializationTools.supports_version
        try:
            SerializationTools.supports_version = lambda x: True

            vector = VectorProperty.new()
            self.assertTrue(vector.is_double)

            quat = QuatProperty.new()
            self.assertTrue(quat.is_double)

            rotator = RotatorProperty.new()
            self.assertTrue(rotator.is_double)

            SerializationTools.supports_version = lambda x: False

            vector = VectorProperty.new()
            self.assertFalse(vector.is_double)

            quat = QuatProperty.new()
            self.assertFalse(quat.is_double)

            rotator = RotatorProperty.new()
            self.assertFalse(rotator.is_double)

        except Exception:
            raise
        finally:
            SerializationTools.supports_version = fn_restore
