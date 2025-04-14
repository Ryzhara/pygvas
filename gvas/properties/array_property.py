"""
Array property implementation for GVAS
Python port of array_property.rs

Key differences from Rust version:
- Uses Python lists instead of Vec
- Simplified type handling
"""

from pydantic import field_serializer
from pydantic.dataclasses import dataclass
from typing import Optional
from io import BytesIO

from .property_base import (
    PropertyFactory,
    PropertyTrait,
)
from .struct_property import StructProperty
from ..utils import *

from .standard_types import (
    is_special_struct,
    get_special_struct_instance,
    StandardStructTrait,
)
from ..utils import read_int16, read_int64

g_bare_type_readers = {
    "StrProperty": read_string,
    "NameProperty": read_string,
    "EnumProperty": read_string,
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
    "NameProperty": write_string,
    "EnumProperty": write_string,
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

    type: str = "ArrayProperty"
    field_name: Optional[str] = None
    type_name: Optional[str] = None
    property_type: Optional[str] = None
    guid: Optional[uuid.UUID] = None  # often nothing but zeros
    values: Any = None  # [str, bytes, list, PropertyTrait, StandardStructTrait]

    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID):
        if type(value) is uuid.UUID:
            return guid_to_str(value)
        return value

    @field_serializer("values")
    def serialize_items(
        self, values: [str, bytes, list, PropertyTrait, StandardStructTrait]
    ):
        # print(f"ArrayProperty.serialize_items: {type(values)=}")
        if type(values) is bytes:
            return values.hex()
        return values

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

        length, self.property_type = read_standard_header(
            stream, stream_readers=[read_string]
        )

        start = stream.tell()
        self.read_body(stream, length)
        end = stream.tell()
        if end - start != length:
            raise DeserializeError.invalid_value_size(length, end - start, start)

    def read_body(self, stream: BinaryIO, length: int) -> None:

        # Read number of elements in the array
        property_count = read_uint32(stream)

        self.values: [
            str,
            bytes,
            list,
            PropertyTrait,
            StandardStructTrait,
        ] = []  # prepare storage

        if self.property_type == "StructProperty":

            # This embedded struct header differs slightly by repeating the field_name.
            self.field_name = read_string(stream)

            with ContextScopeTracker(self.field_name) as _scope_tracker:
                member_type = read_string(stream)
                assert (
                    member_type == self.property_type
                ), f"PropertyFactory array member type mismatch: {member_type} != {self.property_type}"

                expected_byte_count, self.type_name, self.guid = read_standard_header(
                    stream, stream_readers=[read_string, read_guid]
                )
                if self.guid == ZERO_GUID:
                    self.guid = None

                with ByteCountValidator(
                    stream, expected_byte_count, do_validation=True
                ) as _validator:
                    for _ in range(property_count):
                        if is_special_struct(self.type_name):
                            array_property = get_special_struct_instance(self.type_name)
                            array_property.read(stream)
                            self.values.append(array_property)
                        else:
                            array_property = StructProperty(self.property_type)
                            array_property.read_body(stream)
                            self.values.append(array_property)

        elif self.property_type == "TextProperty":
            for _ in range(property_count):
                array_property = PropertyFactory.new(
                    stream, self.property_type, include_header=False
                )
                self.values.append(array_property)

        elif self.property_type == "ByteProperty":
            # read it all as one blob

            suggested_length = (length - 4) if length >= 4 else 0
            suggested_count = suggested_length / property_count if property_count else 1
            if suggested_count == 1:
                self.values = read_bytes(stream, suggested_length)
            else:
                array_property = PropertyFactory.new(
                    stream,
                    self.property_type,
                    include_header=False,
                    suggested_length=suggested_length,
                )
                # We have must use actual_property_count because the sample files are inconsistent
                # regarding whether it is byte count or property count, or 1
                array_property.actual_property_count = property_count
                self.values.append(array_property)

        # some data types are read without any additional metadata
        elif self.property_type in g_bare_type_readers.keys():
            bare_type_reader = g_bare_type_readers[self.property_type]
            for _ in range(property_count):
                self.values.append(bare_type_reader(stream))

        else:  # catchall
            for _ in range(property_count):
                array_property = PropertyFactory.new(
                    stream, self.property_type, include_header=False
                )
                self.values.append(array_property)

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write array to stream"""
        if not include_header:
            raise SerializeError.invalid_value(
                "ArrayProperty is not supported in arrays"
            )

        # First write to a temporary array_buffer to get the length
        array_buffer = BytesIO()
        array_bytes = 0

        # property_count, or number of elements in the array
        property_count = len(self.values)

        # this method is MUCH better than serializing each byte independently. Who does that?!
        if self.property_type == "ByteProperty" and property_count > 0:
            if type(self.values) is list:
                byte_property: "ByteProperty" = self.values[0]
                property_count = byte_property.actual_property_count
            elif type(self.values) is bytes:
                property_count = len(self.values)

        properties_body_start = array_buffer.tell()
        array_bytes += write_uint32(array_buffer, property_count)

        # Handle struct properties
        if self.property_type == "StructProperty":
            body_buffer = BytesIO()
            body_bytes = 0
            for struct_property in self.values:
                if is_special_struct(self.type_name):
                    body_bytes += struct_property.write(body_buffer)
                else:
                    body_bytes += struct_property.write(
                        body_buffer, include_header=False
                    )
            assert body_bytes == len(body_buffer.getvalue())

            # WRITE HEADER extra part
            array_bytes += write_string(array_buffer, self.field_name)
            # write standard header
            array_bytes += write_standard_header(
                array_buffer,
                self.property_type,
                length=body_bytes,
                data_to_write=[self.type_name, self.guid or ZERO_GUID],
            )

            array_bytes += write_bytes(array_buffer, body_buffer.getvalue())

        elif self.property_type == "ByteProperty" and type(self.values) is bytes:
            array_bytes += write_bytes(array_buffer, self.values)
            # else we fall to the catchall

        elif self.property_type in g_bare_type_writers.keys():
            bare_type_writer = g_bare_type_writers[self.property_type]
            for value in self.values:
                array_bytes += bare_type_writer(array_buffer, value)

        else:  # catch everything else
            for value in self.values:
                try:
                    array_bytes += value.write(array_buffer, include_header=False)
                except Exception as e:
                    print(f"Failed to write {self.property_type}: {e}")

        properties_body_end = array_buffer.tell()
        assert (
            properties_body_end == array_bytes
        ), f"Counting is off in array! {array_bytes} != {properties_body_end}"
        properties_body_byte_count = properties_body_end - properties_body_start

        # ========================================
        # now that we have the body in a buffer, write the header and then the body
        header_bytes = write_standard_header(
            stream,
            "ArrayProperty",
            length=properties_body_byte_count,
            data_to_write=[self.property_type],
        )

        # now write the whole thing to the stream
        write_bytes(stream, array_buffer.getvalue())

        return header_bytes + array_bytes
