"""
Common test utilities for GVAS tests
"""

import json
from io import BytesIO
from typing import Dict, Optional, Union
from pathlib import Path

from gvas.gvas_file import GVASFile, GameFileFormat
from gvas.engine_tools import CompressionType, GameVersion
from gvas.gvas_utils import ContextScopeTracker

# Constants for test file paths
RESOURCES_DIR = Path(
    Path(__file__).absolute().parent.parent.parent, "resources", "test"
)


def get_testfile_path(testfile_name: Union[str, Path]) -> Path:
    return Path(RESOURCES_DIR, testfile_name).resolve()


def read_gvas_file(
    input_test_file: str,
    *,
    game_file_format: Optional[GameFileFormat] = None,
    hints: Optional[Union[dict[str, str], str, Path]] = None,
) -> (GVASFile, BytesIO):

    with open(input_test_file, "rb") as f:
        test_file_bytes = f.read()

    test_file_stream = BytesIO(test_file_bytes)

    # set up any requested hints
    if type(hints) is None:
        hints = {}

    elif type(hints) == str() or isinstance(hints, Path):
        hints_file = hints
        with open(hints_file, "r") as f:
            hints = json.load(f)
            # print(f"Loaded {hints} from {hints_file}")

    else:
        assert isinstance(
            hints, dict
        ), f"Hints must be either a dict or a str/Path object to a file."

    ContextScopeTracker.set_hints(hints)

    if game_file_format is not None:
        gvas_test_file: GVASFile = GVASFile.read(
            test_file_stream,
            game_file_format.game_version,
            game_file_format.compression_type,
        )
    else:
        game_file_format = GameFileFormat(
            game_version=GameVersion.DEFAULT, compression_type=CompressionType.NONE
        )
        game_file_format.deserialize_game_version(test_file_stream)
        gvas_test_file, _test_file_stream = GVASFile.read(
            test_file_stream,
            game_file_format.game_version,
            game_file_format.compression_type,
        )

    # reset to start for comparison purposes
    test_file_stream.seek(0)

    # Pass the file back for optional verification
    return gvas_test_file, test_file_stream
