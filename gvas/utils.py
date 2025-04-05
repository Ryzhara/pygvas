"""
Common utility functions for GVAS
"""

import struct
import uuid
import zlib
from io import BytesIO
from typing import BinaryIO, Any, List, Tuple, Dict

from .error import *
from .game_version import GVAS_MAGIC, PLZ_MAGIC, CompressionType
from .gvas_types import HashableIndexMap


class ByteCountValidator:
    """
    Use stream.tell() to count bytes and compare to expectations.
    """

    def __init__(self, stream: BinaryIO, expected_byte_count: int, do_validation):
        self.stream = stream
        self.expected_byte_count = expected_byte_count
        self.do_validation = do_validation
        self.start_byte = 0
        self.end_byte = 0

    def __enter__(self):
        self.start_byte = self.stream.tell()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred: {exc_val}")
            return False
            # # Handle specific exceptions differently
            # if exc_type is ValueError:
            #     print("ValueError handled, suppressing exception")
            #     return True  # Suppress ValueError
            # else:
            #     print("Other exception, re-raising")
            #     return False # Re-raise other exceptions

        if not self.do_validation:
            return
        self.end_byte = self.stream.tell()
        found_bytes = self.end_byte - self.start_byte
        assert (
            found_bytes == self.expected_byte_count
        ), DeserializeError.invalid_read_count(
            self.expected_byte_count, found_bytes, self.start_byte
        )


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


def guid_from_uint32x4(uint1: int, uint2: int, uint3: int, uint4: int) -> uuid:
    buffer = BytesIO()
    write_uint32(buffer, uint1)
    write_uint32(buffer, uint2)
    write_uint32(buffer, uint3)
    write_uint32(buffer, uint4)
    return uuid.UUID(bytes_le=buffer.getvalue())


def read_guid(stream: BinaryIO) -> uuid:
    return uuid.UUID(bytes_le=stream.read(16))


def write_guid(stream: BinaryIO, guid: uuid) -> uuid:
    return stream.write(guid.bytes_le)


def peek(stream, count: int) -> bytes:
    current_position = stream.tell()
    peeked_bytes = read_bytes(stream, count)
    stream.seek(current_position)
    return peeked_bytes


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


def looks_like_gvas(stream: BinaryIO) -> bool:
    peeked_bytes = peek(stream, 4)
    return peeked_bytes == GVAS_MAGIC


def looks_like_palworld(stream: BinaryIO) -> bool:

    current_position = stream.tell()
    # grab the elements
    decompressed_size = read_uint32(stream)
    compressed_size = read_uint32(stream)
    plz_bytes = read_bytes(stream, len(PLZ_MAGIC))
    enum_value = read_uint8(stream)
    stream.seek(current_position)

    # tests:
    sizes_ok = compressed_size <= decompressed_size < 1_000_000_000
    magic_ok = plz_bytes == PLZ_MAGIC
    enum_ok = enum_value in [member.value for member in CompressionType]
    return sizes_ok and magic_ok and enum_ok


def read_standard_header(
    stream: BinaryIO,
    *,
    assert_length=None,
    assert_array_index=0,
    stream_readers=None,  # read after array index and before terminator
) -> List[Any]:

    result_list = [
        read_uint32(stream, assert_length),  # length; almost always something needed
        read_uint32(stream, assert_array_index),  # array_index; almost always zero
    ]

    # if there is a list of reader functions, apply them to extract data
    if stream_readers is not None:
        for reader in stream_readers:
            result_list.append(reader(stream))

    # last step is to ensure a null byte terminator, but we do not return it
    read_uint8(stream, 0)

    return result_list


def write_standard_header(
    stream: BinaryIO,
    property_type,
    *,
    length=None,
    array_index=0,
    data_to_write=None,  # read after array index and before terminator
) -> int:
    bytes_written = 0
    bytes_written += write_string(stream, property_type)
    bytes_written += write_uint32(stream, length)
    bytes_written += write_uint32(stream, array_index)

    # write any optional bare data types; expect this to be strings and/or uuid
    if data_to_write is not None:
        for data in data_to_write:
            if type(data) is str:
                bytes_written += write_string(stream, data)
            elif type(data) is uuid.UUID:
                bytes_written += write_guid(stream, data)
            else:
                raise TypeError(
                    f"Unexpected type in write_standard_header: {type(data)}"
                )

    bytes_written += write_uint8(stream, 0)  # terminator
    return bytes_written
