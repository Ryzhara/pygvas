# GVAS Types Documentation

## Overview
This module provides basic type definitions for the GVAS format, including a specialized dictionary implementation that maintains insertion order and can be hashed. This is particularly useful for serialization and deserialization operations in the GVAS format.

## Type Definitions

### Type Variables
- `K`: Generic type variable for dictionary keys
- `V`: Generic type variable for dictionary values

## Classes

### HashableIndexMap
A specialized dictionary implementation that maintains insertion order and can be hashed. This is the Python equivalent of Rust's `HashableIndexMap`.

#### Inheritance
- Inherits from `dict[K, V]`
- Uses `pydantic.dataclasses.dataclass` for enhanced functionality

#### Methods

##### `__hash__()`
```python
def __hash__(self) -> int
```
- Computes a hash value for the dictionary
- Uses sorted items to ensure consistent hash values across different runs
- Returns an integer hash value

##### `__eq__()`
```python
def __eq__(self, other: object) -> bool
```
- Compares two HashableIndexMap instances for equality
- Returns `NotImplemented` if the other object is not a HashableIndexMap
- Compares the underlying dictionaries for equality

## Usage Examples

### Creating a HashableIndexMap
```python
from gvas_types import HashableIndexMap

# Create a new HashableIndexMap
map1 = HashableIndexMap[str, int]()
map1["key1"] = 1
map1["key2"] = 2

# Create another HashableIndexMap with the same values
map2 = HashableIndexMap[str, int]()
map2["key1"] = 1
map2["key2"] = 2

# The maps are equal
assert map1 == map2

# The maps have the same hash value
assert hash(map1) == hash(map2)
```

### Using in Data Structures
```python
from gvas_types import HashableIndexMap

# Create a set of HashableIndexMaps
maps_set = set()
map1 = HashableIndexMap[str, int]()
map1["a"] = 1
maps_set.add(map1)

# Create another map with the same contents
map2 = HashableIndexMap[str, int]()
map2["a"] = 1

# The set will recognize this as a duplicate
assert map2 in maps_set
```

## Implementation Notes
- The class is designed to be compatible with Python's dictionary interface
- Hash values are computed based on sorted items to ensure consistency
- Equality comparison is based on the underlying dictionary contents
- The class is particularly useful for serialization where consistent ordering is important
- The implementation ensures that identical dictionaries will have the same hash value
- The class maintains insertion order like a regular Python dictionary
- The class is designed to work with any hashable key and value types 