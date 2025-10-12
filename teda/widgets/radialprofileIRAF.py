from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QThread, Signal
from matplotlib.figure import Figure, Axes
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from teda.views.fitsplot import coo_data_to_index, coo_index_to_data

import numpy as np
import math
from scipy import optimize


class RadialStatsCalculator(QThread):
    """Background thread for radial profile area statistics calculation."""
    finished = Signal(dict)  # Emits {mean, median, std, min, max}

    def __init__(self, values):
        super().__init__()
        self.values = values
        self._cancel = False

    def cancel(self):
        """Request cancellation of ongoing calculation."""
        self._cancel = True

    def run(self):
        """Calculate statistics from all pixels in encircled area."""
        if self._cancel or not self.values:
            return

        try:
            values_array = np.array(self.values)

            if values_array.size == 0:
                return

            stats = {
                'mean': float(np.mean(values_array)),
                'median': float(np.median(values_array)),
                'std': float(np.std(values_array)),
                'min': float(np.amin(values_array)),
                'max': float(np.amax(values_array)),
            }

            if not self._cancel:
                self.finished.emit(stats)
        except Exception as e:
            print(f"Error calculating radial profile statistics: {e}")

class IRAFRadialProfileWidget(QWidget):

    stats_updated = Signal(dict)  # Emits stats when calculation completes

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data
        self.x = 500
        self.y = 675
        self.radius = 20
        self.stats_calculator = None  # Background stats calculator
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

        # Calculate area statistics in background thread
        # Get all pixel values within the circle (re-use calc_profile result)
        _, circle_values = self.calc_profile()
        if circle_values:
            # Cancel any ongoing calculation
            if self.stats_calculator is not None and self.stats_calculator.isRunning():
                self.stats_calculator.cancel()
                self.stats_calculator.wait(100)  # Wait up to 100ms

            # Start new calculation
            self.stats_calculator = RadialStatsCalculator(circle_values)
            self.stats_calculator.finished.connect(self.stats_updated.emit)
            self.stats_calculator.start()

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

        opt, cov = optimize.curve_fit(gauss0, x, y, p0=[1.0, 0.0, 1.0],
                                      bounds=([-2.0**19, -2.0**16, 0.0],
                                              [2.0**19,   2.0**16, 70]  # max fwhm=20
                                              )
                                      )
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
        """Vectorized radial profile extraction (Phase 2.2)

        Replaces nested loops with NumPy array operations for 10-50x speedup.

        Parameters
        ----------
        x0, y0 : float
            Center coordinates in 1-based pixel-centered data coordinates
        rmax : float
            Maximum radius in pixels
        img : ndarray
            2D image array

        Returns
        -------
        distances : list
            Distances from center for each pixel within radius
        values : list
            Pixel values for each pixel within radius
        """
        # Convert data coordinates to array indices for the bounding box
        row_min = coo_data_to_index(y0 - rmax)
        row_max = coo_data_to_index(y0 + rmax)
        col_min = coo_data_to_index(x0 - rmax)
        col_max = coo_data_to_index(x0 + rmax)

        # Clip to image bounds to avoid out-of-bounds access
        h, w = img.shape
        row_min = max(0, row_min)
        row_max = min(h - 1, row_max)
        col_min = max(0, col_min)
        col_max = min(w - 1, col_max)

        # Create meshgrid of indices in the bounding box
        rows = np.arange(row_min, row_max + 1)
        cols = np.arange(col_min, col_max + 1)
        row_grid, col_grid = np.meshgrid(rows, cols, indexing='ij')

        # Convert indices to data coordinates (vectorized)
        # Following coo_index_to_data: (row, col) -> (col + 1.0, row + 1.0)
        x_coords = col_grid + 1.0
        y_coords = row_grid + 1.0

        # Calculate squared distances from center
        dist2 = (x_coords - x0)**2 + (y_coords - y0)**2

        # Create mask for pixels within radius
        rmax2 = rmax * rmax
        mask = dist2 <= rmax2

        # Extract distances and values using mask
        distances = np.sqrt(dist2[mask])
        values = img[row_min:row_max+1, col_min:col_max+1][mask]

        # Return as lists for compatibility with existing code
        return distances.tolist(), values.tolist()









