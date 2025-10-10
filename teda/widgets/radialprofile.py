import numpy as np
import PySide6
from PySide6.QtWidgets import QWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class RadialProfileWidget(QWidget):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_on = True
        self.data = data
        self.x = 500
        self.y = 675
        self.radius = 20
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(2.5, 2.5))
        # self.fig.tight_layout()

        canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.plotted_profile = self.ax.plot([1,2,3,4],[1,4,6,8])[0]

        figure_layout.addWidget(canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(50)

        # import matplotlib.pyplot as plt
        # axes = plt.axes()
        # axes.set_ylim([0, 1])

    def showEvent(self, event: PySide6.QtGui.QShowEvent):
        super().showEvent(event)
        # self.turn_on()
        self.invalidate()

    # def hideEvent(self, event: PySide6.QtGui.QHideEvent):
    #     super().hideEvent(event)
    #     self.turn_off()

    def set_centroid(self, x, y, radius=None):
        self.x = x
        self.y = y
        if radius:
            self.radius = radius
        self.invalidate()

    def set_radius(self, radius):
        self.radius = radius
        self.invalidate()

    def set_data(self, data):
        self.data = data
        self.invalidate()

    # def turn_off(self):
    #     self.is_on = False
    #
    # def turn_on(self):
    #     self.is_on = True
    #     self.invalidate()

    def invalidate(self):
        if not self.isVisible() or self.data is None:
            return
        rad, val = self.calc_profile()
        self.plotted_profile.set_xdata(rad)
        self.plotted_profile.set_ydata(val)
        self.ax.autoscale(tight=True)
        self.ax.relim()
        self.ax.autoscale(tight=True)
        # self.ax.plot(rad,val)
        self.fig.canvas.draw_idle()

    def calc_profile(self):
        return self.get_radius_brightness(self.x, self.y, self.radius, self.data)

    @staticmethod
    def get_circle_brightness(x0, y0, r, img):
        # step_rad = np.pi * 0.1 /r; make the density dependent on the radius
        step_rad = np.pi * 0.01;
        c = 0
        brightness = 0
        for rad in np.arange(0, 2 * np.pi, step_rad):
            x = int(r * np.sin(rad) + x0)
            y = int(r * np.cos(rad) + y0)
            try:
                if x < 0 or y < 0:
                    raise IndexError()
                v = img[y, x]
                c = c + 1
            except IndexError:
                v = 0
            brightness = brightness + v
        try:
            brightness = brightness / c
        except ArithmeticError:
            brightness = 0.0
        return brightness


    def get_radius_brightness(self, x0, y0, rmax, img):
        # suppose the center point of the image is the center of the star
        radius = []
        result = []
        for r in np.arange(0.1, rmax, 0.1):
            b = self.get_circle_brightness(x0, y0, r, img);
            result.append(b)
            radius.append(r)
        return radius, result









