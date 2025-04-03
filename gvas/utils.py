"""
Common utility functions for GVAS
"""

from typing import BinaryIO
import struct
import uuid
from .error import *
import zlib


def read_atomic_data(
    stream: BinaryIO,
    format_str: str,
    width: int,
    assert_value=None,
    error_msg: str = None,
) -> int:
    position = stream.tell()
    value = struct.unpack(format_str, stream.read(width))[0]
    if assert_value is not None:
        if value != assert_value:
            raise AssertionError(
                f"{error_msg+': ' if error_msg is not None else ""}Expected value {value} != {assert_value} at {position=}"
            )
    return value


# ============= NUMERIC READS/WRITES ========================
def read_int8(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<b", 1, assert_value=assert_value, error_msg=error_msg
    )


def write_int8(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<b", value))


def read_uint8(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<B", 1, assert_value=assert_value, error_msg=error_msg
    )


def write_uint8(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<B", value))


def read_bool(stream: BinaryIO, assert_value=None, error_msg: str = None) -> bool:
    return bool(
        read_atomic_data(stream, "?", 1, assert_value=assert_value, error_msg=error_msg)
    )


def write_bool(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("?", value))


def read_int16(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<h", 2, assert_value=assert_value, error_msg=error_msg
    )


def write_int16(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<h", value))


def read_uint16(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<H", 2, assert_value=assert_value, error_msg=error_msg
    )


def write_uint16(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<H", value))


def read_int32(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<i", 4, assert_value=assert_value, error_msg=error_msg
    )


def write_int32(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<i", value))


def read_uint32(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<I", 4, assert_value=assert_value, error_msg=error_msg
    )


def write_uint32(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<I", value))


def read_int64(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<q", 8, assert_value=assert_value, error_msg=error_msg
    )


def write_int64(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<q", value))


def read_uint64(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<Q", 8, assert_value=assert_value, error_msg=error_msg
    )


def write_uint64(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<Q", value))


def read_float(stream: BinaryIO, assert_value=None, error_msg: str = None) -> float:
    return read_atomic_data(
        stream, "<f", 4, assert_value=assert_value, error_msg=error_msg
    )


def write_float(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<f", value))


def read_double(stream: BinaryIO, assert_value=None, error_msg: str = None) -> float:
    return read_atomic_data(
        stream, "<d", 8, assert_value=assert_value, error_msg=error_msg
    )


def write_double(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<d", value))


# ============= MISC READS/WRITES ========================
def read_null_byte_terminator(stream: BinaryIO) -> None:
    # Read terminator
    read_uint8(stream, assert_value=0, error_msg="Invalid terminator")


def read_bytes(stream: BinaryIO, byte_count: int) -> bytes:
    return stream.read(byte_count)


def write_bytes(stream: BinaryIO, value_bytes: bytes) -> int:
    return stream.write(value_bytes)


def read_string(stream: BinaryIO) -> str:
    """Read a string from the stream
    prefix is uint32: length, followed by UTF-8 byte encoded string
    """

    if (length := read_uint32(stream)) == 0:
        return ""
    value_bytes = read_bytes(stream, length)
    return value_bytes.decode("utf-8")[:-1]  # Remove included '\0'


def write_string(stream: BinaryIO, value: str) -> int:
    """Write a string to the stream
    prefix is uint32: length, followed by UTF-8 byte encoded string
    """
    if not value:  # null | 0 | "" | ''
        return write_uint32(stream, 0)

    value_bytes = (value + "\0").encode("utf-8")  # attach null terminator
    bytes_written = write_uint32(stream, len(value_bytes))
    bytes_written += write_bytes(stream, value_bytes)
    return bytes_written  # 4 + len(value) + 1


def read_guid(stream: BinaryIO) -> uuid:
    return uuid.UUID(bytes_le=stream.read(16))


def write_guid(stream: BinaryIO, guid: uuid) -> uuid:
    return stream.write(guid.bytes_le)


def read_guid_with_terminator(stream: BinaryIO) -> uuid:
    guid = read_guid(stream)
    terminator_position = stream.tell()
    terminator = read_uint8(stream)
    assert terminator == 0, DeserializeError.invalid_terminator(
        terminator, terminator_position
    )
    return guid


def write_guid_with_terminator(stream: BinaryIO, guid: uuid) -> int:
    bytes_written = write_guid(stream, guid)
    bytes_written += write_uint8(stream, 0)
    return bytes_written


def is_zlib_compressed(data):
    """
    Checks if the data is likely zlib compressed based on the initial bytes.

    Args:
        data: The bytes-like object to check.

    Returns:
        True if the data is likely zlib compressed, False otherwise.
    """
    if len(data) < 2:
        return False
    return data[:2] in (b"\x78\x01", b"\x78\x9c", b"\x78\xda")


def is_definitely_zlib_compressed(data):
    """
    Checks if the data is definitely zlib compressed by attempting decompression.

    Args:
        data: The bytes-like object to check.

    Returns:
        True if the data is definitely zlib compressed, False otherwise.
    """
    try:
        zlib.decompress(data)
        return True
    except zlib.error:
        return False
