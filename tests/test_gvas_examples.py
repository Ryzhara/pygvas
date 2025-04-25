"""
Main test file for GVAS functionality
"""

import json
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from typing import override
from pydantic import TypeAdapter

from gvas.gvas_file import GVASFile
from gvas.gvas_utils import ContextScopeTracker
from tests.common.test_utils import (
    get_gvas_file_and_stream,
    get_testfile_path,
)

TEST_FILE_CONFIG = {
    "ASSERT_FAILED": {
        "file": "assert_failed.sav",
        "json": "assert_failed.sav.json",
        "hints": None,
    },
    "COMPONENT8": {
        "file": "component8.sav",
        "json": "component8.sav.json",
        "hints": None,
    },
    "DELEGATE": {
        "file": "delegate.sav",
        "json": "delegate.sav.json",
        "hints": None,
    },
    "ENUM_ARRAY": {
        "file": "enum_array.sav",
        "json": "enum_array.sav.json.zip",
        "hints": None,
    },
    "ISLANDS_OF_INSIGHT": {
        "file": "islands_of_insight.sav",
        "json": "islands_of_insight.sav.json.zip",
        "hints": None,
    },
    "FEATURES_01": {
        "file": "features_01.bin",
        "json": "features_01.bin.json",
        "hints": "features_01.hints.json",
    },
    "OPTIONS": {
        "file": "options.sav",
        "json": "options.sav.json",
        "hints": None,
    },
    "PACKAGE_VERSION_524": {
        "file": "package_version_524.sav",
        "json": "package_version_524.sav.json",
        "hints": None,
    },
    "PACKAGE_VERSION_525": {
        "file": "package_version_525.sav",
        "json": "package_version_525.sav.json",
        "hints": None,
    },
    "PROFILE_0": {
        "file": "profile_0.sav",
        "json": "profile_0.sav.json",
        "hints": None,
    },
    "REGRESSION_01": {
        "file": "regression_01.bin",
        "json": "regression_01.bin.json",
        "hints": None,
    },
    "RO_64BIT_FAV": {
        "file": "ro_64bit_fav.sav",
        "json": "ro_64bit_fav.sav.json",
        "hints": None,
    },
    "SAVESLOT_03": {
        "file": "saveslot_03.sav",
        "json": "saveslot_03.sav.json",
        "hints": None,
    },
    "SLOT1": {
        "file": "slot1.sav",
        "json": "slot1.sav.json",
        "hints": None,
    },
    "SLOT2": {
        "file": "slot2.sav",
        "json": "slot2.sav.json",
        "hints": None,
    },
    "SLOT3": {
        "file": "slot3.sav",
        "json": "slot3.sav.json",
        "hints": None,
    },
    "TEXT_PROPERTY_NOARRAY": {
        "file": "text_property_noarray.bin",
        "json": "text_property_noarray.bin.json",
        "hints": None,
    },
    "TRANSFORM": {
        "file": "transform.sav",
        "json": "transform.sav.json",
        "hints": None,
    },
    "VECTOR2D": {
        "file": "vector2d.sav",
        "json": "vector2d.sav.json",
        "hints": None,
    },
    "PALWORLD_ZLIB": {
        "file": "palworld_zlib.sav",
        "json": "palworld_zlib.sav.json",
        "hints": None,
    },
    "PALWORLD_ZLIB_TWICE": {
        "file": "palworld_zlib_twice.sav",
        "json": "palworld_zlib_twice.sav.json.zip",
        "hints": "palworld_zlib_twice.hints.json",
    },
}


def get_test_file_config(key: str) -> (str, str, str):
    if key not in TEST_FILE_CONFIG.keys():
        raise KeyError()

    config = TEST_FILE_CONFIG[key]
    test_file = get_testfile_path(config["file"])
    json_file = get_testfile_path(config["json"])

    if type(config["hints"]) is str or isinstance(config["hints"], Path):
        hints_file = get_testfile_path(config["hints"])
    elif type(config["hints"]) is dict:
        hints_file = config["hints"]
    else:
        hints_file = {}

    return test_file, json_file, hints_file


