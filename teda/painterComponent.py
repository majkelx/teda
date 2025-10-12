from .painterShapes.circleShape import (CircleShape)
from .painterShapes.CircleCenterShape import (CircleCenterShape)
from .painterShapes.rectangleMinatureShape import (RectangleMiniatureShape)
from .painterShapes.lineProfileShape import (LineProfileShape)
import matplotlib.pyplot as plt
from traitlets import Float, Int, HasTraits, Bool, observe
import math

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

    # Observable flag for shape changes (overlay sync)
    shapes_changed = Bool(False)
    line_profile_changed = Bool(False)  # For line profile updates

    def __init__(self, fits_plotter):
        self.shapes = []
        self.centerCircle = []
        self.rectangleMiniature = []
        self.lineProfile = []  # Singleton list for line profile (max 1 element)
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
        self.interactionEnabled = True  # For read-only overlay views

        # Line drawing mode state
        self.line_profile_mode = False
        self.line_drawing = False
        self.line_start_x = None
        self.line_start_y = None


    def add(self, x, y, size = 15,type="circle",size2=0):
        if type == "circle":
            c = CircleShape(x, y, size)
            self.shapes.append(c)
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
        # axes.patches.clear()
        # axes.lines.clear()
        print(f"[paintAllShapes] axes={axes}, interactionEnabled={self.interactionEnabled}")
        print(f"[paintAllShapes] Before clear: patches={len(axes.patches)}, lines={len(axes.lines)}")
        for p in axes.patches:
            p.remove()
        for p in axes.lines:
            p.remove()
        self.listOfPaintedShapes = []
        self.drs = []
        print(f"[paintAllShapes] Painting {len(self.shapes)} circles, {len(self.centerCircle)} centerCircles, {len(self.rectangleMiniature)} rectangles")
        for shape in self.shapes:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            print(f"[paintAllShapes] Painted circle, returned shap={shap}")
            if self.interactionEnabled:  # Only create draggables if interaction enabled
                dr = DraggablePoint(shap, shape, self)
                dr.connect()
                self.drs.append(dr)
        for shape in self.centerCircle:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            print(f"[paintAllShapes] Painted centerCircle, returned shap={shap}")
            if self.interactionEnabled:  # Only create draggables if interaction enabled
                dr = DraggablePoint(shap, shape, self)
                dr.connect()
                self.drs.append(dr)
        for shape in self.rectangleMiniature:
            shap=shape.paintShape(axes)
            self.listOfPaintedShapes.append(shap)
            print(f"[paintAllShapes] Painted rectangle, returned shap={shap}")
            if self.interactionEnabled:  # Only create draggables if interaction enabled
                dr = DraggablePoint(shap, shape, self)
                dr.connect()
                self.drs.append(dr)

        # Paint line profile (singleton)
        print(f"[paintAllShapes] Painting {len(self.lineProfile)} line profiles")
        for line in self.lineProfile:
            line_objects = line.paintShape(axes)  # Returns [line, handle_start, handle_end]
            self.listOfPaintedShapes.extend(line_objects)
            print(f"[paintAllShapes] Painted line profile, returned {len(line_objects)} objects")
            if self.interactionEnabled:  # Only create draggables if interaction enabled
                # Make endpoint handles draggable
                dr_start = DraggableLineHandle(line_objects[1], line, self, 'start')
                dr_end = DraggableLineHandle(line_objects[2], line, self, 'end')
                dr_start.connect()
                dr_end.connect()
                self.drs.append(dr_start)
                self.drs.append(dr_end)

        print(f"[paintAllShapes] After painting: patches={len(axes.patches)}, lines={len(axes.lines)}")
        print(f"[paintAllShapes] Calling tempCanvas.draw_idle(), canvas={self.tempCanvas}")
        self.tempCanvas.draw_idle()

    def makeAllShapesDraggable(self, axes):
        self.draggableActive = True
        # axes.patches.clear()
        # axes.lines.clear()
        for p in axes.patches:
            p.remove()
        for p in axes.lines:
            p.remove()
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

    def disableInteraction(self):
        """Disable all interaction for read-only overlay views"""
        self.interactionEnabled = False
        self.draggableActive = False
        self.drs = []

    def notifyShapesChanged(self):
        """Notify observers that shapes have changed (toggle to trigger)"""
        self.shapes_changed = not self.shapes_changed

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
        self.tempLines = [l for l in ax.lines]   # .copy()
        canvas.draw_idle()

    def paintLine(self,canvas,x1,x2,y1,y2):
        ax = canvas.figure.axes[0]
        if self.templine != None:
            self.templine = None
            ax.lines[-1].remove()
        if self.tempcircle != None:
            self.tempcircle.remove()
            self.tempcircle = None
        xcord = [x1,x2]
        ycord = [y1,y2]
        r = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        self.tempcircle = plt.Circle((x1, y1), r, color='g', fill=False)
        ax.add_patch(self.tempcircle)
        self.templine = ax.plot(xcord, ycord, linewidth=1, color='g')
        canvas.draw_idle()

    def hideLine(self,canvas):
        # restore the background region
        ax = canvas.figure.axes[0]
        self.templine = None
        self.tempcircle = None
        for l in self.tempLines:
            ax.add_line(l)
        # ax.lines = self.tempLines    #.copy()
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
                # BUG FIX #6: Notify shape changes during circle creation (throttled)
                # This syncs temporary circle to zoom/full windows as user drags
                if not hasattr(self, '_circle_motion_counter'):
                    self._circle_motion_counter = 0
                self._circle_motion_counter += 1
                if self._circle_motion_counter % 3 == 0:  # Throttle to every 3rd frame
                    self.notifyShapesChanged()


    def onAddCircleRelease(self, event):
        if not self.eventInShapeFlag:
            self.startpainting = 'false'
            self._circle_motion_counter = 0  # BUG FIX #6: Reset counter
            self.hideLine(self.tempCanvas)
            r = math.sqrt((event.xdata - self.clicked['x'])**2 + (event.ydata - self.clicked['y'])**2)
            if r == 0:
                r = 15
            self.add(self.clicked['x'], self.clicked['y'], r, self.actualShape)
            ax = self.tempCanvas.figure.axes[0]
            self.paintAllShapes(ax)
            self.tempCanvas.draw_idle()
            self.notifyShapesChanged()  # Notify observers (overlay sync)
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
                # Use draw_idle() for Qt's automatic coalescing (Phase 2.4)
                self.tempCanvas.draw_idle()


    def onMovingRelease(self,event):
        if not self.eventInShapeFlag:
            if self.startMoving:
                # Use draw_idle() for Qt's automatic coalescing (Phase 2.4)
                self.tempCanvas.draw_idle()
                self.press = None
                self.curr_lim = None
                self.dx = 0
                self.dy = 0
        self.eventInShapeFlag = False
        self.startMoving = False

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
        self.notifyShapesChanged()  # Notify observers (overlay sync)

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
        for line in self.lineProfile:
            # Line profile has multiple objects (line + handles)
            if line.line:
                self.listOfPaintedShapes.append(line.line)
            if line.handle_start:
                self.listOfPaintedShapes.append(line.handle_start)
            if line.handle_end:
                self.listOfPaintedShapes.append(line.handle_end)

    def centerRadialProfile(self, x, y, r, force=False):
        # self.tempCanvas holds the current canvas
        # Perform centering here
        # Return new x, y coordinates
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

    # ===== Line Profile Mode Methods =====

    def activateLineProfileMode(self):
        """Activate line profile drawing mode."""
        print("[LineProfile] Line profile mode activated")
        # Connect mouse events for line drawing
        if self.tempCanvas:
            self.removeCanvasEvents(self.tempCanvas)
            # Disconnect any existing line profile handlers first
            self._disconnectLineProfileHandlers()
            # Now connect new handlers
            self.line_profile_mode = True
            self.line_press_cid = self.tempCanvas.mpl_connect('button_press_event', self.onLinePress)
            self.line_motion_cid = self.tempCanvas.mpl_connect('motion_notify_event', self.onLineMotion)
            self.line_release_cid = self.tempCanvas.mpl_connect('button_release_event', self.onLineRelease)

    def deactivateLineProfileMode(self):
        """Deactivate line profile mode."""
        if not self.line_profile_mode:
            return  # Already deactivated

        print("[LineProfile] Line profile mode deactivated")
        self.line_profile_mode = False
        self._disconnectLineProfileHandlers()

    def _disconnectLineProfileHandlers(self):
        """Internal method to disconnect line profile event handlers."""
        # Disconnect line profile event handlers
        if self.tempCanvas:
            if hasattr(self, 'line_press_cid'):
                self.tempCanvas.mpl_disconnect(self.line_press_cid)
                delattr(self, 'line_press_cid')
            if hasattr(self, 'line_motion_cid'):
                self.tempCanvas.mpl_disconnect(self.line_motion_cid)
                delattr(self, 'line_motion_cid')
            if hasattr(self, 'line_release_cid'):
                self.tempCanvas.mpl_disconnect(self.line_release_cid)
                delattr(self, 'line_release_cid')

        # Clean up temporary drawing state
        self.line_drawing = False
        if hasattr(self, 'temp_line_preview') and self.temp_line_preview is not None:
            try:
                self.temp_line_preview.remove()
            except (ValueError, AttributeError):
                pass
            self.temp_line_preview = None

    def onLinePress(self, event):
        """Mouse press: start drawing line."""
        if event.inaxes and event.button == 1:  # Left click
            if self.eventInShape(event):
                self.eventInShapeFlag = True
                return
            self.line_start_x = event.xdata
            self.line_start_y = event.ydata
            self.line_drawing = True
            # Store current lines for restoration
            ax = self.tempCanvas.figure.axes[0]
            self.tempLines = [l for l in ax.lines]
            print(f"[LineProfile] Line drawing started at ({self.line_start_x}, {self.line_start_y})")

    def onLineMotion(self, event):
        """Mouse drag: show rubber-band line preview."""
        if self.line_drawing and event.inaxes:
            # Draw temporary line from start to current position
            ax = self.tempCanvas.figure.axes[0]

            # Remove previous temporary line if exists
            if hasattr(self, 'temp_line_preview') and self.temp_line_preview is not None:
                try:
                    self.temp_line_preview.remove()
                except ValueError:
                    pass

            # Draw new temporary line
            self.temp_line_preview, = ax.plot([self.line_start_x, event.xdata],
                                               [self.line_start_y, event.ydata],
                                               color='#1f77b4', linewidth=1, alpha=0.5, linestyle='--')
            self.tempCanvas.draw_idle()

    def onLineRelease(self, event):
        """Mouse release: finalize line creation."""
        if not self.eventInShapeFlag and self.line_drawing and event.inaxes:
            end_x = event.xdata
            end_y = event.ydata
            print(f"[LineProfile] Line drawing ended at ({end_x}, {end_y})")

            # Remove temporary line preview
            if hasattr(self, 'temp_line_preview') and self.temp_line_preview is not None:
                try:
                    self.temp_line_preview.remove()
                except ValueError:
                    pass
                self.temp_line_preview = None

            # Clear existing line (singleton pattern)
            self.lineProfile = []

            # Create new line
            line = LineProfileShape(self.line_start_x, self.line_start_y, end_x, end_y)
            self.lineProfile.append(line)

            # Repaint all shapes (includes new line)
            ax = self.tempCanvas.figure.axes[0]
            self.paintAllShapes(ax)

            # Notify observers (triggers sync and profile calculation)
            self.notifyShapesChanged()
            self.line_profile_changed = not self.line_profile_changed  # Toggle for observer

            self.line_drawing = False
        self.eventInShapeFlag = False

