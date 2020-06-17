from PySide2.QtCore import QDir
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QHBoxLayout, QFileSystemModel, QTreeView, QListView, QAction, QVBoxLayout, \
    QPushButton, QToolButton, QFileDialog

from teda.icons import IconFactory


class FileSystemWidget(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.currentRootPath = '/'

        self.mainWindow = parent;

        self.chooseDirAction = QAction(IconFactory.getIcon('play_circle_outline'), 'Root dir', self, statusTip="Root directory", triggered=self.chooseRootDir)
        self.showAllAction = QAction(IconFactory.getIcon('play_circle_outline'), 'Show all', self, statusTip="Show all/only FITS files", triggered=self.showAllFiles)

        self.chooseDirBtn = QToolButton()
        self.chooseDirBtn.setDefaultAction(self.chooseDirAction)

        self.showAllBtn = QToolButton()
        self.showAllBtn.setDefaultAction(self.showAllAction)

        iconlayout = QHBoxLayout()
        iconlayout.setAlignment(Qt.AlignLeft)
        iconlayout.addWidget(self.chooseDirBtn)
        iconlayout.addWidget(self.showAllBtn)

        viewslayout = QHBoxLayout()

        self.dirModel = QFileSystemModel(self)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dirModel.setRootPath(self.currentRootPath);

        self.tree = QTreeView()
        self.tree.setModel(self.dirModel)
        self.tree.hideColumn(1); self.tree.hideColumn(2); self.tree.hideColumn(3)
        self.tree.setRootIndex(self.dirModel.index(self.currentRootPath))

        index = self.dirModel.index(QDir.currentPath())
        self.tree.setCurrentIndex(index)
        self.tree.setExpanded(index, True)

        self.tree.clicked.connect(self.onDirChange)

        self.filesModel = QFileSystemModel(self)
        self.filesModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)

        self.filesModel.setRootPath(QDir.currentPath());

        self.files = QListView()
        self.files.setModel(self.filesModel)
        self.files.setRootIndex(self.filesModel.index(QDir.currentPath()))
        self.files.doubleClicked.connect(self.onChooseFile)

        viewslayout.addWidget(self.tree)
        viewslayout.addWidget(self.files)

        layout = QVBoxLayout()
        layout.addLayout(iconlayout)
        layout.addLayout(viewslayout)

        self.setLayout(layout)

    def onDirChange(self, item):
        index = self.tree.selectedIndexes()[0]
        path = self.dirModel.filePath(index)
        self.files.setRootIndex(self.filesModel.setRootPath(path))

    def onChooseFile(self, item):
        index = self.files.selectedIndexes()[0]
        path = self.filesModel.filePath(index)
        self.mainWindow.open_fits(path)

    def chooseRootDir(self):
        fileName = QFileDialog.getExistingDirectory(self, 'Select directory')
        if fileName:
            self.setRootPath(fileName);

    def setRootPath(self, fileName):
        self.currentRootPath = fileName
        self.dirModel.setRootPath(fileName)
        self.tree.setRootIndex(self.dirModel.index(fileName))

        self.filesModel.setRootPath(fileName)
        self.files.setRootIndex(self.filesModel.index(fileName))

    def showAllFiles(self):
        pass