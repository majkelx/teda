from os import path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedLayout, QLabel, QFormLayout, QLineEdit

import numpy as np


class InfoWidget(QWidget):

    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainwindow = mainwindow
        self.filename = QLineEdit(mainwindow.filename)
        self.filename.setReadOnly(True)  # Phase 6.11: Allow copy

        self.value = QLineEdit('')
        self.value.setReadOnly(True)  # Phase 6.11: Allow copy

        self.xy = QLineEdit('')
        self.xy.setReadOnly(True)  # Phase 6.11: Allow copy

        self.wcs_coo = QLineEdit('')
        self.wcs_coo.setReadOnly(True)  # Phase 6.11: Allow copy

        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Filename', self.filename)
        layout.addRow('Value', self.value)
        layout.addRow('Image x,y', self.xy)
        layout.addRow('WCS', self.wcs_coo)
        self.setLayout(layout)
        self.formlayout = layout

        mainwindow.fits_image.observe(lambda change: self.on_filename_change(change), ['fitsfile'])
        mainwindow.cursor_coords.observe(lambda change: self.on_xy_change(change), ['img_versionno'])
        mainwindow.cursor_coords.observe(lambda change: self.on_wcs_change(change), ['wcs_formatted'])
        mainwindow.cursor_coords.observe(lambda change: self.on_wcs_system_change(change), ['wcs_framename'])


    def on_filename_change(self, change):
        self.filename.setText(path.basename(change.new))
        self.filename.setCursorPosition(0)  # Show beginning of filename

    def on_wcs_system_change(self, change):
        try:
            self.formlayout.labelForField(self.wcs_coo).setText(change.new)
        except Exception as e:
            print('wcs label exceptrion', e)
            pass

    def on_wcs_change(self, change):
        self.wcs_coo.setText(change.new)
        self.wcs_coo.setCursorPosition(0)  # Show beginning of WCS coordinates

    def on_xy_change(self, change):
        coords = self.mainwindow.cursor_coords
        x,y = coords.img_x, coords.img_y
        if x is not None and y is not None:
            self.xy.setText(f'{x:.3f} {y:.3f}')
            self.xy.setCursorPosition(0)  # Show beginning of coordinates
            val = self.mainwindow.fits_image.value(x,y)
            if val is not None and not np.isnan(val):
                self.value.setText(f'{val:.5f}')
                self.value.setCursorPosition(0)  # Show beginning of value
            else:
                self.value.setText('')
        else:
            self.xy.setText('')
            self.value.setText('')