class DraggablePoint:
    lock = None #only one can be animated at a time
    def __init__(self, point, painterElement, paintComp):
        self.point = point
        self.painterElement = painterElement
        self.paintComp = paintComp
        self.press = None
        self.background = None
        self.movingStart = False
        self.motion_counter = 0  # BUG FIX #2: Counter for throttling drag updates

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

        # Highlight/select on drag
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

        # BUG FIX #2: Notify shape changes during drag (throttled to every 3rd frame)
        # This syncs zoom/full windows in real-time as user drags shapes
        self.motion_counter += 1
        if self.motion_counter % 3 == 0:  # Only notify every 3rd motion event
            self.paintComp.notifyShapesChanged()

    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None
        self.motion_counter = 0  # BUG FIX #2: Reset counter on release

        # turn off the current animation property and reset the background
        self.point.set_animated(False)
        self.background = None
        axes = self.point.axes
        # redraw the full figure
        if self.movingStart == False:
            self.painterElement.selectDeselect()
            self.point = self.painterElement.refreshShape(axes)

        if self.movingStart == True:
            if hasattr(self.painterElement, 'shapeType'):
                if self.painterElement.shapeType == 'centerCircle':
                    newx, newy = self.paintComp.centerRadialProfile(self.painterElement.x, self.painterElement.y, self.painterElement.size)
                    self.painterElement.x = newx
                    self.painterElement.y = newy
                    self.paintComp.ccenter_x = self.painterElement.x
                    self.paintComp.ccenter_y = self.painterElement.y
                    self.paintComp.cradius = self.painterElement.size
                    # Repaint all shapes to ensure autocenter position updates visually
                    self.paintComp.paintAllShapes(axes)
                    self.paintComp.fillListOfPaintedShapes()
                else:
                    self.point = self.painterElement.refreshShape(axes)
            self.paintComp.notifyShapesChanged()  # Notify observers (overlay sync)

        if not (self.movingStart and hasattr(self.painterElement, 'shapeType') and
                self.painterElement.shapeType == 'centerCircle'):
            # Only draw if we didn't already repaint everything for autocenter
            self.point.figure.canvas.draw_idle()
            self.paintComp.fillListOfPaintedShapes()
        self.movingStart = False

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)


