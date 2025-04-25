"""
Common test utilities for GVAS tests
"""

import json
from io import BytesIO
from typing import Optional, Union
import pathlib

from gvas.gvas_file import GVASFile, GameFileFormat
from gvas.engine_tools import CompressionType, GameVersion

# Constants for test file paths
RESOURCES_DIR = pathlib.Path(
    pathlib.Path(__file__).absolute().parent.parent.parent, "resources", "test"
)


def get_testfile_path(testfile_name: Union[str, pathlib.Path]) -> pathlib.Path:
    return pathlib.Path(RESOURCES_DIR, testfile_name).resolve()


def read_gvas_file(
    input_test_file: str,
    *,
    game_file_format: Optional[GameFileFormat] = None,
    deserialization_hints: Optional[Union[dict[str, str], str, pathlib.Path]] = None,
) -> (GVASFile, BytesIO):

    GVASFile.set_up_gvas_deserialization_hints(deserialization_hints)

    if game_file_format is None:
        game_file_format = GVASFile.get_game_file_format(input_test_file)

    assert isinstance(game_file_format, GameFileFormat)

    with open(input_test_file, "rb") as f:
        test_file_bytes = f.read()

        test_file_stream = BytesIO(test_file_bytes)

        gvas_test_file = GVASFile.read(
            test_file_stream,
            game_file_format.game_version,
            game_file_format.compression_type,
        )

        # reset to start for comparison purposes
        test_file_stream.seek(0)

        # Pass the file back for optional verification
        return gvas_test_file, test_file_stream
