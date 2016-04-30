# -*- coding: utf-8 -*-

"""
Module implementing ConfigTableViewWidget.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from .Ui_calculatedvalues import Ui_ConfigTableViewWidget


class ConfigTableViewWidget(QDialog, Ui_ConfigTableViewWidget):
    """
    Class documentation goes here.
    """
    def __init__(self, availableScalars, scalarsToShow, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.ValueListModel = QStandardItemModel()

        for value in availableScalars:                   
            item = QStandardItem(value)
            check = Qt.Checked if value in scalarsToShow else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            self.ValueListModel.appendRow(item)
        
        
        self.ValueListView.setModel(self.ValueListModel)
        
    def setVisibleValues(self):
        setVisible = []
        for row in range(self.ValueListModel.rowCount()):
            item = self.ValueListModel.item(row)                  
            if item.checkState() == Qt.Checked:
                setVisible.append(item.text())
                
        return setVisible
                
        
