from Demos.mmapfile_demo import offset

# pygvas

The pygvas module is a Python library that allows parsing of gvas save files.

## Documentation

Crate documentation is contained in the project at [DOCUMENTATION](docs)

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
then use the included utility files. See the [UTILITIES](docs/utilities.md) documentation for more.

* gvas2json.py
* json2gvas.py
* detect_gvas_format.py

# Detailed Overview
The utilities also include examples of code for de/serialization. 
See the [OVERVIEW](docs/gvas_overview.md) documentation for a detailed overview of the library.

See any of the very detailed files in the [DOCUMENTATION](docs) directory for information overload.

# Requirements

- Python 3.9+
- See requirements.txt for package dependencies