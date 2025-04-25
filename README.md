# GVAS Python Port

This is a Python port of the GVAS (Game Version Agnostic Save) Rust library for parsing Unreal Engine 4/5 save files.

## Key Differences from Rust Version

1. **Error Handling**
   - Uses Python's exception system instead of Rust's Result types
   - Simplified error hierarchy with custom exception classes

2. **Type System**
   - Uses Python's type hints and dataclasses
   - Replaces Rust enums with Python Enum classes
   - Uses Python's built-in types where appropriate

3. **Memory Management**
   - Relies on Python's garbage collection instead of Rust's ownership system
   - Simplified memory handling patterns

4. **Performance Considerations**
   - May be slower than Rust version due to Python's interpreted nature
   - Uses Python's struct module for binary data handling
   - Maintains similar algorithmic complexity

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic example of reading a save file:

```python
from gvas import GVASFile, GameVersion

# Open and read a save file
with open("save.sav", "rb") as f:
    gvas_file = GVASFile.read(f, GameVersion.Default)

# Print the contents
print(gvas_file)
```

Example with type hints for struct properties:

```python
from gvas import GVASFile, GameVersion

# Create type deserialization_hints for ambiguous structs
hints = {
    "UnLockedMissionParameters.MapProperty.Key.StructProperty": "Guid"
}

# Read with deserialization_hints
with open("save.sav", "rb") as f:
    gvas_file = GVASFile.read_with_hints(f, GameVersion.Default, hints)
```

## Structure

The Python port maintains a similar structure to the Rust version:

- `gvas/`
  - `__init__.py` - Package initialization and exports
  - `array_property.py` - Array property implementation
  - `error.py` - Error types and handling
  - `game_version.py` - Game version information
  - `types.py` - Basic type definitions
  - `properties/` - PropertyFactory type implementations

## Requirements

- Python 3.7+
- See requirements.txt for package dependencies

## Notes on Translation

This port aims to maintain the functionality of the original Rust library while adapting to Python's idioms and best practices. Some key translation decisions:

1. Used dataclasses for structured data instead of Rust structs
2. Implemented custom exceptions instead of Result types
3. Used Python's built-in UUID handling for GUIDs
4. Maintained similar file format compatibility
5. Preserved the original binary format handling

## Contributing

Contributions are welcome! Please ensure that any contributions:

1. Maintain compatibility with the original file format
2. Include appropriate type hints
3. Follow Python best practices
4. Include tests for new functionality

## License

Same as the original Rust library 