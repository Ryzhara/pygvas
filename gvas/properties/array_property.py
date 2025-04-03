"""
Array property implementation for GVAS
Python port of array_property.rs

Key differences from Rust version:
- Uses Python lists instead of Vec
- Simplified type handling
"""

from dataclasses import dataclass
from typing import List, Optional, Any, BinaryIO
from io import BytesIO

from .property_base import Property, PropertyTrait, SerializationHints
from .struct_property import StructProperty
from ..utils import *

from .standard_types import (
    is_special_struct,
    get_special_struct_instance,
)
from ..utils import read_int16, read_int64

g_bare_type_readers = {
    "StrProperty": read_string,
    "GuidProperty": read_guid,
    "BoolProperty": read_bool,
    "Int8Property": read_int8,
    "UInt8Property": read_uint8,
    "Int16Property": read_int16,
    "UInt16Property": read_uint16,
    "Int32Property": read_int32,
    "UInt32Property": read_uint32,
    "IntProperty": read_int32,  # backward compatibility
    "Int64Property": read_int64,
    "UInt64Property": read_uint64,
    "FloatProperty": read_float,
    "DoubleProperty": read_double,
}

g_bare_type_writers = {
    "StrProperty": write_string,
    "GuidProperty": write_guid,
    "BoolProperty": write_bool,
    "Int8Property": write_int8,
    "UInt8Property": write_uint8,
    "Int16Property": write_int16,
    "UInt16Property": write_uint16,
    "Int32Property": write_int32,
    "UInt32Property": write_uint32,
    "IntProperty": write_int32,  # backward compatibility
    "Int64Property": write_int64,
    "UInt64Property": write_uint64,
    "FloatProperty": write_float,
    "DoubleProperty": write_double,
}


