from painterShapes.circleShape import (CircleShape)
from painterShapes.CircleCenterShape import (CircleCenterShape)
import matplotlib.pyplot as plt
from math import *

class PainterComponent(object):
    """Painter"""

    def __init__(self):
        self.shapes = []
        self.centerCircle = []
        self.drs = []
        self.templine = None
        self.tempCanvas = None
        self.tempcircle = None
        self.startpainting = 'false'
        self.actualShape = ""
        self.draggableActive = False


    def add(self, x, y, size = 10,type="circle"):
        if type == "circle":
            c = CircleShape(x, y, size)
            self.shapes.append(c)
        if type == "circleCenter":
            self.centerCircle = []
            c = CircleCenterShape(x, y, size)
            self.centerCircle.append(c)

    def paintAllShapes(self, axes):
        axes.patches.clear()
        axes.lines.clear()
        for shape in self.shapes:
            shap=shape.paintShape(axes)
        for shape in self.centerCircle:
            shap=shape.paintShape(axes)
        self.tempCanvas.draw()

    def makeAllShapesDraggable(self, axes):
        self.draggableActive = True
        axes.patches.clear()
        axes.lines.clear()
        self.drs = []
        for shape in self.shapes:
            shap = shape.paintShape(axes)
            dr = DraggablePoint(shap, shape)
            dr.connect()
            self.drs.append(dr)
        for shape in self.centerCircle:
            shap = shape.paintShape(axes)
            dr = DraggablePoint(shap, shape)
            dr.connect()
            self.drs.append(dr)

    def disableAllShapesDraggable(self):
        self.draggableActive = False
        self.drs = []

    def getAllShapes(self):
        return self.shapes

    def startPainting(self,canvas,shape):
        self.actualShape = shape
        self.setCanvasEvents(canvas)
    def stopPainting(self,canvas):
        self.actualShape = ""
        self.removeCanvasEvents(canvas)

    def startLine(self,canvas,x1,y1):
        ax = canvas.figure.axes[0]
        self.tempLines = ax.lines.copy()
        canvas.draw()

    def paintLine(self,canvas,x1,x2,y1,y2):
        ax = canvas.figure.axes[0]
        if self.templine != None:
            self.templine = None
            ax.lines = ax.lines[:-1]
        if self.tempcircle != None:
            ax.patches.remove(self.tempcircle)
            self.tempcircle = None
        xcord = [x1,x2]
        ycord = [y1,y2]
        r = sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2))
        self.tempcircle = plt.Circle((x1, y1), r, color='g', fill=False)
        ax.add_patch(self.tempcircle)
        self.templine = ax.plot(xcord, ycord, linewidth=1, color='g')
        canvas.draw()

    def hideLine(self,canvas):
        # restore the background region
        ax = canvas.figure.axes[0]
        self.templine = None
        self.tempcircle = None
        ax.lines = self.tempLines.copy()
        canvas.draw()

    def setCanvasEvents(self,canvas):
        self.tempCanvas = canvas
        self.addButtonPress = canvas.mpl_connect("button_press_event", self.onAddCircle)
        self.addButtonRelease = canvas.mpl_connect('button_release_event', self.onAddCircleRelease)
        self.addButtonMotion = canvas.mpl_connect('motion_notify_event', self.onAddCircleMotion)

    def removeCanvasEvents(self,canvas):
        if hasattr(self, 'addButtonPress'):
            canvas.mpl_disconnect(self.addButtonPress)
            canvas.mpl_disconnect(self.addButtonRelease)
            canvas.mpl_disconnect(self.addButtonMotion)

    def onAddCircle(self, event):
        self.clicked = {
            'x': event.xdata,
            'y': event.ydata
        }
        self.startpainting = 'true'
        self.startLine(self.tempCanvas,event.xdata,event.ydata)


    def onAddCircleMotion(self, event):
        if self.startpainting == 'true':
            self.paintLine(self.tempCanvas,self.clicked['x'],event.xdata,self.clicked['y'],event.ydata)
        self.tempCanvas.draw()


    def onAddCircleRelease(self, event):
        self.startpainting = 'false'
        self.hideLine(self.tempCanvas)
        r=sqrt(pow((event.xdata-self.clicked['x']),2)+pow((event.ydata-self.clicked['y']),2))
        if r == 0:
            r = 15
        self.add(self.clicked['x'], self.clicked['y'], r, self.actualShape)
        ax = self.tempCanvas.figure.axes[0]
        self.paintAllShapes(ax)
        self.tempCanvas.draw()

    def deleteSelectedShapes(self, axes):
        tempShapes = []
        for shape in self.shapes:
            if shape.selected != True:
                tempShapes.append(shape)
        self.shapes = tempShapes
        for shape in self.centerCircle:
            if shape.selected == True:
                self.centerCircle.remove(shape)
        self.paintAllShapes(axes)
        if self.draggableActive:
            self.makeAllShapesDraggable(axes)


class DraggablePoint:
    lock = None #only one can be animated at a time
    def __init__(self, point, painterElement):
        self.point = point
        self.painterElement = painterElement
        self.press = None
        self.background = None
        self.movingStart = False

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes

        self.point.set_animated(True)
        if hasattr(self.painterElement, 'removeAdditional'):
            self.painterElement.removeAdditional()
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the selected
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)
        self.painterElement.x = self.point.center[0]
        self.painterElement.y = self.point.center[1]

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        #zaznaczenie na przesuwaniu
        if self.movingStart == False:
            self.movingStart = True
            self.painterElement.select()
            self.point = self.painterElement.refreshShape(axes)
            self.point.set_animated(True)

        # redraw just the current
        axes.draw_artist(self.point)
        if hasattr(self.painterElement, 'repaintAdditional'):
            self.painterElement.repaintAdditional(axes)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the current animation property and reset the background
        self.point.set_animated(False)
        self.background = None
        axes = self.point.axes
        # redraw the full figure
        if self.movingStart == False:
            self.painterElement.selectDeselect()
            self.point = self.painterElement.refreshShape(axes)
        self.point.figure.canvas.draw()
        self.movingStart = False

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
