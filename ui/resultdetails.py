# -*- coding: utf-8 -*-

"""
Module implementing ResultDetailDlg.
"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView

from .Ui_resultdetails import Ui_ResultDetailDlg


class ResultDetailDlg(QDialog, Ui_ResultDetailDlg):
    """
    Class documentation goes here.
    """
    def __init__(self, result, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.result = result
        self.fillTable()
        
    def fillTable(self):
        
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(len(self.result))
        horHeaders = ['Result',  'Value']
        self.tableWidget.setHorizontalHeaderLabels(horHeaders)
        row = 0
        for item in self.result.keys():
            size = QTableWidgetItem(item)
            value = QTableWidgetItem(str(self.result[item])) #'%.4f' % 
            self.tableWidget.setItem(row, 0, size)
            self.tableWidget.setItem(row, 1, value)
            row = row + 1
            
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
