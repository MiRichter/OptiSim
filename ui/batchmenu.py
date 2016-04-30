# -*- coding: utf-8 -*-

"""
Module implementing BatchDlg.
"""

from PyQt5.QtCore import pyqtSlot,  Qt
from PyQt5.QtWidgets import QMessageBox, QDialog, QDoubleSpinBox, QLineEdit, QPushButton, QFileDialog, QComboBox

from .Ui_batchmenu import Ui_Dialog


class BatchDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, stack, batchVariables = [], parent=None):
        """
        batch menu opens as follows
        
        material
            which 
                thickness
                constant n
                constant k
                roughness thickness
                haze
                
        stack
            excitation
                angle of incidence
            
            
        batchVariables is structured as nested list for each variation with each three entries
            i) int 0 - material, 1 - stack
            ii) name of material layer or stack category
            iii) variable name as shown above
            iv) list of start, step, stop value
            
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.layers = []
        for layer in stack:
            self.layers.append(layer.name)
            
        self.materialParameters = ['thickness', 'constant n', 'constant k', 'roughness', 'haze', 'diffusion length']
        self.stackParameters = ['angle of incidence']
       
        self.variables = batchVariables.copy()
        self.variableNumberSB.setValue(len(self.variables))
        self.updateLayout()

        
        self.buttonBox.accepted.connect(self.checkInput)

    def updateLayout(self):
        self.updating = True
        for i in reversed(range(self.variableLayout.count())):
            if i > 1:
                self.variableLayout.itemAt(i).widget().deleteLater()

        for i, variable in enumerate(self.variables):
            self.currentVariable = i
            Cat1 = QComboBox()
            Cat1.addItems(['material', 'stack'])
            Cat1.setCurrentIndex(variable[0])
            Cat1.currentIndexChanged.connect(self.cat1Changed)
            
            Cat2 = QComboBox()
            if variable[0] == 0:
                Cat2.addItems(self.layers)
            else:
                Cat2.addItems(['excitation'])
            Cat2.currentIndexChanged.connect(self.cat2Changed)
                
            idx = Cat2.findText(variable[1])
            if idx >= 0:
                Cat2.setCurrentIndex(idx)
            else:
                Cat2.setCurrentIndex(0)
                self.variables[i][1] = Cat2.currentText()

            Cat3 = QComboBox()
            if variable[0] == 0:
                Cat3.addItems(self.materialParameters)
            else:
                Cat3.addItems(self.stackParameters)

            Cat3.currentIndexChanged.connect(self.cat3Changed)
            idx = Cat3.findText(variable[2])
            if idx >= 0:
                Cat3.setCurrentIndex(idx)
            else:
                Cat3.setCurrentIndex(0)
                self.variables[i][2] = Cat3.currentText()
            
            startSB = QDoubleSpinBox()
            stepSB = QDoubleSpinBox()
            stopSB = QDoubleSpinBox()
            
            if variable[2] == 'thickness' or variable[2] == 'roughness':
                startSB.setRange(1.0, 9998.0)
                startSB.setSingleStep(1)
                stepSB.setRange(1.0, 9998.0)
                stepSB.setSingleStep(1.0)
                stopSB.setRange(2.0, 9999.0)
                stopSB.setSingleStep(1.0)
            elif variable[2] == 'constant n' or variable[2] == 'constant k':
                startSB.setRange(0.0, 20.0)
                startSB.setSingleStep(0.1)
                stepSB.setRange(0.01, 1.0)
                stepSB.setSingleStep(0.01)
                stopSB.setRange(0.01, 20.0)
                stopSB.setSingleStep(0.01)
            elif variable[2] == 'haze':
                startSB.setRange(0.0, 1.0)
                startSB.setSingleStep(1)
                stepSB.setRange(0.01, 1.0)
                stepSB.setSingleStep(1.0)
                stopSB.setRange(0.01, 1.0)
                stopSB.setSingleStep(0.01)
            elif variable[2] == 'angle of incident':
                startSB.setRange(0.0, 89.0)
                startSB.setSingleStep(1)
                stepSB.setRange(1.0, 90.0)
                stepSB.setSingleStep(1)
                stopSB.setRange(2.0, 90.0)
                stopSB.setSingleStep(1.0)
            else:
                startSB.setRange(0.0, 999999)
                startSB.setSingleStep(1)
                stepSB.setRange(1.0, 999999)
                stepSB.setSingleStep(1)
                stopSB.setRange(0.000001, 999999)
                stopSB.setSingleStep(1.0)
            startSB.setValue(variable[3][0])
            stepSB.setValue(variable[3][1])
            stopSB.setValue(variable[3][2])
            startSB.valueChanged.connect(self.startSBChanged)
            stepSB.valueChanged.connect(self.stepSBChanged)
            stopSB.valueChanged.connect(self.stopSBChanged)           
            stopSB.setValue(variable[3][2])
            
            self.variableLayout.addWidget(Cat1, i+1, 0)
            self.variableLayout.addWidget(Cat2, i+1, 1)
            self.variableLayout.addWidget(Cat3, i+1, 2)
            self.variableLayout.addWidget(startSB, i+1, 3)
            self.variableLayout.addWidget(stepSB, i+1, 4)
            self.variableLayout.addWidget(stopSB, i+1, 5)
        self.updating = False
        
        
    @pyqtSlot(int)
    def cat1Changed(self, i):
        self.variables[self.currentVariable][0] = i
        self.updateLayout()
    
    @pyqtSlot(int)
    def cat2Changed(self, i):
        if not self.updating:
            if self.variables[self.currentVariable][0] == 0:
                self.variables[self.currentVariable][1] = self.layers[i]
            else:
                self.variables[self.currentVariable][1] = 'excitation'
        
            self.updateLayout()
    
    @pyqtSlot(int)
    def cat3Changed(self, i):
        if not self.updating:
            if self.variables[self.currentVariable][0] == 0:
                self.variables[self.currentVariable][2] = self.materialParameters[i]
            else:
                self.variables[self.currentVariable][2] = self.stackParameters[i]
            
            parameter = self.variables[self.currentVariable][2]
            
            if parameter == 'thickness' or parameter == 'roughness':
                range = [100, 10, 200]
            elif parameter == 'constant n' or parameter == 'constant k':
                range = [1, 0.1, 2]
            elif parameter == 'haze':
                range = [0, 0.1, 1]
            elif parameter == 'angle of incidence':
                range = [0, 10, 90]
            else:
                range = [0, 1, 0.1]
            self.variables[self.currentVariable][3] = range
            
            self.updateLayout()
        
    def startSBChanged(self, p0):
        self.variables[self.currentVariable][3][0] = p0
    def stepSBChanged(self, p0):
        self.variables[self.currentVariable][3][1] = p0
    def stopSBChanged(self, p0):
        self.variables[self.currentVariable][3][2] = p0
        
    @pyqtSlot(int)
    def on_variableNumberSB_valueChanged(self, p0):
        if p0 > len(self.variables):
            self.variables.append([0, self.layers[0], 'thickness', [100, 10, 200]])
            self.updateLayout()
        elif p0 < len(self.variables):
            self.variables.pop(p0)
            self.updateLayout()


    def checkInput(self):
        pass
