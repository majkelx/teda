from PySide2.QtCore import Qt
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

    def paintShape(self,axis):
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        return self.circle

    def repaintShape(self,axis,x,y,size,color):
        self.circle.remove()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        return self.circle

    def refreshShape(self,axis):
        self.circle.remove()
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        return self.circle

    def paintAdditional(self):
        pass

    def repaintAdditional(self,axis):
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

