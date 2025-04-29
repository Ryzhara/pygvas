import datetime
import struct
import uuid
from typing import BinaryIO, Any, Callable, Union, Optional

from pygvas.error import DeserializeError, SerializeError


# ============================================
# Encapsulate constants as class variables
class MagicConstants:
    # Used in a lot of places
    ZERO_GUID = uuid.UUID(int=0)
    # Magic number that appears at the start of every GVAS file
    GVAS_MAGIC = b"GVAS"
    # Magic number for Palworld files. Not sure why RUST uses a null byte terminator on this constant
    PLZ_MAGIC = b"PlZ"
    MIN_STRING_LENGTH = -131072  # 0x020000
    MAX_STRING_LENGTH = 131072  # 0xFE0000


# ============================================
# Do NOT make this @dataclass because then our class variable syntax is wrong. ;)
class UnitTestGlobals:
    _unit_tests_running: bool = False

    # ============= UNIT TESTING HELPER ====================
    @classmethod
    def set_inside_unit_tests(cls) -> None:
        cls._unit_tests_running = True

    @classmethod
    def inside_unit_tests(cls) -> bool:
        return cls._unit_tests_running


# ============================================
# Do NOT make this @dataclass because then our class variable syntax is wrong. ;)
# The following is adpabted from the Rust code:
# ## Hints
# If your file fails while parsing with a `DeserializeError` error you probably need deserialization_hints.
# When a struct is stored inside ArrayProperty/SetProperty/MapProperty in GvasFile it does not contain type annotations.
# This means that a library parsing the file must know the type beforehand. That's why you need deserialization_hints.
class ContextScopeTracker:
    _context_stack: list[str] = []
    _deserialization_hints: dict[str, Union[str, dict[str, Any]]] = {}
    # this one is for the remote case when you want the ByteBlobStruct or similar.
    _hint_context: dict[str, Any] = {}

    # ============= CONTEXT TRACKING ====================
    @classmethod
    def push_context_step(cls, step: str) -> None:
        cls._context_stack.append(step)

    @classmethod
    def pop_context_step(cls) -> None:
        cls._context_stack.pop()

    @classmethod
    def get_context_path(cls) -> str:
        return ".".join(cls._context_stack)

    # ============= PROCESSING HINTS ====================

    @classmethod
    def set_deserialization_hints(
        cls, deserialization_hints: dict[str, Union[str, dict[str, Any]]]
    ):
        """For those files that need deserialization_hints for successful deserialization."""
        cls._deserialization_hints = deserialization_hints

    @classmethod
    def add_deserialization_hint_for_current_context(cls, hint_type):
        current_context_path = cls.get_context_path()
        cls._deserialization_hints[current_context_path] = hint_type

    @classmethod
    def get_hint_for_context(cls) -> Union[str, Union[str, dict[str, Any]]]:
        hint_context_path = cls.get_context_path()
        hint_type_override = cls._deserialization_hints.get(hint_context_path, None)
        return hint_type_override

    # ============= MOST UNUSUAL CASE HANDLING ====================
    @classmethod
    def set_hint_context(cls, context: dict[str, Any]):
        """Some deserialization_hints are more than just a type name. ByteBlobStruct requires a length, for example."""
        cls._hint_context = context

    @classmethod
    def get_hint_context(cls) -> dict[str, Any]:
        return cls._hint_context

    # ============= IMPLEMENTATION FOR PYTHON CONTEXT MANAGER ====================
    def __init__(self, context: str):
        # a snapshot for debugging
        self.parent_context = ContextScopeTracker.get_context_path()
        self.context = context

    def __enter__(self):
        ContextScopeTracker.push_context_step(self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if not UnitTestGlobals.inside_unit_tests():
                print(
                    f"An exception of type {exc_type} occurred: {exc_val} with context\n\t{ContextScopeTracker.get_context_path()}"
                )
                import traceback
                import sys

                traceback.print_exception(exc_type, exc_val, exc_tb, file=sys.stdout)
            return False

        ContextScopeTracker.pop_context_step()
        return True


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
            if not UnitTestGlobals.inside_unit_tests():
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


def datetime_to_str(dt: int) -> str:
    # datetime.datetime.fromtimestamp takes time in seconds since January 1, 1970, 00:00:00 (UTC) as a floating-point number
    # FDateTime type represents dates and times as ticks (0.1 microseconds) since January 1, 0001
    # seconds_since_1_1_00001 = 6_392_264_799_600
    try:
        ticks_per_second = 10_000_000.0
        seconds = dt / ticks_per_second
        datetime_str = (
            datetime.datetime.min + datetime.timedelta(seconds=seconds)
        ).strftime("%d/%m/%Y %H:%M:%S.%f")
    except Exception as e:
        print(f"Cant process {dt=} : {e}")
        datetime_str = str(dt)

    return datetime_str


def timespan_to_str(tspan: int) -> str:
    return str(datetime.timedelta(milliseconds=(tspan / 1000.0)))


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
    try:
        value = struct.unpack(format_str, stream.read(width))[0]
    except struct.error:
        raise DeserializeError(f"Unpack error {struct.error}: {error_msg}")

    if assert_value is not None:
        if value != assert_value:
            raise DeserializeError(
                f"{error_msg+': ' if error_msg is not None else ""}Expected value {value} != {assert_value} at {position=}"
            )
    return value


# ============= TOOLS FOR READS/WRITES ========================
#
def guid_from_uint32x4(uint1: int, uint2: int, uint3: int, uint4: int) -> uuid:
    byte_buffer = struct.pack("<IIII", uint1, uint2, uint3, uint4)
    return uuid.UUID(bytes=byte_buffer)


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
            f"Invalid read_bool32bit value {value} at {stream.tell()} with context {ContextScopeTracker.get_context_path()}",
        )
    return True if value else False


