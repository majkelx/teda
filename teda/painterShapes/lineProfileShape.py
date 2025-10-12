from PySide6.QtCore import Qt
import matplotlib.pyplot as plt


class LineProfileShape(object):
    """Line profile shape with two draggable endpoint handles."""

    def __init__(self, start_x, start_y, end_x, end_y, thickness=1.0, color='#1f77b4'):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.thickness = thickness  # Phase A: always 1.0, reserved for future
        self.color = color
        self.selectionColor = 'yellow'
        self.selected = False
        self.originColor = color
        self.shapeType = "lineProfile"

        # Matplotlib objects (created in paintShape)
        self.line = None
        self.handle_start = None
        self.handle_end = None

    def paintShape(self, axes):
        """Paint line and two endpoint handles."""
        # Draw line
        self.line, = axes.plot([self.start_x, self.end_x],
                               [self.start_y, self.end_y],
                               color=self.color, linewidth=1, alpha=0.7)

        # Draw endpoint handles (circles)
        self.handle_start, = axes.plot([self.start_x], [self.start_y], 'o',
                                       color=self.color, markersize=8,
                                       markeredgewidth=2, markerfacecolor='none')
        self.handle_end, = axes.plot([self.end_x], [self.end_y], 'o',
                                     color=self.color, markersize=8,
                                     markeredgewidth=2, markerfacecolor='none')

        # Return all objects as list for draggable handles
        return [self.line, self.handle_start, self.handle_end]

    def repaintShape(self, axes=None):
        """Update line and handles after position change (e.g., during drag)."""
        if self.line:
            self.line.set_data([self.start_x, self.end_x],
                              [self.start_y, self.end_y])
            self.line.set_color(self.color)

        if self.handle_start:
            self.handle_start.set_data([self.start_x], [self.start_y])
            self.handle_start.set_color(self.color)

        if self.handle_end:
            self.handle_end.set_data([self.end_x], [self.end_y])
            self.handle_end.set_color(self.color)

    def refreshShape(self, axes):
        """Refresh shape visual properties (color, selection state)."""
        self.repaintShape(axes)
        return [self.line, self.handle_start, self.handle_end]

    def paintAdditional(self, axes):
        """Paint additional elements (none for line profile in Phase A)."""
        pass

    def repaintAdditional(self, axes):
        """Repaint additional elements (none for line profile in Phase A)."""
        pass

    def removeAdditional(self):
        """Remove additional elements (none for line profile in Phase A)."""
        pass

    def selectDeselect(self):
        """Toggle selection state."""
        if self.selected == False:
            self.selected = True
            self.color = self.selectionColor
        else:
            self.selected = False
            self.color = self.originColor

    def select(self):
        """Mark shape as selected."""
        self.selected = True
        self.color = self.selectionColor

    def deselect(self):
        """Mark shape as deselected."""
        self.selected = False
        self.color = self.originColor

    def getShape(self):
        """Return the main shape object (line)."""
        return self.line
