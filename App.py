import json
import tkinter as tk
import copy
from Gui import Gui
from Body import *
import Colors

class CelestialBody:

    __maxPointsInTrajectory = 3
    @classmethod
    def setPointsInTrajectory(cls, value):
        if value < 0:
            raise ValueError("MaxPointsInTrajectory cannot be lower than 1")
        cls.__maxPointsInTrajectory = value

    def __init__(self, body, app):
        self.__body = body
        self.__trajectory = []              # list of points ( list(Vector) )
        self.__trajectoryIDs = []
        self.__app = app                    # handler to app

    def updateTrajectory(self):
        self.__trajectory.append(copy.deepcopy(self.__body.position))
        while len(self.__trajectory) > CelestialBody.__maxPointsInTrajectory:
            self.__app.removeShape(self.__trajectoryIDs[0])
            self.__trajectory.pop(0)
            self.__trajectoryIDs.pop(0)
        if len(self.__trajectory) >= 3:     # at least two points to create trajectory
            coords = (
                self.__trajectory[-2].x,
                self.__trajectory[-2].y,
                self.__trajectory[-1].x,
                self.__trajectory[-1].y
            )
            id = self.__app.addLine(coords, self.__body.color)
            self.__trajectoryIDs.append(id)

    def eraseTrajectory(self):
        for i in self.__trajectoryIDs:
            self.__app.removeShape(i)
        self.__trajectoryIDs = []
        self.__trajectory = []

    @property
    def body(self):
        return self.__body

    def toDict(self):
        return self.__body.toDict()

