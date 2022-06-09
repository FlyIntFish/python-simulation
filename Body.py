from utility import *
from Sprite import Sprite

class Body:
    def __init__(self, r : float, mass : float, color : str, position = Vector(), initialSpeed = Vector()):
        self._mass = mass
        self._velocity = initialSpeed
        self._acceleration = Vector()
        self._sprite = Sprite(r, color, position)

    @property
    def mass(self) -> float:
        return self._mass

    @mass.setter
    def mass(self, newMass):
        if newMass <= 0:
            raise ValueError("Mass has to be positive value")
        self._mass = newMass

    @property
    def radius(self) -> float:
        return self.sprite.radius

    @radius.setter
    def radius(self, newRadius):
        if newRadius <= 0:
            raise ValueError("Radius has to be positive value")
        self.sprite.radius = newRadius

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def position(self) -> Vector:
        return self._sprite.position

    @property
    def boundingBoxCoords(self) -> tuple:
        return self._sprite.getBoundingBoxCoords()

    @property
    def color(self) -> str:
        return self._sprite.color

    @property
    def sprite(self):
        return self._sprite

    def __updateAcceleration(self, force : Vector):
        deltaAcc = force / self._mass
        self._acceleration = deltaAcc

    def __updateVelocity(self, deltaTime: float):
        self._velocity += self._acceleration * deltaTime

    def updatePhysics(self, force: Vector, deltaTime: float):
        self.__updateAcceleration(force)
        self.__updateVelocity(deltaTime)

    def updatePosition(self, deltaTime: float):
        self._sprite.move(self._velocity * deltaTime)

    def toDict(self):
        return {
            "mass" : self._mass,
            "radius" : self._sprite.radius,
            "color" : self._sprite.color,
            "posX" : self._sprite.position.x,
            "posY" : self._sprite.position.y,
            "velX" : self._velocity.x,
            "velY" : self._velocity.y
        }

    @staticmethod
    def createFromDict(data):
        return Body(
            int(data["radius"]),
            int(data["mass"]),
            data["color"],
            Vector(int(data["posX"]), int(data["posY"])),
            Vector(int(data["velX"]), int(data["velY"]))
        )