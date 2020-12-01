from os import path
import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QHBoxLayout, QStackedLayout, QLabel, QFormLayout, QLineEdit, QAction, \
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QMenu

import numpy as np

from astwro.starlist import StarList
from astwro.starlist.ds9 import write_ds9_regions, read_ds9_regions
from astwro.starlist import read_dao_file, write_dao_file


class RegionsWidget(QWidget):

    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainwindow = mainwindow

        self.loadAction = QAction('Load Regions File', self,
                                     statusTip="Load Regions File",
                                     triggered=self.loadRegionsMethod)
        self.addAction(self.loadAction)

        self.Loadbutton = QPushButton("&Load Regions File", self)
        self.Loadbutton.clicked.connect(self.loadRegionsMethod)

        self.saveAction = QAction('Save Regions File', self,
                                  statusTip="Save Regions File",
                                  triggered=self.loadRegionsMethod)
        self.addAction(self.saveAction)

        self.savebutton = QPushButton("&Save Regions", self)
        self.savebutton.clicked.connect(self.saveRegionsMethod)


        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        layout.addRow(self.Loadbutton,self.savebutton)
        self.setLayout(layout)
        self.formlayout = layout

        self.groupTable = groupTableWidget(self)
        self.groupTable.setColumnCount(2)
        self.groupTable.setHorizontalHeaderItem(0, QTableWidgetItem("Group"))
        self.groupTable.setHorizontalHeaderItem(1, QTableWidgetItem("Count"))
        self.groupTable.horizontalHeader().setStretchLastSection(1)
        self.groupTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.groupTable.clearFocus()

        layout.addRow(self.groupTable)

        self.reverseAction = QAction('Reverse Selection', self,
                                  statusTip="Reverse Selection",
                                  triggered=self.reversSeclection)
        self.addAction(self.reverseAction)

        self.reversebutton = QPushButton("&Reverse Selection", self)
        self.reversebutton.clicked.connect(self.reversSeclection)

        layout.addRow(self.reversebutton)

    def selectGroup(self,row,col):
        val = self.groupTable.item(row,col)
        group = self.mainwindow.painterComponent.region_groups[row]
        self.mainwindow.painterComponent.selectGroup(group, axies=self.mainwindow.central_widget.figure.axes[0])

    def deselectGroup(self,row,col):
        val = self.groupTable.item(row,col)
        group = self.mainwindow.painterComponent.region_groups[row]
        self.mainwindow.painterComponent.deselectGroup(group, axies=self.mainwindow.central_widget.figure.axes[0])

    def activateGroup(self,row,col):
        self.mainwindow.painterComponent.setActiveGroup(row)

    def deleteGroup(self,row,col):
        #group = self.mainwindow.painterComponent.region_groups[row]
        self.mainwindow.painterComponent.deleteGroup(row, axies=self.mainwindow.central_widget.figure.axes[0])
        self.updateRegionList()

    def reversSeclection(self):
        self.mainwindow.painterComponent.reverseSelection(axies=self.mainwindow.central_widget.figure.axes[0])

    def updateRegionList(self):
        pos = 0
        toDelete=  []
        self.groupTable.setRowCount(0)
        for reg in self.mainwindow.painterComponent.region_groups:
            if self.mainwindow.painterComponent.getGroupCount(reg)>0:
                self.groupTable.insertRow(pos)
                newKeyItem = QTableWidgetItem()
                newKeyItem.setText(reg.name)
                newValItem = QTableWidgetItem()
                newValItem.setText(str(self.mainwindow.painterComponent.getGroupCount(reg)))
                self.groupTable.setItem(pos, 0, newKeyItem)
                self.groupTable.setItem(pos, 1, newValItem)
                pos += 1
            else:
                toDelete.append(reg)

        for grp in toDelete:
            index = -1
            for reg in self.mainwindow.painterComponent.region_groups:
                index += 1
                if grp is reg:
                    self.mainwindow.painterComponent.deleteGroup(index, axies=self.mainwindow.central_widget.figure.axes[0])

        self.groupTable.resizeRowsToContents()
        self.groupTable.verticalHeader().hide()


    def loadRegionsMethod(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open region file", ".", "Region files (*.reg *.lst *.ap *.coo *.als *.xy)")
        #self.parseRawRegions(1)
        if fileName:
            self.mainwindow.painterComponent.read_regions_file(fileName, axies=self.mainwindow.central_widget.figure.axes[0])
            self.updateRegionList()

    def saveRegionsMethod(self):
        if len(self.mainwindow.painterComponent.region_groups) > 0:
            dialog = QFileDialog.getSaveFileName(self, "Save Regions...", os.path.splitext(self.mainwindow.filename)[0], "reg (*.reg);;lst (*.lst);;ap (*.ap);;coo (*.coo);;als (*.als);;xy (*.xy)")
            if dialog[0] != "":
                save = True

    def parseRawRegions(self,rawfile):
        self.mainwindow.painterComponent.add(50, 50)

class groupTableWidget(QTableWidget):

    def __init__(self, parent = None):
        QTableWidget.__init__(self, parent)
        self.parent = parent


    def contextMenuEvent(self, event):
        if self.selectionModel().selection().indexes():
            for i in self.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QMenu(self)
            sel = menu.addAction("Select")
            desel = menu.addAction("Deselect")
            activate = menu.addAction("Make active")
            delete = menu.addAction("Delete group")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == sel:
                self.parent.selectGroup(row, column)
            if action == desel:
                self.parent.deselectGroup(row, column)
            if action == activate:
                self.parent.activateGroup(row, column)
            if action == delete:
                self.parent.deleteGroup(row, column)


    def leaveEvent(self, e):
        self.clearFocus()