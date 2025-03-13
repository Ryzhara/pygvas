"""
Common utility functions for GVAS
"""

from typing import BinaryIO
import struct

def read_string(stream: BinaryIO) -> str:
    """Read a string from the stream (length + utf-8 bytes)"""
    length = struct.unpack('<I', stream.read(4))[0]
    if length == 0:
        return ""
    return stream.read(length).decode('utf-8')[:-1]  # Remove null terminator

def write_string(stream: BinaryIO, value: str) -> int:
    """Write a string to the stream (length + utf-8 bytes)"""
    if not value:
        stream.write(struct.pack('<I', 0))
        return 4
    value_bytes = (value + '\0').encode('utf-8')
    stream.write(struct.pack('<I', len(value_bytes)))
    stream.write(value_bytes)
    return 4 + len(value_bytes) 