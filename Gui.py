from __future__ import annotations
import tkinter as tk
from tkinter import *
import os
from tkinter import filedialog
from tkinter import messagebox

from pyparsing import col
from utility import *
from tkinter.constants import NSEW

class Gui:

    __ElementsColors = {
        "toolbar" : "#F0F0F0",
        "canvas" : "#000000",
        "default_color" : "#FF00FF"
    }

    __textures_path = f'{os.getcwd()}\\textures\\'

    @classmethod
    def colorOf(cls, nameOfElement):
        if nameOfElement.lower() in cls.__ElementsColors.keys():
            return cls.__ElementsColors[nameOfElement]
        return cls.__ElementsColors["default_color"]

    def __init__(self, root, app : App):
        self.__VELOCITY_SLIDERS_LENGTH = 150
        self.__TIME_FACTOR_SLIDER_LENGTH = 100
        self.__app = app
        self.__root = root
        self.__menuBar = tk.Menu(self.__root)
        self.__initCanvas()
        self.__initMenuBar()
        self.__initOptionsBar()
        self.__initToolbar()
        self.__initStatusBar()
        self.__configureRootColumnsAndRows()

    def __createToolbar(self):
        self.__toolbar = tk.Frame(self.__root, background=Gui.colorOf("toolbar"))
        self.__toolbar.grid(row=1, column=0, columnspan=3, sticky=NSEW)

    def __initToolbar(self):
        self.__createToolbar()
        self.__addToolbarButtons()
        self.__initToolbarSliders()
        self.__initToolbarTextFields()

    def __initToolbarTextFields(self):
        self.__addToolbarFrameForTextFields()
        self.__addToolbarMassTextField()
        self.__addToolbarRadiusTextField()

    def __initStatusBar(self):
        self.__statusbar = tk.Label(self.__root, text="Running...",
                                       anchor=tk.W)
        self.__statusbar.grid(row=2, column=0, sticky=tk.EW)


    def __addToolbarButtons(self):
        self.__toolbar_images = []
        for image, command in (
                ("reload.png", self.__app.removeAllBodies),
                ("play-button.png", self.__app.resume),
                ("pause-button.png", self.__app.pause)):
            image = os.path.join(Gui.__textures_path, image)
            try:
                image = tk.PhotoImage(file=image)
                self.__toolbar_images.append(image)
                button = tk.Button(self.__toolbar, image=image,
                                        command=command)
                button.grid(row=0, column=self.__toolbar.grid_size()[0], sticky=NSEW)
            except tk.TclError as err:
                print(err)                                                  # problem with file
        self.__toolbar.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

    def __addToolbarFrameForSliders(self):
        self.__slidersToolbarFrame = tk.Frame(self.__toolbar)
        self.__slidersToolbarFrame.grid(row=0, column=self.__getToolbarNextColumn())

    def __getToolbarTextFieldsFrameNextColumn(self):
        return self.__textFieldsToolbarFrame.grid_size()[0]

    def __getToolbarNextColumn(self):
        return self.__toolbar.grid_size()[0]

    def __getToolbarSlidersFrameNextColumn(self):
        return self.__slidersToolbarFrame.grid_size()[0]

    def __addToolbarSlider(self, from__, to_, command_, labelText_, variable_, length_=None, resolution_=1):
        newColumn = self.__getToolbarSlidersFrameNextColumn()
        slider = tk.Scale(
            self.__slidersToolbarFrame,
            orient='horizontal',
            from_=from__,
            to=to_,
            command = command_,
            variable = variable_,
            length=length_,
            resolution=resolution_
        )
        slider.grid(row=0, column=newColumn)
        label = tk.Label(
            self.__slidersToolbarFrame,
            text=labelText_
        )
        label.grid(row=1, column=newColumn)

    def __addToolbarTimeFactorSlider(self):
        variable=tk.IntVar()
        self.__addToolbarSlider(
            from__=1,
            to_=self.__app.MAX_SPEED_FACTOR,
            command_=lambda event: setattr(self.__app, 'speedFactor', variable.get()),
            labelText_="Speed factor",
            variable_=variable,
            length_=self.__TIME_FACTOR_SLIDER_LENGTH
        )

    def __addToolbarTrajectoryPointsSlider(self):
        variable = tk.IntVar()
        self.__addToolbarSlider(
        from__=self.__app.MIN_TRAJECTORY_POINTS,
        to_=self.__app.MAX_TRAJECTORY_POINTS,
        command_=lambda event: self.__app.setPointsInTrajectory(variable.get()),
        labelText_="Trajectory length",
        variable_=variable,
        length_=self.__app.MAX_TRAJECTORY_POINTS/5
        )

    def __addToolbarInitHorizontalVelocitySlider(self):
        variable = tk.DoubleVar()
        self.__addToolbarSlider(
            from__=self.__app.MIN_INIT_BODY_VELOCITY,
            to_=self.__app.MAX_INIT_BODY_VELOCITY,
            command_=lambda event: setattr(self.__app, 'newBodyVelocity', Vector(variable.get(), self.__app.newBodyVelocity.y)),
            labelText_="X velocity",
            variable_=variable,
            resolution_=0.2,
            length_=self.__VELOCITY_SLIDERS_LENGTH
        )

    def __addToolbarInitVerticalVelocitySlider(self):
        variable = tk.DoubleVar()
        self.__addToolbarSlider(
            from__=self.__app.MIN_INIT_BODY_VELOCITY,
            to_=self.__app.MAX_INIT_BODY_VELOCITY,
            command_=lambda event: setattr(self.__app, 'newBodyVelocity', Vector(self.__app.newBodyVelocity.x, variable.get())),
            labelText_="Y velocity",
            variable_=variable,
            resolution_=0.2,
            length_=self.__VELOCITY_SLIDERS_LENGTH
        )

    def __addToolbarTextField(self, labelText):
        newColumn = self.__getToolbarTextFieldsFrameNextColumn()
        textField = tk.Entry(
            self.__textFieldsToolbarFrame
        )
        textField.grid(row=1, column=newColumn)
        label = tk.Label(
            self.__textFieldsToolbarFrame,
            text=labelText
        )
        label.grid(row=2, column=newColumn)
        return textField

    def __validateInput(self, field, minValue, maxValue, fieldName):
        try:
            val = int(field.get())
            if val < minValue:
                field.delete(0, tk.END)
                field.insert(0,f'{fieldName} has to be > {minValue}')
            elif val > maxValue:
                field.delete(0, tk.END)
                field.insert(0,f'{fieldName} has to be < {maxValue}')
            else:
                return True
            return False
        except:
            field.delete(0, tk.END)
            field.insert(0,'non-integer value passed')
            return False

    def __massTextFieldCallback(self, field):
        if self.__validateInput(field, 1, self.__app.MAX_BODY_MASS, "mass"):
            self.__app.newBodyMass = int(field.get())

    def __radiusTextFieldCallback(self, field):
        if self.__validateInput(field, 1, self.__app.MAX_BODY_RADIUS, "radius"):
            self.__app.newBodyRadius = int(field.get())

    def __addToolbarFrameForTextFields(self):
        self.__textFieldsToolbarFrame = tk.Frame(self.__toolbar)
        self.__textFieldsToolbarFrame.grid(row=0, column=self.__getToolbarNextColumn(), sticky=NSEW)
        self.__textFieldsToolbarFrame.rowconfigure(0, weight=1)
        self.__textFieldsToolbarFrame.rowconfigure(1, weight=1)
        self.__textFieldsToolbarFrame.rowconfigure(2, weight=1)

    def __addToolbarRadiusTextField(self):
        field = self.__addToolbarTextField(
            "Radius"
        )
        field.bind("<Return>", lambda event: self.__radiusTextFieldCallback(field))

    def __addToolbarMassTextField(self):
        field = self.__addToolbarTextField(
            "Mass"
        )
        field.bind("<Return>", lambda event: self.__massTextFieldCallback(field))

    def __initToolbarSliders(self):
        self.__addToolbarFrameForSliders()
        self.__addToolbarTimeFactorSlider()
        self.__addToolbarTrajectoryPointsSlider()
        self.__addToolbarInitHorizontalVelocitySlider()
        self.__addToolbarInitVerticalVelocitySlider()

    def __initOptionsBar(self):
        self.__root["menu"] = self.__menuBar
        fileMenu = tk.Menu(self.__menuBar)
        for label, command, shortcut_text, shortcut in (
                ("Clear", self.__app.removeAllBodies, "Ctrl+C", "<Control-c>"),
                ("Resume", self.__app.resume, "Ctrl+R", "<Control-r>"),
                ("Pause", self.__app.pause, "Ctrl+P", "<Control-p>")
                ):
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.__root.bind(shortcut, command)
        self.__menuBar.add_cascade(label="Options", menu=fileMenu, underline=0)

    def __initMenuBar(self):
        self.__root["menu"] = self.__menuBar
        fileMenu = tk.Menu(self.__menuBar)
        for label, command, shortcut_text, shortcut in (
                ("New...", self.__app.removeAllBodies, "Ctrl+N", "<Control-n>"),
                ("Open...", self.__loadFromFile, "Ctrl+O", "<Control-o>"),
                ("Save", self.__saveToFile, "Ctrl+S", "<Control-s>"),
                (None, None, None, None),
                ("Quit", self.quit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.__root.bind(shortcut, command)
        self.__menuBar.add_cascade(label="File", menu=fileMenu, underline=0)

    def __initCanvas(self):
        self.__canvas = tk.Canvas(self.__root, background=Gui.colorOf("canvas"))
        self.__canvas.bind("<Button-1>", lambda event: self.__app.addUserDefinedCelestialBody(position_=Vector(event.x, event.y)))
        self.__canvas.grid(row=1, column=0, padx=0, pady=0, sticky=NSEW)

    def __configureRootColumnsAndRows(self):
        self.__root.columnconfigure(0, weight=10)
        self.__root.rowconfigure(0, weight=1)
        self.__root.rowconfigure(1, weight=999)

    def __loadFromFile(self):
        filename = tk.filedialog.askopenfilename(parent=self.__root,
        title="Choose file:",
        filetypes=[("JSON files", ".json")])
        self.__app.loadFromFile(filename)

    def __saveToFile(self):
        filename = tk.filedialog.askopenfilename(parent=self.__root,
        title="Choose file:",
        filetypes=[("JSON files", ".json")])
        self.__app.saveCurrentStateToFile(filename)

    def guiLoop(self, func):
        self.__canvas.after(5, func)

    def addSprite(self, sprite : Sprite) -> int:
        return self.__canvas.create_oval(
            sprite.getBoundingBoxCoords(),
            fill = sprite.color
            )

    def setStatusBarText(self, text):
        self.__statusbar["text"] = text

    def setSpritePosition(self, spriteId : int, position):      # position as bounding box
        self.__canvas.coords(spriteId, position)


    def addLine(self, coords, color) -> int:
        return self.__canvas.create_line(coords, fill=color)

    def removeShape(self, shapeId):
        self.__canvas.delete(shapeId)

    def quit(self):
        reply = tk.messagebox.askyesno(
                    "quit",
                    "Are you sure you want to quit?",
                    parent=self.__root
                    )
        if reply:
            self.__root.destroy()
