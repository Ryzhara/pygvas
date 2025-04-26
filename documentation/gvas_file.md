# GVAS File Interface Documentation

## Overview
This document describes the main classes used to interact with GVAS files: `GvasHeader`, `GameFileFormat`, and the central `GVASFile` class. `GVASFile` provides methods for reading (deserializing) from `.sav` files or JSON, and writing (serializing) back to `.sav` or JSON formats.

## Class and Function Definitions

### `GvasHeader`
A dataclass representing the header information found at the beginning of a GVAS file.

```python
from gvas.engine_tools import FEngineVersion

@dataclass
class GvasHeader:
    type: str = "Unknown" # e.g., "Version2", "Version3"
    package_file_version: int = None
    package_file_version_ue5: Optional[int] = None # Only present in Version3
    engine_version: FEngineVersion = None
    custom_version_format: int = None
    custom_versions: dict[str, int] = None # Maps GUID string to version integer
    save_game_class_name: str = None

    @classmethod
    def read(cls, stream: BinaryIO) -> "GvasHeader": ...
    def write(self, stream: BinaryIO) -> int: ...
```
- Contains metadata about the engine version, custom serialization versions, and the main save game class.
- `read` and `write` handle the specific binary layout of the header.

### `GameFileFormat`
A dataclass holding information about the detected game and compression type, primarily used for handling Palworld's specific GVAS variations.

```python
from gvas.engine_tools import GameVersion, CompressionType

@dataclass
class GameFileFormat:
    game_version: GameVersion = GameVersion.UNKNOWN
    compression_type: CompressionType = CompressionType.UNKNOWN

    @classmethod
    def has_gvas_header(cls, stream: BinaryIO) -> bool: ...
    @classmethod
    def has_palworld_header(cls, stream: BinaryIO) -> bool: ...
    @classmethod
    def has_zlib_header(cls, stream: BinaryIO) -> bool: ...
    @classmethod
    def is_definitely_zlib_compressed(cls, stream: BinaryIO) -> bool: ...

    def check_for_palworld(self, stream: BinaryIO) -> bool: ...
    def deserialize_game_version(self, stream: BinaryIO, verbose: bool = False):
        # Determines game_version and compression_type based on magic numbers
        ...
```
- Includes methods to detect GVAS, Palworld (`PlZ`), and Zlib magic numbers.
- `deserialize_game_version` attempts to identify the format by reading the first few bytes of a stream.

### `GVASFile` (inherits `pydantic.BaseModel`)
The main class representing a loaded GVAS file. It holds the header, detected file format, and the deserialized properties.

```python
from pydantic import BaseModel
from typing import Optional, Union
import pathlib
from io import BinaryIO
from gvas.properties.aggregator_properties import UNREAL_ENGINE_PROPERTIES

class GVASFile(BaseModel):
    game_file_format: GameFileFormat
    header: GvasHeader
    properties: dict[str, UNREAL_ENGINE_PROPERTIES]

    # --- Class Methods for Loading/Deserialization ---
    @classmethod
    def get_game_file_format(cls, file_path: str) -> GameFileFormat:
        """Reads only enough of the file to determine its format."""
        ...

    @classmethod
    def deserialize_json(cls, json_content: dict) -> "GVASFile":
        """Deserializes GVAS data from a Python dictionary (e.g., loaded from JSON)."""
        ...

    @classmethod
    def deserialize_from_json_file(cls, json_file_path: str) -> "GVASFile":
        """Loads and deserializes GVAS data from a JSON file."""
        ...

    @classmethod
    def set_up_gvas_deserialization_hints(
        cls, deserialization: Optional[Union[dict, str, pathlib.Path]]
    ):
        """Sets hints needed for ambiguous types (e.g., structs in arrays)."""
        ...

    @classmethod
    def deserialize_gvas_file(
        cls,
        file_path: str,
        *,
        game_file_format: Optional[GameFileFormat] = None,
        deserialization_hints: Optional[Union[dict, str, pathlib.Path]] = None,
    ) -> "GVASFile":
        """Loads and deserializes a GVAS (.sav) file from disk."""
        ...

    @classmethod
    def read(
        cls,
        stream: BinaryIO,
        game_version: GameVersion,
        compression_type: CompressionType,
    ) -> "GVASFile":
        """Core deserialization logic from an already-opened stream."""
        ...

    # --- Instance Methods for Saving/Serialization ---
    def serialize_to_json(self) -> dict:
        """Serializes the GVAS data to a Python dictionary."""
        ...

    def serialize_to_json_file(self, file_path: str) -> None:
        """Serializes the GVAS data and saves it to a JSON file."""
        ...

    def serialize_to_gvas_file(self, output_file: str, uncompressed_output_file: Optional[str] = None) -> None:
        """Serializes the GVAS data and saves it to a GVAS (.sav) file."""
        ...

    def write(
        self,
        stream: BinaryIO,
        uncompressed_file_name: Optional[str] = None,
    ) -> None:
        """Core serialization logic to an already-opened stream."""
        ...
```

