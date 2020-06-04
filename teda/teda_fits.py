#!/usr/bin/env python
"""
TeDa FITS Viewer application

by Akond Lab
"""
from PySide2.QtWidgets import QApplication
from teda.viewer_mainwindow import MainWindow


def main():
    import sys

    app = QApplication(sys.argv)
    QApplication.setOrganizationName('Akond Lab')
    QApplication.setOrganizationDomain('akond.com')
    QApplication.setApplicationName('TeDa FITS Viewer')
    mainWin = MainWindow()
    # mainWin.resize(800, 600)   # now in config, see: MainWindow.readWindowSettings
    mainWin.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
