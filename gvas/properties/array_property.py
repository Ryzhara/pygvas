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
from ..gvas_types import Guid
from ..utils import *

from .graphical_types import (
    is_special_struct,
    get_special_struct_instance,
)


@dataclass
class ArrayProperty(PropertyTrait):
    """A property that holds an array of values"""

    property_type: str = ""
    field_name: Optional[str] = None
    type_name: Optional[str] = None
    guid: Optional[Guid] = None
    values: List[Any] = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.guid is None:
            self.guid = Guid()

    @classmethod
    def new(
        cls,
        property_type: str,
        field_name: Optional[str] = None,
        type_name: Optional[str] = None,
        guid: Optional[Guid] = None,
    ) -> "ArrayProperty":
        """Create a new array property"""
        return cls(
            property_type=property_type,
            field_name=field_name,
            type_name=type_name,
            guid=guid or Guid(),
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
        property_count = struct.unpack("<I", stream.read(4))[0]
        # print(f"Found {property_count=}")

        self.values = []  # prepare storage

        if self.property_type == "StructProperty":
            # Read field type_name
            self.field_name = read_string(stream)

            # Read structure sub/generic type
            array_member_property_type = read_string(stream)

            # print(f"Found StructProperty {array_member_property_type=}")
            assert (
                array_member_property_type == self.property_type
            ), f"Property array member type mismatch: {array_member_property_type} != {self.property_type}"

            # Read properties size
            # TODO: add check for byte count
            properties_size = struct.unpack("<Q", stream.read(8))[0]

            self.type_name = read_string(stream)

            self.guid = read_guid_with_terminator(stream)

            for _ in range(property_count):
                if is_special_struct(self.type_name):
                    # print(f"Array: Reading instance of {self.type_name}")
                    new_array_property = get_special_struct_instance(self.type_name)
                    new_array_property.read(stream)
                    self.values.append(new_array_property)
                else:
                    new_array_property = StructProperty(self.property_type)
                    new_array_property.read_body(stream)
                    self.values.append(new_array_property)

        elif self.property_type == "Guid":
            for _ in range(property_count):
                self.values.append(Guid.from_bytes(stream.read(16)))

        # we probably  need to handle more things in detail? read the code
        # case "Guid", "DateTime", "Quat", "Vector", "Rotator", etc:
        #     pass
        elif self.property_type in [
            "StrProperty",
            "ObjectProperty",
        ]:
            for _ in range(property_count):
                string_element = read_string(stream)
                self.values.append(string_element)

        elif self.property_type == "ByteProperty":
            # this is an array of bytes, so just make it a thing
            new_array_property = Property.new(
                stream,
                self.property_type,
                include_header=False,
                suggested_length=property_count,
            )
            self.values.append(new_array_property)

        elif self.property_type in [
            "BoolProperty",
            "Int8Property",
            "UInt8Property",
            "UInt8Property",
            "Int16Property",
            "UInt16Property",
            "Int32Property",
            "UInt32Property",
            "IntProperty",
            "Int64Property",
            "UInt64Property",
            "FloatProperty",
            "DoubleProperty",
        ]:
            for _ in range(property_count):
                match self.property_type:
                    case "BoolProperty":
                        self.values.append(read_bool(stream))
                    case "Int8Property":
                        self.values.append(read_int8(stream))
                    case "UInt8Property":
                        self.values.append(read_uint8(stream))
                    case "UInt8Property":
                        self.values.append(read_uint8(stream))
                    case "Int16Property":
                        self.values.append(read_int16(stream))
                    case "UInt16Property":
                        self.values.append(read_uint16(stream))
                    case "IntProperty":  # backward compatibility
                        self.values.append(read_int32(stream))
                    case "Int32Property":
                        self.values.append(read_int32(stream))
                    case "UInt32Property":
                        self.values.append(read_uint32(stream))
                    case "Int64Property":
                        self.values.append(read_int64(stream))
                    case "UInt64Property":
                        self.values.append(read_uint64(stream))
                    case "FloatProperty":
                        self.values.append(read_float(stream))
                    case "DoubleProperty":
                        self.values.append(read_double(stream))

        elif self.property_type in ["TextProperty"]:
            # capture the thing as a blob for now
            new_array_property = Property.new(
                stream, self.property_type, include_header=False
            )
            self.values.append(new_array_property.value)

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
        array_property_byte_count_location = array_bytes
        array_bytes += array_buffer.write(struct.pack("<I", 0))  # TBD total byte count
        array_bytes += array_buffer.write(struct.pack("<I", 0))  # index

        array_bytes += write_string(array_buffer, self.property_type)

        # header terminator null byte
        array_bytes += array_buffer.write(struct.pack("<B", 0))
        # ====== END OF HEADER ==============

        properties_start = array_bytes

        # property_count, or number of elements in the array
        property_count = len(self.values)
        array_bytes += array_buffer.write(struct.pack("<I", property_count))
        # print(f"\tWriting array: {property_count=}")

        # Handle struct properties
        if self.property_type == "StructProperty":

            array_bytes += write_string(array_buffer, self.field_name)

            # Write property type again
            array_bytes += write_string(array_buffer, self.property_type)

            struct_byte_count_location = array_buffer.tell()
            array_bytes += array_buffer.write(struct.pack("<I", 0))
            array_bytes += array_buffer.write(struct.pack("<I", 0))

            array_bytes += write_string(array_buffer, self.type_name)
            array_bytes += write_guid_with_terminator(array_buffer, self.guid)

            # Write properties to array_buffer
            start = array_buffer.tell()
            for struct_property in self.values:
                if is_special_struct(self.type_name):
                    print(f"Array: writing instance of {self.type_name}")
                    array_bytes += struct_property.write(array_buffer)
                else:
                    array_bytes += struct_property.write(
                        array_buffer, include_header=False
                    )

            end = array_buffer.tell()

            # write total bytes in structs
            struct_properties_bytes = end - start
            array_buffer.seek(struct_byte_count_location)
            array_buffer.write(struct.pack("<I", struct_properties_bytes))

        elif self.property_type == "Guid":
            for value in self.values:
                array_bytes += array_buffer.write(value.to_bytes())

        elif self.property_type in [
            "StrProperty",
            "ObjectProperty",
        ]:
            # some of these are "FString" types; not sure if those are handled correctly
            for string_value in self.values:
                array_bytes += write_string(array_buffer, string_value)

        elif self.property_type == "ByteProperty":
            # this is an array of bytes, so just make it a thing
            for byte_property in self.values:
                if type(byte_property.value.value) is int:
                    write_uint8(array_buffer, byte_property.value)
                elif type(byte_property.value.value) is bytes:
                    write_bytes(array_buffer, byte_property.value.value)
                else:
                    raise ValueError(f"Invalid type for type value in: {self}")

        elif self.property_type in [
            "BoolProperty",
            "Int8Property",
            "ByteProperty",
            "UInt8Property",
            "Int16Property",
            "UInt16Property",
            "Int32Property",
            "UInt32Property",
            "IntProperty",
            "Int64Property",
            "UInt64Property",
            "FloatProperty",
            "DoubleProperty",
        ]:
            for value in self.values:
                match self.property_type:
                    case "BoolProperty":
                        array_bytes += array_buffer.write(struct.pack("?", value))
                    case "Int8Property":
                        array_bytes += array_buffer.write(struct.pack("b", value))
                    case "UInt8Property":
                        array_bytes += array_buffer.write(struct.pack("B", value))
                    case "Int16Property":
                        array_bytes += array_buffer.write(struct.pack("<h", value))
                    case "UInt16Property":
                        array_bytes += array_buffer.write(struct.pack("<H", value))
                    case "IntProperty":  # backward compatibility
                        array_bytes += array_buffer.write(struct.pack("<i", value))
                    case "Int32Property":
                        array_bytes += array_buffer.write(struct.pack("<i", value))
                    case "UInt32Property":
                        array_bytes += array_buffer.write(struct.pack("<I", value))
                    case "Int64Property":
                        array_bytes += array_buffer.write(struct.pack("<q", value))
                    case "UInt64Property":
                        array_bytes += array_buffer.write(struct.pack("<Q", value))
                    case "FloatProperty":
                        array_bytes += array_buffer.write(struct.pack("<f", value))
                    case "DoubleProperty":
                        array_bytes += array_buffer.write(struct.pack("<d", value))

        elif self.property_type in [
            "Vector",
            "Vector2",
            "Rotator",
            "Quat",
            "DateTime",
            "Timespan",
            "LinearColor",
            "IntPoint",
        ]:
            assert False, f"Encountered unhandled property type {self.property_type}"

        else:  # catch everything else
            # Write array elements
            for array_property in self.values:
                array_bytes += array_property.write(array_buffer, include_header=False)

        properties_end = array_bytes
        array_property_byte_count = properties_end - properties_start

        # Write total byte count size
        array_buffer.seek(array_property_byte_count_location)
        array_buffer.write(struct.pack("<I", array_property_byte_count))

        # now write the whole thing to the stream
        stream.write(array_buffer.getvalue())

        return array_bytes
