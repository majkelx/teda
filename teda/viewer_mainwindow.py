"""TeDa FITS Viewer main window"""
import os

import PySide6
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QFile, Qt, QTextStream, QSettings
from PySide6.QtGui import QFont, QIcon, QKeySequence, QKeyEvent, QMouseEvent, QAction
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QApplication, QLabel, QDialog, QDockWidget, QWidget, QPushButton,
                               QFileDialog, QMainWindow, QMessageBox, QTableWidgetItem,
                               QComboBox)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from teda.version import __version__
from teda.views.fitsplot import FitsPlotter
from teda.views.fitsplot_fitsfile import FitsPlotterFitsFile
from teda.models.coordinates import CoordinatesModel
from teda.painterComponent import PainterComponent
from teda.widgets.radialprofile import RadialProfileWidget
from teda.widgets.fullViewWidget import FullViewWidget
from teda.widgets.zoomViewWidget import ZoomViewWidget
from teda.widgets.radialprofileIRAF import IRAFRadialProfileWidget
from teda.widgets.headerTableWidget import HeaderTableWidget
from teda.widgets.scaleWidget import ScaleWidget
from teda.widgets.scanToolbar import ScanToolbar
from teda.widgets.info import InfoWidget
from teda.models.cmaps import ColorMaps
from teda.models.scalesModel import ScalesModel
from teda.icons import IconFactory
from teda import draggingComponent
from . import console
from .widgets.fileSystemWidget import FileSystemWidget


