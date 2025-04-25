"""
String property implementations for GVAS
Python port of set_property.rs, map_property.rs, struct_property.rs, array_property.rs
"""

from io import BytesIO
from typing import ClassVar, Annotated, Literal

from pydantic import field_serializer, Discriminator
from pydantic.dataclasses import dataclass

from gvas.gvas_utils import *
from gvas.properties.delegate_property import (
    MulticastInlineDelegateProperty,
    MulticastSparseDelegateProperty,
    DelegateProperty,
)
from gvas.properties.enum_property import EnumProperty
from gvas.properties.field_path_property import FieldPath, FieldPathProperty
from gvas.properties.name_property import NameProperty
from gvas.properties.numerical_property import (
    BoolProperty,
    ByteProperty,
    FloatProperty,
    DoubleProperty,
    IntProperty,
    Int8Property,
    UInt8Property,
    Int16Property,
    UInt16Property,
    Int32Property,
    UInt32Property,
    Int64Property,
    UInt64Property,
)
from gvas.properties.object_property import ObjectProperty
from gvas.properties.property_base import PropertyFactory, PropertyTrait
from gvas.properties.standard_structs import (
    is_standard_struct,
    get_standard_struct_instance,
    StandardStructTrait,
    DateTimeStruct,
    GuidStruct,
    TimespanStruct,
    IntPointStruct,
    LinearColorStruct,
    RotatorStruct,
    QuatStruct,
    VectorStruct,
    Vector2DStruct,
)
from gvas.properties.str_property import StrProperty
from gvas.properties.text_property import TextProperty

UNREAL_ENGINE_PROPERTIES = Annotated[
    Union[
        BoolProperty,
        ByteProperty,
        FloatProperty,
        DoubleProperty,
        IntProperty,
        Int8Property,
        UInt8Property,
        Int16Property,
        UInt16Property,
        Int32Property,
        UInt32Property,
        Int64Property,
        UInt64Property,
        FloatProperty,
        DoubleProperty,
        DateTimeStruct,
        GuidStruct,
        TimespanStruct,
        IntPointStruct,
        LinearColorStruct,
        RotatorStruct,
        QuatStruct,
        VectorStruct,
        Vector2DStruct,
        "SetProperty",
        "MapProperty",
        "StructProperty",
        "ArrayProperty",
        EnumProperty,
        TextProperty,
        NameProperty,
        StrProperty,
        ObjectProperty,
        FieldPath,
        FieldPathProperty,
        MulticastInlineDelegateProperty,
        MulticastSparseDelegateProperty,
        DelegateProperty,
    ],
    Discriminator("type"),
]


@dataclass
class MapProperty(PropertyTrait):
    """
    A property that holds a key-value mapping
    For MapProperty, we store tuples of (key, value) to avoid complexity of
    trying to boil things down to immutable types and then reverse that.
    That DOES mean the end user can encounter collisions if they do it wrong.

    And the tuples get serialized as a list of two items: [key, value]
    """

    KEY_TYPE = Union[str, UNREAL_ENGINE_PROPERTIES]
    VALUE_TYPE = Union[bool, int, str, UNREAL_ENGINE_PROPERTIES]

    type: Literal["MapProperty"] = "MapProperty"
    key_type: KEY_TYPE = None
    value_type: VALUE_TYPE = None
    allocation_flags: int = 0
    values: list[tuple[KEY_TYPE, VALUE_TYPE]] = None

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read map from stream"""
        length = 0
        if include_header:
            # content_length = self.read_header(stream)
            length, self.key_type, self.value_type = read_standard_header(
                stream, stream_readers=[read_string, read_string]
            )

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            # Read number of entries
            self.allocation_flags = read_uint32(stream)
            element_count = read_uint32(stream)

            # Read entries
            self.values = []
            for _ in range(element_count):
                with ContextScopeTracker("Key") as _scope_tracker:
                    key_property = PropertyFactory.create_and_deserialize(
                        stream, self.key_type, include_header=False
                    )
                with ContextScopeTracker("Value") as _scope_tracker:
                    value_property = PropertyFactory.create_and_deserialize(
                        stream, self.value_type, include_header=False
                    )
                try:
                    self.values.append((key_property, value_property))
                except Exception as e:
                    print(f"error: {e}")
                    raise e

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write map to stream"""

        body_buffer = BytesIO()
        buffer_bytes_written = 0

        # START OF BODY
        body_start = body_buffer.tell()
        buffer_bytes_written += write_uint32(body_buffer, self.allocation_flags)
        element_count = len(self.values)
        buffer_bytes_written += write_uint32(body_buffer, element_count)

        # Write entries
        for key, value in self.values:
            buffer_bytes_written += key.write(body_buffer, include_header=False)
            buffer_bytes_written += value.write(body_buffer, include_header=False)

        body_end = body_buffer.tell()
        body_bytes = body_end - body_start
        assert body_bytes == buffer_bytes_written

        stream_bytes_written = 0
        if include_header:
            stream_bytes_written += write_standard_header(
                stream,
                "MapProperty",
                length=body_bytes,
                data_to_write=[self.key_type, self.value_type],
            )

        stream_bytes_written += write_bytes(stream, body_buffer.getvalue())

        # now write the temp buffer to the stream
        return stream_bytes_written


