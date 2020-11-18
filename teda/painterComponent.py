from .models.shapes_group import ShapesGroup
from .painterShapes.circleShape import (CircleShape)
from .painterShapes.CircleCenterShape import (CircleCenterShape)
from .painterShapes.rectangleMinatureShape import (RectangleMiniatureShape)
import matplotlib.pyplot as plt
from traitlets import Float, Int, HasTraits, Bool
from math import *

from .fitting import fit_gauss_2d_c

class PainterComponent(HasTraits):
    """Painter"""

    ccenter_x = Float()
    ccenter_y = Float()
    cradius = Float()

    viewX = Float()
    viewY = Float()

    movingViewX = Float()
    movingViewY = Float()

    auto_center = Bool(True)

    _active_region_group = Int(default_value=None, allow_none=True)

    def __init__(self, fits_plotter):
        self.shapes = []
        self.centerCircle = []
        self.rectangleMiniature = []
        self.listOfPaintedShapes = []
        self.drs = []
        self.templine = None
        self.tempCanvas = None
        self.tempcircle = None
        self.startpainting = 'false'
        self.startMoving = False
        self.actualShape = ""
        self.draggableActive = False
        self.eventInShapeFlag = False
        self.fits_plotter = fits_plotter
        self.region_groups = []

    def get_active_region_group(self) -> ShapesGroup:
        """Returns active region group: ShapesGroup object.
        If there is no region groups, new one is created and activated"""
        if self._active_region_group is None:
            self._active_region_group = self.new_region_group()
        return self.region_groups[self._active_region_group]

    def new_region_group(self, name=None) -> int:
        """Creates new region group and returns its index"""
        grp = ShapesGroup()
        if name is not None:
            grp.name = name
        self.region_groups.append(grp)
        if self._active_region_group is None:
            self._active_region_group = len(self.region_groups) - 1
        return len(self.region_groups) - 1

    def get_region_group_shapes(self, group_id):
        grp = self.region_groups[group_id]
        ret = []
        for shape in self.shapes:
            try:
                if shape.region_group == grp:
                    ret.append(shape)
            except AttributeError:  # not all shapes has region_group
                continue
        return ret


    def remove_region_group(self, axies, group_id):
        # TODO: maybe `axies` should be romoved, maybe Shapes should have set of axies on which it is visible
        # TODO: and allow visibility of shape in multiple axies and made it easier to manage shapes without bothering
        # TODO: with axies

        self.deleteShapes(axes=axies, shapes_to_delete=self.get_region_group_shapes(group_id))

        if self._active_region_group > group_id:  # the id of active group will move (decrease)
            self._active_region_group -= 1
        elif self._active_region_group == group_id:
            if len(self.region_groups) == 1:  # we are deleting the only group
                assert group_id == 0
                self._active_region_group = None
            else:  # we are deleting active group, make first one (after deletion) active
                self._active_region_group = 0

        del self.region_groups[group_id]

    def read_regions_file(self, filename, axies):
        group_id = self.new_region_group()
        grp = self.region_groups[group_id]
        try:
            grp.read_file(filename)
            grp.starlist['x'].count()  # generate exception if column not exists
            grp.starlist['y'].count()
        except Exception as e:
            self.remove_region_group(axies, group_id)
            raise e

        self._active_region_group = group_id
        # TODO: Deleting 0 group is temporary! until we have full support of multiple groups
        self.remove_region_group(axies, 0)

        for label, star in grp.starlist.iterrows():
            self.add(star['x'], star['y'], grp_id=self._active_region_group, label=label)

        self.paintAllShapes(axies)
        axies.figure.canvas.draw_idle()

    def add(self, x, y, size = 15,type="circle",size2=0, grp_id=None, label=None):
        if type == "circle":
            c = CircleShape(x, y, size)
            self.shapes.append(c)
            if grp_id is None:
                grp = self.get_active_region_group()
            else:
                grp = self.region_groups[grp_id]
            label = grp.on_shape_added(x, y, label)
            c.label = label
            c.region_group = grp
        if type == "circleCenter":
            self.centerCircle = []
            newx,newy = self.centerRadialProfile(x, y ,size)
            c = CircleCenterShape(newx, newy, size)
            self.ccenter_x = newx
            self.ccenter_y = newy
            self.cradius = size
            self.centerCircle.append(c)
        if type == "rectangleMiniature":
            self.rectangleMiniature = []
            c = RectangleMiniatureShape(x, y, size, size2)
            self.rectangleMiniature.append(c)


    def paintAllShapes(self, axes):
        axes.patches.clear()
        axes.lines.clear()
        self.listOfPaintedShapes = []
        self.drs = []
        for shape in self.shapes:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)
        for shape in self.centerCircle:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)
        for shape in self.rectangleMiniature:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)
        self.tempCanvas.draw_idle()

    def makeAllShapesDraggable(self, axes):
        self.draggableActive = True
        axes.patches.clear()
        axes.lines.clear()
        self.drs = []
        for shape in self.shapes:
            shap = shape.paintShape(axes)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)
        for shape in self.centerCircle:
            shap = shape.paintShape(axes)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)
        for shape in self.rectangleMiniature:
            shap=shape.paintShape(axes)
            dr = DraggablePoint(shap, shape, self)
            dr.connect()
            self.drs.append(dr)

    def disableAllShapesDraggable(self):
        self.draggableActive = False
        self.drs = []

    def getAllShapes(self):
        return self.shapes

    def startPainting(self, canvas, shape):
        self.removeCanvasEvents(canvas)
        self.actualShape = shape
        self.setCanvasEvents(canvas,'painting')

    def startMovingEvents(self, canvas):
        self.removeCanvasEvents(canvas)
        self.setCanvasEvents(canvas,'moving')

    def stopPainting(self,canvas):
        self.actualShape = ""
        self.removeCanvasEvents(canvas)

    def stopMovingEvents(self, canvas):
        self.removeCanvasEvents(canvas)

    def startLine(self,canvas,x1,y1):
        ax = canvas.figure.axes[0]
        self.tempLines = ax.lines.copy()
        canvas.draw_idle()

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
        canvas.draw_idle()

    def hideLine(self,canvas):
        # restore the background region
        ax = canvas.figure.axes[0]
        self.templine = None
        self.tempcircle = None
        ax.lines = self.tempLines.copy()
        canvas.draw_idle()

    def setCanvas(self, canvas):
        self.tempCanvas = canvas

    def setCanvasEvents(self,canvas, mode):
        self.tempCanvas = canvas
        if mode =='painting':
            self.addButtonPress = canvas.mpl_connect("button_press_event", self.onAddCircle)
            self.addButtonRelease = canvas.mpl_connect('button_release_event', self.onAddCircleRelease)
            self.addButtonMotion = canvas.mpl_connect('motion_notify_event', self.onAddCircleMotion)
        if mode == 'moving':
            self.addButtonPress = canvas.mpl_connect("button_press_event", self.onMovingClick)
            self.addButtonRelease = canvas.mpl_connect('button_release_event', self.onMovingRelease)
            self.addButtonMotion = canvas.mpl_connect('motion_notify_event', self.onMovingMotion)

    def removeCanvasEvents(self,canvas):
        if hasattr(self, 'addButtonPress'):
            canvas.mpl_disconnect(self.addButtonPress)
            canvas.mpl_disconnect(self.addButtonRelease)
            canvas.mpl_disconnect(self.addButtonMotion)

    def onAddCircle(self, event):
        if self.eventInShape(event):
            self.eventInShapeFlag = True
            return
        self.clicked = {
            'x': event.xdata,
            'y': event.ydata
        }
        self.startpainting = 'true'
        self.startLine(self.tempCanvas,event.xdata,event.ydata)


    def onAddCircleMotion(self, event):
        if not self.eventInShapeFlag:
            if self.startpainting == 'true':
                self.paintLine(self.tempCanvas,self.clicked['x'],event.xdata,self.clicked['y'],event.ydata)
                self.tempCanvas.draw_idle()


    def onAddCircleRelease(self, event):
        if not self.eventInShapeFlag:
            self.startpainting = 'false'
            self.hideLine(self.tempCanvas)
            r=sqrt(pow((event.xdata-self.clicked['x']),2)+pow((event.ydata-self.clicked['y']),2))
            if r == 0:
                r = 15
            self.add(self.clicked['x'], self.clicked['y'], r, self.actualShape)
            ax = self.tempCanvas.figure.axes[0]
            self.paintAllShapes(ax)
            self.tempCanvas.draw_idle()
        self.eventInShapeFlag = False

    def onMovingClick(self,event):
        if self.eventInShape(event):
            self.eventInShapeFlag = True
            return
        try:
            ax = self.tempCanvas.figure.axes[0]
            self.press = event.xdata, event.ydata
            self.curr_lim = ax.get_xlim(), ax.get_ylim()
            self.startMoving = True
            self.dx = 0
            self.dy = 0
        except LookupError:  # no axies :(
            pass

    def onMovingMotion(self,event):
        if not self.eventInShapeFlag:
            if self.startMoving:
                ax = self.tempCanvas.figure.axes[0]
                xpress, ypress = self.press
                xlim, ylim = self.curr_lim
                self.dx = event.xdata - xpress + self.dx
                self.dy = event.ydata - ypress + self.dy
                xli1, xli2 = xlim
                yli1, yli2 = ylim
                ax.set_xlim(xli1 - self.dx, xli2 - self.dx)
                ax.set_ylim(yli1 - self.dy, yli2 - self.dy)
                self.movingViewX = xli1 - self.dx
                self.movingViewY = yli1 - self.dy
                self.tempCanvas.draw()


    def onMovingRelease(self,event):
        if not self.eventInShapeFlag:
            if self.startMoving:
                self.tempCanvas.draw()
                self.press = None
                self.curr_lim = None
                self.dx = 0
                self.dy = 0
                self.tempCanvas.draw()
        self.eventInShapeFlag = False
        self.startMoving = False

    def deleteSelectedShapes(self, axes):
        todeleteShapes = []
        for shape in self.shapes:
            if shape.selected:
                todeleteShapes.append(shape)
        self.deleteShapes(axes=axes, shapes_to_delete=todeleteShapes)

    def deleteShapes(self, axes, shapes_to_delete):
        tempShapes = []
        for shape in self.shapes:
            if shape not in shapes_to_delete:
                tempShapes.append(shape)
        self.shapes = tempShapes
        for shape in self.centerCircle:
            if shape in shapes_to_delete:
                self.centerCircle.remove(shape)
        for shape in shapes_to_delete:
            try:
                shape.region_group.on_shape_deleted(id=shape.label)
            except AttributeError: pass
        self.paintAllShapes(axes)
        if self.draggableActive:
            self.makeAllShapesDraggable(axes)

    def eventInShape(self, event):
        inShapeClicked = False
        for shape in self.listOfPaintedShapes:
            contains, attrd = shape.contains(event)
            if contains:
                inShapeClicked = True
        return inShapeClicked

    def fillListOfPaintedShapes(self):
        self.listOfPaintedShapes = []
        for shape in self.shapes:
            shap = shape.getShape()
            self.listOfPaintedShapes.append(shap)
        for shape in self.centerCircle:
            shap = shape.getShape()
            self.listOfPaintedShapes.append(shap)
        for shape in self.rectangleMiniature:
            shap = shape.getShape()
            self.listOfPaintedShapes.append(shap)

    def centerRadialProfile(self, x, y, r, force=False):
        #self.tempCanvas w tym jest aktualny canvas
        #tu centrowanie
        #zwrócić nowe x,y
        # if force is False, center only if self.auto_center
        if not force and not self.auto_center:
            return x,y
        try:
            xy, values = self.fits_plotter.get_pixels_in_circle(x, y, r)
            model, a, mu_x, mu_y, sig, c, rmse = fit_gauss_2d_c(xy, values,
                                                                initial_mu=[x,y],
                                                                mu_radius=[5,5])
            self.fit_xy = xy
            self.fit_values = values
            self.fit_model = model
            self.fit_a = a
            self.fit_mu_x = mu_x
            self.fit_mu_y = mu_y
            self.fit_sig = sig
            self.fit_c = c

        except Exception as e:
            print(e)
            return x,y
        return mu_x, mu_y

