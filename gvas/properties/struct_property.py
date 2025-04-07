"""
Struct property implementation for GVAS
Python port of struct_property.rs

Key differences from Rust version:
- Uses dataclasses for struct types
- Simplified type handling
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, BinaryIO, List
from io import BytesIO

from .standard_types import (
    is_special_struct,
    get_special_struct_instance,
    SpecialStructTrait,
)
from .property_base import (
    Property,
    PropertyTrait,
    SerializationTools,
    ContextScopeTracker,
)
from ..utils import *


@dataclass
class StructPropertyValue:
    """Value stored in a struct property"""

    type_name: str
    properties: Dict[str, Property] | SpecialStructTrait

    @classmethod
    def new(cls, type_name: str, properties=None) -> "StructPropertyValue":
        """Create a new struct property value"""
        return cls(type_name=type_name, properties=properties or {})


@dataclass
class StructProperty(PropertyTrait):
    """A property that holds structured data"""

    type = "StructProperty"
    type_name: str = ""
    guid: uuid = None
    value: Optional[StructPropertyValue] = None

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

        #  This modelled after the line in RUST file struct_property.rs
        #  "StructProperty" => match include_header {
        #    true => Ok(StructProperty::read(cursor, include_header, options)?.into()),
        else:
            # see if we have to override the type name
            struct_path = SerializationTools.get_path()
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
            self.value = StructPropertyValue(deserialize_type, property_value)

        else:  # fully custom
            self.value = StructPropertyValue(deserialize_type, {})
            while True:
                if (property_name := read_string(stream)) == "None":
                    break
                with ContextScopeTracker(property_name) as _scope_tracker:
                    property_type = read_string(stream)
                    property_value = Property.new(
                        stream, property_type, include_header=True
                    )
                    self.value.properties[property_name] = property_value

    def write(
        self,
        stream: BinaryIO,
        include_header: bool = True,
    ) -> int:
        """Write struct to stream"""

        body_buffer = BytesIO()
        body_bytes = 0

        if self.value:
            if isinstance(self.value.properties, SpecialStructTrait):
                body_bytes += self.value.properties.write(body_buffer)
            else:
                for (
                    property_name,
                    property_value,
                ) in self.value.properties.items():
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
                data_to_write=[self.type_name, self.guid],
            )

        # Write buffer contents with optional header
        bytes_written += write_bytes(stream, body_buffer.getvalue())

        return bytes_written
