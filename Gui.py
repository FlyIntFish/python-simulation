from __future__ import annotations
import tkinter as tk
from tkinter import *
import os
from tkinter import messagebox
from utility import *
from tkinter.constants import NSEW
from Sprite import Sprite
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App import App

class Gui:

    __ElementsColors = {
        "toolbar" : "#000000",
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
        self.__app = app
        self.__root = root
        self.__menuBar = tk.Menu(self.__root)
        self.__initCanvas()
        self.__initMenuBar()
        self.__initOptionsBar()
        self.__initToolbar()
        self.__configureColumnAndRows()

    def __createToolbar(self):
        self.__toolbar = tk.Frame(self.__root, background=Gui.colorOf("toolbar"))
        self.__toolbar.grid(row=1, column=0, columnspan=3, sticky=NSEW)

    def __initToolbar(self):
        nextColumn = 0
        self.__createToolbar()
        nextColumn = self.__addToolbarButtons(nextColumn)
        nextColumn = self.__addToolbarTimeFactorSlider(nextColumn)

    def placeholder(self):
        pass
    
    def __addToolbarButtons(self, column):
        self.__toolbar_images = []
        for image, command in (
                ("reload.png", self.__app.removeAllBodies),
                ("play-button.png", self.__app.resume),
                ("pause-button.png", self.__app.pause),
                ("settings.png", self.placeholder)):
            image = os.path.join(Gui.__textures_path, image)
            try:
                image = tk.PhotoImage(file=image)
                self.__toolbar_images.append(image)
                button = tk.Button(self.__toolbar, image=image,
                                        command=command)
                button.grid(row=0, column=column)
                column += 1 
            except tk.TclError as err:
                print(err)                                              # problem with file 
        self.__toolbar.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        return column

    def __addToolbarTimeFactorSlider(self, column):
        current_value = tk.DoubleVar()
        self.__speedFactorSlider = tk.Scale(
            self.__toolbar,
            orient='horizontal',
            from_ = 1,
            to = self.__app.MAX_SPEED_FACTOR,
            command = lambda event: setattr(self.__app, 'speedFactor', self.__speedFactorSlider.get()), 
            variable = current_value
        )
        self.__speedFactorSlider.grid(row=0, column=column)
        return column + 1

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
                ("New...", self.placeholder, "Ctrl+N", "<Control-n>"),
                ("Open...", self.__app.resume, "Ctrl+O", "<Control-o>"),
                ("Save", self.__app.pause, "Ctrl+S", "<Control-s>"),
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
        self.__canvas.grid(row=1, column=0, padx=0, pady=0, sticky=NSEW)

    def __configureColumnAndRows(self):
        self.__root.columnconfigure(0, weight=10)
        self.__root.rowconfigure(0, weight=1)
        self.__root.rowconfigure(1, weight=999)


    def guiLoop(self, func):
        self.__canvas.after(5, func)

    def addSprite(self, sprite : Sprite) -> int:
        return self.__canvas.create_oval(
            sprite.getBoundingBoxCoords(),
            fill = sprite.color
            )

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
