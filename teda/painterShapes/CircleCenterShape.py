from PySide6.QtCore import Qt
import matplotlib.pyplot as plt


class CircleCenterShape(object):
    """Center Circle"""

    def __init__(self,x,y,size,color='r'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.selectionColor = 'y'
        self.selected = False
        self.originColor = color
        self.shapeType = "centerCircle"


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self,axes):
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axes.add_patch(self.circle)
        self.paintAdditional(axes)
        return self.circle

    def repaintShape(self,axes,x,y,size,color):
        self.circle.remove()
        self.removeAdditional()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axes.add_patch(self.circle)
        self.paintAdditional(axes)
        return self.circle

    def refreshShape(self,axes):
        #self.circle.remove()
        self.removeAdditional()
        #self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        #axes.add_patch(self.circle)
        self.circle.set_center((self.x, self.y))
        self.circle.set_color(self.color)
        self.circle.set_radius(self.size)
        self.paintAdditional(axes)
        return self.circle

    def paintAdditional(self,axes):
        xcord = [self.x, self.x]
        ycord = [self.y - self.size / 2, self.y + self.size / 2]
        self.linex = axes.plot(xcord, ycord, linewidth=1, color=self.color)
        xcord = [self.x - self.size / 2, self.x + self.size / 2]
        ycord = [self.y, self.y]
        self.liney = axes.plot(xcord, ycord, linewidth=1, color=self.color)

    def repaintAdditional(self,axes):
        xcord = [self.x, self.x]
        ycord = [self.y - self.size / 2, self.y + self.size / 2]
        self.linex[0].set_xdata(xcord)
        self.linex[0].set_ydata(ycord)
        xcord = [self.x - self.size / 2, self.x + self.size / 2]
        ycord = [self.y, self.y]
        self.liney[0].set_xdata(xcord)
        self.liney[0].set_ydata(ycord)
        axes.draw_artist(self.linex[0])
        axes.draw_artist(self.liney[0])

    def removeAdditional(self):
        try:
            self.linex[0].remove()
            self.liney[0].remove()
        except:
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