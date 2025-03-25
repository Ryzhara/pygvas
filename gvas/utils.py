"""
Common utility functions for GVAS
"""

from typing import BinaryIO
import struct
from .gvas_types import Guid


def read_string(stream: BinaryIO) -> str:
    """Read a string from the stream (length + utf-8 bytes)"""
    length = struct.unpack("<I", stream.read(4))[0]
    if length == 0:
        return ""
    return stream.read(length).decode("utf-8")[:-1]  # Remove null terminator after read


def write_string(stream: BinaryIO, value: str) -> int:
    """Write a string to the stream (length + utf-8 bytes)"""
    if not value:
        stream.write(struct.pack("<I", 0))
        return 4
    value_bytes = (value + "\0").encode("utf-8")  # attach null terminator
    bytes_written = stream.write(struct.pack("<I", len(value_bytes)))
    bytes_written += stream.write(value_bytes)
    return bytes_written  # 4 + len(value) + 1


def read_guid_as_str(stream: BinaryIO) -> str:
    guid = Guid.from_bytes(stream.read(16))


def read_guid_with_terminator(stream: BinaryIO) -> Guid:
    guid_bytes = stream.read(16)
    guid = Guid.from_bytes(guid_bytes)
    # print(f"read_body: found {self.guid=}")
    terminator_position = stream.tell()
    terminator = stream.read(1)[0]
    assert (
        terminator == 0
    ), f"Invalid terminator: {terminator} at {terminator_position=}"
    return guid


def write_guid_with_terminator(stream: BinaryIO, guid: Guid) -> int:
    # Write GUID
    bytes_written = stream.write(guid.to_bytes())
    # bytes_written += 16

    # Write terminator
    bytes_written += stream.write(bytes([0]))
    # bytes_written += 1
    return bytes_written
