"""
PropertyFactory type implementations for GVAS
"""

from .numerical_property import (
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
from .property_base import PropertyFactory, PropertyTrait

from .aggregators import SetProperty, MapProperty, ArrayProperty, StructProperty

from .enum_property import EnumProperty
from .text_property import TextProperty
from .name_property import NameProperty
from .str_property import StrProperty
from .object_property import ObjectProperty
from .field_path_property import FieldPath, FieldPathProperty
from .delegate_property import (
    MulticastInlineDelegateProperty,
    MulticastSparseDelegateProperty,
    DelegateProperty,
)

__all__ = [
    "BoolProperty",
    "ByteProperty",
    "FloatProperty",
    "DoubleProperty",
    "IntProperty",
    "Int8Property",
    "UInt8Property",
    "Int16Property",
    "UInt16Property",
    "Int32Property",
    "UInt32Property",
    "Int64Property",
    "UInt64Property",
    "PropertyFactory",
    "PropertyTrait",
    "ArrayProperty",
    "StructProperty",
    "SetProperty",
    "MapProperty",
    "EnumProperty",
    "TextProperty",
    "NameProperty",
    "StrProperty",
    "ObjectProperty",
    "FieldPath",
    "FieldPathProperty",
    "MulticastInlineDelegateProperty",
    "MulticastSparseDelegateProperty",
    "DelegateProperty",
]
