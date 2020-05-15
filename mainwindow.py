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
from fitsopen import (FitsOpen)
from painterComponent import PainterComponent
from matplotlib.figure import Figure
from math import *
from radialprofile import RadialProfileWidget
from radialprofileIRAF import  IRAFRadialProfileWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.combobox = QComboBox()
        self.filename = None
        fig = Figure(figsize=(14, 10))
        fig.tight_layout()

        self.fits_image = FitsPlotter(figure=fig)
        self.central_widget = FigureCanvas(fig)
        self.setCentralWidget(self.central_widget)

        self.stretch_dict = {}
        self.interval_dict = {}

        self.painterComponent = PainterComponent()
        self.painterComponent.startMovingEvents(self.central_widget)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createInfoWindow()
        self.createDockWindows()
        # self.defineButtonsActions()
        self.setWindowTitle("TeDa")

        self.readWindowSettings()

        self.painterComponent.observe(lambda change: self.onCenterCircleChange(change), ['ccenter_x', 'ccenter_y'])
        self.painterComponent.observe(lambda change: self.onCenterCircleRadiusChange(change), ['cradius'])
        self.fits_image.observe(lambda change: self.onMouseMoveOnImage(change), ['mouse_xdata', 'mouse_ydata'])

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent):
        self.writeWindowSettings()
        super().closeEvent(event)

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(mainWin, "Open Image", ".", "Fits files (*.fits)")
        # fileName = QFileDialog.getOpenFileName(mainWin, "Open Image", "/home/akond/Pulpit/fits files", "Fits files (*.fits)")[0]
        if not fileName:
            return
        self.filename = fileName
        self.fits_image.set_file(self.filename)
        self.fits_image.plot_fits_file()
        self.fits_image.invalidate()

        self.radial_profile_widget.set_data(self.fits_image.data)
        self.radial_profile_iraf_widget.set_data(self.fits_image.data)

        # self.fits_plot = FitsOpen(fileName)
        # self.fits_plot.plot_fits_file()
        # self.central_widget.figure = self.fits_plot.figure
        # self.central_widget = FigureCanvas(self.fits_plot.figure)
        # self.toolbar = NavigationToolbar(self.central_widget, self)
        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        # layout.addWidget(self.central_widget)

        # Create a placeholder widget to hold our toolbar and canvas.
        # widget = QtWidgets.QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)
        #
        self.headerWidget.setHeader()

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
        QMessageBox.about(self, "About Dock Widgets",
                          "The <b>Dock Widgets</b> example demonstrates how to use "
                          "Qt's dock widgets. You can enter your own text, click a "
                          "customer to add a customer name and address, and click "
                          "standard paragraphs to add them.")

    def createActions(self):
        # ico1 = QPixmap('/Users/mka/projects/astro/teda/icons/png.png')
        # self.openAct = QAction(ico1, "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open)
        self.openAct = QAction(QIcon.fromTheme('document-open'), "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open)
        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application", triggered=self.close)
        self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, statusTip="Show the Qt library's About box", triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.viewMenu = self.menuBar().addMenu("&View")

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
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        #comboboxes
        widget = QWidget()
        layout = QVBoxLayout()
        self.combobox_widget = QWidget()
        self.combobox_layout = self.createComboboxes()
        self.combobox_widget.setLayout(self.combobox_layout)
        # self.combobox_widget.setMaximumHeight(40)
        layout.addWidget(self.combobox_widget)

        #Stretch
        self.stretch_sliders_widget = QWidget()
        self.stretch_sliders_layout = self.createStretchStackedLayout()
        self.stretch_sliders_widget.setLayout(self.stretch_sliders_layout)
        # self.stretch_sliders_widget.setMaximumHeight(50)
        layout.addWidget(self.stretch_sliders_widget)

        #Interval
        self.interval_sliders_widget = QWidget()
        self.interval_sliders_layout = self.createIntervalStackedLayout()
        self.interval_sliders_widget.setLayout(self.interval_sliders_layout)
        # self.interval_sliders_widget.setMaximumHeight(125)
        layout.addWidget(self.interval_sliders_widget)
        widget.setLayout(layout)
        widget.setMaximumHeight(350)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        #radial profiles
        dock = QDockWidget("Radial Profile Curve", self)
        dock.setObjectName("RADIAL_PROFILE")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.radial_profile_widget = RadialProfileWidget(self.fits_image.data)
        dock.setWidget(self.radial_profile_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = QDockWidget("Radial Profile Fit", self)
        dock.setObjectName("RADIAL_PROFILE_IRAF")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.radial_profile_iraf_widget = IRAFRadialProfileWidget(self.fits_image.data)
        dock.setWidget(self.radial_profile_iraf_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())


    def createStretchStackedLayout(self):
        self.stretchStackedLayout = QStackedLayout()
        asinhSlider = self.createAsinhParamsSliders()
        contrastbiasSliders = self.createContrastbiasParamsSliders()
        histogram = QLabel("histogram") #do zmiany
        linear = self.createLinearSliders()
        log = self.createLogSliders()
        powerdist = self.createPowerdistSliders()
        power = self.createPowerSliders()
        sinh = self.createSinhSliders()
        sqrt = QLabel("sqrt") #do zmiany
        square = QLabel("square") #do zmiany
        self.stretchStackedLayout.addWidget(asinhSlider)
        self.stretchStackedLayout.addWidget(contrastbiasSliders)
        self.stretchStackedLayout.addWidget(histogram)
        self.stretchStackedLayout.addWidget(linear)
        self.stretchStackedLayout.addWidget(log)
        self.stretchStackedLayout.addWidget(powerdist)
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
        self.intervalStackedLayout.addWidget(QLabel("minmax")) #do zmiany
        self.intervalStackedLayout.addWidget(manual)
        self.intervalStackedLayout.addWidget(percentile)
        self.intervalStackedLayout.addWidget(asymetric)
        self.intervalStackedLayout.addWidget(zscale)

        return self.intervalStackedLayout

    def createManualParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        vminSlider = QSlider(Qt.Horizontal)
        vminSlider.setMinimum(0)
        vminSlider.setMaximum(10000)

        vmaxSlider = QSlider(Qt.Horizontal)
        vmaxSlider.setMinimum(10000)
        vmaxSlider.setMaximum(50000)

        vminSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                          {'vmin': vminSlider.value()/10,
                                                                          'vmax': vmaxSlider.value()}))
        vmaxSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                          {'vmin': vminSlider.value(),
                                                                          'vmax': vmaxSlider.value()}))

        layout.addWidget(QLabel('vmin'), 0, 0)
        layout.addWidget(vminSlider, 0, 1)
        layout.addWidget(QLabel('vmax'), 1, 0)
        layout.addWidget(vmaxSlider, 1, 1)
        widget.setLayout(layout)

        return widget

    def createPercentileParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        percentileSlider = QSlider(Qt.Horizontal)
        percentileSlider.setMinimum(10)
        percentileSlider.setMaximum(100)

        samplesSlider = QSlider(Qt.Horizontal)
        samplesSlider.setMinimum(100)
        samplesSlider.setMaximum(2000)

        percentileSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                                {'percentile': percentileSlider.value()/100,
                                                                                'n_samples': samplesSlider.value()}))
        samplesSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                             {'percentile': percentileSlider.value()/100,
                                                                             'n_samples': samplesSlider.value()}))

        layout.addWidget(QLabel('percentile'), 0, 0)
        layout.addWidget(percentileSlider, 0, 1)
        layout.addWidget(QLabel('samples'), 1, 0)
        layout.addWidget(samplesSlider, 1, 1)
        widget.setLayout(layout)

        return widget

    def createAsymetricParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        l_percentileSlider = QSlider(Qt.Horizontal)
        l_percentileSlider.setMinimum(10)
        l_percentileSlider.setMaximum(100)

        u_percentileSlider = QSlider(Qt.Horizontal)
        u_percentileSlider.setMinimum(20)
        u_percentileSlider.setMaximum(100)

        samplesSlider = QSlider(Qt.Horizontal)
        samplesSlider.setMinimum(100)
        samplesSlider.setMaximum(2000)
        #connects

        l_percentileSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                                  {'lower_percentile': l_percentileSlider.value()/100,
                                                                                  'upper_percentile': u_percentileSlider.value()/100,
                                                                                  'n_samples': samplesSlider.value()}))
        u_percentileSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                                  {'lower_percentile': l_percentileSlider.value()/100,
                                                                                  'upper_percentile': u_percentileSlider.value()/100,
                                                                                  'n_samples': samplesSlider.value()}))
        samplesSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                             {'lower_percentile': l_percentileSlider.value()/100,
                                                                                  'upper_percentile': u_percentileSlider.value()/100,
                                                                                  'n_samples': samplesSlider.value()}))

        layout.addWidget(QLabel("l_percentile"), 0, 0)
        layout.addWidget(l_percentileSlider, 0, 1)
        layout.addWidget(QLabel("u_percentile"), 1, 0)
        layout.addWidget(u_percentileSlider, 1, 1)
        layout.addWidget(QLabel("samples"), 2, 0)
        layout.addWidget(samplesSlider, 2, 1)
        widget.setLayout(layout)

        return widget

    def createZscaleParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        samplesSlider = QSlider(Qt.Horizontal)
        samplesSlider.setMinimum(100)
        samplesSlider.setMaximum(2000)

        contrastSlider = QSlider(Qt.Horizontal)
        contrastSlider.setMinimum(1)
        contrastSlider.setMaximum(100)

        m_rejectSlider = QSlider(Qt.Horizontal)
        m_rejectSlider.setMinimum(1)
        m_rejectSlider.setMaximum(100)

        min_pixelsSlider = QSlider(Qt.Horizontal)
        min_pixelsSlider.setMinimum(1)
        min_pixelsSlider.setMaximum(10)

        krejSlider = QSlider(Qt.Horizontal)
        krejSlider.setMinimum(10)
        krejSlider.setMaximum(50)

        m_iterationsSlider = QSlider(Qt.Horizontal)
        m_iterationsSlider.setMinimum(1)
        m_iterationsSlider.setMaximum(10)

        samplesSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                             {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value()/100,
                                                                             'max_reject': m_rejectSlider.value()/100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value()/10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                             ))
        contrastSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                              {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value() / 100,
                                                                             'max_reject': m_rejectSlider.value() / 100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value() / 10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                              ))
        m_rejectSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                              {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value() / 100,
                                                                             'max_reject': m_rejectSlider.value() / 100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value() / 10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                              ))
        min_pixelsSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                                {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value()/100,
                                                                             'max_reject': m_rejectSlider.value()/100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value()/10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                                ))
        krejSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                          {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value() / 100,
                                                                             'max_reject': m_rejectSlider.value() / 100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value() / 10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                          ))
        m_iterationsSlider.valueChanged.connect(lambda changed: self.changeParams(self.stretch_dict,
                                                                                  {'nsamples': samplesSlider.value(),
                                                                             'contrast': contrastSlider.value() / 100,
                                                                             'max_reject': m_rejectSlider.value() / 100,
                                                                             'min_npixels': min_pixelsSlider.value(),
                                                                             'krej': krejSlider.value() / 10,
                                                                             'max_iterations': m_iterationsSlider.value()}
                                                                                  ))

        layout.addWidget(QLabel("samples"), 0, 0)
        layout.addWidget(samplesSlider, 0, 1)
        layout.addWidget(QLabel("contrast"), 1, 0)
        layout.addWidget(contrastSlider, 1, 1)
        layout.addWidget(QLabel("max reject"), 2, 0)
        layout.addWidget(m_rejectSlider, 2, 1)
        layout.addWidget(QLabel("pixels"), 3, 0)
        layout.addWidget(min_pixelsSlider, 3, 1)
        layout.addWidget(QLabel("krej"), 4, 0)
        layout.addWidget(krejSlider, 4, 1)
        layout.addWidget(QLabel("m_iterations"), 5, 0)
        layout.addWidget(m_iterationsSlider, 5, 1)

        widget.setLayout(layout)

        return widget

    def createComboboxes(self):
        layout = QHBoxLayout()

        self.stretch_combobox = QComboBox()
        self.stretch_combobox.addItems(['asinh', 'contrastbias', 'histogram', 'linear',
                                        'log', 'powerdist', 'power', 'sinh', 'sqrt', 'square'])


        self.interval_combobox = QComboBox()
        self.interval_combobox.addItems(['minmax', 'manual', 'percentile', 'asymetric', 'zscale'])

        self.color_combobox = QComboBox()
        self.color_combobox.addItems(['green', 'red', 'blue'])

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
        self.plotNewFitsImage(self.stretch_combobox.currentText(), self.interval_combobox.currentText())

    def plotNewFitsImage(self, stretch, interval):
        if self.fits_image == None:
            self.fits_image = FitsPlotter(fitsfile=fileName, stretch=stretch, interval=interval)
            self.fits_image.plot_fits_file()
        else:
            self.fits_image.set_normalization(stretch=stretch, interval=interval)
        self.fits_image.invalidate()
        # self.central_widget = FigureCanvas(self.fits_image.figure)
        # self.setCentralWidget(self.central_widget)

    def createAsinhParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        aSlider = QSlider(Qt.Horizontal)
        aSlider.setMinimum(1)
        aSlider.setMaximum(10)

        aSlider.valueChanged.connect(lambda changed: self.changeParams({'a': aSlider.value() / 10}, self.interval_dict))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(aSlider, 0, 1)
        widget.setLayout(layout)

        return widget

    def createContrastbiasParamsSliders(self):

        widget = QWidget()
        layout = QGridLayout()

        contrastSlider = QSlider(Qt.Horizontal)
        contrastSlider.setMinimum(1)
        contrastSlider.setMaximum(30)

        biasSlider = QSlider(Qt.Horizontal)
        biasSlider.setMinimum(1)
        biasSlider.setMaximum(30)

        contrastSlider.valueChanged.connect(
            lambda checked: self.changeParams(
                {'contrast': contrastSlider.value()/10,
                 'bias': biasSlider.value()/10},
                self.interval_dict))
        biasSlider.valueChanged.connect(
            lambda checked: self.changeParams(
                {'contrast': contrastSlider.value()/10,
                 'bias': biasSlider.value()/10},
                self.interval_dict))

        layout.addWidget(QLabel('contrast'), 0, 0)
        layout.addWidget(contrastSlider, 0, 1)
        layout.addWidget(QLabel('bias'), 1, 0)
        layout.addWidget(biasSlider, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLinearSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        slopeSlider = QSlider(Qt.Horizontal)
        slopeSlider.setMinimum(1)
        slopeSlider.setMaximum(10)

        interceptSlider = QSlider(Qt.Horizontal)
        interceptSlider.setMinimum(0)
        interceptSlider.setMaximum(10)

        #connects
        slopeSlider.valueChanged.connect(
            lambda changed: self.changeParams(
                {'slope': slopeSlider.value()/10,
                 'intercept': interceptSlider.value()/10},
                self.interval_dict))
        interceptSlider.valueChanged.connect(
            lambda changed: self.changeParams(
                {'slope': slopeSlider.value()/10,
                 'intercept': interceptSlider.value()/10},
                self.interval_dict))

        layout.addWidget(QLabel("slope"), 0, 0)
        layout.addWidget(slopeSlider, 0, 1)
        layout.addWidget(QLabel("intercept"), 1, 0)
        layout.addWidget(interceptSlider, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLogSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        aSlider = QSlider(Qt.Horizontal)
        aSlider.setMinimum(10)
        aSlider.setMaximum(20000)
        aSlider.valueChanged.connect(lambda changed: self.changeParams({'a': aSlider.value() / 10},
                                                                       self.interval_dict))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(aSlider, 0, 1)
        widget.setLayout(layout)

        return widget

    def createPowerdistSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        aSlider = QSlider(Qt.Horizontal)
        aSlider.setMinimum(10)
        aSlider.setMaximum(20000)
        aSlider.valueChanged.connect(lambda changed: self.changeParams({'a': aSlider.value() / 10},
                                                                       self.interval_dict))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(aSlider, 0, 1)
        widget.setLayout(layout)
        return widget

    def createPowerSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        aSlider = QSlider(Qt.Horizontal)
        aSlider.setMinimum(1)
        aSlider.setMaximum(10)

        # connects
        aSlider.valueChanged.connect(lambda changed: self.changeParams({'a': aSlider.value() / 10},
                                                                       self.interval_dict))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(aSlider, 0, 1)
        widget.setLayout(layout)
        return widget

    def createSinhSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        aSlider = QSlider(Qt.Horizontal)
        aSlider.setMinimum(1)
        aSlider.setMaximum(10)

        # connects
        aSlider.valueChanged.connect(lambda changed: self.changeParams({'a': aSlider.value() / 10},
                                                                       self.interval_dict))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(aSlider, 0, 1)
        widget.setLayout(layout)
        return widget

    def changeParams(self, stretch_dictionary, interval_dictionary):
        #testowe
        print(self.stretch_combobox.currentText())
        print(self.interval_combobox.currentText())
        print("------------------")
        print(stretch_dictionary)
        print(interval_dictionary)
        #
        if self.stretch_dict != stretch_dictionary:
            self.stretch_dict = stretch_dictionary
        if self.interval_dict != interval_dictionary:
            self.interval_dict = interval_dictionary
        self.fits_image.set_normalization(stretch=self.stretch_combobox.currentText(),
                                          interval=self.interval_combobox.currentText(),
                                          stretchkwargs=stretch_dictionary,
                                          intervalkwargs=interval_dictionary)

        self.fits_image.invalidate()
        # self.central_widget = FigureCanvas(self.fits_image.figure)
        # widget = QWidget()
        # layout = QVBoxLayout()
        # layout.addWidget(self.toolbar)
        # layout.addWidget(self.central_widget)
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

    def changeColor(self, color):
        #testowe
        print(self.stretch_combobox.currentText())
        print(self.interval_combobox.currentText())
        print(color)
        print("------------------")
        print(self.stretch_dict)
        print(self.interval_dict)
        #
        if color == 'red':
            self.fits_image.plot_fits_file(color='r')
        elif color == 'green':
            self.fits_image.plot_fits_file(color='g')
        elif color == 'blue':
            self.fits_image.plot_fits_file(color='b')

        self.fits_image.set_normalization(stretch=self.stretch_combobox.currentText(),
                                          interval=self.interval_combobox.currentText(),
                                          stretchkwargs=self.stretch_dict,
                                          intervalkwargs=self.interval_dict)

        self.fits_image.invalidate()
        # self.central_widget = FigureCanvas(self.fits_image.figure)
        # self.setCentralWidget(self.central_widget)

    def createInfoWindow(self):
        dock = QDockWidget("FITS header", self)
        dock.setObjectName("FTIS_DATA")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.headerWidget = HeaderTableWidget(self)
        self.headerWidget.setColumnCount(2)
        self.headerWidget.setHorizontalHeaderItem(0, QTableWidgetItem("KEY"))
        self.headerWidget.setHorizontalHeaderItem(1, QTableWidgetItem("VALUE"))
        self.headerWidget.horizontalHeader().setStretchLastSection(1);
        self.headerWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        dock.setWidget(self.headerWidget)




    def onCenterCircleChange(self, change):
        self.radial_profile_widget.set_centroid(self.painterComponent.ccenter_x, self.painterComponent.ccenter_y)
        self.radial_profile_iraf_widget.set_centroid(self.painterComponent.ccenter_x, self.painterComponent.ccenter_y)

    def onCenterCircleRadiusChange(self, change):
        self.radial_profile_widget.set_radius(self.painterComponent.cradius)
        self.radial_profile_iraf_widget.set_radius(self.painterComponent.cradius)

    def onMouseMoveOnImage(self, change):
        display = ''
        if change.new is not None:
            display = f'{change.new:f}'
        if change.name == 'mouse_xdata':
            self.mouse_x_label.setText(display)
        elif change.name == 'mouse_ydata':
            self.mouse_y_label.setText(display)

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


class HeaderTableWidget(QTableWidget):

    def __init__(self, parent = None):
        QTableWidget.__init__(self, parent)
        self.pinnedItems = []


    def contextMenuEvent(self, event):
        if self.selectionModel().selection().indexes():
            for i in self.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QMenu(self)
            pin = menu.addAction("Pin/Unpin")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == pin:
                self.changePinAction(row, column)

            self.setHeader()

    def changePinAction(self, row, column):
        cell = self.item(row, 0);
        try:
            self.pinnedItems.index(cell.text())
            self.pinnedItems.remove(cell.text())
        except ValueError:
            self.pinnedItems.append(cell.text())
        print(self.pinnedItems)

    def createRow(self, pos, key, val, pin):
        newKeyItem = QTableWidgetItem()
        newKeyItem.setText(key)
        newValItem = QTableWidgetItem()
        newValItem.setText(val)

        color = PySide2.QtGui.QColor(200, 220, 200)
        if bool(pin):
            newKeyItem.setIcon(QIcon.fromTheme('emblem-important'));
            newKeyItem.setBackground(color)
            newValItem.setBackground(color)
        self.insertRow(pos)
        self.setItem(pos, 0, newKeyItem)
        self.setItem(pos, 1, newValItem)

    def setHeader(self):
        header = mainWin.fits_image.header
        self.setRowCount(0)
        pos = 0
        for key in self.pinnedItems :
            try:
                value = str(header[key])
            except KeyError:
                value = "---- NOT FOUND ----"
            self.createRow(pos, key, value, bool(1))
            pos += 1

        for key in list(header.keys()):
            try:
                self.pinnedItems.index(key)
            except ValueError:
                value = str(header[key])
                self.createRow(pos, key, value, bool(0))
                pos += 1

        self.resizeRowsToContents()
        self.verticalHeader().hide()

    def readSettings(self, settings):
        try:
            size = settings.beginReadArray("pinnedHeaders");
            for i in range(size):
                settings.setArrayIndex(i);
                pin = settings.value("pin");
                self.pinnedItems.append(pin);
            settings.endArray();
        except SystemError:
            self.pinnedItems = None

        if self.pinnedItems is None:
            self.pinnedItems = []

    def writeSettings(self, settings):
        settings.beginWriteArray("pinnedHeaders");
        i = 0
        for pin in self.pinnedItems:
            settings.setArrayIndex(i);
            settings.setValue("pin", pin);
            i += 1
        settings.endArray();

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
