#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import json

import traitlets as tr
from numpy import *
import math

from astropy.io import fits
from astropy.io.fits.hdu import(PrimaryHDU, ImageHDU)
import astropy.visualization as vis

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class FitsPlotter(tr.HasTraits):
    """Fits plotter"""
    # contrast = traitlets.Float()
    mouse_xdata = tr.Float(allow_none=True)
    mouse_ydata = tr.Float(allow_none=True)
    fitsfile = tr.Unicode(allow_none=True)

    viewX = tr.Float()
    viewY = tr.Float()
    viewW = tr.Float()
    viewH = tr.Float()

    def __init__(self, fitsfile=None, hdu=0,
                 figure=None, ax=None,
                 interval=None, intervalkwargs=None,
                 stretch=None, stretchkwargs=None):
        self.fitsfile = fitsfile
        self.hdu = 0
        self.figure = figure
        self.ax = ax
        self.zoom = 1.0
        self.interval = interval
        self.interval_kwargs = intervalkwargs
        self.stretch = stretch
        self.stretch_kwargs = stretchkwargs
        self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list('zielonka', ['w', 'g'], )
        self._huds = None
        self.img = None

    def open(self):
        if self._huds is None and self.fitsfile:
            self._huds = fits.open(self.fitsfile, lazy_load_hdus=False)
            self._huds.info()

    def set_file(self, filename):
        self._huds = None
        self.fitsfile = filename

    @property
    def data(self):
        self.open()
        if self._huds is not None and \
                (isinstance(self._huds[self.hdu], PrimaryHDU) or isinstance(self._huds[self.hdu], ImageHDU)):
            return self._huds[self.hdu].data
        else:
            return None

    @property
    def header(self):
        self.open()
        try:
            return self._huds[self.hdu].header
        except (TypeError, LookupError):
            return None

    @property
    def full_xlim(self):
        return (-0.5, self.data.shape[1] - 0.5)

    @property
    def full_ylim(self):
        return (-0.5, self.data.shape[0] - 0.5)

    def get_ax(self, figsize=(6, 6)):
        if self.ax is None:
            if self.figure is None:
                self.figure = plt.figure(figsize=figsize)
            self.ax = self.figure.add_subplot(111)
            self.setup_axies(self.ax)
        return self.ax

    def plot_fits_data(self, data, ax, alpha, norm, cmap):
        extent = (0.5, data.shape[1] + 0.5, 0.5, data.shape[0] + 0.5)
        if self.img is not None:
            self.img.set_data(data)
            self.img.set_extent(extent)
        else:
            self.img = ax.imshow(data, origin='lower', extent=extent,
                                 alpha=alpha, norm=norm, cmap=cmap, resample=False)

    def plot_fits_data_old(self, data, ax, alpha, norm, cmap):
        self.img = ax.imshow(data, origin='lower',
                             alpha=alpha, norm=norm, cmap=cmap, resample=False)

    def plot_fits_file(self, ax=None, alpha=1.0, color=None):
        if color is not None:
            self.changeCmap(color)
        if ax is None:
            ax = self.get_ax()
        data = self.data;
        if data is not None:
            self.plot_fits_data(data, ax, alpha, self.get_normalization(), self.cmap)

    def changeCmap(self,color):
        self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list('zielonka', ['w', color], )

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
                # stretch = vis.LinearStretch(**kwargs)
                stretch = vis.LinearStretch()
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
        return   # one figure, one exies
        self.ax = None
        #self.figure.
        plt.close(self.figure)
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

    def changeHDU(self, relative, val):
        if relative:
            self.hdu = self.hdu + val
        else:
            self.hdu = val;
        if self.hdu < 0:
            self.hdu = 0
        elif self.hdu > len(self._huds) - 1:
            self.hdu = len(self._huds) - 1

        self.reset_ax()
        self.plot_fits_file()

    def invalidate(self):
        print('Invalidate')
        self.figure.canvas.draw_idle()

    def setup_axies(self, ax):
        ax.yaxis.set_major_locator(plt.NullLocator())
        ax.xaxis.set_major_locator(plt.NullLocator())
        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', lambda event: self.on_zoom(event))
        fig.canvas.mpl_connect('figure_leave_event', lambda event: self.on_mouse_exit(event))
        fig.canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event))

    def on_mouse_exit(self, event):
        self.mouse_xdata = None
        self.mouse_ydata = None

    def on_mouse_move(self, event):
        self.mouse_xdata = event.xdata
        self.mouse_ydata = event.ydata

    def on_zoom(self, event):
        # taken from https://gist.github.com/tacaswell/3144287
        base_scale = 1.2
        min_zoom = 0.1
        max_zoom = 50

        if event.button == 'up' :
            # deal with zoom in
            new_zoom = self.zoom * base_scale
        elif event.button == 'down':
            # deal with zoom out
            new_zoom = self.zoom / base_scale
        else:
            # deal with something that should never happen
            new_zoom = 1.0

        if min_zoom < new_zoom < max_zoom:
            self.zoom = new_zoom

            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            full_xlim = self.full_xlim
            full_ylim = self.full_ylim

            self.ax.set_xlim(self.calc_new_limits(cur_xlim, full_xlim, event.xdata, self.zoom))
            self.ax.set_ylim(self.calc_new_limits(cur_ylim, full_ylim, event.ydata, self.zoom))

            self.ax.figure.canvas.draw_idle()  # force re-draw the next time the GUI refreshes

    def setZoom(self, zoom:float, reset_pos:bool):
        if reset_pos:
            self.ax.set_xlim(self.full_xlim)
            self.ax.set_ylim(self.full_ylim)
            self.ax.figure.canvas.draw_idle()
            self.zoom = 1.0
            return
        min_zoom = 0.1
        max_zoom = 50

        new_zoom = self.zoom * zoom

        if min_zoom < new_zoom < max_zoom:
            self.zoom = new_zoom

            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            full_xlim = self.full_xlim
            full_ylim = self.full_ylim
            x = cur_xlim[0]+((cur_xlim[1] - cur_xlim[0]) / 2)
            y = cur_ylim[0]+((cur_ylim[1] - cur_ylim[0]) / 2)
            self.ax.set_xlim(self.calc_new_limits(cur_xlim, full_xlim, x, self.zoom))
            self.ax.set_ylim(self.calc_new_limits(cur_ylim, full_ylim, y, self.zoom))
            self.ax.figure.canvas.draw_idle()

    def moveToXYcordsWithZoom(self, x, y, zoom, fits):
        self.get_ax()
        full_xlim = fits.full_xlim
        full_ylim = fits.full_ylim
        xsize = ((full_xlim[1] - full_xlim[0]) / 2)/zoom
        ysize = ((full_ylim[1] - full_ylim[0]) / 2)/zoom
        newxlim = x - xsize, x + xsize
        newylim = y - ysize, y + ysize
        self.ax.set_xlim(newxlim)
        self.ax.set_ylim(newylim)
        self.ax.figure.canvas.draw_idle()

    def moveToXYcords(self, x, y):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xsize = (cur_xlim[1] - cur_xlim[0])
        ysize = (cur_ylim[1] - cur_ylim[0])
        newxlim = x, x + xsize
        newylim = y, y + ysize
        self.ax.set_xlim(newxlim)
        self.ax.set_ylim(newylim)
        self.ax.figure.canvas.draw_idle()

    def center(self):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        full_xlim = self.full_xlim
        full_ylim = self.full_ylim
        xsize = (cur_xlim[1] - cur_xlim[0])/2
        ysize = (cur_ylim[1] - cur_ylim[0])/2
        centerx = (full_xlim[1] - full_xlim[0])/2
        centery = (full_ylim[1] - full_ylim[0])/2
        newxlim = centerx - xsize, centerx + xsize
        newylim = centery - ysize, centery + ysize
        self.ax.set_xlim(newxlim)
        self.ax.set_ylim(newylim)

    def get_pixels_in_circle(self, center_x, center_y, radius):
        pix = []
        val = []
        radius2 = radius*radius
        for x in range(int(round(center_x - radius)), int(round(center_x + radius)) + 1):
            for y in range(int(round(center_y - radius)), int(round(center_y + radius)) + 1):
                if (x - center_x)**2 + (y - center_y)**2 <= radius2:
                    try:
                        val.append(self.data[ coo_data_to_index([x,y]) ])
                        pix.append((x,y))
                    except LookupError:
                        pass
        return pix, val

    def value(self, x, y):
        try:
            return self.data[coo_data_to_index([x,y])]
        except LookupError:
            return nan

    @staticmethod
    def calc_new_limits(cur_lim, full_lim, stationary, zoom):
        # get the current x and y limits
        # set the range
        cur_range = (cur_lim[1] - cur_lim[0])
        full_range = (full_lim[1] - full_lim[0])
        new_range = full_range / zoom
        new_lim = [stationary + new_range/cur_range*(cur_lim[0] - stationary), 0]

        max_margin = new_range - full_range
        # if new_lim[0] > max_margin:
        #     new_lim[0] -= new_lim[0] - max_margin
        #     print('Correction -')
        # elif new_lim[0] + new_range < full_range - max_margin:
        #     new_lim[0] += full_range - new_lim[0] - max_margin - new_range
        #     print('Correction +')
        new_lim[1] = new_lim[0] + new_range
        return new_lim


#  Functions for conversion between data pixel coordinates and data array indices
def coo_data_to_index(data_coo):
    """
    Converts 1-based pixel-centerd (x,y) coordinates to data index (row, col)

    data: (float, float) or float
        point in image data coordinates or single coordinate
    """
    try:
        return math.floor(data_coo[1] - 0.5), math.floor(data_coo[0] - 0.5)
    except (TypeError, IndexError):
        return math.floor(data_coo - 0.5)


def coo_index_to_data(index):
    """
    Converts data index (row, col) to 1-based pixel-centerd (x,y) coordinates of the center ot the pixel

    index: (int, int) or int
        (row,col) index of the pixel in dtatabel or single row or col index
    """
    return (index[1] + 1.0, index[0] + 1.0)