import tkinter as tk
import copy
from Gui import Gui
from Body import *

class CelestialBody:

    __maxPointsInTrajectory = 300
    @classmethod
    def setMaxPointsInTrajectory(cls, value):
        if value < 1:
            raise ValueError("MaxPointsInTrajectory cannot be lower than 1")
        cls.__maxPointsInTrajectory = value

    def __init__(self, body, app):
        self.__body = body
        self.__trajectory = []              # list of points ( list(Vector) )
        self.__trajectoryIDs = []
        self.__app = app                    # handler to app
    
    def updateTrajectory(self):
        self.__trajectory.append(copy.deepcopy(self.__body.position))
        if len(self.__trajectory) > CelestialBody.__maxPointsInTrajectory:
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
            app.removeShape(i)
        self.__trajectoryIDs = []
        self.__trajectory = []

    @property
    def body(self):
        return self.__body

class App:

    def __init__(self):
        self.__celestialBodies = {}             # int : CelestialBody
        self.__maxDeltaTime = 1000.0/20.0       # we don't want to go below 20FPS to avoid inaccurate calculations
        self.__speedFactor = 5
        self.__lastTime = None                  # time since last __resetClock method
        self.__timeAcc = 0                      # accumulator for time
        self.__pause = False
        self.__resetClock()
        self.__MAX_SPEED_FACTOR = 20
        self.__UPDATE_TRAJECTORY_DT = 0.2  
        self.__MAX_TRAJECTORY_POINTS = 1000
        self.__timeToUpdateTrajectory = self.__UPDATE_TRAJECTORY_DT

    @property
    def MAX_TRAJECTORY_POINTS(self):
        return self.__MAX_SPEED_FACTOR

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
    
    def addCelestialBody(self, radius: float, mass: float, position: Vector, color = "white", initSpeed = Vector() ):
        body = Body(radius, mass, color, position, initSpeed)
        id = self.__gui.addSprite(body._sprite)
        self.__celestialBodies.update({id : CelestialBody(body, self)})

    # sila grawitacji jako dwuwymiarowy wektor [x,y], wynikowy wektor jest wzgledem pierwszego ciala,
    # tzn. jest to sila oddzialowujaca na to cialo przez body2
    @staticmethod
    def calculateForceVector(body1, body2) -> Vector:
        deltaS = body2.position - body1.position
        distanceValue =  Vector.distance(body1.position, body2.position).len()
        if distanceValue == 0:
            return Vector(0,0)
        forceValue = Const.getGValue() * body1.mass * body2.mass / distanceValue
        force = Vector(
            forceValue * deltaS.x / distanceValue,
            forceValue * deltaS.y / distanceValue
        )
        return force

    def __calculateForce(self, bodyId: int):
        force = Vector()
        for id, cbody in self.__celestialBodies.items():
            if bodyId != id:
                force += App.calculateForceVector(self.__celestialBodies[bodyId].body, cbody.body)
        return force


    def __resetTrajectoryTimer(self):
        self.__timeToUpdateTrajectory = self.__UPDATE_TRAJECTORY_DT / self.__speedFactor        # the faster simulation goes, the rarer we
                                                                                                # want to update trajectory 

    def update(self):
        deltaTime = secondsSince(self.__lastTime)
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

        
    
    

if __name__ == "__main__":
    root = tk.Tk()
    root.wm_geometry("1500x700+0+0")
    root.resizable(0,0)

    app = App()
    gui = Gui(root, app)
    app.assignGui(gui)
    app.addCelestialBody(20, 1, position=Vector(800,400), initSpeed=Vector(6.324,0))
    app.addCelestialBody(30, 10000, position=Vector(200,300), color="blue", initSpeed=Vector(2,0))
    app.addCelestialBody(20, 1, position=Vector(800,200), color="green", initSpeed=Vector(6.324,0))
    app.addCelestialBody(20, 10000, position=Vector(650,200),color="yellow", initSpeed=Vector(6.324,0))
    app.addCelestialBody(10, 1, position=Vector(200,350),color="grey", initSpeed=Vector(7.324,0))
    app.addCelestialBody(20, 1, position=Vector(340,250),color="violet", initSpeed=Vector(9.324,0))
    app.update()

    root.mainloop()
    