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
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from teda.version import __version__
from teda.views.fitsplot import FitsPlotter
from teda.views.fitsplot_fitsfile import FitsPlotterFitsFile
from teda.models.coordinates import CoordinatesModel
from teda.painterComponent import PainterComponent
from teda.painterShapes.circleShape import CircleShape
from teda.painterShapes.CircleCenterShape import CircleCenterShape
from teda.widgets.radialprofile import RadialProfileWidget
from teda.widgets.fullViewWidget import FullViewWidget
from teda.widgets.zoomViewWidget import ZoomViewWidget
from teda.widgets.radialprofileIRAF import IRAFRadialProfileWidget
from teda.widgets.linearProfileWidget import LinearProfileWidget
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
from .help_content import HELP_TEXT
import numpy as np


class StatsCalculator(QtCore.QThread):
    """Background thread to calculate image statistics (Phase 6.8)"""
    finished = QtCore.Signal(dict)  # Emits {mean, median, std, min, max}

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        """Calculate statistics in background to avoid blocking UI"""
        try:
            if self.data is None or self.data.size == 0:
                return

            # Use np.percentile for median (faster than np.median on large arrays)
            stats = {
                'mean': float(np.mean(self.data)),
                'median': float(np.percentile(self.data, 50)),
                'std': float(np.std(self.data)),
                'min': float(np.amin(self.data)),
                'max': float(np.amax(self.data)),
            }
            self.finished.emit(stats)
        except Exception as e:
            print(f"Error calculating image statistics: {e}")


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

        # Mouse event debouncing for performance (Phase 2.1)
        self._mouse_timer = QtCore.QTimer()
        self._mouse_timer.setSingleShot(True)
        self._mouse_timer.timeout.connect(self._update_mouse_widgets)
        self._pending_mouse_x = None
        self._pending_mouse_y = None

        # Image statistics calculator (Phase 6.8)
        self._stats_calculator = None
        self._stats_label = None

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

        # Handle reset options before reading settings (Phase 6.1, 6.2)
        self.handleResetOptions()

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

        # Overlay synchronization: observe shape changes in main painter (Phase 2.5)
        self.painterComponent.observe(lambda change: self.onShapesChanged(change), ['shapes_changed'])

        # Line profile: observe line changes (Phase 6.6)
        self.painterComponent.observe(lambda change: self.onLineProfileChanged(change), ['line_profile_changed'])

        # open last fits
        try:
            self.openLastFits()
        except FileNotFoundError:
            print('Error reading or missing last loaded file')

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

        # Line profile shortcuts (Phase 6.7)
        if e.key() == Qt.Key_H:
            self._positionLineHorizontal()
        elif e.key() == Qt.Key_V:
            self._positionLineVertical()
        elif e.key() == Qt.Key_D:
            if e.modifiers() & Qt.ShiftModifier:
                self._positionLineDiagonal(135)  # Shift+D = backslash \
            else:
                self._positionLineDiagonal(45)  # D = forward slash /

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
        self.linear_profile_widget.set_data(self.fits_image.data)

        self.updateHeaderData()

        # BUG FIX #5: Update zoom/full widgets BEFORE setting viewport coordinates
        # This ensures full_view_widget.fits_image.ax exists when rectangle is created
        self.zoom_view_widget.updateFits(self.fits_image)
        self.full_view_widget.updateFits(self.fits_image)

        # BUG FIX #5: Now initialize viewport boundaries - this will trigger observer
        # Observer will call updateMiniatureShape() which will create the rectangle
        # on the correct axes (full_view_widget.fits_image.ax which now exists)
        if self.fits_image.ax is not None:
            self.fits_image.setCordsToTraitlets()

        self.saveLastFits()

        # Phase 6.8: Calculate image statistics in background
        self.calculateImageStatistics()

    def saveLastFits(self):
        if self.tedaCommandLine.ignoreSettings:
            return
        settings = QSettings()
        settings.beginGroup("Files")
        settings.setValue("lastFile", self.filename)
        settings.endGroup()

    def openLastFits(self):
        # Handle directory parameter from CLI
        if self.tedaCommandLine.openDirectory is not None:
            self.file_widget.setPath(self.tedaCommandLine.openDirectory)
            print(f'File explorer set to directory: {self.tedaCommandLine.openDirectory}')
            return

        # Handle file parameter from CLI or settings
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

    def showHelp(self):
        """Display TeDa quick help guide (Phase 6.14)"""
        from PySide6.QtWidgets import QDialog, QTextBrowser, QVBoxLayout

        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("TeDa FITS Viewer - Quick Help")
        help_dialog.resize(750, 650)

        text_browser = QTextBrowser()

        # Resolve logo path
        logo_path = os.path.join(os.path.dirname(__file__), 'img', 'akondastro_logo_dark.svg')
        help_text = HELP_TEXT.format(logo_path=logo_path)

        text_browser.setHtml(help_text)
        text_browser.setOpenExternalLinks(True)

        layout = QVBoxLayout()
        layout.addWidget(text_browser)
        help_dialog.setLayout(layout)

        help_dialog.exec()

    def about(self):
        logo_path = os.path.join(os.path.dirname(__file__), 'img', 'akondastro_logo_dark.svg')
        QMessageBox.about(self, "TeDa FITS Viewer",
                          f"<div style='text-align: center;'>"
                          f"<a href='https://akond.space'><img src='file://{logo_path}' alt='AkondAstro' style='max-width: 180px; margin: 10px 0;'></a>"
                          f"<h3>TeDa FITS Viewer {__version__}</h3>"
                          f"</div>"
                          "<b>Authors:</b> <ul> "
                          "<li>Michał Brodniak</li>"
                          "<li>Konrad Górski</li>"
                          "<li>Mikołaj Kałuszyński</li>"
                          "<li>Edward Lis</li>"
                          "<li>Grzegorz Mroczkowski</li>"
                          "</ul>"
                          "Created by <a href='https://akond.space'>AkondAstro</a> with cooperation of the "
                          "<a href='https://ocm.camk.edu.pl'>OCM observatory</a><br/>"
                          "<b>Licence:</b> MIT <br/>"
                          "<b>3rd party work used:</b> "
                          "<a href='https://material.io/resources/icons/'>Google Material Icons</a>, "
                          "<a href='https://www.astropy.org'>AstroPy</a>, "
                          "<a href='https://doc.qt.io/qtforpython/'>Qt5/PySide6</a>, "
                          "<a href='https://www.scipy.org'>SciPy</a>, and other..."
                          "<br/><br/>"
                          "Visit the <a href='https://github.com/majkelx/teda'>project's GitHub page</a> for help "
                          "and the issue tracker"
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
        # TeDa icon button - shows About dialog
        self.tedaIconAct = QAction(IconFactory.getIcon('teda'), 'About TeDa', self,
                                   statusTip="About TeDa FITS Viewer", triggered=self.about)

        # ico1 = QPixmap('/Users/mka/projects/astro/teda/icons/png.png')
        # self.openAct = QAction(ico1, "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open)
        self.openAct = QAction(IconFactory.getIcon('note_add'),
                               "&Open", self, shortcut=QKeySequence.Open, statusTip="Open FITS file", triggered=self.open_dialog)
        self.saveAct = QAction(IconFactory.getIcon('save'),
                               "&Save", self, shortcut=QKeySequence.Save, statusTip="Save FITS view",
                               triggered=self.save_dialog)
        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit the application", triggered=self.close)
        self.helpAct = QAction("&TeDa Help", self, shortcut=QKeySequence.HelpContents, statusTip="Show TeDa quick help guide", triggered=self.showHelp)
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
        self.lineProfileAct = QAction(IconFactory.getIcon('timeline'), 'Line Profile', self,
                                      statusTip="Draw line profile (h/v/d/D for quick positioning)", triggered=self.changeLineProfileStatus)
        self.autoCenterAct = QAction('Auto Center', self,
                                     statusTip="Automatically center cursor on star centroid",
                                     triggered=self.changeAutoCenter)
        self.deleteAct = QAction(IconFactory.getIcon('delete_forever'), 'Delete selected', self,
                                 statusTip="Delete selected [Del]-key", triggered=self.deleteSelected)

        self.slidersAct = QAction(IconFactory.getIcon('slider'), 'Dynamic Scale Sliders', self,
                                  statusTip='Show/Hide Dynamic Scale',
                                  triggered=self.dynamicScaleDockWidgetTriggerActions)

        self.resetLayoutAct = QAction('Reset Layout', self,
                                      statusTip="Reset window layout and dock positions to defaults",
                                      triggered=self.resetLayoutAction)

        self.panningAct.setCheckable(True)
        self.panningAct.setChecked(True)
        self.circleAct.setCheckable(True)
        self.autoCenterAct.setCheckable(True)
        self.autoCenterAct.setChecked(self.painterComponent.auto_center)
        self.centerCircleAct.setCheckable(True)
        self.lineProfileAct.setCheckable(True)





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
        self.viewMenu.addAction(self.resetLayoutAct)
        self.viewMenu.addSeparator()

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.helpAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File Toolbar")
        self.fileToolBar.addAction(self.tedaIconAct)  # TeDa icon - leftmost
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
        self.mouseActionToolBar.addAction(self.lineProfileAct)
        self.mouseActionToolBar.addAction(self.deleteAct)

        self.sliderToolBar = self.addToolBar("Slider Toolbar")
        self.slidersAct.setChecked(True)
        self.sliderToolBar.addAction(self.slidersAct)

        # Help toolbar - positioned in top toolbar row, as far right as possible
        self.helpToolBar = self.addToolBar("Help Toolbar")
        # Create help button action with question_mark icon
        self.helpButtonAct = QAction(IconFactory.getIcon('question_mark'), 'Quick Help', self,
                                     statusTip="Show TeDa quick help guide", triggered=self.showHelp)
        self.helpToolBar.addAction(self.helpButtonAct)

        self.viewMenu.addAction(self.fileToolBar.toggleViewAction())
        self.viewMenu.addAction(self.hduToolBar.toggleViewAction())
        self.viewMenu.addAction(self.scanToolBar.toggleViewAction())
        # self.viewMenu.addAction(self.infoToolBar.toggleViewAction())
        self.viewMenu.addAction(self.zoomToolBar.toggleViewAction())
        self.viewMenu.addAction(self.mouseActionToolBar.toggleViewAction())
        self.viewMenu.addAction(self.sliderToolBar.toggleViewAction())
        self.viewMenu.addAction(self.helpToolBar.toggleViewAction())
        self.viewMenu.addSeparator()

    def nextHDU(self):
        self.fits_image.changeHDU(True, 1)
        self.updateHeaderData()
        self.calculateImageStatistics()  # Phase 6.8: Update stats when HDU changes

    def prevHDU(self):
        self.fits_image.changeHDU(True, -1)
        self.updateHeaderData()
        self.calculateImageStatistics()  # Phase 6.8: Update stats when HDU changes

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

    def changeLineProfileStatus(self):
        """Activate/deactivate line profile drawing mode."""
        if self.lineProfileAct.isChecked():
            self.toogleOffRegionButtons()
            self.lineProfileAct.toggle()
            self.painterComponent.activateLineProfileMode()
            # Auto-show linear profile widget when tool is activated
            if not self.dockLinearProfile.isVisible():
                self.dockLinearProfile.show()
            print("[MainWindow] Line profile mode activated")
        else:
            self.painterComponent.deactivateLineProfileMode()
            self.painterComponent.startMovingEvents(self.central_widget)
            self.panningAct.toggle()
            print("[MainWindow] Line profile mode deactivated")

    def changeAutoCenter(self):
        self.painterComponent.auto_center = self.autoCenterAct.isChecked()

    def deleteSelected(self):
        self.painterComponent.deleteSelectedShapes(self.central_widget.figure.axes[0])

    # ===== Line Profile Keyboard Shortcuts (Phase 6.7) =====

    def _positionLineHorizontal(self):
        """Create or reposition line to horizontal (boundary-to-boundary) at cursor/center Y."""
        if self.fits_image.data is None:
            return

        mouse_x, mouse_y = self._get_mouse_or_center_coords()

        # Horizontal line at y = mouse_y, spanning full width
        h, w = self.fits_image.data.shape
        start_x, start_y = 1.0, mouse_y
        end_x, end_y = float(w), mouse_y

        self._createOrUpdateLine(start_x, start_y, end_x, end_y)

    def _positionLineVertical(self):
        """Create or reposition line to vertical (boundary-to-boundary) at cursor/center X."""
        if self.fits_image.data is None:
            return

        mouse_x, mouse_y = self._get_mouse_or_center_coords()

        # Vertical line at x = mouse_x, spanning full height
        h, w = self.fits_image.data.shape
        start_x, start_y = mouse_x, 1.0
        end_x, end_y = mouse_x, float(h)

        self._createOrUpdateLine(start_x, start_y, end_x, end_y)

    def _positionLineDiagonal(self, angle_deg):
        """Create or reposition line to diagonal (boundary-to-boundary) at given angle."""
        if self.fits_image.data is None:
            return

        mouse_x, mouse_y = self._get_mouse_or_center_coords()

        # Calculate boundary intersections for diagonal at given angle
        h, w = self.fits_image.data.shape
        start_x, start_y, end_x, end_y = self._calculateDiagonalEndpoints(
            angle_deg, mouse_x, mouse_y, w, h
        )

        self._createOrUpdateLine(start_x, start_y, end_x, end_y)

    def _createOrUpdateLine(self, start_x, start_y, end_x, end_y):
        """Create new line or update existing line position."""
        from teda.painterShapes.lineProfileShape import LineProfileShape

        if self.painterComponent.lineProfile:
            # Update existing line
            line = self.painterComponent.lineProfile[0]
            line.start_x, line.start_y = start_x, start_y
            line.end_x, line.end_y = end_x, end_y
            line.repaintShape()
            # Repaint all shapes to refresh the view
            ax = self.central_widget.figure.axes[0]
            self.painterComponent.paintAllShapes(ax)
        else:
            # Create new line
            line = LineProfileShape(start_x, start_y, end_x, end_y)
            self.painterComponent.lineProfile.append(line)
            ax = self.central_widget.figure.axes[0]
            self.painterComponent.paintAllShapes(ax)

        # Notify observers and show widget
        self.painterComponent.notifyShapesChanged()
        self.painterComponent.line_profile_changed = not self.painterComponent.line_profile_changed

        # Auto-show linear profile widget
        if not self.dockLinearProfile.isVisible():
            self.dockLinearProfile.show()

    def _calculateDiagonalEndpoints(self, angle_deg, cross_x, cross_y, img_width, img_height):
        """
        Calculate boundary-to-boundary diagonal line endpoints.

        For 45° and 135° angles passing through (cross_x, cross_y).
        Returns: (start_x, start_y, end_x, end_y)
        """
        import numpy as np

        # Convert angle to slope
        slope = np.tan(np.radians(angle_deg))

        # Line equation: y - cross_y = slope * (x - cross_x)
        # Find intersections with boundaries: x=1, x=width, y=1, y=height

        intersections = []

        # Left edge (x = 1)
        y = cross_y + slope * (1.0 - cross_x)
        if 1.0 <= y <= img_height:
            intersections.append((1.0, y))

        # Right edge (x = width)
        y = cross_y + slope * (img_width - cross_x)
        if 1.0 <= y <= img_height:
            intersections.append((img_width, y))

        # Top edge (y = 1)
        if slope != 0:
            x = cross_x + (1.0 - cross_y) / slope
            if 1.0 <= x <= img_width:
                intersections.append((x, 1.0))

        # Bottom edge (y = height)
        if slope != 0:
            x = cross_x + (img_height - cross_y) / slope
            if 1.0 <= x <= img_width:
                intersections.append((x, img_height))

        # Should have exactly 2 intersections
        if len(intersections) >= 2:
            start_x, start_y = intersections[0]
            end_x, end_y = intersections[1]
            return start_x, start_y, end_x, end_y

        # Fallback (shouldn't happen)
        return cross_x, 1.0, cross_x, img_height

    def _get_mouse_or_center_coords(self):
        """Get current mouse coords if inside image, else image center."""
        # Check if mouse is inside main canvas and we have valid coordinates
        if (hasattr(self, 'current_x_coord') and hasattr(self, 'current_y_coord') and
            self.current_x_coord is not None and self.current_y_coord is not None and
            self.current_x_coord > 0 and self.current_y_coord > 0):
            return self.current_x_coord, self.current_y_coord

        # Default to image center
        if self.fits_image.data is not None:
            h, w = self.fits_image.data.shape
            return w / 2.0, h / 2.0

        return 1.0, 1.0

    def toogleOffRegionButtons(self):
        if self.panningAct.isChecked():
            self.panningAct.toggle()
        if self.circleAct.isChecked():
            self.circleAct.toggle()
        if self.centerCircleAct.isChecked():
            self.centerCircleAct.toggle()
        if self.lineProfileAct.isChecked():
            self.lineProfileAct.toggle()
        self.painterComponent.stopPainting(self.central_widget)
        self.painterComponent.deactivateLineProfileMode()


    def createStatusBar(self):
        """Create status bar with permanent statistics display (Phase 6.8, 6.6)"""
        self.statusBar().showMessage("Ready")

        # Add permanent widget for linear profile statistics
        self._linear_stats_label = QLabel("Linear: --")
        self._linear_stats_label.setFrameStyle(QLabel.Panel | QLabel.Sunken)
        self._linear_stats_label.setMinimumWidth(350)
        self._linear_stats_label.setToolTip("Linear profile statistics: mean (μ), std (σ), and value range [min-max]")
        self.statusBar().addPermanentWidget(self._linear_stats_label)

        # Add permanent widget for radial profile statistics
        self._radial_stats_label = QLabel("Radial: --")
        self._radial_stats_label.setFrameStyle(QLabel.Panel | QLabel.Sunken)
        self._radial_stats_label.setMinimumWidth(350)
        self._radial_stats_label.setToolTip("Radial profile area statistics: mean (μ), std (σ), and value range [min-max]")
        self.statusBar().addPermanentWidget(self._radial_stats_label)

        # Add permanent widget for image statistics
        self._stats_label = QLabel("Image: --")
        self._stats_label.setFrameStyle(QLabel.Panel | QLabel.Sunken)
        self._stats_label.setMinimumWidth(350)
        self._stats_label.setToolTip("Whole image statistics: mean (μ), std (σ), and value range [min-max]")
        self.statusBar().addPermanentWidget(self._stats_label)

    def createDockWindows(self):
        # Scale
        self.dynamic_scale_dock = QDockWidget("Dynamic Scale", self)
        self.dynamic_scale_dock.setObjectName("SCALE")
        self.dynamic_scale_dock.setAllowedAreas(Qt.NoDockWidgetArea)  # Phase 6.3: Prevent docking
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
        self.radial_profile_iraf_widget.stats_updated.connect(self._onRadialStatsCalculated)
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

        # Linear profile
        dock = QDockWidget("Linear Profile", self)
        dock.setObjectName("LINEAR_PROFILE")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.linear_profile_widget = LinearProfileWidget(self.fits_image.data)
        self.linear_profile_widget.stats_updated.connect(self._onLinearStatsCalculated)
        dock.setWidget(self.linear_profile_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())
        self.dockLinearProfile = dock
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
        # IMMEDIATE updates (critical for responsive UI - no lag)
        val = change.new if change.new is not None else 0

        if change.name == 'mouse_xdata':
            # self.mouse_x_label.setText(display)
            self.current_x_coord = val
            self.cursor_coords.set_img_x(change.new)
            self._pending_mouse_x = change.new
        elif change.name == 'mouse_ydata':
            # self.mouse_y_label.setText(display)
            self.current_y_coord = val
            self.cursor_coords.set_img_y(change.new)
            self._pending_mouse_y = change.new

        # Update zoom widget IMMEDIATELY - user needs instant visual feedback
        # (Optimization is in the zoom widget itself using draw_idle() instead of draw())
        if change.new is not None:
            self.zoom_view_widget.setXYofZoom(
                self.fits_image,
                self.current_x_coord,
                self.current_y_coord,
                self.fits_image.zoom
            )
            # BUG FIX #4: Re-sync shapes after zoom viewport moves
            # Otherwise shapes disappear or show wrong region when mouse moves
            self.syncShapesToZoomView()

        # DEBOUNCED updates (non-critical operations - 50ms delay)
        if change.new is not None:
            self._mouse_timer.start(50)  # Restart 50ms timer

    def _update_mouse_widgets(self):
        """Deferred update of non-critical operations - called after 50ms mouse idle (Phase 2.1)"""
        if self._pending_mouse_x is not None and self._pending_mouse_y is not None:
            # Set focus if needed
            if not self.hasFocus():
                self.setFocus()

            # Autopause handling
            if self.scanObject.activeScan and self.scanObject.enableAutopause:
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

    def onShapesChanged(self, change):
        """Handle shape changes in main painter - sync to full and zoom views (Phase 2.5)"""
        self.syncShapesToFullView()
        self.syncShapesToZoomView()

    def onLineProfileChanged(self, change):
        """Handle line profile changes - update widget (Phase 6.6)"""
        if self.painterComponent.lineProfile and len(self.painterComponent.lineProfile) > 0:
            line = self.painterComponent.lineProfile[0]
            self.linear_profile_widget.set_line(
                line.start_x, line.start_y, line.end_x, line.end_y, line.thickness
            )
        else:
            # No line - clear the widget
            self.linear_profile_widget.clear()

    def syncShapesToFullView(self):
        """Synchronize shapes from main painter to full-image view (Phase 2.5)"""
        full_painter = self.full_view_widget.painterComponent
        main_painter = self.painterComponent

        # Get full view axes - use fits_image.ax if available (after plot()), otherwise widget.ax
        full_ax = self.full_view_widget.fits_image.ax
        if full_ax is None:
            full_ax = self.full_view_widget.ax

        if full_ax is None:
            return

        # Clear existing synced shapes (keep viewport rectangle)
        full_painter.shapes = []
        full_painter.centerCircle = []
        full_painter.lineProfile = []

        # Create NEW shape instances from main painter circles
        for circle in main_painter.shapes:
            # BUG FIX #1: Use originColor (base color) instead of color (which includes selection state)
            new_circle = CircleShape(circle.x, circle.y, circle.size, color=circle.originColor)
            full_painter.shapes.append(new_circle)

        # Create NEW shape instances from main painter center circles
        for center in main_painter.centerCircle:
            # BUG FIX #1: Use originColor (base color) instead of color (which includes selection state)
            new_center = CircleCenterShape(center.x, center.y, center.size, color=center.originColor)
            full_painter.centerCircle.append(new_center)

        # Create NEW shape instances from main painter line profile
        from teda.painterShapes.lineProfileShape import LineProfileShape
        for line in main_painter.lineProfile:
            new_line = LineProfileShape(line.start_x, line.start_y, line.end_x, line.end_y,
                                         line.thickness, color=line.originColor)
            full_painter.lineProfile.append(new_line)

        # Repaint all shapes
        full_painter.paintAllShapes(full_ax)

        # BUG FIX #6: Draw temporary circle during creation (click-drag preview)
        if (hasattr(main_painter, 'tempcircle') and main_painter.tempcircle is not None and
            hasattr(main_painter, 'startpainting') and main_painter.startpainting == 'true'):
            import matplotlib.pyplot as plt
            temp_center = main_painter.tempcircle.center
            temp_radius = main_painter.tempcircle.radius
            temp_circle_patch = plt.Circle(temp_center, temp_radius, color='g', fill=False, linestyle='--')
            full_ax.add_patch(temp_circle_patch)
            full_painter.tempCanvas.draw_idle()

        # BUG FIX #3: Keep only viewport rectangle draggable, remove circle/line draggables
        # Circles and lines should be read-only in full view, only viewport boundary should be draggable
        full_painter.drs = [dr for dr in full_painter.drs
                            if hasattr(dr, 'painterElement') and
                            hasattr(dr.painterElement, 'shapeType') and
                            dr.painterElement.shapeType == 'rectangleMiniature']

    def syncShapesToZoomView(self):
        """Synchronize shapes from main painter to zoom view (Phase 2.5)"""
        zoom_painter = self.zoom_view_widget.painterComponent
        main_painter = self.painterComponent

        # Get zoom view axes - use fits_image.ax if available (after plot()), otherwise widget.ax
        zoom_ax = self.zoom_view_widget.fits_image.ax
        if zoom_ax is None:
            zoom_ax = self.zoom_view_widget.ax

        if zoom_ax is None:
            return

        x_min, x_max = zoom_ax.get_xlim()
        y_min, y_max = zoom_ax.get_ylim()

        # Clear existing synced shapes
        zoom_painter.shapes = []
        zoom_painter.centerCircle = []
        zoom_painter.lineProfile = []

        # Create NEW shape instances for circles that overlap zoom region
        for circle in main_painter.shapes:
            overlaps = self._shapeOverlapsRegion(circle, x_min, x_max, y_min, y_max)
            if overlaps:
                # BUG FIX #1: Use originColor (base color) instead of color (which includes selection state)
                new_circle = CircleShape(circle.x, circle.y, circle.size, color=circle.originColor)
                zoom_painter.shapes.append(new_circle)

        # Create NEW shape instances for center circles that overlap zoom region
        for center in main_painter.centerCircle:
            overlaps = self._shapeOverlapsRegion(center, x_min, x_max, y_min, y_max)
            if overlaps:
                # BUG FIX #1: Use originColor (base color) instead of color (which includes selection state)
                new_center = CircleCenterShape(center.x, center.y, center.size, color=center.originColor)
                zoom_painter.centerCircle.append(new_center)

        # Create NEW shape instances for line profiles that overlap zoom region
        from teda.painterShapes.lineProfileShape import LineProfileShape
        for line in main_painter.lineProfile:
            # Check if line overlaps zoom region (simple check - any endpoint or line segment in view)
            line_overlaps = self._lineOverlapsRegion(line, x_min, x_max, y_min, y_max)
            if line_overlaps:
                new_line = LineProfileShape(line.start_x, line.start_y, line.end_x, line.end_y,
                                             line.thickness, color=line.originColor)
                zoom_painter.lineProfile.append(new_line)

        # Repaint all shapes (read-only - no dragging)
        zoom_painter.paintAllShapes(zoom_ax)

        # BUG FIX #6: Draw temporary circle during creation (click-drag preview)
        if (hasattr(main_painter, 'tempcircle') and main_painter.tempcircle is not None and
            hasattr(main_painter, 'startpainting') and main_painter.startpainting == 'true'):
            import matplotlib.pyplot as plt
            temp_center = main_painter.tempcircle.center
            temp_radius = main_painter.tempcircle.radius
            # Only draw if temporary circle overlaps with zoom region
            if self._shapeOverlapsRegion(type('obj', (object,), {
                'x': temp_center[0], 'y': temp_center[1], 'size': temp_radius
            })(), x_min, x_max, y_min, y_max):
                temp_circle_patch = plt.Circle(temp_center, temp_radius, color='g', fill=False, linestyle='--')
                zoom_ax.add_patch(temp_circle_patch)
                zoom_painter.tempCanvas.draw_idle()

    def _shapeOverlapsRegion(self, shape, x_min, x_max, y_min, y_max):
        """Check if a shape overlaps with given region (Phase 2.5)"""
        # Shape is a circle with center (x, y) and radius size
        # Check if circle center + radius overlaps with region
        shape_x = shape.x
        shape_y = shape.y
        shape_radius = shape.size

        # Simple bounding box check
        if (shape_x + shape_radius >= x_min and shape_x - shape_radius <= x_max and
            shape_y + shape_radius >= y_min and shape_y - shape_radius <= y_max):
            return True
        return False

    def _lineOverlapsRegion(self, line, x_min, x_max, y_min, y_max):
        """Check if a line profile overlaps with given region (Phase 6.5)"""
        # Simple check: if either endpoint is in the region, or if the line crosses the region
        # For simplicity, check if either endpoint is in region, or if bounding box overlaps
        start_in = (x_min <= line.start_x <= x_max and y_min <= line.start_y <= y_max)
        end_in = (x_min <= line.end_x <= x_max and y_min <= line.end_y <= y_max)

        if start_in or end_in:
            return True

        # Check if line's bounding box overlaps with region
        line_x_min = min(line.start_x, line.end_x)
        line_x_max = max(line.start_x, line.end_x)
        line_y_min = min(line.start_y, line.end_y)
        line_y_max = max(line.start_y, line.end_y)

        if (line_x_max >= x_min and line_x_min <= x_max and
            line_y_max >= y_min and line_y_min <= y_max):
            return True

        return False

    def calculateImageStatistics(self):
        """Start background calculation of image statistics (Phase 6.8)"""
        if self.fits_image.data is None:
            self._stats_label.setText("Image: --")
            return

        # Cancel existing calculation if running
        if self._stats_calculator is not None and self._stats_calculator.isRunning():
            self._stats_calculator.quit()
            self._stats_calculator.wait()

        # Show calculating message
        self._stats_label.setText("Image: calculating...")

        # Start new calculation in background thread
        self._stats_calculator = StatsCalculator(self.fits_image.data)
        self._stats_calculator.finished.connect(self._onImageStatsCalculated)
        self._stats_calculator.start()

    def _onImageStatsCalculated(self, stats):
        """Handle calculated image statistics and update status bar (Phase 6.8)"""
        try:
            # Format: "Image: μ=1234.5 σ=45.6 [1000-5000]"
            text = (f"Image: μ={stats['mean']:.1f} "
                    f"σ={stats['std']:.1f} "
                    f"[{stats['min']:.0f}-{stats['max']:.0f}]")
            self._stats_label.setText(text)

            # Update tooltip with more details
            tooltip = (f"Whole image statistics:\n"
                       f"Mean (μ): {stats['mean']:.2f}\n"
                       f"Median: {stats['median']:.2f}\n"
                       f"Std Dev (σ): {stats['std']:.2f}\n"
                       f"Min: {stats['min']:.2f}\n"
                       f"Max: {stats['max']:.2f}")
            self._stats_label.setToolTip(tooltip)
        except Exception as e:
            print(f"Error displaying image statistics: {e}")
            self._stats_label.setText("Image: error")

    def _onLinearStatsCalculated(self, stats):
        """Handle calculated linear profile statistics and update status bar (Phase 6.6)"""
        try:
            # Format: "Linear: μ=1234.5 σ=45.6 [1000-5000]"
            text = (f"Linear: μ={stats['mean']:.1f} "
                    f"σ={stats['std']:.1f} "
                    f"[{stats['min']:.0f}-{stats['max']:.0f}]")
            self._linear_stats_label.setText(text)

            # Update tooltip with more details
            tooltip = (f"Linear profile statistics:\n"
                       f"Mean (μ): {stats['mean']:.2f}\n"
                       f"Median: {stats['median']:.2f}\n"
                       f"Std Dev (σ): {stats['std']:.2f}\n"
                       f"Min: {stats['min']:.2f}\n"
                       f"Max: {stats['max']:.2f}")
            self._linear_stats_label.setToolTip(tooltip)
        except Exception as e:
            print(f"Error displaying linear profile statistics: {e}")
            self._linear_stats_label.setText("Linear: error")

    def _onRadialStatsCalculated(self, stats):
        """Handle calculated radial profile statistics and update status bar"""
        try:
            # Format: "Radial: μ=1234.5 σ=45.6 [1000-5000]"
            text = (f"Radial: μ={stats['mean']:.1f} "
                    f"σ={stats['std']:.1f} "
                    f"[{stats['min']:.0f}-{stats['max']:.0f}]")
            self._radial_stats_label.setText(text)

            # Update tooltip with more details
            tooltip = (f"Radial profile area statistics:\n"
                       f"Mean (μ): {stats['mean']:.2f}\n"
                       f"Median: {stats['median']:.2f}\n"
                       f"Std Dev (σ): {stats['std']:.2f}\n"
                       f"Min: {stats['min']:.2f}\n"
                       f"Max: {stats['max']:.2f}")
            self._radial_stats_label.setToolTip(tooltip)
        except Exception as e:
            print(f"Error displaying radial profile statistics: {e}")
            self._radial_stats_label.setText("Radial: error")

    def handleResetOptions(self):
        """Handle --reset-layout and --reset-config CLI options (Phase 6.1, 6.2)"""
        if self.tedaCommandLine.resetConfig:
            self.clearAllSettings()
            print("All configuration has been reset to defaults")
        elif self.tedaCommandLine.resetLayout:
            self.clearLayoutSettings()
            print("Window layout has been reset to defaults")

    def resetLayoutAction(self):
        """Menu action to reset layout (Phase 6.1)"""
        self.clearLayoutSettings()
        # Prevent saving settings on exit to preserve the reset
        self.tedaCommandLine.ignoreSettings = True
        QMessageBox.information(self, "Layout Reset",
                                "Window layout has been reset to defaults.\n"
                                "Please restart TeDa for changes to take effect.")

    def clearLayoutSettings(self):
        """Clear layout-specific settings (Phase 6.1)"""
        settings = QSettings()
        # Clear window geometry and state
        settings.beginGroup("MainWindow")
        settings.remove("size")
        settings.remove("pos")
        settings.endGroup()
        settings.remove("geometry")
        settings.remove("windowState")
        # Clear widget-specific layout settings
        settings.beginGroup("fileWidget")
        settings.remove("splitterGeometry")
        settings.remove("splitterState")
        settings.endGroup()

    def clearAllSettings(self):
        """Clear all configuration settings (Phase 6.2)"""
        settings = QSettings()
        settings.clear()  # Clear everything

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
    # Wrapper for QWidget to handle leave event
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

    def leaveEvent(self, e):
        self.clearFocus()

