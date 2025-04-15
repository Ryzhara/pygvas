"""
Struct property implementation for GVAS
Python port of struct_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from io import BytesIO
from typing import Optional

from pydantic import field_serializer
from pydantic.dataclasses import dataclass

from .property_base import (
    PropertyFactory,
    PropertyTrait,
)
from .standard_types import (
    is_special_struct,
    get_special_struct_instance,
    StandardStructTrait,
)
from ..utils import *
from gvas.properties import *


@dataclass
class StructProperty(PropertyTrait):
    """A property that holds structured data"""

    type: str = "StructProperty"
    guid: Optional[uuid.UUID] = None
    type_name: Optional[str] = None
    value: Union[
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
        ArrayProperty,
        EnumProperty,
        TextProperty,
        MapProperty,
        NameProperty,
        SetProperty,
        StrProperty,
        "StructProperty",
        # ObjectProperty,
        # FieldPath,
        # FieldPathProperty,
        # MulticastInlineDelegateProperty,
        # MulticastSparseDelegateProperty,
        # DelegateProperty,
    ] = None

    @field_serializer("guid")
    def serialize_guid(self, value: uuid.UUID):
        if type(value) is uuid.UUID:
            return guid_to_str(value)
        return value

    def read(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> None:
        """Read struct from stream"""
        length = 0
        type_name_override = None
        if include_header:
            length, self.type_name, self.guid = read_standard_header(
                stream, stream_readers=[read_string, read_guid]
            )
        if self.guid == ZERO_GUID:
            self.guid = None

        #  This modelled after the line in RUST file struct_property.rs
        #  "StructProperty" => match include_header {
        #    true => Ok(StructProperty::read(cursor, include_header, options)?.into()),
        else:
            # see if we have to override the type name
            struct_path = SerializationTools.get_context_path()
            type_name_override = SerializationTools.hints.get(struct_path, None)

        with ByteCountValidator(
            stream, length, do_validation=include_header
        ) as _validator:
            self.read_body(stream, type_name_override)

    def read_body(self, stream: BinaryIO, type_name_override: str = None) -> None:
        """we must check for type_name in the special (graphical) structure types and
        then invoke reading that, vs reading a custom, arbitrary body as below"""

        deserialize_type = type_name_override or self.type_name

        if is_special_struct(deserialize_type):
            property_value = get_special_struct_instance(deserialize_type)
            property_value.read(stream)
            self.value = property_value

        else:  # fully custom
            self.value = {}
            while True:
                if (property_name := read_string(stream)) == "None":
                    break
                with ContextScopeTracker(property_name) as _scope_tracker:
                    property_type = read_string(stream)
                    property_value = PropertyFactory.new(
                        stream, property_type, include_header=True
                    )
                    self.value[property_name] = property_value

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write struct to stream"""

        body_buffer = BytesIO()
        body_bytes = 0

        if self.value:
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
                data_to_write=[self.type_name, self.guid or ZERO_GUID],
            )

        # Write buffer contents with optional header
        bytes_written += write_bytes(stream, body_buffer.getvalue())

        return bytes_written