class TestGvasExamples(unittest.TestCase):
    """
    Test GVAS file
    * deserialization from binary
    * serialization to binary
    * serialization to JSON
    * deserialization from JSON
    """

    @classmethod
    @override
    def setUpClass(cls) -> None:
        ContextScopeTracker.set_inside_unit_tests()
        ContextScopeTracker.set_deserialization_hints({})

    @classmethod
    @override
    def setUp(self):
        ContextScopeTracker.set_inside_unit_tests()
        ContextScopeTracker.set_deserialization_hints({})

    def perform_gvas_deserialization_test(
        self, test_key: str, should_be_equal: bool = True
    ):
        """
        Read GVAS file from storage. compare the serialized version to original binary.
        """
        test_file, json_file, hints_file = get_test_file_config(test_key)
        gvas_file, original_file_stream = get_gvas_file_and_stream(
            test_file, deserialization_hints=hints_file
        )

        serialized_stream = BytesIO()
        gvas_file.write(serialized_stream)

        serialized_stream.seek(0)
        original_file_stream.seek(0)

        if should_be_equal:
            self.assertEqual(
                original_file_stream.getvalue(),
                serialized_stream.getvalue(),
                f"GVAS deserialization failed for {test_key}",
            )
        else:
            self.assertNotEqual(
                original_file_stream.getvalue(),
                serialized_stream.getvalue(),
                f"GVAS deserialization failed for {test_key}",
            )

    @staticmethod
    def get_possibly_zipped_json_content(json_file):
        # load test file. check if it was zipped because size
        if zipfile.is_zipfile(json_file):
            json_file_without_ext = json_file
            if Path(json_file).suffix.lower() == ".zip":
                json_file_without_ext = Path(json_file).stem
            with zipfile.ZipFile(json_file, "r") as zf:
                with zf.open(json_file_without_ext) as f:
                    expected_json = json.load(f)
        else:
            with open(json_file, "r") as f:
                expected_json = json.load(f)

        return expected_json

    def perform_json_serialization_test(self, test_key: str):
        """
        Read GVAS file from storage and serialize into JSON. Compare that to the expected JSON.
        """
        test_file, json_file, hints_file = get_test_file_config(test_key)

        # gvas_file, original_file_stream = GVASFile.read_gvas_file(test_file)

        gvas_file, original_file_stream = get_gvas_file_and_stream(
            test_file, deserialization_hints=hints_file
        )
        # serialize to json
        gvas_adaptor = TypeAdapter(GVASFile)
        gvas_file_dict = gvas_adaptor.dump_python(gvas_file, exclude_none=True)
        serialized_json_str = json.dumps(gvas_file_dict)

        expected_json = self.get_possibly_zipped_json_content(json_file)

        # normalize spacing, just in case
        expected_json_str = json.dumps(expected_json)

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

        exemplar_json = self.get_possibly_zipped_json_content(json_file)

        # deserialize the JSON to a GVAS file
        deserialized_gvas = GVASFile.deserialize_json(exemplar_json)

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

    def do_all_tests(self, test_key: str):
        self.perform_gvas_deserialization_test(test_key)
        self.perform_json_serialization_test(test_key)
        self.perform_json_deserialization_test(test_key)

    def test_005_assert_failed(self):
        self.do_all_tests("ASSERT_FAILED")

    def test_010_component8(self):
        self.do_all_tests("COMPONENT8")

    def test_030_delegate(self):
        self.do_all_tests("DELEGATE")

    def test_040_enum_array(self):
        self.do_all_tests("ENUM_ARRAY")

    def test_050_options(self):
        self.do_all_tests("OPTIONS")

    def test_060_package_version_524(self):
        self.do_all_tests("PACKAGE_VERSION_524")

    def test_065_package_version_525(self):
        self.do_all_tests("PACKAGE_VERSION_525")

    def test_070_profile_0(self):
        """Note: this python implementation does not need deserialization_hints."""
        self.do_all_tests("PROFILE_0")

    def test_080_ro_64bit_fav(self):
        self.do_all_tests("RO_64BIT_FAV")

    def test_090_saveslot03(self):
        """Note: this python implementation does not need deserialization_hints."""
        self.do_all_tests("SAVESLOT_03")

    def test_100_slot1(self):
        self.do_all_tests("SLOT1")

    def test_110_slot2(self):
        self.do_all_tests("SLOT2")

    def test_120_slot3(self):
        self.do_all_tests("SLOT3")

    def test_130_transform(self):
        self.do_all_tests("TRANSFORM")

    def test_140_vector2d(self):
        self.do_all_tests("VECTOR2D")

    def test_200_regression_01(self):
        """This is a BIN file that needs no deserialization_hints."""
        self.do_all_tests("REGRESSION_01")

    def test_210_text_property_noarray(self):
        """This is a BIN file with an ERROR and needs no deserialization_hints."""
        # This file is invalid because it contains duplicate StructProperty members.
        # Duplicates occur around byte # 114,712 -- according to the internets, that's not INVALID:
        #       StructProperty["TrackedQuestsNames"] = NameProperty(value="QU91_InvestigateTower_B2")
        # Deserialization overwrites the first instance and only serializes it back out once.
        self.perform_gvas_deserialization_test(
            "TEXT_PROPERTY_NOARRAY", should_be_equal=False
        )

    def test_220_features_01(self):
        """This is a BIN file that needs deserialization_hints."""
        self.do_all_tests("FEATURES_01")

    def test_300_palworld_zlib(self):
        self.do_all_tests("PALWORLD_ZLIB")

    def test_310_palworld_zlib_twice(self):
        self.do_all_tests("PALWORLD_ZLIB_TWICE")

    def test_320_enum_array(self):
        self.do_all_tests("ISLANDS_OF_INSIGHT")


if __name__ == "__main__":
    unittest.main()
