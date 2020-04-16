from PySide2.QtCore import Qt
import matplotlib.pyplot as plt


class CircleShape(object):
    """Painter"""

    def __init__(self,x,y,size,color='r'):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.selected = 'false'


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self):
        circle = plt.Circle((self.x, self.y), self.size, color=self.color, fill=False)
        return circle
