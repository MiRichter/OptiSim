# -*- coding: utf-8 -*-

"""
Module implementing ExtractBandgapDlg.
"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog

from .Ui_extractbandgap import Ui_Dialog

import numpy as np
import scipy

class ExtractBandgapDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, wvl, k, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() |
                              Qt.WindowSystemMenuHint |
                              Qt.WindowMinMaxButtonsHint)
        
        wvl = np.array(wvl)
        k = np.array(k)
        self.eV =  1239.941 / wvl
        self.alpha = 4 * np.pi * k/ wvl  # 1/nm
        self.m = 0.5
        
        self.fit = False
        
        self.minX = np.min(self.eV)
        self.maxX = np.max(self.eV)
        
        self.minFitSlider.setRange(int(self.minX*1000), int(self.maxX*1000))
        self.minFitSlider.setValue(int(self.minX*1000))
        self.maxFitSlider.setRange(int(self.minX*1000), int(self.maxX*1000))
        self.maxFitSlider.setValue(int(self.maxX*1000))
        self.minFitSB.setRange(self.minX, self.maxX)
        self.minFitSB.setValue(self.minX)
        self.maxFitSB.setRange(self.minX, self.maxX)
        self.maxFitSB.setValue(self.maxX)
        
        self.updatePlot()
        
    def updatePlot(self):
        self.alphaM = (self.alpha*self.eV)**(1/self.m)
        curves = {'(alpha*hv)^1/{}'.format(self.m): self.alphaM}
        if self.fit:
            curves['fit'] = self.fitCurve
        self.alphaPlot.showCurves(self.eV, curves, 'energy (eV)', '(alpha*hv)^1/{}'.format(self.m), self.minX, self.maxX)
        #print('min {}, max {}'.format(self.minX, self.maxX))
    
    @pyqtSlot(int)
    def on_minFitSlider_sliderMoved(self, value):
        self.minX = float(value)/1000
        self.minFitSB.setValue(self.minX)
        self.updatePlot()
    
    @pyqtSlot()
    def on_minFitSB_editingFinished(self):
        self.minX = self.minFitSB.value()
        self.minFitSlider.setValue(int(self.minX*1000))
        self.updatePlot()
    
    @pyqtSlot(int)
    def on_maxFitSlider_sliderMoved(self, value):
        self.maxX = float(value)/1000
        self.maxFitSB.setValue(self.maxX)
        self.updatePlot()
    
        
    @pyqtSlot()
    def on_maxFitSB_editingFinished(self):
        self.maxX = self.maxFitSB.value()
        self.maxFitSlider.setValue(int(self.maxX*1000))
        self.updatePlot()
         
    @pyqtSlot(bool)
    def on_fitModeDirect_toggled(self, checked):
        self.m = 0.5
        self.updatePlot()
        
    @pyqtSlot(bool)
    def on_fitModeIndirect_toggled(self, checked):
        self.m = 2
        self.updatePlot()
        
    @pyqtSlot(bool)
    def on_fitModeForbiddenDirect_toggled(self, checked):
        self.m = 1.5
        self.updatePlot()
        
    @pyqtSlot(bool)
    def on_fitModeForbiddenIndirect_toggled(self, checked):
        self.m = 3
        self.updatePlot()
    
    @pyqtSlot(bool)
    def on_fitModeCostum_toggled(self, checked):
        self.m = self.fitModeCostumSB.value()
        self.updatePlot()
    
    @pyqtSlot()
    def on_fitModeCostumValueSB_editingFinished(self):
        self.m = self.fitModeCostumSB.value()
        self.updatePlot()
    
    @pyqtSlot()
    def on_startFit_clicked(self):
        if self.eV[1] < self.eV[0]: 
            minIdx = np.nonzero(self.eV > self.minX)[0][-1]
            maxIdx = np.nonzero(self.eV < self.maxX)[0][0]
            x = self.eV[maxIdx:minIdx+1]
            y = self.alphaM[maxIdx:minIdx+1]
        else:
            minIdx = np.nonzero(self.eV > self.minX)[0][0]
            maxIdx = np.nonzero(self.eV < self.maxX)[0][-1]
            x = self.eV[minIdx:maxIdx+1]
            y = self.alphaM[minIdx:maxIdx+1]
        #print(x)
        #print(y)
        z = np.polyfit(x, y, 1)
        
        slope = z[0]
        intersect = z[1]
        Eg = -intersect / slope
        curve = np.poly1d(z)
        
        yhat = curve(x)
        ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
        ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
        sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
        r_square = ssreg / sstot
        
        self.fit = True
        self.fitCurve = curve(self.eV)
        self.fitCurve[self.fitCurve < 0] = 0
        #self.alphaPlot.plot(x, yhat, 'fit')
        #self.alphaPlot.canvas.draw()
        self.updatePlot()
        self.textEdit.setText('Bandgap = {} eV\nR^2 = {}'.format(Eg, r_square))
       
        
