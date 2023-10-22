import tkinter as tk
import random

class Triangle:

    def __init__(self, height=2, base=3):
        self.height = height
        self.base = base

    def getHeight(self):
        return self.height

    def getBase(self):
        return self.base

    def setHeight(self, height):
        self.height = height

    def setBase(self, base):
        self.base = base

    def calcArea(self):
        self.area = (self.height * self.base) / 2

    def show(self):
        self.calcArea()
        return "Area of Triangle: {:.2f}".format(self.area)


class Rectangle:

    def __init__(self, length=4, width=5):
        self.length = length
        self.width = width

    def getLength(self):
        return self.length

    def getWidth(self):
        return self.width

    def setLength(self, length):
        self.length = length

    def setWidth(self, width):
        self.width = width

    def calcArea(self):
        self.area = self.length * self.width

    def show(self):
        self.calcArea()
        return "Area of Rectangle: {:.2f}".format(self.area)


class Parallelogram:

    def __init__(self, height=6, base=7):
        self.height = height
        self.base = base

    def getHeight(self):
        return self.height

    def getBase(self):
        return self.base

    def setHeight(self, height):
        self.height = height

    def setBase(self, base):
        self.base = base

    def calcArea(self):
        self.area = self.height * self.base

    def show(self):
        self.calcArea()
        return "Area of Parallelogram: {:.2f}".format(self.area)


def main():
    global var
    output = []
    shapeName = None
    results = ''
    for _ in range(8):
        randomChoice = random.randint(1, 3)

        if randomChoice == 1:
            output.append(Triangle())

        elif randomChoice == 2:
            output.append(Rectangle())

        elif randomChoice == 3:
            output.append(Parallelogram())

    for result in output:
        result.show()
        if isinstance(result, Triangle):
            shapeName = "Triangle"
        if isinstance(result, Rectangle):
            shapeName = "Rectangle"
        if isinstance(result, Parallelogram):
            shapeName = "Parallelogram"

        results += "Area of {}: {}\n".format(shapeName, result.show())
    var.set(results)
    print(var)


master = tk.Tk()
master.title("Area")
master.geometry("300x250")
btn = tk.Button(master, text="Show Output", command=main)
btn.pack()
var = tk.StringVar(master, '')
Label = tk.Label(master, textvariable=var)
Label.pack()
master.mainloop()