class DraggableLineHandle:
    """Draggable handle for line profile endpoints."""
    lock = None  # only one can be animated at a time

    def __init__(self, handle, line_shape, paintComp, endpoint_type):
        self.handle = handle  # matplotlib marker object
        self.line_shape = line_shape  # LineProfileShape instance
        self.paintComp = paintComp
        self.endpoint_type = endpoint_type  # 'start' or 'end'
        self.press = None
        self.background = None
        self.movingStart = False
        self.motion_counter = 0

    def connect(self):
        """Connect to all the events we need."""
        self.cidpress = self.handle.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.handle.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.handle.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.handle.axes:
            return
        if DraggableLineHandle.lock is not None:
            return
        contains, attrd = self.handle.contains(event)
        if not contains:
            return

        # Store initial position
        if self.endpoint_type == 'start':
            self.press = (self.line_shape.start_x, self.line_shape.start_y), event.xdata, event.ydata
        else:  # end
            self.press = (self.line_shape.end_x, self.line_shape.end_y), event.xdata, event.ydata

        DraggableLineHandle.lock = self

        # draw everything but the selected and store the pixel buffer
        canvas = self.handle.figure.canvas
        axes = self.handle.axes

        self.handle.set_animated(True)
        self.line_shape.line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.handle.axes.bbox)

        # now redraw just the selected
        axes.draw_artist(self.line_shape.line)
        axes.draw_artist(self.handle)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggableLineHandle.lock is not self:
            return
        if event.inaxes != self.handle.axes:
            return

        (orig_x, orig_y), xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        # Update line endpoint
        if self.endpoint_type == 'start':
            self.line_shape.start_x = orig_x + dx
            self.line_shape.start_y = orig_y + dy
        else:  # end
            self.line_shape.end_x = orig_x + dx
            self.line_shape.end_y = orig_y + dy

        # Highlight/select on drag
        if self.movingStart == False:
            self.movingStart = True
            self.line_shape.select()

        # Update visual representation
        self.line_shape.repaintShape()

        canvas = self.handle.figure.canvas
        axes = self.handle.axes

        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current
        axes.draw_artist(self.line_shape.line)
        axes.draw_artist(self.line_shape.handle_start)
        axes.draw_artist(self.line_shape.handle_end)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

        # Notify shape changes during drag (throttled to every 3rd frame)
        self.motion_counter += 1
        if self.motion_counter % 3 == 0:
            self.paintComp.notifyShapesChanged()
            self.paintComp.line_profile_changed = not self.paintComp.line_profile_changed

    def on_release(self, event):
        """On release we reset the press data."""
        if DraggableLineHandle.lock is not self:
            return

        self.press = None
        DraggableLineHandle.lock = None
        self.motion_counter = 0

        # turn off the current animation property and reset the background
        self.handle.set_animated(False)
        self.line_shape.line.set_animated(False)
        self.background = None

        # Deselect line after editing (return to original cyan color)
        if self.movingStart:
            self.line_shape.deselect()
            self.line_shape.repaintShape()
            # Final notification
            self.paintComp.notifyShapesChanged()
            self.paintComp.line_profile_changed = not self.paintComp.line_profile_changed

        self.handle.figure.canvas.draw_idle()
        self.paintComp.fillListOfPaintedShapes()
        self.movingStart = False

    def disconnect(self):
        """Disconnect all the stored connection ids."""
        self.handle.figure.canvas.mpl_disconnect(self.cidpress)
        self.handle.figure.canvas.mpl_disconnect(self.cidrelease)
        self.handle.figure.canvas.mpl_disconnect(self.cidmotion)
