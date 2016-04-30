# -*- coding: utf-8 -*-

"""
Module implementing ReferencesDlg.
"""
import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog

from .Ui_references import Ui_Dialog


class ReferencesDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, references, parent=None):
        """
        Constructor
        
        class to edit the pathes to the specific reference files
        R reference
        T reference
        EQE reference
        psi reference
        delta reference
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.references = references.copy()
        
        self.R_LE.setText(self.references['R reference'][0]) 
        self.T_LE.setText(self.references['T reference'][0]) 
        self.EQE_LE.setText(self.references['EQE reference'][0]) 
        self.psi_LE.setText(self.references['psi reference'][0]) 
        self.delta_LE.setText(self.references['delta reference'][0])
        
        self.R_CB.setChecked(self.references['R reference'][1]) 
        self.T_CB.setChecked(self.references['T reference'][1]) 
        self.EQE_CB.setChecked(self.references['EQE reference'][1]) 
        self.psi_CB.setChecked(self.references['psi reference'][1]) 
        self.delta_CB.setChecked(self.references['delta reference'][1])
        

    @pyqtSlot()
    def on_R_PB_clicked(self):
        fileName,  _ = QFileDialog.getOpenFileName(self, 'select a file with reflection data', os.getcwd()+'\\references')
        if fileName:
            self.R_LE.setText(fileName)

    @pyqtSlot()
    def on_T_PB_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'select a file with transmission data', os.getcwd()+'\\references')
        if fileName:
            self.T_LE.setText(fileName)

    @pyqtSlot()
    def on_EQE_PB_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'select a file with EQE data', os.getcwd()+'\\references')
        if fileName:
            self.EQE_LE.setText(fileName)

    @pyqtSlot()
    def on_psi_PB_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'select a file with psi data', os.getcwd()+'\\references')
        if fileName:
            self.psi_LE.setText(fileName)

    @pyqtSlot()
    def on_delta_PB_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'select a file with delta data', os.getcwd()+'\\references')
        if fileName:
            self.delta_LE.setText(fileName)

    @pyqtSlot()
    def accept(self):
        self.references['R reference'] = [self.R_LE.text(), self.R_CB.isChecked()]
        self.references['T reference'] = [self.T_LE.text(), self.T_CB.isChecked()]
        self.references['EQE reference'] = [self.EQE_LE.text(), self.EQE_CB.isChecked()]
        self.references['psi reference'] = [self.psi_LE.text(), self.psi_CB.isChecked()]
        self.references['delta reference'] = [self.delta_LE.text(), self.delta_CB.isChecked()]
        
        QDialog.accept(self)