# ============================================
#
def write_bool32bit(stream: BinaryIO, value: [int, bool]) -> int:
    if value not in [0, 1, True, False]:
        raise SerializeError.invalid_value(
            f"Invalid write_bool32bit value {value} at {stream.tell()} with context {ContextScopeTracker.get_context_path()}"
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
def read_bytes(stream: BinaryIO, byte_count: int) -> bytes:
    return stream.read(byte_count)


# ============================================
#
def write_bytes(stream: BinaryIO, value_bytes: bytes) -> int:
    return stream.write(value_bytes)


# ============================================
#
def peek_valid_string(stream: BinaryIO) -> bool:
    start_position = stream.tell()
    try:
        _valid_string = read_string(stream)
        return True
    except Exception as e:
        return False
    finally:
        stream.seek(start_position)


# ============================================
#
def read_string(stream: BinaryIO) -> str | None:
    """Read a string from the stream
    prefix is uint32: length, followed by UTF-8 byte encoded string
    """

    if (length := read_int32(stream)) == 0:
        return None  # ""

    if (
        not MagicConstants.MIN_STRING_LENGTH
        <= length
        <= MagicConstants.MAX_STRING_LENGTH
    ):
        position = stream.tell() - 4
        raise SerializeError.invalid_value(
            f"String length is out of range {MagicConstants.MIN_STRING_LENGTH} <= {length} <= {MagicConstants.MAX_STRING_LENGTH} around {position=} with context {ContextScopeTracker.get_context_path()}"
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
                f"Suspicious UTF-16 bytes are really ascii: {value_bytes} at {position=}"
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
    # null -- if we read an empty string, we write an empty string
    if value is None:
        return write_uint32(stream, 0)

    bytes_written = 0
    # Note: bytes have not null terminator
    if value.isascii():
        length = len(value) + 1
        value_bytes = value.encode("utf-8")
        bytes_written += write_int32(stream, length)
        bytes_written += write_bytes(stream, value_bytes)
        bytes_written += write_uint8(stream, 0)  # manual terminator
    else:
        value_words_as_bytes = value.encode("utf-16-le")
        length = len(value) + 1
        bytes_written += write_int32(stream, -length)
        bytes_written += write_bytes(stream, value_words_as_bytes)
        bytes_written += write_uint16(stream, 0)  # manual terminator

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
    assert_length: Optional[int] = None,
    assert_array_index: Optional[int] = 0,
    stream_readers: Optional[
        list[Callable[[BinaryIO], Any]]
    ] = None,  # read after array index and before terminator
) -> list[Any]:
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
        UINT8 -- REQUIRED BUT NOT RETURNED

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
    length: int = None,
    array_index: int = 0,
    data_to_write: list[
        Union[str, uuid.UUID]
    ] = None,  # only accommodate str and guid for now
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