-   **Attributes**: `game_file_format`, `header`, `properties` (a dictionary mapping top-level property names to their instances).
-   **Deserialization**: Provides methods like `deserialize_gvas_file` (primary method for loading `.sav` files), `deserialize_from_json_file`, and the core `read` method.
-   **Serialization**: Provides methods like `serialize_to_gvas_file` (primary method for saving `.sav` files), `serialize_to_json_file`, and the core `write` method.
-   **Hints**: Requires `set_up_gvas_deserialization_hints` to be called before deserialization if the file contains ambiguous structures (like structs within arrays) that need type information provided externally.
-   **Compression/Format Handling**: Internally handles potential Zlib compression and Palworld-specific file structure variations during `read` and `write` based on the `game_file_format`.

## Binary Format

The overall structure of a GVAS file processed by this class is:

1.  **Optional Palworld Prefix** (if `game_version == GameVersion.PALWORLD`):
    *   Decompressed Size (UInt32)
    *   Compressed Size (UInt32)
    *   Magic Bytes (`b"PlZ"`)
    *   Compression Type Enum (Int8)
2.  **Optional Compressed Data** (if `compression_type != CompressionType.NONE`):
    *   The Zlib-compressed (potentially twice) data containing the Header and Body.
3.  **GVAS Header** (`GvasHeader.read`/`write`):
    *   Magic Bytes (`b"GVAS"`)
    *   Save Game Version (UInt32)
    *   Package File Version (UInt32)
    *   Package File Version UE5 (Optional UInt32)
    *   Engine Version (`FEngineVersion` data)
    *   Custom Version Format (UInt32)
    *   Custom Versions Count (UInt32)
    *   Custom Versions Array (`FCustomVersion` data * Count)
    *   Save Game Class Name (`String`)
4.  **GVAS Body**:
    *   Top-Level Properties (Sequence): Zero or more instances of:
        *   Property Name (`String`)
        *   Property Type (`String`)
        *   Full Property Data: Binary data for the property, **including** its standard header (`include_header=True`).
    *   Terminator (`String`): The literal string "None".
5.  **Final Terminator** (UInt32): A final `0x00000000` after the "None" string.

```
[Optional Palworld Prefix]
[Optional Compressed Data Start]
  [GVAS Header]
  [GVAS Body]
    [Property 1 Name: String]
    [Property 1 Type: String]
    [Property 1 Data (Full Header + Body)]
    ...
    [Property N Name: String]
    [Property N Type: String]
    [Property N Data (Full Header + Body)]
    [Terminator: String = "None"]
  [Final Terminator: UInt32 = 0]
[Optional Compressed Data End]
```

## Examples

```python
from gvas.gvas_file import GVASFile

# --- Deserializing from a .sav file ---
hints = {
    "SaveGameData.StructArrayExample": "Vector", # Hint: Elements are Vector structs
    "SaveGameData.ByteBlobbedStruct": { # Hint: Treat as raw bytes
        "type": "ByteBlobStruct",
        "context": {"byte_count": 12}
    }
}

try:
    gvas_data = GVASFile.deserialize_gvas_file("MySave.sav", deserialization_hints=hints)

    # Access properties
    player_name = gvas_data.properties["SaveGameData"].value["PlayerName"].value
    print(f"Player Name: {player_name}")

    # Modify properties (ensure type correctness)
    gvas_data.properties["SaveGameData"].value["Health"].value = 95.5

    # --- Serializing back to a .sav file ---
    gvas_data.serialize_to_gvas_file("MySave_Modified.sav")

    # --- Serializing to JSON ---
    gvas_data.serialize_to_json_file("MySave.json")

    # --- Deserializing from JSON ---
    gvas_data_from_json = GVASFile.deserialize_from_json_file("MySave.json")

except Exception as e:
    print(f"An error occurred: {e}")

```

## Implementation Notes

-   `GVASFile` uses Pydantic `BaseModel` for data validation and serialization/deserialization to/from Python dictionaries (and thus JSON).
-   The `read` and `write` methods handle the core GVAS logic, including potential decompression/compression and Palworld format specifics.
-   Deserialization relies heavily on `PropertyFactory` to instantiate correct property types.
-   Serialization relies on the `write` method implemented by each `PropertyTrait` subclass.
-   **Deserialization Hints are crucial** for correctly parsing arrays or maps containing structs, as the type information is not stored per-element in the binary format for those cases.
-   Engine version information (`EngineVersionTool`) is automatically set up during deserialization to handle version-specific logic (like LWC float/double differences).

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 