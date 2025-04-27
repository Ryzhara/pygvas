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

# Detailed Overview
See the [GVAS OVERVIEW](documentation/gvas_overview.md) file for a detailed overview of the library.

See any of the very detailed files in the [DOCUMENTATION](documentation) directory for information overload.

# Requirements

- Python 3.7+
- See requirements.txt for package dependencies