class App:

    def __init__(self):
        self.__celestialBodies = {}             # int : CelestialBody
        self.__maxDeltaTime = 1000.0/20.0       # we don't want to go below 20FPS to avoid inaccurate calculations
        self.__speedFactor = 5
        self.__lastTime = None                  # time since last __resetClock method
        self.__timeAcc = 0                      # accumulator for time
        self.__pause = False
        self.__resetClock()
        self.__MAX_SPEED_FACTOR = 40
        self.__UPDATE_TRAJECTORY_DT = 0.2
        self.__MAX_TRAJECTORY_POINTS = 750
        self.__MIN_TRAJECTORY_POINTS = 3
        self.__timeToUpdateTrajectory = self.__UPDATE_TRAJECTORY_DT
        self.__newBodyVelocity = Vector()
        self.__newBodyRadius = 10
        self.__fps = 0
        self.__newBodyMass = 100
        self.__MIN_INIT_BODY_VELOCITY = -30.0
        self.__MAX_INIT_BODY_VELOCITY = 30.0
        self.__MAX_BODY_RADIUS = 40
        self.__MAX_BODY_MASS = 10**6
        self.__secondsToUpdateFpsCounter = 1


    @staticmethod
    def setPointsInTrajectory(value):
        CelestialBody.setPointsInTrajectory(value)

    @staticmethod
    def calculateForceVector(body1, body2) -> Vector:
        deltaS = body2.position - body1.position
        distanceValue =  Vector.distance(body1.position, body2.position).len()
        if distanceValue < body1.radius + body2.radius:
            distanceValue = body1.radius + body2.radius
        forceValue = Const.getGValue() * body1.mass * body2.mass / distanceValue
        force = Vector(
            forceValue * deltaS.x / distanceValue,
            forceValue * deltaS.y / distanceValue
        )
        return force

    @property
    def newBodyRadius(self):
        return self.__newBodyRadius

    @newBodyRadius.setter
    def newBodyRadius(self, value):
        if value <= 0:
            raise ValueError("Radius cannot be less than 0")
        if value > self.MAX_BODY_RADIUS:
            raise ValueError(f'Radius canot be greater than {self.MAX_BODY_RADIUS}')
        self.__newBodyRadius = value

    @property
    def fps(self):
        return self.__fps

    @property
    def newBodyMass(self):
        return self.__newBodyMass

    @newBodyMass.setter
    def newBodyMass(self, value):
        if value <= 0:
            raise ValueError("Mass cannot be less than 0")
        if value > self.MAX_BODY_MASS:
            raise ValueError(f'Mass canot be greater than {self.MAX_BODY_MASS}')
        self.__newBodyMass = value

    @property
    def newBodyVelocity(self):
        return self.__newBodyVelocity

    @newBodyVelocity.setter
    def newBodyVelocity(self, velocity : Vector):
        if (velocity.x < self.__MIN_INIT_BODY_VELOCITY
            or velocity.y < self.__MIN_INIT_BODY_VELOCITY
            or velocity.x > self.__MAX_INIT_BODY_VELOCITY
            or velocity.y > self.__MAX_INIT_BODY_VELOCITY
        ):
            raise ValueError(f'initial velocity for new body is out of range [{self.__MIN_INIT_BODY_VELOCITY}, {self.__MAX_INIT_BODY_VELOCITY}]')
        self.__newBodyVelocity = velocity
        print(self.__newBodyVelocity)

    @property
    def MIN_INIT_BODY_VELOCITY(self):
        return self.__MIN_INIT_BODY_VELOCITY

    @property
    def MAX_INIT_BODY_VELOCITY(self):
        return self.__MAX_INIT_BODY_VELOCITY

    @property
    def MAX_BODY_RADIUS(self):
        return self.__MAX_BODY_RADIUS

    @property
    def MAX_BODY_MASS(self):
        return self.__MAX_BODY_MASS

    @property
    def MIN_TRAJECTORY_POINTS(self):
        return self.__MIN_TRAJECTORY_POINTS

    @MIN_TRAJECTORY_POINTS.setter
    def MIN_TRAJECTORY_POINTS(self, value):
        if self.MIN_TRAJECTORY_POINTS:
            raise ValueError("MIN_TRAJECTORY_POINTS is constant and cannot be changed")
        elif value < 3:
            raise ValueError("MIN_TRAJECTORY_POINTS cannot be lower than 3")
        self.MIN_TRAJECTORY_POINTS = value

    @property
    def MAX_TRAJECTORY_POINTS(self):
        return self.__MAX_TRAJECTORY_POINTS

    @MAX_TRAJECTORY_POINTS.setter
    def MAX_TRAJECTORY_POINTS(self, value):
        if self.MAX_TRAJECTORY_POINTS:
            raise ValueError("MAX_TRAJECTORY_POINTS is constant and cannot be changed")
        elif value < 1:
            raise ValueError("MAX_TRAJECTORY_POINTS cannot be lower than 1")
        self.MAX_TRAJECTORY_POINTS = value

    @property
    def MAX_SPEED_FACTOR(self):
        return self.__MAX_SPEED_FACTOR

    @MAX_SPEED_FACTOR.setter
    def MAX_SPEED_FACTOR(self, value):
        if self.__MAX_SPEED_FACTOR:
            raise ValueError("MAX_SPEED_FACTOR is constant and cannot be changed")
        elif value < 1:
            raise ValueError("MAX_SPEED_FACTOR cannot be lower than 1")
        self.__MAX_SPEED_FACTOR = value

    @property
    def speedFactor(self):
        return self.__speedFactor

    @speedFactor.setter
    def speedFactor(self, value):
        if value < 1:
            self.__speedFactor = 1
        elif value > self.__MAX_SPEED_FACTOR:
            self.__speedFactor = self.MAX_SPEED_FACTOR
        else:
            self.__speedFactor = value

    def assignGui(self, gui : Gui):             # handler to gui instance
        self.__gui = gui

    def pause(self):
        self.__pause = True

    def resume(self):
        self.__pause = False
        self.__resetClock()

    def removeAllBodies(self):
        for id,body in self.__celestialBodies.items():
            body.eraseTrajectory()
            self.removeShape(id)
        self.__celestialBodies.clear()

    def __resetClock(self):
        self.__lastTime = time.time()

    def addCelestialBody(self, radius: float, mass: float, position: Vector, color: str, initSpeed: Vector):
        body = Body(radius, mass, color, copy.deepcopy(position), copy.deepcopy(initSpeed))
        id = self.__gui.addSprite(body._sprite)
        self.__celestialBodies.update({id : CelestialBody(body, self)})

    def addExistingCelestialBody(self, cbody : CelestialBody):
        id = self.__gui.addSprite(cbody.body.sprite)
        self.__celestialBodies.update({id : CelestialBody(cbody.body, self)})

    def __calculateForce(self, bodyId: int):
        force = Vector()
        for id, cbody in self.__celestialBodies.items():
            if bodyId != id:
                force += App.calculateForceVector(self.__celestialBodies[bodyId].body, cbody.body)
        return force


    def __resetTrajectoryTimer(self):
        self.__timeToUpdateTrajectory = self.__UPDATE_TRAJECTORY_DT / self.__speedFactor        # the faster simulation goes, the rarer we

                                                                                                # want to update trajectory
    def __updateFpsCounter(self, deltaTime):
        self.__secondsToUpdateFpsCounter -= deltaTime
        if self.__secondsToUpdateFpsCounter <= 0:
            self.__secondsToUpdateFpsCounter = 1.0
            self.__gui.setStatusBarText("Fps: "+str(self.__fps))
            self.__fps = 0
        self.__fps += 1

    def update(self):
        deltaTime = secondsSince(self.__lastTime)
        self.__updateFpsCounter(deltaTime)
        self.__resetClock()
        if not self.__pause:
            self.__timeAcc += deltaTime
            self.__timeToUpdateTrajectory -= deltaTime
            if self.__timeAcc > self.__maxDeltaTime:
                self.__timeAcc = self.__maxDeltaTime
            self.__timeAcc *= self.__speedFactor

            if (self.__timeToUpdateTrajectory <= 0):
                self.__updateTrajectory()
                self.__resetTrajectoryTimer()

            self.__updatePhysics()
            self.__updateGui()
            self.__timeAcc = 0
        self.__gui.guiLoop(self.update)

    def __updateTrajectory(self):
        for cbody in self.__celestialBodies.values():
            cbody.updateTrajectory()

    def __updatePhysics(self):
        for id, cbody in self.__celestialBodies.items():
            force = self.__calculateForce(id)
            cbody.body.updatePhysics(force, self.__timeAcc)
        for cbody in self.__celestialBodies.values():
            cbody.body.updatePosition(self.__timeAcc)

    def __updateGui(self):
        for id, cbody in self.__celestialBodies.items():
            self.__gui.setSpritePosition(id, cbody.body.boundingBoxCoords)

    def addLine(self, coords_, color_) -> int:         # return shape id
        return self.__gui.addLine(coords_, color_)

    def removeShape(self, shapeId):
        self.__gui.removeShape(shapeId)

    def addUserDefinedCelestialBody(self, position_ : Vector):
        self.addCelestialBody(
            radius=self.__newBodyRadius,
            mass=self.__newBodyMass,
            position=position_,
            color=Colors.getRandomColor(),
            initSpeed=self.__newBodyVelocity
        )

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            data = file.read()
        file.close()
        self.__createBodiesFromJsonFile(data)

    def __createBodiesFromJsonFile(self, data):
        data = data.split('\n')
        for i in data:
            if i:
                try:
                    parsed = json.loads(i)
                    self.addExistingCelestialBody(
                        CelestialBody(Body.createFromDict(parsed), app))
                except:
                    print('err')


    def __createJsonData(self):
        output = ""
        for i in self.__celestialBodies.values():
            output += json.dumps(i.toDict()) + "\n"
        print(output)
        return output

    def saveCurrentStateToFile(self, filename):
        data = self.__createJsonData()
        with open(filename, 'w') as file:
            file.write(data)




if __name__ == "__main__":
    root = tk.Tk()
    root.wm_geometry("1500x700+0+0")
    root.resizable(0,0)

    app = App()
    gui = Gui(root, app)
    app.assignGui(gui)
    app.update()

    root.mainloop()
