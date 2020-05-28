#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

"""PySide2 port of the widgets/mainwindows/dockwidgets example from Qt v5.x, originating from PyQt"""
import PySide2
from PySide2 import QtWidgets
from PySide2.QtCore import QDate, QFile, Qt, QTextStream, QSize, QSettings
from PySide2.QtGui import (QFont, QIcon, QKeySequence, QTextCharFormat, QPixmap,
                           QTextCursor, QTextTableFormat)
from PySide2.QtPrintSupport import QPrintDialog, QPrinter
from PySide2.QtWidgets import (QAction, QApplication, QLabel, QDialog, QDockWidget, QSlider, QStackedLayout,
                               QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QPushButton,
                               QFileDialog, QListWidget, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem,
                               QComboBox, QMenu)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from fitsplot import (FitsPlotter)
from scalesModel import (ScalesModel)
from coordinates import CoordinatesModel
from fitsplot_fitsfile import FitsPlotterFitsFile
from fitsopen import (FitsOpen)
from painterComponent import PainterComponent
from matplotlib.figure import Figure
from math import *
from radialprofile import RadialProfileWidget
from radialprofileIRAF import IRAFRadialProfileWidget
from fullViewWidget import FullViewWidget
from zoomViewWidget import ZoomViewWidget
from radialprofileIRAF import IRAFRadialProfileWidget
from headerTableWidget import HeaderTableWidget
from info import InfoWidget
from cmaps import ColorMaps
import console


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cmaps = ColorMaps()
        self.combobox = QComboBox()
        self.filename = None
        self.cursor_coords = CoordinatesModel()
        fig = Figure(figsize=(14, 10))
        fig.tight_layout()
        self.scalesModel = ScalesModel()
        self.fits_image = FitsPlotter(figure=fig)
        fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)

        self.fits_image = FitsPlotterFitsFile(figure=fig, cmap=self.cmaps.get_active_color_map())
        self.central_widget = FigureCanvas(fig)
        self.setCentralWidget(self.central_widget)

        self.stretch_dict = {}
        self.interval_dict = {}
        self.current_x_coord = 0
        self.current_y_coord = 0

        self.fullWidgetXcord = 0
        self.fullWidgetYcord = 0
        self.centralWidgetcordX = 0
        self.centralWidgetcordY = 0

        self.painterComponent = PainterComponent(self.fits_image)
        self.painterComponent.startMovingEvents(self.central_widget)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createInfoWindow()
        self.readSlidersValues()
        self.createDockWindows()
        # self.defineButtonsActions()
        self.setWindowTitle("TeDa")

        self.readWindowSettings()

        self.painterComponent.observe(lambda change: self.onCenterCircleChange(change), ['ccenter_x', 'ccenter_y'])
        self.painterComponent.observe(lambda change: self.onCenterCircleRadiusChange(change), ['cradius'])
        self.fits_image.observe(lambda change: self.onMouseMoveOnImage(change), ['mouse_xdata', 'mouse_ydata'])
        self.cmaps.observe(lambda change: self.on_colormap_change(change))
        self.full_view_widget.painterComponent.observe(lambda change: self.onRectangleInWidgetMove(change), ['viewX', 'viewY'])
        self.painterComponent.observe(lambda change: self.movingCentralWidget(change), ['movingViewX', 'movingViewY'])
        self.fits_image.observe(lambda change: self.onMouseZoomOnImage(change), ['viewBounaries_versionno'])

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        self.writeWindowSettings()
        self.writeSlidersValues()
        super().closeEvent(event)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.deleteSelected()
        if e.key() == Qt.Key_R:
            action = self.dockRadialFit.toggleViewAction()
            if not action.isChecked():
                action.trigger()
            if (self.cursor_coords.img_x != 0 and self.cursor_coords.img_x != None) and (self.cursor_coords.img_y != 0 and self.cursor_coords.img_y != None):
                self.painterComponent.add(self.cursor_coords.img_x, self.cursor_coords.img_y, type="circleCenter")
                self.painterComponent.paintAllShapes(self.central_widget.figure.axes[0])

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def open_dialog(self):
        fileName, _ = QFileDialog.getOpenFileName(mainWin, "Open Image", ".", "Fits files (*.fits)")
        # fileName = QFileDialog.getOpenFileName(mainWin, "Open Image", "/home/akond/Pulpit/fits files", "Fits files (*.fits)")[0]
        if fileName:
            self.open_fits(fileName)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Choose a file name", '.', "HTML (*.html *.htm)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Dock Widgets",
                                "Cannot write file %s:\n%s." % (filename, file.errorString()))
            return

        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.textEdit.toHtml()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved '%s'" % filename, 2000)


    def open_fits(self, fileName):
        """Opens specified FITS file and loads it to user interface"""
        self.filename = fileName
        self.fits_image.set_file(self.filename)
        self.cursor_coords.set_wcs_from_fits(self.fits_image.header)  # TODO: one up and extract and set wcs in fits_image before plot
        self.fits_image.set_wcs(self.cursor_coords.wcs)

        self.fits_image.plot()


        self.radial_profile_widget.set_data(self.fits_image.data)
        self.radial_profile_iraf_widget.set_data(self.fits_image.data)
        self.adjustSliders()

        self.headerWidget.setHeader()

    def adjustSliders(self):
        self.getSliders(self.stretchStackedLayout.currentIndex(), self.intervalStackedLayout.currentIndex())
        self.stretch_sliders_widget.setEnabled(True)
        self.interval_sliders_widget.setEnabled(True)
        self.combobox_widget.setEnabled(True)
        self.manual_vmin.setValue(self.scalesModel.interval_manual_vmin * 10)
        self.manual_vmax.setValue(self.scalesModel.interval_manual_vmax)
        self.percentile_percentile.setValue(self.scalesModel.interval_percentile_percentile * 10)
        self.percentile_nsamples.setValue(self.scalesModel.interval_percentile_nsamples)
        self.asymetric_lpercentile.setValue(self.scalesModel.interval_asymetric_lower_percentile * 10)
        self.asymetric_upercentile.setValue(self.scalesModel.interval_asymetric_upper_percentile * 10)
        self.asymetric_nsamples.setValue(self.scalesModel.interval_asymetric_nsamples)
        self.zscale_nsamples.setValue(self.scalesModel.interval_zscale_nsamples)
        self.zscale_contrast.setValue(self.scalesModel.interval_zscale_contrast * 100)
        self.zscale_mreject.setValue(self.scalesModel.interval_zscale_maxreject * 10)
        self.zscale_minpixels.setValue(self.scalesModel.interval_zscale_minpixels)
        self.zscale_krej.setValue(self.scalesModel.interval_zscale_krej * 10)
        self.zscale_miterations.setValue(self.scalesModel.interval_zscale_maxiterations)
        self.asinh_a.setValue(self.scalesModel.stretch_asinh_a * 10)
        self.contrast_contrast.setValue(self.scalesModel.stretch_contrastbias_contrast * 10)
        self.contrast_bias.setValue(self.scalesModel.stretch_contrastbias_bias * 10)
        self.linear_slope.setValue(self.scalesModel.stretch_linear_slope * 10)
        self.linear_intercept.setValue(self.scalesModel.stretch_linear_intercept * 10)
        self.log_a.setValue(self.scalesModel.stretch_log_a * 10)
        self.powerdist_a.setValue(self.scalesModel.stretch_powerdist_a * 10)
        self.power_a.setValue(self.scalesModel.stretch_power_a * 10)
        self.sinh_a.setValue(self.scalesModel.stretch_sinh_a * 100)

    def undo(self):
        document = self.textEdit.document()
        document.undo()

    def insertCustomer(self, customer):
        if not customer:
            return

    def addParagraph(self, paragraph):
        if not paragraph:
            return

    def about(self):
        QMessageBox.about(self, "TeDa FITS Viewer",
                          "Authors: <ul> "
                          "<li>Michał Brodniak</li>"
                          "<li>Konrad Górski</li>"
                          "<li>Mikołaj Kałuszyński</li>"
                          "<li>Edward Lis</li>"
                          "<li>Grzegorz Mroczkowski</li>"
                          "</ul>"
                          "Created by <a href='https://akond.com'>Akond Lab</a> for The Araucaria Project")

    def on_console_show(self):
        console.show(ax=self.fits_image.ax, window=self, data=self.fits_image.data, header=self.fits_image.header, wcs=self.cursor_coords.wcs)

    def createActions(self):
        # ico1 = QPixmap('/Users/mka/projects/astro/teda/icons/png.png')
        # self.openAct = QAction(ico1, "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open)
        self.openAct = QAction(QIcon.fromTheme('document-open'), "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open_dialog)
        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application", triggered=self.close)
        self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, statusTip="Show the Qt library's About box", triggered=QApplication.instance().aboutQt)

        self.qtConsoleAct = QAction('Python Console', self,
                                    statusTip="Open IPython console window", triggered=self.on_console_show)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.viewMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.qtConsoleAct)
        self.viewMenu.addSeparator()

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File Toolbar")
        self.fileToolBar.addAction(self.openAct)

        self.hduToolBar = self.addToolBar("HDU Toolbar")
        self.hduToolBar.addAction("prevHDU").triggered.connect(self.prevHDU)
        self.hduToolBar.addAction("nextHDU").triggered.connect(self.nextHDU)

        self.infoToolBar = self.addToolBar("Info Toolbar")
        self.mouse_x_label = QLabel('100.1')
        self.mouse_y_label = QLabel('100.145')
        self.infoToolBar.addWidget(QLabel('image x:'))
        self.infoToolBar.addWidget(self.mouse_x_label)
        self.infoToolBar.addWidget(QLabel('y:'))
        self.infoToolBar.addWidget(self.mouse_y_label)

        self.zoomToolBar = self.addToolBar("Zoom Toolbar")
        self.zoomToolBar.addAction("x4").triggered.connect(self.setZoomButton4)
        self.zoomToolBar.addAction("x2").triggered.connect(self.setZoomButton2)
        self.zoomToolBar.addAction("Home").triggered.connect(self.setZoomButtonHome)
        self.zoomToolBar.addAction("1/2").triggered.connect(self.setZoomButton05)
        self.zoomToolBar.addAction("1/4").triggered.connect(self.setZoomButton025)

        self.mouseActionToolBar = self.addToolBar("Mouse Task Toolbar")

        self.BtnCircle = QPushButton("Add Region")
        self.BtnCircle.setCheckable(True)
        self.BtnCircle.clicked.connect(self.changeAddCircleStatus)
        self.mouseActionToolBar.addWidget(self.BtnCircle)

        self.BtnCenterCircle = QPushButton("Radial profile")
        self.BtnCenterCircle.setCheckable(True)
        self.BtnCenterCircle.clicked.connect(self.changeAddCenterCircleStatus)
        self.mouseActionToolBar.addWidget(self.BtnCenterCircle)

        self.BtnDelete = QPushButton("Delete selected")
        self.BtnDelete.clicked.connect(self.deleteSelected)
        self.mouseActionToolBar.addWidget(self.BtnDelete)

        self.viewMenu.addAction(self.fileToolBar.toggleViewAction())
        self.viewMenu.addAction(self.hduToolBar.toggleViewAction())
        self.viewMenu.addAction(self.infoToolBar.toggleViewAction())
        self.viewMenu.addAction(self.mouseActionToolBar.toggleViewAction())
        self.viewMenu.addSeparator()

    def nextHDU(self):
        self.fits_image.changeHDU(True, 1)
        self.headerWidget.setHeader()

    def prevHDU(self):
        self.fits_image.changeHDU(True, -1)
        self.headerWidget.setHeader()

    def setZoomButton4(self):
        self.setZoomButton(4,False)
    def setZoomButton2(self):
        self.setZoomButton(2,False)
    def setZoomButtonHome(self):
        self.setZoomButton(1,True)
    def setZoomButton05(self):
        self.setZoomButton(0.5,False)
    def setZoomButton025(self):
        self.setZoomButton(0.25,False)
    def setZoomButton(self,zoom:float,reset:bool):
        if self.fits_image.ax!=None:
            self.fits_image.setZoom(zoom, reset)
            self.full_view_widget.updateMiniatureShape(self.fits_image.viewX, self.fits_image.viewY, self.fits_image.viewW, self.fits_image.viewH)

    def changeAddCircleStatus(self):
        if self.BtnCircle.isChecked():
            self.toogleOffRegionButtons()
            self.BtnCircle.toggle()
            self.painterComponent.startPainting(self.central_widget, "circle")
        else:
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.startMovingEvents(self.central_widget)

    def changeAddCenterCircleStatus(self):
        if self.BtnCenterCircle.isChecked():
            self.toogleOffRegionButtons()
            self.BtnCenterCircle.toggle()
            self.painterComponent.startPainting(self.central_widget,"circleCenter")
        else:
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.startMovingEvents(self.central_widget)

    def deleteSelected(self):
        self.painterComponent.deleteSelectedShapes(self.central_widget.figure.axes[0])

    def toogleOffRegionButtons(self):
        if self.BtnCircle.isChecked():
            self.BtnCircle.toggle()
        if self.BtnCenterCircle.isChecked():
            self.BtnCenterCircle.toggle()
        self.painterComponent.stopPainting(self.central_widget)


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createDockWindows(self):
        dock = QDockWidget("Scale", self)
        dock.setObjectName("SCALE")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)

        #comboboxes
        widget = QWidgetCustom()
        layout = QVBoxLayout()
        self.combobox_widget = QWidget()
        self.combobox_widget.setEnabled(False)
        self.combobox_layout = self.createComboboxes()
        self.combobox_widget.setLayout(self.combobox_layout)
        # self.combobox_widget.setMaximumHeight(40)
        layout.addWidget(self.combobox_widget)

        #Stretch
        self.stretch_sliders_widget = QWidget()
        self.stretch_sliders_layout = self.createStretchStackedLayout()
        self.stretch_sliders_widget.setEnabled(False)
        self.stretch_sliders_widget.setLayout(self.stretch_sliders_layout)
        # self.stretch_sliders_widget.setMaximumHeight(50)
        layout.addWidget(self.stretch_sliders_widget)

        #Interval
        self.interval_sliders_widget = QWidget()
        self.interval_sliders_layout = self.createIntervalStackedLayout()
        self.interval_sliders_widget.setEnabled(False)
        self.interval_sliders_widget.setLayout(self.interval_sliders_layout)
        # self.interval_sliders_widget.setMaximumHeight(125)
        layout.addWidget(self.interval_sliders_widget)
        widget.setLayout(layout)
        widget.setMaximumHeight(350)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        #radial profiles
        dock = QDockWidget("Radial Profile Fit", self)
        dock.setObjectName("RADIAL_PROFILE_IRAF")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.radial_profile_iraf_widget = IRAFRadialProfileWidget(self.fits_image.data)
        dock.setWidget(self.radial_profile_iraf_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.dockRadialFit = dock

        dock = QDockWidget("Radial Profile Curve", self)
        dock.setObjectName("RADIAL_PROFILE")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.radial_profile_widget = RadialProfileWidget(self.fits_image.data)
        dock.setWidget(self.radial_profile_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        #info panel
        dock = QDockWidget("info", self)
        dock.setObjectName("INFO_PANEL")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.info_widget = InfoWidget(self)
        dock.setWidget(self.info_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        # full
        dock = QDockWidget("Full view", self)
        dock.setObjectName("FULL_VIEW")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.full_view_widget = FullViewWidget(self.fits_image)
        dock.setWidget(self.full_view_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        # zoom
        dock = QDockWidget("Zoom view", self)
        dock.setObjectName("ZOOM_VIEW")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.zoom_view_widget = ZoomViewWidget(self.fits_image)
        dock.setWidget(self.zoom_view_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        self.viewMenu.addSeparator()

    def createStretchStackedLayout(self):
        self.stretchStackedLayout = QStackedLayout()
        asinh = self.createAsinhParamsSliders()
        contrastbias = self.createContrastbiasParamsSliders()
        histogram = QLabel("")
        linear = self.createLinearSliders()
        log = self.createLogSliders()
        powerdist = self.createPowerdistSliders()
        power = self.createPowerSliders()
        sinh = self.createSinhSliders()
        sqrt = QLabel("")
        square = QLabel("")
        self.stretchStackedLayout.addWidget(powerdist)
        self.stretchStackedLayout.addWidget(asinh)
        self.stretchStackedLayout.addWidget(contrastbias)
        self.stretchStackedLayout.addWidget(histogram)
        self.stretchStackedLayout.addWidget(linear)
        self.stretchStackedLayout.addWidget(log)
        self.stretchStackedLayout.addWidget(power)
        self.stretchStackedLayout.addWidget(sinh)
        self.stretchStackedLayout.addWidget(sqrt)
        self.stretchStackedLayout.addWidget(square)

        return self.stretchStackedLayout

    def createIntervalStackedLayout(self):
        self.intervalStackedLayout = QStackedLayout()

        manual = self.createManualParamsSliders()
        percentile = self.createPercentileParamsSliders()
        asymetric = self.createAsymetricParamsSliders()
        zscale = self.createZscaleParamsSliders()
        self.intervalStackedLayout.addWidget(zscale)
        self.intervalStackedLayout.addWidget(QLabel(""))
        self.intervalStackedLayout.addWidget(manual)
        self.intervalStackedLayout.addWidget(percentile)
        self.intervalStackedLayout.addWidget(asymetric)

        return self.intervalStackedLayout

    def createManualParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        self.manual_vmin = QSlider(Qt.Horizontal)
        self.manual_vmin.setMinimum(0)
        self.manual_vmin.setMaximum(10000)

        self.manual_vmax = QSlider(Qt.Horizontal)
        self.manual_vmax.setMinimum(10000)
        self.manual_vmax.setMaximum(50000)

        self.manual_vmin.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_manual_vmin',
                                                                                       self.manual_vmin.value() / 10.0))
        self.manual_vmax.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_manual_vmax',
                                                                                       self.manual_vmax.value()))

        layout.addWidget(QLabel('vmin'), 0, 0)
        layout.addWidget(self.manual_vmin, 0, 1)
        layout.addWidget(QLabel('vmax'), 1, 0)
        layout.addWidget(self.manual_vmax, 1, 1)
        widget.setLayout(layout)

        return widget

    def createPercentileParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        self.percentile_percentile = QSlider(Qt.Horizontal)
        self.percentile_percentile.setMinimum(1)
        self.percentile_percentile.setMaximum(10)

        self.percentile_nsamples = QSlider(Qt.Horizontal)
        self.percentile_nsamples.setMinimum(500)
        self.percentile_nsamples.setMaximum(1500)

        self.percentile_percentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_percentile_percentile',
                                                                                                 self.percentile_percentile.value() / 10.0))
        self.percentile_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_percentile_nsamples',
                                                                                               self.percentile_nsamples.value()))

        layout.addWidget(QLabel('percentile'), 0, 0)
        layout.addWidget(self.percentile_percentile, 0, 1)
        layout.addWidget(QLabel('samples'), 1, 0)
        layout.addWidget(self.percentile_nsamples, 1, 1)
        widget.setLayout(layout)

        return widget

    def createAsymetricParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.asymetric_lpercentile = QSlider(Qt.Horizontal)
        self.asymetric_lpercentile.setMinimum(1)
        self.asymetric_lpercentile.setMaximum(10)

        self.asymetric_upercentile = QSlider(Qt.Horizontal)
        self.asymetric_upercentile.setMinimum(2)
        self.asymetric_upercentile.setMaximum(20)

        self.asymetric_nsamples = QSlider(Qt.Horizontal)
        self.asymetric_nsamples.setMinimum(500)
        self.asymetric_nsamples.setMaximum(1500)

        self.asymetric_lpercentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_lower_percentile',
                                                                                                 self.asymetric_lpercentile.value() / 10.0))
        self.asymetric_upercentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_upper_percentile',
                                                                                                 self.asymetric_upercentile.value() / 10.0))
        self.asymetric_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_nsamples',
                                                                                              self.asymetric_nsamples.value()))

        layout.addWidget(QLabel("l_percentile"), 0, 0)
        layout.addWidget(self.asymetric_lpercentile, 0, 1)
        layout.addWidget(QLabel("u_percentile"), 1, 0)
        layout.addWidget(self.asymetric_upercentile, 1, 1)
        layout.addWidget(QLabel("samples"), 2, 0)
        layout.addWidget(self.asymetric_nsamples, 2, 1)
        widget.setLayout(layout)

        return widget

    def createZscaleParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.zscale_nsamples = QSlider(Qt.Horizontal)
        self.zscale_nsamples.setMinimum(500)
        self.zscale_nsamples.setMaximum(1500)

        self.zscale_contrast = QSlider(Qt.Horizontal)
        self.zscale_contrast.setMinimum(10)
        self.zscale_contrast.setMaximum(50)

        self.zscale_mreject = QSlider(Qt.Horizontal)
        self.zscale_mreject.setMinimum(1)
        self.zscale_mreject.setMaximum(20)

        self.zscale_minpixels = QSlider(Qt.Horizontal)
        self.zscale_minpixels.setMinimum(1)
        self.zscale_minpixels.setMaximum(10)

        self.zscale_krej = QSlider(Qt.Horizontal)
        self.zscale_krej.setMinimum(10)
        self.zscale_krej.setMaximum(50)

        self.zscale_miterations = QSlider(Qt.Horizontal)
        self.zscale_miterations.setMinimum(1)
        self.zscale_miterations.setMaximum(10)

        self.zscale_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_nsamples',
                                                                                           self.zscale_nsamples.value()))
        self.zscale_contrast.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_contrast',
                                                                                           self.zscale_contrast.value() / 100.0))
        self.zscale_mreject.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_maxreject',
                                                                                          self.zscale_mreject.value() / 10))
        self.zscale_minpixels.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_minpixels',
                                                                                            self.zscale_minpixels.value()))
        self.zscale_krej.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_krej',
                                                                                       self.zscale_krej.value() / 10))
        self.zscale_miterations.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_maxiterations',
                                                                                              self.zscale_miterations.value()))

        layout.addWidget(QLabel("samples"), 0, 0)
        layout.addWidget(self.zscale_nsamples, 0, 1)
        layout.addWidget(QLabel("contrast"), 1, 0)
        layout.addWidget(self.zscale_contrast, 1, 1)
        layout.addWidget(QLabel("max reject"), 2, 0)
        layout.addWidget(self.zscale_mreject, 2, 1)
        layout.addWidget(QLabel("pixels"), 3, 0)
        layout.addWidget(self.zscale_minpixels, 3, 1)
        layout.addWidget(QLabel("krej"), 4, 0)
        layout.addWidget(self.zscale_krej, 4, 1)
        layout.addWidget(QLabel("m_iterations"), 5, 0)
        layout.addWidget(self.zscale_miterations, 5, 1)

        widget.setLayout(layout)

        return widget

    def createComboboxes(self):
        layout = QHBoxLayout()

        self.stretch_combobox = QComboBox()
        self.stretch_combobox.setFocusPolicy(Qt.NoFocus)
        self.stretch_combobox.addItems(['powerdist', 'asinh', 'contrastbias', 'histogram', 'linear',
                                        'log', 'power', 'sinh', 'sqrt', 'square'])


        self.interval_combobox = QComboBox()
        self.interval_combobox.setFocusPolicy(Qt.NoFocus)
        self.interval_combobox.addItems(['zscale','minmax', 'manual', 'percentile', 'asymetric'])

        self.color_combobox = QComboBox()
        self.color_combobox.setFocusPolicy(Qt.NoFocus)
        self.color_combobox.addItems(self.cmaps.colormaps.keys())

        layout.addWidget(self.stretch_combobox)
        layout.addWidget(self.interval_combobox)
        layout.addWidget(self.color_combobox)

        self.stretch_combobox.activated.connect(lambda activated: self.getSliders(self.stretch_combobox.currentIndex(), self.interval_combobox.currentIndex()))
        self.interval_combobox.activated.connect(lambda activated: self.getSliders(self.stretch_combobox.currentIndex(), self.interval_combobox.currentIndex()))
        self.color_combobox.currentTextChanged.connect(lambda activated: self.changeColor(self.color_combobox.currentText()))
        return layout

    def getSliders(self, stretch_index, interval_index):
        self.stretchStackedLayout.setCurrentIndex(stretch_index)
        self.intervalStackedLayout.setCurrentIndex(interval_index)
        self.fitsNormalization(self.stretch_combobox.currentText(), self.interval_combobox.currentText())

    def fitsNormalization(self, stretch, interval):
        self.fits_image.set_normalization(stretch=stretch,
                                          interval=interval,
                                          stretchkwargs=self.scalesModel.dictionary[stretch],
                                          intervalkwargs=self.scalesModel.dictionary[interval])

        self.fits_image.invalidate()
        self.updateFitsInWidgets()

    def changeSlidersParams(self, param, value):
        setattr(self.scalesModel, param, value)
        current_stretch = self.stretch_combobox.currentText()
        current_interval = self.interval_combobox.currentText()

        self.fitsNormalization(current_stretch, current_interval)

    def createAsinhParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.asinh_a = QSlider(Qt.Horizontal)
        self.asinh_a.setMinimum(1)
        self.asinh_a.setMaximum(10)

        self.asinh_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_asinh_a', self.asinh_a.value() / 10.0))
        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.asinh_a , 0, 1)
        widget.setLayout(layout)

        return widget

    def createContrastbiasParamsSliders(self):

        widget = QWidget()
        layout = QGridLayout()

        self.contrast_contrast = QSlider(Qt.Horizontal)
        self.contrast_contrast.setMinimum(1)
        self.contrast_contrast.setMaximum(30)

        self.contrast_bias = QSlider(Qt.Horizontal)
        self.contrast_bias.setMinimum(1)
        self.contrast_bias.setMaximum(20)

        self.contrast_contrast.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_contrastbias_contrast',
                                                                                             self.contrast_contrast.value() / 10.0))
        self.contrast_bias.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_contrastbias_bias',
                                                                                         self.contrast_bias.value() / 10.0))
        layout.addWidget(QLabel('contrast'), 0, 0)
        layout.addWidget(self.contrast_contrast, 0, 1)
        layout.addWidget(QLabel('bias'), 1, 0)
        layout.addWidget(self.contrast_bias, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLinearSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.linear_slope = QSlider(Qt.Horizontal)
        self.linear_slope.setTickPosition(QSlider.TicksAbove)
        self.linear_slope.setMinimum(1) # 0.1
        self.linear_slope.setMaximum(30) # 3.0

        self.linear_intercept = QSlider(Qt.Horizontal)
        self.linear_intercept.setMinimum(-10) # -1.0
        self.linear_intercept.setMaximum(10) # 1.0

        #connects
        self.linear_slope.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_linear_slope',
                                                                                        self.linear_slope.value() / 10.0))
        self.linear_intercept.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_linear_intercept',
                                                                                            self.linear_intercept.value() / 10.0))

        layout.addWidget(QLabel("slope"), 0, 0)
        layout.addWidget(self.linear_slope, 0, 1)
        layout.addWidget(QLabel("intercept"), 1, 0)
        layout.addWidget(self.linear_intercept, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLogSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.log_a = QSlider(Qt.Horizontal)
        self.log_a.setMinimum(5000)
        self.log_a.setMaximum(15000)

        self.log_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_log_a',
                                                                                 self.log_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.log_a, 0, 1)
        widget.setLayout(layout)

        return widget

    def createPowerdistSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.powerdist_a = QSlider(Qt.Horizontal)
        self.powerdist_a.setMinimum(5000)
        self.powerdist_a.setMaximum(15000)

        self.powerdist_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_powerdist_a',
                                                                                       self.powerdist_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.powerdist_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def createPowerSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.power_a = QSlider(Qt.Horizontal)
        self.power_a.setMinimum(1)
        self.power_a.setMaximum(20)

        self.power_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_power_a',
                                                                                   self.power_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.power_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def createSinhSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.sinh_a = QSlider(Qt.Horizontal)
        self.sinh_a.setMinimum(10)
        self.sinh_a.setMaximum(100)

        self.sinh_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_sinh_a',
                                                                                  self.sinh_a.value() / 100.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.sinh_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def changeColor(self, color):
        self.cmaps.set_active_color_map(color)

    def on_colormap_change(self, change):
        self.fits_image.cmap = self.cmaps.get_active_color_map()
        self.fits_image.plot()
        self.updateFitsInWidgets()

    def createInfoWindow(self):
        dock = QDockWidget("FITS header", self)
        dock.setObjectName("FTIS_DATA")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.headerWidget = HeaderTableWidget(self)
        self.headerWidget.setColumnCount(2)
        self.headerWidget.setHorizontalHeaderItem(0, QTableWidgetItem("KEY"))
        self.headerWidget.setHorizontalHeaderItem(1, QTableWidgetItem("VALUE"))
        self.headerWidget.horizontalHeader().setStretchLastSection(1)
        self.headerWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        dock.setWidget(self.headerWidget)




    def onCenterCircleChange(self, change):
        self.radial_profile_widget.set_centroid(self.painterComponent.ccenter_x, self.painterComponent.ccenter_y)
        self.radial_profile_iraf_widget.set_centroid(self.painterComponent.ccenter_x, self.painterComponent.ccenter_y)

    def onCenterCircleRadiusChange(self, change):
        self.radial_profile_widget.set_radius(self.painterComponent.cradius)
        self.radial_profile_iraf_widget.set_radius(self.painterComponent.cradius)

    def onRectangleInWidgetMove(self, change):
        changed = False
        if change.new is not None:
            changed = True
        if change.name == 'viewX':
            self.fullWidgetXcord = change.new
        elif change.name == 'viewY':
            self.fullWidgetYcord = change.new
        if changed:
            self.fits_image.moveToXYcords(self.fullWidgetXcord,self.fullWidgetYcord)

    def movingCentralWidget(self,change):
        changed = False
        if change.new is not None:
            changed = True
        if change.name == 'movingViewX':
            self.centralWidgetcordX = change.new
        elif change.name == 'movingViewY':
            self.centralWidgetcordY = change.new
        if changed:
            self.full_view_widget.updateMiniatureShapeXYonly(self.centralWidgetcordX, self.centralWidgetcordY)

    def onMouseMoveOnImage(self, change):
        display = ''
        val = 0
        if change.new is not None:
            display = f'{change.new:f}'
            val = change.new
        if change.name == 'mouse_xdata':
            self.mouse_x_label.setText(display)
            self.current_x_coord = val
            self.cursor_coords.set_img_x(change.new)
        elif change.name == 'mouse_ydata':
            self.mouse_y_label.setText(display)
            self.current_y_coord = val
            self.cursor_coords.set_img_y(change.new)
        if display != '':
            self.zoom_view_widget.setXYofZoom(self.fits_image, self.current_x_coord, self.current_y_coord, self.fits_image.zoom)

    def onMouseZoomOnImage(self, change):
        changed = False
        if change.new is not None:
            changed = True
        if changed:
            self.full_view_widget.updateMiniatureShape(self.fits_image.viewX,self.fits_image.viewY,self.fits_image.viewW,self.fits_image.viewH)

    def readWindowSettings(self):
        settings = QSettings()
        settings.beginGroup("MainWindow")
        size, pos = settings.value("size"), settings.value("pos")
        settings.endGroup()
        if size is not None and pos is not None:
            print('settings: resize to {} and move to {}', size, pos)
            self.move(pos)
            # self.resize(size)
            print('Size reported ', self.size())
            print('Size set ', size)
            self.resize(size)
            print('Size reported ', self.size())
        else:
            self.resize(800, 600)

        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
            self.restoreState(settings.value("windowState"))

        self.headerWidget.readSettings(settings)

    def writeWindowSettings(self):
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.endGroup()

        settings.setValue('geometry',self.saveGeometry())
        settings.setValue('windowState',self.saveState())

        self.headerWidget.writeSettings(settings)

    def updateFitsInWidgets(self):
        # print("updateFitsInWidgets")
        self.full_view_widget.updateFits(self.fits_image)
        self.zoom_view_widget.updateFits(self.fits_image)

    def writeSlidersValues(self):
        settings = QSettings()
        settings.beginGroup("Sliders")
        settings.setValue("asinh/a", self.scalesModel.stretch_asinh_a)
        settings.setValue("contrast/contrast", self.scalesModel.stretch_contrastbias_contrast)
        settings.setValue("contrast/bias", self.scalesModel.stretch_contrastbias_bias)
        settings.setValue("linear/slope", self.scalesModel.stretch_linear_slope)
        settings.setValue("linear/intercept", self.scalesModel.stretch_linear_intercept)
        settings.setValue("log/a", self.scalesModel.stretch_log_a)
        settings.setValue("powerdist/a", self.scalesModel.stretch_powerdist_a)
        settings.setValue("power/a", self.scalesModel.stretch_power_a)
        settings.setValue("sinh/a", self.scalesModel.stretch_sinh_a)

        settings.setValue("manual/vmin", self.scalesModel.interval_manual_vmin)
        settings.setValue("manual/vmax", self.scalesModel.interval_manual_vmax)
        settings.setValue("percentile/percentile", self.scalesModel.interval_percentile_percentile)
        settings.setValue("percentile/nsamples", self.scalesModel.interval_percentile_nsamples)
        settings.setValue("asymetric/lpercentile", self.scalesModel.interval_asymetric_lower_percentile)
        settings.setValue("asymetric/upercentile", self.scalesModel.interval_asymetric_upper_percentile)
        settings.setValue("asymetric/nsamples", self.scalesModel.interval_asymetric_nsamples)
        settings.setValue("zscale/contrast", self.scalesModel.interval_zscale_contrast)
        settings.setValue("zscale/nsamples", self.scalesModel.interval_zscale_nsamples)
        settings.setValue("zscale/maxreject", self.scalesModel.interval_zscale_maxreject)
        settings.setValue("zscale/minpixels", self.scalesModel.interval_zscale_minpixels)
        settings.setValue("zscale/krej", self.scalesModel.interval_zscale_krej)
        settings.setValue("zscale/maxiterations", self.scalesModel.interval_zscale_maxiterations)

        settings.endGroup()

    def readSlidersValues(self):
        settings = QSettings()
        settings.beginGroup("Sliders")

        asinh_a_value = settings.value("asinh/a")
        contrast_contrast_value = settings.value("contrast/contrast")
        contrast_bias_value = settings.value("contrast/bias")
        linear_slope_value = settings.value("linear/slope")
        linear_intercept_value = settings.value("linear/intercept")
        log_a_value = settings.value("log/a")
        powerdist_a_value = settings.value("powerdist/a")
        power_a_value = settings.value("power/a")
        sinh_a_value = settings.value("sinh/a")

        manual_vmin_value = settings.value("manual/vmin")
        manual_vmax_value = settings.value("manual/vmax")
        percentile_percentile_value = settings.value("percentile/percentile")
        percentile_nsamples_value = settings.value("percentile/nsamples")
        asymetric_lpercentile_value = settings.value("asymetric/lpercentile")
        asymetric_upercentile_value = settings.value("asymetric/upercentile")
        asymetric_nsamples_value = settings.value("asymetric/nsamples")
        zscale_contrast_value = settings.value("zscale/contrast")
        zscale_nsamples_value = settings.value("zscale/nsamples")
        zscale_maxreject_value = settings.value("zscale/maxreject")
        zscale_minpixels_value = settings.value("zscale/minpixels")
        zscale_krej_value = settings.value("zscale/krej")
        zscale_maxiterations_value = settings.value("zscale/maxiterations")
        settings.endGroup()

        if asinh_a_value:
            self.scalesModel.stretch_asinh_a = float(asinh_a_value)
        if contrast_contrast_value:
            self.scalesModel.stretch_contrastbias_contrast = float(contrast_contrast_value)
        if contrast_bias_value:
            self.scalesModel.stretch_contrastbias_bias = float(contrast_bias_value)
        if linear_slope_value:
            self.scalesModel.stretch_linear_slope = float(linear_slope_value)
        if linear_intercept_value:
            self.scalesModel.stretch_linear_intercept = float(linear_intercept_value)
        if log_a_value:
            self.scalesModel.stretch_log_a = float(log_a_value)
        if powerdist_a_value:
            self.scalesModel.stretch_powerdist_a = float(powerdist_a_value)
        if power_a_value:
            self.scalesModel.stretch_power_a = float(power_a_value)
        if sinh_a_value:
            self.scalesModel.stretch_sinh_a = float(sinh_a_value)

        if manual_vmin_value:
            self.scalesModel.interval_manual_vmin = float(manual_vmin_value)
        if manual_vmax_value:
            self.scalesModel.interval_manual_vmax = int(manual_vmax_value)
        if percentile_percentile_value:
            self.scalesModel.interval_percentile_percentile = float(percentile_percentile_value)
        if percentile_nsamples_value:
            self.scalesModel.interval_percentile_nsamples = int(percentile_nsamples_value)
        if asymetric_lpercentile_value:
            self.scalesModel.interval_asymetric_lower_percentile = float(asymetric_lpercentile_value)
        if asymetric_upercentile_value:
            self.scalesModel.interval_asymetric_upper_percentile = float(asymetric_upercentile_value)
        if asymetric_nsamples_value:
            self.scalesModel.interval_asymetric_nsamples = int(asymetric_nsamples_value)
        if zscale_nsamples_value:
            self.scalesModel.interval_zscale_nsamples = int(zscale_nsamples_value)
        if zscale_contrast_value:
            self.scalesModel.interval_zscale_contrast = float(zscale_contrast_value)
        if zscale_maxreject_value:
            self.scalesModel.interval_zscale_maxreject = float(zscale_maxreject_value)
        if zscale_minpixels_value:
            self.scalesModel.interval_zscale_minpixels = int(zscale_minpixels_value)
        if zscale_krej_value:
            self.scalesModel.interval_zscale_krej = float(zscale_krej_value)
        if zscale_maxiterations_value:
            self.scalesModel.interval_zscale_maxiterations = int(zscale_maxiterations_value)


class QWidgetCustom(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
    def leaveEvent(self, e):
        self.clearFocus()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    QApplication.setOrganizationName('Akond Lab')
    QApplication.setOrganizationDomain('akond.com')
    QApplication.setApplicationName('TeDa FITS Viewer')
    mainWin = MainWindow()
    # mainWin.resize(800, 600)   # now in config, see: MainWindow.readWindowSettings
    mainWin.show()

    sys.exit(app.exec_())
