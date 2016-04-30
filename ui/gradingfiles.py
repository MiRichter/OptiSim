# -*- coding: utf-8 -*-

"""
Module implementing GradingFiles.
"""
import os
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QMessageBox, QDialog, QDoubleSpinBox, QLineEdit, QPushButton, QFileDialog

from .Ui_gradingfiles import Ui_Dialog

import numpy as np

class GradingFilesDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, files, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.files = files.copy()   # [xMole, Eg, FilePath] 
        self.fileNumberSB.setValue(len(self.files))
        self.updateLayout()
        
        #self.buttonBox.accepted.connect(self.accept)

    def updateLayout(self):
        self.updating = True
        for i in reversed(range(self.fileLayout.count())):
            if i > 2:
                self.fileLayout.itemAt(i).widget().deleteLater()

        for i, file in enumerate(self.files):
            SB = QDoubleSpinBox()
            SB.setValue(file[0])
            SB.setRange(0.0, 1.0)
            SB.setSingleStep(0.1)
            SB.valueChanged.connect(self.updateFiles)
            SBEg = QDoubleSpinBox()
            SBEg.setValue(file[1])
            SBEg.setRange(0.1, 9.9)
            SBEg.setSingleStep(0.1)
            SBEg.valueChanged.connect(self.updateFiles)
            LE = QLineEdit(file[2])
            LE.textChanged.connect(self.updateFiles)
            PB = QPushButton('load')
            PB.clicked.connect(self.selectPath)
            self.fileLayout.addWidget(SB, i+1, 0)
            self.fileLayout.addWidget(SBEg, i+1, 1)
            self.fileLayout.addWidget(LE, i+1, 2)
            self.fileLayout.addWidget(PB, i+1, 3)
        self.updating = False


    def updateFiles(self):
        if not self.updating:
            for row in range(len(self.files)):
                self.files[row][0] = self.fileLayout.itemAtPosition(row+1, 0).widget().value() # xMole
                self.files[row][1] = self.fileLayout.itemAtPosition(row+1, 1).widget().value() # Eg
                self.files[row][2] = self.fileLayout.itemAtPosition(row+1, 2).widget().text() # FilePath

    @pyqtSlot(int)
    def on_fileNumberSB_valueChanged(self, p0):
        if p0 > len(self.files):
            self.files.append([0, 1, ''])
            self.updateLayout()
        elif p0 < len(self.files):
            self.files.pop(p0)
            self.updateLayout()

    def selectPath(self):
        fileName,  _= QFileDialog.getOpenFileName(self, 'select a file containing the nk data', os.getcwd()+'\\materialDB')
        if fileName:
            PB = self.sender()
            idx = self.fileLayout.indexOf(PB)
            self.fileLayout.itemAt(idx-1).widget().setText(fileName)

    
    # overwrite dialog's accept method
    def accept(self):
        xMoles = [x[0] for x in self.files]
        files = [x[2] for x in self.files]
        if not np.unique(xMoles).size == len(xMoles):
            QMessageBox.warning(self,
                "Warning","There are repeating xMole values",
                QMessageBox.StandardButtons(
                QMessageBox.Ok))
            return
        doubleFiles = list(set([x for x in files if files.count(x) > 1]))
        if doubleFiles:
            QMessageBox.warning(self,
                "Warning","There are repeating files",
                QMessageBox.StandardButtons(
                QMessageBox.Ok))
            return
        QDialog.accept(self)