@dataclass
class SetProperty(PropertyTrait):
    """A property that stores a set of properties"""

    type: Literal["SetProperty"] = "SetProperty"
    property_type: Optional[str] = None
    allocation_flags: int = 0
    properties: Optional[list[UNREAL_ENGINE_PROPERTIES]] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = []

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read set from stream"""
        if not include_header:
            raise DeserializeError.invalid_property(
                "SetProperty is not supported in arrays", stream.tell()
            )

        length, self.property_type = read_standard_header(
            stream, stream_readers=[read_string]
        )

        with ByteCountValidator(stream, length, do_validation=True) as _validator:
            self.allocation_flags = read_uint32(stream)
            element_count = read_uint32(stream)

            self.properties = []
            if element_count > 0:
                total_bytes_per_property = (length - 8) // element_count
                for _ in range(element_count):
                    property_instance = PropertyFactory.create_and_deserialize(
                        stream,
                        self.property_type,
                        include_header=False,
                        suggested_length=total_bytes_per_property,
                    )
                    self.properties.append(property_instance)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write set to stream"""

        # Create the body in a temporary buffer
        body_buffer = BytesIO()
        body_bytes = 0

        # Write allocation flags and element count
        body_bytes += write_uint32(body_buffer, self.allocation_flags)
        body_bytes += write_uint32(body_buffer, len(self.properties))

        # Write properties
        for set_property in self.properties:
            body_bytes += set_property.write(body_buffer, include_header=False)

        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream,
                "SetProperty",
                length=body_bytes,
                data_to_write=[self.property_type],
            )

        # Write buffer contents
        bytes_written += write_bytes(stream, body_buffer.getvalue())
        return bytes_written


