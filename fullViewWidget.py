import numpy as np
import PySide2
from PySide2.QtWidgets import QWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from fitsplot import (FitsPlotter)


class FullViewWidget(QWidget):

    def __init__(self, fits, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fits = fits
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(6, 6))
        # self.fig.tight_layout()

        self.fits_image = FitsPlotter(figure=self.fig)
        self.canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)

        figure_layout.addWidget(self.canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(150)
        self.setMinimumWidth(150)
        self.setMaximumWidth(150)
        self.setMaximumHeight(150)

    def setNewFits(self,fits):
        self.fits = fits
        self.fits_image.figure.add_subplot(111)
        self.fits_image.plot_fits_data(self.fits.data,self.fits_image.figure.axes[0],1.0, self.fits.get_normalization(),self.fits.cmap)
        #self.fits_image.figure.axes[0].images = self.fits.figure.axes[0].images
        self.fits_image.invalidate()
        self.fig.canvas.draw_idle()

    def invalidate(self):
        self.fig.canvas.draw_idle()