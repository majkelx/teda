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
from PySide2 import QtWidgets
from PySide2.QtCore import QDate, QFile, Qt, QTextStream
from PySide2.QtGui import (QFont, QIcon, QKeySequence, QTextCharFormat,
                           QTextCursor, QTextTableFormat)
from PySide2.QtPrintSupport import QPrintDialog, QPrinter
from PySide2.QtWidgets import (QAction, QApplication, QDialog, QDockWidget, QWidget, QGridLayout, QPushButton,
                               QFileDialog, QListWidget, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from fitsplot import (FitsPlotter)
from fitsopen import (FitsOpen)
from painterComponent import (PainterComponent)
from matplotlib.figure import Figure
from math import *
# from astropy.io import fits
# import matplotlib
# import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #self.fits_plot = None

        self.setWindowTitle("TEDA")

        fig = Figure(figsize=(14, 10))
        self.central_widget = FigureCanvas(fig)
        self.setCentralWidget(self.central_widget)

        self.painterComponent = PainterComponent()
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createInfoWindow()
        self.createDockWindows()
        self.setButtonsStatuses()#do wyrzucenia jesli będą przyciski stanowe activ/inactiv
        self.defineButtonsActions()
        self.setWindowTitle("TEDA")
        #self.startpainting = 'false'

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def open(self):
        global fileName
        fileName, _ = QFileDialog.getOpenFileName(mainWin, "Open Image", ".", "Fits files (*.fits)")
        # fileName = QFileDialog.getOpenFileName(mainWin, "Open Image", "/home/akond/Pulpit/fits files", "Fits files (*.fits)")[0]
        if not fileName:
            return

        self.fits_plot = FitsOpen(fileName)
        self.fits_plot.plot_fits_file()
        self.central_widget = FigureCanvas(self.fits_plot.figure)
        toolbar = NavigationToolbar(self.central_widget, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.central_widget)
        #
        # # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #
        self.setHeader(self.fits_plot.header)

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
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.openAct)
        self.viewMenu.addAction(self.fileToolBar.toggleViewAction())
        self.viewMenu.addSeparator()

        self.hduToolBar = self.addToolBar("HDU")
        self.hduToolBar.addAction("prevHDU").triggered.connect(self.prevHDU)
        self.hduToolBar.addAction("nextHDU").triggered.connect(self.nextHDU)

        self.regionToolBar = self.addToolBar("Region")
        self.regionToolBar.addAction("add circle").triggered.connect(self.changeAddCircleStatus)
        self.regionToolBar.addAction("add center circle").triggered.connect(self.changeAddCenterCircleStatus)
        self.regionToolBar.addAction("make draggable").triggered.connect(self.changeDraggableStatus)

    def nextHDU(self):
        self.fits_plot.changeHDU(True, 1)
        self.setHeader(self.fits_plot.header)

    def prevHDU(self):
        self.fits_plot.changeHDU(True, -1)
        self.setHeader(self.fits_plot.header)

    def changeAddCircleStatus(self):
        #przydałby sie przycisk stanowy activ/inactiv
        self.addCircleActive = 'true'
        self.painterComponent.stopPainting(self.central_widget)
        self.painterComponent.disableAllShapesDraggable()
        self.painterComponent.startPainting(self.central_widget,"circle")

    def changeAddCenterCircleStatus(self):
        # przydałby sie przycisk stanowy activ/inactiv
        self.addCircleActive = 'true'
        self.painterComponent.stopPainting(self.central_widget)
        self.painterComponent.disableAllShapesDraggable()
        self.painterComponent.startPainting(self.central_widget, "circleCenter")

    def changeDraggableStatus(self):
        self.painterComponent.stopPainting(self.central_widget)
        ax = self.central_widget.figure.add_subplot(111)
        self.painterComponent.makeAllShapesDraggable(ax)

    def setButtonsStatuses(self):
        self.addCircleActive = 'false'

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createStretchButtons(self):

        self.layout = QGridLayout()

        self.asinh_stretch = QPushButton("asinh")
        self.contrastbias_stretch = QPushButton("contrastbias")
        self.histogram_stretch = QPushButton("histogram")
        self.linear_stretch = QPushButton("linear")
        self.log_stretch = QPushButton("log")
        self.powerdist_stretch = QPushButton("powerdist")
        self.power_stretch = QPushButton("power")
        self.sinh_stretch = QPushButton("sinh")
        self.sqrt_stretch = QPushButton("sqrt")
        self.square_stretch = QPushButton("square")

        self.layout.addWidget(self.asinh_stretch, 0, 0)
        self.layout.addWidget(self.contrastbias_stretch, 0, 1)
        self.layout.addWidget(self.histogram_stretch, 0, 2)
        self.layout.addWidget(self.linear_stretch, 1, 0)
        self.layout.addWidget(self.log_stretch, 1, 1)
        self.layout.addWidget(self.powerdist_stretch, 1, 2)
        self.layout.addWidget(self.power_stretch, 2, 0)
        self.layout.addWidget(self.sinh_stretch, 2, 1)
        self.layout.addWidget(self.sqrt_stretch, 2, 2)
        self.layout.addWidget(self.square_stretch, 3, 0)

        return self.layout

    def createIntervalButtons(self):

        self.layout = QGridLayout()

        self.minmax_interval = QPushButton("minmax")
        self.manual_interval = QPushButton("manual")
        self.percentile_interval = QPushButton("percentile")
        self.asymetric_interval = QPushButton("asymetric")
        self.zscale_interval = QPushButton("zscale")

        self.layout.addWidget(self.minmax_interval, 0, 0)
        self.layout.addWidget(self.manual_interval, 0, 1)
        self.layout.addWidget(self.percentile_interval, 0, 2)
        self.layout.addWidget(self.asymetric_interval, 1, 0)
        self.layout.addWidget(self.zscale_interval, 1, 1)

        return self.layout

    def createDockWindows(self):
        dock = QDockWidget("Stretchs", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.stretch_buttons_widget = QWidget()
        self.stretch_buttons_layout = self.createStretchButtons()
        self.stretch_buttons_widget.setLayout(self.stretch_buttons_layout)
        dock.setWidget(self.stretch_buttons_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        dock = QDockWidget("Intervals", self)
        self.interval_buttons_widget = QWidget()
        self.interval_buttons_layout = self.createIntervalButtons()
        self.interval_buttons_widget.setLayout(self.interval_buttons_layout)
        dock.setWidget(self.interval_buttons_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())


    def defineButtonsActions(self):
        #stretches
        self.asinh_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'asinh'))
        self.contrastbias_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'contrastbias'))
        self.histogram_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'histogram'))
        self.linear_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'linear'))
        self.log_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'log'))
        self.powerdist_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'powerdist'))
        self.power_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'power'))
        self.sinh_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'sinh'))
        self.sqrt_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'sqrt'))
        self.square_stretch.clicked.connect(lambda clicked: self.stretch_plot(stretch = 'square'))

        #intervals
        self.minmax_interval.clicked.connect(lambda clicked: self.interval_plot(interval='minmax'))
        self.manual_interval.clicked.connect(lambda clicked: self.interval_plot(interval='manual'))
        self.percentile_interval.clicked.connect(lambda clicked: self.interval_plot(interval='percentile'))
        self.asymetric_interval.clicked.connect(lambda clicked: self.interval_plot(interval='asymetric'))
        self.zscale_interval.clicked.connect(lambda clicked: self.interval_plot(interval='zscale'))


    def createInfoWindow(self):
        dock = QDockWidget("FITS data", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.headerWidget = QTableWidget(self)
        self.headerWidget.setColumnCount(2)
        dock.setWidget(self.headerWidget)


    def setHeader(self, header):
        self.headerWidget.setRowCount(len(header))
        i = 0;
        for key in list(header.keys()) :
            newItem = QTableWidgetItem()
            newItem.setText(key)
            self.headerWidget.setItem(i, 0, newItem)
            newItem = QTableWidgetItem()
            newItem.setText(str(header[key]))
            self.headerWidget.setItem(i, 1, newItem)
            i = i + 1

    def stretch_plot(self, stretch):
        if not fileName:
            return

        self.fits_plot = FitsPlotter(fitsfile=fileName, stretch=stretch)
        self.fits_plot.plot_fits_file()
        self.central_widget = FigureCanvas(self.fits_plot.figure)
        self.setCentralWidget(mainWin.central_widget)


    def interval_plot(self, interval):
        if not fileName:
            return

        self.fits_plot = FitsPlotter(fitsfile=fileName, interval=interval)
        self.fits_plot.plot_fits_file()
        self.central_widget = FigureCanvas(self.fits_plot.figure)
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(800, 600)
    mainWin.show()
    sys.exit(app.exec_())
