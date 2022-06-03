from multiprocessing.sharedctypes import Value
from turtle import distance
from utility import *

# Position defines center of sprite, i.e. center of circle 
class Sprite:
    def __init__(self, r, color, initPosition = Vector(0,0)):
        self._color = color
        self._radius = r
        self._position = initPosition

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, newPos : Vector):
        self._position = newPos
    
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, newColor: str):
        self._color = newColor

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, newRadius : float):
        if newRadius <= 0:
            raise ValueError("Radius has to be positive value")
        self._radius = newRadius

    def move(self, offset : Vector):
        self._position += offset

    def getBoundingBoxCoords(self):
        return (
            self.position.x - self._radius/2,    # left upper corner X
            self.position.y - self._radius/2,    # left upper corner Y
            self.position.x + self._radius/2,    # right bottom corner X
            self.position.y + self._radius/2,    # right bottom corner Y
        )

    @staticmethod
    def collision(sprite1, sprite2) -> bool:
        return Vector.distance(sprite1.position, sprite2.position).len() <= sprite1.radius + sprite2.radius
