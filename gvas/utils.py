"""
Common utility functions for GVAS
"""

import enum
import json
import dataclasses
import uuid
import datetime
import struct
from io import BytesIO
from typing import BinaryIO, Any, List, Tuple, Dict

from .custom_versions import FEditorObjectVersion, FUE5ReleaseStreamObjectVersion
from .error import *

ZERO_GUID = uuid.UUID(int=0)


def datetime_to_str(dt: int) -> str:
    # datetime.datetime.fromtimestamp takes time in seconds since January 1, 1970, 00:00:00 (UTC) as a floating-point number
    # FDateTime type represents dates and times as ticks (0.1 microseconds) since January 1, 0001
    # seconds_since_1_1_00001 = 6_392_264_799_600
    try:
        ticks_per_second = 10_000_000.0
        seconds = dt / ticks_per_second
        comment = (
            datetime.datetime.min + datetime.timedelta(seconds=seconds)
        ).strftime("%d/%m/%Y %H:%M:%S.%f")
    except Exception as e:
        print(f"Cant process {dt=} : {e}")
        comment = str(dt)

    return comment


# ============================================
class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, obj):

        def is_not_empty(value):
            # if isinstance(value, (str, type(None))):
            #     return not not value
            if isinstance(value, (type(None))):
                return not not value

            if isinstance(value, uuid.UUID) and value == ZERO_GUID:
                return False

            return True

        if isinstance(obj, enum.IntEnum):
            return obj.name

        if isinstance(obj, uuid.UUID):
            return guid_to_str(obj)

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, list):
            return [self.default(item) for item in obj]

        if isinstance(obj, tuple):
            return [self.default(item) for item in obj]

        if isinstance(obj, bytes):
            return obj.hex()

        if isinstance(obj, dict):
            return {k: self.default(v) for k, v in obj.items() if is_not_empty(v)}

        if dataclasses.is_dataclass(obj):
            return {
                k: self.default(v)
                for k, v in dataclasses.asdict(obj).items()
                if is_not_empty(v)
            }

        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj

        return obj


# ============================================
#
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
            print(
                f"An exception of type {exc_type} was caught in ByteCountValidator: {exc_val}\n\t{self.start_byte=} {self.expected_byte_count=} {self.do_validation=}\n\t{exc_tb}"
            )
            return False

        if not self.do_validation:
            return None

        self.end_byte = self.stream.tell()
        read_byte_count = self.end_byte - self.start_byte

        if read_byte_count != self.expected_byte_count:
            raise DeserializeError.invalid_read_count(
                self.expected_byte_count, read_byte_count, self.start_byte
            )
        return None


# ============================================
#
class SerializationTools:
    """
    This class corresponds to the Rust package use of "options" and scoped property stacks.
    It is never instantiated and avoids cluttering signatures with mostly unused parameters.

    If your file fails while parsing with a DeserializeError::MissingHint error you need hints.
    When a struct is stored inside ArrayProperty/SetProperty/MapProperty in GvasFile it does not
    contain type annotations. This means that a library parsing the file must know the type
    beforehand. That’s why you need hints.
    """

    custom_versions: dict[str, int]
    hints: Dict[str, str] = {}
    context_stack: List[str] = []
    engine_major: int = 4
    engine_minor: int = 0

    @classmethod
    def set_engine_version(cls, engine_major: int, engine_minor: int) -> None:
        cls.engine_major = engine_major
        cls.engine_minor = engine_minor

    @classmethod
    def version_is_at_least(cls, engine_major: int, engine_minor: int):
        return engine_major >= cls.engine_major and engine_minor >= cls.engine_minor

    def version_is_less_than(cls, engine_major: int, engine_minor: int):
        return engine_major < cls.engine_major and engine_minor < cls.engine_minor

    # initialization requirements
    @classmethod
    def set_custom_versions(cls, custom_versions: dict[str, int]) -> None:
        cls.custom_versions = custom_versions

    # used for processing hints
    @classmethod
    def push_context_step(cls, step: str) -> None:
        cls.context_stack.append(step)

    @classmethod
    def pop_context_step(cls) -> None:
        cls.context_stack.pop()

    @classmethod
    def get_context_path(cls) -> str:
        return ".".join(cls.context_stack)

    @classmethod
    def supports_version(
        cls, required_version: FEditorObjectVersion | FUE5ReleaseStreamObjectVersion
    ) -> bool:
        guid_key_str = guid_to_str(required_version.custom_version_guid)
        supported_version = cls.custom_versions.get(guid_key_str, 0)
        return supported_version >= required_version.value