class MainWindow(QMainWindow):
    def __init__(self, tedaCommandLine):
        super().__init__()
        self.tedaCommandLine = tedaCommandLine
        self.cmaps = ColorMaps()
        self.combobox = QComboBox()
        self.filename = None
        self.isMousePressed = False
        self.isCmdPressed = False
        self.cursor_coords = CoordinatesModel()
        self.scales_model = ScalesModel()
        fig = Figure(figsize=(14, 10))
        fig.tight_layout()
        self.fits_image = FitsPlotter(figure=fig)
        fig.subplots_adjust(left=0, bottom=0.001, right=1, top=1, wspace=None, hspace=None)

        self.fits_image = FitsPlotterFitsFile(figure=fig, cmap_model=self.cmaps,
                                              scale_model=self.scales_model)
        self.central_widget = FigureCanvas(fig)
        self.setCentralWidget(self.central_widget)

        self.current_x_coord = 0
        self.current_y_coord = 0

        self.fullWidgetXcord = 0
        self.fullWidgetYcord = 0
        self.centralWidgetcordX = 0
        self.centralWidgetcordY = 0

        self.painterComponent = PainterComponent(self.fits_image)
        # self.painterComponent.startMovingEvents(self.central_widget)
        self.painterComponent.setCanvas(self.central_widget)
        self.scanObject = ScanToolbar(self)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()
        if not self.tedaCommandLine.ignoreSettings:
            self.scaleWidget.readSlidersValues()
        # self.defineButtonsActions()
        self.setWindowTitle("TeDa")

        self.painterComponent.observe(lambda change: self.onAutoCenterChange(change), ['auto_center'])

        self.readWindowSettings()
        self.readAppState()

        self.updateHeaderData()
        self.dragging = draggingComponent.Dragging(widget=self, scale_widget=self.scaleWidget)
        self.activeLinearAdjustmentByMouseMovement()

        # Observing here may be to late for values loaded from settings e.g. via readAppState
        self.painterComponent.observe(lambda change: self.onCenterCircleChange(change), ['ccenter_x', 'ccenter_y'])
        self.painterComponent.observe(lambda change: self.onCenterCircleRadiusChange(change), ['cradius'])
        self.fits_image.observe(lambda change: self.onMouseMoveOnImage(change), ['mouse_xdata', 'mouse_ydata'])
        # self.cmaps.observe(lambda change: self.on_colormap_change(change))
        self.full_view_widget.painterComponent.observe(lambda change: self.onRectangleInWidgetMove(change), ['viewX', 'viewY'])
        self.painterComponent.observe(lambda change: self.movingCentralWidget(change), ['movingViewX', 'movingViewY'])
        self.fits_image.observe(lambda change: self.onMouseZoomOnImage(change), ['viewBounaries_versionno'])

        # open last fits
        try:
            self.openLastFits()
        except FileNotFoundError:
            print('Błąd w odczycie lub brak ostatio wczytanego pliku')

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent):
        self.writeAppState()
        self.writeWindowSettings()
        if not self.tedaCommandLine.ignoreSettings:
            self.scaleWidget.writeSlidersValues()
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
        if e.key() == Qt.Key_Control:
            self.isCmdPressed = True

    def keyReleaseEvent(self, event:PySide6.QtGui.QKeyEvent):
        if event.key() == Qt.Key_Control:
            self.isCmdPressed = False

    def canvasMousePressEvent(self, event):
        self.isMousePressed = not self.isMousePressed

    def mouseMoveEventOnCanvas(self, event):
        if self.isCmdPressed:
            if self.isMousePressed:
                self.dragging.mouseMoveEvent(event)

    def print_(self):
        document = self.textEdit.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def open_dialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", ".", "Fits files (*.fits)")
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

    def save_dialog(self):
        figure = self.central_widget.figure
        filetypes = figure.canvas.get_supported_filetypes_grouped()
        filterstr = ';;'.join([
            k+' (' + ' '.join([
                '*.'+ext for ext in v
            ])+')' for k, v in filetypes.items()
        ])
        dialog = QFileDialog.getSaveFileName(self, "Save Image As...", os.path.splitext(self.filename)[0], filterstr)
        if dialog[0] != "":
            try:
                self.central_widget.figure.savefig(dialog[0])
            except ValueError:
                print("Unsupported format")

    def open_fits(self, fileName):
        """Opens specified FITS file and loads it to user interface"""
        self.fits_image.set_file(fileName)
        self.filename = fileName
        self.cursor_coords.set_wcs_from_fits(self.fits_image.header)  # TODO: one up and extract and set wcs in fits_image before plot
        self.fits_image.set_wcs(self.cursor_coords.wcs)

        self.fits_image.plot()

        self.radial_profile_widget.set_data(self.fits_image.data)
        self.radial_profile_iraf_widget.set_data(self.fits_image.data)

        self.updateHeaderData()

        self.zoom_view_widget.updateFits(self.fits_image)
        self.full_view_widget.updateFits(self.fits_image)
        self.saveLastFits()

    def saveLastFits(self):
        if self.tedaCommandLine.ignoreSettings:
            return
        settings = QSettings()
        settings.beginGroup("Files")
        settings.setValue("lastFile", self.filename)
        settings.endGroup()

    def openLastFits(self):
        if (self.tedaCommandLine.openFile is None):
            if self.tedaCommandLine.ignoreSettings:
                return
            settings = QSettings()
            settings.beginGroup("Files")
            filename = settings.value("lastFile")
            settings.endGroup()
        else:
            filename = self.tedaCommandLine.openFile
        if filename:
            try:
                self.open_fits(filename)
            except (FileNotFoundError, OSError) as e:
                print(f'Error opening last file {filename}: {e}')

    def readAppState(self):
        if self.tedaCommandLine.ignoreSettings:
            return
        settings = QSettings()
        settings.beginGroup("WCS")
        self.wcsSexAct.setChecked(bool(settings.value("sexagesimal", True)))
        self.wcsGridAct.setChecked(bool(settings.value("grid", False)))
        settings.endGroup()
        settings.beginGroup("paint")
        self.painterComponent.auto_center = bool(settings.value("auto_center", True))
        settings.endGroup()




    def writeAppState(self):
        if self.tedaCommandLine.ignoreSettings:
            return
        settings = QSettings()
        settings.beginGroup("WCS")
        settings.setValue("sexagesimal", self.wcsSexAct.isChecked())
        settings.setValue("grid", self.wcsGridAct.isChecked())
        settings.endGroup()
        settings.beginGroup("paint")
        settings.setValue("auto_center", self.painterComponent.auto_center)
        settings.endGroup()

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
                          f"TeDa FITS Viewer {__version__} <br/>"
                          "Authors: <ul> "
                          "<li>Michał Brodniak</li>"
                          "<li>Konrad Górski</li>"
                          "<li>Mikołaj Kałuszyński</li>"
                          "<li>Edward Lis</li>"
                          "<li>Grzegorz Mroczkowski</li>"
                          "</ul>"
                          "Created by <a href='https://akond.com'>Akond Lab</a> for The "
                          "<a href='https://araucaria.camk.edu.pl'>Araucaria Project</a><br/>"
                          "Licence: MIT <br/>"
                          "3rd party work used: "
                          "<a href='https://material.io/resources/icons/'> Google Material Icons</a>, "
                          "<a href='https://www.astropy.org'> AstroPy</a>, "
                          "<a href='https://doc.qt.io/qtforpython/'> Qt5/PySide6</a>, "
                          "<a href='https://www.scipy.org'> SciPy</a>, and other..."
                          "<br/><br/>"
                          "Visit the <a href='https://github.com/majkelx/teda'>project's GitHub  page</a> for help"
                          " and the issue tracker"
                          )

    def on_console_show(self):
        console.show(
            ax=self.fits_image.ax,
            window=self,
            data=self.fits_image.data,
            header=self.fits_image.header,
            wcs=self.cursor_coords.wcs)

    def on_sex_toggle(self):
        print('sex toggled to :', self.wcsSexAct.isChecked())
        self.cursor_coords.wcs_sexagesimal = self.wcsSexAct.isChecked()

    def on_grid_toggle(self):
        self.fits_image.plot_grid = self.wcsGridAct.isChecked()

    def createActions(self):
        # ico1 = QPixmap('/Users/mka/projects/astro/teda/icons/png.png')
        # self.openAct = QAction(ico1, "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open)
        self.openAct = QAction(IconFactory.getIcon('note_add'),
                               "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open_dialog)
        self.saveAct = QAction(IconFactory.getIcon('save'),
                               "&Save", self, shortcut=QKeySequence.Save, statusTip="Save FITS view",
                               triggered=self.save_dialog)
        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application", triggered=self.close)
        self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, statusTip="Show the Qt library's About box", triggered=QApplication.instance().aboutQt)

        self.qtConsoleAct = QAction('Python Console', self,
                                    statusTip="Open IPython console window", triggered=self.on_console_show)

        self.wcsSexAct = QAction('Sexagesimal', self,
                                 statusTip="Format WCS coordinates as sexagesimal (RA in hour angle) instead of decimal deg")
        self.wcsSexAct.toggled.connect(self.on_sex_toggle)
        self.wcsSexAct.setCheckable(True)

        self.wcsGridAct = QAction('Show Grid', self,
                                 statusTip="Overlay WCS coordinates grid over image",)
        self.wcsGridAct.setCheckable(True)
        self.wcsGridAct.toggled.connect(self.on_grid_toggle)

        self.prevHDUAct = QAction(IconFactory.getIcon('skip_previous'), 'Prev HDU', self,
                                  statusTip="Previous HDU", triggered=self.prevHDU)
        self.nextHDUAct = QAction(IconFactory.getIcon('skip_next'), 'Next HDU', self,
                                  statusTip="Next HDU", triggered=self.nextHDU)

        self.zoom4Act = QAction(IconFactory.getIcon("x4"), 'Zoom ×4', self,
                                  statusTip="Zoom ×4", triggered=self.setZoomButton4)
        self.zoom2Act = QAction(IconFactory.getIcon("x2"), 'Zoom ×2', self,
                                  statusTip="Zoom ×2", triggered=self.setZoomButton2)
        self.zoomHomeAct = QAction(IconFactory.getIcon('home'), 'Home', self,
                                  statusTip="Reset zoom an position", triggered=self.setZoomButtonHome)
        self.zoom05Act = QAction(IconFactory.getIcon("1-2"), 'Zoom 1/2', self,
                                  statusTip="Zoom 1/2", triggered=self.setZoomButton05)
        self.zoom025Act = QAction(IconFactory.getIcon("1-4"), 'Zoom 1/4', self,
                                  statusTip="Zoom 1/4", triggered=self.setZoomButton025)

        self.panningAct = QAction(IconFactory.getIcon('panning'), 'Panning', self,
                                 statusTip="Panning", triggered=self.changePanningStatus)
        self.circleAct = QAction(IconFactory.getIcon('circle'), 'Add Region', self,
                                  statusTip="Add Region", triggered=self.changeAddCircleStatus)
        self.centerCircleAct = QAction(IconFactory.getIcon('add_circle_outline'), 'Radial profile', self,
                                 statusTip="Radial profile with gaussoide fit [R]-key", triggered=self.changeAddCenterCircleStatus)
        self.autoCenterAct = QAction('Auto Center', self,
                                     statusTip="Automatically center cursor on star centroid",
                                     triggered=self.changeAutoCenter)
        self.deleteAct = QAction(IconFactory.getIcon('delete_forever'), 'Delete selected', self,
                                 statusTip="Delete selected [Del]-key", triggered=self.deleteSelected)

        self.slidersAct = QAction(IconFactory.getIcon('slider'), 'Dynamic Scale Sliders', self,
                                  statusTip='Show/Hide Dynamic Scale',
                                  triggered=self.dynamicScaleDockWidgetTriggerActions)

        self.panningAct.setCheckable(True)
        self.panningAct.setChecked(True)
        self.circleAct.setCheckable(True)
        self.autoCenterAct.setCheckable(True)
        self.autoCenterAct.setChecked(self.painterComponent.auto_center)
        self.centerCircleAct.setCheckable(True)





    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.scanObject.scanAct)
        self.fileMenu.addAction(self.scanObject.stopAct)
        self.fileMenu.addAction(self.scanObject.pauseAct)
        self.fileMenu.addAction(self.scanObject.resumeAct)
        self.fileMenu.addAction(self.scanObject.autopauseAct)
        self.fileMenu.addAction(self.scanObject.disabledautopauseAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.panningAct)
        self.editMenu.addAction(self.circleAct)
        self.editMenu.addAction(self.centerCircleAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.autoCenterAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.deleteAct)

        self.hduMenu = self.menuBar().addMenu("HDU")
        self.hduMenu.addAction(self.prevHDUAct)
        self.hduMenu.addAction(self.nextHDUAct)
        self.hduMenu.addSeparator()

        self.zoomMenu = self.menuBar().addMenu("Zoom")
        self.zoomMenu.addAction(self.zoom4Act)
        self.zoomMenu.addAction(self.zoom2Act)
        self.zoomMenu.addAction(self.zoomHomeAct)
        self.zoomMenu.addAction(self.zoom05Act)
        self.zoomMenu.addAction(self.zoom025Act)

        self.WcsMenu = self.menuBar().addMenu("W&CS")
        self.WcsMenu.addAction(self.wcsSexAct)
        self.WcsMenu.addSeparator()
        self.WcsMenu.addAction(self.wcsGridAct)

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
        self.fileToolBar.addAction(self.saveAct)

        self.hduToolBar = self.addToolBar("HDU Toolbar")
        self.hduToolBar.addAction(self.prevHDUAct)
        self.hduToolBar.addAction(self.nextHDUAct)

        self.scanToolBar = self.addToolBar("Scan Toolbar")
        self.scanToolBar.addAction(self.scanObject.scanAct)
        self.scanToolBar.addAction(self.scanObject.stopAct)
        self.scanToolBar.addAction(self.scanObject.pauseAct)
        self.scanToolBar.addAction(self.scanObject.resumeAct)
        self.scanToolBar.addAction(self.scanObject.autopauseAct)
        self.scanToolBar.addAction(self.scanObject.disabledautopauseAct)
        self.scanToolBar.hide()

        # self.infoToolBar = self.addToolBar("Info Toolbar")
        # self.mouse_x_label = QLabel('100.1')
        # self.mouse_y_label = QLabel('100.145')
        # self.infoToolBar.addWidget(QLabel('image x:'))
        # self.infoToolBar.addWidget(self.mouse_x_label)
        # self.infoToolBar.addWidget(QLabel('y:'))
        # self.infoToolBar.addWidget(self.mouse_y_label)
        # self.infoToolBar.hide()

        self.zoomToolBar = self.addToolBar("Zoom Toolbar")
        self.zoomToolBar.addAction(self.zoom4Act)
        self.zoomToolBar.addAction(self.zoom2Act)
        self.zoomToolBar.addAction(self.zoomHomeAct)
        self.zoomToolBar.addAction(self.zoom05Act)
        self.zoomToolBar.addAction(self.zoom025Act)

        self.mouseActionToolBar = self.addToolBar("Mouse Task Toolbar")
        self.mouseActionToolBar.addAction(self.panningAct)
        self.mouseActionToolBar.addAction(self.circleAct)
        self.mouseActionToolBar.addAction(self.centerCircleAct)
        self.mouseActionToolBar.addAction(self.deleteAct)

        self.sliderToolBar = self.addToolBar("Slider Toolbar")
        self.slidersAct.setChecked(True)
        self.sliderToolBar.addAction(self.slidersAct)


        self.viewMenu.addAction(self.fileToolBar.toggleViewAction())
        self.viewMenu.addAction(self.hduToolBar.toggleViewAction())
        self.viewMenu.addAction(self.scanToolBar.toggleViewAction())
        # self.viewMenu.addAction(self.infoToolBar.toggleViewAction())
        self.viewMenu.addAction(self.zoomToolBar.toggleViewAction())
        self.viewMenu.addAction(self.mouseActionToolBar.toggleViewAction())
        self.viewMenu.addAction(self.sliderToolBar.toggleViewAction())
        self.viewMenu.addSeparator()

    def nextHDU(self):
        self.fits_image.changeHDU(True, 1)
        self.updateHeaderData()

    def prevHDU(self):
        self.fits_image.changeHDU(True, -1)
        self.updateHeaderData()

    def updateHeaderData(self):
        self.headerWidget.setHeader()
        self.prevHDUAct.setEnabled(self.fits_image._huds is not None and self.fits_image.hdu != 0)
        self.nextHDUAct.setEnabled(self.fits_image._huds is not None and self.fits_image.hdu != len(self.fits_image._huds) - 1)

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

    def changePanningStatus(self):
        if self.panningAct.isChecked():
            self.toogleOffRegionButtons()
            self.panningAct.toggle()
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.startMovingEvents(self.central_widget)
        else:
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.stopMovingEvents(self.central_widget)

    def changeAddCircleStatus(self):
        if self.circleAct.isChecked():
            self.toogleOffRegionButtons()
            self.circleAct.toggle()
            self.painterComponent.startPainting(self.central_widget, "circle")
        else:
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.startMovingEvents(self.central_widget)
            self.panningAct.toggle()

    def changeAddCenterCircleStatus(self):
        if self.centerCircleAct.isChecked():
            self.toogleOffRegionButtons()
            self.centerCircleAct.toggle()
            self.painterComponent.startPainting(self.central_widget, "circleCenter")
        else:
            self.painterComponent.stopPainting(self.central_widget)
            self.painterComponent.startMovingEvents(self.central_widget)
            self.panningAct.toggle()

    def changeAutoCenter(self):
        self.painterComponent.auto_center = self.autoCenterAct.isChecked()

    def deleteSelected(self):
        self.painterComponent.deleteSelectedShapes(self.central_widget.figure.axes[0])

    def toogleOffRegionButtons(self):
        if self.panningAct.isChecked():
            self.panningAct.toggle()
        if self.circleAct.isChecked():
            self.circleAct.toggle()
        if self.centerCircleAct.isChecked():
            self.centerCircleAct.toggle()
        self.painterComponent.stopPainting(self.central_widget)


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createDockWindows(self):
        # Scale
        self.dynamic_scale_dock = QDockWidget("Dynamic Scale", self)
        self.dynamic_scale_dock.setObjectName("SCALE")
        self.dynamic_scale_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.scaleWidget = ScaleWidget(self, scales_model=self.scales_model, cmap_model=self.cmaps)
        self.dynamic_scale_dock.setWidget(self.scaleWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dynamic_scale_dock)
        self.viewMenu.addAction(self.dynamic_scale_dock.toggleViewAction())
        self.dynamic_scale_dock.setFloating(True)
        self.dynamic_scale_dock.hide()


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
        dock.hide()

        #info panel
        dock = QDockWidget("Info", self)
        dock.setObjectName("INFO_PANEL")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.info_widget = InfoWidget(self)
        dock.setWidget(self.info_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        # FITS headers
        dock = QDockWidget("FITS header", self)
        dock.setObjectName("FTIS_DATA")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.headerWidget = HeaderTableWidget(self)
        self.headerWidget.setColumnCount(2)
        self.headerWidget.setHorizontalHeaderItem(0, QTableWidgetItem("KEY"))
        self.headerWidget.setHorizontalHeaderItem(1, QTableWidgetItem("VALUE"))
        self.headerWidget.horizontalHeader().setStretchLastSection(1)
        self.headerWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.headerWidget.clearFocus()
        dock.setWidget(self.headerWidget)

        # full
        dock = QDockWidget("Full view", self)
        dock.setObjectName("FULL_VIEW")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.full_view_widget = FullViewWidget(self.fits_image)
        self.full_view_widget.fits_image.set_scale_model(self.scales_model)
        self.full_view_widget.fits_image.set_cmap_model(self.cmaps)
        dock.setWidget(self.full_view_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        # zoom
        dock = QDockWidget("Zoom view", self)
        dock.setObjectName("ZOOM_VIEW")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.zoom_view_widget = ZoomViewWidget(self.fits_image)
        self.zoom_view_widget.fits_image.set_scale_model(self.scales_model)
        self.zoom_view_widget.fits_image.set_cmap_model(self.cmaps)
        dock.setWidget(self.zoom_view_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        # fileSelector
        dock = QDockWidget("Directory view", self)
        dock.setObjectName("DIRECTORY_VIEW")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.file_widget = FileSystemWidget(self)
        dock.setWidget(self.file_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        self.viewMenu.addSeparator()


    # def changeColor(self, color):
    #     self.cmaps.set_active_color_map(color)

    # def on_colormap_change(self, change):
    #     self.fits_image.cmap = self.cmaps.get_active_color_map()
    #     self.fits_image.plot()
    #     self.updateFitsInWidgets()


    def onAutoCenterChange(self, change):
        self.autoCenterAct.setChecked(change.new)

    def dynamicScaleDockWidgetTriggerActions(self):
        if self.dynamic_scale_dock.isHidden():
            self.dynamic_scale_dock.show()
        else:
            self.dynamic_scale_dock.hide()


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
            # self.mouse_x_label.setText(display)
            self.current_x_coord = val
            self.cursor_coords.set_img_x(change.new)
        elif change.name == 'mouse_ydata':
            # self.mouse_y_label.setText(display)
            self.current_y_coord = val
            self.cursor_coords.set_img_y(change.new)
        if display != '':
            self.zoom_view_widget.setXYofZoom(self.fits_image, self.current_x_coord, self.current_y_coord, self.fits_image.zoom)
            if not self.hasFocus():
                self.setFocus()
            if self.scanObject.activeScan and self.scanObject.enableAutopause:#reser autopause
                if not self.scanObject.obserwableValue.autopauseFlag:
                    self.scanObject.obserwableValue.autopauseFlag = True

    def activeLinearAdjustmentByMouseMovement(self):
        self.central_widget.mpl_connect('motion_notify_event', self.mouseMoveEventOnCanvas)
        self.central_widget.mpl_connect('button_press_event', self.canvasMousePressEvent)
        self.central_widget.mpl_connect('button_release_event', self.canvasMousePressEvent)

    def onMouseZoomOnImage(self, change):
        changed = False
        if change.new is not None:
            changed = True
        if changed:
            self.full_view_widget.updateMiniatureShape(self.fits_image.viewX,self.fits_image.viewY,self.fits_image.viewW,self.fits_image.viewH)

    def readWindowSettings(self):
        if self.tedaCommandLine.ignoreSettings:
            return
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
        self.file_widget.readSettings(settings)

    def writeWindowSettings(self):
        if self.tedaCommandLine.ignoreSettings:
            return
        settings = QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.endGroup()

        settings.setValue('geometry',self.saveGeometry())
        settings.setValue('windowState',self.saveState())

        self.headerWidget.writeSettings(settings)
        self.file_widget.writeSettings(settings)

    # def updateFitsInWidgets(self):
    #     # print("updateFitsInWidgets")
    #     self.full_view_widget.updateFits(self.fits_image)
    #     self.zoom_view_widget.updateFits(self.fits_image)

class QWidgetCustom(QWidget):
    #nakładka na QWidget dla eventu leave
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

    def leaveEvent(self, e):
        self.clearFocus()