@dataclass
class ArrayProperty(PropertyTrait):
    """A property that holds an array of values"""

    property_type: str = ""
    field_name: Optional[str] = None
    type_name: Optional[str] = None
    guid: Optional[uuid] = None
    values: List[Any] = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.guid is None:
            self.guid = uuid.UUID(int=0)

    @classmethod
    def new(
        cls,
        property_type: str,
        field_name: Optional[str] = None,
        type_name: Optional[str] = None,
        guid: Optional[uuid] = None,
    ) -> "ArrayProperty":
        """Create a new array property"""
        return cls(
            property_type=property_type,
            field_name=field_name,
            type_name=type_name,
            guid=guid or uuid.UUID(int=0),
        )

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read array from stream"""
        if not include_header:
            raise DeserializeError.invalid_property(
                "ArrayProperty is not supported in arrays", stream.tell()
            )

        length = self.read_header(stream)
        start = stream.tell()
        SerializationHints.set_body_bytes(start, start + length)
        self.read_body(stream)
        end = stream.tell()
        SerializationHints.set_body_bytes(0, 0)
        if end - start != length:
            raise DeserializeError.invalid_value_size(length, end - start, start)

    def read_header(self, stream: BinaryIO) -> (int, str):
        # Read length and array index
        length = read_uint32(stream)
        _array_index = read_uint32(stream, 0)
        self.property_type = read_string(stream)
        _header_terminator = read_uint8(stream, 0)

        # END OF HEADER FOR ARRAY PROPERTY
        return length

    def read_body(self, stream: BinaryIO) -> None:

        # Read number of elements in the array
        property_count = read_uint32(stream)
        # print(f"Found {property_count=}")

        self.values = []  # prepare storage

        # don't read bytes that are not for you!
        if property_count == 0:
            return

        if self.property_type == "StructProperty":
            # Read field type_name
            self.field_name = read_string(stream)

            # Read structure sub/generic type
            member_property_type = read_string(stream)

            assert (
                member_property_type == self.property_type
            ), f"Property array member type mismatch: {member_property_type} != {self.property_type}"

            expected_byte_count = read_uint64(stream)
            self.type_name = read_string(stream)
            self.guid = read_guid_with_terminator(stream)

            start = stream.tell()
            for _ in range(property_count):
                if is_special_struct(self.type_name):
                    new_array_property = get_special_struct_instance(self.type_name)
                    new_array_property.read(stream)
                    self.values.append(new_array_property)
                else:
                    new_array_property = StructProperty(self.property_type)
                    new_array_property.read_body(stream)
                    self.values.append(new_array_property)
            end = stream.tell()
            assert (
                end - start == expected_byte_count
            ), DeserializeError.invalid_value_size(
                expected_byte_count, end - start, start
            )

        elif self.property_type in ["TextProperty"]:
            # capture the thing as a blob for now; ugly hack
            new_array_property = Property.new(
                stream, self.property_type, include_header=False
            )
            new_array_property.value.actual_text_count = property_count
            self.values.append(new_array_property.value)

        elif self.property_type == "ByteProperty":
            # this is an array of bytes, so just make it a thing
            new_array_property = Property.new(
                stream,
                self.property_type,
                include_header=False,
                suggested_length=property_count,
            )
            self.values.append(new_array_property)

        # some data types are read without any additional metadata
        elif self.property_type in g_bare_type_readers.keys():
            bare_type_reader = g_bare_type_readers[self.property_type]
            for _ in range(property_count):
                self.values.append(bare_type_reader(stream))

        else:  # catchall
            for _ in range(property_count):
                new_array_property = Property.new(
                    stream, self.property_type, include_header=False
                )
                self.values.append(new_array_property.value)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write array to stream"""
        if not include_header:
            raise SerializeError.invalid_property(
                "ArrayProperty is not supported in arrays"
            )

        # First write to a temporary array_buffer to get the length
        array_buffer = BytesIO()
        array_bytes = 0

        # Write property type
        array_bytes += write_string(array_buffer, "ArrayProperty")

        # ====== START OF HEADER ==============
        array_property_byte_count_location = array_buffer.tell()
        array_bytes += write_uint32(array_buffer, 0)  # TBD total byte count
        array_bytes += write_uint32(array_buffer, 0)  # index
        array_bytes += write_string(array_buffer, self.property_type)
        array_bytes += write_uint8(array_buffer, 0)  # header terminator null byte
        # ====== END OF HEADER ==============

        # property_count, or number of elements in the array
        property_count = len(self.values)
        # ugly, hacky fixup until we complete TextProperty implementation
        if self.property_type == "TextProperty" and property_count > 0:
            text_property: TextProperty = self.values[0]
            property_count = text_property.actual_text_count

        elif self.property_type == "ByteProperty" and property_count > 0:
            byte_property: ByteProperty = self.values[0]
            property_count = len(byte_property.value.value)

        properties_body_start = array_buffer.tell()
        array_bytes += write_uint32(array_buffer, property_count)

        # Handle struct properties
        if self.property_type == "StructProperty":
            # Write properties to array_buffer
            body_buffer = BytesIO()
            body_bytes = 0
            body_start = body_buffer.tell()
            for struct_property in self.values:
                if is_special_struct(self.type_name):
                    # print(f"Array: writing instance of {self.type_name}")
                    body_bytes += struct_property.write(body_buffer)
                else:
                    body_bytes += struct_property.write(
                        body_buffer, include_header=False
                    )
            body_end = body_buffer.tell()
            struct_body_bytes = body_end - body_start
            try:
                assert struct_body_bytes == len(body_buffer.getvalue())
            except AssertionError:
                pass

            # ALWAYS WRITE HEADER
            array_bytes += write_string(array_buffer, self.field_name)
            array_bytes += write_string(array_buffer, self.property_type)
            array_bytes += write_uint32(array_buffer, struct_body_bytes)
            array_bytes += write_uint32(array_buffer, 0)
            array_bytes += write_string(array_buffer, self.type_name)
            array_bytes += write_guid_with_terminator(array_buffer, self.guid)
            try:
                write_bytes(array_buffer, body_buffer.getvalue())
                array_bytes += struct_body_bytes
            except Exception as e:
                print(f"{e}")

        elif self.property_type in g_bare_type_writers.keys():
            bare_type_writer = g_bare_type_writers[self.property_type]
            for value in self.values:
                array_bytes += bare_type_writer(array_buffer, value)

        # elif self.property_type == "ByteProperty":
        #     # read was special, but write is not
        #     for value in self.values:
        #         array_bytes += value.write(array_buffer, include_header=False)
        else:  # catch everything else
            for value in self.values:
                array_bytes += value.write(array_buffer, include_header=False)

        properties_body_end = array_buffer.tell()
        assert (
            properties_body_end == array_bytes
        ), f"Counting is off in array! {array_bytes} != {properties_body_end}"
        properties_body_byte_count = properties_body_end - properties_body_start

        # Write total byte count size
        array_buffer.seek(array_property_byte_count_location)
        write_uint32(array_buffer, properties_body_byte_count)

        # now write the whole thing to the stream
        stream.write(array_buffer.getvalue())

        return array_bytes
