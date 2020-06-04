from PySide2.QtWidgets import QWidget, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from teda.views.fitsplotcontrolled import (FitsPlotterControlled)
from teda.painterComponent import PainterComponent


class FullViewWidget(QWidget):

    def __init__(self, fits, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fits = fits
        figure_layout = QHBoxLayout()
        self.fig = Figure(figsize=(6, 6))
        #self.fig.tight_layout()
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

        self.fits_image = FitsPlotterControlled(figure=self.fig)
        self.canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_axis_off()

        figure_layout.addWidget(self.canvas)
        self.setLayout(figure_layout)
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.setMaximumHeight(200)

        self.painterComponent = PainterComponent(self.fits_image)
        self.painterComponent.setCanvas(self.canvas)
        self.painterComponent.paintAllShapes(self.ax)
        self.painterComponent.makeAllShapesDraggable(self.ax)

    def updateFits(self, fits):
        self.fits = fits
        self.fits_image.data = self.fits.data
        # self.fits_image.copy_visualization_parameters(self.fits)
        self.fits_image.plot()
        self.fits_image.disconnectEvents()

        # self.fits_image.plot_fits_data(self.fits.data,self.fits_image.figure.axes[0],1.0, self.fits.get_normalization(),self.fits.cmap)
        # #self.fits_image.figure.axes[0].images = self.fits.figure.axes[0].images
        # self.fig.canvas.draw_idle()

    def updateMiniatureShape(self,x,y,size,size2):
        if self.painterComponent.rectangleMiniature.__len__()==0:
            self.painterComponent.add(x, y, size=size, type="rectangleMiniature", size2=size2)
            self.painterComponent.paintAllShapes(self.ax)
        else:
            self.painterComponent.rectangleMiniature[0].repaintShape(self.ax, x, y, size, self.painterComponent.rectangleMiniature[0].color, size2)
            self.painterComponent.tempCanvas.draw_idle()
        #self.painterComponent.paintAllShapes(self.ax)
        #self.painterComponent.makeAllShapesDraggable(self.ax)

    def updateMiniatureShapeXYonly(self,x,y):
        if self.painterComponent.rectangleMiniature.__len__() == 0:
            self.painterComponent.add(x, y, size=self.ax.viewLim.width, type="rectangleMiniature", size2=self.ax.viewLim.height)
            self.painterComponent.paintAllShapes(self.ax)
        else:
            self.painterComponent.rectangleMiniature[0].repaintShapeXY(self.ax, x, y)
            self.painterComponent.tempCanvas.draw_idle()
        #self.painterComponent.paintAllShapes(self.ax)
        #self.painterComponent.makeAllShapesDraggable(self.ax)
