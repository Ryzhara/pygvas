"""
Common test utilities for GVAS tests
"""

import os
import unittest
from io import BytesIO
from typing import Dict, Optional

from gvas.gvas_file import GVASFile
from gvas.game_version import GameVersion

# Constants for test file paths
RESOURCES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "resources",
)
ASSERT_FAILED_PATH = os.path.join(RESOURCES_DIR, "assert_failed.sav")
COMPONENT8_PATH = os.path.join(RESOURCES_DIR, "component8.sav")
DELEGATE_PATH = os.path.join(RESOURCES_DIR, "delegate.sav")
ENUM_ARRAY_PATH = os.path.join(RESOURCES_DIR, "enum_array.sav")
FEATURES_01_PATH = os.path.join(RESOURCES_DIR, "features_01.sav")
OPTIONS_PATH = os.path.join(RESOURCES_DIR, "options.sav")
PACKAGE_VERSION_524_PATH = os.path.join(RESOURCES_DIR, "package_version_524.sav")
PALWORLD_ZLIB_PATH = os.path.join(RESOURCES_DIR, "palworld_zlib.sav")
PALWORLD_ZLIB_TWICE_PATH = os.path.join(RESOURCES_DIR, "palworld_zlib_twice.sav")
PROFILE_0_PATH = os.path.join(RESOURCES_DIR, "profile_0.sav")
REGRESSION_01_PATH = os.path.join(RESOURCES_DIR, "regression_01.sav")
RO_64BIT_FAV_PATH = os.path.join(RESOURCES_DIR, "ro_64bit_fav.sav")
SAVESLOT_03_PATH = os.path.join(RESOURCES_DIR, "saveslot_03.sav")
SLOT1_PATH = os.path.join(RESOURCES_DIR, "slot1.sav")
SLOT2_PATH = os.path.join(RESOURCES_DIR, "slot2.sav")
SLOT3_PATH = os.path.join(RESOURCES_DIR, "slot3.sav")
TEXT_PROPERTY_NOARRAY = os.path.join(RESOURCES_DIR, "text_property_noarray.sav")
TRANSFORM_PATH = os.path.join(RESOURCES_DIR, "transform.sav")
VECTOR2D_PATH = os.path.join(RESOURCES_DIR, "vector2d.sav")


def test_gvas_file(path: str) -> GVASFile:
    """
    Test loading and saving a GVAS file with default settings

    Args:
        path: Path to the GVAS file

    Returns:
        The loaded GVASFile object
    """
    return test_gvas_file_with_hints(path, GameVersion.DEFAULT, {})


def test_gvas_file_with_hints(
    path: str, game_version: GameVersion, hints: Dict[str, str]
) -> GVASFile:
    """
    Test loading and saving a GVAS file with custom settings

    Args:
        path: Path to the GVAS file
        game_version: The game version to use for parsing
        hints: Type hints for property paths

    Returns:
        The loaded GVASFile object
    """
    # Read the file into a BytesIO
    with open(path, "rb") as f:
        data = f.read()

    # Convert the BytesIO to a GVASFile
    stream = BytesIO(data)
    file = GVASFile.read_with_hints(stream, game_version, hints)

    # Convert the GVASFile back to a BytesIO
    writer = BytesIO()
    file.write(writer)

    # Compare the two BytesIOs if not using compression
    if file.deserialized_game_version == GameVersion.DEFAULT:
        assert data == writer.getvalue(), "Serialized data doesn't match original"

    # Read the file back in again
    reader = BytesIO(writer.getvalue())
    file2 = GVASFile.read_with_hints(reader, game_version, hints)

    # Compare the two GvasFiles
    assert file == file2, "Deserialized files don't match"

    # Pass the file back for optional verification
    return file
