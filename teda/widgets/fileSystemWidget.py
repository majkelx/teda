from PySide2.QtCore import QDir
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QHBoxLayout, QFileSystemModel, QTreeView, QListView, QAction, QVBoxLayout, \
    QPushButton, QToolButton, QFileDialog, QSplitter

from teda.icons import IconFactory


class FileSystemWidget(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.currentRootPath = '/'
        self.currentPath = QDir.currentPath()

        self.mainWindow = parent;

        self.chooseDirAction = QAction(IconFactory.getIcon('folder'), 'Root directory', self, statusTip="Change root directory", triggered=self.chooseRootDir)
        self.showOFAction = QAction(IconFactory.getIcon('filter_alt'), 'Show only FITS files', self, statusTip="Show only FITS/all files", triggered=self.showOFFiles)
        self.showOFAction.setCheckable(True)
        self.showOFAction.toggled.connect(self.showOFFiles)

        self.chooseDirBtn = QToolButton()
        self.chooseDirBtn.setDefaultAction(self.chooseDirAction)

        self.showOFBtn = QToolButton()
        self.showOFBtn.setDefaultAction(self.showOFAction)


        iconlayout = QHBoxLayout()
        iconlayout.setAlignment(Qt.AlignLeft)
        iconlayout.addWidget(self.chooseDirBtn)
        iconlayout.addWidget(self.showOFBtn)

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
        self.filesModel.setNameFilterDisables(False)

        self.files = QListView()
        self.files.setModel(self.filesModel)
        self.files.doubleClicked.connect(self.onFilesDoubleClick)

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
            self.filesModel.setFilter(QDir.NoDot | QDir.AllEntries | QDir.DirsFirst | QDir.Type)
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
            self.mainWindow.open_fits(info.filePath())

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

    def writeSettings(self, settings):
        settings.beginGroup("fileWidget")
        settings.setValue('splitterGeometry',self.viewsSplitter.saveGeometry())
        settings.setValue('splitterState',self.viewsSplitter.saveState())
        settings.setValue('rootPath',self.currentRootPath)
        settings.setValue('path',self.currentPath)
        settings.endGroup()

    def readSettings(self, settings):
        settings.beginGroup("fileWidget")
        self.viewsSplitter.restoreGeometry(settings.value("splitterGeometry"))
        self.viewsSplitter.restoreState(settings.value("splitterState"))
        rootPath = settings.value("rootPath")
        path = settings.value("path")
        settings.endGroup()

        if rootPath is None:
            rootPath = '/'
        self.setRootPath(rootPath)

        if path is None:
            path = QDir.currentPath()
        self.setPath(path)

        self.splitterMoved(self.viewsSplitter.handle(1).pos().x(), 0)