@dataclass
class StructProperty(PropertyTrait):
    """A property that holds structured data"""

    type: Literal["StructProperty"] = "StructProperty"
    guid: Optional[uuid.UUID] = None
    type_name: Optional[str] = None
    value: Union[
        dict[str, UNREAL_ENGINE_PROPERTIES],
        # these must be here because they can be "special" types.
        # These can also appear inside the dictionary.
        DateTimeStruct,
        GuidStruct,
        TimespanStruct,
        IntPointStruct,
        LinearColorStruct,
        RotatorStruct,
        QuatStruct,
        VectorStruct,
        Vector2DStruct,
    ] = None

    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID):
        if type(value) is uuid.UUID:
            return guid_to_str(value)
        return value

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
        """Read struct from stream"""
        length = 0
        if include_header:
            length, self.type_name, self.guid = read_standard_header(
                stream, stream_readers=[read_string, read_guid]
            )

        if self.guid == MagicConstants.ZERO_GUID:
            self.guid = None

        # # see if we have to override the type name
        # hint_context_path = ContextScopeTracker.get_context_path()
        # hint_type_override: Union[str, dict] = ContextScopeTracker.deserialization_hints.get(
        #     hint_context_path, None
        # )

        hint_type_override = ContextScopeTracker.get_hint_for_context()

        # either we test for self.type_name or we use the override
        deserialize_type = hint_type_override or self.type_name

        # unwrap this version
        if type(deserialize_type) is dict:
            # context may be, for example, the number of bytes in a "ByteBlobStruct"
            deserialize_type = hint_type_override["type"]
            ContextScopeTracker.set_hint_context(hint_type_override["context"])

        # may have been a str, but the dict must also result in a "type" str
        standard_struct_override = None
        if is_standard_struct(deserialize_type):
            standard_struct_override = get_standard_struct_instance(deserialize_type)

        # It turns out that we almost always want to default to a custom struct, here.
        # I leave this commentary here for future reference, in case we wish to change
        # this choice.
        # if deserialize_type is None:
        #     deserialize_type = "StructProperty"
        #           or maybe
        #     self.type_name = "CustomStruct"
        #           or just
        #     raise DeserializeError.missing_hint(
        #         self.type, ContextScopeTracker.get_context_path(), stream.tell()
        #     )

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.read_body(stream, standard_struct_override)

    def read_body(
        self, stream: BinaryIO, standard_struct_override: StandardStructTrait = None
    ) -> None:
        """we must check for type_name in the special (graphical) structure types and
        then invoke reading that, vs reading a custom, arbitrary body as below"""

        if standard_struct_override and isinstance(
            standard_struct_override, StandardStructTrait
        ):
            standard_struct_override.read(stream)
            self.value = standard_struct_override

        else:  # fully custom is the default
            self.value = {}
            while True:
                if (property_name := read_string(stream)) == "None":
                    break
                with ContextScopeTracker(property_name) as _scope_tracker:
                    property_type = read_string(stream)
                    property_value = PropertyFactory.create_and_deserialize(
                        stream, property_type, include_header=True
                    )
                    self.value[property_name] = property_value

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
        """Write struct to stream"""

        body_buffer = BytesIO()
        body_bytes = 0

        if self.value is not None:
            if isinstance(self.value, StandardStructTrait):
                body_bytes += self.value.write(body_buffer)
            else:
                for (
                    property_name,
                    property_value,
                ) in self.value.items():
                    body_bytes += write_string(body_buffer, property_name)
                    body_bytes += property_value.write(body_buffer, include_header=True)
                # Write "None" terminator
                body_bytes += write_string(body_buffer, "None")

        assert body_bytes == len(body_buffer.getvalue())

        bytes_written = 0
        if include_header:
            bytes_written += write_standard_header(
                stream,
                "StructProperty",
                length=body_bytes,
                data_to_write=[
                    self.type_name or "",
                    self.guid or MagicConstants.ZERO_GUID,
                ],
            )

        # Write buffer contents with optional header
        bytes_written += write_bytes(stream, body_buffer.getvalue())

        return bytes_written


