# GVAS Python Tests

This directory contains unit tests for the GVAS Python library. The tests are organized in a parallel directory structure to match the Rust implementation.

## Directory Structure

- `tests/` - Main test directory
  - `common/` - Common test utilities
  - `gvas_tests/` - Specific tests for GVAS functionality

## Running Tests

To run all tests:

```bash
cd python
python -m unittest discover tests
```

To run a specific test file:

```bash
cd python
python -m unittest tests.test_gvas
```

To run a specific test case:

```bash
cd python
python -m unittest tests.gvas_tests.test_property.TestProperty.test_bool_property
```

## Test Resources

The tests use the same resource files as the Rust implementation, located in the `resources/` directory at the root of the project.

## Test Organization

The tests are organized to mirror the Rust implementation:

1. `test_gvas.py` - Main test file that tests loading and saving various GVAS files
2. `gvas_tests/test_property.py` - Tests for property serialization and deserialization
3. `gvas_tests/test_guid.py` - Tests for GUID functionality
4. `gvas_tests/test_file.py` - Tests for GVASFile functionality
5. `gvas_tests/test_errors.py` - Tests for error handling

## Adding New Tests

When adding new tests, follow these guidelines:

1. Use the `unittest` module for test cases
2. Follow the parallel directory structure to match the Rust implementation
3. Use descriptive test method names that start with `test_`
4. Add docstrings to test methods to describe what they test
5. Use the common test utilities in `common/utils.py` when appropriate 