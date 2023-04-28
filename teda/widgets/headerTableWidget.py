from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QMenu)
from PySide6.QtGui import (QIcon)
import PySide6

from teda.icons import IconFactory

class HeaderTableWidget(QTableWidget):

    def __init__(self, parent = None):
        QTableWidget.__init__(self, parent)
        self.pinnedItems = []
        self.parent = parent


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

        color = PySide6.QtGui.QColor(200, 220, 200)
        if bool(pin):
            # newKeyItem.setIcon(QIcon.fromTheme('emblem-important'));
            newKeyItem.setIcon(IconFactory.getIcon('push_pin'))
            newKeyItem.setBackground(color)
            newValItem.setBackground(color)
        self.insertRow(pos)
        self.setItem(pos, 0, newKeyItem)
        self.setItem(pos, 1, newValItem)

    def setHeader(self):
        header = self.parent.fits_image.header
        if header is None:
            return
        self.setRowCount(0)
        pos = 0
        for key in self.pinnedItems :
            try:
                value = str(header[key])
            except KeyError:
                value = "---- NOT FOUND ----"
            self.createRow(pos, key, value, bool(1))
            pos += 1

        if header is not None:
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

    def leaveEvent(self, e):
        self.clearFocus()