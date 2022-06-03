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
        return self._radius

    @radius.setter
    def radius(self, newRadius):
        if newRadius <= 0:
            raise ValueError("Radius has to be positive value")
        self.radius = newRadius

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

# body = Body(6, 100, "White", initialSpeed=Vector(20, 0))
# body2 = Body(3, 100, "Blue", Vector(100, 100))

# force = Body.calculateForceVector(body, body2)
# dt = 0.002
# print(body.position)
# body.updateAcceleration(force)
# body.updateVelocity(dt)
# body.updatePosition(dt)
# print(Sprite.collision(body._sprite, body2._sprite))
