from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class RectangleMiniatureShape(object):
    """Center Circle"""

    def __init__(self,x,y,size,size2,color='b'):
        self.x = x
        self.y = y
        self.size = size
        self.size2 = size2
        self.color = color
        self.originColor = color
        self.shapeType = "rectangleMiniature"


    def paint(self):
        return {self.x, self.y, self.size}

    def paintShape(self,axes):
        self.rect = patches.Rectangle((self.x,self.y),self.size,self.size2,linewidth=1,edgecolor=self.color,facecolor='none')
        axes.add_patch(self.rect)
        return self.rect

    def repaintShape(self,axes,x,y,size,color,size2):
        #self.rect.remove()
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.size2 = size2
        #self.rect = patches.Rectangle((self.x,self.y),self.size,self.size2,linewidth=1,edgecolor=self.color,facecolor='none')
        self.rect.set_xy((self.x, self.y))
        self.rect.set_height(self.size2)
        self.rect.set_width(self.size)
        #axes.add_patch(self.rect)
        return self.rect

    def repaintShapeXY(self,axes,x,y):
        #self.rect.remove()
        self.x = x
        self.y = y
        self.rect.set_xy((self.x, self.y))
        #self.rect = patches.Rectangle((self.x, self.y), self.size, self.size2, linewidth=1, edgecolor=self.color, facecolor='none')
        #axes.add_patch(self.rect)
        return self.rect

    def refreshShape(self,axes):
        #self.rect.remove()
        #self.rect = patches.Rectangle((self.x,self.y),self.size,self.size2,linewidth=1,edgecolor=self.color,facecolor='none')
        #axes.add_patch(self.rect)
        self.rect.set_xy((self.x, self.y))
        self.rect.set_height(self.size2)
        self.rect.set_width(self.size)
        return self.rect

    def paintAdditional(self):
        pass

    def repaintAdditional(self,axes):
        pass

    def removeAdditional(self):
        pass

    def selectDeselect(self):
        pass

    def select(self):
        pass

    def deselect(self):
        pass

    def getShape(self):
        return self.rect