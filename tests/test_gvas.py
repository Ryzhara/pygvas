"""
Main test file for GVAS functionality
"""

import json
import unittest
from io import BytesIO

from pydantic import TypeAdapter

from gvas.gvas_file import GVASFile
from tests.common.test_utils import (
    read_gvas_file,
    get_testfile_path,
)

TEST_FILE_CONFIG = {
    "ASSERT_FAILED": {
        "file": "assert_failed.sav",
        "json": "assert_failed.json",
        "hints": None,
    },
    "COMPONENT_8": {"file": "component8.sav", "json": "component8.json", "hints": None},
    "DELEGATE": {"file": "delegate.sav", "json": "delegate.json", "hints": None},
    "ENUM_ARRAY": {"file": "enum_array.sav", "json": "enum_array.json", "hints": None},
    "FEATURES_01": {
        "file": "features_01.sav",
        "json": "features_01.json",
        "hints": None,
    },
    "OPTIONS": {"file": "options.sav", "json": "options.json", "hints": None},
    "PACKAGE_VERSION_524": {
        "file": "package_version_524.sav",
        "json": "package_version_524.json",
        "hints": None,
    },
    "PACKAGE_VERSION_525": {
        "file": "package_version_525.sav",
        "json": "package_version_525.json",
        "hints": None,
    },
    "PROFILE_0": {"file": "profile_0.sav", "json": "profile_0.json", "hints": None},
    "REGRESSION_01": {
        "file": "regression_01.sav",
        "json": "regression_01.json",
        "hints": None,
    },
    "RO_64bit_fav": {
        "file": "ro_64bit_fav.sav",
        "json": "ro_64bit_fav.json",
        "hints": None,
    },
    "SAVESLOT_03": {
        "file": "saveslot_03.sav",
        "json": "saveslot_03.json",
        "hints": None,
    },
    "SLOT1": {"file": "slot1.sav", "json": "slot1.json", "hints": None},
    "SLOT2": {"file": "slot2.sav", "json": "slot2.json", "hints": None},
    "SLOT3": {"file": "slot3.sav", "json": "slot3.json", "hints": None},
    "TEXT_PROPERTY_NOARRAY": {
        "file": "text_property_noarray.sav",
        "json": "text_property_noarray.json",
        "hints": None,
    },
    "TRANSFORM": {"file": "transform.sav", "json": "transform.json", "hints": None},
    "VECTOR2D": {"file": "vector2d.sav", "json": "vector2d.json", "hints": None},
    "PALWORLD_ZLIB": {
        "file": "palworld_zlib.sav",
        "json": "palworld_zlib.json",
        "hints": None,
    },
    "PASLWORLD_ZLIP_TWICE": {
        "file": "palworld_zlib_twice.sav",
        "json": "palworld_zlib_twice.json",
        "hints": "palworld_zlib_twice.hints.json",
    },
}


def get_test_file_config(key: str) -> (str, str, str):
    if key not in TEST_FILE_CONFIG.keys():
        raise KeyError()
    config = TEST_FILE_CONFIG[key]
    test_file = get_testfile_path(config["file"])
    json_file = get_testfile_path(config["json"])
    hints_file = get_testfile_path(config["hints"])
    return test_file, json_file, hints_file


