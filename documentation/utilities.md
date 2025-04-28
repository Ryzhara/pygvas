# Utility Scripts and Testing Documentation

## Overview
This document describes the top-level utility scripts and batch files provided with the `pygvas` library for common tasks like file conversion, format detection, and running tests.

## Python Utility Scripts

These scripts provide command-line interfaces for interacting with GVAS files using the `pygvas` library.

### `gvas2json.py`
Converts a GVAS file (`.sav`) into a JSON representation.

**Usage:**
```bash
python gvas2json.py <input_gvas_file.sav> <output_json_file.json> [--hints_file <hints.json>]
```
- `<input_gvas_file.sav>`: Path to the source GVAS file.
- `<output_json_file.json>`: Path where the output JSON file will be saved.
- `--hints_file <hints.json>` (Optional): Path to a JSON file containing deserialization hints needed for ambiguous structures (like structs within arrays).

**Functionality:**
1.  Parses command-line arguments.
2.  Calls `GVASFile.deserialize_gvas_file()` to read and parse the input GVAS file, using hints if provided.
3.  Calls `gvas_file.serialize_to_json_file()` to write the parsed data to the specified JSON output file.

### `json2gvas.py`
Converts a JSON file (previously created by `gvas2json.py` or conforming to the expected structure) back into a GVAS file (`.sav`).

**Usage:**
```bash
python json2gvas.py <input_json_file.json> <output_gvas_file.sav>
```
- `<input_json_file.json>`: Path to the source JSON file.
- `<output_gvas_file.sav>`: Path where the output GVAS file will be saved.

**Functionality:**
1.  Parses command-line arguments.
2.  Calls `GVASFile.deserialize_from_json_file()` to load and parse the input JSON file into a `GVASFile` object.
3.  Calls `gvas_file.serialize_to_gvas_file()` to write the data back into the binary GVAS format in the specified output file.

### `detect_gvas_format.py`
Detects and reports the game format (e.g., `DEFAULT`, `PALWORLD`) and compression type (e.g., `NONE`, `ZLIB`) of a given GVAS file.

**Usage:**
```bash
python detect_gvas_format.py <input_gvas_file.sav>
```
- `<input_gvas_file.sav>`: Path to the GVAS file to analyze.

**Functionality:**
1.  Parses command-line arguments.
2.  Calls `GVASFile.get_game_file_format()` which reads the initial bytes of the file to determine the format and compression.
3.  Prints the detected game version and compression type to the console.

## Batch Scripts (Windows)

These batch files are assumed to execute test suites for the library.

### `do_unit_tests.bat`
Likely runs the main unit test suite for the core `pygvas` library components (e.g., individual property serialization/deserialization).

### `do_utility_tests.bat`
Likely runs tests specifically designed for the command-line utility scripts (`gvas2json.py`, `json2gvas.py`, `detect_gvas_format.py`), potentially involving file comparisons.

## Implementation Notes

-   The Python scripts rely heavily on the `GVASFile` class from `gvas.gvas_file` for their core functionality.
-   They use Python's `argparse` module for command-line argument handling.
-   Error handling is included for file not found and other potential exceptions during processing.
-   The batch scripts provide a convenient way to execute predefined test scenarios on Windows.

> #### Note
> This document was created with a generative AI prompt in the Cursor IDE. 