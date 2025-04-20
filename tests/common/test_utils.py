"""
Common test utilities for GVAS tests
"""

import json
import os
from io import BytesIO
from typing import Dict, Optional, Union
from pathlib import Path

from gvas.gvas_file import GVASFile, GameFileFormat
from gvas.gvas_utils import SerializationTools

# Constants for test file paths
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")


def get_testfile_path(testfile_name: Union[str, Path]) -> Path:
    return Path(RESOURCES_DIR, testfile_name).resolve()


def read_gvas_file(
    input_test_file: str,
    *,
    game_file_format: Optional[GameFileFormat] = None,
    hints: Optional[Union[Dict[str, str], str, Path]] = None,
) -> (BytesIO, GVASFile):

    full_testfile_path = get_testfile_path(input_test_file)
    with open(full_testfile_path, "rb") as f:
        test_file_bytes = f.read()

    test_file_stream = BytesIO(test_file_bytes)

    # set up any requested hints
    if type(hints) is None:
        hints = {}

    elif type(hints) == str() or isinstance(hints, Path):
        full_hints_file_path = get_testfile_path(hints)
        with open(full_hints_file_path, "rb") as f:
            hints = json.load(f)

    else:
        assert isinstance(
            hints, dict
        ), f"Hints must be either a dict or a str/Path object to a file."

    SerializationTools.hints = hints

    if game_file_format is not None:
        gvas_test_file: GVASFile = GVASFile.read(
            test_file_stream,
            game_file_format.game_version,
            game_file_format.compression_type,
        )
    else:
        game_file_format = GameFileFormat()
        game_file_format.deserialize_game_version(test_file_stream)
        gvas_test_file: GVASFile = GVASFile.read(
            test_file_stream,
            game_file_format.game_version,
            game_file_format.compression_type,
        )

    # reset to start for comparison purposes
    test_file_stream.seek(0)

    # Pass the file back for optional verification
    return test_file_stream, gvas_test_file
