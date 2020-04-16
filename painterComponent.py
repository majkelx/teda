from painterShapes.circleShape import (CircleShape)

class PainterComponent(object):
    """Painter"""

    def __init__(self):
        self.shapes = []
        self.drs = []
        c = CircleShape(20, 20, 10)
        self.shapes.append(c)
        b = CircleShape(30, 30, 14)
        self.shapes.append(b)

    def add(self, x, y, size = 10,type="circle"):
        if type == "circle":
            c = CircleShape(x, y, size)
            self.shapes.append(c)

    def paintAllShapes(self, axis):
        axis.patches.clear()
        self.drs = []
        for shape in self.shapes:
            shap=shape.paintShape()
            axis.add_patch(shap)
            dr = DraggablePoint(shap,shape)
            dr.connect()
            self.drs.append(dr)

    def getAllShapes(self):
        return self.shapes

class DraggablePoint:
    lock = None #only one can be animated at a time
    def __init__(self, point, painterElement):
        self.point = point
        self.painterElement = painterElement
        self.press = None
        self.background = None

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

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
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

        # redraw just the current rectangle
        axes.draw_artist(self.point)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
