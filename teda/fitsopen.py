#!/usr/bin/env python
# -*- coding: utf-8 -*-

from astropy.io import fits
from astropy.io.fits.hdu import(PrimaryHDU, ImageHDU)
import astropy.visualization as vis

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class FitsOpen(object):
    """Open clear fits"""

    def __init__(self, fitsfile):
        self.fitsfile = fitsfile
        self.hdu = 0
        self._hdus = None
        self.img = None
        self.figure = None
        self.ax = None
        self.cmap = 'gray'

    def open(self):
        if self._hdus is None:
            self._hdus = fits.open(self.fitsfile, lazy_load_hdus=True, memmap=True)
            self._hdus.info()

    @property
    def data(self):
        self.open()
        if isinstance(self._hdus[self.hdu], PrimaryHDU) or isinstance(self._hdus[self.hdu], ImageHDU):
            return self._hdus[self.hdu].data
        else:
            return None

    @property
    def header(self):
        self.open()
        return self._hdus[self.hdu].header

    def get_ax(self, figsize=(6, 6)):
        if self.ax is None:
            if self.figure is None:
                self.figure = plt.figure(figsize=figsize)
            self.ax = self.figure.add_subplot(111)
        return self.ax

    def plot_fits_data(self, data, ax, alpha, cmap):
        self.img = ax.imshow(data, origin='lower', alpha=alpha, cmap=cmap, resample=False)

    def plot_fits_file(self, ax=None, alpha=1.0):
        if ax is None:
            ax = self.get_ax()
        data = self.data
        if data is not None:
            self.plot_fits_data(data, ax, alpha, self.cmap)

    def reset_ax(self):
        self.ax = None
        #self.figure.
        plt.close(self.figure)
        self.figure = None

    def changeHDU(self, relative, val):
        if relative:
            self.hdu = self.hdu + val
        else:
            self.hdu = val;
        if self.hdu < 0:
            self.hdu = 0
        elif self.hdu > len(self._hdus) - 1:
            self.hdu = len(self._hdus) - 1

        self.reset_ax()
        self.plot_fits_file()