# ============================================
#
class ContextScopeTracker:
    parent_context = "unknown"
    context = "unknown"

    def __init__(self, context: str):
        self.parent_context = SerializationTools.get_context_path()
        self.context = context

    def __enter__(self):
        SerializationTools.push_context_step(self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(
                f"An exception of type {exc_type} occurred: {exc_val} with context\n\t{SerializationTools.get_context_path()}"
            )
            import traceback
            import sys

            traceback.print_exception(exc_type, exc_val, exc_tb, file=sys.stdout)
            return False
        # Don't pop so we can have deepest context for debugging
        SerializationTools.pop_context_step()
        return True


# ============================================
#
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


# ============= TOOLS FOR READS/WRITES ========================


# ============================================
#
def peek(stream, count: int) -> bytes:
    current_position = stream.tell()
    peeked_bytes = read_bytes(stream, count)
    stream.seek(current_position)
    return peeked_bytes


# ============================================
#
def read_int8(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<b", 1, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_int8(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<b", value))


# ============================================
#
def read_uint8(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<B", 1, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_uint8(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<B", value))


# ============================================
#
def read_bool(stream: BinaryIO, assert_value=None, error_msg: str = None) -> bool:
    return bool(
        read_atomic_data(stream, "?", 1, assert_value=assert_value, error_msg=error_msg)
    )


# ============================================
#
def write_bool(stream: BinaryIO, value: bool) -> int:
    return stream.write(struct.pack("?", value))


# ============================================
#
def read_bool32bit(stream: BinaryIO) -> bool:
    value = read_uint32(stream)
    if value not in [0, 1]:
        raise DeserializeError.invalid_value(
            value,
            stream.tell() - 4,
            "read_bool32bit",
        )
    return True if value else False


# ============================================
#
def write_bool32bit(stream: BinaryIO, value: [int, bool]) -> int:
    if value not in [0, 1, True, False]:
        raise SerializeError.invalid_value(
            f"Invalid bool32bit value {value} at {stream.tell()}"
        )
    return write_uint32(stream, 1 if value else 0)


# ============================================
#
def read_int16(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<h", 2, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_int16(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<h", value))


# ============================================
#
def read_uint16(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<H", 2, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_uint16(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<H", value))


# ============================================
#
def read_int32(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<i", 4, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_int32(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<i", value))


# ============================================
#
def read_uint32(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<I", 4, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_uint32(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<I", value))


# ============================================
#
def read_int64(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<q", 8, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_int64(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<q", value))