class DraggablePoint:
    lock = None #only one can be animated at a time
    def __init__(self, point, painterElement, paintComp):
        self.point = point
        self.painterElement = painterElement
        self.paintComp = paintComp
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
        if hasattr(self.point,'center'):
            self.press = (self.point.center), event.xdata, event.ydata
        elif hasattr(self.point, 'xy'):
            self.press = (self.point.xy), event.xdata, event.ydata
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
        if hasattr(self.painterElement, 'repaintAdditional'):
            self.painterElement.repaintAdditional(axes)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        if hasattr(self.point,'center'):
            self.point.center, xpress, ypress = self.press
        elif hasattr(self.point, 'xy'):
            self.point.xy, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        if hasattr(self.point, 'center'):
            self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)
            self.painterElement.x = self.point.center[0]
            self.painterElement.y = self.point.center[1]
        elif hasattr(self.point, 'xy'):
            self.point.xy = (self.point.xy[0] + dx, self.point.xy[1] + dy)
            self.painterElement.x = self.point.xy[0]
            self.painterElement.y = self.point.xy[1]

        if hasattr(self.painterElement, 'shapeType'):
            if self.painterElement.shapeType == 'rectangleMiniature':
                self.paintComp.viewX = self.painterElement.x
                self.paintComp.viewY = self.painterElement.y

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

        if self.movingStart == True:
            # mka: CircleShape will be also cantered, there is switch in menu to avoid auto-centering
            if isinstance(self.painterElement, CircleShape) or self.painterElement.shapeType == 'centerCircle':
                newx, newy = self.paintComp.centerRadialProfile(self.painterElement.x, self.painterElement.y, self.painterElement.size)
                self.painterElement.x = newx
                self.painterElement.y = newy
                self.paintComp.ccenter_x = self.painterElement.x
                self.paintComp.ccenter_y = self.painterElement.y
                self.paintComp.cradius = self.painterElement.size
                self.point = self.painterElement.refreshShape(axes)
                try:
                    self.painterElement.region_group.on_shape_moved(self.painterElement.x, self.painterElement.y,
                                                                    self.painterElement.label)
                except AttributeError:
                    pass

        self.point.figure.canvas.draw_idle()
        self.paintComp.fillListOfPaintedShapes()
        self.movingStart = False

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
