from PySide2.QtWidgets import QWidget, QHBoxLayout
from matplotlib.figure import Figure, Axes
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from teda.views.fitsplot import coo_data_to_index, coo_index_to_data

import numpy as np
import math
from scipy import optimize

class IRAFRadialProfileWidget(QWidget):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data
        self.x = 500
        self.y = 675
        self.radius = 20
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(2.5, 2.5))
        # self.fig.tight_layout()

        canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.setup_axies(self.ax)


        # self.gaussian = self.ax.fill_between([1,2,3,4],[1,4,6,8], alpha=0.5)
        self.plotted_profile = self.ax.plot([1,2,3,4],[1,4,6,8], '.', alpha=0.6,ms=1)[0]
        self.gaussian = self.ax.plot([1,2,3,4],[1,4,6,8], alpha=0.9, lw=0.5)[0]

        # self.rms_legend = self.ax.text(1,0.99, 'Gauss RMS: <?> ',
        #                                horizontalalignment='right',
        #                                verticalalignment='top',
        #                                transform=self.ax.transAxes
        #                                )

        figure_layout.addWidget(canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(50)

        # import matplotlib.pyplot as plt
        # axes = plt.axes()
        # axes.set_ylim([0, 1])

    def setup_axies(self, ax: Axes):
        # ax.tick_params()
        # ax.yaxis.set_tick_params(direction='in')
        self.ax.tick_params(axis='both', labelsize='small', direction='in')
        # self.ax.tick_params(axis='both', labelsize='small')


        @ticker.FuncFormatter
        def formatter(v, pos):
            if pos < 0.001:
                return ''
            if v >= 10000:
                return f'{v/1000.0:.0f}k'
            if v >= 1000:
                return f'{v/1000.0:.1f}k'
            return f'{v:4g}'

        ax.yaxis.set_major_formatter(formatter)

        # ax.yaxis.set_major_locator(plt.NullLocator())
        # ax.xaxis.set_major_locator(plt.NullLocator())
        # fig = ax.get_figure()
        # fig.canvas.mpl_connect('scroll_event', lambda event: self.on_zoom(event))
        # fig.canvas.mpl_connect('figure_leave_event', lambda event: self.on_mouse_exit(event))
        # fig.canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event))


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

    def invalidate(self):
        rad, val = self.calc_profile()
        self.plotted_profile.set_xdata(rad)
        self.plotted_profile.set_ydata(val)

        try:
            rad, val, rmse, fwhm, sky = self.fit_gaussian(rad, val, self.radius)
            self.gaussian.set_xdata(rad)
            self.gaussian.set_ydata(val)
            self.ax.set_title(f'rms:{rmse:.2f} fwhm:{fwhm:.2f} sky:{sky:.2f}', fontsize='small')
            # self.rms_legend.set_text(f'rms={rmse:.2f} fwhm={fwhm:.2f} sky={sky:.2f} ')
        except Exception as e:
            print('Radial Profile:', e)
            pass

        # self.ax.autoscale()
        self.ax.relim()
        self.ax.autoscale()
        self.ax.margins
        # self.ax.plot(rad,val)
        self.fig.canvas.draw_idle()

    def fit_gaussian(self, x, y, ymax):
        """
        Fits gaussian + sky of mu=0

        Returns
        -------
        x_linespace, y_fit, rmse, fwhm, sky
        """
        # mu=0 gaussian + constant
        x, y = np.asarray(x), np.asarray(y)
        gauss0 = lambda x, a, c, sig2: c + a * np.exp(-x**2/(2*sig2))

        opt, cov = optimize.curve_fit(gauss0, x, y, p0=[1.0, 0.0, 1.0])
        res = gauss0(x, *opt) - y
        rmse = math.sqrt((res*res).sum()/len(res))
        try:
            fwhm = 2.355 * math.sqrt(opt[2])
        except ValueError:
            fwhm = 0
        sky = opt[1]
        xs = np.linspace(0, ymax)
        return xs, gauss0(xs, *opt), rmse, fwhm, sky

    def calc_profile(self):
        return self.get_radius_brightness(self.x, self.y, self.radius, self.data)


    def get_radius_brightness(self, x0, y0, rmax, img):
        distances = []
        values = []
        rmax2 = rmax * rmax
        for i in range(coo_data_to_index(y0 - rmax), coo_data_to_index(y0 + rmax) + 1):
            for j in range(coo_data_to_index(x0 - rmax), coo_data_to_index(x0 + rmax) + 1):
                try:
                    v = img[i,j]
                    pixelpos = coo_index_to_data([i,j])
                    dist2 = (pixelpos[0] - x0)**2 + (pixelpos[1] - y0)**2
                    if dist2 <= rmax2:
                        distances.append(math.sqrt(dist2))
                        values.append(v)
                except (LookupError, TypeError):
                    pass # pixel out of table or no table
        return distances, values