# ============================================
#
def read_uint64(stream: BinaryIO, assert_value=None, error_msg: str = None) -> int:
    return read_atomic_data(
        stream, "<Q", 8, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_uint64(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<Q", value))


# ============================================
#
def read_float(stream: BinaryIO, assert_value=None, error_msg: str = None) -> float:
    return read_atomic_data(
        stream, "<f", 4, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_float(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<f", value))


# ============================================
#
def read_double(stream: BinaryIO, assert_value=None, error_msg: str = None) -> float:
    return read_atomic_data(
        stream, "<d", 8, assert_value=assert_value, error_msg=error_msg
    )


# ============================================
#
def write_double(stream: BinaryIO, value) -> int:
    return stream.write(struct.pack("<d", value))


# ============= MISC READS/WRITES ========================


# ============================================
#
def read_null_byte_terminator(stream: BinaryIO) -> None:
    # Read terminator
    read_uint8(stream, assert_value=0, error_msg="Invalid terminator")


# ============================================
#
def read_bytes(stream: BinaryIO, byte_count: int) -> bytes:
    return stream.read(byte_count)


# ============================================
#
def write_bytes(stream: BinaryIO, value_bytes: bytes) -> int:
    return stream.write(value_bytes)


# ============================================
#
def read_string(stream: BinaryIO) -> str | None:
    """Read a string from the stream
    prefix is uint32: length, followed by UTF-8 byte encoded string
    """

    if (length := read_int32(stream)) == 0:
        return None  # ""

    if not -131072 <= length <= 131072:
        raise SerializeError.invalid_value(
            f"String length {length} is out of range -131072 <= length <= 131072"
        )

    # UTF 16
    position = stream.tell()
    if length < 0:
        length = 2 * abs(length)  # includes null terminator
        encoding = "utf-16-le"
        value_bytes = read_bytes(stream, length - 2)
        _null_terminator = read_uint16(
            stream, assert_value=0, error_msg="Invalid UTF-16 terminator"
        )
        if value_bytes.isascii():
            raise ValueError(
                f"Suspicous UTF-16 bytes are really ascii: {value_bytes} at {position=}"
            )
    else:
        encoding = "utf-8"
        value_bytes = read_bytes(stream, length - 1)
        _null_terminator = read_uint8(
            stream, assert_value=0, error_msg="Invalid UTF-8 terminator"
        )
        if not value_bytes.isascii():
            raise ValueError(
                f"Invalid UTF-8 bytes are not ASCII: {value_bytes} at {position=}"
            )
    try:
        final_string = value_bytes.decode(encoding)
    except UnicodeDecodeError as ude:
        raise ude

    return final_string


# ============================================
#
def write_string(stream: BinaryIO, value: str) -> int:
    """Write a string to the stream
    prefix is uint32: length, followed by UTF-8 byte encoded string
    """
    if (
        value is None
    ):  # null -- if we read an empty string, we write an empty string | "" | ''
        return write_uint32(stream, 0)

    bytes_written = 0
    if value.isascii():
        length = len(value) + 1
        value_bytes = value.encode("utf-8")  # attach null terminator
        bytes_written += write_int32(stream, length)
        bytes_written += write_bytes(stream, value_bytes)
        bytes_written += write_uint8(stream, 0)  # manual terminator
    else:
        value_words_as_bytes = value.encode("utf-16-le")  # attach null terminator
        length = len(value) + 1
        bytes_written += write_int32(stream, -length)
        bytes_written += write_bytes(stream, value_words_as_bytes)
        bytes_written += write_uint16(stream, 0)  # manual terminator

    # value_bytes = (value + "\0").encode("utf-8")  # attach null terminator
    # bytes_written = write_uint32(stream, len(value_bytes))
    # bytes_written += write_bytes(stream, value_bytes)
    return bytes_written


# ============================================
#
def guid_to_str(guid_uuid: uuid) -> str:
    return str(guid_uuid).upper()


# ============================================
#
def str_to_guid(guid_str: str) -> uuid:
    return uuid.UUID(guid_str)


# ============================================
#
def read_guid(stream: BinaryIO) -> uuid:
    return uuid.UUID(bytes=stream.read(16))


# ============================================
#
def write_guid(stream: BinaryIO, guid: [uuid, str]) -> uuid:
    if type(guid) is str:
        guid = str_to_guid(guid)
    return stream.write(guid.bytes)


# ============================================
#
def read_standard_header(
    stream: BinaryIO,
    *,
    assert_length=None,
    assert_array_index=0,
    stream_readers=None,  # read after array index and before terminator
) -> List[Any]:
    """
    Args:
        stream: source from which to read data
        assert_length: if not None, assert required value
        assert_array_index: if not None, assert required value
        stream_readers: list of function taking a stream and returning something

    Data structure to be read:
        UINT32 - length
        UINT32 - array_index
        [TYPE_1, ... TYPE_N] - as requested
        UINT8 -- REUQIRED, NOT RETURENED

    Returns:
        [
        length
        OPTIONAL: array_index
        OPTIONAL: [TYPE_1, ... TYPE_N]
        ]
    """

    length = read_uint32(stream, assert_length)
    array_index = read_uint32(stream, assert_array_index)

    result_list = [length]  # length; almost always something needed
    if assert_array_index is None:
        result_list.append(array_index)

    # if there is a list of reader functions, apply them to extract data
    if stream_readers is not None:
        for reader in stream_readers:
            result_list.append(reader(stream))

    # last, ensure a null byte terminator; we do not return it
    read_uint8(stream, 0)

    return result_list


# ============================================
#
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
