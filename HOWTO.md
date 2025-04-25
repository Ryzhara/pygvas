from Demos.mmapfile_demo import offset

# pygvas

The pygvas module is a Python library that allows parsing of gvas save files.

## Documentation

Crate documentation is contained in the project at [DOCUMENTATION](documentation)

## Pydantic Support

This modules uses Pydantic for deserialization and serialization. To use serde with
pygvas, Pydantic must be enabled by running:
```bash
pip install pydantic
```
or if more dependencies are added in the future:
```bash
pip install -r requirements.txt
```

# Usage

If you just need to convert back and forth so you can inspect/modify the JSON,
then use the included utility files. The utilities also include examples of code
for reading.

* gvas2json.py
* json2gvas.py
* detect_gvas_format.py

## Example code
```python
from gvas.gvas_file import GVASFile

# Open and read a save file
gvas_file: GVASFile = GVASFile.deserialize_gvas_file("save.sav")
```

Example with type hints for struct properties:

```python
from gvas.gvas_file import GVASFile

# Read with deserialization_hints inline
hints = {
    "UnLockedMissionParameters.MapProperty.Key.StructProperty": "Guid"
}

gvas_file: GVASFile = GVASFile.deserialize_gvas_file(
    "save.sav", deserialization_hints=hints
)

# or

# Read with deserialization_hints file
gvas_file: GVASFile = GVASFile.deserialize_gvas_file(
    "save.sav", deserialization_hints="save.hints.json"
)
```

If you want to go lower level, then functions to look at include:
```python
    def read(
        cls,
        stream: BinaryIO,
        game_version: GameVersion,
        compression_type: CompressionType,
    ) -> "GVASFile":
```
and
```python
    def write(
        self,
        stream: BinaryIO,
        uncompressed_file_name: str = None,
    ) -> None:
```
where the optional uncompressed file name is used for development debugging.

# Requirements

- Python 3.7+
- See requirements.txt for package dependencies