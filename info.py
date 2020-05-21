from os import path
import PySide2
from PySide2.QtWidgets import QWidget, QHBoxLayout, QStackedLayout, QLabel, QFormLayout, QLineEdit
from matplotlib.figure import Figure, Axes
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from fitsplot import coo_data_to_index, coo_index_to_data

import numpy as np
import math
from scipy import optimize


class InfoWidget(QWidget):

    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainwindow = mainwindow
        self.filename = QLineEdit(mainwindow.filename)
        self.filename.setEnabled(False)

        self.value = QLineEdit('')
        self.value.setEnabled(False)

        self.xy = QLineEdit('')
        self.xy.setEnabled(False)

        self.wcs_coo = QLineEdit('')
        self.wcs_coo.setEnabled(False)

        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Filename', self.filename)
        layout.addRow('Value', self.value)
        layout.addRow('Image x,y', self.xy)
        layout.addRow('WCS', self.wcs_coo)
        self.setLayout(layout)

        mainwindow.fits_image.observe(lambda change: self.on_filename_change(change), ['fitsfile'])
        mainwindow.cursor_coords.observe(lambda change: self.on_xy_change(change), ['img_versionno'])


    def on_filename_change(self, change):
        self.filename.setText(path.basename(change.new))

    def on_xy_change(self, change):
        coords = self.mainwindow.cursor_coords
        x,y = coords.img_x, coords.img_y
        if x is not None and y is not None:
            self.xy.setText(f'{x:.3f} {y:.3f}')
            val = self.mainwindow.fits_image.value(x,y)
            wx, wy =  coords.wcs_x_deg, coords.wcs_y_deg
            if val is not None and not np.isnan(val):
                self.value.setText(f'{val:.5f}')
            else:
                self.value.setText('')
            if wx is not None and wy is not None:
                self.wcs_coo.setText(f'{wx:.6f}, {wy:.6f}')
            else:
                self.wcs_coo.setText('')
        else:
            self.xy.setText('')
            self.value.setText('')
            self.wcs_coo.setText('')
