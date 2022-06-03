from __future__ import annotations
import math
import time

class Const:
    __GValue = 0.004
    __GValueFactor = 1.0

    @classmethod
    def getGValue(cls):
        return cls.__GValue * cls.__GValueFactor


class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __add__(self, vector):
        return Vector(
            self.x + vector.x,
            self.y + vector.y
        )

    def __mul__(self, scalar : float):
        return Vector(
            self.x * scalar,
            self.y * scalar
        )

    def __sub__(self, vector):
        return Vector(
            self.x - vector.x,
            self.y - vector.y
        )

    def __truediv__(self, scalar : float) -> Vector:
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector(self.x / scalar, self.y / scalar)

    def __iadd__(self, vector):
        self.x += vector.x
        self.y += vector.y
        return self

    def __isub__(self, vector):
        self.x -= vector.x
        self.y -= vector.y
        return self

    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    def __str__(self):
        return f'[{self.x},{self.y}]'

    def toPair(self):
        return (self.x,self.y)

    def len(self):
        return math.sqrt(self.x**2 + self.y**2)

    # considering points as vectors
    @staticmethod
    def distance(point1 : Vector, point2 : Vector) -> Vector:
        return Vector(math.sqrt((point1.x - point2.x)**2), math.sqrt((point1.y - point2.y)**2))


def secondsSince(time_):
    return (time.time() - time_)

    

    