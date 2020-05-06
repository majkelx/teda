from PySide2.QtCore import Qt
import matplotlib.pyplot as plt


class CircleCenterShape(object):
    """Painter"""

    def __init__(self,x,y,size,color='r'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.selected = 'false'


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self,axis):
        circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        axis.add_patch(circle)
        xcord = [self.x, self.x]
        ycord = [self.y-self.size/2, self.y+self.size/2]
        self.linex = plt.plot(xcord, ycord, linewidth=1, color='r')
        xcord = [self.x - self.size/2, self.x + self.size/2]
        ycord = [self.y, self.y]
        self.liney = plt.plot(xcord, ycord, linewidth=1, color='r')
        return circle

    def paintAdditional(self):
        xcord = [self.x, self.x]
        ycord = [self.y - self.size / 2, self.y + self.size / 2]
        self.linex = plt.plot(xcord, ycord, linewidth=1, color='r')
        xcord = [self.x - self.size / 2, self.x + self.size / 2]
        ycord = [self.y, self.y]
        self.liney = plt.plot(xcord, ycord, linewidth=1, color='r')

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
        self.linex[0].remove()
        self.liney[0].remove()
