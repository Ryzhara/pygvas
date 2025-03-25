from dataclasses import dataclass
from typing import Optional, BinaryIO
import datetime

"""
    "DateTime",
    "Timespan",
"""


@dataclass
class DateTime:
    value: datetime.datetime

    @classmethod
    def new(cls, value: datetime.datetime) -> "DateTime":
        """Create a new IntPoint property"""
        return cls(value)


@dataclass
class IntPoint:
    x: int
    y: int

    @classmethod
    def new(cls, x: int, y: int) -> "IntPoint":
        """Create a new IntPoint property"""
        return cls(x, y)


@dataclass
class LinearColor:
    a: float
    b: float
    g: float
    r: float

    @classmethod
    def new(cls, a: float, b: float, g: float, r: float) -> "LinearColor":
        """Create a new LinearColor property - can be F or D"""
        return cls(a, b, g, r)


@dataclass
class Rotator:
    pitch: float
    yaw: float
    roll: float

    @classmethod
    def new(cls, pitch: float, yaw: float, roll: float) -> "Rotator":
        """Create a new Rotator property - can be F or D"""
        return cls(pitch, yaw, roll)


@dataclass
class Quat:
    x: float
    y: float
    z: float
    w: float

    @classmethod
    def new(cls, x: float, y: float, z: float, w: float) -> "Quat":
        """Create a new LinearColor property - can be F or D"""
        return cls(x, y, z, w)


@dataclass
class Vector:
    x: float
    y: float
    z: float

    @classmethod
    def new(cls, x: float, y: float, z: float) -> "Vector":
        """Create a new Vector(3) property - can be F or D"""
        return cls(x, y, z)


# In Python, floats are actually doubles
@dataclass
class Vector2:
    x: float
    y: float

    @classmethod
    def new(cls, x: float, y: float) -> "Vector2":
        """Create a new VectorD property"""
        return cls(x, y)
