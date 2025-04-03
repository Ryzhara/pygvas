"""
Error types for GVAS
Python port of error.rs

Key differences from Rust version:
- Uses Python's exception system instead of Result types
- Simplified error hierarchy
"""


class DeserializeError(Exception):
    """Error that occurs during deserialization"""

    def __init__(self, message: str, position: int = None):
        self.position = position
        if position is not None:
            message = f"{message} at position {position}"
        super().__init__(message)

    @classmethod
    def invalid_header(cls, message: str) -> "DeserializeError":
        """Create an invalid header error"""
        return cls(f"Invalid header: {message}")

    @classmethod
    def invalid_property(cls, message: str, position: int) -> "DeserializeError":
        """Create an invalid property error"""
        return cls(f"Invalid property: {message}", position)

    @classmethod
    def invalid_terminator(cls, terminator: int, position: int) -> "DeserializeError":
        """Create an invalid terminator error"""
        return cls(f"Invalid terminator: {terminator}", position)

    @classmethod
    def missing_hint(
        cls, property_type: str, property_path: str, position: int
    ) -> "DeserializeError":
        """Create a missing hint error"""
        return cls(
            f"Missing hint for {property_type} at path {property_path}", position
        )

    @classmethod
    def invalid_value_size(cls, length: int, param: int, position: int):
        return cls(f"Invalid size: expecting {length} and got {param} at {position=}")

    @classmethod
    def invalid_read_count(cls, expected: int, found: int, position: int):
        return cls(
            f"Expected to read {expected} bytes but got {found} bytes at {position=}"
        )


class SerializeError(BaseException):
    """Error that occurs during serialization"""

    @classmethod
    def invalid_value(cls, message: str) -> "SerializeError":
        """Create an invalid value error"""
        return cls(f"Invalid value: {message}")
