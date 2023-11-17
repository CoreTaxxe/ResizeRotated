import math
from dataclasses import dataclass
from enum import IntEnum


class Handle(IntEnum):
    TOP_RIGHT: int = 0
    MIDDLE_RIGHT: int = 1
    BOTTOM_RIGHT: int = 2

    TOP_LEFT: int = 3
    MIDDLE_LEFT: int = 4
    BOTTOM_LEFT: int = 5

    TOP_MIDDLE: int = 6
    BOTTOM_MIDDLE: int = 7


@dataclass(frozen=True)
class Point(object):
    x: float
    y: float

    @property
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def __getitem__(self, index: int) -> float:
        """
        get item at index
        :param index: index to get
        :return: value at index (0: x, 1: y)
        """
        if not isinstance(index, int):
            raise TypeError("Unsupported index type.")

        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError(f"Point index {index} out of range (0-1)")

    def __iter__(self) -> float:
        """
        Make point iterable
        :return: x, y
        """
        yield self.x
        yield self.y


@dataclass(frozen=True)
class Rectangle(object):
    x: float
    y: float
    width: float
    height: float

    @property
    def pcenter(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    @property
    def size(self) -> tuple[float, float]:
        return self.width, self.height

    @property
    def ppos(self) -> Point:
        return Point(self.x, self.y)

    @property
    def pos(self) -> tuple[float, float]:
        return self.x, self.y


def rotate(point: Point, origin: Point, angle: float) -> Point:
    """
    rotate point around origin
    :param point: point to rotate
    :param origin: origin to rotate around
    :param angle: angle to rotate in degree
    :return: rotated point
    """
    angle = math.radians(angle)
    return Point(
(point.x - origin.x) * math.cos(angle) - (point.y - origin.y) * math.sin(angle) + origin.x,
(point.x - origin.x) * math.sin(angle) + (point.y - origin.y) * math.cos(angle) + origin.y,
)


def adjust_points(corner_a: Point, corner_c: Point, center: Point, angle: float) -> tuple[Point, Point]:
    """
    adjust points around new center
    :param corner_a: corner A of rect
    :param corner_c: corner C of rect (should be the diagonal corner)
    :param center: center to rotate around
    :param angle: angle to rotate by
    :return: A', C'
    """
    rotated_a: Point = rotate(corner_a, center, angle)

    new_center: Point = Point(
        (rotated_a.x + corner_c.x) / 2,
        (rotated_a.y + corner_c.y) / 2
    )
    return rotate(rotated_a, new_center, -angle), rotate(corner_c, new_center, -angle)


def get_adjusted_point(rectangle: Rectangle, target: Point, angle: float, handle: Handle) -> tuple[Point, Point]:
    """
    return the adjusted a and c points
    :param rectangle: rectangle to adjust
    :param target: target position of handle
    :param angle: angle to rotate by
    :param handle: target handle
    :return: A', C'
    """
    normal_c: Point = rotate(target, rectangle.pcenter, -angle)
    match handle:
        case Handle.TOP_RIGHT:
            return Point(rectangle.x, rectangle.y), target

        case Handle.MIDDLE_RIGHT:
            interpolated_d: Point = Point(normal_c.x, rectangle.y + rectangle.height)
            return Point(rectangle.x, rectangle.y), rotate(interpolated_d, rectangle.pcenter, angle)

        case Handle.BOTTOM_RIGHT:
            return Point(rectangle.x, rectangle.y + rectangle.height), target

        case Handle.TOP_LEFT:
            return Point(rectangle.x + rectangle.width, rectangle.y), target

        case Handle.MIDDLE_LEFT:
            interpolated_d: Point = Point(normal_c.x, rectangle.y + rectangle.height)
            return Point(rectangle.x + rectangle.width, rectangle.y), rotate(interpolated_d, rectangle.pcenter, angle)

        case Handle.BOTTOM_LEFT:
            return Point(rectangle.x + rectangle.width, rectangle.y + rectangle.height), target

        case Handle.TOP_MIDDLE:
            interpolated_d: Point = Point(rectangle.x + rectangle.width, normal_c.y)
            return Point(rectangle.x, rectangle.y), rotate(interpolated_d, rectangle.pcenter, angle)

        case Handle.BOTTOM_MIDDLE:
            interpolated_d: Point = Point(rectangle.x + rectangle.width, normal_c.y)
            return Point(rectangle.x, rectangle.y + rectangle.height), rotate(interpolated_d, rectangle.pcenter, angle)


def to_rect(a: Point, c: Point, handle: Handle) -> Rectangle:
    """
    convert point to rect depending on handle
    :param a: fixed corner
    :param c: target corner
    :param handle: handle
    :return: bottom left adjusted Rectangle
    """
    match handle:
        case Handle.TOP_RIGHT | Handle.MIDDLE_RIGHT | Handle.TOP_MIDDLE:
            return Rectangle(*a, c.x - a.x, c.y - a.y)

        case Handle.BOTTOM_RIGHT:
            height: float = a.y - c.y
            return Rectangle(a.x, a.y - height, c.x - a.x, height)

        case Handle.TOP_LEFT | Handle.MIDDLE_LEFT:
            height: float = c.y - a.y
            return Rectangle(c.x, c.y - height, a.x - c.x, height)

        case Handle.BOTTOM_LEFT:
            return Rectangle(c.x, c.y, a.x - c.x, a.y - c.y)

        case Handle.BOTTOM_MIDDLE:
            return Rectangle(a.x, c.y, c.x - a.x, a.y - c.y)
        