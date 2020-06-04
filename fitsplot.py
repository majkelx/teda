#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import json

import traitlets as tr
from numpy import *
import math

import astropy.visualization as vis

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class FitsPlotter(tr.HasTraits):
    """Fits plotter"""
    # contrast = traitlets.Float()
    mouse_xdata = tr.Float(allow_none=True)
    mouse_ydata = tr.Float(allow_none=True)
    alpha = tr.Float(default_value=1.0, max=1.0, min=0.0)

    viewX = tr.Float()
    viewY = tr.Float()
    viewW = tr.Float()
    viewH = tr.Float()
    viewBounaries_versionno = tr.Int()

    plot_grid = tr.Bool(default_value=False)

    def __init__(self,
                 figure=None, ax=None,
                 interval=None, intervalkwargs=None,
                 stretch=None, stretchkwargs=None, cmap=None):
        super().__init__()
        self._data = None
        self.wcs = None
        self.figure = figure
        self.ax = ax
        self.zoom = 1.0
        self.interval = interval
        self.interval_kwargs = intervalkwargs
        self.stretch = stretch
        self.stretch_kwargs = stretchkwargs
        if cmap is None:
            self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list('zielonka', ['w', 'g'], )
        else:
            self.cmap = cmap
        self.img = None
        self.observe(lambda change: self.on_show_grid(change), ['plot_grid'])

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, d):
        self._data = d

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
            if self.wcs is not None:
                self.ax = self.figure.add_subplot(111, projection=self.wcs)
            else:
                self.ax = self.figure.add_subplot(111)
            self.setup_axies()
        return self.ax

    def plot_fits_data(self, data, ax, alpha, norm, cmap):
        extent = (0.5, data.shape[1] + 0.5, 0.5, data.shape[0] + 0.5)
        if self.img is not None:
            self.img.set_data(data)
            self.img.set_extent(extent)
            self.img.set_norm(norm)
            self.img.set_alpha(alpha)
            self.img.set_cmap(cmap)
        else:
            self.img = ax.imshow(data, origin='lower', extent=extent,
                                 alpha=alpha, norm=norm, cmap=cmap, resample=False)


    def plot(self):
        # if color is not None:
        #     self.changeCmap(color)
        ax = self.get_ax()
        data = self.data;
        if data is not None:
            self.plot_fits_data(data, ax, self.alpha, self.get_normalization(), self.cmap)
            self.invalidate()

    def set_cmap(self, cmap):
        self.cmap = cmap
        if self.img is not None:
            self.img.set_cmap(cmap)

    def set_normalization(self, stretch=None, interval=None, stretchkwargs={}, intervalkwargs={}):
        if stretch is None:
            if self.stretch is None:
                stretch = 'linear'
            else:
                stretch = self.stretch
        if isinstance(stretch, str):
            print(stretch, ' '.join([f'{k}={v}' for k, v in stretchkwargs.items()]))
            if self.data is None:  # can not calculate objects yet
                self.stretch_kwargs = stretchkwargs
            else:
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
                    stretch = vis.SqrtStretch()
                elif stretch == 'square':
                    stretch = vis.SquaredStretch()
                else:
                    raise ValueError('Unknown stretch:' + stretch)
        self.stretch = stretch
        if interval is None:
            if self.interval is None:
                interval = 'zscale'
            else:
                interval = self.interval
        if isinstance(interval, str):
            print(interval, ' '.join([f'{k}={v}' for k, v in intervalkwargs.items()]))
            kwargs = self.prepare_kwargs(self.interval_kws_defaults[interval],
                                         self.interval_kwargs, intervalkwargs)
            if self.data is None:
                self.interval_kwargs = intervalkwargs
            else:
                if interval == 'minmax':
                    interval = vis.MinMaxInterval()
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

    def get_normalization(self):
        if not isinstance(self.interval, vis.BaseInterval) or not isinstance(self.stretch, vis.BaseStretch):
            self.set_normalization(self.stretch, self.interval)
        return vis.ImageNormalize(self.data, interval=self.interval, stretch=self.stretch, clip=True)

    # def copy_visualization_parameters(self, source):
    #     self.cmap = source.cmap
    #     self.alpha = source.alpha
    #     self.set_normalization(source.stretch, source.interval)

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

    def invalidate(self, idle=True):
        if idle:
            self.figure.canvas.draw_idle()
        else:
            self.figure.canvas.draw()

    def setup_axies(self):
        fig = self.ax.get_figure()
        fig.subplots_adjust(wspace=0)
        self.set_axies_margins()

        self.zoomEvent = fig.canvas.mpl_connect('scroll_event', lambda event: self.on_zoom(event))
        self.mouseExitEvent = fig.canvas.mpl_connect('figure_leave_event', lambda event: self.on_mouse_exit(event))
        self.mouseMoveEvent = fig.canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event))

    def set_axies_margins(self):
        if self.plot_grid:
            self.ax.set_position([0.1, 0.1, 0.9, 0.9])
            # self.ax
        else:
            self.ax.set_position([0.0, 0.0, 1.0, 1.0])
            locator = self.ax.yaxis.get_major_locator()
            self.ax.yaxis.set_major_locator(plt.NullLocator())
            self.ax.xaxis.set_major_locator(plt.NullLocator())

    def disconnectEvents(self):
        self.figure.canvas.mpl_disconnect(self.zoomEvent)

    def on_show_grid(self, change):
        if self.ax:
            self.set_axies_margins()
            self.ax.grid(change.new)
            self.invalidate()


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

            self.invalidate()  # force re-draw the next time the GUI refreshes
            self.setCordsToTraitlets()

    def setZoom(self, zoom:float, reset_pos:bool):
        if reset_pos:
            self.ax.set_xlim(self.full_xlim)
            self.ax.set_ylim(self.full_ylim)
            self.zoom = 1.0
            self.invalidate()
            self.setCordsToTraitlets()
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
            self.invalidate()
            self.setCordsToTraitlets()

    def setCordsToTraitlets(self):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        self.viewX = cur_xlim[0]
        self.viewY = cur_ylim[0]
        self.viewW = cur_xlim[1] - cur_xlim[0]
        self.viewH = cur_ylim[1] - cur_ylim[0]
        self.viewBounaries_versionno += 1

    def moveToXYcordsWithZoom(self, x, y, zoom, fits, idle=True):
        self.get_ax()
        full_xlim = fits.full_xlim
        full_ylim = fits.full_ylim
        xsize = ((full_xlim[1] - full_xlim[0]) / 2)/zoom
        ysize = ((full_ylim[1] - full_ylim[0]) / 2)/zoom
        newxlim = x - xsize, x + xsize
        newylim = y - ysize, y + ysize
        self.ax.set_xlim(newxlim)
        self.ax.set_ylim(newylim)
        self.invalidate(idle)

    def moveToXYcords(self, x, y, idle=True):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xsize = (cur_xlim[1] - cur_xlim[0])
        ysize = (cur_ylim[1] - cur_ylim[0])
        newxlim = x, x + xsize
        newylim = y, y + ysize
        self.ax.set_xlim(newxlim)
        self.ax.set_ylim(newylim)
        self.ax.figure.canvas.draw_idle()
        self.invalidate(idle)

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