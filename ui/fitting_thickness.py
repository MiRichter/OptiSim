# -*- coding: utf-8 -*-

"""
Module implementing FittingThicknessDlg.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .Ui_fitting_thickness import Ui_Dialog


class FittingThicknessDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, stack, references, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.layers = []
        for layer in stack:
            self.layers.append(layer.name)
        
        self.references = []
        for key, value in references.items():
            if value[0]:
                self.references.append(key)
        
        methods = ['Nelder-Mead', 'Powell', 'CG', 'BFGS', 'L-BFGS-B', 'TNC', 'COBYLA', 'SLSQP']
         # with Jacobian necessary: 'Newton-CG', 'dogleg',  'trust-ncg'
        self.method = methods[0]
        
        self.layersCB.addItems(self.layers)
        self.referencesCB.addItems(self.references)
        self.methodCB.addItems(methods)
        self.methodCB.setCurrentIndex(0)
        self.selectedLayer = 0
        self.selectedReference = self.references[0]
        self.noOfIterations = 100
        self.noOfIterationsSB.setValue(self.noOfIterations)
        
    @pyqtSlot(int)
    def on_layersCB_currentIndexChanged(self, p0):
        self.selectedLayer = p0
    
    @pyqtSlot(str)
    def on_referencesCB_currentIndexChanged(self, p0):
        self.selectedReference = p0
        #print(p0)
    
    @pyqtSlot(int)
    def on_noOfIterationsSB_valueChanged(self, p0):
        self.noOfIterations = p0
    
    @pyqtSlot(str)
    def on_methodCB_currentIndexChanged(self, p0):
       self.method = p0
