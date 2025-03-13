"""
Main test file for GVAS functionality
"""

import unittest
from typing import Dict

from gvas.game_version import GameVersion
from gvas.gvas_file import GVASFile

from tests.common.utils import (
    ASSERT_FAILED_PATH,
    COMPONENT8_PATH,
    DELEGATE_PATH,
    ENUM_ARRAY_PATH,
    FEATURES_01_PATH,
    OPTIONS_PATH,
    PACKAGE_VERSION_524_PATH,
    PALWORLD_ZLIB_PATH,
    PALWORLD_ZLIB_TWICE_PATH,
    PROFILE_0_PATH,
    REGRESSION_01_PATH,
    RO_64BIT_FAV_PATH,
    SAVESLOT_03_PATH,
    SLOT1_PATH,
    SLOT2_PATH,
    SLOT3_PATH,
    TEXT_PROPERTY_NOARRAY,
    TRANSFORM_PATH,
    VECTOR2D_PATH,
    test_gvas_file,
    test_gvas_file_with_hints,
)

# Import expected values for comparison
from tests.gvas_tests.delegate import expected as delegate_expected
from tests.gvas_tests.options import expected as options_expected
from tests.gvas_tests.saveslot3 import (
    expected as saveslot3_expected,
    hints as saveslot3_hints,
)
from tests.gvas_tests.slot1 import expected as slot1_expected
from tests.gvas_tests.vector2d import expected as vector2d_expected
from tests.gvas_tests.features import hints as features_hints
from tests.gvas_tests.palworld import hints as palworld_hints
from tests.gvas_tests.profile0 import hints as profile0_hints


class TestGvas(unittest.TestCase):
    """Test GVAS file loading and saving"""

    def test_assert_failed(self):
        """Test loading assert_failed.sav"""
        test_gvas_file(ASSERT_FAILED_PATH)

    def test_component8(self):
        """Test loading component8.sav"""
        test_gvas_file(COMPONENT8_PATH)

    def test_delegate(self):
        """Test loading delegate.sav"""
        file = test_gvas_file(DELEGATE_PATH)
        self.assertEqual(file, delegate_expected())

    def test_enum_array(self):
        """Test loading enum_array.sav"""
        test_gvas_file(ENUM_ARRAY_PATH)

    def test_features_01(self):
        """Test loading features_01.sav"""
        test_gvas_file_with_hints(
            FEATURES_01_PATH, GameVersion.DEFAULT, features_hints()
        )

    def test_options(self):
        """Test loading options.sav"""
        file = test_gvas_file(OPTIONS_PATH)
        self.assertEqual(file, options_expected())

    def test_package_version_524(self):
        """Test loading package_version_524.sav"""
        test_gvas_file(PACKAGE_VERSION_524_PATH)

    def test_palworld_zlib(self):
        """Test loading palworld_zlib.sav"""
        test_gvas_file_with_hints(PALWORLD_ZLIB_PATH, GameVersion.PALWORLD, {})

    def test_palworld_zlib_twice(self):
        """Test loading palworld_zlib_twice.sav"""
        test_gvas_file_with_hints(
            PALWORLD_ZLIB_TWICE_PATH, GameVersion.PALWORLD, palworld_hints()
        )

    def test_profile_0(self):
        """Test loading profile_0.sav"""
        test_gvas_file_with_hints(PROFILE_0_PATH, GameVersion.DEFAULT, profile0_hints())

    def test_regression_01(self):
        """Test loading regression_01.sav"""
        test_gvas_file(REGRESSION_01_PATH)

    def test_ro_64bit_fav(self):
        """Test loading ro_64bit_fav.sav"""
        test_gvas_file(RO_64BIT_FAV_PATH)

    def test_saveslot03(self):
        """Test loading saveslot_03.sav"""
        file = test_gvas_file_with_hints(
            SAVESLOT_03_PATH, GameVersion.DEFAULT, saveslot3_hints()
        )
        self.assertEqual(file, saveslot3_expected())

    def test_slot1(self):
        """Test loading slot1.sav"""
        file = test_gvas_file(SLOT1_PATH)
        self.assertEqual(file, slot1_expected())

    def test_slot2(self):
        """Test loading slot2.sav"""
        test_gvas_file(SLOT2_PATH)

    def test_slot3(self):
        """Test loading slot3.sav"""
        test_gvas_file(SLOT3_PATH)

    def test_text_property_noarray(self):
        """Test loading text_property_noarray.sav"""
        test_gvas_file(TEXT_PROPERTY_NOARRAY)

    def test_transform(self):
        """Test loading transform.sav"""
        test_gvas_file(TRANSFORM_PATH)

    def test_vector2d(self):
        """Test loading vector2d.sav"""
        file = test_gvas_file(VECTOR2D_PATH)
        self.assertEqual(file, vector2d_expected())


if __name__ == "__main__":
    unittest.main()