class TestGvas(unittest.TestCase):
    """
    Test GVAS file
    * deserialization from binary
    * serialization to binary
    * serialization to JSON
    * deserialization from JSON
    """

    def perform_gvas_deserialization_test(self, test_key: str):
        """
        Read GVAS file from storage. compare the serialized version to original binary.
        """
        test_file, json_file, hints_file = get_test_file_config(test_key)
        original_file_stream, gvas_file = read_gvas_file(test_file, hints=hints_file)

        serialized_stream = BytesIO()
        gvas_file.write(serialized_stream)
        original_file_stream.seek(0)

        self.assertEqual(
            original_file_stream,
            serialized_stream,
            f"GVAS deserialization failed for {test_key}",
        )

    def perform_json_serialization_test(self, test_key: str):
        """
        Read GVAS file from storage and serialize into JSON. Compare that to the expected JSON.
        """
        test_file, json_file, hints_file = get_test_file_config(test_key)
        original_file_stream, gvas_file = read_gvas_file(test_file, hints=hints_file)
        # serialize to json
        gvas_adaptor = TypeAdapter(GVASFile)
        gvas_file_dict = gvas_adaptor.dump_python(gvas_file, exclude_none=True)
        serialized_json_str = json.dumps(gvas_file_dict, indent=2)
        # load test file
        with open(json_file, "r") as f:
            expected_json = json.load(f)
        # normalize spacing, just in case
        expected_json_str = json.dumps(expected_json, indent=2)

        self.assertEqual(
            serialized_json_str,
            expected_json_str,
            f"JSON serialization failed for {test_key}",
        )

    def perform_json_deserialization_test(self, test_key: str):
        """
        Deserialized expected JSON into a GVAS object, which is then serialized to binary.
        Compare that binary to the original binary.
        """
        test_file, json_file, hints_file = get_test_file_config(test_key)

        with open(json_file, "r") as f:
            expected_json = json.load(f)
        expected_json_str = json.dumps(expected_json)

        # deserialize the JSON to a GVAS file
        gvas_adaptor = TypeAdapter(GVASFile)
        deserialized_gvas = gvas_adaptor.validate_python(expected_json)

        # serialize back to binary
        deserialized_gvas_stream: BytesIO = BytesIO()
        deserialized_gvas.write(deserialized_gvas_stream)
        deserialized_gvas_stream.seek(0)

        with open(test_file, "rb") as f:
            original_bytes = f.read()

        self.assertEqual(
            original_bytes,
            deserialized_gvas_stream.getvalue(),
            f"JSON deserialization failed for {test_key}",
        )

    def test_000_assert_failed(self):
        self.perform_gvas_deserialization_test("ASSERT_FAILED")

    def test_001_assert_failed_json_serialization(self):
        self.perform_json_serialization_test("ASSERT_FAILED")

    def test_002_assert_failed_json_deserialization(self):
        self.perform_json_deserialization_test("ASSERT_FAILED")

    def test_010_component8(self):
        self.perform_gvas_deserialization_test("COMPONENT8")

    def test_011_component8_json_serialization(self):
        self.perform_json_serialization_test("COMPONENT8")

    def test_012_component8_json_deserialization(self):
        self.perform_json_deserialization_test("COMPONENT8")

    def test_030_delegate(self):
        self.perform_gvas_deserialization_test("DELEGATE")

    def test_031_delegate_json_serialization(self):
        self.perform_json_serialization_test("DELEGATE")

    def test_032_delegate_json_deserialization(self):
        self.perform_json_deserialization_test("DELEGATE")

    def test_040_enum_array(self):
        self.perform_gvas_deserialization_test("ENUM_ARRAY")

    def test_041_enum_array_json_serialization(self):
        self.perform_json_serialization_test("ENUM_ARRAY")

    def test_042_enum_array_json_deserialization(self):
        self.perform_json_deserialization_test("ENUM_ARRAY")

    def test_050_options(self):
        self.perform_gvas_deserialization_test("OPTIONS")

    def test_051_options_json_serialization(self):
        self.perform_json_serialization_test("OPTIONS")

    def test_052_options_json_deserialization(self):
        self.perform_json_deserialization_test("OPTIONS")

    def test_600_package_version_524(self):
        self.perform_gvas_deserialization_test("PACKAGE_VERSION_524")

    def test_601_package_version_524_json_serialization(self):
        self.perform_json_serialization_test("PACKAGE_VERSION_524")

    def test_602_package_version_524_json_deserialization(self):
        self.perform_json_deserialization_test("PACKAGE_VERSION_524")

    def test_610_package_version_525(self):
        self.perform_gvas_deserialization_test("PACKAGE_VERSION_525")

    def test_611_package_version_525_json_serialization(self):
        self.perform_json_serialization_test("PACKAGE_VERSION_525")

    def test_612_package_version_525_json_deserialization(self):
        self.perform_json_deserialization_test("PACKAGE_VERSION_525")

    def test_070_profile_0(self):
        """Note: this python implementation does not need hints."""
        self.perform_gvas_deserialization_test("PROFILE_0")

    def test_071_profile_0_json_serialization(self):
        """Note: this python implementation does not need hints."""
        self.perform_json_serialization_test("PROFILE_0")

    def test_072_profile_0_json_deserialization(self):
        """Note: this python implementation does not need hints."""
        self.perform_json_deserialization_test("PROFILE_0")

    def test_080_ro_64bit_fav(self):
        self.perform_gvas_deserialization_test("RO_64BIT_FAV")

    def test_081_ro_64bit_fav_json_serialization(self):
        self.perform_json_serialization_test("RO_64BIT_FAV")

    def test_082_ro_64bit_fav_json_deserialization(self):
        self.perform_json_deserialization_test("RO_64BIT_FAV")

    def test_090_saveslot03(self):
        """Note: this python implementation does not need hints."""
        self.perform_gvas_deserialization_test("SAVESLOT_03")

    def test_091_saveslot03_json_serialization(self):
        """Note: this python implementation does not need hints."""
        self.perform_json_serialization_test("SAVESLOT_03")

    def test_092_saveslot03_json_sdeerialization(self):
        """Note: this python implementation does not need hints."""
        self.perform_json_deserialization_test("SAVESLOT_03")

    def test_100_slot1(self):
        self.perform_gvas_deserialization_test("SLOT1")

    def test_101_slot1_json_serialization(self):
        self.perform_json_serialization_test("SLOT1")

    def test_102_slot1_json_deserialization(self):
        self.perform_json_deserialization_test("SLOT1")

    def test_110_slot2(self):
        self.perform_gvas_deserialization_test("SLOT2")

    def test_111_slot2_json_serialization(self):
        self.perform_json_serialization_test("SLOT2")

    def test_112_slot2_json_deserialization(self):
        self.perform_json_deserialization_test("SLOT2")

    def test_120_slot3(self):
        self.perform_gvas_deserialization_test("SLOT3")

    def test_121_slot3_json_serialization(self):
        self.perform_json_serialization_test("SLOT3")

    def test_122_slot3_json_deserialization(self):
        self.perform_json_deserialization_test("SLOT3")

    def test_130_transform(self):
        self.perform_gvas_deserialization_test("TRANSFORM")

    def test_131_transform_json_serialization(self):
        self.perform_json_serialization_test("TRANSFORM")

    def test_132_transform_json_deserialization(self):
        self.perform_json_deserialization_test("TRANSFORM")

    def test_140_vector2d(self):
        self.perform_gvas_deserialization_test("VECTOR2D")

    def test_141_vector2d_json_serialization(self):
        self.perform_json_serialization_test("VECTOR2D")

    def test_142_vector2d_json_deserialization(self):
        self.perform_json_deserialization_test("VECTOR2D")

    def test_200_regression_01(self):
        """This is a BIN file."""
        self.perform_gvas_deserialization_test("REGRESSION_01")

    def test_201_regression_01_json_serialization(self):
        """This is a BIN file."""
        self.perform_json_serialization_test("REGRESSION_01")

    def test_202_regression_01_json_deserialization(self):
        """This is a BIN file."""
        self.perform_json_deserialization_test("REGRESSION_01")

    def test_210_text_property_noarray(self):
        """This is a BIN file."""
        self.perform_gvas_deserialization_test("TEXT_PROPERTY_NOARRAY")

    def test_211_text_property_noarray_json_serialization(self):
        """This is a BIN file."""
        self.perform_json_serialization_test("TEXT_PROPERTY_NOARRAY")

    def test_212_text_property_noarray_json_deserialization(self):
        """This is a BIN file."""
        self.perform_json_deserialization_test("TEXT_PROPERTY_NOARRAY")

    def test_220_features_01(self):
        """This is a BIN file."""
        self.perform_gvas_deserialization_test("FEATURES_01")

    def test_221_features_01_json_serialization(self):
        """This is a BIN file."""
        self.perform_json_serialization_test("FEATURES_01")

    def test_222_features_01_json_deserialization(self):
        """This is a BIN file."""
        self.perform_json_deserialization_test("FEATURES_01")

    def test_300_palworld_zlib(self):
        self.perform_gvas_deserialization_test("PALWORLD_ZLIB")

    def test_301_palworld_zlib_json_serialization(self):
        self.perform_json_serialization_test("PALWORLD_ZLIB")

    def test_302_palworld_zlib_json_deserialization(self):
        self.perform_json_deserialization_test("PALWORLD_ZLIB")

    def test_310palworld_zlib_twice(self):
        self.perform_gvas_deserialization_test("PALWORLD_ZLIB_TWICE")

    def test_311palworld_zlib_twice_json_serialization(self):
        self.perform_json_serialization_test("PALWORLD_ZLIB_TWICE")

    def test_312palworld_zlib_twice_json_deserialization(self):
        self.perform_json_deserialization_test("PALWORLD_ZLIB_TWICE")


if __name__ == "__main__":
    unittest.main()
