import unittest
from io import BytesIO
from typing import Union, Callable

from typing_extensions import override

from pygvas.engine_tools import EngineVersionTool
from pygvas.gvas_utils import (
    MagicConstants,
    guid_to_str,
    datetime_to_str,
    timespan_to_str,
    ContextScopeTracker,
    UnitTestGlobals,
)

from pygvas.properties.standard_structs import (
    DateTimeStruct,
    GuidStruct,
    IntPointStruct,
    LinearColorStruct,
    QuatStruct,
    RotatorStruct,
    TimespanStruct,
    VectorStruct,
    Vector2DStruct,
    ByteBlobStruct,
    STANDARD_STRUCT_UNION,
    StandardStructTrait,
)


class TestTextPropertyTypes(unittest.TestCase):
    fn_storage: Callable = None

    @classmethod
    @override
    def setUpClass(cls) -> None:
        UnitTestGlobals.set_inside_unit_tests()
        ContextScopeTracker.set_deserialization_hints({})

    def write_and_read_standard_type(
        self,
        test_value: STANDARD_STRUCT_UNION,
        deserializer: STANDARD_STRUCT_UNION,
        supports_version: bool,
    ) -> None:
        fn_restore = EngineVersionTool.supports_version
        try:
            EngineVersionTool.supports_version = lambda x: supports_version
            # object is initialized. We only do testing for serialize and deserialize and compare
            write_buffer = BytesIO()
            _bytes_written = test_value.write(write_buffer)
            write_buffer.seek(0)

            # only one object type does not return themselves, but have to handle that
            deserializer.read(write_buffer)
        except Exception:
            raise
        finally:
            EngineVersionTool.supports_version = fn_restore

    def perform_roundtrip_standard_type_roundtrip_test(
        self,
        test_value: STANDARD_STRUCT_UNION,
        deserializer: STANDARD_STRUCT_UNION,
        supports_version: bool,
        msg: str,
    ):

        # have to do this, as construction occurs after this by parent
        self.write_and_read_standard_type(test_value, deserializer, supports_version)
        self.assertEqual(test_value, deserializer, msg)

    def test_00_test_duck_typing_supports_version(self):
        class DuckClass(StandardStructTrait):
            expected_value: bool = None

            def read(self, stream: BytesIO) -> None:
                if (
                    self.expected_value is None
                    or self.expected_value != self.uses_lwc()
                ):
                    raise ValueError(
                        "Duck type failed {self.expected_value=} and {self.uses_lwc()=}"
                    )

            def write(self, stream: BytesIO) -> int:
                if (
                    self.expected_value is None
                    or self.expected_value != self.uses_lwc()
                ):
                    raise ValueError(
                        "Duck type failed {self.expected_value=} and {self.uses_lwc()=}"
                    )
                return 0

        fn_restore = EngineVersionTool.supports_version
        try:
            for supports_version in [True, False]:
                duck_class = DuckClass()
                EngineVersionTool.supports_version = lambda x: supports_version
                duck_class.expected_value = supports_version

                _write_buffer = BytesIO()
                _bytes_written = duck_class.write(_write_buffer)
                _write_buffer.seek(0)

                duck_class.read(_write_buffer)
        except Exception:
            raise
        finally:
            EngineVersionTool.supports_version = fn_restore

    def test_10_datetime_property(self):
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        self.perform_roundtrip_standard_type_roundtrip_test(
            DateTimeStruct(datetime=ticks, comment=datetime_to_str(ticks)),
            DateTimeStruct(),
            supports_version=False,
            msg=f"Testing standard type DateTimeStruct",
        )

    def test_20_guid_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            GuidStruct(guid=guid_to_str(MagicConstants.ZERO_GUID)),
            GuidStruct(),
            supports_version=False,
            msg=f"Testing standard type GUIDProperty",
        )

    def test_30_int_point_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            IntPointStruct(x=3, y=-3),
            IntPointStruct(),
            supports_version=False,
            msg=f"Testing standard type IntPointStruct",
        )

    # this one will likely have the double/float issue because we're using doubles internally
    def test_40_linear_color_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            LinearColorStruct(a=1.0, b=1.0, g=1.0, r=1.0),
            LinearColorStruct(),
            supports_version=False,
            msg=f"Testing standard type LinearColorStruct",
        )

    # this one will likely have the double/float issue because we're using doubles internally
    def test_50_quat_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            QuatStruct(x=1.0, y=1.0, z=1.0, w=1.0),
            QuatStruct(),
            supports_version=False,
            msg=f"Testing standard type QuatStruct",
        )

    def test_60_rotator_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            RotatorStruct(pitch=1.0, yaw=1.0, roll=1.0),
            RotatorStruct(),
            supports_version=False,
            msg=f"Testing standard type RotatorStruct (float)",
        )

    def test_61_rotator_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            RotatorStruct(pitch=1.0, yaw=1.0, roll=1.0),
            RotatorStruct(),
            supports_version=True,
            msg=f"Testing standard type RotatorStruct (double)",
        )

    def test_70_timespan_property(self):
        ticks = 500000000000000000  # '09/06/1585 16:53:20.000000'
        self.perform_roundtrip_standard_type_roundtrip_test(
            TimespanStruct(timespan=ticks, comment=timespan_to_str(ticks)),
            TimespanStruct(),
            supports_version=False,
            msg=f"Testing standard type TimespanStruct",
        )

    def test_80_vector2d_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            Vector2DStruct(x=1.0, y=1.0),
            Vector2DStruct(),
            supports_version=False,
            msg=f"Testing standard type Vector2DStruct",
        )

    def test_81_vector2d_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            Vector2DStruct(x=1.0, y=1.0),
            Vector2DStruct(),
            supports_version=True,
            msg=f"Testing standard type Vector2DStruct",
        )

    def test_80_vector_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            VectorStruct(x=1.0, y=1.0, z=1.0),
            VectorStruct(),
            supports_version=False,
            msg=f"Testing standard type VectorStruct",
        )

    def test_81_vector_property(self):
        self.perform_roundtrip_standard_type_roundtrip_test(
            VectorStruct(x=3.14159, y=3.14159, z=3.14159),
            VectorStruct(),
            supports_version=True,
            msg=f"Testing standard type VectorStruct",
        )

    def test_90_byte_blob_property(self):
        test_blob_list = ["", "0123456789abcdef"]
        for byte_blob in test_blob_list:
            self.assertEqual(
                len(byte_blob) % 2,
                0,
                "Test string for byte_blob must have an even number of characters.",
            )
            hint_context_restore = ContextScopeTracker.get_hint_context()
            ContextScopeTracker.set_hint_context({"byte_count": len(byte_blob)})
            try:
                self.perform_roundtrip_standard_type_roundtrip_test(
                    ByteBlobStruct(byte_blob=byte_blob),
                    ByteBlobStruct(),
                    supports_version=False,
                    msg=f"Testing standard type ByteBlobStruct",
                )
            finally:
                ContextScopeTracker.set_hint_context(hint_context_restore)
