from PySide2.QtCore import Qt
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


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self,axis):
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        self.paintAdditional()
        return self.circle

    def repaintShape(self,axis,x,y,size,color):
        self.circle.remove()
        self.removeAdditional()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        self.paintAdditional()
        return self.circle

    def refreshShape(self,axis):
        self.circle.remove()
        self.removeAdditional()
        self.circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(self.circle)
        self.paintAdditional()
        return self.circle

    def paintAdditional(self):
        xcord = [self.x, self.x]
        ycord = [self.y - self.size / 2, self.y + self.size / 2]
        self.linex = plt.plot(xcord, ycord, linewidth=1, color=self.color)
        xcord = [self.x - self.size / 2, self.x + self.size / 2]
        ycord = [self.y, self.y]
        self.liney = plt.plot(xcord, ycord, linewidth=1, color=self.color)

    def repaintAdditional(self,axis):
        xcord = [self.x, self.x]
        ycord = [self.y - self.size / 2, self.y + self.size / 2]
        self.linex[0].set_xdata(xcord)
        self.linex[0].set_ydata(ycord)
        xcord = [self.x - self.size / 2, self.x + self.size / 2]
        ycord = [self.y, self.y]
        self.liney[0].set_xdata(xcord)
        self.liney[0].set_ydata(ycord)
        axis.draw_artist(self.linex[0])
        axis.draw_artist(self.liney[0])

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