#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide2 import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtCharts import *
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename as get
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import scipy.misc
import matplotlib.pyplot as plt
import matplotlib
from numpy import *
import astropy.visualization as vis
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap


@Slot()
def load_fits_file():
    fileName = QFileDialog.getOpenFileName(mainWin, "Open Image", "/home/akond/Pulpit/fits", "Fits files (*.fits)")[0]

    fits_plot = FitsPlotter(fileName)
    fits_plot.plot_fits_file()
    fig = fits_plot.figure
    canvas = FigureCanvas(fig)
    mainWin.central_widget.image_widget.layout.addWidget(canvas)
    mainWin.central_widget.image_widget.setLayout(mainWin.central_widget.image_widget.layout)
    # mainWin.image_widget.show_image()


@Slot()
def clear_image():
    # temporary
    widgets_size = mainWin.central_widget.image_widget.layout.count()
    widget_to_remove = mainWin.central_widget.image_widget.layout.itemAt(widgets_size - 1)
    widget_to_remove.widget().deleteLater()


class FitsPlotter(object):
    """Fits plotter"""

    def __init__(self, fitsfile, hdu=0,
                 figure=None, ax=None,
                 interval=None, intervalkwargs=None,
                 stretch=None, stretchkwargs=None):
        self.fitsfile = fitsfile
        self.hdu = 0
        self.figure = figure
        self.ax = ax
        self.interval = interval
        self.interval_kwargs = intervalkwargs
        self.stretch = stretch
        self.stretch_kwargs = stretchkwargs
        self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list('zielonka', ['w', 'g'], )
        self._data = None
        self.img = None

    @property
    def data(self):
        if self._data is None:
            hdus = fits.open(self.fitsfile, lazy_load_hdus=False)
            self._data = hdus[self.hdu].data
        return self._data

    def get_ax(self, figsize=(6, 6)):
        if self.ax is None:
            if self.figure is None:
                self.figure = plt.figure(figsize=figsize)
            self.ax = self.figure.add_subplot(111)
        return self.ax

    def plot_fits_data(self, data, ax, alpha, norm, cmap):
        self.img = ax.imshow(data, origin='lower', alpha=alpha,
                             norm=norm, cmap=cmap, resample=False)

    def plot_fits_file(self, ax=None, alpha=1.0):
        if ax is None:
            ax = self.get_ax()
        self.plot_fits_data(self.data, ax, alpha, self.get_normalization(), self.cmap)

    def set_normalization(self, stretch=None, interval=None, stretchkwargs={}, intervalkwargs={}):
        if stretch is None:
            if self.stretch is None:
                stretch = 'powerdist'
            else:
                stretch = self.stretch
        if isinstance(stretch, str):
            kwargs = self.prepare_kwargs(self.stretch_kws_defaults[stretch],
                                         self.stretch_kwargs, stretchkwargs)
            if stretch == 'asinh':  # arg: a=0.1
                stretch = vis.AsinhStretch(**kwargs)
            elif stretch == 'contrastbias':  # args: contrast, bias
                stretch = vis.ContrastBiasStretch(**kwargs)
            elif stretch == 'histogram':
                stretch = vis.HistEqStretch(self.data, **kwargs)
            elif stretch == 'linear':  # args: slope=1, intercept=0
                stretch = vis.LinearStretch(**kwargs)
            elif stretch == 'log':  # args: a=1000.0
                stretch = vis.LogStretch(**kwargs)
            elif stretch == 'powerdist':  # args: a=1000.0
                stretch = vis.PowerDistStretch(**kwargs)
            elif stretch == 'power':  # args: a
                stretch = vis.PowerStretch(**kwargs)
            elif stretch == 'sinh':  # args: a=0.33
                stretch = vis.SinhStretch(**kwargs)
            elif stretch == 'sqrt':
                stretch = vis.SqrtStretch(**kwargs)
            elif stretch == 'square':
                stretch = vis.SquaredStretch(**kwargs)
            else:
                raise ValueError('Unknown stretch:' + stretch)
        self.stretch = stretch
        if interval is None:
            if self.interval is None:
                interval = 'zscale'
            else:
                interval = self.interval
        if isinstance(interval, str):
            kwargs = self.prepare_kwargs(self.interval_kws_defaults[interval],
                                         self.interval_kwargs, intervalkwargs)
            if interval == 'minmax':
                interval = vis.MinMaxInterval(**kwargs)
            elif interval == 'manual':  # args: vmin, vmax
                interval = vis.ManualInterval(**kwargs)
            elif interval == 'percentile':  # args: percentile, n_samples
                interval = vis.PercentileInterval(**kwargs)
            elif interval == 'asymetric':  # args: lower_percentile, upper_percentile, n_samples
                interval = vis.AsymmetricPercentileInterval(**kwargs)
            elif interval == 'zscale':  # args: nsamples=1000, contrast=0.25, max_reject=0.5, min_npixels=5, krej=2.5, max_iterations=5
                interval = vis.ZScaleInterval(**kwargs)
            else:
                raise ValueError('Unknown interval:' + interval)
        self.interval = interval
        if self.img is not None:
            self.img.set_norm(vis.ImageNormalize(self.data, interval=self.interval, stretch=self.stretch, clip=True))

    def get_normalization(self, stretch=None, interval=None,
                          stretchkwargs={}, intervalkwargs={}):
        self.set_normalization(stretch, interval, stretchkwargs, intervalkwargs)
        return vis.ImageNormalize(self.data, interval=self.interval, stretch=self.stretch, clip=True)

    def prepare_kwargs(self, defaults, *specific):
        r = defaults.copy()
        for d in specific:
            if d is not None:
                r.update(d)
        return {k: r[k] for k in defaults.keys()}

    def reset_ax(self):
        self.ax = None
        self.figure = None

    interval_kws_defaults = {
        'minmax': {},
        'manual': {'vmin': 0.0, 'vmax': 30000},
        'percentile': {'percentile': 0.1, 'n_samples': 1000},
        'asymetric': {'lower_percentile': 0.1, 'upper_percentile': 0.2, 'n_samples': 1000},
        'zscale': {'nsamples': 1000, 'contrast': 0.25, 'max_reject': 0.5,
                   'min_npixels': 5, 'krej': 2.5, 'max_iterations': 5},
    }

    stretch_kws_defaults = {
        'asinh': {'a': 0.1},
        'contrastbias': {'contrast': 2.0, 'bias': 1.0},
        'histogram': {},
        'linear': {'slope': 1.0, 'intercept': 0.0},
        'log': {'a': 1000.0},
        'powerdist': {'a': 1000.0},
        'power': {'a': 1.0},
        'sinh': {'a': 0.333333},
        'sqrt': {},
        'square': {},
    }


class CentralWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.button_widget = ButtonsWidget()
        self.image_widget = ImageWidget()
        self.layout.addWidget(self.button_widget)
        self.layout.addWidget(self.image_widget)

        self.setLayout(self.layout)


class ImageWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()


class ButtonsWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.layout = QGridLayout()
        load_button = QPushButton("Load fits file")
        clear_button = QPushButton("Clear")

        load_button.clicked.connect(load_fits_file)
        clear_button.clicked.connect(clear_image)

        self.layout.addWidget(load_button, 0, 0)
        self.layout.addWidget(clear_button, 0, 1)

        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("TEDA")
        self.central_widget = CentralWidget()
        # self.buttons_widget = ButtonsWidget()
        # self.image_widget = ImageWidget()
        self.setCentralWidget(self.central_widget)


    # def create_menu(self):
    #     self.file_menu = self.menuBar().addMenu("File")
    #     self.file_menu.addAction(self.draw_fits_image())


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(800, 600)
    mainWin.show()
    sys.exit(app.exec_())