from PySide6.QtCore import Qt
import matplotlib.pyplot as plt


class CircleShape(object):
    """Circle"""

    def __init__(self,x,y,size,color='r'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.selectionColor = 'y'
        self.selected = False
        self.originColor = color


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self,axes):
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axes.add_patch(self.circle)
        return self.circle

    def repaintShape(self,axes,x,y,size,color):
        self.circle.remove()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axes.add_patch(self.circle)
        return self.circle

    def refreshShape(self,axes):
        #self.circle.remove()
        #self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        #axes.add_patch(self.circle)
        self.circle.set_center((self.x, self.y))
        self.circle.set_color(self.color)
        self.circle.set_radius(self.size)
        return self.circle

    def paintAdditional(self):
        pass

    def repaintAdditional(self,axes):
        pass

    def removeAdditional(self):
        pass

    def selectDeselect(self):
        if self.selected == False:
            self.selected = True
            self.color = self.selectionColor
        else:
            self.selected = False
            self.color = self.originColor

    def select(self):
        self.selected = True
        self.color = self.selectionColor

    def deselect(self):
        self.selected = False
        self.color = self.originColor

    def getShape(self):
        return self.circle

