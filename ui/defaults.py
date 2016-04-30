# -*- coding: utf-8 -*-

"""
Module implementing DefaultsDlg.
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QStandardItemModel, QStandardItem

from .Ui_defaults import Ui_Dialog


class DefaultsDlg(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, defaults, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.defaults = defaults
        
        self.fillScalars()
        self.fillPlots()
        self.fillCalculations()
        
    def updateDefaults(self):
        self.defaults['defaultScalars'] = self.setDefaultScalars()
        self.defaults['defaultPlots'] = self.setDefaultPlots()
        self.defaults['defaultCalculations'] = self.setDefaultCalculations()
        
    def fillScalars(self):
        scalars = [ 'absorbance (%)', 
                    'reflectance (%)', 
                    'transmittance (%)',
                    'absorbance (mA/cm²)',
                    'reflectance (mA/cm²)', 
                    'transmittance (mA/cm²)',
                    'generation',
                    'Jmax (mA/cm²)',
                    'absorption layerwise (%)',
                    'absorption layerwise (mA/cm²)', 
                    'collection layerwise (%)',
                    'collection layerwise (mA/cm²)', 
                    'calc. time (s)'
                    ]
                    
        self.scalarListModel = QStandardItemModel()
        scalarsToShow = self.defaults['defaultScalars']
        for value in scalars:                   
            item = QStandardItem(value)
            check = Qt.Checked if value in scalarsToShow else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            self.scalarListModel.appendRow(item)
    
        self.scalarListView.setModel(self.scalarListModel)
        
    def setDefaultScalars(self):
        setVisible = []
        for row in range(self.scalarListModel.rowCount()):
            item = self.scalarListModel.item(row)                  
            if item.checkState() == Qt.Checked:
                setVisible.append(item.text())
                
        return setVisible
        
        
    def fillPlots(self):
        plots = [   'total A,R,T',              # requires calc [0]
                    'Ellipsometry',               # requires nothing
                    'absorption (layerwise)',   # requires calc [2]
                    'collection (layerwise)',   # requires calc [2]
                    'QE',                       # requires calc [2]
                    'reflection (interfacewise)', 
                    'generation'                # requires calc [3]
                    
                    
                ]
                    
        self.plotListModel = QStandardItemModel()
        plotsToShow = self.defaults['defaultPlots']
        for value in plots:                   
            item = QStandardItem(value)
            check = Qt.Checked if value in plotsToShow else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            self.plotListModel.appendRow(item)
    
        self.plotListView.setModel(self.plotListModel)
        
    def setDefaultPlots(self):
        setVisible = []
        for row in range(self.plotListModel.rowCount()):
            item = self.plotListModel.item(row)                  
            if item.checkState() == Qt.Checked:
                setVisible.append(item.text())
                
        return setVisible
                
    def fillCalculations(self):
        self.calculations = ['Stack optics (A,R,T)',
                        'Ellipsometry', 
                        'Field intensity',
                        'Layerwise optics (absorption, collection, QE)', 
                        'Generation'
                        ]
                    
        self.calcListModel = QStandardItemModel()
        calculationsToShow = self.defaults['defaultCalculations']
        for value in self.calculations:                   
            item = QStandardItem(value)
            check = Qt.Checked if value in calculationsToShow else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            #item.setEnabled(False)
            self.calcListModel.appendRow(item)
    
        self.calculationsListView.setModel(self.calcListModel)
        
    def setDefaultCalculations(self):
        for row in range(self.calcListModel.rowCount()):
            item = self.calcListModel.item(row)                  
            if item.checkState() == Qt.Checked:
                highestRow = row 
                
                
        setCalcOn = self.calculations[:highestRow+1]
                
        return setCalcOn
