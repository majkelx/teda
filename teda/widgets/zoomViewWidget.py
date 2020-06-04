from PySide2.QtWidgets import QWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from teda.views.fitsplotzoomed import FitsPlotterZoomed


class ZoomViewWidget(QWidget):

    def __init__(self, fits, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fits = fits
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(20, 20))
        #self.fig.tight_layout()
        # self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

        self.fits_image = FitsPlotterZoomed(figure=self.fig)
        self.canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_axis_off()

        figure_layout.addWidget(self.canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.setMaximumHeight(200)

    def updateFits(self, fits):
        self.fits = fits
        self.fits_image.data = self.fits.data
        # self.fits_image.copy_visualization_parameters(self.fits)
        self.fits_image.plot()
        self.fits_image.disconnectEvents()

    def setXYofZoom(self, fits,x ,y ,zoom=1):
        self.fits_image.moveToXYcordsWithZoom(x,y,zoom*8,fits, idle=False)

