from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QThread, Signal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.ticker as ticker
import numpy as np
from scipy.ndimage import map_coordinates


class LinearProfileCalculator(QThread):
    """Background thread for line profile calculation with cancellation support."""

    finished = Signal(object, object)  # (distances, values)

    def __init__(self, img, start_x, start_y, end_x, end_y, thickness=1.0):
        super().__init__()
        self.img = img
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.thickness = thickness
        self._cancel = False

    def cancel(self):
        """Request cancellation of ongoing calculation."""
        self._cancel = True

    def run(self):
        """Calculate profile in background thread."""
        if self._cancel:
            return

        try:
            distances, values = self.extract_line_profile(
                self.img, self.start_x, self.start_y,
                self.end_x, self.end_y, self.thickness
            )

            if not self._cancel:
                self.finished.emit(distances, values)
        except Exception as e:
            print(f"Error calculating line profile: {e}")

    def extract_line_profile(self, img, start_x, start_y, end_x, end_y, thickness=1.0):
        """
        Extract pixel values along line from start to end.

        Phase A: thickness=1.0 (single-pixel line using interpolation)

        Parameters
        ----------
        img : ndarray
            2D image array
        start_x, start_y : float
            Start coordinates in 1-based pixel-centered data coordinates
        end_x, end_y : float
            End coordinates in 1-based pixel-centered data coordinates
        thickness : float
            Line thickness in pixels (Phase A: always 1.0)

        Returns
        -------
        distances : ndarray
            Distances from start point (in pixels)
        values : ndarray
            Interpolated pixel values at each point
        """
        # Calculate line length
        length = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

        # Number of sample points (at least 1 per pixel)
        num_samples = max(int(np.ceil(length)), 2)

        # Generate sample points along line (in data coordinates)
        t = np.linspace(0, 1, num_samples)
        x_samples = start_x + t * (end_x - start_x)
        y_samples = start_y + t * (end_y - start_y)

        # Convert to array indices for map_coordinates
        # Data coordinates: (x, y) where x=1 is first column, y=1 is first row
        # Array indices: [row, col] where row=0 is first row, col=0 is first column
        col_indices = x_samples - 1.0
        row_indices = y_samples - 1.0

        # Extract values using bilinear interpolation
        coords = np.vstack([row_indices, col_indices])
        values = map_coordinates(img, coords, order=1, mode='nearest')

        # Calculate distances from start point
        distances = np.linspace(0, length, num_samples)

        return distances, values


class LinearProfileWidget(QWidget):
    """Widget displaying line profile with statistics."""

    stats_updated = Signal(dict)  # Emits stats when calculation completes

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.calculator = None  # Current calculation thread
        self.last_stats = None  # Statistics for status bar
        self.line_start_x = None  # For horizontal/vertical detection
        self.line_start_y = None
        self.line_end_x = None
        self.line_end_y = None

        # Create matplotlib figure
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(3.5, 2.5))
        canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.setup_axes(self.ax)

        # Initial empty plot
        self.plotted_line = self.ax.plot([], [], '.', alpha=0.6, ms=2, color='#1f77b4')[0]
        self.fitted_line = None  # Will be created when linear fit is added

        figure_layout.addWidget(canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(50)

    def setup_axes(self, ax):
        """Configure axes appearance."""
        ax.set_xlabel('Distance (pixels)', fontsize='small')
        ax.set_ylabel('Pixel Value', fontsize='small')
        ax.tick_params(axis='both', labelsize='small', direction='in')
        ax.set_title('Linear Profile', fontsize='small')

        # Y-axis formatter for large values
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

    def set_line(self, start_x, start_y, end_x, end_y, thickness=1.0):
        """Update line and trigger background calculation."""
        if self.data is None:
            return

        # Store line coordinates for horizontal/vertical detection
        self.line_start_x = start_x
        self.line_start_y = start_y
        self.line_end_x = end_x
        self.line_end_y = end_y

        # Cancel any ongoing calculation
        if self.calculator is not None and self.calculator.isRunning():
            self.calculator.cancel()
            self.calculator.wait(100)  # Wait up to 100ms

        # Show calculating status
        self.ax.set_title('Calculating...', fontsize='small')
        self.fig.canvas.draw_idle()

        # Start new calculation
        self.calculator = LinearProfileCalculator(
            self.data, start_x, start_y, end_x, end_y, thickness
        )
        self.calculator.finished.connect(self._on_calculation_finished)
        self.calculator.start()

    def _on_calculation_finished(self, distances, values):
        """Update plot when background calculation completes."""
        if distances is None or values is None or len(distances) == 0:
            return

        self.plotted_line.set_xdata(distances)
        self.plotted_line.set_ydata(values)

        # Calculate linear fit
        if len(distances) >= 2:
            # Linear regression: y = slope * x + intercept
            coeffs = np.polyfit(distances, values, 1)
            slope, intercept = coeffs[0], coeffs[1]

            # Generate fit line
            fit_y = np.polyval(coeffs, distances)

            # Plot or update orange fit line
            if self.fitted_line is None:
                self.fitted_line, = self.ax.plot(distances, fit_y, color='orange',
                                                  linewidth=1.5, alpha=0.8, label='Linear Fit')
            else:
                self.fitted_line.set_xdata(distances)
                self.fitted_line.set_ydata(fit_y)

            # Check if line is horizontal or vertical for row/column indication
            tolerance = 0.1  # pixel tolerance for detecting h/v lines
            title_parts = []

            if abs(self.line_start_y - self.line_end_y) < tolerance:
                # Horizontal line - show row number
                row_num = int(round(self.line_start_y))
                title_parts.append(f'row:{row_num}')
            elif abs(self.line_start_x - self.line_end_x) < tolerance:
                # Vertical line - show column number
                col_num = int(round(self.line_start_x))
                title_parts.append(f'column:{col_num}')

            # Add fit parameters
            title_parts.append(f'slope={slope:.2f} intercept={intercept:.1f}')

            # Update title with row/column indication (if h/v) and fit parameters
            self.ax.set_title(' | '.join(title_parts), fontsize='small')
        else:
            self.ax.set_title('Linear Profile', fontsize='small')

        # Store statistics for status bar
        self.last_stats = {
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std': float(np.std(values)),
            'min': float(np.amin(values)),
            'max': float(np.amax(values)),
        }

        # Emit signal for status bar update
        self.stats_updated.emit(self.last_stats)

        # Rescale and redraw
        self.ax.relim()
        self.ax.autoscale()
        self.fig.canvas.draw_idle()

    def set_data(self, data):
        """Update data when image changes."""
        self.data = data

    def clear(self):
        """Clear the profile plot."""
        self.plotted_line.set_xdata([])
        self.plotted_line.set_ydata([])
        self.ax.set_title('Linear Profile', fontsize='small')
        self.fig.canvas.draw_idle()
