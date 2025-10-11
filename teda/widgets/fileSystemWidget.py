from PySide6.QtCore import QDir
from PySide6.QtGui import Qt, QAction
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileSystemModel, QTreeView, QListView, QVBoxLayout, \
    QPushButton, QToolButton, QFileDialog, QSplitter, QApplication, QMenu

from teda.icons import IconFactory


class FileSystemWidget(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.currentRootPath = '/'
        self.currentPath = QDir.currentPath()

        self.mainWindow = parent

        self.chooseDirAction = QAction(IconFactory.getIcon('folder'), 'Root directory', self, statusTip="Change root directory", triggered=self.chooseRootDir)

        self.showOFAction = QAction(IconFactory.getIcon('filter_alt'), 'Show only FITS files', self, statusTip="Show only FITS/all files", triggered=self.showOFFiles)
        self.showOFAction.setCheckable(True)
        # self.showOFAction.toggled.connect(self.showOFFiles)

        self.refreshFilesAction = QAction(IconFactory.getIcon('refresh'), 'Auto-refresh files', self, statusTip="Auto-refresh on new files", triggered=self.refreshFiles)
        self.refreshFilesAction.setCheckable(True)

        self.sortFilesAction = QAction(IconFactory.getIcon('sort'), 'Reverse file sort', self, statusTip="Ascending/Descending sort of files (by name)", triggered=self.sortFiles)
        self.sortFilesAction.setCheckable(True)

        self.chooseDirBtn = QToolButton()
        self.chooseDirBtn.setDefaultAction(self.chooseDirAction)

        self.showOFBtn = QToolButton()
        self.showOFBtn.setDefaultAction(self.showOFAction)

        self.refreshFilesBtn = QToolButton()
        self.refreshFilesBtn.setDefaultAction(self.refreshFilesAction)

        self.sortFilesBtn = QToolButton()
        self.sortFilesBtn.setDefaultAction(self.sortFilesAction)

        iconlayout = QHBoxLayout()
        iconlayout.setAlignment(Qt.AlignLeft)
        iconlayout.addWidget(self.chooseDirBtn)
        iconlayout.addWidget(self.showOFBtn)
        iconlayout.addWidget(self.refreshFilesBtn)
        iconlayout.addWidget(self.sortFilesBtn)

        self.viewsSplitter = QSplitter(Qt.Horizontal)
        self.viewsSplitter.splitterMoved.connect(self.splitterMoved)

        self.dirsModel = QFileSystemModel(self)
        self.dirsModel.setOption(QFileSystemModel.DontWatchForChanges, True)
        self.dirsModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dirsModel.setNameFilterDisables(False)

        self.dirs = QTreeView()
        self.dirs.setModel(self.dirsModel)
        self.dirs.hideColumn(1); self.dirs.hideColumn(2); self.dirs.hideColumn(3)

        self.dirs.clicked.connect(self.onDirsClick)
        self.dirs.doubleClicked.connect(self.onDirsDoubleClick)

        self.filesModel = QFileSystemModel(self)
        self.filesModel.setOption(QFileSystemModel.DontWatchForChanges, True)
        self.filesModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.filesModel.sort(0, Qt.AscendingOrder)
        self.filesModel.setNameFilterDisables(False)

        self.files = QListView()
        self.files.setModel(self.filesModel)
        self.files.doubleClicked.connect(self.onFilesDoubleClick)
        # Enable context menu for file browser (Phase 6.10)
        self.files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files.customContextMenuRequested.connect(self.onFilesContextMenu)

        self.viewsSplitter.addWidget(self.dirs)
        self.viewsSplitter.addWidget(self.files)
        viewslayout = QHBoxLayout()
        viewslayout.addWidget(self.viewsSplitter)

        layout = QVBoxLayout()
        layout.addLayout(iconlayout)
        layout.addLayout(viewslayout)

        self.setLayout(layout)

        self.dirsModel.setRootPath(self.currentRootPath);
        self.dirs.setRootIndex(self.dirsModel.index(self.currentRootPath))

        index = self.dirsModel.index(self.currentPath)
        self.dirs.setCurrentIndex(index)
        self.dirs.setExpanded(index, True)

        self.filesModel.setRootPath(self.currentPath);
        self.files.setRootIndex(self.filesModel.index(self.currentPath))

    def splitterMoved(self, pos, index):
        if pos == 0:
            self.filesModel.setFilter(QDir.NoDot | QDir.AllEntries) # | QDir.DirsFirst | QDir.Type)
        elif pos == self.viewsSplitter.width()-self.viewsSplitter.handleWidth():
            self.dirsModel.setFilter(QDir.NoDotAndDotDot|QDir.AllEntries)
        else:
            self.dirsModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.filesModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)

    def onDirsClick(self, item):
        index = self.dirs.selectedIndexes()[0]
        info = self.dirsModel.fileInfo(index)
        if info.isDir():
            self.currentPath = info.filePath()
            self.files.setRootIndex(self.filesModel.setRootPath(info.filePath()))

    def onDirsDoubleClick(self, item):
        index = self.dirs.selectedIndexes()[0]
        info = self.dirsModel.fileInfo(index)
        if info.isDir():
            self.currentPath = info.filePath()
            self.files.setRootIndex(self.filesModel.setRootPath(info.filePath()))
        else:
            self.mainWindow.open_fits(info.filePath())

    def onFilesDoubleClick(self, item):
        index = self.files.selectedIndexes()[0]
        info = self.filesModel.fileInfo(index)
        if info.isDir():
            self.setPath(info.filePath())
        else:
            try:
                self.mainWindow.open_fits(info.filePath())
            except FileNotFoundError:
                self.setPath(self.currentPath) # refesh maybe?

    def onFilesContextMenu(self, position):
        """Context menu for file browser - copy file path (Phase 6.10)"""
        # Get the index at the cursor position
        index = self.files.indexAt(position)
        if not index.isValid():
            return  # No item under cursor

        # Get file info
        info = self.filesModel.fileInfo(index)

        # Create context menu
        menu = QMenu(self)
        copy_path_action = menu.addAction("Copy Path")

        # Show menu and get selected action
        action = menu.exec_(self.files.viewport().mapToGlobal(position))

        # Handle action
        if action == copy_path_action:
            file_path = info.filePath()
            QApplication.clipboard().setText(file_path)

    def setPath(self, path):
        self.currentPath = path

        index = self.dirsModel.index(self.currentPath)
        self.dirs.setCurrentIndex(index)
        self.dirs.setExpanded(index, True)

        self.files.setRootIndex(self.filesModel.setRootPath(self.currentPath))

    def chooseRootDir(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select directory')
        if dir:
            self.setRootPath(dir);

    def setRootPath(self, dir):
        self.currentRootPath = dir

        self.dirsModel.setRootPath(self.currentRootPath)
        self.dirs.setRootIndex(self.dirsModel.index(self.currentRootPath))

        self.setPath(self.currentRootPath)

    def showOFFiles(self):
        if self.showOFAction.isChecked():
            self.dirsModel.setNameFilters(["*.FITS", "*.fits"])
            self.filesModel.setNameFilters(["*.FITS", "*.fits"])
        else:
            self.dirsModel.setNameFilters(["*"])
            self.filesModel.setNameFilters(["*"])

    def refreshFiles(self):
        if self.refreshFilesAction.isChecked():
            self.filesModel.setOption(QFileSystemModel.DontWatchForChanges, False)
        else:
            self.filesModel.setOption(QFileSystemModel.DontWatchForChanges, True)

    def sortFiles(self):
        if self.sortFilesAction.isChecked():
            self.filesModel.sort(0, Qt.DescendingOrder)
        else:
            self.filesModel.sort(0, Qt.AscendingOrder)

    def writeSettings(self, settings):
        settings.beginGroup("fileWidget")
        settings.setValue('splitterGeometry',self.viewsSplitter.saveGeometry())
        settings.setValue('splitterState',self.viewsSplitter.saveState())
        settings.setValue('rootPath',self.currentRootPath)
        settings.setValue('path',self.currentPath)
        settings.setValue('showOF',self.showOFAction.isChecked())
        settings.setValue('refresh',self.refreshFilesAction.isChecked())
        settings.setValue('sort',self.sortFilesAction.isChecked())
        settings.endGroup()

    def readSettings(self, settings):
        settings.beginGroup("fileWidget")
        self.viewsSplitter.restoreGeometry(settings.value("splitterGeometry"))
        self.viewsSplitter.restoreState(settings.value("splitterState"))
        rootPath = settings.value("rootPath")
        path = settings.value("path")
        self.showOFAction.setChecked(settings.value("showOF") == True)
        self.refreshFilesAction.setChecked(settings.value("refresh") == True)
        self.sortFilesAction.setChecked(settings.value("sort") == True)
        settings.endGroup()

        if rootPath is None:
            rootPath = '/'
        self.setRootPath(rootPath)

        if path is None:
            path = QDir.currentPath()
        self.setPath(path)

        self.splitterMoved(self.viewsSplitter.handle(1).pos().x(), 0)

        self.showOFFiles()
        self.refreshFiles()
        self.sortFiles()

