# Engine Tools Documentation

## Overview
This document describes the classes and enums related to Unreal Engine versioning and compression types within the GVAS format. These tools are primarily used internally by the library to handle version-specific serialization differences and compression schemes.

## Class and Function Definitions

### Enums

#### `CompressionType` (enum.Enum)
Defines known GVAS compression methods.
- `UNKNOWN`: Default/unidentified.
- `NONE`: No compression (Magic: `0x30`).
- `ZLIB`: Standard Zlib compression (Magic: `0x31`).
- `ZLIB_TWICE`: Zlib compression applied twice (Magic: `0x32`).
- `PLZ`: Palworld-specific compression (Magic: `0xFF`, not implemented).

#### `GameVersion` (enum.Enum)
Identifies specific games for potential custom handling (currently minimal usage).
- `UNKNOWN`: Default.
- `DEFAULT`: Standard Unreal Engine.
- `PALWORLD`: Specific identifier for Palworld.

#### `EngineVersion` (enum.Enum)
Defines major/minor version pairs for various Unreal Engine releases (e.g., `VER_UE4_27`, `VER_UE5_1`).

#### `FEditorObjectVersion` (enum.IntEnum)
Represents custom serialization versions specific to the main UE4 editor development stream. Each member corresponds to a specific feature or fix introduced in a particular engine version. Includes properties for `friendly_name`, `custom_version_guid`, and `version_mappings`.

#### `FUE5ReleaseStreamObjectVersion` (enum.IntEnum)
Represents custom serialization versions specific to the UE5 release streams. Similar structure to `FEditorObjectVersion`.

### Dataclasses

#### `FEngineVersion`
Stores the detailed engine version read from the GVAS header.

```python
from io import BinaryIO

@dataclass
class FEngineVersion:
    major: int = 0  # u16
    minor: int = 0  # u16
    patch: int = 0  # u16
    change_list: int = 0  # u32
    branch: str = "un.known"  # String

    def read(self, stream: BinaryIO) -> "FEngineVersion": ...
    def write(self, stream: BinaryIO) -> int: ...
```

### Static Class

#### `EngineVersionTool`
A static class (not meant to be instantiated) used to hold global engine version information and custom version data read from a GVAS file. This allows other parts of the library to check version support for specific features.

```python
import uuid
from .engine_tools import FEditorObjectVersion, FUE5ReleaseStreamObjectVersion

ENGINE_VERSION_CLASSES = Union[FEditorObjectVersion, FUE5ReleaseStreamObjectVersion]

class EngineVersionTool:
    custom_versions: dict[str, int] = {} # Maps GUID string to version int
    engine_major: int = 4
    engine_minor: int = 0

    @classmethod
    def set_engine_version(cls, engine_major: int, engine_minor: int) -> None: ...

    @classmethod
    def version_is_at_least(cls, engine_major: int, engine_minor: int) -> bool: ...

    @classmethod
    def set_custom_versions(cls, custom_versions: dict[str, int]) -> None: ...

    @classmethod
    def supports_version(cls, required_version: ENGINE_VERSION_CLASSES) -> bool: ...
```

-   `set_engine_version(cls, major, minor)`: Sets the global major/minor engine version.
-   `version_is_at_least(cls, major, minor)`: Checks if the global engine version is at least the specified version.
-   `set_custom_versions(cls, custom_versions)`: Sets the global dictionary of custom versions read from the GVAS header. The dictionary maps GUID strings to integer version numbers.
-   `supports_version(cls, required_version)`: Checks if a specific custom version (passed as an enum member like `FUE5ReleaseStreamObjectVersion.LargeWorldCoordinates`) is supported by comparing its value against the version stored in the global `custom_versions` dictionary under the appropriate GUID.

## Binary Format

This file primarily defines Python classes and enums. The only class with direct serialization methods is `FEngineVersion`.

### `FEngineVersion`
Reads/writes the following sequence:
1.  Major Version (UInt16)
2.  Minor Version (UInt16)
3.  Patch Version (UInt16)
4.  Changelist (UInt32)
5.  Branch Name (`String`): Length-prefixed string.

```
[Major: UInt16]
[Minor: UInt16]
[Patch: UInt16]
[Changelist: UInt32]
[Branch Name: String]
```

## Examples

### Example `FEngineVersion` Binary Data
Version: 4.27.2, Changelist 12345, Branch "UE4Release"

```
# Major = 4
04 00
# Minor = 27 (0x1B)
1B 00
# Patch = 2
02 00
# Changelist = 12345 (0x3039)
39 30 00 00
# Branch Name: "UE4Release" (UTF-8)
0B 00 00 00       # Length = 11 (10 chars + null)
55 45 34 52 65 6C 65 61 73 65 # "UE4Release"
00                # Null terminator
```

## Implementation Notes
- The `EngineVersionTool` acts as a global state holder for version information, initialized when a `GvasFile` is read.
- The `supports_version` method is key for enabling conditional serialization logic in other property classes (e.g., using `double` vs `float` for `VectorStruct` based on `FUE5ReleaseStreamObjectVersion.LargeWorldCoordinates`).
- Custom versions (`FEditorObjectVersion`, `FUE5ReleaseStreamObjectVersion`) allow fine-grained feature detection based on specific engine development streams and versions.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 