@dataclass
class ArrayProperty(PropertyTrait):
    """A property that holds an array of values"""

    # class variable is not serialized
    bare_readers: ClassVar[dict[str, Callable[[BinaryIO], Any]]] = {
        "StrProperty": read_string,
        "NameProperty": read_string,
        "EnumProperty": read_string,
        "GuidStruct": read_guid,
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

    # class variable is not serialized
    bare_writers: ClassVar[dict[str, Callable[[BinaryIO, Any], int]]] = {
        "StrProperty": write_string,
        "NameProperty": write_string,
        "EnumProperty": write_string,
        "GuidStruct": write_guid,
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

    type: Literal["ArrayProperty"] = "ArrayProperty"
    field_name: Optional[str] = None
    type_name: Optional[str] = None
    property_type: Optional[str] = None
    guid: Optional[uuid.UUID] = None  # often nothing but zeros
    values: Union[
        str,
        list[
            Union[
                # property types
                UNREAL_ENGINE_PROPERTIES,
                # bare types
                str,
                int,
                float,
                bool,
                bytes,
                uuid.UUID,
                None,
            ],
        ],
    ] = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        elif type(self.values) is str:
            self.values = bytes.fromhex(self.values)

    # Guidance to pydantic
    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID):
        if type(value) is uuid.UUID:
            return guid_to_str(value)
        return value

    # Guidance to pydantic
    @field_serializer("values")
    def serialize_values(
        self, values: [str, bytes, list, PropertyTrait, StandardStructTrait], field_info
    ):
        if type(values) is bytes:
            return values.hex()
        return values

    def read(self, stream: BinaryIO, include_header: bool = True) -> None:
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

        self.values = []  # prepare storage

        if self.property_type == "StructProperty":

            # This embedded struct header differs slightly by repeating the field_name.
            self.field_name = read_string(stream)

            # ArrayProperty does not use a ContextScopeTracker!:
            member_type = read_string(stream)
            assert (
                member_type == self.property_type
            ), f"PropertyFactory array member type mismatch: {member_type} != {self.property_type}"

            expected_byte_count, self.type_name, self.guid = read_standard_header(
                stream, stream_readers=[read_string, read_guid]
            )
            if self.guid == MagicConstants.ZERO_GUID:
                self.guid = None

            with ByteCountValidator(
                stream, expected_byte_count, do_validation=True
            ) as _validator:
                for _ in range(property_count):
                    if is_standard_struct(self.type_name):
                        array_property = get_standard_struct_instance(self.type_name)
                        array_property.read(stream)
                        self.values.append(array_property)
                    else:
                        array_property = StructProperty(self.property_type)
                        array_property.read_body(stream)
                        self.values.append(array_property)

        elif self.property_type == "ByteProperty":
            # read it all as one blob

            suggested_length = (length - 4) if length >= 4 else 0
            suggested_count = suggested_length / property_count if property_count else 1
            if suggested_count == 1:
                self.values = read_bytes(stream, suggested_length)
            else:
                array_property = PropertyFactory.create_and_deserialize(
                    stream,
                    self.property_type,
                    include_header=False,
                    suggested_length=suggested_length,
                )
                self.values.append(array_property)

        # some data types are read without any additional metadata
        elif self.property_type in self.bare_readers.keys():
            bare_type_reader = self.bare_readers[self.property_type]
            for _ in range(property_count):
                self.values.append(bare_type_reader(stream))

        else:  # catchall
            for _ in range(property_count):
                array_property = PropertyFactory.create_and_deserialize(
                    stream, self.property_type, include_header=False
                )
                self.values.append(array_property)

    def write(self, stream: BinaryIO, include_header: bool = True) -> int:
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

        properties_body_start = array_buffer.tell()
        array_bytes += write_uint32(array_buffer, property_count)

        # Handle struct properties
        if self.property_type == "StructProperty":
            body_buffer = BytesIO()
            body_bytes = 0
            for struct_property in self.values:
                if is_standard_struct(self.type_name):
                    body_bytes += struct_property.write(body_buffer)
                else:
                    body_bytes += struct_property.write(
                        body_buffer, include_header=False
                    )
            assert body_bytes == len(body_buffer.getvalue())

            # WRITE HEADER extra part
            array_bytes += write_string(array_buffer, self.field_name)
            array_bytes += write_standard_header(
                array_buffer,
                self.property_type,
                length=body_bytes,
                data_to_write=[self.type_name, self.guid or MagicConstants.ZERO_GUID],
            )

            array_bytes += write_bytes(array_buffer, body_buffer.getvalue())

        elif self.property_type == "ByteProperty" and type(self.values) is bytes:
            array_bytes += write_bytes(array_buffer, self.values)
            # else we fall to the catchall

        elif self.property_type in self.bare_writers.keys():
            bare_type_writer = self.bare_writers[self.property_type]
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
